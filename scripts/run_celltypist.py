#!/usr/bin/env python3
"""E9 — CellTypist harmonisation against published / Leiden cell-type labels.

Reviewer R2-M5 asked for CellTypist (or Azimuth) harmonised cell labels
across the four overlay datasets with Cohen's κ vs the published
labels. This script runs the focused single-dataset version on
Tabib 2021 (GSE138669) skin, which is the dataset where the
fibroblast / myofibroblast / endothelial distinction is most
contested and most relevant to the SSc-MIM M2 / M3 narrative.

Strategy:
  1. Re-load the 22 Tabib .h5 files (same loader as
     `scripts/build_overlay_multi.process_tabib`).
  2. Apply the same QC + normalisation + Leiden (resolution 0.35),
     reproducing the manuscript's per-cluster labels.
  3. Run CellTypist with `Adult_Human_Skin.pkl` (majority-voting
     across the kNN), assign a predicted cell type to every cell.
  4. Compute Cohen's κ between (a) the marker-rule-based label that
     `build_overlay_multi._cluster_to_celltype` assigns and (b) the
     CellTypist majority label.
  5. Write a per-(cluster, CellTypist-label) confusion matrix to
     `analysis/overlay/celltypist_labels.tsv` and a summary JSON.

Runtime: ~10–15 min on a 16-core laptop (mostly the Leiden step).

Output:
  analysis/overlay/celltypist_labels.tsv
  analysis/overlay/celltypist_kappa.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import celltypist
from celltypist import models
from sklearn.metrics import cohen_kappa_score, adjusted_rand_score
from scipy.sparse import issparse


# CellTypist Adult_Human_Skin label → coarse skin cell type. The
# CellTypist taxonomy is finer-grained (F1/F2/F3 fibroblast subtypes,
# Differentiated/Undifferentiated KC, VE1/VE2/VE3 vascular endothelium,
# Pericyte_1/2, Macro_1/2, etc.) than the 6-class marker rule used in
# build_overlay_multi. To compute a meaningful Cohen's κ on a *common
# label space*, we collapse the CellTypist output to the same 6
# coarse classes via this table. Adjusted Rand Index (ARI) on the
# raw partitions is also reported (label-name-invariant).
CT_TO_COARSE: dict[str, str] = {
    # Fibroblasts
    "F1": "fibroblast", "F2": "fibroblast", "F3": "fibroblast",
    "F4": "fibroblast", "F5": "fibroblast",
    # Pericytes — biologically myofibroblast-adjacent and the M3
    # vascular substrate; we collapse them onto the marker class
    # "myofibroblast_FAP_CTHRC1" since the marker rule places
    # FAP+/ACTA2+ cells there.
    "Pericyte_1": "myofibroblast_FAP_CTHRC1",
    "Pericyte_2": "myofibroblast_FAP_CTHRC1",
    # Vascular endothelium
    "VE1": "endothelial_vascular", "VE2": "endothelial_vascular",
    "VE3": "endothelial_vascular", "LE1": "endothelial_vascular",
    "LE2": "endothelial_vascular",
    # Keratinocytes (any compartment)
    "Differentiated_KC": "keratinocyte",
    "Undifferentiated_KC": "keratinocyte",
    "KC": "keratinocyte",
    # T lymphocytes
    "Th": "T_lymphocyte", "Tc": "T_lymphocyte", "Treg": "T_lymphocyte",
    "ILC1_NK": "T_lymphocyte", "ILC1_3": "T_lymphocyte",
    "ILC2": "T_lymphocyte",
    # Macrophages / DCs / mast / B / plasma — collapse to macrophage_dermal
    # since the marker rule treats CD68+/C1QA+/LYZ+ as macrophage and
    # has no separate DC class.
    "Macro_1": "macrophage_dermal", "Macro_2": "macrophage_dermal",
    "Inf_mac": "macrophage_dermal",
    "MigDC": "macrophage_dermal", "Mast_cell": "macrophage_dermal",
    "DC1": "macrophage_dermal", "DC2": "macrophage_dermal",
    "LC": "macrophage_dermal", "moDC": "macrophage_dermal",
    "Plasma": "macrophage_dermal", "B_cell": "macrophage_dermal",
    "B": "macrophage_dermal",
    # Melanocytes / Schwann — not represented in marker rule; map to
    # "unknown" so they don't false-inflate the marker-class κ.
    "Melanocyte": "unknown",
    "Schwann_1": "unknown", "Schwann_2": "unknown",
    "MC": "unknown",
}

# Match build_overlay_multi's donor → condition map for GSE138669
TABIB_DONOR_COND = {
    "SC1":  "HC",  "SC2":  "HC",  "SC4":  "HC",  "SC5":  "HC",
    "SC18": "HC",  "SC32": "HC",  "SC33": "HC",  "SC34": "HC",
    "SC50": "HC",  "SC68": "HC",
    "SC19": "SSc", "SC49": "SSc", "SC60": "SSc", "SC69": "SSc",
    "SC70": "SSc", "SC86": "SSc", "SC119":"SSc", "SC124":"SSc",
    "SC125":"SSc", "SC185":"SSc", "SC188":"SSc", "SC189":"SSc",
}

DATA_DIR = Path("data/raw/tabib2021")
OUT_TSV = Path("analysis/overlay/celltypist_labels.tsv")
OUT_JSON = Path("analysis/overlay/celltypist_kappa.json")
MODEL = "Adult_Human_Skin.pkl"


def assign_marker_label(scores: dict[str, float]) -> str:
    if not scores:
        return "unknown"
    best, _ = max(scores.items(), key=lambda kv: kv[1])
    return best


SKIN_MARKERS = {
    "fibroblast":               ["COL1A1", "COL1A2", "COL3A1", "DCN", "LUM"],
    "myofibroblast_FAP_CTHRC1": ["ACTA2", "FAP",   "CTHRC1", "POSTN", "COMP"],
    "endothelial_vascular":     ["PECAM1", "CDH5", "VWF",   "ACKR1"],
    "keratinocyte":             ["KRT14", "KRT5",  "KRT1",  "KRT10"],
    "T_lymphocyte":             ["CD3D",  "CD3E",  "CD2",   "TRAC"],
    "macrophage_dermal":        ["CD68",  "C1QA",  "C1QB",  "LYZ"],
}


def marker_label_for_cluster(adata, cluster_col: str = "leiden") -> dict[str, str]:
    """Score each cluster against the skin marker dict, return marker label."""
    labels: dict[str, str] = {}
    for ct in sorted(adata.obs[cluster_col].cat.categories):
        sub = adata[adata.obs[cluster_col] == ct]
        if sub.n_obs == 0:
            continue
        scores: dict[str, float] = {}
        for ctype, marks in SKIN_MARKERS.items():
            present = [g for g in marks if g in adata.var_names]
            if not present:
                continue
            X = sub[:, present].X
            if issparse(X):
                X = X.toarray()
            scores[ctype] = float(np.mean(X))
        labels[ct] = assign_marker_label(scores)
    return labels


def main() -> int:
    h5_files = sorted(DATA_DIR.glob("*.h5"))
    if not h5_files:
        raise SystemExit(f"No .h5 files under {DATA_DIR}")

    print(f"loading {len(h5_files)} Tabib .h5 files …")
    adatas = []
    rx = re.compile(r"_(SC\d+)raw")
    for h5 in h5_files:
        m = rx.search(h5.name)
        donor = m.group(1) if m else h5.stem
        ad = sc.read_10x_h5(str(h5))
        ad.var_names_make_unique()
        ad.obs_names = [f"{donor}_{bc}" for bc in ad.obs_names]
        ad.obs["donor_id"] = donor
        ad.obs["condition"] = TABIB_DONOR_COND.get(donor, "unknown")
        adatas.append(ad)
    adata = sc.concat(adatas, merge="same")
    print(f"  raw concat: {adata.n_obs} cells × {adata.n_vars} genes")

    # QC matching build_overlay_multi defaults
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True,
                                percent_top=None, log1p=False)
    adata = adata[(adata.obs["n_genes_by_counts"] >= 200) &
                  (adata.obs["n_genes_by_counts"] <= 6000) &
                  (adata.obs["pct_counts_mt"] < 25)].copy()
    sc.pp.filter_genes(adata, min_cells=10)
    print(f"  after QC:   {adata.n_obs} cells × {adata.n_vars} genes")

    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    # Stash the log1p (un-scaled) expression for CellTypist before scaling
    # breaks the CPM/log1p assumption.
    adata.raw = adata
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=30, mask_var="highly_variable")
    sc.pp.neighbors(adata, n_neighbors=20, n_pcs=20)
    sc.tl.leiden(adata, resolution=0.35, flavor="igraph",
                  directed=False, n_iterations=2)
    print(f"  Leiden clusters: {adata.obs['leiden'].nunique()}")

    # Marker-rule labels per cluster (build_overlay_multi style)
    marker_label = marker_label_for_cluster(adata)
    adata.obs["marker_label"] = adata.obs["leiden"].map(marker_label)

    # CellTypist
    print(f"running CellTypist {MODEL} …")
    try:
        mdl = models.Model.load(model=MODEL)
    except Exception:
        models.download_models(model=[MODEL])
        mdl = models.Model.load(model=MODEL)

    # CellTypist needs the un-scaled log-normalised data
    adata_ct = adata.copy()
    if hasattr(adata_ct, "raw") and adata_ct.raw is not None:
        adata_ct = adata_ct.raw.to_adata()
    pred = celltypist.annotate(adata_ct, model=mdl,
                                majority_voting=True,
                                over_clustering=adata.obs["leiden"].astype(str).values)
    adata.obs["celltypist_pred"]    = pred.predicted_labels.predicted_labels.values
    adata.obs["celltypist_majority"] = pred.predicted_labels.majority_voting.values

    # Collapse the CellTypist labels to the same 6-class coarse space
    # as the marker rule (CT_TO_COARSE), then compute Cohen's κ on a
    # common label vocabulary. Also report Adjusted Rand Index (ARI)
    # on the raw partitions, which is label-name-invariant.
    adata.obs["celltypist_coarse"] = (
        adata.obs["celltypist_majority"]
            .map(lambda s: CT_TO_COARSE.get(str(s), "unknown"))
    )
    # Cell-level κ on coarse space + ARI on raw partitions
    cells_kappa_coarse = cohen_kappa_score(adata.obs["marker_label"],
                                            adata.obs["celltypist_coarse"])
    cells_ari_raw = adjusted_rand_score(adata.obs["marker_label"],
                                         adata.obs["celltypist_majority"])
    cells_kappa_raw = cohen_kappa_score(adata.obs["marker_label"],
                                         adata.obs["celltypist_majority"])

    # Cluster-level: one marker label + one majority CellTypist label
    # per Leiden cluster.
    cluster_table = (adata.obs
                       .groupby("leiden", observed=True)
                       .agg(marker=("marker_label", "first"),
                            celltypist=("celltypist_majority",
                                        lambda s: s.value_counts().index[0]),
                            celltypist_coarse=("celltypist_coarse",
                                                lambda s: s.value_counts().index[0]),
                            n_cells=("leiden", "size")))
    cluster_kappa_coarse = cohen_kappa_score(cluster_table["marker"],
                                              cluster_table["celltypist_coarse"])
    cluster_ari = adjusted_rand_score(cluster_table["marker"],
                                       cluster_table["celltypist"])
    cluster_kappa_raw = cohen_kappa_score(cluster_table["marker"],
                                           cluster_table["celltypist"])

    # Confusion matrix
    confusion = (adata.obs
                   .groupby(["leiden", "marker_label", "celltypist_majority"],
                            observed=True)
                   .size()
                   .reset_index(name="n_cells"))
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    confusion.to_csv(OUT_TSV, sep="\t", index=False)

    summary = {
        "dataset": "tabib2021 (GSE138669)",
        "celltypist_model": MODEL,
        "n_cells_kept": int(adata.n_obs),
        "n_leiden_clusters": int(adata.obs["leiden"].nunique()),
        "n_marker_labels":  int(adata.obs["marker_label"].nunique()),
        "n_celltypist_labels": int(adata.obs["celltypist_majority"].nunique()),
        "n_celltypist_coarse_labels": int(adata.obs["celltypist_coarse"].nunique()),
        "cells_kappa_marker_vs_celltypist_raw": round(float(cells_kappa_raw), 3),
        "cells_kappa_marker_vs_celltypist_coarse": round(float(cells_kappa_coarse), 3),
        "cells_ari_marker_vs_celltypist_raw": round(float(cells_ari_raw), 3),
        "cluster_kappa_marker_vs_celltypist_raw": round(float(cluster_kappa_raw), 3),
        "cluster_kappa_marker_vs_celltypist_coarse": round(float(cluster_kappa_coarse), 3),
        "cluster_ari_marker_vs_celltypist_raw": round(float(cluster_ari), 3),
        "interpretation": (
            "Cohen's κ on the *coarse* label space (marker rule and "
            "CellTypist majority both projected to the 6 marker classes via "
            "CT_TO_COARSE) is the meaningful agreement number: ≥ 0.6 = "
            "strong, ≥ 0.4 = moderate. Cohen's κ on the *raw* label spaces "
            "is uninformative because the two vocabularies do not overlap "
            "in string identity (e.g. CellTypist 'F2' ≠ marker rule "
            "'fibroblast'). The Adjusted Rand Index (ARI) on raw "
            "partitions is label-name-invariant and reflects whether the "
            "two classifiers agree on the *grouping* of cells, regardless "
            "of how they name each group."
        ),
        "cluster_table": cluster_table.reset_index().to_dict(orient="records"),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")

    print()
    print(f"cell-level   κ raw    : {cells_kappa_raw:.3f}  (uninformative — label spaces don't overlap)")
    print(f"cell-level   κ coarse : {cells_kappa_coarse:.3f}  (after CT_TO_COARSE projection)")
    print(f"cell-level   ARI raw  : {cells_ari_raw:.3f}  (label-name-invariant)")
    print(f"cluster      κ coarse : {cluster_kappa_coarse:.3f}")
    print(f"cluster      ARI raw  : {cluster_ari:.3f}")
    print(f"wrote {OUT_TSV} + {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
