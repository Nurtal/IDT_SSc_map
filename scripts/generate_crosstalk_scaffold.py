#!/usr/bin/env python3
"""Generate the crosstalk matrix scaffold from module specs.

Parses the "Crosstalk edges" / "Crosstalk edges in/out of MX" sections of
each docs/module_specs/M*.md and emits docs/crosstalk_matrix.md — a single
table with one row per declared crosstalk edge.

Each crosstalk bullet in a spec follows a loose convention:
    - **In:** <module> — <mechanism>
    - **Out:** <module> — <mechanism>
    - <module> ↔ <module>: <mechanism>
    - <module> → <module>: <mechanism>

We extract source/target modules and a free-text mechanism. Module of the
file itself (M1..M4) is inferred from the filename.

This script is **lossy on purpose**: the goal is a starter `crosstalk_matrix.md`
that the curator refines. The script is idempotent — re-running rewrites
the matrix from the latest spec contents.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path


SPEC_NAME_RE = re.compile(r"^(M[1-4])_.*\.md$")

CROSSTALK_SECTION_HEADER_RE = re.compile(
    r"^##\s+\d+\.\s+Crosstalk\s+edges?\b.*$", re.IGNORECASE | re.MULTILINE
)
NEXT_SECTION_HEADER_RE = re.compile(r"^##\s+\d+\.\s+", re.MULTILINE)

# 1. "- **In:** M1 — text" or "- **In:** M1 → text" or "- **Out:** M2: text"
DIRECTED_RE = re.compile(
    r"-\s+\*\*(?P<direction>In|Out)[:*]+\*\*\s+(?P<other>M[1-4])\b[^:—–\-→]*\s*[:—–\-→]?\s*(?P<text>.+)",
    re.IGNORECASE,
)
# 2. "- → M2 ...: text"  (implicit self module; bullet starts with arrow + target)
IMPLICIT_OUT_RE = re.compile(
    r"-\s+(?:→|->)\s+(?P<other>M[1-4])\b[^:]*:\s*(?P<text>.+)"
)
# 3. "Mx → My: text" or "Mx ↔ My — text"
ARROW_RE = re.compile(
    r"(?P<src>M[1-4])\s*(?P<arrow>→|->|↔|<->|<-)\s*(?P<dst>M[1-4])\s*[:—–\-]\s*(?P<text>.+)"
)


def infer_self_module(path: Path) -> str:
    m = SPEC_NAME_RE.match(path.name)
    return m.group(1) if m else "?"


def find_crosstalk_block(text: str) -> str:
    m = CROSSTALK_SECTION_HEADER_RE.search(text)
    if not m:
        return ""
    start = m.end()
    rest = text[start:]
    end = NEXT_SECTION_HEADER_RE.search(rest)
    return rest[: end.start()] if end else rest


def normalise_text(t: str) -> str:
    return " ".join(t.strip().split())


def parse_edges_from_spec(path: Path) -> list[tuple[str, str, str]]:
    self_m = infer_self_module(path)
    text = path.read_text(encoding="utf-8")
    block = find_crosstalk_block(text)
    edges: list[tuple[str, str, str]] = []
    for line in block.splitlines():
        m = DIRECTED_RE.search(line)
        if m:
            direction = m.group("direction").lower()
            other = m.group("other")
            mech = normalise_text(m.group("text"))
            if direction == "in":
                edges.append((other, self_m, mech))
            else:
                edges.append((self_m, other, mech))
            continue
        m = IMPLICIT_OUT_RE.search(line)
        if m:
            other = m.group("other")
            mech = normalise_text(m.group("text"))
            edges.append((self_m, other, mech))
            continue
        m = ARROW_RE.search(line)
        if m:
            src = m.group("src")
            dst = m.group("dst")
            mech = normalise_text(m.group("text"))
            arrow = "↔" in line or "<->" in line
            edges.append((src, dst, mech))
            if arrow:
                edges.append((dst, src, mech))
    return edges


def dedupe_preserve_order(items: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[tuple[str, str, str]] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
    return out


MD_HEADER = """# Crosstalk matrix — SSc-MIM

> Auto-generated from `docs/module_specs/M*.md` "Crosstalk edges" sections by
> `scripts/generate_crosstalk_scaffold.py`. Hand-edit only the **status** and
> **notes** columns — anything else will be overwritten on re-run.

## Conventions

- Source / target are the four sub-modules: M1 (IFN-I), M2 (TGF-β / fibrosis),
  M3 (EndoMT / vasculopathy), M4 (IL-6 / Th2 / B-cell).
- *Mechanism* is the spec's prose verbatim.
- *Status*: `declared` (in a spec, not yet built) → `scaffolded` (placeholder
  exists in CellDesigner) → `curated` (full SBGN reaction + MI2CAST).
- Use the GitHub issue `curation_request` template to track work on any row.

## Edges

"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--specs-dir",
        type=Path,
        default=Path("docs/module_specs"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/crosstalk_matrix.md"),
    )
    args = ap.parse_args(argv[1:])

    spec_files = sorted(args.specs_dir.glob("M*.md"))
    if not spec_files:
        print(f"no specs under {args.specs_dir}", file=sys.stderr)
        return 2

    all_edges: list[tuple[str, str, str]] = []
    for f in spec_files:
        edges = parse_edges_from_spec(f)
        print(f"  {f.name}: {len(edges)} edge(s) parsed")
        all_edges.extend(edges)

    deduped = dedupe_preserve_order(all_edges)
    print(f"total unique edges: {len(deduped)}")

    lines: list[str] = [MD_HEADER]
    lines.append("| # | source | target | mechanism | status | notes |")
    lines.append("|---|--------|--------|-----------|--------|-------|")
    for i, (src, dst, mech) in enumerate(deduped, 1):
        lines.append(f"| {i} | {src} | {dst} | {mech} | declared |  |")
    lines.append("")
    lines.append(f"_{len(deduped)} edge(s) auto-extracted from {len(spec_files)} module spec(s)._")
    lines.append("")

    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
