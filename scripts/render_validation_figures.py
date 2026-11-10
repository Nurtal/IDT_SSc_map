#!/usr/bin/env python3
"""Render the L2 validation figures from committed result files (issue #21).

Every number drawn here is read from a committed artefact; nothing is typed
into this renderer (the F7 hard-coding incident is the precedent).

  figures/F8_independent_validation.{svg,png}
      A  Analysis A: rank-biserial effect (SSc vs HC, singscore) per module ×
         cohort, with the single-cell reference direction and the verdict
         (analysis/validation/external_replication.json)
      B  Analysis B: GWAS fold enrichment per module vs protein-coding genes,
         with padj and the registered prediction
         (analysis/validation/genetic_support.json)
  figures/F3b_community_concordance.{svg,png}
      Fold enrichment of each module in each community holding at least one
      significant cell; significant cells marked. Internal consistency check
      (analysis/network/community_enrichment.tsv).

Run:  python3 scripts/render_validation_figures.py   (or make validation-figures)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "analysis/validation"
FIGS = ROOT / "figures"

INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#a3a29c", "#e4e3df", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834"]          # validated pair (dataviz validator, light surface)
MARKERS = ["o", "s"]                      # secondary encoding for the two cohorts
SEQ = ["#e6f0fc", "#b7d3f6", "#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "ssc-mim",
                     "svg.fonttype": "none", "axes.edgecolor": GRID})


def _clean(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0)


def _save(fig, stem: str) -> None:
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / f"{stem}.svg", facecolor=SURFACE, metadata={"Date": None})
    fig.savefig(FIGS / f"{stem}.png", dpi=300, facecolor=SURFACE, metadata={"Software": None})
    plt.close(fig)


def validation_figure() -> None:
    a = json.loads((VAL / "external_replication.json").read_text())
    b = json.loads((VAL / "genetic_support.json").read_text())
    prim = a["primary_singscore"]
    modules = sorted({r["module"] for r in prim["results"]})
    cohorts = list(a["cohorts"])

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.4, 3.6), facecolor=SURFACE,
                                 gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.25})
    _clean(ax)
    _clean(bx)

    # A — effects per module × cohort
    ys = {m: i for i, m in enumerate(modules)}
    ax.axvline(0, color=MUTED, linewidth=1)
    for k, c in enumerate(cohorts):
        rs = [r for r in prim["results"] if r["source"] == c]
        off = (k - (len(cohorts) - 1) / 2) * 0.22
        ax.scatter([r["effect_size"] for r in rs], [ys[r["module"]] + off for r in rs],
                   s=42, marker=MARKERS[k], color=SERIES[k], edgecolor=SURFACE, linewidth=1.5,
                   zorder=3, label=f"{c} ({a['cohorts'][c]['n_ssc']} SSc / {a['cohorts'][c]['n_hc']} HC)")
    for m in modules:
        ref = a["reference_directions"][m]
        arrow = {"up": "ref ↑", "down": "ref ↓"}.get(ref["direction"], "ref –")
        verdict = prim["verdicts"][m].split(":")[0].replace("_", " ")
        ax.text(-0.97, ys[m], f"{arrow}  {verdict}", va="center", ha="left", color=INK2, fontsize=7.5)
    ax.set_yticks(range(len(modules)), modules)
    ax.set_ylim(len(modules) - 0.5, -0.5)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Rank-biserial effect, SSc vs HC", color=INK2)
    ax.xaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_title("A  Bulk skin replication", loc="left", color=INK, fontsize=9.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, fontsize=7.5,
              labelcolor=INK2, ncol=1, handletextpad=0.3)

    # B — GWAS enrichment per module
    res = {r["module"]: r for r in b["primary_protein_coding"]["results"]}
    for m in modules:
        r = res[m]
        fold = r["effect_size"] or 0.0
        x = np.log2(fold) if fold > 0 else None
        sig = r["extra"]["significant"]
        if x is not None:
            bx.plot([0, x], [ys[m], ys[m]], color=SERIES[0] if sig else MUTED, linewidth=2, zorder=2)
            bx.scatter([x], [ys[m]], s=42, color=SERIES[0] if sig else SURFACE,
                       edgecolor=SERIES[0] if sig else MUTED, linewidth=1.5, zorder=3)
        n = r["extra"]["n_overlap"]
        label = (f"{n} gene{'s' if n != 1 else ''}, padj {r['padj']:.2g}\n"
                 f"predicted: {b['registered_predictions'][m]['prediction']}")
        bx.text(1.04, ys[m], label, transform=bx.get_yaxis_transform(), va="center", color=INK2, fontsize=7.5)
    bx.axvline(0, color=MUTED, linewidth=1)
    bx.set_yticks(range(len(modules)), modules)
    bx.set_ylim(len(modules) - 0.5, -0.5)
    bx.set_xlabel("log2 fold enrichment of SSc GWAS genes", color=INK2)
    bx.xaxis.grid(True, color=GRID, linewidth=0.6)
    bx.set_axisbelow(True)
    gw = b["gwas_catalog"]
    bx.set_title("B  Genetic support", loc="left", color=INK, fontsize=9.5)
    fig.text(0.01, 0.01, f"A: singscore, BH over {len(prim['family']['members'])} module × cohort tests; "
             f"verdict against the single-cell reference (null references: descriptive).\n"
             f"B: GWAS Catalog {gw['downloaded']}, {gw['n_gwas_genes_protein_coding']} protein-coding genes "
             "at p ≤ 5e-8, BH over the five modules; filled = padj ≤ 0.05.", color=INK2, fontsize=6.5)
    fig.subplots_adjust(left=0.06, right=0.76, top=0.9, bottom=0.3)
    _save(fig, "F8_independent_validation")


def community_figure() -> None:
    with (ROOT / "analysis/network/community_enrichment.tsv").open() as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    modules = sorted({r["module"] for r in rows})
    comms = sorted({int(r["community"]) for r in rows if r["significant"] == "true"})
    cell = {(int(r["community"]), r["module"]): r for r in rows}
    folds = [float(r["fold_enrichment"]) for r in rows if int(r["community"]) in comms]
    top = max(folds)
    bins = np.linspace(0, top, len(SEQ) + 1)

    fig, ax = plt.subplots(figsize=(7.2, 2.6), facecolor=SURFACE)
    _clean(ax)
    ax.spines["bottom"].set_visible(False)
    for j, c in enumerate(comms):
        for i, m in enumerate(modules):
            r = cell.get((c, m))
            f = float(r["fold_enrichment"]) if r else 0.0
            colour = SEQ[min(int(np.searchsorted(bins, f, side="right")) - 1, len(SEQ) - 1)] if f > 0 else SURFACE
            ax.add_patch(plt.Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, color=colour,
                                       ec=INK if r and r["significant"] == "true" else GRID,
                                       lw=1.4 if r and r["significant"] == "true" else 0.6))
    ax.set_xlim(-0.6, len(comms) - 0.4)
    ax.set_ylim(len(modules) - 0.5, -0.5)
    ax.set_xticks(range(len(comms)), [str(c) for c in comms])
    ax.set_yticks(range(len(modules)), modules)
    ax.set_xlabel("Community (greedy modularity), those with ≥ 1 significant module", color=INK2)
    sig = sum(r["significant"] == "true" for r in rows)
    ax.set_title(f"Module enrichment in network communities: {sig} of {len(rows)} tests at q < 0.05",
                 loc="left", color=INK, fontsize=9.5)
    fig.text(0.01, 0.01, "Internal consistency check, not independent evidence: communities are detected on the "
             f"curated graph. Fill: fold enrichment (0–{top:.1f}); outlined: BH q < 0.05.",
             color=INK2, fontsize=6.5)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.85, bottom=0.27)
    _save(fig, "F3b_community_concordance")


def main() -> int:
    validation_figure()
    community_figure()
    print("[OK] wrote figures/F8_independent_validation.* and figures/F3b_community_concordance.*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
