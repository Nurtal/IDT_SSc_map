#!/usr/bin/env python3
"""Seed curation/annotations/species_annotations.tsv from processed imports.

Walks curation/imports/**/*.processed.xml, extracts each <species> with its
post-processed id, name, and compartment, and writes a row to
species_annotations.tsv. Existing rows (matched on species_id) are preserved
so this is idempotent — re-running adds new species without overwriting any
hand-edited columns.

Module is inferred from the parent directory under curation/imports/ (M1,
M2, M3, M4). Compartment is taken from the <compartment name=> attribute of
the species' parent compartment (resolved through compartments_by_id).

UniProt / Ensembl / ChEBI fields are left blank — they are filled by a
later annotation pass (week 5+ of curation, against UniProt's HGNC mapping).

Output column order is the one fixed in
curation/annotations/species_annotations.tsv:
    species_id, hgnc_symbol, uniprot, ensembl, chebi, compartment, module,
    taxonomy, notes

Usage:
    scripts/seed_species_from_imports.py [--imports-root curation/imports]
                                         [--tsv curation/annotations/species_annotations.tsv]
                                         [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
HGNC_RE = re.compile(r"^[A-Z][A-Z0-9\-]*$")


COLUMNS = [
    "species_id",
    "hgnc_symbol",
    "uniprot",
    "ensembl",
    "chebi",
    "compartment",
    "module",
    "taxonomy",
    "notes",
]


def looks_like_hgnc(name: str) -> bool:
    """Heuristic — true if the name looks like a single HGNC symbol."""
    return bool(HGNC_RE.match(name))


def infer_module(import_path: Path) -> str | None:
    for parent in import_path.parents:
        if parent.name in {"M1", "M2", "M3", "M4"}:
            return parent.name
    return None


def parse_one(path: Path) -> list[dict[str, str]]:
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"s": SBML_NS}
    comps = {c.get("id"): (c.get("name") or c.get("id") or "")
             for c in root.findall(".//s:compartment", ns)}
    module = infer_module(path) or ""
    rows: list[dict[str, str]] = []
    for sp in root.findall(".//s:species", ns):
        name = sp.get("name") or ""
        sp_id = sp.get("id") or ""
        comp_name = comps.get(sp.get("compartment") or "", "")
        rows.append({
            "species_id": sp_id,
            "hgnc_symbol": name if looks_like_hgnc(name) else "",
            "uniprot": "",
            "ensembl": "",
            "chebi": "",
            "compartment": comp_name,
            "module": module,
            "taxonomy": "9606",
            "notes": f"imported from {path.parts[-2]}; raw name: {name}",
        })
    return rows


def read_existing(tsv: Path) -> tuple[list[str], list[dict[str, str]], set[str]]:
    """Return (header, rows, existing_species_ids).

    If the file only has a header and no rows, existing_species_ids is empty.
    """
    text = tsv.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return COLUMNS, [], set()
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    return header, rows, {r.get("species_id", "") for r in rows}


def write_tsv(tsv: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    out: list[str] = ["\t".join(header)]
    for r in rows:
        out.append("\t".join(r.get(c, "") for c in header))
    tsv.write_text("\n".join(out) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--imports-root", type=Path, default=Path("curation/imports"))
    ap.add_argument("--tsv", type=Path, default=Path("curation/annotations/species_annotations.tsv"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv[1:])

    processed_files = sorted(args.imports_root.rglob("*.processed.xml"))
    if not processed_files:
        print(f"no *.processed.xml under {args.imports_root}", file=sys.stderr)
        return 2

    header, existing, existing_ids = read_existing(args.tsv)
    if header != COLUMNS:
        print(
            f"WARN: existing TSV header differs from expected; using expected order "
            f"({COLUMNS}) and re-aligning rows.",
            file=sys.stderr,
        )
        header = COLUMNS

    added = 0
    seen_in_this_run: set[str] = set()
    new_rows: list[dict[str, str]] = []

    for f in processed_files:
        rows = parse_one(f)
        for r in rows:
            sp_id = r["species_id"]
            if not sp_id:
                continue
            if sp_id in existing_ids or sp_id in seen_in_this_run:
                continue
            seen_in_this_run.add(sp_id)
            new_rows.append(r)
            added += 1

    print(f"scanned {len(processed_files)} processed import(s)")
    print(f"existing rows: {len(existing)}")
    print(f"new species:   {added}")

    if args.dry_run:
        for r in new_rows[:5]:
            print(f"  + {r['species_id']}\t{r['hgnc_symbol']}\t{r['compartment']}\t{r['module']}")
        if added > 5:
            print(f"  ... ({added - 5} more)")
        return 0

    out_rows = existing + new_rows
    write_tsv(args.tsv, header, out_rows)
    print(f"wrote {args.tsv}: {len(out_rows)} total rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
