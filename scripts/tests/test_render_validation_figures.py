#!/usr/bin/env python3
"""Tests for render_validation_figures.py (issue #21): the committed figures
regenerate byte-identically from the committed result files.

Run::

    python3 -m pytest -q scripts/tests/test_render_validation_figures.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
pytest.importorskip("matplotlib")
import render_validation_figures as rv  # noqa: E402

STEMS = ("F8_independent_validation", "F3b_community_concordance")


def _digests():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for s in STEMS for p in sorted(rv.FIGS.glob(f"{s}.svg"))}


def test_svg_figures_regenerate_identically():
    before = _digests()
    assert len(before) == len(STEMS)
    rv.main()
    assert _digests() == before
