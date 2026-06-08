#!/usr/bin/env python3
"""Fetch source-paper text for the edge-discovery grounding gate (G2).

For every PMID referenced by candidate edges (or listed in a PMID file), fetch the open-access
full text (Europe PMC) when available, else the abstract (NCBI efetch), and cache the
normalised text to curation/staging/corpus/<pmid>.txt. The grounding gate
(validate_edge_candidates.py G2) checks each candidate's verbatim quote against this cache —
so an edge can only survive if its quote is provably present in the real article.

Run:
    python3 scripts/fetch_ssc_corpus.py                # PMIDs from staging candidates
    python3 scripts/fetch_ssc_corpus.py --pmids 12345 67890
or  make corpus-fetch

Network: Europe PMC + NCBI E-utils. Re-runs are offline for cached PMIDs (unless --refresh).
"""
from __future__ import annotations

import argparse
import csv
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "curation/staging/ssc_edge_candidates.tsv"
CORPUS = ROOT / "curation/staging/corpus"
UA = "SSc-MIM-corpus/0.1 (mailto:nathan.foulquier.pro@gmail.com)"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def get(url: str, timeout: int = 60) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout).read()


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def epmc_fulltext(pmid: str) -> str | None:
    """Open-access full text via Europe PMC, if present."""
    try:
        q = json.loads(get(f"{EPMC}/search?" + urllib.parse.urlencode(
            {"query": f"EXT_ID:{pmid} AND SRC:MED", "resultType": "core", "format": "json"}), 30))
    except Exception:
        return None
    res = q.get("resultList", {}).get("result", [])
    if not res:
        return None
    r = res[0]
    pmcid = r.get("pmcid", "")
    if not (pmcid and r.get("isOpenAccess") == "Y"):
        return None
    try:
        xml = get(f"{EPMC}/{pmcid}/fullTextXML", 60)
        return normalise("".join(ET.fromstring(xml).itertext()))
    except Exception:
        return None


def efetch_abstract(pmid: str) -> str | None:
    try:
        root = ET.fromstring(get(EFETCH + "?" + urllib.parse.urlencode(
            {"db": "pubmed", "id": pmid, "retmode": "xml"}), 30))
    except Exception:
        return None
    parts = [root.findtext(".//ArticleTitle") or ""]
    parts += [t.text or "" for t in root.findall(".//Abstract/AbstractText")]
    txt = normalise(" ".join(parts))
    return txt or None


def pmids_from_candidates() -> list[str]:
    if not CAND.exists():
        return []
    out = []
    for r in csv.DictReader(CAND.open(), delimiter="\t"):
        p = (r.get("source_pmid", "") or "").strip()
        if p.isdigit() and p not in out:
            out.append(p)
    return out


def main() -> None:
    import json as _json
    global json
    json = _json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pmids", nargs="*")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    CORPUS.mkdir(parents=True, exist_ok=True)
    pmids = args.pmids or pmids_from_candidates()
    print(f"[corpus] {len(pmids)} PMID(s) to fetch")
    for p in pmids:
        out = CORPUS / f"{p}.txt"
        if out.exists() and not args.refresh:
            print(f"  {p}: cached ({out.stat().st_size} B)")
            continue
        txt = epmc_fulltext(p)
        src = "OA-fulltext"
        if not txt:
            txt = efetch_abstract(p)
            src = "abstract"
        if txt:
            out.write_text(f"[source={src} pmid={p}]\n{txt}")
            print(f"  {p}: {src} ({len(txt)} chars)")
        else:
            print(f"  {p}: FAILED (no text)")
        time.sleep(0.4)
    print(f"[corpus] cache at {CORPUS}")


if __name__ == "__main__":
    main()
