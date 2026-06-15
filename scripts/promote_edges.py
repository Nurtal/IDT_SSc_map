#!/usr/bin/env python3
"""Promote ratified, gate-passing candidate edges into the curated map (edge-discovery final).

Promotes a candidate from curation/staging/ssc_edge_candidates.tsv into
curation/ssc_curated_reactions.tsv only when BOTH hold:
  - validate_edge_candidates.py gave it verdict PASS, AND
  - its `decision` field is `promote` (human/curator ratification; default empty = held).

Promoted rows get the next free ssc_<MODULE>_NNN id, the candidate's PMID + ECO, the verbatim
supporting quote stored in `notes`, and ratification = "AI-proposed (discovery)" so they are
auditable and trivially reversible (delete the row, re-wire). Nothing is promoted that did not
clear every gate, including verbatim-quote grounding.

After promotion, run: make wire network evidence-audit evidence-lint preflight.

Run: python3 scripts/promote_edges.py            # promote decision=promote PASS rows
     python3 scripts/promote_edges.py --dry-run
or  make promote-edges
"""
from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "curation/staging/ssc_edge_candidates.tsv"
REPORT = ROOT / "curation/staging/validation_report.tsv"
SSC = ROOT / "curation/ssc_curated_reactions.tsv"


def next_ids(rows: list[dict]) -> dict[str, int]:
    nxt: dict[str, int] = {}
    for r in rows:
        m = re.match(r"ssc_(M\d|crosstalk)_(\d+)", r["reaction_id"])
        if m:
            mod, n = m.group(1), int(m.group(2))
            nxt[mod] = max(nxt.get(mod, 0), n)
    return nxt


EVIDENCE = ROOT / "curation/interaction_evidence.tsv"
EV_COLS = ["reaction_id", "role", "pmid", "evidence_code", "supporting_quote", "provenance"]


def append_evidence(rows: list[dict]) -> None:
    new = not EVIDENCE.exists()
    with EVIDENCE.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=EV_COLS, delimiter="\t")
        if new:
            w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report = {r["candidate_id"]: r for r in csv.DictReader(REPORT.open(), delimiter="\t")} if REPORT.exists() else {}
    cands = {c["candidate_id"]: c for c in csv.DictReader(CAND.open(), delimiter="\t")}
    ssc_rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    fn = list(ssc_rows[0].keys())
    if "secondary_pmids" not in fn:
        fn = fn + ["secondary_pmids"]
        for r in ssc_rows:
            r["secondary_pmids"] = ""
    by_id = {r["reaction_id"]: r for r in ssc_rows}
    nxt = next_ids(ssc_rows)
    existing = {(r["type"], r["reactants"], r["products"], r["pmid"]) for r in ssc_rows}

    new_rows, merges, contradictions = [], [], []
    ev_rows = []
    for cid, c in cands.items():
        if (c.get("decision", "") or "").strip() != "promote":
            continue
        rep = report.get(cid, {})
        if rep.get("verdict") == "REJECT":
            continue
        flags = rep.get("flags", "")
        key = (c["type"], c["reactants"], c["products"], c["source_pmid"])
        # MERGE: same gene pair + same sign, new source -> cumulate evidence on the existing reaction
        mm = re.search(r"G3:merge_into\[(ssc_[A-Za-z0-9_]+)\]", flags)
        cm = re.search(r"G3:contradicts\[(ssc_[A-Za-z0-9_]+)\]", flags)
        if mm and mm.group(1) in by_id:
            tgt = mm.group(1)
            if c["source_pmid"] in (by_id[tgt]["pmid"], *by_id[tgt].get("secondary_pmids", "").split(";")):
                continue  # already a source on this reaction
            ev_rows.append({"reaction_id": tgt, "role": "secondary", "pmid": c["source_pmid"],
                            "evidence_code": c.get("proposed_eco", "ECO:0000033"),
                            "supporting_quote": c.get("supporting_quote", ""),
                            "provenance": f"ai-discovery/{date.today()}"})
            sp = [x for x in by_id[tgt].get("secondary_pmids", "").split(";") if x]
            sp.append(c["source_pmid"])
            by_id[tgt]["secondary_pmids"] = ";".join(sp)
            merges.append((cid, tgt, c["source_pmid"]))
            continue
        # otherwise create a NEW reaction (novel, or a CONTRADICTION kept separate for review)
        if key in existing:
            continue
        mod = c["module"]
        nxt[mod] = nxt.get(mod, 0) + 1
        rid = f"ssc_{mod}_{nxt[mod]:03d}"
        note = f"discovery candidate {cid}; quote: \"{c.get('supporting_quote','')[:160]}\""
        if cm:
            note += f" | CONTRADICTS {cm.group(1)} (opposite sign on same gene pair) — kept as a separate interaction for human review"
            contradictions.append((cid, rid, cm.group(1)))
        row = {k: "" for k in fn}
        row.update({
            "reaction_id": rid, "module": mod, "type": c["type"], "mechanism": c["mechanism"],
            "reactants": c["reactants"], "products": c["products"], "modifiers": c.get("modifiers", ""),
            "pmid": c["source_pmid"], "evidence_code": c.get("proposed_eco", "ECO:0000033"),
            "ssc_relevance": c.get("ssc_relevance", ""), "notes": note,
            "curation_status": "confirmed", "candidate_pmids": "", "secondary_pmids": "",
            "provenance": f"ai-discovery/{date.today()}",
            "ratification": f"AI-proposed (discovery) {date.today()}",
        })
        ev_rows.append({"reaction_id": rid, "role": "primary", "pmid": c["source_pmid"],
                        "evidence_code": c.get("proposed_eco", "ECO:0000033"),
                        "supporting_quote": c.get("supporting_quote", ""),
                        "provenance": f"ai-discovery/{date.today()}"})
        new_rows.append((cid, rid, row))

    print(f"[promote] new reactions: {len(new_rows)} | merged sources: {len(merges)} | contradictions kept separate: {len(contradictions)}")
    for cid, rid, row in new_rows:
        print(f"  NEW   {cid} -> {rid}: {row['reactants']} -> {row['products']} ({row['type']}, {row['pmid']})")
    for cid, tgt, pmid in merges:
        print(f"  MERGE {cid} -> +source {pmid} on {tgt}")
    for cid, rid, other in contradictions:
        print(f"  ⚠ CONTRADICTION {cid} -> {rid} (vs {other}); both kept for review")
    if args.dry_run or (not new_rows and not merges):
        print("[promote] dry-run / nothing to write." if args.dry_run else "[promote] nothing new.")
        return
    with SSC.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fn, delimiter="\t")
        w.writeheader()
        w.writerows(ssc_rows + [r for _, _, r in new_rows])
    if ev_rows:
        append_evidence(ev_rows)
    print(f"[promote] wrote {SSC} (+{len(new_rows)}), {EVIDENCE} (+{len(ev_rows)}). "
          f"Next: make wire network evidence-audit evidence-lint preflight")


if __name__ == "__main__":
    main()
