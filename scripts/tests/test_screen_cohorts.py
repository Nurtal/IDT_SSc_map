#!/usr/bin/env python3
"""Tests for screen_cohorts.py — cohort screening and freeze (issue #11).

Synthetic samples with a known arm; assertions on the assignment and on the
symbol resolution, then a round-trip on the committed outputs when the raw
inputs are present.

Run::

    python3 -m pytest -q scripts/tests/test_screen_cohorts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import screen_cohorts as sc  # noqa: E402


def sample(title, **chars):
    return {"gsm": "GSM0", "title": title, "source": "skin biopsy", "chars": chars}


def test_gse130955_keeps_first_biopsy_per_subject_only():
    arms = sc.arms_gse130955([
        sample("S001_P", **{"diagnosis": "SSc patient", "biopsy number for this subject": "1"}),
        sample("S002_P", **{"diagnosis": "SSc patient", "biopsy number for this subject": "2"}),
        sample("S003_N", **{"diagnosis": "healthy control", "biopsy number for this subject": "1"}),
    ])
    assert [a for a, _ in arms] == ["SSc", "excluded", "HC"]


def test_gse58095_handles_shifted_labels_and_longitudinal_resamples():
    arms = sc.arms_gse58095([
        sample("PATIENT01", tissue="skin biopsy"),
        sample("SAMPLE001", group="Control"),
        sample("SAMPLE061", **{"time point": "Late"}),
        sample("SAMPLE082", group="SSc", **{"affected (1=yes)": "0", "time point": "Early"}),
        sample("SAMPLE088", group="SSc"),
        sample("SAMPLE093", group="SSc", **{"affected (1=yes)": "1"}),
        sample("SAMPLE099"),
    ])
    assert [a for a, _ in arms] == ["SSc", "HC", "excluded", "excluded", "SSc", "SSc", "excluded"]


@pytest.fixture
def hgnc(tmp_path):
    p = tmp_path / "hgnc.tsv"
    p.write_text(
        "symbol\tstatus\tensembl_gene_id\tprev_symbol\n"
        "TAFAZZIN\tApproved\tENSG1\tTAZ\n"
        "WWTR1\tApproved\tENSG2\t\n"
        "STING1\tApproved\tENSG3\tTMEM173\n"
        "COL1A1\tApproved\tENSG4\t\n"
    )
    return sc.Hgnc(p)


def test_map_taz_is_the_yap_coactivator_not_tafazzin(hgnc):
    assert hgnc.map_symbol("TAZ") == "WWTR1"
    assert hgnc.current("TAZ") == "TAFAZZIN"   # a platform's TAZ probe is tafazzin


def test_previous_symbols_resolve_to_the_approved_successor(hgnc):
    assert hgnc.map_symbol("TMEM173") == "STING1"
    assert hgnc.current("COL1A1") == "COL1A1"
    assert hgnc.current("UNKNOWN") == "UNKNOWN"


def test_committed_screening_matches_a_fresh_run():
    if any(not p.exists() for p in sc.FETCH):
        pytest.skip("screening inputs absent (python3 scripts/screen_cohorts.py --fetch)")
    assert sc.main(["--check"]) == 0
