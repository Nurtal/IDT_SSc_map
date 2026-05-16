#!/usr/bin/env python3
"""Mine PMIDs from the Reactome SBML L3 exports under curation/imports/.

The files we currently have under `*.owl` are Reactome's SBML L3v1 fallback
(the BioPAX endpoint 404'd at fetch time; SBML carries the same biology).
PMIDs are stored as `<rdf:li rdf:resource="https://identifiers.org/pubmed:NNNN" />`
inside `<bqbiol:isDescribedBy>` blocks attached to species and reactions.

Outputs:
  1. Append BibTeX entries for new PMIDs to curation/pubmed_corpus.bib.
     New entries are stubs (pmid + a TODO body); a later
     `scripts/bib_lookup.py` will fill in title/journal/year/etc.
  2. Pre-fill curation/annotations/reaction_evidence.tsv with one row per
     Reactome reaction, columns matching the header. Idempotent: existing
     rows (matched by reaction_id) are preserved.

Module inference: each `*.owl` lives under curation/imports/M[1-4]/.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_L3 = "http://www.sbml.org/sbml/level3/version1/core"
PMID_RE = re.compile(r"identifiers\.org/pubmed[/:]([0-9]+)", re.IGNORECASE)
MODULE_RE = re.compile(r"/imports/(M[1-4])/")


REACTION_COLUMNS = [
    "reaction_id",
    "type",
    "participants",
    "mechanism",
    "pmid",
    "evidence_code",
    "context_biotype",
    "context_assay",
    "module",
    "crosstalk_modules",
    "notes",
]


def q(tag: str, ns: str = SBML_L3) -> str:
    return f"{{{ns}}}{tag}"


def infer_module(path: Path) -> str:
    m = MODULE_RE.search(str(path))
    return m.group(1) if m else "?"


def extract_pmids_from_block(elem: ET.Element) -> list[str]:
    """Return the unique pubmed IDs referenced anywhere under `elem`."""
    out: list[str] = []
    seen: set[str] = set()
    # cheapest: serialise and regex
    raw = ET.tostring(elem, encoding="unicode")
    for m in PMID_RE.findall(raw):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def reaction_summary(rxn: ET.Element) -> tuple[str, str, list[str]]:
    """Return (id, name, participants) for a Reactome SBML L3 reaction."""
    rid = rxn.get("id", "")
    name = rxn.get("name", "")
    parts: list[str] = []
    lor = rxn.find(q("listOfReactants"))
    if lor is not None:
        for sr in lor.findall(q("speciesReference")):
            parts.append(sr.get("species", ""))
    lop = rxn.find(q("listOfProducts"))
    if lop is not None:
        for sr in lop.findall(q("speciesReference")):
            parts.append(sr.get("species", ""))
    return rid, name, parts


def read_existing_tsv(path: Path) -> tuple[list[str], list[dict[str, str]], set[str]]:
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return REACTION_COLUMNS, [], set()
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    return header, rows, {r.get("reaction_id", "") for r in rows}


def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    out = ["\t".join(header)]
    for r in rows:
        out.append("\t".join(r.get(c, "") for c in header))
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def append_bib_entries(bib: Path, pmids: list[str]) -> int:
    text = bib.read_text(encoding="utf-8") if bib.exists() else ""
    existing = set(re.findall(r"pmid\s*=\s*\{(\d+)\}", text))
    new_pmids = [p for p in pmids if p not in existing]
    if not new_pmids:
        return 0
    chunks = ["\n% --- auto-appended from Reactome SBML PMID mining ---\n"]
    for pmid in sorted(set(new_pmids), key=int):
        chunks.append(
            f"@article{{Reactome_pmid_{pmid},\n"
            f"  pmid    = {{{pmid}}},\n"
            f"  title   = {{TODO}},\n"
            f"  journal = {{TODO}},\n"
            f"  year    = {{TODO}},\n"
            f"  note    = {{auto-extracted; needs metadata fill via scripts/bib_lookup.py}}\n"
            f"}}\n"
        )
    bib.write_text(text + "\n".join(chunks), encoding="utf-8")
    return len(set(new_pmids))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--imports-root", type=Path, default=Path("curation/imports"))
    ap.add_argument("--bib", type=Path, default=Path("curation/pubmed_corpus.bib"))
    ap.add_argument(
        "--tsv",
        type=Path,
        default=Path("curation/annotations/reaction_evidence.tsv"),
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv[1:])

    owl_files = sorted(args.imports_root.rglob("*.owl"))
    if not owl_files:
        print(f"no *.owl under {args.imports_root}", file=sys.stderr)
        return 2

    all_pmids: set[str] = set()
    new_rows: list[dict[str, str]] = []
    per_file_stats: dict[str, dict[str, int]] = defaultdict(lambda: {
        "reactions": 0,
        "reactions_with_pmid": 0,
        "pmids_unique": 0,
    })

    header, existing, existing_ids = read_existing_tsv(args.tsv)
    if header != REACTION_COLUMNS:
        header = REACTION_COLUMNS

    for f in owl_files:
        module = infer_module(f)
        try:
            tree = ET.parse(f)
        except ET.ParseError as exc:
            print(f"[warn] cannot parse {f}: {exc}", file=sys.stderr)
            continue
        root = tree.getroot()

        # Iterate over reactions
        file_pmids: set[str] = set()
        rxn_count = 0
        rxn_with_pmid = 0
        for rxn in root.findall(f".//{q('reaction')}"):
            rid, name, parts = reaction_summary(rxn)
            rxn_count += 1
            pmids = extract_pmids_from_block(rxn)
            if pmids:
                rxn_with_pmid += 1
            file_pmids.update(pmids)
            all_pmids.update(pmids)

            # Pre-fill reaction_evidence.tsv row
            row_id = f"{module}_{rid}"
            if row_id in existing_ids:
                continue
            new_rows.append({
                "reaction_id": row_id,
                "type": "TODO",
                "participants": ";".join(parts),
                "mechanism": name,
                "pmid": ";".join(pmids),
                "evidence_code": "ECO:0000305" if pmids else "TODO",
                "context_biotype": "",
                "context_assay": "",
                "module": module,
                "crosstalk_modules": "",
                "notes": f"auto-imported from {f.name}",
            })

        per_file_stats[str(f)] = {
            "reactions": rxn_count,
            "reactions_with_pmid": rxn_with_pmid,
            "pmids_unique": len(file_pmids),
        }

    print(f"--- per-file stats ---")
    for k, v in per_file_stats.items():
        print(f"  {k}")
        print(f"    reactions={v['reactions']} with_pmid={v['reactions_with_pmid']} unique_pmids={v['pmids_unique']}")
    print()
    print(f"--- totals ---")
    print(f"  unique PMIDs across all imports: {len(all_pmids)}")
    print(f"  new reaction_evidence rows:      {len(new_rows)}")

    if args.dry_run:
        return 0

    # Append new PMIDs to bib
    appended = append_bib_entries(args.bib, sorted(all_pmids, key=int))
    print(f"  appended {appended} new BibTeX stub entries to {args.bib}")

    # Write reaction_evidence.tsv
    write_tsv(args.tsv, header, existing + new_rows)
    print(f"  wrote {args.tsv}: {len(existing) + len(new_rows)} total rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
