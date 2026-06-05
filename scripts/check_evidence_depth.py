#!/usr/bin/env python3
"""CI guard for SSc-Tier-1 evidence depth (regression lock-in).

Part of the curation-depth pass (see docs/curation_depth_pass.md). Implements the
open CI-lint item in docs/mi2cast_checklist.md §"Open items".

Every SSc-curated reaction must be **explicitly triaged**. A row is *resolved* when:
  - it carries a primary PMID (status `confirmed` or `proposed`), OR
  - it is honestly reclassified (`conceptual_bridge` / `phenotype_aggregation`), OR
  - it is declared backlog (`untested`, with a candidate pool).

The lint FAILS on:
  - undeclared inference debt — `ECO:0000305` + no PMID + status not in the declared
    set above (i.e. an empty/unset status, or a new uncurated row), and
  - a `confirmed`/`proposed` row with no PMID (a contradiction).

It does NOT fail on `untested` rows — those are tracked backlog, reported as an advisory.
This enforces triage completeness and prevents silent new debt, without demanding a
zero-inference map.

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
