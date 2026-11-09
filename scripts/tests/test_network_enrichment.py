#!/usr/bin/env python3
"""Tests for the community-module enrichment in network_analysis.py (issue #10).

Planted communities with a known answer. Run::

    python3 -m pytest -q scripts/tests/test_network_enrichment.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("networkx")
pytest.importorskip("scipy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import network_analysis as na  # noqa: E402


def _membership():
    # 20 M1 species, 20 M2 species, 20 M3, 20 M4, 20 M5 — one module each.
    return {f"{m}_{i}": {m} for m in na.FROZEN_MODULES for i in range(20)}


def test_planted_pure_community_is_enriched_for_its_module_only():
    mem = _membership()
    pure = {f"M1_{i}" for i in range(15)}
    tests = na.community_module_enrichment([pure], mem)
    sig = {t["module"] for t in tests if t["significant"]}
    assert sig == {"M1"}


def test_mixed_community_is_not_called_enriched():
    mem = _membership()
    mixed = {f"{m}_{i}" for m in na.FROZEN_MODULES for i in range(3)}
    tests = na.community_module_enrichment([mixed], mem)
    assert not any(t["significant"] for t in tests)


def test_family_is_every_large_community_times_every_module():
    mem = _membership()
    big = {f"M2_{i}" for i in range(5)}
    tiny = {"M3_0", "M3_1"}                       # below min_size: not tested
    tests = na.community_module_enrichment([big, tiny], mem)
    assert len(tests) == len(na.FROZEN_MODULES)  # zero intersections kept in the family
    assert {t["community"] for t in tests} == {0}


def test_species_without_a_gene_are_outside_the_universe():
    mem = _membership()
    comm = {f"M4_{i}" for i in range(5)} | {"cGAMP__cyto", "ISG_signature__nuc"}
    tests = na.community_module_enrichment([comm], mem)
    assert all(t["n_community"] == 5 for t in tests)
