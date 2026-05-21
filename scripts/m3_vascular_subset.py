#!/usr/bin/env python3
"""E8 — M3 within-vascular-subset analysis (Gur 2022).

Reviewer R2-M3 asked for restriction of the M3 (Notch/EndoMT/vasculopathy)
module analysis to the cell populations where EndoMT actually happens —
the dermal vascular endothelium and the pericyte sleeve. Gur 2022
(GSE195452) provides published cell-type labels for exactly these
populations:

    Vascular_ACKR1  — venular endothelial cells
    Vascular_RBP7   — capillary / arteriolar endothelial cells
    Peri_RGS5       — quiescent pericytes
    Peri_TGFBI      — activated pericytes (the EndoMT-prone subset)

This script extracts, from the v1.1 mixed-effects DEG output, the
per-(cluster, gene) statistics for a curator-chosen M3 panel — the
canonical EndoMT axis — across these four clusters. It writes a tidy
TSV and a 2-panel supplementary figure (F5):

  panel A — heatmap of log₂FC per (cluster × gene)
  panel B — −log₁₀ padj_dataset for the same matrix

Outputs:
  analysis/overlay/m3_vascular_subset.tsv
  figures/F5_M3_vascular.{svg,png}

The "M3 panel" is the set of genes named in the manuscript §3.2 /
§4.5 EndoMT discussion + the curated M3 Tier-1 entities present in
the MIM denominator. Genes absent from the DEG output are emitted
with NaN.
"""
from __future__ import annotations

import csv
from pathlib import Path

DEG = Path("analysis/overlay/cluster_deg_multi_v11.tsv")
OUT_TSV = Path("analysis/overlay/m3_vascular_subset.tsv")
FIG_SVG = Path("figures/F5_M3_vascular.svg")
FIG_PNG = Path("figures/F5_M3_vascular.png")

VASCULAR_CLUSTERS = ("Vascular_ACKR1", "Vascular_RBP7",
                     "Peri_RGS5", "Peri_TGFBI")

# Canonical M3 EndoMT panel — order matters for figure readability:
#   first the EndoMT transcription factors (SNAI/ZEB/TWIST/PRRX),
#   then mesenchymal acquisition (ACTA2, FN1, CDH2, FAP, S100A4),
#   then endothelial loss (CDH5, PECAM1),
#   then Notch axis (NOTCH1/3, JAG1/2, DLL1/4, HES1, HEY1, DTX1, MAML1, NUMB),
#   then endothelin / vascular tone (EDN1, EDNRA, EDNRB, NOS3, VEGFA, ANGPT2),
#   then contractility (ROCK1, ROCK2, RHOA).
M3_PANEL = [
    "SNAI1", "SNAI2", "ZEB1", "ZEB2", "TWIST1", "PRRX1",
    "ACTA2", "FN1", "CDH2", "FAP", "S100A4",
    "CDH5", "PECAM1",
    "NOTCH1", "NOTCH3", "JAG1", "JAG2", "DLL1", "DLL4",
    "HES1", "HEY1", "DTX1", "MAML1", "NUMB",
    "EDN1", "EDNRA", "EDNRB", "NOS3", "VEGFA", "ANGPT2",
    "ROCK1", "ROCK2", "RHOA",
]


def load_deg() -> dict[tuple[str, str], dict[str, str]]:
    """Return {(cluster, hgnc): row} for Gur (skin_gur) rows only."""
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    with DEG.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("dataset") != "gse195452":
                continue
            key = (row["cluster"], row["hgnc"])
            by_key[key] = row
    return by_key


