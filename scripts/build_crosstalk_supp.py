#!/usr/bin/env python3
"""Build manuscript/supplementary/S1_crosstalk_reactions.tsv (E5).

Extracts the 8 inter-module crosstalk reactions from
`curation/ssc_curated_reactions.tsv`, parses the source/target
module from the mechanism description (looks for a "MX→MY" or
"MX -> MY" token), validates that every row carries a PMID and
ECO code, and emits the supplementary table with two extra
columns: `crosstalk_source_module`, `crosstalk_target_module`.

Rows whose ECO code is the weakest IEA-equivalent (ECO:0000305 —
curator inference) or whose PMID is empty are flagged in a
`quality_flag` column for transparent reporting.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SRC = Path("curation/ssc_curated_reactions.tsv")
OUT = Path("manuscript/supplementary/S1_crosstalk_reactions.tsv")
REPORT = Path("manuscript/supplementary/S1_crosstalk_reactions.report.json")

ARROW_RE = re.compile(r"\bM([1-4])\s*(?:→|->)\s*M([1-4])\b")
WEAK_ECO = {"ECO:0000305"}


def parse_arrow(mechanism: str) -> tuple[str, str] | tuple[None, None]:
    m = ARROW_RE.search(mechanism)
    if not m:
        return None, None
    return f"M{m.group(1)}", f"M{m.group(2)}"


def main() -> int:
    if not SRC.exists():
        print(f"ERR: {SRC} not found", file=sys.stderr)
        return 2

    rows_out: list[dict[str, str]] = []
    with SRC.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("module") != "crosstalk":
                continue
            src, tgt = parse_arrow(row.get("mechanism", ""))
            flags: list[str] = []
            if not row.get("pmid"):
                flags.append("no_pmid")
            if row.get("evidence_code") in WEAK_ECO:
                flags.append("eco_weak_305_curator_inference")
            if not src or not tgt:
                flags.append("module_arrow_unparsed")
            out_row = {
                "reaction_id": row["reaction_id"],
                "crosstalk_source_module": src or "",
                "crosstalk_target_module": tgt or "",
                "type": row.get("type", ""),
                "mechanism": row.get("mechanism", ""),
                "reactants": row.get("reactants", ""),
                "products": row.get("products", ""),
                "modifiers": row.get("modifiers", ""),
                "pmid": row.get("pmid", ""),
                "evidence_code": row.get("evidence_code", ""),
                "ssc_relevance": row.get("ssc_relevance", ""),
                "quality_flag": ";".join(flags),
                "notes": row.get("notes", ""),
            }
            rows_out.append(out_row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        fieldnames = list(rows_out[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows_out)

    n = len(rows_out)
    n_with_pmid = sum(1 for r in rows_out if r["pmid"])
    n_eco_weak = sum(1 for r in rows_out if "eco_weak" in r["quality_flag"])
    n_arrow_ok = sum(1 for r in rows_out if r["crosstalk_source_module"])

    edges = sorted({
        (r["crosstalk_source_module"], r["crosstalk_target_module"])
        for r in rows_out
        if r["crosstalk_source_module"] and r["crosstalk_target_module"]
    })

    import json
    REPORT.write_text(json.dumps({
        "n_crosstalk_reactions": n,
        "n_with_pmid": n_with_pmid,
        "n_eco_weak_305": n_eco_weak,
        "n_arrow_parsed": n_arrow_ok,
        "unique_module_edges": [f"{s}→{t}" for s, t in edges],
        "source": str(SRC),
        "out": str(OUT),
    }, indent=2) + "\n")

    print(f"wrote {OUT} — {n} rows")
    print(f"  with PMID:           {n_with_pmid}/{n}")
    print(f"  ECO stricter than 305:{n - n_eco_weak}/{n}")
    print(f"  module arrow parsed: {n_arrow_ok}/{n}")
    print(f"  unique edges:        {', '.join(f'{s}→{t}' for s, t in edges)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
