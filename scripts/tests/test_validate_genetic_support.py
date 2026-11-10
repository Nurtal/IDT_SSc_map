#!/usr/bin/env python3
"""Tests for validate_genetic_support.py (issue #18).

Planted enrichment with a known answer, then a round-trip on the committed
output when the GWAS snapshot is present.

Run::

    python3 -m pytest -q scripts/tests/test_validate_genetic_support.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import validate_genetic_support as vg  # noqa: E402

UNIVERSE = {f"G{i}" for i in range(2000)}
HITS = {f"G{i}" for i in range(40)}


def test_module_holding_many_gwas_genes_is_enriched():
    e = vg.enrichment({f"G{i}" for i in range(20)} | {"G1500"}, HITS, UNIVERSE)
    assert e["n_overlap"] == 20 and e["p"] < 1e-10
    assert e["overlap_genes"][:2] == ["G0", "G1"]


def test_module_without_gwas_genes_is_not_enriched():
    e = vg.enrichment({f"G{i}" for i in range(1000, 1030)}, HITS, UNIVERSE)
    assert e["n_overlap"] == 0 and e["p"] == 1.0


def test_members_outside_the_universe_are_ignored():
    e = vg.enrichment({"G0", "NOT_PROTEIN_CODING"}, HITS, UNIVERSE)
    assert e["n_members"] == 1


def test_gwas_genes_keep_genome_wide_hits_of_the_resolved_traits_only(tmp_path):
    class H:
        def current(self, s):
            return {"OLD1": "NEW1"}.get(s, s)
    snap = {"associations": [
        {"p_value": 1e-9, "efo_traits": [{"efo_id": "MONDO_0005100"}], "accession_id": "A1",
         "mapped_genes": ["OLD1"], "author_reported_genes": ["STAT4"]},
        {"p_value": 1e-6, "efo_traits": [{"efo_id": "MONDO_0005100"}], "accession_id": "A2",
         "mapped_genes": ["IRF5"]},
        {"p_value": 1e-12, "efo_traits": [{"efo_id": "EFO_9999999"}], "accession_id": "A3",
         "mapped_genes": ["TNFAIP3"]},
    ]}
    genes = vg.gwas_genes(snap, H(), {"NEW1", "STAT4", "IRF5", "TNFAIP3"})
    assert set(genes) == {"NEW1", "STAT4"}


def test_committed_output_reproduces():
    if not vg.SNAPSHOT.exists():
        pytest.skip("GWAS snapshot absent (make validate-genetic after --fetch)")
    assert vg.main(["--check"]) == 0