def main() -> int:
    deg = load_deg()

    # Build the (cluster × gene) table
    rows_out: list[dict[str, str]] = []
    import math
    for ct in VASCULAR_CLUSTERS:
        for g in M3_PANEL:
            row = deg.get((ct, g))
            rows_out.append({
                "cluster":   ct,
                "hgnc":      g,
                "log2fc":    row["log2fc"] if row else "",
                "pvalue":    row["pvalue"] if row else "",
                "padj":      row["padj_dataset"] if row else "",
                "n_donors_ssc": row["n_donors_ssc"] if row else "",
                "n_donors_hc":  row["n_donors_hc"] if row else "",
                "in_deg_output": "yes" if row else "no",
            })

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()), delimiter="\t")
        w.writeheader(); w.writerows(rows_out)
    print(f"wrote {OUT_TSV} ({len(rows_out)} rows)")

    # Per-cluster summary
    print()
    print("Per-cluster M3 panel coverage (genes tested at q ≤ 0.05):")
    print("=" * 75)
    sig_genes_by_cluster = {ct: [] for ct in VASCULAR_CLUSTERS}
    for ct in VASCULAR_CLUSTERS:
        n_tested = 0; n_sig = 0
        for g in M3_PANEL:
            row = deg.get((ct, g))
            if row:
                n_tested += 1
                try:
                    padj = float(row["padj_dataset"])
                    if padj <= 0.05:
                        n_sig += 1
                        sig_genes_by_cluster[ct].append(
                            (g, float(row["log2fc"]), padj))
                except ValueError:
                    pass
        print(f"  [{ct}] {n_sig}/{n_tested} significant of {len(M3_PANEL)} panel members")
        for g, lfc, padj in sorted(sig_genes_by_cluster[ct], key=lambda x: x[2]):
            sign = "+" if lfc > 0 else "−"
            print(f"      {sign} {g:<8s}  log2FC={lfc:+.3f}  padj={padj:.2e}")

    # Figure
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not available; skipping figure", flush=True)
        return 0

    M = np.full((len(M3_PANEL), len(VASCULAR_CLUSTERS)), np.nan)
    P = np.full((len(M3_PANEL), len(VASCULAR_CLUSTERS)), np.nan)
    for j, ct in enumerate(VASCULAR_CLUSTERS):
        for i, g in enumerate(M3_PANEL):
            row = deg.get((ct, g))
            if not row:
                continue
            try:
                M[i, j] = float(row["log2fc"])
                p = float(row["padj_dataset"])
                P[i, j] = -np.log10(max(p, 1e-300))
            except ValueError:
                pass

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 9.0),
                                   gridspec_kw={"wspace": 0.55})
    # log2FC heatmap with diverging cmap
    vmax = max(2.0, np.nanmax(np.abs(M)) if np.any(~np.isnan(M)) else 2.0)
    im1 = ax1.imshow(M, aspect="auto", cmap="RdBu_r",
                      vmin=-vmax, vmax=vmax)
    ax1.set_xticks(range(len(VASCULAR_CLUSTERS)))
    ax1.set_xticklabels(VASCULAR_CLUSTERS, rotation=35, ha="right")
    ax1.set_yticks(range(len(M3_PANEL)))
    ax1.set_yticklabels(M3_PANEL, fontsize=8)
    ax1.set_title("A. M3 panel log₂FC\n(SSc vs HC, mixed-effects NB GLM)", fontsize=9)
    cb1 = fig.colorbar(im1, ax=ax1, shrink=0.6, label="log₂FC")

    # -log10(padj) heatmap
    pmax = np.nanmax(P[np.isfinite(P)]) if np.any(np.isfinite(P)) else 1.0
    pmax = max(pmax, -np.log10(0.05))
    im2 = ax2.imshow(P, aspect="auto", cmap="viridis",
                      vmin=0, vmax=pmax)
    ax2.set_xticks(range(len(VASCULAR_CLUSTERS)))
    ax2.set_xticklabels(VASCULAR_CLUSTERS, rotation=35, ha="right")
    ax2.set_yticks(range(len(M3_PANEL)))
    ax2.set_yticklabels(M3_PANEL, fontsize=8)
    ax2.set_title("B. M3 panel −log₁₀(padj)\n(BH-FDR per dataset)", fontsize=9)
    cb2 = fig.colorbar(im2, ax=ax2, shrink=0.6, label="−log₁₀(padj)")

    # Overlay padj ≤ 0.05 contour as black dots
    for ax, mat in [(ax2, P)]:
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                if np.isfinite(mat[i, j]) and mat[i, j] >= -np.log10(0.05):
                    ax.plot(j, i, "o", markersize=2.5, color="white",
                            markeredgecolor="black", markeredgewidth=0.3)

    fig.suptitle(
        "Supplementary Figure F5 — M3 EndoMT panel in Gur 2022 vascular subsets\n"
        "(Vascular_ACKR1 venular EC · Vascular_RBP7 capillary EC · "
        "Peri_RGS5 quiescent pericyte · Peri_TGFBI activated pericyte)",
        fontsize=10, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    FIG_SVG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_SVG, format="svg", bbox_inches="tight")
    fig.savefig(FIG_PNG, format="png", dpi=300, bbox_inches="tight")
    print(f"wrote {FIG_SVG} + {FIG_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
