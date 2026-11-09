#!/usr/bin/env python3
"""Tests for build_module_genesets.py — the frozen module gene sets (issue #2).

Planted inputs with a known answer; assertions on the gene sets and verdicts
the builder reaches, then a round-trip on the real committed artefacts.

Run::

    python3 -m pytest -q scripts/tests/test_build_module_genesets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build_module_genesets as bg  # noqa: E402


def ann(sid, sym, module):
    return {"species_id": sid, "hgnc_symbol": sym, "module": module}


def rxn(rid, module, reactants="", products="", modifiers=""):
    return {"reaction_id": rid, "module": module, "reactants": reactants,
            "products": products, "modifiers": modifiers}


def sets(rows):
    out = {}
    for r in rows:
        out.setdefault(r["module"], set()).add(r["hgnc_symbol"])
    return out


ANN = [
    ann("A__cyto", "A", "M1"),
    ann("B__cyto", "B", "M1,M2"),
    ann("T1__cyto", "T1", "ssc_tier1"),     # Tier-1: no module label of its own
    ann("C__nuc", "C", "M5"),
    ann("cGAMP__cyto", "", "M1"),           # metabolite: no symbol
    ann("X__cyto", "X", "crosstalk"),
]


def test_membership_follows_module_column_not_reaction_id():
    # An M5 reaction still carrying its pre-split ssc_M4_ prefix.
    curated = [rxn("ssc_M4_011", "M5", reactants="T1__cyto", products="C__nuc")]
    rows, _ = bg.build(ANN, curated, measured={"A", "B", "C", "T1"})
    s = sets(rows)
    assert "T1" in s["M5"]
    assert "T1" not in s.get("M4", set())


def test_tier1_symbol_joins_its_module_through_the_curated_layer():
    curated = [rxn("r1", "M2", reactants="T1__cyto", modifiers="cGAMP__cyto")]
    rows, summary = bg.build(ANN, curated, measured={"A", "B", "C", "T1"})
    assert "T1" in sets(rows)["M2"]
    t1 = next(r for r in rows if r["hgnc_symbol"] == "T1")
    assert t1["source"] == "curated_layer"


def test_overlap_is_reported():
    rows, summary = bg.build(ANN, [], measured={"A", "B", "C"})
    assert summary["pairwise_overlap"]["M1|M2"] == 1
    assert summary["multi_module_symbols"] == {"B": ["M1", "M2"]}
    b_in_m1 = next(r for r in rows if r["module"] == "M1" and r["hgnc_symbol"] == "B")
    assert b_in_m1["other_modules"] == "M2"


def test_module_below_floor_is_not_testable_and_floor_is_recorded():
    rows, summary = bg.build(ANN, [], measured={"A", "B", "C"}, floor=2)
    assert summary["min_detectable_symbols"] == 2
    assert summary["per_module"]["M1"]["testable"] is True     # A, B
    assert summary["per_module"]["M5"]["testable"] is False    # C only
    assert "M5" in summary["not_testable"]


def test_unmeasured_symbol_is_flagged_not_detectable():
    rows, summary = bg.build(ANN, [], measured={"B"}, floor=1)
    a = next(r for r in rows if r["hgnc_symbol"] == "A")
    assert a["detectable"] == "false"
    assert summary["per_module"]["M1"]["not_detectable"] == ["A"]


def test_crosstalk_reaction_joins_no_module_but_orphans_are_listed():
    curated = [rxn("x1", "crosstalk", reactants="X__cyto", products="A__cyto")]
    rows, summary = bg.build(ANN, curated, measured=set())
    assert "X" not in {r["hgnc_symbol"] for r in rows}
    assert summary["crosstalk_symbols_in_no_module"] == ["X"]


@pytest.mark.parametrize("curated, annotations", [
    ([rxn("r1", "M1", reactants="GHOST__cyto")], ANN),          # unknown species
    ([rxn("r1", "M6", reactants="A__cyto")], ANN),              # unknown module
    ([], ANN + [ann("Z__cyto", "Z", "M9")]),                    # unknown label
])
def test_inputs_that_do_not_reconcile_fail_the_build(curated, annotations):
    with pytest.raises(bg.GenesetError):
        bg.build(annotations, curated, measured=set())


def test_build_is_deterministic():
    curated = [rxn("r1", "M2", reactants="T1__cyto")]
    first = bg.build(ANN, curated, measured={"A", "T1"})
    second = bg.build(list(reversed(ANN)), curated, measured={"T1", "A"})
    assert first == second


def test_committed_artefacts_match_a_fresh_build(capsys):
    assert bg.main(["--check"]) == 0
