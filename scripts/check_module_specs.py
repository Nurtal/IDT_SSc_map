#!/usr/bin/env python3
"""Lint docs/module_specs/M*.md for cross-module consistency.

Checks:
  1. Every entity in a module's Tier-1 entity table does NOT also appear in
     another module's Tier-1 entity table (cross-module duplicates would
     duplicate species on integration). Entities that legitimately span
     modules belong in the crosstalk section, not in two Tier-1 tables.
  2. Compartment values come from the fixed vocabulary defined in
     docs/curation_guidelines.md § Compartments.
  3. The "Source" column values are drawn from a small whitelist.

Exit code:
  0  no issues
  1  at least one issue found
  2  no spec files found, or argument error
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


COMPARTMENT_VOCAB = {
    "extracellular",
    "ECM",
    "plasma_membrane",
    "cytosol",
    "nucleus",
    "ER",
    "endosome",
    "mitochondrion",
}

SOURCE_VOCAB = {
    "Reactome",
    "RA-map",
    "WikiPathways",
    "SYSCID",
    "manual",
}

TABLE_HEADER_RE = re.compile(
    r"^\|\s*Symbol\s*\|\s*Type\s*\|\s*Compartment\s*\|\s*Role\s*\|\s*Source\s*\|",
    re.IGNORECASE,
)
ENTITY_RE = re.compile(r"[A-Z][A-Z0-9\-]+(?:/[A-Z0-9\-]+)*")


def parse_tier1_table(path: Path) -> list[dict[str, str]]:
    """Return the list of rows of the *first* Tier-1 entity table in a spec file."""
    rows: list[dict[str, str]] = []
    in_table = False
    skipped_separator = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not in_table:
            if TABLE_HEADER_RE.search(line):
                in_table = True
            continue
        if not skipped_separator:
            skipped_separator = True
            continue
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            break
        rows.append(
            dict(zip(("symbol", "type", "compartment", "role", "source"), cells[:5]))
        )
    return rows


def normalise_compartments(value: str) -> list[str]:
    """Split a compartment cell like 'cytosol / nucleus' or 'cytosol → nucleus'."""
    parts = re.split(r"\s*[/→,]\s*", value)
    out = []
    for p in parts:
        # strip a cell-type prefix like "EC_cytosol"
        if "_" in p:
            tail = p.split("_", 1)[1]
            if tail in COMPARTMENT_VOCAB:
                out.append(tail)
                continue
        out.append(p.strip())
    return [x for x in out if x]


def normalise_sources(value: str) -> list[str]:
    """A source cell can list multiple values joined by '+'."""
    return [p.strip() for p in re.split(r"\s*\+\s*", value) if p.strip()]


def extract_entities(symbol_cell: str) -> list[str]:
    """Extract individual entity tokens from a Symbol cell.

    Strip parenthetical aliases (e.g. 'CDH2 (N-cadherin)' → 'CDH2') so we
    don't match fragments inside the parenthetical name. Tokens with fewer
    than 3 characters are also dropped (avoids matching prepositions or
    one-letter alias fragments).
    """
    cleaned = re.sub(r"\([^)]*\)", "", symbol_cell)
    return [t for t in ENTITY_RE.findall(cleaned) if len(t) >= 3]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <docs/module_specs/>", file=sys.stderr)
        return 2

    root = Path(argv[1])
    spec_files = sorted(root.glob("M*.md"))
    if not spec_files:
        print(f"no module specs found under {root}", file=sys.stderr)
        return 2

    entity_modules: dict[str, set[str]] = defaultdict(set)
    issues: list[str] = []

    for spec in spec_files:
        module_id = spec.stem.split("_", 1)[0]
        rows = parse_tier1_table(spec)
        if not rows:
            issues.append(f"{spec}: no Tier-1 entity table found")
            continue

        for row in rows:
            # compartment vocabulary
            for c in normalise_compartments(row["compartment"]):
                if c not in COMPARTMENT_VOCAB:
                    issues.append(
                        f"{spec}: unknown compartment '{c}' for symbol '{row['symbol']}'"
                    )
            # source vocabulary
            for s in normalise_sources(row["source"]):
                # allow free trailing notes after '(' in source cells
                base = s.split("(", 1)[0].strip()
                if base and base not in SOURCE_VOCAB:
                    issues.append(
                        f"{spec}: unknown source '{base}' for symbol '{row['symbol']}'"
                    )
            # collect entities for cross-module duplicate check
            for ent in extract_entities(row["symbol"]):
                entity_modules[ent].add(module_id)

    # cross-module duplicates (entities in two or more Tier-1 tables)
    duplicates = {ent: mods for ent, mods in entity_modules.items() if len(mods) > 1}
    for ent, mods in sorted(duplicates.items()):
        issues.append(
            f"cross-module Tier-1 duplicate: '{ent}' appears in {sorted(mods)} "
            f"— move to a crosstalk section or the integrated map"
        )

    if issues:
        print(f"FOUND {len(issues)} ISSUE(S):")
        for line in issues:
            print(f"  - {line}")
        return 1

    print(f"OK — {len(spec_files)} spec(s) scanned, no consistency issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
