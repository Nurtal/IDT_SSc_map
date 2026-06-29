#!/usr/bin/env python3
"""CI guard: every external dataset a script consumes must be in the mirror.

Failure mode this prevents (observed 2026-06-29): the GSE45536 whole-blood
cohort carried the headline M5 external-validation p-values, yet it was
absent from `data/MIRROR.sha256` and from disk — so the result was not
reproducible and nobody noticed. This guard makes that class of omission a
hard CI failure.

Rule: every GEO accession (`GSE\\d+` / `GPL\\d+`) referenced in a Python
script under scripts/ must be listed in `data/MIRROR.sha256`, unless it is
explicitly declared in ALLOWLIST below (with a reason). Adding a dataset to
the analysis without manifesting it (or consciously allow-listing it) fails
the build.

Truncated FTP path fragments (e.g. `GSE138` inside the URL `GSE138nnn`) are
ignored automatically: any accession that is a strict prefix of a longer
referenced accession is dropped.

Run:
    python3 scripts/check_data_manifest.py     # exit 1 on any unmanifested accession
or  make check-manifest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
MANIFEST = ROOT / "data/MIRROR.sha256"

# No trailing boundary: accessions are routinely followed by '_' (a word
# char), e.g. "GSE138669_RAW.tar" — a trailing \b would miss those.
ACCESSION_RE = re.compile(r"(?<![A-Za-z0-9])(GSE\d+|GPL\d+)")

# Accessions that are referenced by scripts but deliberately NOT mirrored.
# Each entry MUST carry a reason; this is the audit trail for every
# conscious exclusion.
ALLOWLIST: dict[str, str] = {
    # Per-platform clinical series matrices of Gur 2022; the parent GSE195452
    # raw data is mirrored, and these sub-platform matrices are only an
    # auxiliary donor-phenotype cache (scripts/fetch_clinical_metadata.py),
    # not an input to any published number.
    "GPL18573": "Gur sub-platform; auxiliary clinical metadata only (parent GSE195452 mirrored)",
    "GPL24676": "Gur sub-platform; auxiliary clinical metadata only (parent GSE195452 mirrored)",
}


def referenced_accessions() -> set[str]:
    found: set[str] = set()
    for py in sorted(SCRIPTS_DIR.glob("*.py")):
        if py.name == Path(__file__).name:
            continue  # don't count the guard's own docstring examples
        text = py.read_text(errors="replace")
        found |= set(ACCESSION_RE.findall(text))
    # Drop truncated FTP fragments: an accession that is a strict prefix of a
    # longer referenced one (GSE138 vs GSE138669).
    pruned = {
        a for a in found
        if not any(b != a and b.startswith(a) for b in found)
    }
    return pruned


def manifested_accessions() -> set[str]:
    if not MANIFEST.exists():
        return set()
    return set(ACCESSION_RE.findall(MANIFEST.read_text(errors="replace")))


def main() -> int:
    refs = referenced_accessions()
    manifested = manifested_accessions()

    missing = sorted(a for a in refs if a not in manifested and a not in ALLOWLIST)
    allowed = sorted(a for a in refs if a not in manifested and a in ALLOWLIST)

    print(f"accessions referenced by scripts/: {len(refs)}  "
          f"({', '.join(sorted(refs)) or 'none'})")
    print(f"accessions in data/MIRROR.sha256:  {len(manifested)}  "
          f"({', '.join(sorted(manifested)) or 'none'})")
    for a in allowed:
        print(f"  [allowlisted] {a} — {ALLOWLIST[a]}")

    if missing:
        print("\n[FAIL] datasets used by scripts but NOT in data/MIRROR.sha256:")
        for a in missing:
            print(f"  - {a}")
        print("\nFix: download the file(s), pin size + SHA-256 in data/MIRROR.sha256")
        print("and data/MIRROR.md, or add the accession to ALLOWLIST with a reason.")
        return 1

    print("\n[OK] every referenced dataset is manifested (or consciously allow-listed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
