#!/usr/bin/env python3
"""Validate every SBML / CellDesigner XML file under a directory.

Exit code:
  0  all files parse and contain no level-2-or-above libSBML errors
  1  one or more files failed parsing or raised serious errors

Notes:
- Allows empty placeholder files (0 bytes) and CellDesigner-only annotations.
- Only fatal / error severities block the build; warnings are reported but
  do not fail CI.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import libsbml  # type: ignore
except ImportError:
    print(
        "python-libsbml is required. Install with: pip install python-libsbml",
        file=sys.stderr,
    )
    sys.exit(2)


SEVERITY_NAMES = {
    libsbml.LIBSBML_SEV_INFO: "INFO",
    libsbml.LIBSBML_SEV_WARNING: "WARNING",
    libsbml.LIBSBML_SEV_ERROR: "ERROR",
    libsbml.LIBSBML_SEV_FATAL: "FATAL",
}


def validate_one(path: Path) -> bool:
    """Return True if the file passes validation, False otherwise."""
    if path.stat().st_size == 0:
        print(f"[skip] {path} — empty placeholder")
        return True

    reader = libsbml.SBMLReader()
    doc = reader.readSBMLFromFile(str(path))

    n = doc.getNumErrors()
    ok = True
    for i in range(n):
        err = doc.getError(i)
        sev = err.getSeverity()
        name = SEVERITY_NAMES.get(sev, "?")
        line = err.getLine()
        msg = err.getMessage().strip().replace("\n", " ")
        print(f"[{name}] {path}:{line}: {msg}")
        if sev in (libsbml.LIBSBML_SEV_ERROR, libsbml.LIBSBML_SEV_FATAL):
            ok = False

    if ok and n == 0:
        print(f"[ok]   {path}")
    elif ok:
        print(f"[ok]   {path} (warnings only)")
    return ok


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <directory>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.exists():
        print(f"directory not found: {root}", file=sys.stderr)
        return 2

    files = sorted(root.rglob("*.xml"))
    if not files:
        print(f"[info] no XML files under {root} yet — nothing to validate.")
        return 0

    all_ok = True
    for f in files:
        if not validate_one(f):
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
