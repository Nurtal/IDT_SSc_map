#!/usr/bin/env python3
"""Extract the dangling-species list from sink_connectivity output (E13).

A "dangling" species is one whose `nearest_sink_distance` is -1 in
`analysis/network/sink_connectivity.tsv` (i.e. no path to any of
the four phenotype sinks within the configured `max_path = 6`
traversal). The canonical detection logic lives in
`scripts/sink_connectivity.py`; this helper just projects the
relevant rows out so that the manuscript can reference a small,
self-contained file.

Output: `analysis/network/dangling_species.tsv`
Columns: species_id, module, nearest_sink_distance, reason
"""
from __future__ import annotations

import csv
from pathlib import Path

SRC = Path("analysis/network/sink_connectivity.tsv")
OUT = Path("analysis/network/dangling_species.tsv")


def main() -> int:
    if not SRC.exists():
        raise SystemExit(
            f"{SRC} not found — run `make sink-check` first to regenerate it."
        )

    rows: list[dict[str, str]] = []
    with SRC.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("nearest_sink_distance", "") == "-1" and row.get("is_sink") != "yes":
                rows.append({
                    "species_id": row["species_id"],
                    "module": row.get("module", ""),
                    "nearest_sink_distance": "-1",
                    "reason": "no_path_to_sink_within_max_path",
                })

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["species_id", "module", "nearest_sink_distance", "reason"],
            delimiter="\t",
        )
        w.writeheader()
        w.writerows(rows)

    print(f"dangling species: {len(rows)}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
