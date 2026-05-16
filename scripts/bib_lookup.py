#!/usr/bin/env python3
"""Fill in BibTeX entries from NCBI E-utils (PubMed efetch).

Walks curation/pubmed_corpus.bib for entries whose `title = {TODO}`,
batches their PMIDs, fetches metadata via NCBI E-utils efetch
(retmode=xml), parses title/authors/journal/year/DOI, and rewrites the
entry in place. Idempotent.

Usage:
  scripts/bib_lookup.py
  scripts/bib_lookup.py --batch 100 --rate 1 --max 50  # debug-friendly

Network call. Honours an `NCBI_API_KEY` env var (raises rate limit to 10
req/s) if present; otherwise stays at ~3 req/s (NCBI guidance).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET


EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
USER_AGENT = "SSc-MIM-bib-lookup/0.1 (mailto:nathan.foulquier.pro@gmail.com)"
DEFAULT_BATCH = 200
DEFAULT_RATE = 0.34  # seconds between requests (~3/s without API key)


ENTRY_RE = re.compile(
    r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,(?P<body>.*?)\n\}\s*",
    re.DOTALL,
)
FIELD_RE = re.compile(r"^\s*(?P<k>\w+)\s*=\s*\{(?P<v>.*?)\}\s*,?\s*$", re.MULTILINE)


def parse_bib(text: str) -> list[dict[str, str]]:
    """Lightweight BibTeX parser: returns a list of {type, key, raw, fields}.

    raw is the verbatim entry text (so we can replace in place).
    """
    entries: list[dict[str, str]] = []
    for m in ENTRY_RE.finditer(text):
        body = m.group("body")
        fields = {fm.group("k").lower(): fm.group("v") for fm in FIELD_RE.finditer(body)}
        entries.append({
            "type": m.group("type").lower(),
            "key": m.group("key"),
            "raw": m.group(0),
            "fields": fields,
            "start": m.start(),
            "end": m.end(),
        })
    return entries


def needs_lookup(entry: dict) -> bool:
    """An entry needs lookup if it has a pmid and either title=TODO or no title."""
    pmid = entry["fields"].get("pmid", "")
    if not pmid or pmid.upper() == "TODO":
        return False
    title = entry["fields"].get("title", "")
    return title == "TODO" or title.strip() == ""


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def efetch_batch(pmids: list[str]) -> ET.Element:
    api_key = os.environ.get("NCBI_API_KEY", "")
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    if api_key:
        params["api_key"] = api_key
    url = EFETCH + "?" + urllib.parse.urlencode(params)
    data = http_get(url)
    return ET.fromstring(data)


def extract_record(article: ET.Element) -> dict[str, str]:
    """Best-effort metadata extraction from a PubmedArticle XML element."""
    pmid = article.findtext(".//PMID") or ""
    title = (article.findtext(".//ArticleTitle") or "").strip()
    journal = (article.findtext(".//Journal/ISOAbbreviation")
               or article.findtext(".//Journal/Title")
               or "").strip()
    year = (article.findtext(".//PubDate/Year")
            or article.findtext(".//PubDate/MedlineDate")
            or "")[:4]

    # authors: "Last1 FM1, Last2 FM2, ..."
    authors_parts: list[str] = []
    for a in article.findall(".//AuthorList/Author"):
        last = a.findtext("LastName") or a.findtext("CollectiveName") or ""
        initials = a.findtext("Initials") or ""
        if last:
            authors_parts.append(f"{last} {initials}".strip())
    authors = " and ".join(authors_parts)

    doi = ""
    for aid in article.findall(".//ArticleIdList/ArticleId"):
        if (aid.get("IdType") or "").lower() == "doi":
            doi = (aid.text or "").strip()
            break

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "doi": doi,
    }


def format_entry(entry_type: str, key: str, fields: dict[str, str]) -> str:
    order = ["author", "title", "journal", "year", "pmid", "doi", "note"]
    lines: list[str] = [f"@{entry_type}{{{key},"]
    for k in order:
        v = fields.get(k, "")
        if not v:
            continue
        # Sanitise braces in values
        v = v.replace("{", "(").replace("}", ")")
        lines.append(f"  {k:<7} = {{{v}}},")
    if lines[-1].endswith(","):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bib", type=Path, default=Path("curation/pubmed_corpus.bib"))
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    ap.add_argument("--rate", type=float, default=DEFAULT_RATE)
    ap.add_argument(
        "--max",
        type=int,
        default=0,
        help="cap the number of PMIDs fetched (debug; 0 = all)",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv[1:])

    if not args.bib.exists():
        print(f"bib not found: {args.bib}", file=sys.stderr)
        return 2

    text = args.bib.read_text(encoding="utf-8")
    entries = parse_bib(text)
    to_fetch = [e for e in entries if needs_lookup(e)]
    if args.max:
        to_fetch = to_fetch[: args.max]

    print(f"entries in bib:    {len(entries)}")
    print(f"need lookup:       {len(to_fetch)}")

    if args.dry_run or not to_fetch:
        return 0

    pmid_to_entry = {e["fields"]["pmid"]: e for e in to_fetch}
    pmids = list(pmid_to_entry.keys())

    updates: dict[str, dict[str, str]] = {}  # pmid -> filled fields

    for start in range(0, len(pmids), args.batch):
        batch = pmids[start : start + args.batch]
        print(f"[fetch] batch {start // args.batch + 1}: {len(batch)} PMID(s)")
        try:
            root = efetch_batch(batch)
        except Exception as exc:  # noqa: BLE001
            print(f"  [err] {exc!r} — abandoning batch", file=sys.stderr)
            time.sleep(args.rate)
            continue
        # Each PubmedArticle has its own PMID
        for art in root.findall(".//PubmedArticle"):
            rec = extract_record(art)
            if rec["pmid"]:
                updates[rec["pmid"]] = rec
        time.sleep(args.rate)

    print(f"[ok] fetched {len(updates)} / {len(pmids)} record(s)")

    # Apply updates to bib text. Iterate over entries to keep order; replace
    # `raw` with a formatted version where TODO fields are now filled.
    new_text = text
    # We must replace longest-first or use offsets — easiest: rebuild from
    # the parsed entry list and concatenate.
    rebuilt: list[str] = []
    cursor = 0
    for entry in entries:
        rebuilt.append(text[cursor : entry["start"]])
        cursor = entry["end"]
        rec = updates.get(entry["fields"].get("pmid", ""), None)
        if rec is None:
            rebuilt.append(entry["raw"])
            continue
        fields = dict(entry["fields"])
        # Replace TODOs with the fetched values
        for k in ("title", "journal", "year", "doi"):
            v = rec.get(k, "")
            if v and (fields.get(k, "TODO") == "TODO" or not fields.get(k, "")):
                fields[k] = v
        if rec.get("authors") and not fields.get("author", "").strip():
            fields["author"] = rec["authors"]
        # Drop the placeholder note if it's the only thing left
        if fields.get("note", "").startswith("auto-extracted"):
            del fields["note"]
        rebuilt.append(format_entry(entry["type"], entry["key"], fields))
        rebuilt.append("\n")
    rebuilt.append(text[cursor:])

    args.bib.write_text("".join(rebuilt), encoding="utf-8")
    print(f"[ok] wrote {args.bib}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
