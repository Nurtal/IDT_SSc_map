#!/usr/bin/env python3
"""Tests for opentargets_coverage.py (issue #12): descriptive output, no verdict.

Run::

    python3 -m pytest -q scripts/tests/test_opentargets_coverage.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import opentargets_coverage as ot  # noqa: E402


def test_committed_output_is_labelled_corroboration_and_carries_no_verdict():
    out = json.loads(ot.OUT.read_text())
    assert out["role"].lower().startswith("corroboration, not validation")
    assert out["source"]["data_version"] and out["source"]["downloaded"]
    flat = json.dumps(out).lower()
    for word in ("verdict", "replicated", "padj", "significant"):
        assert word not in flat


def test_committed_output_reproduces():
    if not ot.SNAPSHOT.exists():
        pytest.skip("OpenTargets snapshot absent (opentargets_coverage.py --fetch)")
    assert ot.main(["--check"]) == 0
