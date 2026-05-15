#!/usr/bin/env python3
"""Harmonise a *.processed.xml import: normalise identifiers and flag biology.

This is the third step of the import pipeline, after fetch (reactome_pilot)
and post-process (post_process_reactome). It targets the "import-cleanup
backlog" documented in docs/import_pilot.md.

It does only **identifier-level** transformations (rename species ids,
rewrite references). Any structural change (splitting a family species
into N members and fanning reactions; promoting a phospho-prefix to a
true SBGN state variable) is left to the CellDesigner curator and is
flagged in the JSON report.

Transformations applied
-----------------------
The species `name` attribute carries CellDesigner-encoded text:
    _space_   -> ' '
    _slash_   -> '/'
    _minus_   -> '-'
    _x_       -> ':'

After decoding, the harmoniser computes a clean species id with the rules
below (first match wins):

1. Known gene-family placeholders:
     "Mx GTPases"                 -> MX_family
     "OAS proteins"               -> OAS_family
     "IRF 1-9"                    -> IRF_family
     "SOCS-1/SOCS-3"              -> SOCS_family
     "Type I IFN-regulated genes…" -> ISG_signature
   Flagged in report under `family_to_expand`.

2. Phospho prefix: "p-X" -> "pX". Flagged under `phospho_state`.

3. Isoform suffix: "X-N" (X is a known HGNC-like prefix, N is one digit)
   -> "X_iso<N>". Flagged under `isoform`.

4. Dimer prefix: "Dimeric X" -> "X_dimer". Flagged under `homodimer`.

5. Slash-pair "X/Y" (no compartment context) -> "XY", flagged under
   `slash_pair_to_split`.

6. Otherwise: keep the post-processor id.

Compartment "default" is remapped to "extracellular" with a flag.

Outputs
-------
- <input>.harmonised.xml
- <input>.harmonised.report.json (every rename + flags)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

ET.register_namespace("", SBML_NS)
ET.register_namespace("celldesigner", CD_NS)
ET.register_namespace("rdf", RDF_NS)


def species_tag() -> str:
    return f"{{{SBML_NS}}}species"


def reaction_tag() -> str:
    return f"{{{SBML_NS}}}reaction"


def compartment_tag() -> str:
    return f"{{{SBML_NS}}}compartment"


def decode_name(s: str) -> str:
    """Reverse CellDesigner's escape encoding."""
    return (
        s.replace("_space_", " ")
        .replace("_slash_", "/")
        .replace("_minus_", "-")
        .replace("_x_", ":")
    )


def sanitise_for_id(s: str) -> str:
    out = re.sub(r"[^A-Za-z0-9_]+", "_", s)
    out = re.sub(r"_+", "_", out).strip("_")
    return out or "unknown"


COMPARTMENT_REMAP_DEFAULT = {
    # MINERVA-converted Reactome compartments -> our fixed vocabulary
    "default": "extracellular",
    "extracellular_space_exosome": "extracellular",
    "early_space_endosome": "endosome",
    "Golgi_space_lumen": "Golgi",
    "endoplasmic_space_reticulum_space_lumen": "ER",
    "nucleoplasm": "nucleus",
    "mitochondrial_space_matrix": "mitochondrion",
}

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


# Known gene-family placeholders. The expansion list documents the members
# the curator should later instantiate; we keep one species per family in
# the harmonised XML and flag it for split.
FAMILY_RULES = {
    "Mx GTPases": ("MX_family", ["MX1", "MX2"]),
    "OAS proteins": ("OAS_family", ["OAS1", "OAS2", "OAS3"]),
    "IRF 1-9": ("IRF_family", [f"IRF{i}" for i in range(1, 10)]),
    "SOCS-1/SOCS-3": ("SOCS_family", ["SOCS1", "SOCS3"]),
    "SOCS-1 and SOCS-3": ("SOCS_family", ["SOCS1", "SOCS3"]),
    "SOCS-1/SOCS-3 ": ("SOCS_family", ["SOCS1", "SOCS3"]),  # trailing space variant
}


