#!/usr/bin/env python3
"""Supplementary figure: SSc-Tier-1 evidence-depth pass (curation rigour).

Three panels:
  A. SSc-Tier-1 citation coverage before vs after the 2026-06 depth pass.
  B. The 85 SSc reactions by ratification provenance (who/what verified each).
  C. Evidence grade by provenance layer (Reactome backbone vs SSc-Tier-1).

Outputs figures/F_supp_evidence_depth.{svg,png}.
Run: python3 scripts/render_evidence_depth_figure.py  (or make evidence-figure)
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "analysis/curation/evidence_stratification.json"
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
OUT = ROOT / "figures/F_supp_evidence_depth"

C = {"orig": "#4477AA", "ft": "#228833", "abs": "#66CCEE", "recl": "#CCBB44",
     "before": "#BBBBBB", "after": "#228833", "backbone": "#AA3377", "ssc": "#228833"}


def main() -> None:
    strat = json.loads(STRAT.read_text())
    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    rat = Counter()
    for r in rows:
        t = (r.get("ratification", "") or "").strip()
        if t.startswith("human"):
            rat["orig"] += 1
        elif "full-text" in t:
            rat["ft"] += 1
        elif "reclassification" in t:
            rat["recl"] += 1
        elif t.startswith("AI"):
            rat["abs"] += 1
        else:
            rat["orig"] += 1

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    fig.suptitle("SSc-MIM — SSc-Tier-1 curation evidence depth", fontsize=13, fontweight="bold")

    # Panel A: coverage before vs after
    a = axes[0]
    a.bar(["before\n(2026-05)", "after\n(2026-06)"], [47.1, 88.2],
          color=[C["before"], C["after"]], width=0.6)
    for x, v, n in [(0, 47.1, "40/85"), (1, 88.2, "75/85")]:
        a.text(x, v + 1.5, f"{v:.0f}%\n{n}", ha="center", fontsize=10, fontweight="bold")
    a.set_ylim(0, 100)
    a.set_ylabel("% SSc-Tier-1 reactions with a primary PMID")
    a.set_title("A · Citation coverage", fontsize=11, loc="left")
    a.spines[["top", "right"]].set_visible(False)

    # Panel B: ratification provenance (stacked single bar)
    b = axes[1]
    order = [("orig", "human-original (40)"), ("ft", "AI, full-text-verified (27)"),
             ("abs", "AI, abstract-verified (8)"), ("recl", "AI reclassification (10)")]
    bottom = 0
    for key, label in order:
        b.bar(0, rat[key], bottom=bottom, width=0.5, color=C[key], label=label)
        if rat[key]:
            b.text(0, bottom + rat[key] / 2, str(rat[key]), ha="center", va="center",
                   color="white", fontweight="bold")
        bottom += rat[key]
    b.set_xlim(-0.6, 0.6)
    b.set_xticks([])
    b.set_ylabel("SSc-Tier-1 reactions (n=85)")
    b.set_title("B · How each edge was verified", fontsize=11, loc="left")
    b.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), fontsize=8, frameon=False)
    b.spines[["top", "right"]].set_visible(False)

    # Panel C: evidence grade by layer
    c = axes[2]
    bb = strat["provenance"]["reactome_backbone"]
    sc = strat["provenance"]["ssc_tier1"]
    groups = ["with PMID", "experimental/\nreview ECO"]
    x = range(len(groups))
    w = 0.38
    c.bar([i - w / 2 for i in x], [bb["pct_with_pmid"], bb["pct_experimental_eco"]],
          width=w, color=C["backbone"], label=f"Reactome backbone (n={bb['n_reactions']})")
    c.bar([i + w / 2 for i in x], [sc["pct_with_pmid"], sc["pct_experimental_eco"]],
          width=w, color=C["ssc"], label=f"SSc-Tier-1 (n={sc['n_reactions']})")
    c.set_xticks(list(x))
    c.set_xticklabels(groups)
    c.set_ylim(0, 100)
    c.set_ylabel("% of reactions")
    c.set_title("C · Evidence grade by layer", fontsize=11, loc="left")
    c.legend(fontsize=8, frameon=False)
    c.spines[["top", "right"]].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(f"{OUT}.svg")
    fig.savefig(f"{OUT}.png", dpi=300)
    print(f"[evidence-figure] wrote {OUT}.{{svg,png}}  (ratification: {dict(rat)})")


if __name__ == "__main__":
    main()
