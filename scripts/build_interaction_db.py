#!/usr/bin/env python3
"""Build the reviewer-ready interaction database (tidy CSV) for the SSc-curated layer.

One row per SSc-curated interaction, with — for each — the evidence level, the article
reference (PMID + DOI + title), and the verbatim sentence used to decide it. Designed as the
backend for a static HTML review app: a human reviewer can scan claim + evidence + quote and
adjudicate (confirm / reject / edit) row by row.

Quote provenance (best available):
  - AI-discovery edges -> verbatim quote stored in `notes` / staging candidates
  - AI full-text-verified edges -> evidence snippet from curation/fulltext_verification_log.md
  - original curation / abstract-only / reclassifications -> blank (quote_status=to_complete)

Adds a `contradiction_flag` from scripts/check_contradictions.py and empty `review_decision`
/ `review_notes` columns for the app to write into.

Outputs:
    analysis/curation/interaction_database.csv

Run: python3 scripts/build_interaction_db.py   (or make interaction-db)
Network: NCBI esummary for DOI/title (cached in analysis/curation/_pmid_meta.json).
"""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from check_contradictions import get_contradiction_flags

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
STAGING = ROOT / "curation/staging/ssc_edge_candidates.tsv"
FT_LOG = ROOT / "curation/fulltext_verification_log.md"
META = ROOT / "analysis/curation/_pmid_meta.json"
OUT = ROOT / "analysis/curation/interaction_database.csv"
UA = "SSc-MIM-db/0.1 (mailto:nathan.foulquier.pro@gmail.com)"

EVIDENCE_LEVEL = {
    "ECO:0000314": "experimental — direct assay",
    "ECO:0000315": "experimental — mutant/loss-of-function",
    "ECO:0000270": "experimental — expression pattern",
    "ECO:0000353": "experimental — physical interaction",
    "ECO:0000033": "review — traceable author statement",
    "ECO:0000305": "curator inference",
}
PROVENANCE = {
    "original-curation": "human — original curation",
    "fulltext-verified-claude": "AI — full-text-verified",
    "claude-lit-mine": "AI — abstract-verified",
    "claude-reclassify": "AI — reclassification",
    "ai-discovery": "AI — literature-mined (discovery)",
}


def has_pmid(v: str) -> bool:
    v = (v or "").strip()
    return bool(v) and v != "-" and bool(re.search(r"\d", v))


def provenance_label(ratification: str, provenance: str) -> str:
    key = (ratification or provenance or "").split("/")[0].strip()
    # ratification field may read "AI-verified 2026-06-08 (full-text)" etc.
    low = (ratification or "").lower()
    if low.startswith("human"):
        return PROVENANCE["original-curation"]
    if "full-text" in low:
        return PROVENANCE["fulltext-verified-claude"]
    if "reclassification" in low:
        return PROVENANCE["claude-reclassify"]
    for k, v in PROVENANCE.items():
        if provenance.startswith(k):
            return v
    if low.startswith("ai"):
        return PROVENANCE["ai-discovery"]
    return provenance or ratification or "unknown"


EVIDENCE = ROOT / "curation/interaction_evidence.tsv"


def load_secondary_evidence() -> dict[str, list[str]]:
    """reaction_id -> list of secondary PMIDs (multi-source cumulative evidence)."""
    out: dict[str, list[str]] = {}
    if EVIDENCE.exists():
        for r in csv.DictReader(EVIDENCE.open(), delimiter="\t"):
            if r.get("role") == "secondary" and r.get("pmid"):
                out.setdefault(r["reaction_id"], []).append(r["pmid"])
    return out


def load_staging_quotes() -> dict[str, str]:
    if not STAGING.exists():
        return {}
    return {r["candidate_id"]: r.get("supporting_quote", "")
            for r in csv.DictReader(STAGING.open(), delimiter="\t")}


def load_ftlog_snippets() -> dict[str, str]:
    out: dict[str, str] = {}
    if not FT_LOG.exists():
        return out
    for m in re.finditer(r"- \*\*(ssc_[A-Za-z0-9_]+)\*\* — (.+)", FT_LOG.read_text()):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


