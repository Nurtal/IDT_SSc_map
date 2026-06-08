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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    passing = {r["candidate_id"] for r in csv.DictReader(REPORT.open(), delimiter="\t")
               if r["verdict"] == "PASS"} if REPORT.exists() else set()
    cands = {c["candidate_id"]: c for c in csv.DictReader(CAND.open(), delimiter="\t")}
    ssc_rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    fn = list(ssc_rows[0].keys())
    nxt = next_ids(ssc_rows)

    # idempotency: skip candidates whose (type, reactants, products, pmid) is already curated
    existing = {(r["type"], r["reactants"], r["products"], r["pmid"]) for r in ssc_rows}
    to_promote = [c for cid, c in cands.items()
                  if (c.get("decision", "") or "").strip() == "promote" and cid in passing
                  and (c["type"], c["reactants"], c["products"], c["source_pmid"]) not in existing]
    if not to_promote:
        print("[promote] nothing to promote (need decision=promote AND verdict=PASS)")
        return

    new_rows = []
    for c in to_promote:
        mod = c["module"]
        nxt[mod] = nxt.get(mod, 0) + 1
        rid = f"ssc_{mod}_{nxt[mod]:03d}"
        note = f"discovery candidate {c['candidate_id']}; quote: \"{c.get('supporting_quote','')[:160]}\""
        row = {k: "" for k in fn}
        row.update({
            "reaction_id": rid, "module": mod, "type": c["type"], "mechanism": c["mechanism"],
            "reactants": c["reactants"], "products": c["products"], "modifiers": c.get("modifiers", ""),
            "pmid": c["source_pmid"], "evidence_code": c.get("proposed_eco", "ECO:0000033"),
            "ssc_relevance": c.get("ssc_relevance", ""), "notes": note,
            "curation_status": "confirmed", "candidate_pmids": "",
            "provenance": f"ai-discovery/{date.today()}",
            "ratification": f"AI-proposed (discovery) {date.today()}",
        })
        new_rows.append((c["candidate_id"], rid, row))

    print(f"[promote] {len(new_rows)} candidate(s) -> curated map:")
    for cid, rid, row in new_rows:
        print(f"  {cid} -> {rid}: {row['reactants']} -> {row['products']}  ({row['type']}, {row['pmid']})")
    if args.dry_run:
        print("[promote] dry-run; nothing written.")
        return
    with SSC.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fn, delimiter="\t")
        w.writeheader()
        w.writerows(ssc_rows + [r for _, _, r in new_rows])
    print(f"[promote] appended {len(new_rows)} rows to {SSC}. Next: make wire network evidence-audit evidence-lint preflight")


if __name__ == "__main__":
    main()
