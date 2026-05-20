#!/usr/bin/env python3
"""Smoke tests for clinical_correlation.py and demographic_match.py.

Synthetic data with planted correlations and an SSc/HC imbalance;
verifies:
- Spearman ρ + bootstrap CI recover a strong planted correlation.
- The gap-only banner is emitted when no clinical variable is present.
- Propensity matching produces same-sex / similar-age pairs.

Run::

    python3 scripts/tests/test_clinical_correlation.py
"""
from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import clinical_correlation as cc  # noqa: E402
import demographic_match as dm  # noqa: E402


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def _write_tsv(path: Path, rows: list[dict], cols: list[str]):
    with path.open("w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")


# ── tests: clinical_correlation ────────────────────────────────────────────────

def test_spearman_and_bootstrap():
    print("\n[spearman + bootstrap]")
    rng = np.random.default_rng(0)
    # Strong planted positive correlation
    x = rng.normal(size=50)
    y = 0.7 * x + 0.3 * rng.normal(size=50)
    r = cc.spearman(x, y)
    lo, hi = cc.bootstrap_ci(x, y, n_boot=500, seed=1)
    print(f"      ρ = {r:+.3f}   CI95 = [{lo:+.3f}, {hi:+.3f}]")
    _assert(r > 0.5, "Spearman recovers strong positive correlation")
    _assert(lo > 0, "bootstrap CI lower bound > 0 for strong + signal")

    # Null: no correlation
    yz = rng.normal(size=50)
    r0 = cc.spearman(x, yz)
    lo0, hi0 = cc.bootstrap_ci(x, yz, n_boot=500, seed=2)
    print(f"      null ρ = {r0:+.3f}  CI95 = [{lo0:+.3f}, {hi0:+.3f}]")
    _assert(lo0 < 0 < hi0, "bootstrap CI spans 0 under null")


def test_planted_correlation_pipeline():
    print("\n[planted correlation pipeline]")
    rng = np.random.default_rng(3)
    n = 24
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # Synthetic scores
        score_rows = []
        mrss_vals = rng.uniform(0, 40, size=n)
        m1_vals = 0.005 * mrss_vals + 0.05 * rng.normal(size=n)  # planted +
        for i in range(n):
            score_rows.append({
                "donor_id": f"d{i:02d}",
                "group":    "SSc" if i < 16 else "HC",
                "dataset":  "synth",
                "tissue":   "skin",
                "M1": f"{m1_vals[i]:.4f}",
                "M2": f"{rng.normal()*0.05:.4f}",
                "M3": "0.0",
                "M4": "0.0",
                "ssc_tier1": "0.0",
            })
        scores_p = td / "scores.tsv"
        _write_tsv(scores_p, score_rows,
                   ["donor_id","group","dataset","tissue","M1","M2","M3","M4","ssc_tier1"])

        meta_rows = []
        for i in range(n):
            meta_rows.append({
                "dataset": "synth",
                "tissue":  "skin",
                "sample_title": f"d{i:02d}",
                "canon_mrss": f"{mrss_vals[i]:.1f}",
                "canon_age": f"{30 + rng.integers(0, 40)}",
                "canon_sex": "male" if i % 2 == 0 else "female",
                "canon_condition": "SSc" if i < 16 else "control",
            })
        meta_p = td / "meta.tsv"
        _write_tsv(meta_p, meta_rows,
                   ["dataset","tissue","sample_title","canon_mrss","canon_age",
                    "canon_sex","canon_condition"])

        out = td / "corr.tsv"
        summ = cc.analyse(scores_p, meta_p, out, n_boot=300, fig_path=None)
        _assert(summ.get("status") == "ok",
                f"pipeline returns ok status (got {summ})")
        rows = list(csv.DictReader(out.open(), delimiter="\t"))
        # Find the M1↔mrss row
        m1_mrss = [r for r in rows if r["module"] == "M1" and r["clinical_var"] == "mrss"]
        _assert(len(m1_mrss) == 1, "M1↔mrss test present")
        rho = float(m1_mrss[0]["spearman_rho"])
        print(f"      planted M1 vs mRSS ρ recovered = {rho:+.2f}")
        _assert(rho > 0.4, "planted M1↔mRSS correlation recovered (ρ > 0.4)")


def test_gap_when_no_clinical_var():
    print("\n[gap report]")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        scores_p = td / "scores.tsv"
        _write_tsv(scores_p, [{
            "donor_id": "d0", "group": "SSc", "dataset": "synth",
            "tissue": "skin", "M1": "0.5", "M2": "0.3",
            "M3": "0.0", "M4": "0.0", "ssc_tier1": "0.0",
        }], ["donor_id","group","dataset","tissue","M1","M2","M3","M4","ssc_tier1"])
        meta_p = td / "meta.tsv"
        _write_tsv(meta_p, [{
            "dataset":"synth","tissue":"skin","sample_title":"d0",
            "canon_condition":"SSc",  # only categorical, no numeric var
        }], ["dataset","tissue","sample_title","canon_condition"])
        out = td / "corr.tsv"
        summ = cc.analyse(scores_p, meta_p, out, n_boot=100, fig_path=None)
        _assert(summ.get("status") == "no_numeric_clinical_var",
                f"banner emitted when no numeric var (status={summ.get('status')})")
        text = out.read_text().strip().split("\n")
        _assert(any("gap reason" in line for line in text), "TSV carries gap-reason banner")


# ── tests: demographic_match ──────────────────────────────────────────────────

def test_propensity_match():
    print("\n[propensity match]")
    rng = np.random.default_rng(4)
    rows = []
    # 10 SSc and 10 HC, age/sex overlap deliberately
    for i in range(10):
        rows.append({
            "dataset":"synth","sample_title":f"S{i}",
            "canon_age": str(40 + rng.integers(-10, 10)),
            "canon_sex": "female" if i % 2 == 0 else "male",
            "canon_condition": "SSc",
        })
    for i in range(10):
        rows.append({
            "dataset":"synth","sample_title":f"H{i}",
            "canon_age": str(45 + rng.integers(-12, 12)),
            "canon_sex": "female" if i % 2 == 0 else "male",
            "canon_condition": "control",
        })

    eligible = dm.gather_eligible(rows)
    _assert(len(eligible) == 20, "all 20 synthetic donors eligible")
    matched = dm.propensity_match(eligible, calliper_sd=1.0, seed=5)
    pairs = sum(1 for r in matched if r["matched"]) // 2
    print(f"      {pairs} 1:1 SSc-HC pairs after propensity matching")
    _assert(pairs >= 5, f"≥ 5 pairs matched (got {pairs})")

    # Check that matched pairs share sex
    same_sex = 0
    for r in matched:
        if r["matched"] and r["group"] == "SSc":
            partner_name = r["matched_to"]
            partner = next((q for q in matched if q["donor"] == partner_name), None)
            if partner and partner["sex"] == r["sex"]:
                same_sex += 1
    _assert(same_sex >= pairs - 1, "most matched pairs share sex")


def main():
    test_spearman_and_bootstrap()
    test_planted_correlation_pipeline()
    test_gap_when_no_clinical_var()
    test_propensity_match()
    print("\nall tests passed ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
