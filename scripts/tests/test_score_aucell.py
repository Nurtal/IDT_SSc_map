#!/usr/bin/env python3
"""Smoke test for scripts/score_aucell.py.

Builds a synthetic pseudobulk with two modules:
- M1 genes elevated in SSc donors,
- M2 genes elevated in HC donors (i.e. reverse signal).

Checks:
1. AUCell separates SSc vs HC in the right direction per module.
2. Z-score does the same and is sign-blind.
3. Donors with no module-set expression score ≈ 0 for an unrelated
   module (M3).
4. CLI round-trip writes the expected files.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import score_aucell as mod  # noqa: E402


def _synth_pb(n_ssc=6, n_hc=6, n_genes=200, seed=0):
    """Return (df, module_sets)."""
    import pandas as pd
    rng = np.random.default_rng(seed)
    genes = [f"G{i:03d}" for i in range(n_genes)]
    m1 = set(genes[:10])    # elevated in SSc
    m2 = set(genes[10:25])  # elevated in HC
    m3 = set(genes[25:40])  # nothing planted (negative control)
    rows = []
    for i in range(n_ssc + n_hc):
        cond = "SSC" if i < n_ssc else "HC"
        mu = rng.poisson(50, size=n_genes).astype(float)
        if cond == "SSC":
            for j, g in enumerate(genes):
                if g in m1: mu[j] *= 4
        else:
            for j, g in enumerate(genes):
                if g in m2: mu[j] *= 4
        counts = rng.negative_binomial(10, 10 / (10 + mu))
        row = {"donor_id": f"d{i:02d}", "condition": cond,
               "cell_type": "all", "dataset": "synth", "tissue": "synth"}
        for j, g in enumerate(genes):
            row[g] = int(counts[j])
        rows.append(row)
    df = pd.DataFrame(rows)
    return df, {"M1": m1, "M2": m2, "M3": m3, "M4": set(), "ssc_tier1": set()}


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def test_aucell_directionality():
    print("\n[aucell directionality]")
    df, msets = _synth_pb()
    auc_rows, z_rows, T = mod.score_donors(df, msets)
    _assert(len(auc_rows) == 12, f"all 12 donors scored ({len(auc_rows)})")

    def mean_mod(rows, group, m):
        vs = [r[m] for r in rows if r["group"] == group]
        return sum(vs) / len(vs) if vs else 0.0

    ssc_m1 = mean_mod(auc_rows, "SSc", "M1")
    hc_m1  = mean_mod(auc_rows, "HC",  "M1")
    ssc_m2 = mean_mod(auc_rows, "SSc", "M2")
    hc_m2  = mean_mod(auc_rows, "HC",  "M2")
    print(f"      AUCell M1: SSc {ssc_m1:.3f}  HC {hc_m1:.3f}  Δ={ssc_m1-hc_m1:+.3f}")
    print(f"      AUCell M2: SSc {ssc_m2:.3f}  HC {hc_m2:.3f}  Δ={ssc_m2-hc_m2:+.3f}")
    _assert(ssc_m1 > hc_m1, "AUCell M1 elevated in SSc (planted up in SSc)")
    _assert(hc_m2 > ssc_m2, "AUCell M2 elevated in HC (planted up in HC) — sign-blind")

    # M3 is negative control: AUCell should be ~ baseline rate
    ssc_m3 = mean_mod(auc_rows, "SSc", "M3")
    hc_m3  = mean_mod(auc_rows, "HC",  "M3")
    print(f"      AUCell M3 (neg-ctrl): SSc {ssc_m3:.3f}  HC {hc_m3:.3f}  Δ={ssc_m3-hc_m3:+.3f}")
    _assert(abs(ssc_m3 - hc_m3) < max(abs(ssc_m1 - hc_m1), abs(hc_m2 - ssc_m2)),
            "M3 SSc-HC delta smaller than M1/M2 (neg-ctrl)")


def test_zscore_directionality():
    print("\n[zscore directionality]")
    df, msets = _synth_pb(seed=1)
    _, z_rows, _ = mod.score_donors(df, msets)
    ssc_m1 = sum(r["M1"] for r in z_rows if r["group"] == "SSc") / 6
    hc_m1  = sum(r["M1"] for r in z_rows if r["group"] == "HC")  / 6
    ssc_m2 = sum(r["M2"] for r in z_rows if r["group"] == "SSc") / 6
    hc_m2  = sum(r["M2"] for r in z_rows if r["group"] == "HC")  / 6
    print(f"      Z M1: SSc {ssc_m1:+.3f}  HC {hc_m1:+.3f}")
    print(f"      Z M2: SSc {ssc_m2:+.3f}  HC {hc_m2:+.3f}")
    _assert(ssc_m1 > hc_m1, "Z-score M1 elevated in SSc")
    _assert(hc_m2 > ssc_m2, "Z-score M2 elevated in HC")


def test_module_gene_set_loader():
    print("\n[module gene set loader]")
    # Use the real annotations file
    tsv = ROOT.parent / "curation" / "annotations" / "species_annotations.tsv"
    if not tsv.exists():
        print(f"  skip — {tsv} absent")
        return
    msets = mod.load_module_gene_sets(tsv)
    print(f"      loaded modules: {sorted(msets.keys())}")
    for m in ("M1", "M2", "M3", "M4", "ssc_tier1"):
        if m in msets:
            print(f"      {m}: {len(msets[m])} HGNC symbols")
    _assert(any(m in msets for m in ("M1","M2","M3","M4")),
            "at least one canonical module loaded from real annotations")
    _assert(len(msets.get("M1", set())) >= 20,
            f"M1 has ≥ 20 genes (got {len(msets.get('M1', set()))})")


def test_cli_roundtrip():
    print("\n[CLI round-trip]")
    df, msets = _synth_pb(seed=2)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        pb_path = td / "pb.tsv"
        df.to_csv(pb_path, sep="\t", index=False)
        # Fake species_annotations.tsv with the synthetic modules
        sp_path = td / "species.tsv"
        with sp_path.open("w") as fh:
            fh.write("species_id\thgnc_symbol\tmodule\n")
            for m, gset in msets.items():
                for g in gset:
                    fh.write(f"sp_{g}\t{g}\t{m}\n")
        auc_path = td / "aucell.tsv"
        z_path   = td / "zscore.tsv"
        rc = mod.main([
            "--pseudobulk", str(pb_path),
            "--species-tsv", str(sp_path),
            "--out-aucell", str(auc_path),
            "--out-zscore", str(z_path),
        ])
        _assert(rc == 0, "CLI returns 0")
        _assert(auc_path.exists() and z_path.exists(), "both output files written")
        head = auc_path.read_text().splitlines()[0]
        _assert(head.split("\t")[:4] == ["donor_id","group","dataset","tissue"],
                "AUCell header has expected leading columns")


def main():
    test_aucell_directionality()
    test_zscore_directionality()
    test_module_gene_set_loader()
    test_cli_roundtrip()
    print("\nall tests passed ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