GENE_SET_PATTERNS = {
    # substring -> canonical id
    "Type I IFN-regulated genes": "ISG_signature",
    "Type I IFN regulated genes": "ISG_signature",
    "IFN-regulated genes": "ISG_signature",
}


PHOSPHO_RE = re.compile(r"^p-([A-Za-z][A-Za-z0-9]+)$")
ISOFORM_RE = re.compile(r"^([A-Z][A-Z0-9]+)-([0-9])$")
DIMER_RE = re.compile(r"^Dimeric\s+([A-Z][A-Z0-9]+)$", re.IGNORECASE)
SLASH_PAIR_RE = re.compile(r"^([A-Z][A-Z0-9]{1,8})/([A-Z][A-Z0-9]{1,8})$")


def classify(name_decoded: str) -> tuple[str, str, str]:
    """Return (id_stem, flag, note) for a decoded name.

    id_stem is the un-compartment-qualified id stem; the caller appends the
    compartment short label.
    """
    n = name_decoded.strip()

    # 1. Gene-set placeholders (substring match)
    for needle, canonical in GENE_SET_PATTERNS.items():
        if needle in n:
            return canonical, "gene_set_placeholder", n

    # 2. Known families (exact match)
    if n in FAMILY_RULES:
        canonical, members = FAMILY_RULES[n]
        return canonical, "family_to_expand", ",".join(members)

    # 3. Phospho prefix
    m = PHOSPHO_RE.match(n)
    if m:
        sym = m.group(1)
        return f"p{sym}", "phospho_state", f"phospho-{sym}; promote to state variable"

    # 4. Isoform suffix
    m = ISOFORM_RE.match(n)
    if m:
        sym, iso = m.groups()
        return f"{sym}_iso{iso}", "isoform", f"isoform {iso} of {sym}"

    # 5. Dimer prefix
    m = DIMER_RE.match(n)
    if m:
        sym = m.group(1)
        return f"{sym}_dimer", "homodimer", f"homodimer of {sym}"

    # 6. Slash pair "X/Y" (only short symbols, not part of a complex name)
    m = SLASH_PAIR_RE.match(n)
    if m:
        a, b = m.groups()
        return f"{a}_{b}", "slash_pair_to_split", f"split into {a} + {b}"

    # Default: sanitise the decoded name without removing any meaning.
    return sanitise_for_id(n), "", ""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv[1:])

    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    out_path = args.out or args.input.with_name(
        args.input.name.replace(".processed.xml", ".harmonised.xml")
    )
    if out_path == args.input:
        print("refusing to overwrite input; pass --out", file=sys.stderr)
        return 2
    report_path = out_path.with_suffix(".report.json")

    tree = ET.parse(args.input)
    root = tree.getroot()

    # Compartment remap pass (id stays the same; we update the `name`
    # attribute on the compartment to use the vocabulary, and compute a
    # `comp_short_by_id` lookup for new species ids).
    comp_short_by_id: dict[str, str] = {}
    comp_remap_events: list[dict[str, str]] = []
    for comp in root.iter(compartment_tag()):
        cid = comp.get("id", "")
        cname = comp.get("name") or cid
        new_name = COMPARTMENT_REMAP_DEFAULT.get(cname, cname)
        if new_name != cname:
            comp_remap_events.append({"id": cid, "from": cname, "to": new_name})
            comp.set("name", new_name)
        comp_short_by_id[cid] = COMPARTMENT_SHORT.get(new_name, new_name[:6].lower())

    # Compute rename plan for species (id-only)
    rename_map: dict[str, str] = {}
    transforms: list[dict[str, str]] = []
    used_new_ids: set[str] = set()

    for sp in root.iter(species_tag()):
        old_id = sp.get("id") or ""
        old_name = sp.get("name") or ""
        decoded = decode_name(old_name)
        stem, flag, note = classify(decoded)
        cs = comp_short_by_id.get(sp.get("compartment") or "", "x")
        candidate = f"{stem}__{cs}"
        # uniquify
        base = candidate
        i = 2
        while candidate in used_new_ids:
            candidate = f"{base}_{i}"
            i += 1
        used_new_ids.add(candidate)

        if candidate != old_id:
            rename_map[old_id] = candidate
            # Update name to the human-readable decoded form (preserves
            # the original meaning while shedding CellDesigner encoding).
            sp.set("name", decoded)
            sp.set("id", candidate)
            sp.set("metaid", candidate)
            transforms.append({
                "from_id": old_id,
                "to_id": candidate,
                "decoded_name": decoded,
                "flag": flag,
                "note": note,
            })
        else:
            # still update name to decoded form for human-friendliness
            if decoded != old_name:
                sp.set("name", decoded)

    # Walk all attributes that reference a species id.
    def resolve(ref: str) -> str:
        return rename_map.get(ref, ref)

    for elem in root.iter():
        for attr in ("species", "reactant", "product"):
            if attr in elem.attrib:
                ref = elem.get(attr) or ""
                new = resolve(ref)
                if new != ref:
                    elem.set(attr, new)
        if "modifiers" in elem.attrib:
            raw = elem.get("modifiers") or ""
            ids = raw.split()
            new_ids = [resolve(i) for i in ids]
            if new_ids != ids:
                elem.set("modifiers", " ".join(new_ids))

    # rdf:about uses '#metaid'; we kept metaid == id, so update accordingly.
    rdf_desc_tag = f"{{{RDF_NS}}}Description"
    rdf_about_attr = f"{{{RDF_NS}}}about"
    for desc in root.iter(rdf_desc_tag):
        about = desc.get(rdf_about_attr) or ""
        if about.startswith("#"):
            ref = about[1:]
            new = resolve(ref)
            if new != ref:
                desc.set(rdf_about_attr, "#" + new)

    # Decode CellDesigner annotation labels (`<celldesigner:name>…</…>`
    # and the `name=` attribute on `<celldesigner:protein>`) so the
    # CellDesigner canvas shows human-readable text. These are display-only
    # fields; the structural ids are already updated above.
    cd_name_tag = f"{{{CD_NS}}}name"
    cd_protein_tag = f"{{{CD_NS}}}protein"
    decoded_labels = 0
    for elem in root.iter(cd_name_tag):
        if elem.text and any(tok in elem.text for tok in ("_space_", "_slash_", "_minus_", "_x_")):
            elem.text = decode_name(elem.text)
            decoded_labels += 1
    for elem in root.iter(cd_protein_tag):
        nm = elem.get("name")
        if nm and any(tok in nm for tok in ("_space_", "_slash_", "_minus_", "_x_")):
            elem.set("name", decode_name(nm))
            decoded_labels += 1

    tree.write(out_path, encoding="UTF-8", xml_declaration=True)

    # ---- summary ------------------------------------------------------
    flag_counts: dict[str, int] = {}
    for t in transforms:
        f = t["flag"] or "renamed_only"
        flag_counts[f] = flag_counts.get(f, 0) + 1

    report = {
        "input": str(args.input),
        "output": str(out_path),
        "compartment_remaps": comp_remap_events,
        "species_renamed": len(rename_map),
        "celldesigner_labels_decoded": decoded_labels,
        "flag_counts": flag_counts,
        "transforms_sample": transforms[:20],
        "all_flagged": [t for t in transforms if t["flag"]],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[ok] wrote {out_path}")
    print(f"[ok] wrote {report_path}")
    print("--- summary ---")
    print(f"  compartment_remaps: {len(comp_remap_events)}")
    print(f"  species_renamed:    {len(rename_map)}")
    for f, c in sorted(flag_counts.items()):
        print(f"    flag={f}: {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
