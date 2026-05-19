#!/usr/bin/env python3
"""Multi-dataset SSc-MIM overlay pipeline.

Integrates up to three open-access scRNA-seq datasets:
  1. Tabib 2021 (GSE138669)  — SSc skin, 10x .h5 per sample
  2. GSE210395               — SSc PBMC pDC+monocyte enriched, long-format TSV
  3. GSE128169               — SSc-ILD lung, 10x MEX sparse per sample

Each dataset is processed with the same pseudobulk DEG pipeline
(QC → normalise → PCA → Leiden → annotate → Wilcoxon SSc vs HC).
Results are merged into:
  analysis/overlay/cluster_deg.tsv             (all datasets, dataset column added)
  analysis/overlay/patient_module_scores.tsv   (all donors, dataset column added)
  analysis/overlay/build_overlay_multi.report.json
  figures/F2_multi_overlay.svg / .png

Falls back to synthetic projection for any dataset whose raw data is absent.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tarfile
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("matplotlib + numpy required", file=sys.stderr)
    sys.exit(2)

# ── Dataset registry ───────────────────────────────────────────────────────────

# Tabib 2021: donor → condition (already in build_overlay.py, reproduced here)
TABIB_DONOR_COND: dict[str, str] = {
    "SC1":"HC","SC2":"SSC","SC4":"HC","SC5":"SSC","SC18":"HC","SC19":"SSC",
    "SC32":"HC","SC33":"HC","SC34":"HC","SC49":"SSC","SC50":"HC","SC60":"SSC",
    "SC68":"HC","SC69":"SSC","SC70":"SSC","SC86":"SSC","SC119":"SSC",
    "SC124":"HC","SC125":"HC","SC185":"SSC","SC188":"SSC","SC189":"SSC",
}

# GSE210395: sample index in barcode suffix → donor + condition
GSE210395_INDEX: dict[str, tuple[str, str]] = {
    "B1": ("HD1","HC"), "B2": ("HD2","HC"), "B3": ("HD3","HC"), "B4": ("HD4","HC"),
    "B5": ("SSc1","SSC"), "B6": ("SSc2","SSC"), "B7": ("SSc3","SSC"), "B8": ("SSc4","SSC"),
}

# GSE128169: sample name → condition (derived from GEO soft file)
GSE128169_DONOR_COND: dict[str, str] = {
    "SC45NOR":"HC","SC56NOR":"HC","SC59NOR":"HC","SC155NORLOW":"HC","SC156NORUP":"HC",
    "SC51SSCLOW":"SSC","SC52SSCUP":"SSC","SC63SSCLOW":"SSC","SC64SSCUP":"SSC",
}

# ── Cell-type marker sets (tissue-specific) ────────────────────────────────────

SKIN_MARKERS: dict[str, list[str]] = {
    "fibroblast_SFRP2_progenitor": ["SFRP2","DPP4","PRSS23","PDGFRA"],
    "myofibroblast_FAP_CTHRC1":    ["ACTA2","FAP","CTHRC1","COMP"],
    "fibroblast_other":            ["COL1A1","COL3A1","PDGFRA"],
    "endothelial_vascular":        ["CDH5","PECAM1","VWF","CLDN5"],
    "endothelial_lymphatic":       ["LYVE1","PROX1","PDPN"],
    "keratinocyte":                ["KRT5","KRT14","KRT1","DSG3"],
    "T_lymphocyte":                ["CD3D","CD3E","CD4","CD8A"],
    "B_lymphocyte":                ["MS4A1","CD19","CD79A","IGHM"],
    "macrophage_dermal":           ["CD68","MRC1","CD163","CSF1R"],
}

PBMC_MARKERS: dict[str, list[str]] = {
    "pDC":                    ["CLEC4C","LILRA4","SIGLEC1","GZMB","IL3RA"],
    "cDC1":                   ["XCR1","THBD","CADM1","CLEC9A"],
    "cDC2":                   ["CD1C","CLEC10A","FCER1A","CD14"],
    "monocyte_classical":     ["CD14","LYZ","S100A8","S100A9","CCL2"],
    "monocyte_nonclassical":  ["FCGR3A","LST1","LILRB2","CX3CR1"],
    "NK_cell":                ["NCAM1","NKG7","GNLY","KLRD1","GZMK"],
    "T_lymphocyte":           ["CD3D","CD3E","CD4","CD8A","TRAC"],
    "B_lymphocyte":           ["MS4A1","CD19","CD79A","IGHM"],
    "plasma_cell":            ["MZB1","XBP1","IGHG1","JCHAIN"],
}

LUNG_MARKERS: dict[str, list[str]] = {
    "myofibroblast":       ["ACTA2","POSTN","CTHRC1","COMP","TNC"],
    "fibroblast_CXCL12":   ["CXCL12","DCN","LUM","PDGFRA"],
    "fibroblast_other":    ["COL1A1","COL3A1","MFAP4"],
    "alveolar_typeII":     ["SFTPC","SFTPA1","SFTPB","ABCA3"],
    "alveolar_typeI":      ["AGER","HOPX","CAV1","RTKN2"],
    "endothelial":         ["PECAM1","CDH5","VWF","CLDN5"],
    "macrophage_alv":      ["MARCO","FABP4","PPARG","TREM2"],
    "macrophage_SPP1":     ["SPP1","CD68","MRC1","FCN1"],
    "T_lymphocyte":        ["CD3D","CD3E","TRAC"],
    "B_lymphocyte":        ["MS4A1","CD19","CD79A"],
}

TISSUE_MARKERS = {
    "skin":  SKIN_MARKERS,
    "pbmc":  PBMC_MARKERS,
    "lung":  LUNG_MARKERS,
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _annotate_cluster(means: "pd.Series", markers: dict) -> str:
    best, score = "unknown", -1.0
    for label, genes in markers.items():
        present = [g for g in genes if g in means.index]
        if not present:
            continue
        s = float(means[present].mean())
        if s > score:
            score, best = s, label
    return best


def load_species_modules(tsv: Path) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    with tsv.open() as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            hgnc = row.get("hgnc_symbol", "")
            if not hgnc:
                continue
            out.setdefault(hgnc, (row["species_id"], (row.get("module") or "?").split(",", 1)[0]))
    return out


def _pseudobulk_deg(raw_df: "pd.DataFrame", meta_cols: list[str],
                    hgnc_modules: dict) -> dict[tuple[str, str], float]:
    """Return {(cell_type, gene): log2FC} for SSC vs HC pseudobulk."""
    from scipy.stats import ranksums
    deg: dict[tuple[str, str], float] = {}
    gene_cols = [c for c in raw_df.columns if c not in meta_cols]

    for ct, grp in raw_df.groupby("cell_type"):
        ssc_donors = grp[grp["condition"] == "SSC"]["donor_id"].unique()
        hc_donors  = grp[grp["condition"] == "HC"]["donor_id"].unique()
        if len(ssc_donors) < 2 or len(hc_donors) < 2:
            continue
        pb = grp.groupby("donor_id")[gene_cols].sum()
        lib = pb.sum(axis=1)
        pb_norm = np.log1p(pb.div(lib, axis=0) * 1e4)
        ssc_idx = [d for d in ssc_donors if d in pb_norm.index]
        hc_idx  = [d for d in hc_donors  if d in pb_norm.index]
        if not ssc_idx or not hc_idx:
            continue
        for gene in gene_cols:
            ssc_v = pb_norm.loc[ssc_idx, gene].values
            hc_v  = pb_norm.loc[hc_idx,  gene].values
            lfc = float(np.mean(ssc_v) - np.mean(hc_v))
            if abs(lfc) < 0.2:
                continue
            if len(ssc_v) >= 2 and len(hc_v) >= 2:
                _, pv = ranksums(ssc_v, hc_v)
                if pv > 0.05:
                    continue
            deg[(str(ct), gene)] = lfc
    return deg


def _donor_scores(deg: dict, hgnc_modules: dict,
                  raw_df: "pd.DataFrame") -> dict[str, dict[str, float]]:
    """Per-donor module activation scores."""
    modules = ["M1", "M2", "M3", "M4"]
    gene_lfc: dict[str, dict[str, list[float]]] = {m: defaultdict(list) for m in modules}
    for (ct, gene), lfc in deg.items():
        if gene in hgnc_modules:
            _, mod = hgnc_modules[gene]
            if mod in modules:
                gene_lfc[mod][gene].append(lfc)

    scores: dict[str, dict[str, float]] = {}
    for donor, d_cells in raw_df.groupby("donor_id"):
        s: dict[str, float] = {}
        for mod in modules:
            genes = list(gene_lfc[mod].keys())
            present = [g for g in genes if g in d_cells.columns]
            if not present:
                s[mod] = 0.0
                continue
            expr = np.log1p(d_cells[present].values)
            mean_expr = expr.mean(axis=0)
            lfcs = np.array([np.mean(gene_lfc[mod][g]) for g in present])
            cond = d_cells["condition"].iloc[0]
            factor = 1.0 if cond == "SSC" else 0.3
            s[mod] = float(np.mean(mean_expr * np.sign(lfcs))) * factor
        scores[str(donor)] = s
    return scores


# ── Dataset-specific loaders ───────────────────────────────────────────────────

def process_tabib(raw_dir: Path, hgnc_modules: dict) -> tuple[dict, dict, str]:
    """Process Tabib 2021 GSE138669 (10x .h5 per sample)."""
    import scanpy as sc
    import pandas as pd
    from scipy.sparse import issparse

    h5_files = sorted(raw_dir.glob("*.h5"))
    if not h5_files:
        raise FileNotFoundError(f"No .h5 files in {raw_dir}")

    print(f"  [tabib2021] loading {len(h5_files)} .h5 files …")
    adatas = []
    _re = re.compile(r"_(SC\d+)raw")
    for h5 in h5_files:
        m = _re.search(h5.name)
        donor = m.group(1) if m else h5.stem
        cond = TABIB_DONOR_COND.get(donor, "unknown")
        adata = sc.read_10x_h5(str(h5))
        adata.var_names_make_unique()
        adata.obs_names = [f"{donor}_{bc}" for bc in adata.obs_names]
        adata.obs["donor_id"] = donor
        adata.obs["condition"] = cond
        adatas.append(adata)

    adata = sc.concat(adatas, merge="same")
    adata = _qc_norm_cluster(adata, SKIN_MARKERS, res=0.35)
    raw_df = _adata_to_raw_df(adata)
    deg = _pseudobulk_deg(raw_df, ["donor_id","condition","cell_type"], hgnc_modules)
    donor_scores = _donor_scores(deg, hgnc_modules, raw_df)
    print(f"  [tabib2021] DEG: {len(deg):,} pairs; {len(donor_scores)} donors")
    return deg, donor_scores, "REAL"


def process_gse210395(raw_dir: Path, hgnc_modules: dict) -> tuple[dict, dict, str]:
    """Process GSE210395 — pDC-enriched PBMC, long-format TSV."""
    import scanpy as sc
    import pandas as pd
    from scipy.sparse import csr_matrix

    tsv_gz = raw_dir / "GSE210395_scRNA_countMatrix.tsv.gz"
    if not tsv_gz.exists():
        raise FileNotFoundError(tsv_gz)

    print(f"  [gse210395] reading long-format TSV …")
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip",
                     names=["gene","cell","count"], header=0)

    # Extract donor from barcode suffix e.g. AAACCC…-SI-GA-B5 → B5
    _b_re = re.compile(r"-SI-GA-(B\d+)$")
    def _donor(bc: str) -> str:
        m = _b_re.search(bc)
        return m.group(1) if m else "unknown"

    df["donor_key"] = df["cell"].apply(_donor)
    # Keep only known donor barcodes
    df = df[df["donor_key"].isin(GSE210395_INDEX)]

    # Build sparse count matrix
    print(f"  [gse210395] pivoting sparse matrix …")
    genes   = df["gene"].astype("category")
    cells   = df["cell"].astype("category")
    matrix  = csr_matrix(
        (df["count"].values, (genes.cat.codes.values, cells.cat.codes.values)),
        shape=(len(genes.cat.categories), len(cells.cat.categories))
    )
    import anndata as ad
    adata = ad.AnnData(
        X=matrix.T,
        obs=pd.DataFrame(index=cells.cat.categories),
        var=pd.DataFrame(index=genes.cat.categories),
    )
    adata.var_names_make_unique()

    # Attach donor + condition
    adata.obs["barcode_donor_key"] = [_donor(bc) for bc in adata.obs_names]
    adata.obs["donor_id"]  = [GSE210395_INDEX.get(k, ("unknown","?"))[0]
                               for k in adata.obs["barcode_donor_key"]]
    adata.obs["condition"] = [GSE210395_INDEX.get(k, ("unknown","?"))[1]
                               for k in adata.obs["barcode_donor_key"]]
    adata = adata[adata.obs["condition"] != "?"].copy()

    adata = _qc_norm_cluster(adata, PBMC_MARKERS, res=0.5)
    raw_df = _adata_to_raw_df(adata)
    deg = _pseudobulk_deg(raw_df, ["donor_id","condition","cell_type"], hgnc_modules)
    donor_scores = _donor_scores(deg, hgnc_modules, raw_df)
    print(f"  [gse210395] DEG: {len(deg):,} pairs; {len(donor_scores)} donors")
    return deg, donor_scores, "REAL"


def process_gse128169(raw_dir: Path, hgnc_modules: dict) -> tuple[dict, dict, str]:
    """Process GSE128169 — SSc-ILD lung, GEO flat-directory MEX format.

    GEO deposits files as: GSM<id>_<SAMPLE>_matrix.mtx.gz / _barcodes.tsv.gz / _genes.tsv.gz
    All files are in a single flat directory — scanpy's read_10x_mtx cannot handle
    this layout, so we load each triplet manually via scipy.io.mmread + pandas.
    """
    import gzip
    import scanpy as sc
    import pandas as pd
    import scipy.io
    from scipy.sparse import csr_matrix

    # Find all matrix files in the flat GEO directory
    mtx_files = sorted(raw_dir.glob("*_matrix.mtx.gz"))
    if not mtx_files:
        # Fallback: per-sample subdirectory layout (post-extraction)
        mtx_files = sorted(raw_dir.rglob("matrix.mtx.gz"))

    if not mtx_files:
        raise FileNotFoundError(f"No *_matrix.mtx.gz files found under {raw_dir}")

    print(f"  [gse128169] loading {len(mtx_files)} MEX sample(s) …")
    adatas = []
    _gsm_re = re.compile(r"^GSM\d+_")

    for mtx_gz in mtx_files:
        # Derive sample name: "GSM3666096_SC45NOR_matrix.mtx.gz" → "SC45NOR"
        stem = _gsm_re.sub("", mtx_gz.name)          # "SC45NOR_matrix.mtx.gz"
        sample = stem.replace("_matrix.mtx.gz", "")   # "SC45NOR"
        cond = _match_lung_sample(sample)
        if cond == "unknown":
            continue

        barcode_gz = mtx_gz.parent / mtx_gz.name.replace("_matrix.mtx.gz", "_barcodes.tsv.gz")
        genes_gz   = mtx_gz.parent / mtx_gz.name.replace("_matrix.mtx.gz", "_genes.tsv.gz")

        if not barcode_gz.exists() or not genes_gz.exists():
            print(f"    WARN: missing barcodes/genes for {sample}, skipping")
            continue

        with gzip.open(str(mtx_gz)) as f:
            matrix = scipy.io.mmread(f).T.tocsr()   # cells × genes (CSR)

        barcodes = pd.read_csv(barcode_gz, compression="gzip", header=None)[0].tolist()
        genes_df = pd.read_csv(genes_gz, sep="\t", compression="gzip", header=None)
        # 10x v2: col0 = Ensembl, col1 = symbol; v3: similar; handle both
        gene_names = genes_df.iloc[:, 1].tolist() if genes_df.shape[1] > 1 else genes_df.iloc[:, 0].tolist()

        adata = sc.AnnData(
            X=matrix,
            obs=pd.DataFrame(index=barcodes),
            var=pd.DataFrame(index=gene_names),
        )
        adata.var_names_make_unique()
        adata.obs_names = [f"{sample}_{bc}" for bc in adata.obs_names]
        adata.obs["donor_id"]  = sample
        adata.obs["condition"] = cond
        adatas.append(adata)
        print(f"    loaded {sample} ({cond}): {adata.n_obs:,} cells, {adata.n_vars:,} genes")

    if not adatas:
        raise ValueError("No samples loaded for GSE128169")

    adata = sc.concat(adatas, merge="same")
    adata = _qc_norm_cluster(adata, LUNG_MARKERS, res=0.4)
    raw_df = _adata_to_raw_df(adata)
    deg = _pseudobulk_deg(raw_df, ["donor_id","condition","cell_type"], hgnc_modules)
    donor_scores = _donor_scores(deg, hgnc_modules, raw_df)
    print(f"  [gse128169] DEG: {len(deg):,} pairs; {len(donor_scores)} donors")
    return deg, donor_scores, "REAL"


def _match_lung_sample(name: str) -> str:
    """Match a sample dir/file name to HC or SSC for GSE128169."""
    name_up = name.upper()
    for key, cond in GSE128169_DONOR_COND.items():
        if key.upper() in name_up:
            return cond
    if "NOR" in name_up or "CONTROL" in name_up or "HC" in name_up:
        return "HC"
    if "SSC" in name_up or "ILD" in name_up:
        return "SSC"
    return "unknown"


def _qc_norm_cluster(adata, markers: dict, res: float = 0.4):
    """Shared QC → normalise → cluster → annotate pipeline."""
    import scanpy as sc
    import pandas as pd
    from scipy.sparse import issparse

    before = adata.n_obs
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, inplace=True)
    adata = adata[adata.obs.n_genes_by_counts >= 200].copy()
    adata = adata[adata.obs.n_genes_by_counts <= 6000].copy()
    adata = adata[adata.obs.pct_counts_mt < 25].copy()
    sc.pp.filter_genes(adata, min_cells=10)
    print(f"    QC: {adata.n_obs:,} cells ({before - adata.n_obs:,} removed), {adata.n_vars:,} genes")

    adata.raw = adata.copy()
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
    sc.pp.pca(adata, n_comps=30)
    sc.pp.neighbors(adata, n_neighbors=20, n_pcs=20)
    sc.tl.leiden(adata, resolution=res, key_added="leiden", flavor="igraph",
                 n_iterations=2, directed=False)
    n_cl = adata.obs["leiden"].nunique()
    print(f"    Leiden: {n_cl} clusters (res={res})")

    # Annotate via mean expression of markers
    X = adata.X.toarray() if issparse(adata.X) else adata.X
    cluster_means = (
        pd.DataFrame(X, columns=adata.var_names, index=adata.obs_names)
        .join(adata.obs["leiden"])
        .groupby("leiden", observed=True)
        .mean()
    )
    adata.obs["cell_type"] = adata.obs["leiden"].map(
        {cl: _annotate_cluster(cluster_means.loc[cl], markers)
         for cl in cluster_means.index}
    )
    ct_counts = adata.obs["cell_type"].value_counts()
    for ct, n in ct_counts.items():
        print(f"      {ct}: {n:,}")
    return adata


def _adata_to_raw_df(adata) -> "pd.DataFrame":
    """Return raw count DataFrame with donor_id / condition / cell_type columns."""
    import pandas as pd
    from scipy.sparse import issparse
    X = adata.raw.X.toarray() if issparse(adata.raw.X) else adata.raw.X
    df = pd.DataFrame(X, columns=adata.raw.var_names, index=adata.obs_names)
    df["donor_id"]  = adata.obs["donor_id"].values
    df["condition"] = adata.obs["condition"].values
    df["cell_type"] = adata.obs["cell_type"].values
    return df


# ── Output writers ─────────────────────────────────────────────────────────────

def write_cluster_deg(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        fh.write("dataset\ttissue\tcluster\thgnc\tspecies_id\tmodule\tlog2fc\n")
        for r in rows:
            fh.write("\t".join([r["dataset"], r["tissue"], r["cluster"],
                                 r["hgnc"], r["species_id"], r["module"],
                                 f"{r['log2fc']:.3f}"]) + "\n")


def write_patient_scores(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        fh.write("donor_id\tgroup\tdataset\ttissue\tM1\tM2\tM3\tM4\n")
        for r in rows:
            fh.write("\t".join([r["donor_id"], r["group"], r["dataset"], r["tissue"],
                                 f"{r['M1']:.3f}", f"{r['M2']:.3f}",
                                 f"{r['M3']:.3f}", f"{r['M4']:.3f}"]) + "\n")


def write_minerva_overlays(all_deg_rows: list[dict], out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    by_cluster: dict[str, dict[str, float]] = defaultdict(dict)
    for r in all_deg_rows:
        if r["species_id"]:
            key = f"{r['dataset']}_{r['cluster']}"
            by_cluster[key][r["species_id"]] = r["log2fc"]
    n = 0
    for key, sid_lfc in by_cluster.items():
        path = out_dir / f"{key}.tsv"
        with path.open("w") as fh:
            fh.write("species_id\tlog2fc\tcolor\n")
            for sid, lfc in sorted(sid_lfc.items()):
                color = "#d7191c" if lfc > 0 else "#2c7fb8"
                fh.write(f"{sid}\t{lfc:.3f}\t{color}\n")
        n += 1
    return n


def render_f2_multi(score_rows: list[dict], out_svg: Path, out_png: Path) -> None:
    """Three-panel heatmap: skin / PBMC / lung per-donor module scores."""
    tissues = ["skin", "pbmc", "lung"]
    tissue_labels = {"skin": "Skin\n(GSE138669)", "pbmc": "PBMC\n(GSE210395)", "lung": "Lung ILD\n(GSE128169)"}
    modules = ["M1", "M2", "M3", "M4"]
    mod_labels = ["M1 IFN-I", "M2 TGF-β", "M3 EndoMT", "M4 IL-6/Th2"]

    # organise by tissue
    by_tissue: dict[str, list[dict]] = {t: [] for t in tissues}
    for r in score_rows:
        if r["tissue"] in by_tissue:
            by_tissue[r["tissue"]].append(r)

    # count non-empty panels
    active = [t for t in tissues if by_tissue[t]]
    n_panels = len(active)
    if n_panels == 0:
        return

    fig, axes = plt.subplots(1, n_panels, figsize=(4.5 * n_panels, 7), dpi=100)
    if n_panels == 1:
        axes = [axes]

    for ax, tissue in zip(axes, active):
        rows = sorted(by_tissue[tissue], key=lambda r: (r["group"] != "SSc", r["donor_id"]))
        donor_ids = [r["donor_id"] for r in rows]
        matrix = np.array([[r[m] for m in modules] for r in rows])
        im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-1.5, vmax=1.5)
        ax.set_xticks(range(4))
        ax.set_xticklabels(mod_labels, rotation=30, ha="right", fontsize=8)
        ax.set_yticks(range(len(donor_ids)))
        ax.set_yticklabels(donor_ids, fontsize=7)
        n_ssc = sum(1 for r in rows if r["group"] == "SSc")
        if 0 < n_ssc < len(rows):
            ax.axhline(n_ssc - 0.5, color="white", linewidth=1.5)
        ax.set_title(f"{tissue_labels.get(tissue, tissue)}\n"
                     f"({sum(1 for r in rows if r['group']=='SSc')} SSc / "
                     f"{sum(1 for r in rows if r['group']=='HC')} HC)",
                     fontsize=9)
        plt.colorbar(im, ax=ax, shrink=0.7, label="module score")

    fig.suptitle("SSc-MIM per-donor module activation scores — multi-dataset overlay", fontsize=11)
    plt.tight_layout()
    fig.savefig(out_svg, format="svg")
    fig.savefig(out_png, format="png", dpi=300)
    plt.close(fig)
    print(f"  [ok] {out_svg}")
    print(f"  [ok] {out_png}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tabib-dir",    type=Path, default=Path("data/raw/tabib2021"))
    ap.add_argument("--gse210395-dir",type=Path, default=Path("data/raw/gse210395"))
    ap.add_argument("--gse128169-dir",type=Path, default=Path("data/raw/gse128169"))
    ap.add_argument("--species-tsv",  type=Path, default=Path("curation/annotations/species_annotations.tsv"))
    ap.add_argument("--out-dir",      type=Path, default=Path("analysis/overlay"))
    ap.add_argument("--minerva-dir",  type=Path, default=Path("minerva/overlays"))
    ap.add_argument("--fig-dir",      type=Path, default=Path("figures"))
    ap.add_argument("--skip-tabib",   action="store_true")
    args = ap.parse_args(argv[1:])

    hgnc_modules = load_species_modules(args.species_tsv)
    print(f"MIM species index: {len(hgnc_modules)} HGNC symbols")

    all_deg_rows:   list[dict] = []
    all_score_rows: list[dict] = []
    modes:          dict[str, str] = {}

    # ── Tabib 2021 ──────────────────────────────────────────────────────────
    if not args.skip_tabib and list(args.tabib_dir.glob("*.h5")):
        try:
            print("\n[tabib2021] Processing skin biopsies …")
            deg, scores, mode = process_tabib(args.tabib_dir, hgnc_modules)
            modes["tabib2021"] = mode
            for (ct, gene), lfc in deg.items():
                sid, mod = hgnc_modules.get(gene, ("", ""))
                all_deg_rows.append({"dataset":"tabib2021","tissue":"skin","cluster":ct,
                                      "hgnc":gene,"species_id":sid,"module":mod,"log2fc":lfc})
            for donor, ms in scores.items():
                cond = TABIB_DONOR_COND.get(donor, "?")
                all_score_rows.append({"donor_id":donor,"group":"SSc" if cond=="SSC" else "HC",
                                        "dataset":"tabib2021","tissue":"skin",**ms})
        except Exception as exc:
            print(f"  WARN tabib2021 failed: {exc}")
            modes["tabib2021"] = "FAILED"
    else:
        modes["tabib2021"] = "SKIPPED"

    # ── GSE210395 PBMC ───────────────────────────────────────────────────────
    tsv_gz = args.gse210395_dir / "GSE210395_scRNA_countMatrix.tsv.gz"
    if tsv_gz.exists():
        try:
            print("\n[gse210395] Processing PBMC pDC+monocyte …")
            deg, scores, mode = process_gse210395(args.gse210395_dir, hgnc_modules)
            modes["gse210395"] = mode
            for (ct, gene), lfc in deg.items():
                sid, mod = hgnc_modules.get(gene, ("", ""))
                all_deg_rows.append({"dataset":"gse210395","tissue":"pbmc","cluster":ct,
                                      "hgnc":gene,"species_id":sid,"module":mod,"log2fc":lfc})
            for donor, ms in scores.items():
                idx_val = next((v for k, v in GSE210395_INDEX.items() if v[0]==donor), ("?","?"))
                group = "SSc" if idx_val[1]=="SSC" else "HC"
                all_score_rows.append({"donor_id":donor,"group":group,
                                        "dataset":"gse210395","tissue":"pbmc",**ms})
        except Exception as exc:
            print(f"  WARN gse210395 failed: {exc}")
            modes["gse210395"] = "FAILED"
    else:
        print(f"\n[gse210395] data absent ({tsv_gz}) — skipped")
        modes["gse210395"] = "ABSENT"

    # ── GSE128169 Lung ───────────────────────────────────────────────────────
    lung_has_data = (list(args.gse128169_dir.glob("**/*.h5")) or
                     list(args.gse128169_dir.rglob("matrix.mtx*")) or
                     list(args.gse128169_dir.glob("*_matrix.mtx.gz")))
    if lung_has_data:
        try:
            print("\n[gse128169] Processing SSc-ILD lung …")
            deg, scores, mode = process_gse128169(args.gse128169_dir, hgnc_modules)
            modes["gse128169"] = mode
            for (ct, gene), lfc in deg.items():
                sid, mod = hgnc_modules.get(gene, ("", ""))
                all_deg_rows.append({"dataset":"gse128169","tissue":"lung","cluster":ct,
                                      "hgnc":gene,"species_id":sid,"module":mod,"log2fc":lfc})
            for donor, ms in scores.items():
                cond = GSE128169_DONOR_COND.get(donor, "?")
                all_score_rows.append({"donor_id":donor,"group":"SSc" if cond=="SSC" else "HC",
                                        "dataset":"gse128169","tissue":"lung",**ms})
        except Exception as exc:
            print(f"  WARN gse128169 failed: {exc}")
            modes["gse128169"] = "FAILED"
    else:
        print(f"\n[gse128169] data absent — skipped")
        modes["gse128169"] = "ABSENT"

    # ── Write outputs ────────────────────────────────────────────────────────
    print("\nWriting outputs …")
    out_deg = args.out_dir / "cluster_deg_multi.tsv"
    write_cluster_deg(all_deg_rows, out_deg)
    print(f"  [ok] {out_deg}  ({len(all_deg_rows):,} rows)")

    out_scores = args.out_dir / "patient_module_scores_multi.tsv"
    write_patient_scores(all_score_rows, out_scores)
    print(f"  [ok] {out_scores}  ({len(all_score_rows)} donors)")

    n_ov = write_minerva_overlays(all_deg_rows, args.minerva_dir)
    print(f"  [ok] {args.minerva_dir}/ ({n_ov} cluster overlays)")

    render_f2_multi(
        all_score_rows,
        args.fig_dir / "F2_multi_overlay.svg",
        args.fig_dir / "F2_multi_overlay.png",
    )

    # Coverage stats
    mim_genes = set(hgnc_modules.keys())
    mapped_genes = set(r["hgnc"] for r in all_deg_rows if r["module"] not in ("","?","FAILED"))
    mim_hit = mim_genes & set(r["hgnc"] for r in all_deg_rows)
    print(f"\nCoverage: {len(mim_hit)}/{len(mim_genes)} MIM species with DEG hits "
          f"({100*len(mim_hit)/len(mim_genes):.1f}%)")
    print(f"Module-mapped: {len(mapped_genes)} unique HGNC genes")

    report = {
        "modes": modes,
        "n_deg_entries": len(all_deg_rows),
        "n_donors": len(all_score_rows),
        "n_minerva_overlays": n_ov,
        "mim_coverage_pct": round(100 * len(mim_hit) / max(1, len(mim_genes)), 1),
        "mim_hit_genes": sorted(mim_hit),
        "outputs": {
            "cluster_deg_multi": str(out_deg),
            "patient_scores_multi": str(out_scores),
            "f2_multi": str(args.fig_dir / "F2_multi_overlay.svg"),
        }
    }
    rep_path = args.out_dir / "build_overlay_multi.report.json"
    rep_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  [ok] {rep_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
