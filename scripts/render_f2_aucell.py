#!/usr/bin/env python3
"""E20 — Re-render Figure 2 with v1.1 AUCell scores + significance bars.

The v1.0 `figures/F2_multi_overlay.svg` is kept in place for sensitivity
comparison. This v1.1 figure uses the sign-blinded AUCell module scores
(`analysis/overlay/patient_module_scores_aucell.tsv`, E2) and adds
per-(dataset, module) Mann–Whitney *p*-values as significance asterisks
on each panel header. The mRSS row that R2-C1 and the editor's E20
asked for is *not* added — 0/773 donor-samples carry mRSS, age, sex,
disease duration, or ANA in the source GEO deposits
(`analysis/clinical/CLINICAL_METADATA_GAP.md`).

Output:
  figures/F2_multi_overlay_aucell.svg / .png

To regenerate:
  make f2-aucell
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

SRC = Path("analysis/overlay/patient_module_scores_aucell.tsv")
OUT_SVG = Path("figures/F2_multi_overlay_aucell.svg")
OUT_PNG = Path("figures/F2_multi_overlay_aucell.png")

DATASETS = [
    ("tabib2021",  "Skin biopsies\n(Tabib, GSE138669)"),
    ("gse195452",  "Skin multiome\n(Gur, GSE195452)"),
    ("gse210395",  "PBMC\n(GSE210395)"),
    ("gse128169",  "Lung ILD\n(Morse, GSE128169)"),
]
MODULES = ["M1", "M2", "M3", "M4", "ssc_tier1"]
MODULE_LABELS = ["M1\nIFN-I", "M2\nTGF-β", "M3\nEndoMT", "M4\nIL-6 Th2", "SSc\nTier-1"]


def stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 1e-4: return "***"
    if p < 1e-3: return "**"
    if p < 0.05: return "*"
    return ""


def main() -> int:
    df = pd.read_csv(SRC, sep="\t")
    n_panels = len(DATASETS)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.5 * n_panels, 7.0),
                              dpi=100, gridspec_kw={"wspace": 0.55})
    if n_panels == 1:
        axes = [axes]

    for ax, (ds, label) in zip(axes, DATASETS):
        sub = df[df["dataset"] == ds].copy()
        if sub.empty:
            ax.set_visible(False)
            continue
        sub = sub.sort_values(["group", "donor_id"], ascending=[False, True])
        n_ssc = int((sub["group"] == "SSc").sum())
        n_hc  = int((sub["group"] == "HC").sum())

        matrix = sub[MODULES].to_numpy(dtype=float)
        donor_ids = sub["donor_id"].tolist()

        # AUCell scores in [0, 1]; tight asymmetric scale around the
        # population median keeps the diverging cmap readable.
        vmax = max(0.30, float(np.nanmax(matrix)) if matrix.size else 0.30)
        im = ax.imshow(matrix, aspect="auto", cmap="viridis", vmin=0, vmax=vmax)
        ax.set_xticks(range(len(MODULES)))
        ax.set_xticklabels(MODULE_LABELS, rotation=0, ha="center", fontsize=8)
        # Donor labels suppressed when too dense (Gur has 154).
        if len(donor_ids) <= 25:
            ax.set_yticks(range(len(donor_ids)))
            ax.set_yticklabels(donor_ids, fontsize=6)
        else:
            ax.set_yticks([0, n_ssc, len(donor_ids) - 1])
            ax.set_yticklabels(["SSc#1", f"HC#1 (n_SSc={n_ssc})",
                                f"HC#{n_hc}"], fontsize=7)
        if 0 < n_ssc < len(sub):
            ax.axhline(n_ssc - 0.5, color="white", linewidth=1.4)

        # Per-module Mann-Whitney sig stars on x-tick labels.
        annot = []
        for mod in MODULES:
            ssc = sub[sub["group"] == "SSc"][mod]
            hc  = sub[sub["group"] == "HC"][mod]
            try:
                _, p = mannwhitneyu(ssc, hc, alternative="two-sided")
            except ValueError:
                p = float("nan")
            annot.append((mod, p, stars(p)))
        # Stars under the x-tick labels
        for i, (mod, p, s) in enumerate(annot):
            if s:
                ax.text(i, -1.1, s, ha="center", va="bottom",
                        fontsize=11, fontweight="bold",
                        color="firebrick")
            ax.text(i, len(sub) + 0.4 + 0.25 * len(donor_ids[:1]),  # below x-axis
                    f"p={p:.2g}" if np.isfinite(p) else "—",
                    ha="center", va="top", fontsize=6, color="dimgrey")

        ax.set_title(f"{label}\n(n = {n_ssc} SSc / {n_hc} HC)", fontsize=9)
        plt.colorbar(im, ax=ax, shrink=0.65, label="AUCell score\n(top 5% rank)")

    fig.suptitle(
        "Figure 2 — SSc-MIM per-donor AUCell module activation across 4 datasets\n"
        "(*** p<1e-4, ** p<1e-3, * p<0.05, two-sided Mann–Whitney SSc vs HC;\n"
        "mRSS row deliberately omitted — 0/773 GEO samples carry clinical metadata, see §4.4)",
        fontsize=10, y=0.995)
    plt.tight_layout(rect=(0, 0, 1, 0.92))

    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_SVG, format="svg", bbox_inches="tight")
    fig.savefig(OUT_PNG, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_SVG} + {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
