#!/usr/bin/env python3
"""CI guard for SSc-Tier-1 evidence depth (regression lock-in).

Part of the curation-depth pass (see docs/curation/curation_depth_pass.md). Implements the
open CI-lint item in docs/curation/mi2cast_checklist.md §"Open items".

Encodes the **tiered evidence policy** of `docs/curation/mi2cast_checklist.md` §"Evidence policy
(tiered)", which follows the GO/GOA gold standard (honest ECO-coded provenance), NOT a
"primary-only" rule. Review citations (`ECO:0000033`, traceable author statement) are
accepted for canonical mechanisms; the higher bar (primary/experimental evidence) is
reserved for the SSc-specific novelty layer — the inter-module crosstalk rows.

Every SSc-curated reaction must be **explicitly triaged**. A row is *resolved* when:
  - it carries a citation at `ECO:0000033` or stronger (status `confirmed` / `proposed`), OR
  - it is honestly reclassified (`conceptual_bridge` / `phenotype_aggregation`), OR
  - it is declared backlog (`untested`, with a candidate pool).

The lint FAILS on:
  - undeclared inference debt — `ECO:0000305` + no PMID + status not in the declared
    set above (i.e. an empty/unset status, or a new uncurated row);
  - a `confirmed`/`proposed` row with no PMID (a contradiction); and
  - a **crosstalk** row that is neither primary/experimental-cited nor reclassified as a
    `conceptual_bridge` — undeclared SSc-novelty debt (§7 of the guidelines).

It does NOT fail on `untested` rows (tracked backlog, advisory), and does NOT demand that
canonical review-cited (`ECO:0000033`) edges be upgraded to primary.

Run:
    python3 scripts/check_evidence_depth.py            # exit 1 on failure
    python3 scripts/check_evidence_depth.py --strict   # also fail if untested > THRESHOLD
or  make evidence-lint
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"

DECLARED = {"confirmed", "proposed", "conceptual_bridge", "phenotype_aggregation", "untested"}
RECLASSIFIED = {"conceptual_bridge", "phenotype_aggregation"}
# Experimental ECO codes (primary evidence) required for the SSc-novelty crosstalk layer.
EXPERIMENTAL = {"ECO:0000314", "ECO:0000270", "ECO:0000353", "ECO:0000315"}
UNTESTED_THRESHOLD = 20  # --strict ceiling on remaining backlog


def has_pmid(v: str) -> bool:
    v = (v or "").strip()
    return bool(v) and v != "-" and bool(re.search(r"\d", v))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help=f"also fail if untested backlog > {UNTESTED_THRESHOLD}")
    args = ap.parse_args()

    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    failures: list[str] = []
    untested = 0
    for r in rows:
        rid = r["reaction_id"]
        status = (r.get("curation_status", "") or "").strip()
        pmid = has_pmid(r.get("pmid", ""))
        eco = (r.get("evidence_code", "") or "").strip()

        if status == "untested":
            untested += 1
        if status in ("confirmed", "proposed") and not pmid:
            failures.append(f"{rid}: status={status} but no PMID (contradiction)")
            continue
        if status not in DECLARED:
            failures.append(f"{rid}: undeclared curation_status '{status}' "
                            f"(eco={eco}, pmid={'yes' if pmid else 'no'})")
            continue
        if eco == "ECO:0000305" and not pmid and status not in (RECLASSIFIED | {"untested"}):
            failures.append(f"{rid}: ECO:0000305 + no PMID + status={status} "
                            f"(undeclared inference debt)")

        # Tiered policy: crosstalk rows carry the map's SSc-specific novelty and are held
        # to the higher bar — primary/experimental evidence, or an explicit conceptual_bridge.
        module = (r.get("module", "") or "").strip()
        if module == "crosstalk" and status not in RECLASSIFIED:
            if not (pmid and eco in EXPERIMENTAL):
                failures.append(
                    f"{rid}: crosstalk needs experimental ECO (314/270/353/315) + PMID, "
                    f"or a conceptual_bridge tag (has eco={eco}, "
                    f"pmid={'yes' if pmid else 'no'}, status={status}) — SSc-novelty debt")

    n = len(rows)
    cited = sum(1 for r in rows if has_pmid(r.get("pmid", "")))
    print(f"[evidence-depth] {n} SSc reactions; {cited} cited ({round(100*cited/n,1)}%); "
          f"{untested} untested backlog")

    if failures:
        print(f"[evidence-depth] FAIL — {len(failures)} issue(s):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    if args.strict and untested > UNTESTED_THRESHOLD:
        print(f"[evidence-depth] FAIL (--strict) — untested backlog {untested} "
              f"> {UNTESTED_THRESHOLD}", file=sys.stderr)
        return 1

    print(f"[evidence-depth] OK — all {n} rows triaged "
          f"({untested} untested backlog reported as advisory)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
