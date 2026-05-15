#!/usr/bin/env python3
"""Post-process a Reactome-derived CellDesigner SBML.

Implements the three transforms decided in
docs/decisions/2026-05-15_reactome_import.md:

  1. Rename species IDs from MINERVA UUIDs (``s_id_entityVertex_*``) to a
     deterministic, human-readable form derived from the existing ``name``
     attribute. Format: ``<sanitised_name>__<compartment_short>``.
  2. Collapse cofactor duplicates within the same compartment to a single
     species. Affects ATP, ADP, AMP, GTP, GDP, GMP, H2O, Pi, PPi, CO2,
     O2, H+, NAD+, NADH, NADP+, NADPH, FAD, FADH2.
  3. Remove free ubiquitin species ("Ub", "ubiquitin") — per
     curation_guidelines.md sec.5 ubiquitination is encoded as a state
     variable on the substrate.

Outputs:
  - <input>.processed.xml — the rewritten CellDesigner SBML.
  - <input>.report.json   — JSON report of every rename, collapse, removal.

Stdlib only (xml.etree.ElementTree + json).

Usage:
  scripts/post_process_reactome.py <input.celldesigner.xml> [--out path]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

NS = {"s": SBML_NS, "cd": CD_NS, "rdf": RDF_NS}


# Keep default prefix as the SBML namespace (no prefix), and short prefixes
# for the rest. Registering before parsing/serialising preserves them.
ET.register_namespace("", SBML_NS)
ET.register_namespace("celldesigner", CD_NS)
ET.register_namespace("rdf", RDF_NS)


COFACTORS = {
    "ATP", "ADP", "AMP",
    "GTP", "GDP", "GMP",
    "CTP", "CDP", "UTP", "UDP",
    "H2O", "Pi", "PPi",
    "CO2", "O2",
    "H+", "H(+)",
    "NAD+", "NADH", "NADP+", "NADPH",
    "FAD", "FADH2",
    "CoA-SH", "CoA",
    "Acetyl-CoA",
}

UBIQUITIN_NAMES = {"Ub", "ubiquitin", "Ubiquitin"}


COMPARTMENT_SHORT = {
    "cytosol": "cyto",
    "nucleoplasm": "nuc",
    "nucleus": "nuc",
    "extracellular": "ext",
    "extracellular_space": "ext",
    "plasma_membrane": "pm",
    "early_space_endosome": "endo",
    "endosome": "endo",
    "endosomal_membrane": "endo",
    "Golgi_space_lumen": "golgi",
    "Golgi": "golgi",
    "endoplasmic_reticulum_lumen": "er",
    "ER": "er",
    "mitochondrial_matrix": "mito",
    "mitochondrion": "mito",
    "default": "def",
}


def sanitise(name: str) -> str:
    """Make a name safe to use as part of an SBML id."""
    s = name.strip()
    # Collapse complex separators
    s = s.replace(":", "_x_")
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unknown"


def compartment_short(name: str | None) -> str:
    if not name:
        return "x"
    return COMPARTMENT_SHORT.get(name, sanitise(name).lower()[:8])


def species_tag() -> str:
    return f"{{{SBML_NS}}}species"


def reaction_tag() -> str:
    return f"{{{SBML_NS}}}reaction"


def compartment_tag() -> str:
    return f"{{{SBML_NS}}}compartment"


def _find_all_elems_with_attr(root: ET.Element, attr: str) -> list[ET.Element]:
    """Return every element in the tree whose attributes contain `attr` (qualified or not)."""
    out: list[ET.Element] = []
    for elem in root.iter():
        if attr in elem.attrib:
            out.append(elem)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output XML path (default: input with .processed.xml suffix)",
    )
    args = ap.parse_args(argv[1:])

    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    out_path = args.out or args.input.with_suffix(".processed.xml")
    report_path = out_path.with_suffix(".report.json")

    tree = ET.parse(args.input)
    root = tree.getroot()

    # ----- Compartment lookup: id -> short label ---------------------------
    compartments_by_id: dict[str, str] = {}
    for comp in root.iter(compartment_tag()):
        comp_id = comp.get("id", "")
        comp_name = comp.get("name") or comp_id
        compartments_by_id[comp_id] = compartment_short(comp_name)

    # ----- Analyse species ------------------------------------------------
    species_elems = list(root.iter(species_tag()))
    species_by_id: dict[str, dict[str, str]] = {}
    for sp in species_elems:
        sp_id = sp.get("id") or ""
        species_by_id[sp_id] = {
            "name": sp.get("name") or "",
            "compartment": sp.get("compartment") or "",
        }

    rename_map: dict[str, str] = {}   # old_id -> new_id
    removed: set[str] = set()
    collapse_map: dict[str, str] = {}  # removed_id -> kept_id (for cofactor collapse)

    # Plan cofactor collapse: per (name, compartment) keep the first id.
    cofactor_first: dict[tuple[str, str], str] = {}
    for sp_id, attrs in species_by_id.items():
        name = attrs["name"]
        comp = attrs["compartment"]
        if name in COFACTORS:
            key = (name, comp)
            if key in cofactor_first:
                kept = cofactor_first[key]
                collapse_map[sp_id] = kept
                removed.add(sp_id)
            else:
                cofactor_first[key] = sp_id

    # Plan ubiquitin removal.
    for sp_id, attrs in species_by_id.items():
        if attrs["name"] in UBIQUITIN_NAMES and sp_id not in removed:
            removed.add(sp_id)

    # Plan renames for everything kept.
    used_new_ids: set[str] = set()
    for sp_id, attrs in species_by_id.items():
        if sp_id in removed:
            continue
        base = sanitise(attrs["name"])
        comp_short = compartments_by_id.get(attrs["compartment"], "x")
        candidate = f"{base}__{comp_short}"
        # Make unique by suffixing a counter if necessary
        if candidate in used_new_ids:
            i = 2
            while f"{candidate}_{i}" in used_new_ids:
                i += 1
            candidate = f"{candidate}_{i}"
        used_new_ids.add(candidate)
        if candidate != sp_id:
            rename_map[sp_id] = candidate

    # Effective id for any old id (handles both rename + collapse).
    def resolve(old: str) -> str | None:
        if old in collapse_map:
            kept = collapse_map[old]
            return rename_map.get(kept, kept)
        if old in removed:
            return None
        return rename_map.get(old, old)

    # ----- Apply renames and rewrites -------------------------------------
    # 1. Species: drop removed; rename id (and metaid for SBML/RDF consistency).
    for sp in list(species_elems):
        sp_id = sp.get("id") or ""
        if sp_id in removed:
            # Find parent and remove
            for parent in root.iter():
                if sp in list(parent):
                    parent.remove(sp)
                    break
            continue
        new = rename_map.get(sp_id)
        if new:
            sp.set("id", new)
            # SBML rdf:about references the metaid; keep metaid == id so the
            # annotation links stay consistent after rewrite.
            sp.set("metaid", new)

    # 2. Walk every element with attributes that reference a species id.
    #    SBML uses `species`; CellDesigner-specific elements also use
    #    `reactant`, `product`, and `modifiers` (space-separated list).
    elems_to_drop: list[tuple[ET.Element, ET.Element]] = []

    def _rewrite_single_attr(elem: ET.Element, attr: str) -> None:
        ref = elem.get(attr) or ""
        if not ref:
            return
        new = resolve(ref)
        if new is None:
            for parent in root.iter():
                if elem in list(parent):
                    elems_to_drop.append((parent, elem))
                    break
        elif new != ref:
            elem.set(attr, new)

    def _rewrite_id_list_attr(elem: ET.Element, attr: str) -> None:
        raw = elem.get(attr) or ""
        if not raw.strip():
            return
        new_ids: list[str] = []
        any_resolved_to_none = False
        for ref in raw.split():
            new = resolve(ref)
            if new is None:
                any_resolved_to_none = True
                continue
            new_ids.append(new)
        if not new_ids and any_resolved_to_none:
            # all referenced species were removed -> drop the modifier element
            for parent in root.iter():
                if elem in list(parent):
                    elems_to_drop.append((parent, elem))
                    break
        else:
            elem.set(attr, " ".join(new_ids))

    for elem in _find_all_elems_with_attr(root, "species"):
        _rewrite_single_attr(elem, "species")
    for elem in _find_all_elems_with_attr(root, "reactant"):
        _rewrite_single_attr(elem, "reactant")
    for elem in _find_all_elems_with_attr(root, "product"):
        _rewrite_single_attr(elem, "product")
    for elem in _find_all_elems_with_attr(root, "modifiers"):
        _rewrite_id_list_attr(elem, "modifiers")

    for parent, elem in elems_to_drop:
        try:
            parent.remove(elem)
        except ValueError:
            pass

    # 3. CellDesigner speciesAlias has its own id; we keep it but update its `species` attr.
    # (Already handled by step 2 since the attribute is called `species`.)

    # 4. rdf:Description / rdf:about — references look like "#<old_id>".
    rdf_desc_tag = f"{{{RDF_NS}}}Description"
    rdf_about_attr = f"{{{RDF_NS}}}about"
    rdf_dropped = 0
    for desc in list(root.iter(rdf_desc_tag)):
        about = desc.get(rdf_about_attr) or ""
        if about.startswith("#"):
            ref = about[1:]
            new = resolve(ref)
            if new is None:
                # Drop the description.
                for parent in root.iter():
                    if desc in list(parent):
                        parent.remove(desc)
                        rdf_dropped += 1
                        break
            elif new != ref:
                desc.set(rdf_about_attr, "#" + new)

    # 5. Reactions: if a reaction now has no reactants AND no products, remove it.
    reactions_removed: list[str] = []
    for rxn in list(root.iter(reaction_tag())):
        listOfReactants = rxn.find(f"{{{SBML_NS}}}listOfReactants")
        listOfProducts = rxn.find(f"{{{SBML_NS}}}listOfProducts")
        n_react = 0 if listOfReactants is None else len(list(listOfReactants))
        n_prod = 0 if listOfProducts is None else len(list(listOfProducts))
        if n_react == 0 and n_prod == 0:
            for parent in root.iter():
                if rxn in list(parent):
                    parent.remove(rxn)
                    reactions_removed.append(rxn.get("id", "?"))
                    break

    # ----- Write outputs --------------------------------------------------
    tree.write(out_path, encoding="UTF-8", xml_declaration=True)

    # Re-count for the report
    new_species = list(root.iter(species_tag()))
    new_reactions = list(root.iter(reaction_tag()))

    report = {
        "input": str(args.input),
        "output": str(out_path),
        "summary": {
            "species_in": len(species_by_id),
            "species_out": len(new_species),
            "species_renamed": len(rename_map),
            "species_collapsed_cofactor": len(collapse_map),
            "species_removed_ubiquitin": sum(
                1 for sid in removed if sid not in collapse_map
            ),
            "reactions_in": len(list(root.iter(reaction_tag()))) + len(reactions_removed),
            "reactions_out": len(new_reactions),
            "reactions_removed_orphan": len(reactions_removed),
            "rdf_descriptions_dropped": rdf_dropped,
        },
        "renames_sample": dict(list(rename_map.items())[:20]),
        "cofactor_collapses": [
            {"from": old, "into": resolve(collapse_map[old])}
            for old in collapse_map
        ],
        "ubiquitin_removed": [
            sid for sid in removed
            if sid not in collapse_map and species_by_id[sid]["name"] in UBIQUITIN_NAMES
        ],
        "reactions_removed": reactions_removed,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[ok] wrote {out_path}")
    print(f"[ok] wrote {report_path}")
    print("--- summary ---")
    for k, v in report["summary"].items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
