#!/usr/bin/env python3
"""Generate SSc-specific Tier-1 species stubs per module.

For each module spec under docs/module_specs/M*.md, parse the Tier-1
entity table and emit a CellDesigner-importable SBML L2v4 fragment with
a placeholder <species> element for each Tier-1 entity whose Source
column contains "manual" AND that isn't already in
species_annotations.tsv (so we don't generate stubs for entities the
Reactome imports have already provided).

The output files:
  curation/celldesigner/ssc_additions_template/M1_ssc_additions.xml
  curation/celldesigner/ssc_additions_template/M2_ssc_additions.xml
  curation/celldesigner/ssc_additions_template/M3_ssc_additions.xml
  curation/celldesigner/ssc_additions_template/M4_ssc_additions.xml

Each file is a standalone SBML L2v4 model the curator can import or
copy/paste into CellDesigner alongside the integrated map.

A markdown report is also written so the curator can scan what was
emitted per module:
  curation/celldesigner/ssc_additions_template/REPORT.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TABLE_HEADER_RE = re.compile(
    r"^\|\s*Symbol\s*\|\s*Type\s*\|\s*Compartment\s*\|\s*Role\s*\|\s*Source\s*\|",
    re.IGNORECASE,
)
HGNC_RE = re.compile(r"^[A-Z][A-Z0-9\-]+$")


COMPARTMENT_SHORT = {
    "extracellular": "ext",
    "ECM": "ecm",
    "plasma_membrane": "pm",
    "cytosol": "cyto",
    "nucleus": "nuc",
    "ER": "er",
    "endosome": "endo",
    "mitochondrion": "mito",
    "Golgi": "golgi",
}


def parse_table(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    skipped_sep = False
    for line in text.splitlines():
        if not in_table:
            if TABLE_HEADER_RE.search(line):
                in_table = True
            continue
        if not skipped_sep:
            skipped_sep = True
            continue
        if not line.startswith("|"):
            in_table = False
            skipped_sep = False
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        rows.append({
            "symbol_cell": cells[0],
            "type": cells[1],
            "compartment": cells[2],
            "role": cells[3],
            "source": cells[4],
        })
    return rows


def normalise_compartments(value: str) -> list[str]:
    """Return the first ≤2 compartments mentioned, mapped to our vocabulary."""
    parts = re.split(r"\s*[/→,]\s*", value)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if "_" in p:
            tail = p.split("_", 1)[1]
            if tail in COMPARTMENT_SHORT:
                p = tail
        if p in COMPARTMENT_SHORT:
            out.append(p)
        if len(out) >= 2:
            break
    return out or ["cytosol"]


def split_symbols(cell: str) -> list[str]:
    """Split a Symbol cell like 'cGAS (MB21D1), STING1 (TMEM173)' into
    canonical HGNC symbols. Prefer the parenthetical when one is present
    (Reactome / CellDesigner use HGNC primary symbols)."""
    parts = re.split(r"\s*,\s*", cell)
    symbols: list[str] = []
    for p in parts:
        if not p:
            continue
        # Prefer text inside parentheses (often the canonical HGNC)
        m = re.search(r"\(([^)]+)\)", p)
        if m:
            cand = m.group(1).strip()
            if HGNC_RE.match(cand):
                symbols.append(cand)
                continue
        # Otherwise use the text before any parenthesis
        head = re.sub(r"\s*\(.*$", "", p).strip()
        # Normalise α/β / Greek
        head = head.replace("αSMA", "ACTA2").replace("β", "B")
        if HGNC_RE.match(head):
            symbols.append(head)
    # Drop family-collective tokens that the harmoniser already produces
    blocked = {"FAMILY", "ISG"}
    symbols = [s for s in symbols if s not in blocked]
    # Dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for s in symbols:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out


def existing_ids_from_annotations(tsv: Path) -> set[str]:
    if not tsv.exists():
        return set()
    rows = tsv.read_text(encoding="utf-8").splitlines()[1:]
    out: set[str] = set()
    for line in rows:
        cells = line.split("\t")
        if cells:
            out.add(cells[0])
    return out


def existing_hgnc_from_annotations(tsv: Path) -> set[str]:
    """Return the set of HGNC symbols already represented in the annotations."""
    if not tsv.exists():
        return set()
    rows = tsv.read_text(encoding="utf-8").splitlines()[1:]
    out: set[str] = set()
    for line in rows:
        cells = line.split("\t")
        if len(cells) > 1 and cells[1]:
            out.add(cells[1])
    return out


def build_sbml(module: str, compartments: list[str], species: list[dict[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sbml xmlns="http://www.sbml.org/sbml/level2/version4"'
        ' xmlns:html="http://www.w3.org/1999/xhtml" level="2" version="4">',
        f'  <model id="{module}_ssc_additions" name="SSc-specific Tier-1 additions for {module}">',
        '    <listOfCompartments>',
    ]
    for c in compartments:
        lines.append(f'      <compartment id="{c}" name="{c}"/>')
    lines.append('    </listOfCompartments>')
    lines.append('    <listOfSpecies>')
    for sp in species:
        sid = sp["id"]
        name = sp["name"]
        comp = sp["compartment"]
        notes = (
            f'      <notes><html:html><html:head><html:title /></html:head><html:body>'
            f'<html:p>module={module}</html:p><html:p>role={sp.get("role", "")}</html:p>'
            f'<html:p>tier=1</html:p><html:p>source=manual_SSc_specific</html:p>'
            f'</html:body></html:html></notes>'
        )
        lines.append(f'      <species id="{sid}" name="{name}" compartment="{comp}">')
        lines.append(notes)
        lines.append('      </species>')
    lines.append('    </listOfSpecies>')
    lines.append('  </model>')
    lines.append('</sbml>')
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--specs-dir", type=Path, default=Path("docs/module_specs"))
    ap.add_argument(
        "--annotations",
        type=Path,
        default=Path("curation/annotations/species_annotations.tsv"),
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("curation/celldesigner/ssc_additions_template"),
    )
    args = ap.parse_args(argv[1:])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    existing_ids = existing_ids_from_annotations(args.annotations)
    existing_hgnc = existing_hgnc_from_annotations(args.annotations)

    spec_files = sorted(args.specs_dir.glob("M*.md"))
    if not spec_files:
        print(f"no specs under {args.specs_dir}", file=sys.stderr)
        return 2

    report_lines: list[str] = [
        "# SSc additions template — what to wire by hand",
        "",
        "Auto-generated by `scripts/ssc_additions_template.py`. For each "
        "module, the table below lists every Tier-1 SSc-specific species "
        "that is **not yet present** in `curation/annotations/species_annotations.tsv` "
        "and therefore needs to be wired in CellDesigner.",
        "",
    ]

    overall_added = 0
    for spec in spec_files:
        module = spec.stem.split("_", 1)[0]
        rows = parse_table(spec.read_text(encoding="utf-8"))

        species_added: list[dict[str, str]] = []
        compartments_used: set[str] = set()
        for row in rows:
            if "manual" not in row["source"].lower():
                continue
            comps = normalise_compartments(row["compartment"])
            symbols = split_symbols(row["symbol_cell"])
            for sym in symbols:
                comp = comps[0]
                short = COMPARTMENT_SHORT.get(comp, comp[:6].lower())
                sid = f"{sym}__{short}"
                # Skip if already represented (by id or by HGNC symbol)
                if sid in existing_ids or sym in existing_hgnc:
                    continue
                species_added.append({
                    "id": sid,
                    "name": sym,
                    "compartment": comp,
                    "role": row["role"],
                })
                compartments_used.add(comp)

        # Write the per-module XML even if empty (consistent file set)
        out_xml = args.out_dir / f"{module}_ssc_additions.xml"
        out_xml.write_text(
            build_sbml(module, sorted(compartments_used) or ["cytosol"], species_added),
            encoding="utf-8",
        )
        print(f"  {module}: {len(species_added)} new species stub(s) -> {out_xml}")
        overall_added += len(species_added)

        report_lines.append(f"## {module}")
        report_lines.append("")
        report_lines.append(f"File: `{out_xml.name}` — {len(species_added)} species stub(s).")
        report_lines.append("")
        if species_added:
            report_lines.append("| Symbol | Compartment | Role |")
            report_lines.append("|--------|-------------|------|")
            for s in species_added:
                report_lines.append(f"| {s['name']} | {s['compartment']} | {s['role']} |")
        else:
            report_lines.append("_(every Tier-1 manual species is already represented)_")
        report_lines.append("")

    (args.out_dir / "REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n[ok] total stubs emitted: {overall_added}")
    print(f"[ok] report:               {args.out_dir / 'REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
