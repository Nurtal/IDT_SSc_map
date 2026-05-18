#!/usr/bin/env python3
"""Integrate the harmonised module imports into one SSc-MIM SBML.

Inputs:
  - curation/imports/*/*/*.harmonised.xml   (5 files: M1, M2x2, M3, M4)

Output:
  - curation/celldesigner/SSc_MIM_integrated.xml
  - curation/celldesigner/SSc_MIM_integrated.report.json

Strategy
--------
1. Use the first file as the structural template (gets the SBML envelope,
   `<model>`, and the CellDesigner annotation extension; we replace the
   model id with `SSc_MIM_integrated`).
2. For each input file in order, walk `<listOfCompartments>`,
   `<listOfSpecies>`, `<listOfReactions>`. Add elements whose `id` is not
   already in the integrated model. Track every dedupe.
3. Tag each species with its source module(s) in `notes` so the curator
   knows which import contributed it. When the same `id` appears in two
   modules, append both module names.
4. Emit a JSON report listing every dedupe and the per-module final tally.

No CellDesigner aliases / layout glyphs are merged — that's a separate
step in the CellDesigner GUI. The output validates as SBML L2v4 (libSBML
check is run by the existing `validate` workflow).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

ET.register_namespace("", SBML_NS)
ET.register_namespace("celldesigner", CD_NS)
ET.register_namespace("rdf", RDF_NS)


def q(tag: str, ns: str = SBML_NS) -> str:
    return f"{{{ns}}}{tag}"


MODULE_RE = re.compile(r"/imports/(M[1-4])/")


def infer_module(path: Path) -> str:
    m = MODULE_RE.search(str(path))
    return m.group(1) if m else "?"


def _insert_notes_before_annotation(sp: ET.Element) -> ET.Element:
    """Create and insert a <notes> element before any existing <annotation>."""
    notes = ET.Element(q("notes"))
    annotation = sp.find(q("annotation"))
    if annotation is not None:
        idx = list(sp).index(annotation)
        sp.insert(idx, notes)
    else:
        sp.append(notes)
    return notes


def annotate_species_with_module(sp: ET.Element, module: str) -> None:
    """Append (or merge into) a `module=<list>` line in the species' notes.

    SBML <notes> contains an XHTML fragment (<html>/<body>/<p>). We search
    *recursively* for an existing `module=` paragraph; if found, merge the
    new module into its comma-separated list. Otherwise, write a fresh
    notes block.
    """
    notes = sp.find(q("notes"))
    if notes is None:
        notes = _insert_notes_before_annotation(sp)
    html_ns = "http://www.w3.org/1999/xhtml"
    p_tag = f"{{{html_ns}}}p"

    # Look for an existing <p>module=…</p> anywhere under notes
    for p in notes.iter(p_tag):
        if (p.text or "").startswith("module="):
            existing = p.text.split("=", 1)[1].strip()
            mods = {m.strip() for m in existing.split(",") if m.strip()}
            if module in mods:
                return  # already recorded
            mods.add(module)
            p.text = "module=" + ",".join(sorted(mods))
            return

    # No module annotation yet — pick or create a body to attach it to.
    body = None
    for b in notes.iter(f"{{{html_ns}}}body"):
        body = b
        break
    if body is None:
        html = ET.SubElement(notes, f"{{{html_ns}}}html")
        head = ET.SubElement(html, f"{{{html_ns}}}head")
        ET.SubElement(head, f"{{{html_ns}}}title")
        body = ET.SubElement(html, f"{{{html_ns}}}body")
    new_p = ET.SubElement(body, p_tag)
    new_p.text = f"module={module}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--inputs-glob",
        default="curation/imports/*/*/*.harmonised.xml",
        help="glob for harmonised XMLs to merge",
    )
    ap.add_argument(
        "--out",
        default="curation/celldesigner/SSc_MIM_integrated.xml",
        type=Path,
    )
    args = ap.parse_args(argv[1:])

    inputs = sorted(glob.glob(args.inputs_glob))
    if not inputs:
        print(f"no inputs match {args.inputs_glob}", file=sys.stderr)
        return 2

    base_tree = ET.parse(inputs[0])
    base_root = base_tree.getroot()
    base_model = base_root.find(q("model"))
    if base_model is None:
        print(f"first input has no <model>: {inputs[0]}", file=sys.stderr)
        return 2

    # Rename the integrated model
    base_model.set("id", "SSc_MIM_integrated")
    base_model.set("name", "SSc-MIM (integrated)")

    base_loc = base_model.find(q("listOfCompartments"))
    base_los = base_model.find(q("listOfSpecies"))
    base_lor = base_model.find(q("listOfReactions"))

    if base_loc is None:
        base_loc = ET.SubElement(base_model, q("listOfCompartments"))
    if base_los is None:
        base_los = ET.SubElement(base_model, q("listOfSpecies"))
    if base_lor is None:
        base_lor = ET.SubElement(base_model, q("listOfReactions"))

    seen_compartments = {c.get("id") for c in base_loc.findall(q("compartment"))}
    seen_species: dict[str, ET.Element] = {sp.get("id", ""): sp for sp in base_los.findall(q("species"))}
    seen_reactions = {r.get("id") for r in base_lor.findall(q("reaction"))}

    module_first = infer_module(Path(inputs[0]))
    for sp in seen_species.values():
        annotate_species_with_module(sp, module_first)

    dedupes: list[dict[str, str]] = []
    per_module_added: dict[str, dict[str, int]] = defaultdict(lambda: {
        "species_added": 0,
        "species_deduped": 0,
        "reactions_added": 0,
        "compartments_added": 0,
    })
    per_module_added[module_first] = {
        "species_added": len(seen_species),
        "species_deduped": 0,
        "reactions_added": len(seen_reactions),
        "compartments_added": len(seen_compartments),
    }

    for path_str in inputs[1:]:
        path = Path(path_str)
        module = infer_module(path)
        tree = ET.parse(path)
        model = tree.getroot().find(q("model"))
        if model is None:
            print(f"skip (no model): {path}")
            continue

        loc = model.find(q("listOfCompartments"))
        los = model.find(q("listOfSpecies"))
        lor = model.find(q("listOfReactions"))

        # Compartments
        if loc is not None:
            for c in loc.findall(q("compartment")):
                cid = c.get("id") or ""
                if cid and cid not in seen_compartments:
                    base_loc.append(c)
                    seen_compartments.add(cid)
                    per_module_added[module]["compartments_added"] += 1

        # Species
        if los is not None:
            for sp in los.findall(q("species")):
                sid = sp.get("id") or ""
                if not sid:
                    continue
                if sid in seen_species:
                    annotate_species_with_module(seen_species[sid], module)
                    dedupes.append({
                        "species_id": sid,
                        "module": module,
                        "via_file": path.name,
                    })
                    per_module_added[module]["species_deduped"] += 1
                else:
                    annotate_species_with_module(sp, module)
                    base_los.append(sp)
                    seen_species[sid] = sp
                    per_module_added[module]["species_added"] += 1

        # Reactions
        if lor is not None:
            for rx in lor.findall(q("reaction")):
                rid = rx.get("id") or ""
                if rid in seen_reactions:
                    continue
                base_lor.append(rx)
                seen_reactions.add(rid)
                per_module_added[module]["reactions_added"] += 1

    # SBML L2V4 requires <notes> before <annotation> in every element.
    # Reactome exports have the reversed order; fix it before writing.
    for el in base_root.iter():
        notes_el = el.find(q("notes"))
        annotation_el = el.find(q("annotation"))
        if notes_el is None or annotation_el is None:
            continue
        children = list(el)
        if children.index(notes_el) > children.index(annotation_el):
            el.remove(notes_el)
            el.insert(list(el).index(annotation_el), notes_el)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    base_tree.write(args.out, encoding="UTF-8", xml_declaration=True)

    report = {
        "output": str(args.out),
        "inputs": inputs,
        "totals": {
            "compartments": len(seen_compartments),
            "species": len(seen_species),
            "reactions": len(seen_reactions),
        },
        "per_module": dict(per_module_added),
        "dedupes": dedupes,
    }
    report_path = args.out.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[ok] integrated SBML: {args.out}")
    print(f"[ok] report:          {report_path}")
    print("--- totals ---")
    print(f"  compartments: {report['totals']['compartments']}")
    print(f"  species:      {report['totals']['species']}")
    print(f"  reactions:    {report['totals']['reactions']}")
    print(f"  dedupes:      {len(dedupes)}")
    print()
    print("--- per module ---")
    for mod, counts in sorted(per_module_added.items()):
        print(f"  {mod}: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
