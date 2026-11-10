#!/usr/bin/env python3
"""Tests for check_numbers.py (issue #5): fails on a seeded stale number,
passes on the current tree, and exempts history only by explicit rule.

Run::

    python3 -m pytest -q scripts/tests/test_check_numbers.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check_numbers as cn  # noqa: E402


def _docs():
    return {d: (cn.ROOT / d).read_text() for d in cn.SCANNED}


def test_current_tree_passes():
    assert cn.check(_docs()) == []


def test_seeded_stale_card_count_fails_and_names_document_and_artefact():
    docs = _docs()
    docs["README.md"] = docs["README.md"].replace("**143**", "**145**", 1)
    problems = cn.check(docs)
    assert len(problems) == 1
    assert problems[0].startswith("README.md:") and "interaction_database.csv" in problems[0]


def test_seeded_stale_coverage_fraction_fails():
    docs = _docs()
    key = "manuscript/SSc_MIM_manuscript_draft.md"
    docs[key] = docs[key].replace("195/236 (82.6 %)", "161/236 (81.3 %)", 1)
    assert any("161/236" in p for p in cn.check(docs))


def test_stale_number_inside_a_historical_section_is_exempt():
    docs = _docs()
    head = "## What's done (with commit refs)\n"
    docs["STATUS.md"] = docs["STATUS.md"].replace(head, head + "\nA past state: 58 overlays.\n", 1)
    assert cn.check(docs) == []


def test_same_stale_number_outside_history_fails():
    docs = _docs()
    docs["STATUS.md"] += "\nCurrent: 58 overlays.\n"
    assert any("MINERVA overlays" in p for p in cn.check(docs))
