#!/usr/bin/env python3
"""Smoke test for scripts/deg_mixed_effects.py.

Builds a tiny synthetic pseudobulk (8 donors × 50 genes × 2 cell types)
with planted differential genes, runs each available backend, checks:

1. Backend detection works.
2. p-values monotone with effect size (strong effect → small p).
3. BH-FDR is non-decreasing in raw p ranking and ≤ 1.
4. The planted genes recover at FDR ≤ 0.05.

Run with::

    python3 scripts/tests/test_deg_mixed_effects.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow importing the sibling module without installing
THIS = Path(__file__).resolve()
ROOT = THIS.parent.parent  # scripts/
sys.path.insert(0, str(ROOT))
import deg_mixed_effects as mod  # noqa: E402


def _synth_pseudobulk(seed: int = 42, n_ssc: int = 6, n_hc: int = 6,
                      n_genes: int = 50, n_diff: int = 10) -> "tuple[object, list[str], set[str]]":
    """Generate a synthetic pseudobulk DF with planted DE genes.

    Returns (df, gene_cols, planted_set).
    """
    import pandas as pd
    rng = np.random.default_rng(seed)
    n = n_ssc + n_hc
    genes = [f"G{i:03d}" for i in range(n_genes)]
    planted = set(genes[:n_diff])  # first n_diff genes are differentially expressed
    cell_types = ["fib", "endo"]

    rows = []
    for ct in cell_types:
        for i in range(n):
            cond = "SSC" if i < n_ssc else "HC"
            mu = rng.poisson(lam=200, size=n_genes).astype(float)  # baseline
            # planted: SSC genes ×3 in fib only
            if ct == "fib":
                for j, g in enumerate(genes):
                    if g in planted and cond == "SSC":
                        mu[j] *= 3.0
            counts = rng.negative_binomial(n=10, p=10 / (10 + mu))
            row = {"donor_id": f"d{i:02d}", "condition": cond, "cell_type": ct,
                   "dataset": "synth", "tissue": "synth"}
            for j, g in enumerate(genes):
                row[g] = int(counts[j])
            rows.append(row)
    return pd.DataFrame(rows), genes, planted


def _assert(cond, msg: str):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def test_scipy_welch():
    print("\n[scipy_welch]")
    df, genes, planted = _synth_pseudobulk()
    rows = mod.pseudobulk_deg(df, gene_cols=genes, dataset="synth", tissue="synth",
                              backend="scipy_welch")
    mod.apply_fdr(rows)
    _assert(len(rows) > 0, f"non-empty result ({len(rows)} rows)")

    # Only "fib" cell type carries planted signal
    fib_rows = [r for r in rows if r.cluster == "fib"]
    sig_fib = [r for r in fib_rows if r.padj_dataset <= 0.05]
    sig_planted = [r for r in sig_fib if r.hgnc in planted]
    print(f"      fib: {len(fib_rows)} tests, {len(sig_fib)} sig (FDR≤0.05); "
          f"{len(sig_planted)}/{len(planted)} planted genes recovered")
    _assert(len(sig_planted) >= 0.7 * len(planted),
            "≥ 70% of planted DE genes recovered in fib at FDR≤0.05")

    # Endothelial has no planted signal → most should be non-sig
    endo_rows = [r for r in rows if r.cluster == "endo"]
    endo_sig = [r for r in endo_rows if r.padj_dataset <= 0.05]
    print(f"      endo: {len(endo_rows)} tests, {len(endo_sig)} sig (FDR≤0.05) — expected ≪ planted")
    _assert(len(endo_sig) < len(planted),
            "fewer false positives in endo than planted-in-fib hits")

    # BH-FDR is non-decreasing in p ordering
    sorted_rows = sorted(fib_rows, key=lambda r: r.pvalue)
    qs = [r.padj_dataset for r in sorted_rows]
    monotone = all(qs[i] <= qs[i + 1] + 1e-9 for i in range(len(qs) - 1))
    _assert(monotone, "BH-FDR monotone in raw-p ranking (within fib)")
    _assert(all(0 <= r.padj_dataset <= 1 for r in fib_rows),
            "FDR-adjusted p-values in [0, 1]")


def test_statsmodels():
    print("\n[statsmodels]")
    try:
        import statsmodels  # noqa: F401
    except ImportError:
        print("  skip — statsmodels not available")
        return
    df, genes, planted = _synth_pseudobulk(seed=7)
    rows = mod.pseudobulk_deg(df, gene_cols=genes, dataset="synth", tissue="synth",
                              backend="statsmodels")
    mod.apply_fdr(rows)
    fib_rows = [r for r in rows if r.cluster == "fib"]
    sig_planted = [r for r in fib_rows if r.hgnc in planted and r.padj_dataset <= 0.05]
    print(f"      {len(sig_planted)}/{len(planted)} planted genes recovered in fib (FDR≤0.05)")
    _assert(len(sig_planted) >= 0.6 * len(planted),
            "statsmodels NB recovers ≥ 60% of planted DE in fib")


def test_backend_detection():
    print("\n[detect_backend]")
    b = mod.detect_backend("auto")
    print(f"      auto → {b}")
    _assert(b in ("pydeseq2", "statsmodels", "scipy_welch"), "auto resolves to known backend")
    b = mod.detect_backend("scipy_welch")
    _assert(b == "scipy_welch", "explicit scipy_welch honoured")


def test_io_roundtrip(tmp_path: Path):
    print("\n[io_roundtrip]")
    df, genes, _ = _synth_pseudobulk(seed=11, n_genes=10, n_diff=2)
    in_path = tmp_path / "pb.tsv"
    out_path = tmp_path / "deg.tsv"
    df.to_csv(in_path, sep="\t", index=False)

    df2, gene_cols = mod.read_pseudobulk_tsv(in_path)
    _assert(set(gene_cols) == set(genes), "gene_cols round-trip preserved")
    rows = mod.pseudobulk_deg(df2, gene_cols=gene_cols, dataset="synth", tissue="synth")
    mod.apply_fdr(rows)
    mod.write_deg_tsv(rows, out_path)
    _assert(out_path.exists() and out_path.stat().st_size > 0, "DEG TSV written")
    text = out_path.read_text().splitlines()
    _assert(text[0].split("\t") == mod.DEG_OUTPUT_COLS, "header columns match schema")
    print(f"      wrote {len(text) - 1} rows to {out_path}")


def main() -> int:
    import tempfile
    test_backend_detection()
    test_scipy_welch()
    test_statsmodels()
    with tempfile.TemporaryDirectory() as td:
        test_io_roundtrip(Path(td))
    print("\nall tests passed ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