def quote_for(row: dict, staging: dict[str, str], ftlog: dict[str, str]) -> tuple[str, str]:
    notes = row.get("notes", "")
    m = re.search(r'quote:\s*"(.+?)"\s*$', notes)
    if m:
        return m.group(1), "verbatim (discovery)"
    cm = re.search(r"discovery candidate (cand_[A-Za-z0-9_]+)", notes)
    if cm and staging.get(cm.group(1)):
        return staging[cm.group(1)], "verbatim (discovery)"
    if row["reaction_id"] in ftlog:
        return ftlog[row["reaction_id"]], "full-text evidence note"
    return "", "to_complete"


EXCLUDED = ROOT / "curation/staging/excluded_interactions.tsv"
STAGING_DROP_REASONS = {
    "cand_negctrl": "NEGATIVE CONTROL: fabricated edge whose quote is absent from any source — "
                    "correctly rejected by the grounding gate (G2). Demonstrates the anti-nonsense guarantee.",
    "cand_sig_cav1_angio": "discarded: the available quote stated TGF-β's role in angiogenesis is "
                           "*uncertain* — it did not support the CAV1→angiogenesis claim.",
    "cand_stat6_col": "discarded: duplicate of the existing IL-13→COL1A1/STAT6 crosstalk (ssc_crosstalk_005).",
}


def load_discarded(curated_rows: list[dict]) -> list[dict]:
    """Considered-but-not-included interactions, with the deciding quote and discard reason."""
    cur = {(r["type"], r["reactants"], r["products"], r["pmid"].strip()) for r in curated_rows}
    # PMIDs that were merged in as secondary evidence (cumulated, not discarded)
    merged_pmids = {p for ps in load_secondary_evidence().values() for p in ps}
    out: list[dict] = []
    # (a) staged candidates that never reached the map
    if STAGING.exists():
        for c in csv.DictReader(STAGING.open(), delimiter="\t"):
            key = (c["type"], c["reactants"], c["products"], c["source_pmid"].strip())
            if key in cur or c["source_pmid"].strip() in merged_pmids:
                continue
            out.append({
                "id": c["candidate_id"], "type": c["type"],
                "regulator": ";".join(x for x in [c["reactants"], c.get("modifiers", "")] if x.strip()),
                "target": c["products"], "mechanism": c.get("mechanism", ""),
                "pmid": c["source_pmid"].strip(), "quote": c.get("supporting_quote", ""),
                "reason": STAGING_DROP_REASONS.get(c["candidate_id"], "not promoted (held / failed a gate)"),
            })
    # (b) interactions surfaced during scanning but judged out (curation_excluded registry)
    if EXCLUDED.exists():
        for c in csv.DictReader(EXCLUDED.open(), delimiter="\t"):
            out.append({
                "id": c["candidate_id"], "type": c["interaction_type"],
                "regulator": c["regulator"], "target": c["target"], "mechanism": "",
                "pmid": c["source_pmid"].strip(), "quote": c.get("supporting_quote", ""),
                "reason": c["discard_reason"],
            })
    return out


def fetch_meta(pmids: list[str]) -> dict[str, dict]:
    cache = json.loads(META.read_text()) if META.exists() else {}
    missing = [p for p in pmids if p and p not in cache]
    for i in range(0, len(missing), 100):
        batch = missing[i:i + 100]
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" +
                urllib.parse.urlencode({"db": "pubmed", "id": ",".join(batch), "retmode": "json"}),
                headers={"User-Agent": UA}), timeout=30).read())
            res = d.get("result", {})
            for p in batch:
                r = res.get(p, {})
                doi = ""
                for aid in r.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                        break
                cache[p] = {"doi": doi, "title": r.get("title", "").rstrip("."),
                            "journal": r.get("source", ""), "year": (r.get("pubdate", "") or "")[:4]}
        except Exception as exc:  # noqa: BLE001
            print(f"  [meta] batch failed: {exc!r}")
        time.sleep(0.4)
    META.write_text(json.dumps(cache, indent=0))
    return cache


