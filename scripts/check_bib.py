#!/usr/bin/env python3
"""Lint curation/pubmed_corpus.bib for incomplete entries.

Reports:
  - entries with pmid = {TODO} (or pmid missing entirely AND no doi)
  - entries with neither pmid nor doi
  - duplicate citation keys

Exit code:
  0  no issues, or --warn-only requested
  1  issues found in strict mode (--strict)
  2  argument error or file not found

The default mode is INFO: prints issues and returns 0. Use --strict in CI
once the corpus is expected to be clean (Phase 2 onwards).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


ENTRY_START_RE = re.compile(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?\s*$", re.MULTILINE)


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    # split on @ at start of line; first chunk is the file preamble
    chunks = re.split(r"^@", text, flags=re.MULTILINE)[1:]
    for chunk in chunks:
        chunk = "@" + chunk
        head = ENTRY_START_RE.search(chunk)
        if not head:
            continue
        entry: dict[str, str] = {
            "type": head.group(1).lower(),
            "key": head.group(2),
        }
        for m in FIELD_RE.finditer(chunk):
            entry[m.group(1).lower()] = m.group(2).strip()
        entries.append(entry)
    return entries


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bibfile", type=Path)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="return non-zero on any issue (use in CI from Phase 2 onwards)",
    )
    args = ap.parse_args(argv[1:])

    if not args.bibfile.exists():
        print(f"file not found: {args.bibfile}", file=sys.stderr)
        return 2

    text = args.bibfile.read_text(encoding="utf-8")
    entries = parse_entries(text)
    if not entries:
        print(f"no BibTeX entries parsed from {args.bibfile}", file=sys.stderr)
        return 2

    issues: list[str] = []

    for entry in entries:
        key = entry["key"]
        pmid = entry.get("pmid", "")
        doi = entry.get("doi", "")
        if pmid.upper() == "TODO":
            issues.append(f"{key}: pmid = TODO (needs real PMID)")
        elif not pmid and not doi:
            issues.append(f"{key}: no pmid and no doi")

    keys = Counter(e["key"] for e in entries)
    for key, count in keys.items():
        if count > 1:
            issues.append(f"{key}: duplicate citation key ({count} occurrences)")

    if issues:
        print(f"FOUND {len(issues)} ISSUE(S) in {args.bibfile}:")
        for line in issues:
            print(f"  - {line}")
        print(f"\n({len(entries)} entries scanned)")
        return 1 if args.strict else 0

    print(f"OK — {len(entries)} entries, no issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
