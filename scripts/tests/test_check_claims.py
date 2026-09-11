#!/usr/bin/env python3
"""Tests for check_claims.py — the guard against untrue review-status claims.

The rule logic runs on in-memory documents ({path: text}); the last tests run
the guard on the real tracked tree, clean and with a seeded violation.

Run::

    python3 -m pytest -q scripts/tests/test_check_claims.py
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check_claims as cc  # noqa: E402

BANNER = (
    "> *Internally generated pre-submission critique. Not a journal review.\n"
    "> The manuscript has never been submitted.*\n"
)


def _problems(documents, allowlist=None):
    return cc.check(documents, allowlist or {}).problems


# ── detection ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "phrase",
    [
        "peer review",
        "Peer-reviewed",
        "PEER REVIEWED",
        "expert-validated",
        "Expert validated",
        "expert-curated",
        "community-curated",
        "Community curated",
        "as requested by the reviewer",
        "As requested by the Editor",
        "as requested by Reviewer 2",
        "major revision",
        "Major Revision",
        "minor-to-major revision",
    ],
)
def test_forbidden_phrasings_detected_case_insensitively(phrase):
    claims = cc.find_claims(f"Intro line.\nThis map, {phrase}, is done.\n")
    assert len(claims) == 1
    assert claims[0].line == 2


@pytest.mark.parametrize(
    "text",
    [
        "The reviewer deck is a mechanism offered for adjudication.",
        "Revision of the citation layer.",
        "No expert validation has happened.",
        "A peer of the curator reviewed nothing.",
        "Curated by one curator; the community may adjudicate.",
    ],
)
def test_innocuous_text_not_flagged(text):
    assert cc.find_claims(text) == []


def test_phrase_wrapped_across_lines_reported_at_its_first_line():
    claims = cc.find_claims("one\nthe work went through peer\nreview last year\n")
    assert [(c.line, c.phrase) for c in claims] == [(2, "peer review")]


def test_phrase_wrapped_inside_a_blockquote_is_detected():
    claims = cc.find_claims("> the npj-SBA major\n> revision was planned\n")
    assert [(c.line, c.phrase) for c in claims] == [(1, "major revision")]


def test_reported_phrase_is_the_whole_word():
    assert [c.phrase for c in cc.find_claims("It was Peer-reviewed.")] == [
        "Peer-reviewed"
    ]


def test_violation_names_file_line_and_phrase():
    problems = _problems({"README.md": "Title\n\nThe map is expert-curated.\n"})
    assert problems == ['README.md:3: "expert-curated"']


# ── structural exemptions ─────────────────────────────────────────────────────


def test_journal_is_exempt():
    report = cc.check({"journal.md": "Decision: Major Revision.\n"}, {})
    assert report.problems == []
    assert any("journal.md" in e for e in report.exempt)


def test_bannered_presubmission_review_file_is_exempt():
    doc = {f"{cc.PRESUBMISSION_REVIEW_DIR}R1.md": BANNER + "\n**Major revision.**\n"}
    assert _problems(doc) == []


def test_unbannered_presubmission_review_file_is_scanned():
    doc = {
        f"{cc.PRESUBMISSION_REVIEW_DIR}R1.md": "# Reviewer 1\n\n**Major revision.**\n"
    }
    assert _problems(doc) == [f'{cc.PRESUBMISSION_REVIEW_DIR}R1.md:3: "Major revision"']


def test_banner_below_the_first_lines_does_not_count():
    doc = {
        f"{cc.PRESUBMISSION_REVIEW_DIR}R1.md": "\n" * cc.BANNER_LINES
        + BANNER
        + "Major revision.\n"
    }
    assert len(_problems(doc)) == 1


def test_banner_does_not_exempt_files_outside_the_presubmission_review():
    assert len(_problems({"README.md": BANNER + "Major revision.\n"})) == 1


# ── mention marker ────────────────────────────────────────────────────────────


def test_mention_marker_exempts_its_own_line_only():
    text = (
        '"Expert-curated" must not be used. <!-- claims-guard: mention -->\n'
        "The map is expert-curated.\n"
    )
    assert _problems({"CONTEXT.md": text}) == ['CONTEXT.md:2: "expert-curated"']


@pytest.mark.parametrize(
    "path", ["CONTEXT.md", "docs/planning/specs/tickets/L1/01-x.md"]
)
def test_mention_marker_honoured_in_rule_documents(path):
    text = '"Expert-curated" must not be used. <!-- claims-guard: mention -->\n'
    assert _problems({path: text}) == []


def test_mention_marker_ignored_outside_rule_documents():
    text = "The map is expert-curated. <!-- claims-guard: mention -->\n"
    assert _problems({"README.md": text}) == ['README.md:1: "expert-curated"']


# ── allowlist ─────────────────────────────────────────────────────────────────

DIRTY = {"README.md": "a peer review\nand a major revision\n"}


def test_allowlisted_file_at_its_pinned_count_passes():
    report = cc.check(DIRTY, {"README.md": (2, "#7 (L1-T3)")})
    assert report.problems == []
    assert any("README.md" in a and "#7" in a for a in report.allowed)


def test_new_claim_in_an_allowlisted_file_fails():
    problems = _problems(DIRTY, {"README.md": (1, "#7 (L1-T3)")})
    assert any("new claim" in p for p in problems)
    assert 'README.md:2: "major revision"' in problems


def test_partially_cleaned_file_must_lower_its_pin():
    problems = _problems(DIRTY, {"README.md": (3, "#7 (L1-T3)")})
    assert len(problems) == 1 and "lower the pin to 2" in problems[0]


def test_cleaned_file_still_allowlisted_fails():
    problems = _problems({"README.md": "clean\n"}, {"README.md": (2, "#7 (L1-T3)")})
    assert len(problems) == 1 and "remove its ALLOWLIST entry" in problems[0]


def test_allowlisted_file_that_is_no_longer_scanned_fails():
    problems = _problems({}, {"gone.md": (1, "#7 (L1-T3)")})
    assert len(problems) == 1 and "gone.md" in problems[0]


def test_allowlisted_file_that_became_exempt_fails():
    path = f"{cc.PRESUBMISSION_REVIEW_DIR}R1.md"
    problems = _problems(
        {path: BANNER + "Major revision.\n"}, {path: (1, "#6 (L1-T2)")}
    )
    assert len(problems) == 1 and "remove its ALLOWLIST entry" in problems[0]


def test_every_allowlist_entry_names_a_ticket():
    for path, (pinned, ticket) in cc.ALLOWLIST.items():
        assert pinned > 0, path
        assert "#" in ticket, f"{path}: allowlist entry must name its ticket"


# ── exit code ─────────────────────────────────────────────────────────────────


def test_run_exits_nonzero_on_a_violation_and_zero_when_clean():
    out = io.StringIO()
    assert cc.run({"README.md": "The map is expert-validated.\n"}, {}, out=out) == 1
    assert 'README.md:1: "expert-validated"' in out.getvalue()
    assert cc.run({"README.md": "A curated map.\n"}, {}, out=io.StringIO()) == 0


def test_real_tree_passes():
    assert cc.main([]) == 0


def test_real_tree_with_a_seeded_violation_fails():
    documents = cc.load_documents(cc.ROOT)
    documents["docs/seeded.md"] = "SSc-MIM is a community-curated map.\n"
    assert cc.run(documents, cc.ALLOWLIST, out=io.StringIO()) == 1