def main() -> None:
    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    staging = load_staging_quotes()
    ftlog = load_ftlog_snippets()
    flags = get_contradiction_flags()
    discarded = load_discarded(rows)
    pmids = {r["pmid"].strip() for r in rows if has_pmid(r.get("pmid", ""))}
    pmids |= {d["pmid"] for d in discarded if d["pmid"]}
    meta = fetch_meta(sorted(pmids))

    secondaries = load_secondary_evidence()
    cols = ["reaction_id", "inclusion_status", "discard_reason", "module", "interaction_type",
            "regulator", "target", "mechanism", "ssc_relevance", "pmid", "doi", "article_title",
            "journal_year", "eco_code", "evidence_level", "supporting_quote", "quote_status",
            "n_sources", "secondary_pmids", "provenance", "curation_status", "contradiction_flag",
            "review_decision", "review_notes"]
    out_rows = []
    for r in rows:
        pmid = r["pmid"].strip()
        m = meta.get(pmid, {})
        quote, qstatus = quote_for(r, staging, ftlog)
        reg = ";".join(x for x in [r["reactants"], r.get("modifiers", "")] if x.strip())
        out_rows.append({
            "reaction_id": r["reaction_id"],
            "inclusion_status": "in_map",
            "discard_reason": "",
            "module": r["module"],
            "interaction_type": r["type"],
            "regulator": reg,
            "target": r["products"],
            "mechanism": r["mechanism"],
            "ssc_relevance": r.get("ssc_relevance", ""),
            "pmid": pmid if has_pmid(pmid) else "",
            "doi": m.get("doi", ""),
            "article_title": m.get("title", ""),
            "journal_year": f"{m.get('journal','')} {m.get('year','')}".strip(),
            "eco_code": r["evidence_code"],
            "evidence_level": EVIDENCE_LEVEL.get(r["evidence_code"].strip(), r["evidence_code"]),
            "supporting_quote": quote,
            "quote_status": qstatus,
            "n_sources": 1 + len(secondaries.get(r["reaction_id"], [])),
            "secondary_pmids": ";".join(secondaries.get(r["reaction_id"], [])),
            "provenance": provenance_label(r.get("ratification", ""), r.get("provenance", "")),
            "curation_status": r.get("curation_status", ""),
            "contradiction_flag": flags.get(r["reaction_id"], ""),
            "review_decision": "",   # for the HTML app: confirm / reject / edit
            "review_notes": "",
        })

    # discarded / considered-but-excluded interactions — full reviewer control
    for d in discarded:
        m = meta.get(d["pmid"], {})
        out_rows.append({
            "reaction_id": d["id"],
            "inclusion_status": "discarded",
            "discard_reason": d["reason"],
            "module": "", "interaction_type": d["type"],
            "regulator": d["regulator"], "target": d["target"], "mechanism": d["mechanism"],
            "ssc_relevance": "",
            "pmid": d["pmid"], "doi": m.get("doi", ""), "article_title": m.get("title", ""),
            "journal_year": f"{m.get('journal','')} {m.get('year','')}".strip(),
            "eco_code": "", "evidence_level": "",
            "supporting_quote": d["quote"],
            "quote_status": "verbatim (excluded)" if d["quote"] else "to_complete",
            "n_sources": 0, "secondary_pmids": "",
            "provenance": "AI — considered & discarded",
            "curation_status": "excluded", "contradiction_flag": "",
            "review_decision": "", "review_notes": "",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    from collections import Counter
    qs = Counter(r["quote_status"] for r in out_rows)
    print(f"[interaction-db] {len(out_rows)} interactions -> {OUT}")
    print(f"  with a verbatim/evidence quote: {len(out_rows) - qs['to_complete']} | to_complete: {qs['to_complete']}")
    print(f"  with DOI: {sum(1 for r in out_rows if r['doi'])} | contradiction-flagged: {sum(1 for r in out_rows if r['contradiction_flag'])}")


if __name__ == "__main__":
    main()
