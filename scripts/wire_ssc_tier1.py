#!/usr/bin/env python3
"""Apply SSc-specific Tier-1 curation to the integrated map.

Reads:
  - curation/celldesigner/SSc_MIM_integrated.xml      (current integrated map)
  - curation/celldesigner/ssc_additions_template/M*_ssc_additions.xml  (88 stubs)
  - curation/ssc_curated_reactions.tsv                 (source-of-truth reactions)

Writes:
  - curation/celldesigner/SSc_MIM_integrated.xml      (in place)
  - curation/celldesigner/SSc_MIM_integrated.wire_report.json
  - curation/annotations/reaction_evidence.tsv        (append curated rows)

Species creation policy (per docs/curation_plan.md):
  - id with __cyto / __nuc / __ext / __ecm / __pm / __er / __endo / __mito
    / __golgi / __cell suffix → infer compartment from suffix.
  - id starting with `phenotype_` → SBGN Phenotype glyph.
  - lowercase first letter → small molecule.
  - uppercase HGNC-like → macromolecule.

No SBO terms emitted for now (curator-readable form first; SBO upgrade
is a one-liner the co-author can add via the GUI). Each reaction gets
the SBML `notes` block with mechanism + ssc_relevance + notes for
traceability on the canvas.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
XHTML_NS = "http://www.w3.org/1999/xhtml"


ET.register_namespace("", SBML_NS)
ET.register_namespace("celldesigner", CD_NS)


def q(tag: str, ns: str = SBML_NS) -> str:
    return f"{{{ns}}}{tag}"


COMPARTMENT_FROM_SUFFIX = {
    "cyto": "cytosol",
    "nuc": "nucleus",
    "ext": "extracellular",
    "ecm": "ECM",
    "pm": "plasma_membrane",
    "er": "ER",
    "endo": "endosome",
    "mito": "mitochondrion",
    "golgi": "Golgi",
    "cell": "cell",
}


REACTION_COLUMNS = [
    "reaction_id", "type", "participants", "mechanism",
    "pmid", "evidence_code", "context_biotype", "context_assay",
    "module", "crosstalk_modules", "notes",
]

SPECIES_COLUMNS = [
    "species_id", "hgnc_symbol", "uniprot", "ensembl", "chebi",
    "compartment", "module", "taxonomy", "notes",
]


def infer_compartment(species_id: str) -> str:
    parts = species_id.rsplit("__", 1)
    if len(parts) == 2 and parts[1] in COMPARTMENT_FROM_SUFFIX:
        return COMPARTMENT_FROM_SUFFIX[parts[1]]
    return "cytosol"


def infer_kind(species_id: str) -> str:
    base = species_id.split("__", 1)[0]
    if base.startswith("phenotype_"):
        return "phenotype"
    if base[:1].islower():
        return "simple_chemical"
    return "macromolecule"


def display_name(species_id: str) -> str:
    base = species_id.split("__", 1)[0]
    return base.replace("_", " ")


def load_stubs(template_dir: Path) -> dict[str, dict[str, str]]:
    """Return {species_id: {name, compartment}} for every stub species."""
    out: dict[str, dict[str, str]] = {}
    for f in sorted(template_dir.glob("M*_ssc_additions.xml")):
        tree = ET.parse(f)
        for sp in tree.iter(q("species")):
            sid = sp.get("id") or ""
            out[sid] = {
                "name": sp.get("name") or display_name(sid),
                "compartment": sp.get("compartment") or infer_compartment(sid),
            }
    return out


def ensure_compartment(root: ET.Element, name: str) -> str:
    """Ensure a compartment with given vocabulary name exists. Return its id."""
    model = root.find(q("model"))
    loc = model.find(q("listOfCompartments"))
    if loc is None:
        loc = ET.SubElement(model, q("listOfCompartments"))
    for c in loc.findall(q("compartment")):
        if (c.get("name") or "") == name or c.get("id") == name:
            return c.get("id") or name
    new = ET.SubElement(loc, q("compartment"))
    new.set("id", name)
    new.set("name", name)
    new.set("size", "1")
    return name


def add_species(root: ET.Element, sid: str, name: str, compartment: str, modules: list[str], notes: str = "") -> None:
    model = root.find(q("model"))
    los = model.find(q("listOfSpecies"))
    if los is None:
        los = ET.SubElement(model, q("listOfSpecies"))
    sp = ET.SubElement(los, q("species"))
    sp.set("id", sid)
    sp.set("metaid", sid)
    sp.set("name", name)
    sp.set("compartment", compartment)
    sp.set("initialAmount", "0")
    nb = ET.SubElement(sp, q("notes"))
    html = ET.SubElement(nb, f"{{{XHTML_NS}}}html")
    body = ET.SubElement(html, f"{{{XHTML_NS}}}body")
    p_mod = ET.SubElement(body, f"{{{XHTML_NS}}}p")
    p_mod.text = "module=" + ",".join(sorted(set(modules)))
    p_tier = ET.SubElement(body, f"{{{XHTML_NS}}}p")
    p_tier.text = "tier=1"
    if notes:
        p_n = ET.SubElement(body, f"{{{XHTML_NS}}}p")
        p_n.text = "notes=" + notes


def add_reaction(
    root: ET.Element,
    rxn_id: str,
    name: str,
    reactants: list[str],
    products: list[str],
    modifiers: list[str],
    module: str,
    mechanism: str,
    pmid: str,
    eco: str,
    ssc_relevance: str,
    notes: str,
) -> None:
    model = root.find(q("model"))
    lor = model.find(q("listOfReactions"))
    if lor is None:
        lor = ET.SubElement(model, q("listOfReactions"))
    rxn = ET.SubElement(lor, q("reaction"))
    rxn.set("id", rxn_id)
    rxn.set("metaid", rxn_id)
    rxn.set("name", name)
    rxn.set("reversible", "false")

    # notes block — preserves the curation rationale on the SBML model
    nb = ET.SubElement(rxn, q("notes"))
    html = ET.SubElement(nb, f"{{{XHTML_NS}}}html")
    body = ET.SubElement(html, f"{{{XHTML_NS}}}body")
    for k, v in [("module", module), ("mechanism", mechanism), ("pmid", pmid),
                 ("evidence_code", eco), ("ssc_relevance", ssc_relevance),
                 ("curation_note", notes)]:
        if v:
            p = ET.SubElement(body, f"{{{XHTML_NS}}}p")
            p.text = f"{k}={v}"

    if reactants:
        lr = ET.SubElement(rxn, q("listOfReactants"))
        for r in reactants:
            sr = ET.SubElement(lr, q("speciesReference"))
            sr.set("species", r)
    if products:
        lp = ET.SubElement(rxn, q("listOfProducts"))
        for p_ in products:
            sr = ET.SubElement(lp, q("speciesReference"))
            sr.set("species", p_)
    if modifiers:
        lm = ET.SubElement(rxn, q("listOfModifiers"))
        for m_ in modifiers:
            ms = ET.SubElement(lm, q("modifierSpeciesReference"))
            ms.set("species", m_)


def load_existing_species(root: ET.Element) -> set[str]:
    return {sp.get("id") or "" for sp in root.iter(q("species"))}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--integrated", type=Path, default=Path("curation/celldesigner/SSc_MIM_integrated.xml"))
    ap.add_argument("--template-dir", type=Path, default=Path("curation/celldesigner/ssc_additions_template"))
    ap.add_argument("--tsv", type=Path, default=Path("curation/ssc_curated_reactions.tsv"))
    ap.add_argument("--evidence-tsv", type=Path, default=Path("curation/annotations/reaction_evidence.tsv"))
    ap.add_argument(
        "--species-tsv",
        type=Path,
        default=Path("curation/annotations/species_annotations.tsv"),
    )
    args = ap.parse_args(argv[1:])

    if not args.integrated.exists():
        print(f"missing: {args.integrated}", file=sys.stderr)
        return 2

    tree = ET.parse(args.integrated)
    root = tree.getroot()
    existing = load_existing_species(root)
    stubs = load_stubs(args.template_dir)

    print(f"integrated map: {len(existing)} species before wiring")
    print(f"available stubs: {len(stubs)}")

    # Pass 1 — add every stub species not yet in the integrated map
    stubs_added = 0
    for sid, meta in stubs.items():
        if sid in existing:
            continue
        ensure_compartment(root, meta["compartment"])
        add_species(root, sid, meta["name"], meta["compartment"], modules=["ssc_tier1"], notes="from ssc_additions_template")
        existing.add(sid)
        stubs_added += 1
    print(f"  stubs wired into integrated map: {stubs_added}")

    # Pass 2 — read curated reactions, auto-create any missing referenced species
    reader = csv.DictReader(args.tsv.open(), delimiter="\t")
    rxn_rows = list(reader)
    print(f"curated reactions to add: {len(rxn_rows)}")

    auto_created: list[str] = []
    rxn_added = 0

    def resolve_species(sid: str, module: str) -> str:
        if sid in existing:
            return sid
        comp = infer_compartment(sid)
        ensure_compartment(root, comp)
        add_species(root, sid, display_name(sid), comp, modules=[module], notes="auto-created by wire_ssc_tier1")
        existing.add(sid)
        auto_created.append(sid)
        return sid

    new_evidence_rows: list[dict[str, str]] = []

    for row in rxn_rows:
        rxn_id = row["reaction_id"]
        module = row["module"]
        reactants = [s for s in row["reactants"].split(";") if s.strip()]
        products = [s for s in row["products"].split(";") if s.strip()]
        modifiers = [s for s in row["modifiers"].split(";") if s.strip()]

        # Ensure every species exists
        for s in reactants + products + modifiers:
            resolve_species(s, module)

        add_reaction(
            root,
            rxn_id=rxn_id,
            name=row["mechanism"][:80],
            reactants=reactants,
            products=products,
            modifiers=modifiers,
            module=module,
            mechanism=row["mechanism"],
            pmid=row["pmid"],
            eco=row["evidence_code"],
            ssc_relevance=row["ssc_relevance"],
            notes=row["notes"],
        )
        rxn_added += 1

        new_evidence_rows.append({
            "reaction_id": rxn_id,
            "type": row["type"],
            "participants": ";".join(reactants + products + modifiers),
            "mechanism": row["mechanism"],
            "pmid": row["pmid"],
            "evidence_code": row["evidence_code"],
            "context_biotype": "SSc dermal fibroblast / endothelium / immune (per module)",
            "context_assay": "curated from literature",
            "module": module,
            "crosstalk_modules": module if module == "crosstalk" else "",
            "notes": (row["ssc_relevance"] + " | " + row["notes"]).strip(" |"),
        })

    print(f"  species auto-created: {len(auto_created)}")
    print(f"  reactions added:      {rxn_added}")

    # Write back the integrated map
    tree.write(args.integrated, encoding="UTF-8", xml_declaration=True)
    print(f"[ok] wrote {args.integrated}")

    # Append to reaction_evidence.tsv
    if args.evidence_tsv.exists():
        existing_lines = args.evidence_tsv.read_text(encoding="utf-8").splitlines()
        header_line = existing_lines[0] if existing_lines else "\t".join(REACTION_COLUMNS)
        body_lines = existing_lines[1:] if existing_lines else []
        existing_ids = {ln.split("\t", 1)[0] for ln in body_lines}
    else:
        header_line = "\t".join(REACTION_COLUMNS)
        body_lines = []
        existing_ids = set()

    for r in new_evidence_rows:
        if r["reaction_id"] in existing_ids:
            continue
        body_lines.append("\t".join(r.get(c, "") for c in REACTION_COLUMNS))
        existing_ids.add(r["reaction_id"])

    args.evidence_tsv.write_text(
        header_line + "\n" + "\n".join(body_lines) + "\n",
        encoding="utf-8",
    )
    print(f"[ok] {args.evidence_tsv}: {len(body_lines)} rows total")

    # Append missing species to species_annotations.tsv (idempotent on species_id)
    if args.species_tsv.exists():
        sp_lines = args.species_tsv.read_text(encoding="utf-8").splitlines()
        sp_header = sp_lines[0] if sp_lines else "\t".join(SPECIES_COLUMNS)
        sp_body = sp_lines[1:] if sp_lines else []
        sp_existing_ids = {ln.split("\t", 1)[0] for ln in sp_body}
    else:
        sp_header = "\t".join(SPECIES_COLUMNS)
        sp_body = []
        sp_existing_ids = set()

    new_sp_rows: list[str] = []
    XHTML_P = f"{{{XHTML_NS}}}p"
    for sp in root.iter(q("species")):
        sid = sp.get("id") or ""
        if not sid or sid in sp_existing_ids:
            continue
        compartment = sp.get("compartment") or infer_compartment(sid)
        name = sp.get("name") or display_name(sid)
        # try to recover module annotation if present
        module = ""
        for p in sp.iter(XHTML_P):
            if (p.text or "").startswith("module="):
                module = p.text.split("=", 1)[1].strip()
                break
        # heuristic HGNC fill
        base = sid.split("__", 1)[0]
        hgnc = base if base.isupper() and "_" not in base and len(base) <= 12 else ""
        new_sp_rows.append("\t".join([
            sid, hgnc, "", "", "", compartment, module, "9606",
            "wired by wire_ssc_tier1.py",
        ]))
        sp_existing_ids.add(sid)

    args.species_tsv.write_text(
        sp_header + "\n" + "\n".join(sp_body + new_sp_rows) + "\n",
        encoding="utf-8",
    )
    print(f"[ok] {args.species_tsv}: +{len(new_sp_rows)} new species (total {len(sp_body) + len(new_sp_rows)})")

    # JSON report
    report = {
        "integrated_xml": str(args.integrated),
        "tsv_input": str(args.tsv),
        "stubs_wired": stubs_added,
        "reactions_added": rxn_added,
        "species_auto_created": auto_created,
    }
    report_path = args.integrated.with_suffix(".wire_report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[ok] {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
