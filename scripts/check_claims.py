#!/usr/bin/env python3
"""CI guard: no document may claim something untrue about how this work was reviewed.

Failure mode this prevents: the simulated pre-submission review left the
repository asserting a journal revision cycle, reviewer-requested changes and
an expert-curated map. The manuscript has never been submitted to any journal,
and no reaction has been ratified by anyone (see CONTEXT.md, "Simulated
pre-submission review" and "Ratification"). Until this guard, only a
proofreading pass could catch such a claim reappearing.

Rule: no scanned document may contain one of the FORBIDDEN phrasings —
matched case-insensitively, with a space, hyphen or line break between the
words — nor one of the three revision-cycle assertions ticket #7 retires (a
revision "merged", E-items "closed", framing "per the editor"). Each hit is
reported as `path:line: "phrase"`.

Scanned: every git-tracked file with a prose suffix (SCANNED_SUFFIXES), plus
the deposition metadata files (SCANNED_NAMES). Code and data files are not
documents and are not scanned.

Structural exemptions — permanent, and the only ones:
  1. JOURNAL, the historical log, kept untouched as a record.
  2. A file in PRESUBMISSION_REVIEW_DIR that carries the standing banner within
     its first BANNER_LINES lines: internally generated, not a journal review,
     the manuscript never submitted. An unbannered file there is scanned like
     any other.
  3. In RULE_DOCUMENTS only — the glossary, and the plan, specs and tickets
     that specify this cleanup — a line that names a forbidden phrasing in
     order to forbid it or deny it of this project carries the marker
     `claims-guard: mention` (in Markdown, inside an HTML comment). The marker
     exempts that line only, and is ignored in every other document.

ALLOWLIST — temporary. See the comment above it.

Run:
    python3 scripts/check_claims.py            # exit 1 on any violation
    python3 scripts/check_claims.py --strict   # also exit 1 while ALLOWLIST is non-empty
or  make check-claims
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple, TextIO

ROOT = Path(__file__).resolve().parents[1]

SCANNED_SUFFIXES = {".md", ".txt", ".rst", ".tex", ".html", ".cff"}
SCANNED_NAMES = {".zenodo.json", "ro-crate-metadata.json"}

JOURNAL = "journal.md"
PRESUBMISSION_REVIEW_DIR = "presubmission_review/"
BANNER_LINES = 5
BANNER_MARKS = ("internally generated", "not a journal review", "never been submitted")

MENTION_MARKER = "claims-guard: mention"
RULE_DOCUMENTS = (
    "CONTEXT.md",
    "docs/planning/npj_submission_plan.md",
    "docs/planning/specs/",
)

# Between two words: whitespace, any hyphen, or a line break continuing a
# Markdown blockquote ("major\n> revision").
_SEP = r"[\s>\-‐‑]+"
_WS = r"\s+"
FORBIDDEN: dict[str, re.Pattern[str]] = {
    "peer review": re.compile(rf"\bpeer{_SEP}review\w*", re.IGNORECASE),
    "expert-validated": re.compile(rf"\bexpert{_SEP}validated\b", re.IGNORECASE),
    "expert-curated": re.compile(rf"\bexpert{_SEP}curated\b", re.IGNORECASE),
    "community-curated": re.compile(rf"\bcommunity{_SEP}curated\b", re.IGNORECASE),
    "as requested by the reviewer/editor": re.compile(
        rf"\bas{_WS}requested{_WS}by{_WS}(?:the{_WS})?(?:reviewer|editor)s?\b",
        re.IGNORECASE,
    ),
    "major revision": re.compile(rf"\bmajor{_SEP}revisions?\b", re.IGNORECASE),
    # Ticket #7's revision-cycle assertions, "in any form". A dot ends the span
    # unless it sits inside a version number ("revision v1.1 MERGED").
    "revision … merged": re.compile(
        r"\brevision\b(?:[^.]|\.(?=\d)){0,40}?\bmerged\b", re.IGNORECASE
    ),
    "E-items … closed": re.compile(r"\bE-items?\b[^.]{0,30}?\bclosed\b", re.IGNORECASE),
    "per the editor": re.compile(rf"\bper{_WS}(?:the{_WS})?editors?\b", re.IGNORECASE),
}

# Files dirty today — TEMPORARY. Each entry pins the file's exact occurrence
# count and names the ticket that will clean it. The build fails when a count
# rises (a new claim), drops (lower the pin) or reaches zero (remove the
# entry), so every cleanup ticket visibly shrinks this list.
#
# RULE: the allowlist MUST be empty before submission. Ticket #16 (L1-T5) is
# not done until it is; entries outside any ticket's named files fall to it.
ALLOWLIST: dict[str, tuple[int, str]] = {
    # The project documents a newcomer reads.
    "CHANGELOG.md": (3, "#7 (L1-T3)"),
    "README.md": (3, "#7 (L1-T3)"),
    "ROADMAP.md": (2, "#7 (L1-T3)"),
    "STATUS.md": (3, "#7 (L1-T3)"),
    # Dated records carrying the same vocabulary.
    "analysis/baseline_v1.0/README.md": (1, "#7 (L1-T3)"),
    "docs/archive/biomodels_submission.md": (1, "#7 (L1-T3)"),
    "docs/planning/historical_roadmap.md": (2, "#7 (L1-T3)"),
    "docs/standups/2026-05-20_revision_kickoff.md": (3, "#7 (L1-T3)"),
    # The manuscript.
    "manuscript/SSc_MIM_manuscript_draft.md": (3, "#8 (L1-T4)"),
}


class Claim(NamedTuple):
    line: int
    phrase: str


@dataclass
class Report:
    problems: list[str] = field(default_factory=list)
    allowed: list[str] = field(default_factory=list)
    exempt: list[str] = field(default_factory=list)


def find_claims(text: str, honour_mentions: bool = True) -> list[Claim]:
    """Forbidden phrasings in `text`, skipping marked lines when `honour_mentions`."""
    lines = text.splitlines()
    claims: list[tuple[int, Claim]] = []
    for pattern in FORBIDDEN.values():
        for m in pattern.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            if honour_mentions and MENTION_MARKER in lines[line - 1]:
                continue
            phrase = re.sub(r"[\s>]+", " ", m.group())
            claims.append((m.start(), Claim(line, phrase)))
    return [c for _, c in sorted(claims)]


def has_banner(text: str) -> bool:
    head = [re.sub(r"^[\s>]+", "", ln) for ln in text.splitlines()[:BANNER_LINES]]
    flat = re.sub(r"[*_]", "", " ".join(" ".join(head).split())).lower()
    return all(mark in flat for mark in BANNER_MARKS)


def exemption(path: str, text: str) -> str | None:
    if path == JOURNAL:
        return "historical journal"
    if path.startswith(PRESUBMISSION_REVIEW_DIR) and has_banner(text):
        return "bannered simulated pre-submission review"
    return None


def is_rule_document(path: str) -> bool:
    return path.startswith(RULE_DOCUMENTS)


def _remove_entry(path: str, why: str, ticket: str) -> str:
    return f"{path}: {why} — remove its ALLOWLIST entry ({ticket})"


def check(documents: dict[str, str], allowlist: dict[str, tuple[int, str]]) -> Report:
    report = Report()
    for path in sorted(documents):
        text = documents[path]
        reason = exemption(path, text)
        if reason:
            report.exempt.append(f"{path} ({reason})")
            if path in allowlist:
                _, ticket = allowlist[path]
                report.problems.append(
                    _remove_entry(path, f"exempt now ({reason})", ticket)
                )
            continue

        claims = find_claims(text, honour_mentions=is_rule_document(path))
        located = [f'{path}:{c.line}: "{c.phrase}"' for c in claims]
        if path not in allowlist:
            report.problems.extend(located)
            continue

        pinned, ticket = allowlist[path]
        if len(claims) == pinned:
            report.allowed.append(f"{path} — {pinned} pending, {ticket}")
        elif not claims:
            report.problems.append(_remove_entry(path, "clean", ticket))
        elif len(claims) > pinned:
            report.problems.append(
                f"{path}: {len(claims)} occurrences, allowlist pins {pinned} — a new claim was added:"
            )
            report.problems.extend(located)
        else:
            report.problems.append(
                f"{path}: {len(claims)} occurrences, allowlist pins {pinned} — "
                f"lower the pin to {len(claims)} ({ticket})"
            )

    for path in sorted(set(allowlist) - set(documents)):
        _, ticket = allowlist[path]
        why = "not a scanned document (moved, deleted or out of scope)"
        report.problems.append(_remove_entry(path, why, ticket))
    return report


def is_scanned(path: str) -> bool:
    p = Path(path)
    return p.suffix.lower() in SCANNED_SUFFIXES or p.name in SCANNED_NAMES


def load_documents(root: Path) -> dict[str, str]:
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\0")
    return {
        path: (root / path).read_text(encoding="utf-8", errors="replace")
        for path in listed
        if path and is_scanned(path) and (root / path).is_file()
    }


def run(
    documents: dict[str, str],
    allowlist: dict[str, tuple[int, str]],
    strict: bool = False,
    out: TextIO = sys.stdout,
) -> int:
    report = check(documents, allowlist)
    if strict and allowlist:
        report.problems.append(
            f"strict mode: ALLOWLIST still holds {len(allowlist)} file(s) — "
            "it must be empty before submission"
        )
    print(
        f"documents scanned: {len(documents)}  (exempt: {len(report.exempt)})", file=out
    )
    for entry in report.exempt:
        print(f"  [exempt] {entry}", file=out)
    for entry in report.allowed:
        print(f"  [allowlisted] {entry}", file=out)

    if report.problems:
        print(
            "\n[FAIL] untrue review-status claims (the manuscript has never been "
            "submitted or peer reviewed; see CONTEXT.md):",
            file=out,
        )
        for problem in report.problems:
            print(f"  {problem}", file=out)
        print(
            "\nFix: rewrite the sentence as what actually happened. In a rule document "
            f"({', '.join(RULE_DOCUMENTS)}), a line that names a phrase only to forbid "
            f"or deny it may carry '{MENTION_MARKER}'.",
            file=out,
        )
        return 1

    pending = (
        f"; {len(report.allowed)} allowlisted file(s) pending cleanup — the "
        "allowlist must be empty before submission"
        if report.allowed
        else ""
    )
    print(f"\n[OK] no untrue review-status claim{pending}.", file=out)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when a document claims something untrue about how this work was reviewed."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail while the allowlist is non-empty (the pre-submission gate)",
    )
    args = parser.parse_args(argv)
    return run(load_documents(ROOT), ALLOWLIST, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
