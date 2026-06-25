#!/usr/bin/env python3
"""Build a B/plasma-cell-restricted pseudobulk from the cell-type-resolved
pseudobulk, so module M5 (B-cell / autoreactivity) can be scored in the right
compartment instead of the whole tissue (where B/plasma cells are too rare to
surface in a whole-tissue AUCell ranking).

Aggregates, per donor, the raw counts of every B-lineage cell type into a single
pseudobulk row. Output schema matches scripts/score_aucell.read_pseudobulk_tsv.

  in : analysis/overlay/pseudobulk_multi.tsv  (donor x cell_type x genes)
  out: analysis/overlay/pseudobulk_bplasma.tsv (one row per donor with >=1 B/plasma cell)
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "analysis/overlay/pseudobulk_multi.tsv"
OUT = ROOT / "analysis/overlay/pseudobulk_bplasma.tsv"

B_LINEAGE = {"B", "B_CXCR4", "B_lymphocyte", "Plasma", "plasma_cell"}
META = ["donor_id", "cell_type", "condition", "group", "dataset", "tissue", "lib_size"]


def main() -> None:
    with IN.open() as f:
        rd = csv.reader(f, delimiter="\t")
        hdr = next(rd)
        gi = [i for i, h in enumerate(hdr) if h not in META]
        genes = [hdr[i] for i in gi]
        ci = {h: hdr.index(h) for h in META if h in hdr}
        sums: dict[str, list[float]] = defaultdict(lambda: [0.0] * len(gi))
        meta: dict[str, dict] = {}
        ncells: dict[str, int] = defaultdict(int)
        for row in rd:
            if row[ci["cell_type"]] not in B_LINEAGE:
                continue
            d = row[ci["donor_id"]]
            acc = sums[d]
            for k, i in enumerate(gi):
                acc[k] += float(row[i])
            meta.setdefault(d, {m: row[ci[m]] for m in ("group", "condition", "dataset", "tissue")})
            ncells[d] += 1

    out_hdr = ["donor_id", "cell_type", "condition", "group", "dataset", "tissue", "lib_size"] + genes
    with OUT.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(out_hdr)
        for d, vec in sums.items():
            m = meta[d]
            lib = sum(vec)
            w.writerow([d, "Bplasma", m["condition"], m["group"], m["dataset"], m["tissue"], f"{lib:.0f}"]
                       + [f"{v:.0f}" for v in vec])
    print(f"[bplasma] {len(sums)} donors with >=1 B/plasma row -> {OUT}")
    from collections import Counter
    print("  by dataset/group:",
          dict(Counter((meta[d]["dataset"], meta[d]["group"]) for d in sums)))


if __name__ == "__main__":
    main()
