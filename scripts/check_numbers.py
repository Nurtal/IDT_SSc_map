#!/usr/bin/env python3
"""CI guard: every headline number quoted in the documents matches its artefact.

Failure mode this prevents: numbers drifting out of sync with the analysis that
produced them (81.3 vs 82.6 % coverage, 58 vs 62 overlays, 143 vs 145 cards),
each previously caught only by chance in a reading pass.

How it works: each FACT names the committed artefact it is computed from and
the phrasings that quote it. Every match in a SCANNED document is compared
with the artefact value; a mismatch fails the build with the number, the
document and line, and the artefact that contradicts it.

Historical numbers are exempt by explicit rule only (HISTORICAL below): a
dated section of a document that records past states, or one exact phrase.
No fuzzy matching.

Not checked, and said so: figures that no committed artefact carries (see
UNCHECKED); they are listed on every run so the gap stays visible.

Run:
    python3 scripts/check_numbers.py      # exit 1 on any divergence
or  make check-numbers
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

SCANNED = (
    "manuscript/SSc_MIM_manuscript_draft.md",
    "README.md",
    "STATUS.md",
    "docs/presentation.md",
)

# Explicit exemptions for numbers quoted deliberately as history.
#   ("section", doc, heading)  every line under that markdown heading (to the next heading of
#                              the same or higher level) is a dated record;
#   ("phrase", doc, text)      that exact text, wherever it occurs in the document.
HISTORICAL = (
    ("section", "STATUS.md", "## What's done (with commit refs)"),
    ("phrase", "STATUS.md", "(grew from 526/260 via the\n  literature-mining growth batches)"),
    ("phrase", "STATUS.md", "(was 81.3/49.5% on 198 symbols)"),
    ("phrase", "STATUS.md", "SSc reactions 85 → 133"),
)

UNCHECKED = (
    "total single-cell counts (266 884 cells; per-dataset cell counts): no committed artefact carries them",
    "p-values quoted in prose: checked by the analyses' own round-trip tests, not here",
)


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def _xml_counts() -> dict[str, int]:
    root = ET.parse(ROOT / "curation/celldesigner/SSc_MIM_integrated.xml").getroot()
    count = lambda tag: sum(1 for e in root.iter() if e.tag.endswith("}" + tag))  # noqa: E731
    return {"species": count("species"), "reactions": count("reaction"), "compartments": count("compartment")}


def _tsv_rows(path: str) -> int:
    with (ROOT / path).open() as fh:
        return sum(1 for _ in csv.DictReader(fh, delimiter="\t"))


def _csv_rows(path: str) -> int:
    with (ROOT / path).open() as fh:
        return sum(1 for _ in csv.DictReader(fh))


def _verdicts() -> dict[str, int]:
    out: dict[str, int] = {}
    for v in _json("curation/ai_review_verdicts.json").values():
        out[v["verdict"]] = out.get(v["verdict"], 0) + 1
    return out


@dataclass
class Fact:
    name: str
    artefact: str
    value: Callable[[], tuple]
    pattern: re.Pattern
    groups: Callable[[re.Match], tuple]


COVERAGE_FRACTIONS = "coverage fractions over the detectable denominator"


def _ints(*idx):
    return lambda m: tuple(int(m.group(i).replace(",", "").replace(" ", "")) for i in idx)


FACTS = [
    Fact("integrated map species / reactions", "curation/celldesigner/SSc_MIM_integrated.xml",
         lambda: (_xml_counts()["species"], _xml_counts()["reactions"]),
         re.compile(r"\b(\d{3}) (?:molecular )?species(?:\*\*)?(?: and| /| ·|,| across) (?:\*\*)?(\d{3}) reactions?"),
         _ints(1, 2)),
    Fact("integrated map compartments", "curation/celldesigner/SSc_MIM_integrated.xml",
         lambda: (_xml_counts()["compartments"],),
         re.compile(r"\b(\d+) compartments\b"), _ints(1)),
    Fact("SSc-curated reactions", "curation/ssc_curated_reactions.tsv",
         lambda: (_tsv_rows("curation/ssc_curated_reactions.tsv"),),
         re.compile(r"\b(\d+) (?:hand-curated|SSc-curated|SSc-specific curated) reactions\b"
                    r"|\bssc_curated_reactions\.tsv`? \| \*\*(\d+) reactions\*\*"),
         lambda m: (int(m.group(1) or m.group(2)),)),
    Fact("interactions offered for adjudication", "analysis/curation/interaction_database.csv",
         lambda: (_csv_rows("analysis/curation/interaction_database.csv"),),
         re.compile(r"\b(\d+) interactions\b|Interactions offered for adjudication[^|\n]*\| \*\*(\d+)\*\*"),
         lambda m: (int(m.group(1) or m.group(2)),)),
    Fact("AI verdicts validate / caution", "curation/ai_review_verdicts.json",
         lambda: (_verdicts().get("validate", 0), _verdicts().get("caution", 0)),
         re.compile(r"\b(\d+) validate / (\d+) caution\b"), _ints(1, 2)),
    Fact("MINERVA overlays", "analysis/overlay/build_overlay_multi.report.json",
         lambda: (_json("analysis/overlay/build_overlay_multi.report.json")["n_minerva_overlays"],),
         re.compile(r"\b(\d+) (?:MINERVA |cluster )?overlays\b"), _ints(1)),
    Fact("single-cell donors (total)", "analysis/overlay/module_score_contrasts_v1.1.json",
         lambda: (_json("analysis/overlay/module_score_contrasts_v1.1.json")["n_donors_total"],),
         re.compile(r"\b(\d+) donors \((?:\d+) SSc / (?:\d+) HC\)|cells (?:from|/|and) (\d+) donors\b"),
         lambda m: (int(m.group(1) or m.group(2)),)),
    Fact("permissive coverage (pct)", "analysis/overlay/coverage_v1.1.json",
         lambda: (_json("analysis/overlay/coverage_v1.1.json")["overall"]["pct"],),
         re.compile(r"(?:MIM )?coverage (\d+\.\d) ?%"), lambda m: (float(m.group(1)),)),
    Fact(COVERAGE_FRACTIONS, "analysis/overlay/coverage_v1.1.json + coverage_sensitivity.json",
         lambda: None,  # checked as a set membership below
         re.compile(r"\b(\d+)/(\d+) \((\d+\.\d) ?%\)"), lambda m: (int(m.group(1)), int(m.group(2)), float(m.group(3)))),
    Fact("network communities", "analysis/network/summary.json",
         lambda: (_json("analysis/network/summary.json")["communities"]["count"],),
         re.compile(r"(?<!in )\b(\d+) (?:functional )?communities\b"), _ints(1)),
    Fact("significant community-module enrichments", "analysis/network/summary.json",
         lambda: (_json("analysis/network/summary.json")["community_enrichment"]["n_significant_at_q05"],
                  _json("analysis/network/summary.json")["community_enrichment"]["n_communities_significant"]),
         re.compile(r"\b(\d+) significant (?:\(community, module\) )?enrichments at q < 0\.05,? in (\d+) communities"),
         _ints(1, 2)),
]


def coverage_pairs() -> set[tuple[int, int, float]]:
    cov = _json("analysis/overlay/coverage_v1.1.json")["overall"]
    pairs = {(cov["hit"], cov["denom"], cov["pct"])}
    with (ROOT / "analysis/overlay/coverage_sensitivity.tsv").open() as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            hit, denom = int(r["hit"]), int(r["denom"])
            pairs.add((hit, denom, round(100 * hit / denom, 1)))
    return pairs


def exempt_spans(doc: str, text: str) -> list[tuple[int, int]]:
    spans = []
    for kind, d, what in HISTORICAL:
        if d != doc:
            continue
        if kind == "phrase":
            start = text.find(what)
            if start < 0:
                raise SystemExit(f"[FAIL] HISTORICAL phrase no longer in {doc}: {what!r} — remove the rule")
            spans.append((start, start + len(what)))
        else:
            start = text.find(what + "\n")
            if start < 0:
                raise SystemExit(f"[FAIL] HISTORICAL section no longer in {doc}: {what!r} — remove the rule")
            level = len(what) - len(what.lstrip("#"))
            nxt = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, start + len(what))
            spans.append((start, nxt.start() if nxt else len(text)))
    return spans


def check(documents: dict[str, str]) -> list[str]:
    problems = []
    pairs = coverage_pairs()
    values = {f.name: f.value() for f in FACTS}
    for doc, text in documents.items():
        spans = exempt_spans(doc, text)
        for f in FACTS:
            for m in f.pattern.finditer(text):
                if any(a <= m.start() < b for a, b in spans):
                    continue
                got = f.groups(m)
                line = text.count("\n", 0, m.start()) + 1
                if f.name == COVERAGE_FRACTIONS:   # must be one of the artefact's (hit, denom, pct)
                    if got[1] in {d for _, d, _ in pairs} and got not in pairs:
                        problems.append(f"{doc}:{line}: {f.name} — quotes {got[0]}/{got[1]} ({got[2]} %), "
                                        f"not a fraction in {f.artefact}")
                    continue
                if got != values[f.name]:
                    problems.append(f"{doc}:{line}: {f.name} — quotes {got}, {f.artefact} says {values[f.name]}")
    return problems


def main() -> int:
    docs = {d: (ROOT / d).read_text() for d in SCANNED}
    problems = check(docs)
    for u in UNCHECKED:
        print(f"  [unchecked] {u}")
    if problems:
        print("\n[FAIL] headline numbers diverge from their artefacts:")
        for p in problems:
            print(f"  {p}")
        print("\nFix: update the document from the artefact (never the reverse), or, if the number is "
              "deliberately historical, add an explicit HISTORICAL rule.")
        return 1
    print(f"[OK] {len(FACTS)} headline facts consistent across {len(docs)} documents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
