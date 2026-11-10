#!/usr/bin/env python3
"""Smoke tests for validate_external_cohorts.py (issue #17).

The decision rules are covered by test_validation_core.py; here: the committed
outputs reproduce from the frozen inputs, and the result shape carries what
the ticket requires. Skips when the cohort inputs are absent.

Run::

    python3 -m pytest -q scripts/tests/test_validate_external_cohorts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
pytest.importorskip("pandas")
import screen_cohorts as sc  # noqa: E402
import validate_external_cohorts as vx  # noqa: E402

needs_data = pytest.mark.skipif(any(not p.exists() for p in sc.FETCH),
                                reason="cohort inputs absent (make screen-cohorts)")


def test_reference_directions_reproduce():
    assert vx.main(["--references", "--check"]) == 0


@needs_data
def test_replication_output_reproduces():
    assert vx.main(["--check"]) == 0


def test_committed_output_reports_every_pair_with_the_required_fields():
    out = json.loads(vx.OUT.read_text())
    for label in ("primary_singscore", "sensitivity_zscore"):
        results = out[label]["results"]
        assert len(results) == len(out[label]["family"]["members"]) + len(
            out[label]["family"]["excluded_not_testable"])
        for r in results:
            for key in ("module", "source", "direction", "effect_size", "n_case", "n_control",
                        "p", "padj", "registered_prediction"):
                assert r[key] is not None, (label, r["module"], r["source"], key)


def test_null_reference_gives_no_verdict():
    out = json.loads(vx.OUT.read_text())
    refs = json.loads(vx.REFERENCES.read_text())["modules"]
    for m, ref in refs.items():
        if ref["p"] > vx.REFERENCE_ALPHA:
            assert out["primary_singscore"]["verdicts"][m].startswith("descriptive only")
