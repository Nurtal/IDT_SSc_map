#!/usr/bin/env python3
"""Discover candidate PubMed PMIDs for the curator-inference SSc reactions (P2).

Part of the curation-depth pass (see docs/curation/curation_depth_pass.md).

`scripts/bib_lookup.py` fills metadata for PMIDs already known; it cannot *find*
a PMID from a mechanism. This script closes that gap: for every SSc-curated
reaction still on curator inference (ECO:0000305, no PMID), it constructs PubMed
`esearch` queries from the reaction's gene participants and mechanism text, runs
two passes (a disease-context pass and a canonical-mechanism pass), and caches
ranked candidate PMIDs with title/year/journal for human triage.

It proposes; the curator (and ultimately the co-author) disposes. Nothing here
writes into the curated map — output is a candidate cache only.

Outputs:
    curation/lit_candidates/<reaction_id>.json   per-reaction candidate sets
    curation/lit_candidates/_index.tsv            roll-up (reaction_id, n_candidates, top_pmid, top_title)

Run:
    python3 scripts/mine_lit_candidates.py            # all uncited inference rows
    python3 scripts/mine_lit_candidates.py --only ssc_M3_003 ssc_M4_001
or  make mine-lit

Network call (NCBI E-utils). Honours NCBI_API_KEY (10 req/s) else ~3 req/s.
Re-runs are offline for rows already cached unless --refresh is given.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
OUT_DIR = ROOT / "curation/lit_candidates"

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
USER_AGENT = "SSc-MIM-lit-mine/0.1 (mailto:nathan.foulquier.pro@gmail.com)"  # reuses bib_lookup.py convention
RATE = 0.34  # ~3 req/s without an API key

GENE_RE = re.compile(r"^[A-Z][A-Z0-9]{1,6}$")
STOP_TOKENS = {"COMPLEX", "ACTIVE", "SIGNAL", "CELL", "DIMER", "REPRESSED", "BOUND"}
MECH_STOP = {
    "the", "and", "with", "into", "from", "via", "that", "this", "their", "then",
    "becomes", "join", "joins", "drive", "drives", "driven", "toward", "towards",
    "induces", "induce", "produces", "produce", "binds", "bind", "represses",
}


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _api_key_params() -> dict:
    key = os.environ.get("NCBI_API_KEY", "")
    return {"api_key": key} if key else {}


def genes_from(*fields: str) -> list[str]:
    """Extract gene-symbol-like tokens from participant fields, order-preserving."""
    out: list[str] = []
    for fld in fields:
        for chunk in re.split(r"[;]", fld or ""):
            base = chunk.split("__", 1)[0]
            if not base or base.startswith("phenotype_"):
                continue
            for tok in re.split(r"[_:]", base):
                tok = tok.strip().rstrip("p")  # strip a trailing phospho 'p' (SMAD3p -> SMAD3)
                tok = tok if GENE_RE.match(tok) else tok.upper()
                if GENE_RE.match(tok) and tok not in STOP_TOKENS and tok not in out:
                    out.append(tok)
    return out


def mech_keywords(mech: str, k: int = 2) -> list[str]:
    words = re.findall(r"[a-zA-Z]{4,}", mech or "")
    kws = [w.lower() for w in words if w.lower() not in MECH_STOP]
    seen, out = set(), []
    for w in kws:
        if w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= k:
            break
    return out


def esearch(term: str, retmax: int = 5) -> list[str]:
    params = {"db": "pubmed", "term": term, "retmax": str(retmax),
              "retmode": "json", "sort": "relevance", **_api_key_params()}
    data = json.loads(http_get(ESEARCH + "?" + urllib.parse.urlencode(params)))
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: list[str]) -> dict[str, dict]:
    if not pmids:
        return {}
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json", **_api_key_params()}
    data = json.loads(http_get(ESUMMARY + "?" + urllib.parse.urlencode(params)))
    res = data.get("result", {})
    out = {}
    for pid in res.get("uids", []):
        rec = res.get(pid, {})
        out[pid] = {
            "pmid": pid,
            "title": rec.get("title", "").rstrip("."),
            "journal": rec.get("source", ""),
            "year": (rec.get("pubdate", "") or "")[:4],
        }
    return out


def build_queries(row: dict) -> dict[str, str]:
    genes = genes_from(row.get("modifiers", ""), row.get("products", ""), row.get("reactants", ""))
    kws = mech_keywords(row.get("mechanism", ""))
    queries: dict[str, str] = {}
    if len(genes) >= 2:
        canonical = f"{genes[0]}[tiab] AND {genes[1]}[tiab]"
    elif genes:
        kw = f' AND {kws[0]}[tiab]' if kws else ""
        canonical = f"{genes[0]}[tiab]{kw}"
    else:
        canonical = " AND ".join(f"{w}[tiab]" for w in kws) or row.get("mechanism", "")[:60]
    queries["canonical"] = canonical
    if genes:
        queries["ssc_context"] = (
            f'{genes[0]}[tiab] AND ("systemic sclerosis"[tiab] OR scleroderma[tiab] '
            f'OR fibrosis[tiab])'
        )
    return queries


def mine_row(row: dict) -> dict:
    queries = build_queries(row)
    candidates: dict[str, dict] = {}
    for qname, term in queries.items():
        try:
            pmids = esearch(term)
        except Exception as exc:  # noqa: BLE001
            print(f"    [err] esearch {row['reaction_id']}/{qname}: {exc!r}")
            pmids = []
        time.sleep(RATE)
        summ = esummary(pmids) if pmids else {}
        time.sleep(RATE)
        for rank, pid in enumerate(pmids):
            rec = summ.get(pid, {"pmid": pid, "title": "", "journal": "", "year": ""})
            if pid not in candidates:
                rec = dict(rec)
                rec["found_by"] = [qname]
                rec["best_rank"] = rank
                candidates[pid] = rec
            else:
                candidates[pid]["found_by"].append(qname)
    # rank: prefer hits found by both passes, then by best rank
    ranked = sorted(candidates.values(), key=lambda r: (-len(r["found_by"]), r["best_rank"]))
    return {
        "reaction_id": row["reaction_id"],
        "module": row["module"],
        "mechanism": row["mechanism"],
        "queries": queries,
        "candidates": ranked,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", default=None, help="restrict to these reaction_ids")
    ap.add_argument("--refresh", action="store_true", help="re-mine even if cached")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    targets = [
        r for r in rows
        if (r.get("evidence_code", "").strip() == "ECO:0000305")
        and (r.get("pmid", "").strip() in ("", "-"))
        and (args.only is None or r["reaction_id"] in args.only)
    ]
    print(f"[mine] {len(targets)} curator-inference rows to mine")

    index_rows = []
    for i, row in enumerate(targets, 1):
        rid = row["reaction_id"]
        cache = OUT_DIR / f"{rid}.json"
        if cache.exists() and not args.refresh:
            result = json.loads(cache.read_text())
            print(f"  [{i}/{len(targets)}] {rid}: cached ({len(result['candidates'])})")
        else:
            print(f"  [{i}/{len(targets)}] {rid}: mining…")
            result = mine_row(row)
            cache.write_text(json.dumps(result, indent=2))
        top = result["candidates"][0] if result["candidates"] else {}
        index_rows.append({
            "reaction_id": rid,
            "module": row["module"],
            "n_candidates": len(result["candidates"]),
            "top_pmid": top.get("pmid", ""),
            "top_year": top.get("year", ""),
            "top_title": top.get("title", "")[:90],
        })

    with (OUT_DIR / "_index.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["reaction_id", "module", "n_candidates",
                                          "top_pmid", "top_year", "top_title"], delimiter="\t")
        w.writeheader()
        w.writerows(index_rows)
    print(f"[mine] wrote {OUT_DIR}/_index.tsv ({len(index_rows)} rows)")


if __name__ == "__main__":
    main()
