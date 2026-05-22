#!/usr/bin/env python3
"""Pseudobulk DEG with proper statistical modelling + BH-FDR.

Addresses npj-SBA reviewer R2-M1: the v1.0 pipeline used a raw-Wilcoxon
per-cell-type test with no multiple-testing correction across the 4 338
(cluster, gene) comparisons. With n=4–13 donors per dataset that is
underpowered and uncontrolled.

This module re-runs DEG on pre-aggregated pseudobulk count matrices
using one of three backends, in preference order:

1. **pydeseq2** (preferred) — NB GLM on raw counts with design
   ``~ condition``. Standard for pseudobulk single-cell DEG.
   Reference: Muzellec et al. *Bioinformatics* 2023.

2. **statsmodels NB** (fallback) — manual NB GLM via
   ``statsmodels.discrete_model.NegativeBinomial`` per gene.

3. **scipy Welch's t-test** (last resort) — on log1p(CPM) values;
   no NB modelling but at least size-corrected and parametric.

In all cases:

- BH-FDR is applied **per dataset** (primary, less conservative than
  per-cluster) and **per cluster** (diagnostic).
- Output schema adds ``pvalue``, ``padj_dataset``, ``padj_cluster``,
  ``n_donors_ssc``, ``n_donors_hc``, ``mean_count_ssc``,
  ``mean_count_hc``, ``backend`` to the v1.0 columns.

Usage as library::

    from deg_mixed_effects import pseudobulk_deg
    out = pseudobulk_deg(pb_counts_df,
                         group_col="condition", donor_col="donor_id",
                         cell_type_col="cell_type",
                         gene_cols=[...], backend="auto")

Usage as CLI::

    python3 scripts/deg_mixed_effects.py \
        --in pseudobulk.tsv \
        --out analysis/overlay/cluster_deg_v1.1.tsv \
        --backend auto
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable

import numpy as np

log = logging.getLogger("deg_mixed")

# ── Schema ─────────────────────────────────────────────────────────────────────

DEG_OUTPUT_COLS = [
    "dataset", "tissue", "cluster", "hgnc",
    "log2fc", "pvalue", "padj_dataset", "padj_cluster",
    "n_donors_ssc", "n_donors_hc",
    "mean_count_ssc", "mean_count_hc",
    "backend",
]


@dataclass
class DEGRow:
    dataset: str
    tissue: str
    cluster: str
    hgnc: str
    log2fc: float
    pvalue: float
    padj_dataset: float = float("nan")
    padj_cluster: float = float("nan")
    n_donors_ssc: int = 0
    n_donors_hc: int = 0
    mean_count_ssc: float = 0.0
    mean_count_hc: float = 0.0
    backend: str = ""

    def as_tsv(self) -> str:
        return "\t".join([
            self.dataset, self.tissue, self.cluster, self.hgnc,
            f"{self.log2fc:.4f}",
            f"{self.pvalue:.4g}",
            f"{self.padj_dataset:.4g}" if not np.isnan(self.padj_dataset) else "",
            f"{self.padj_cluster:.4g}" if not np.isnan(self.padj_cluster) else "",
            str(self.n_donors_ssc), str(self.n_donors_hc),
            f"{self.mean_count_ssc:.3f}", f"{self.mean_count_hc:.3f}",
            self.backend,
        ])


# ── Backend detection ──────────────────────────────────────────────────────────

def detect_backend(requested: str = "auto") -> str:
    """Return the first available backend, in preference order.

    `auto` resolves to pydeseq2 → statsmodels → scipy_welch.
    A literal backend name is returned verbatim if its dependency is importable.
    """
    candidates = (
        ["pydeseq2", "statsmodels", "scipy_welch"]
        if requested == "auto" else [requested]
    )
    for name in candidates:
        try:
            if name == "pydeseq2":
                import pydeseq2  # noqa: F401
            elif name == "statsmodels":
                import statsmodels.api  # noqa: F401
            elif name == "scipy_welch":
                import scipy  # noqa: F401
            else:
                raise ValueError(f"unknown backend: {name}")
            return name
        except ImportError:
            continue
    raise RuntimeError("no DEG backend available (need pydeseq2, statsmodels, or scipy)")


# ── Backend implementations ────────────────────────────────────────────────────

def _deg_pydeseq2(counts: "np.ndarray", labels: list[str], genes: list[str],
                  ssc_label: str = "SSC") -> list[tuple[str, float, float, float, float]]:
    """Run pydeseq2 on a (n_donors × n_genes) integer count matrix.

    Returns list of (gene, log2fc, pvalue, mean_count_ssc, mean_count_hc).
    """
    import pandas as pd
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats

    metadata = pd.DataFrame({"condition": labels}, index=[f"d{i}" for i in range(len(labels))])
    counts_df = pd.DataFrame(counts.astype(int),
                             index=metadata.index, columns=genes)

    dds = DeseqDataSet(counts=counts_df, metadata=metadata,
                       design_factors="condition", quiet=True)
    dds.deseq2()
    stat = DeseqStats(dds, contrast=("condition", ssc_label, "HC"), quiet=True)
    stat.summary()
    res = stat.results_df

    out: list[tuple[str, float, float, float, float]] = []
    ssc_mask = np.array([l == ssc_label for l in labels])
    hc_mask = ~ssc_mask
    for g in genes:
        if g not in res.index:
            continue
        lfc = float(res.loc[g, "log2FoldChange"])
        pv  = float(res.loc[g, "pvalue"])
        if not np.isfinite(pv):
            continue
        m_ssc = float(np.mean(counts[ssc_mask, genes.index(g)]))
        m_hc  = float(np.mean(counts[hc_mask,  genes.index(g)]))
        out.append((g, lfc, pv, m_ssc, m_hc))
    return out


def _deg_statsmodels(counts: "np.ndarray", labels: list[str], genes: list[str],
                     ssc_label: str = "SSC") -> list[tuple[str, float, float, float, float]]:
    """NB GLM per gene via statsmodels.

    Fits ``count ~ condition`` with NB family; reports Wald p on the
    condition coefficient. Slower than pydeseq2 but no extra dep.
    """
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import NegativeBinomial

    out = []
    x = np.array([1 if l == ssc_label else 0 for l in labels])
    X = sm.add_constant(x.astype(float))
    ssc_mask = x == 1
    hc_mask = ~ssc_mask
    libsize = counts.sum(axis=1).astype(float)
    libsize[libsize == 0] = 1.0
    offset = np.log(libsize)

    for j, g in enumerate(genes):
        y = counts[:, j].astype(float)
        if y.sum() < 10:  # too sparse
            continue
        try:
            # NB with data-estimated dispersion + library-size offset
            model = NegativeBinomial(y, X, offset=offset)
            fit = model.fit(disp=0, maxiter=100, method="bfgs")
            coef = float(fit.params[1])
            pv = float(fit.pvalues[1])
        except Exception:
            # Fall back to Poisson GLM with robust SE (Quasi-Poisson-like)
            try:
                model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
                fit = model.fit(cov_type="HC0", disp=0)
                coef = float(fit.params[1])
                pv = float(fit.pvalues[1])
            except Exception:
                continue
        if not np.isfinite(pv):
            continue
        lfc = float(coef / np.log(2.0))
        m_ssc = float(y[ssc_mask].mean())
        m_hc  = float(y[hc_mask].mean())
        out.append((g, lfc, pv, m_ssc, m_hc))
    return out


def _deg_scipy_welch(counts: "np.ndarray", labels: list[str], genes: list[str],
                     ssc_label: str = "SSC") -> list[tuple[str, float, float, float, float]]:
    """Welch's t-test on log1p(CPM × 1e4); a robust last-resort backend.

    Equivalent to the v1.0 logic but reports the unfiltered p-value
    (so it can be FDR-corrected downstream) and reports it for every gene
    that has non-zero variance in at least one group.
    """
    from scipy.stats import ttest_ind

    libsize = counts.sum(axis=1, keepdims=True)
    libsize[libsize == 0] = 1
    cpm_log = np.log1p(counts / libsize * 1e4)
    x = np.array([1 if l == ssc_label else 0 for l in labels])
    ssc_mask = x == 1
    hc_mask = ~ssc_mask

    out = []
    for j, g in enumerate(genes):
        ssc_v = cpm_log[ssc_mask, j]
        hc_v  = cpm_log[hc_mask,  j]
        if ssc_v.size < 2 or hc_v.size < 2:
            continue
        if ssc_v.var() == 0 and hc_v.var() == 0:
            continue
        lfc = float(np.mean(ssc_v) - np.mean(hc_v))
        try:
            _, pv = ttest_ind(ssc_v, hc_v, equal_var=False)
        except Exception:
            continue
        if not np.isfinite(pv):
            continue
        m_ssc = float(counts[ssc_mask, j].mean())
        m_hc  = float(counts[hc_mask,  j].mean())
        out.append((g, lfc, float(pv), m_ssc, m_hc))
    return out


# ── Core API ───────────────────────────────────────────────────────────────────

def pseudobulk_deg(pb_df, *, gene_cols: list[str],
                   group_col: str = "condition",
                   donor_col: str = "donor_id",
                   cell_type_col: str = "cell_type",
                   dataset: str = "?", tissue: str = "?",
                   ssc_label: str = "SSC", hc_label: str = "HC",
                   min_donors_per_group: int = 2,
                   backend: str = "auto") -> list[DEGRow]:
    """Run pseudobulk DEG on a long-format DataFrame.

    Parameters
    ----------
    pb_df
        One row per (donor, cell_type) with raw counts in ``gene_cols``
        and metadata columns ``group_col`` (SSC/HC), ``donor_col``,
        ``cell_type_col``.
    gene_cols
        Subset of columns to test (usually MIM-mapped HGNC symbols, but
        the function does not enforce it).
    backend
        ``auto`` (resolved), or one of pydeseq2, statsmodels, scipy_welch.

    Returns
    -------
    List of ``DEGRow`` with raw p-values populated. FDR adjustment is
    applied separately by :func:`apply_fdr`.
    """
    backend = detect_backend(backend)
    log.info("DEG backend: %s", backend)

    impl = {
        "pydeseq2": _deg_pydeseq2,
        "statsmodels": _deg_statsmodels,
        "scipy_welch": _deg_scipy_welch,
    }[backend]

    rows: list[DEGRow] = []
    for ct, grp in pb_df.groupby(cell_type_col, observed=True):
        labels = grp[group_col].tolist()
        n_ssc = sum(1 for l in labels if l == ssc_label)
        n_hc  = sum(1 for l in labels if l == hc_label)
        if n_ssc < min_donors_per_group or n_hc < min_donors_per_group:
            log.info("  skip %s (n_ssc=%d, n_hc=%d)", ct, n_ssc, n_hc)
            continue
        counts = grp[gene_cols].values
        try:
            res = impl(counts, labels, list(gene_cols), ssc_label=ssc_label)
        except Exception as e:
            log.warning("  %s failed (%s); falling back to scipy_welch", backend, e)
            res = _deg_scipy_welch(counts, labels, list(gene_cols), ssc_label=ssc_label)
        for gene, lfc, pv, m_ssc, m_hc in res:
            rows.append(DEGRow(
                dataset=dataset, tissue=tissue, cluster=str(ct), hgnc=gene,
                log2fc=lfc, pvalue=pv,
                n_donors_ssc=n_ssc, n_donors_hc=n_hc,
                mean_count_ssc=m_ssc, mean_count_hc=m_hc,
                backend=backend,
            ))
    return rows


def apply_fdr(rows: list[DEGRow]) -> None:
    """In-place BH-FDR adjustment.

    Computes:
    - ``padj_dataset`` — BH within each (dataset) group (primary).
    - ``padj_cluster`` — BH within each (dataset, cluster) group (diag).
    """
    from collections import defaultdict
    by_ds: dict[str, list[DEGRow]] = defaultdict(list)
    by_ds_ct: dict[tuple[str, str], list[DEGRow]] = defaultdict(list)
    for r in rows:
        by_ds[r.dataset].append(r)
        by_ds_ct[(r.dataset, r.cluster)].append(r)

    def _bh(rs: list[DEGRow], attr: str) -> None:
        if not rs:
            return
        pvals = np.array([r.pvalue for r in rs])
        m = len(pvals)
        order = np.argsort(pvals)
        ranked = pvals[order]
        bh = ranked * m / (np.arange(m) + 1)
        # enforce monotone-from-the-right
        bh = np.minimum.accumulate(bh[::-1])[::-1]
        bh = np.clip(bh, 0, 1)
        padj = np.empty_like(bh)
        padj[order] = bh
        for r, q in zip(rs, padj):
            setattr(r, attr, float(q))

    for rs in by_ds.values():
        _bh(rs, "padj_dataset")
    for rs in by_ds_ct.values():
        _bh(rs, "padj_cluster")


# ── I/O ────────────────────────────────────────────────────────────────────────

def read_pseudobulk_tsv(path: Path) -> "tuple[object, list[str]]":
    """Read a wide pseudobulk TSV.

    Expects columns: donor_id, condition, cell_type, dataset, tissue,
    then gene columns. Returns (DataFrame, gene_cols).
    """
    import pandas as pd
    df = pd.read_csv(path, sep="\t")
    meta = {"donor_id", "condition", "cell_type", "dataset", "tissue", "lib_size"}
    gene_cols = [c for c in df.columns if c not in meta]
    return df, gene_cols


def write_deg_tsv(rows: list[DEGRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        fh.write("\t".join(DEG_OUTPUT_COLS) + "\n")
        for r in rows:
            fh.write(r.as_tsv() + "\n")


# ── Reporting ──────────────────────────────────────────────────────────────────

def coverage_summary(rows: list[DEGRow], q_threshold: float = 0.05,
                     species_modules: dict[str, str] | None = None) -> dict:
    """Per-dataset / per-module significant-DEG counts at FDR ≤ q.

    species_modules: HGNC → module label. If provided, breaks coverage
    down by module.
    """
    from collections import defaultdict
    sig = [r for r in rows if r.padj_dataset <= q_threshold]
    per_ds: dict[str, int] = defaultdict(int)
    per_ds_genes: dict[str, set[str]] = defaultdict(set)
    for r in sig:
        per_ds[r.dataset] += 1
        per_ds_genes[r.dataset].add(r.hgnc)
    summary = {
        "q_threshold": q_threshold,
        "n_tests_total": len(rows),
        "n_sig_total": len(sig),
        "per_dataset": {k: {"n_sig": v, "n_unique_genes": len(per_ds_genes[k])}
                        for k, v in per_ds.items()},
        "unique_significant_genes": sorted({r.hgnc for r in sig}),
    }
    if species_modules:
        per_mod: dict[str, set[str]] = defaultdict(set)
        for r in sig:
            mod = species_modules.get(r.hgnc, "?")
            per_mod[mod].add(r.hgnc)
        summary["per_module"] = {k: {"n_unique_genes": len(v), "genes": sorted(v)}
                                 for k, v in per_mod.items()}
    return summary


# ── CLI ────────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="in_tsv", required=True, type=Path,
                    help="Pseudobulk wide TSV (donor × gene)")
    ap.add_argument("--out", dest="out_tsv", required=True, type=Path,
                    help="Output DEG TSV")
    ap.add_argument("--summary", type=Path, default=None,
                    help="Optional JSON summary with FDR-cut coverage")
    ap.add_argument("--backend", default="auto",
                    choices=["auto", "pydeseq2", "statsmodels", "scipy_welch"])
    ap.add_argument("--q", type=float, default=0.05,
                    help="FDR threshold for coverage summary (default 0.05)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s %(message)s")

    df, gene_cols = read_pseudobulk_tsv(args.in_tsv)
    log.info("loaded %d rows × %d genes from %s", len(df), len(gene_cols), args.in_tsv)
    rows = pseudobulk_deg(
        df, gene_cols=gene_cols,
        dataset=str(df["dataset"].iloc[0]) if "dataset" in df else "?",
        tissue=str(df["tissue"].iloc[0]) if "tissue" in df else "?",
        backend=args.backend,
    )
    apply_fdr(rows)
    write_deg_tsv(rows, args.out_tsv)
    log.info("wrote %d DEG rows to %s", len(rows), args.out_tsv)

    if args.summary:
        summ = coverage_summary(rows, q_threshold=args.q)
        args.summary.write_text(json.dumps(summ, indent=2))
        log.info("summary at FDR≤%.3f: %d/%d sig (%d unique genes) → %s",
                 args.q, summ["n_sig_total"], summ["n_tests_total"],
                 len(summ["unique_significant_genes"]), args.summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
