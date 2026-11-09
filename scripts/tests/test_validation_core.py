#!/usr/bin/env python3
"""Tests for validation_core.py — the shared L2 decision rules (issue #9).

Planted effects with a known answer; assertions on the verdict reached, not on
intermediate scores. The golden-master test re-runs the migrated M5 analysis
on GSE45536 and must reproduce the audited published values; it skips when
the cohort files are absent.

Run::

    python3 -m pytest -q scripts/tests/test_validation_core.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import validation_core as vc  # noqa: E402

N_CASE, N_CTRL, N_GENES, N_MOD = 40, 40, 400, 25


def cohort(shift: float, seed: int):
    """genes × samples; the first N_MOD genes are the module, shifted in cases."""
    rng = np.random.default_rng(seed)
    expr = rng.normal(size=(N_GENES, N_CASE + N_CTRL))
    expr[:N_MOD, :N_CASE] += shift
    mask = np.zeros(N_GENES, dtype=bool)
    mask[:N_MOD] = True
    return expr, mask


def result(module, source, shift, seed, ref="up", n_detectable=N_MOD, score=vc.singscore):
    expr, mask = cohort(shift, seed)
    s = score(expr, mask)
    return vc.make_result(module, source, n_detectable, s[:N_CASE], s[N_CASE:],
                          reference_direction=ref)


def run(results):
    family = vc.adjust_family(results)
    return vc.decide(results), family


# ── scoring is sign-blind and membership-only ──────────────────────────────────

@pytest.mark.parametrize("score", [vc.singscore, vc.zscore_score])
def test_planted_up_and_down_effects_move_the_score_their_own_way(score):
    for shift, expected in ((1.5, "up"), (-1.5, "down")):
        expr, mask = cohort(shift, seed=1)
        s = score(expr, mask)
        assert vc.contrast(s[:N_CASE], s[N_CASE:]).direction == expected


# ── the four verdicts ──────────────────────────────────────────────────────────

def test_planted_effect_in_reference_direction_is_replicated():
    verdicts, _ = run([result("M1", "c1", 1.5, 1), result("M1", "c2", 1.5, 2)])
    assert verdicts["M1"] == vc.REPLICATED


def test_planted_effect_opposite_to_reference_is_contradicted():
    verdicts, _ = run([result("M2", "c1", -1.5, 3, ref="up")])
    assert verdicts["M2"] == vc.CONTRADICTED


def test_contradiction_is_not_absorbed_by_a_replication_elsewhere():
    verdicts, _ = run([result("M2", "c1", 1.5, 4), result("M2", "c2", -1.5, 5)])
    assert verdicts["M2"] == vc.CONTRADICTED


def test_module_without_planted_signal_is_not_called_replicated():
    verdicts, _ = run([result("M3", "c1", 0.0, 6), result("M3", "c2", 0.0, 7)])
    assert verdicts["M3"] == vc.NOT_REPLICATED


def test_replication_in_some_but_not_all_cohorts_is_partial():
    verdicts, _ = run([result("M4", "c1", 1.5, 8), result("M4", "c2", 0.0, 9)])
    assert verdicts["M4"] == vc.PARTIAL


# ── the family ─────────────────────────────────────────────────────────────────

def test_module_below_floor_is_excluded_from_the_family_and_recorded():
    small = result("M5", "c1", 1.5, 10, n_detectable=vc.MIN_DETECTABLE - 1)
    big = result("M1", "c1", 1.5, 11)
    verdicts, family = run([small, big])
    assert family["members"] == ["M1|c1"]
    assert family["excluded_not_testable"] == ["M5|c1"]
    assert small.padj is None and verdicts["M5"] is None


def test_adjustment_runs_over_the_declared_family_only():
    rs = [result("M1", f"c{i}", 0.0, 20 + i) for i in range(4)]
    rs.append(result("M2", "c0", 1.5, 30, n_detectable=3))     # not testable
    vc.adjust_family(rs)
    testable_p = [r.p for r in rs if r.testable]
    assert [r.padj for r in rs if r.testable] == pytest.approx(vc.bh(testable_p))


def test_result_record_carries_every_field_the_spec_requires():
    r = result("M1", "c1", 1.5, 40)
    r.registered_prediction = "up (high)"
    run([r])
    d = r.to_dict()
    for key in ("module", "source", "direction", "effect_size", "n_case", "n_control",
                "p", "padj", "testable", "verdict", "registered_prediction"):
        assert d[key] is not None, key


def test_deciding_before_adjusting_fails_loudly():
    r = result("M1", "c1", 1.5, 41)
    with pytest.raises(ValueError):
        vc.decide([r])


# ── golden master: the migrated M5 precedent reproduces its audited values ─────

PUBLISHED = {  # analysis/overlay/m5_gse45536_validation.json as audited (commit 48facfc)
    "M5": (-0.29142716312630734, 0.00012690491346156236, 19, 47),
    "autoantigens": (1.0711498507816106, 1.7118757995067647e-10, 2, 3),
    "plasma_core": (-0.42832511875755497, 2.0201665543862756e-06, 6, 15),
    "b_surface": (-0.33686702364375026, 0.0018232680446515941, 9, 24),
}


def test_m5_golden_master_reproduces_published_values():
    import validate_m5_gse45536 as m5
    if not (m5.MAT.exists() and m5.SOFT.exists()):
        pytest.skip("GSE45536 cohort files absent (make fetch-gse45536) — golden master not run")
    samples, phen, rows = m5.load_matrix()
    grp = np.array(["SSc" if "scleroderma" in (p or "").lower() else
                    ("HC" if "healthy" in (p or "").lower() else "other") for p in phen])
    sigs = {"M5": m5.module_genes("M5"), **m5.SUBSIGS}
    for name, (delta, p, n_genes, n_probes) in PUBLISHED.items():
        r = m5.score_signature(rows, samples, grp, sigs[name])
        assert (r["n_ssc"], r["n_hc"]) == (99, 24)
        assert (r["n_genes_mapped"], r["n_probes"]) == (n_genes, n_probes), name
        assert r["delta"] == pytest.approx(delta, rel=1e-12), name
        assert r["p"] == pytest.approx(p, rel=1e-9), name
