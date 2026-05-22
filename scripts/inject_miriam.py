#!/usr/bin/env python3
"""E11 — Inject MIRIAM CVTerm annotations into SSc_MIM_integrated.xml.

The CellDesigner round-trip keeps cross-references (HGNC symbol,
taxonomy) in ``curation/annotations/species_annotations.tsv`` rather
than as MIRIAM ``bqbiol:is`` CVTerm blocks inside the SBML model. The
BioModels submission portal requires the structured-annotation form
to index species against identifier registries.

This script reads species_annotations.tsv, injects:

  bqbiol:isVersionOf identifiers.org/hgnc.symbol/<SYMBOL>   (n=206)
  bqbiol:isVersionOf identifiers.org/taxonomy/<taxon>       (n=526)

into every species via libSBML's CVTerm API (so the resulting
annotation block is BioModels-clean and round-trip-safe), and writes
the result to ``curation/celldesigner/SSc_MIM_integrated.biomodels.xml``.

We use ``bqbiol:isVersionOf`` rather than ``bqbiol:is`` because most
of our species are *qualified* versions of the canonical HGNC entity
(phosphorylated, complex member, compartment-tagged), which is exactly
what BioModels recommends for non-canonical entity instances.

Output:
  curation/celldesigner/SSc_MIM_integrated.biomodels.xml
  curation/celldesigner/SSc_MIM_integrated.miriam_report.json

To regenerate:
  make biomodels
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import libsbml

SRC_XML = Path("curation/celldesigner/SSc_MIM_integrated.xml")
SRC_ANN = Path("curation/annotations/species_annotations.tsv")
OUT_XML = Path("curation/celldesigner/SSc_MIM_integrated.biomodels.xml")
OUT_REPORT = Path("curation/celldesigner/SSc_MIM_integrated.miriam_report.json")

HGNC_URL = "http://identifiers.org/hgnc.symbol/"
TAXONOMY_URL = "http://identifiers.org/taxonomy/"


def add_cv(species, qualifier_int: int, urls: list[str]) -> int:
    """Add a single MIRIAM CVTerm with multiple resources. Returns 1 on success."""
    cv = libsbml.CVTerm()
    cv.setQualifierType(libsbml.BIOLOGICAL_QUALIFIER)
    cv.setBiologicalQualifierType(qualifier_int)
    for u in urls:
        cv.addResource(u)
    species.addCVTerm(cv)
    return 1


def main() -> int:
    # Load annotation table
    ann_by_id: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(SRC_ANN.open(), delimiter="\t"):
        ann_by_id[row["species_id"]] = row

    reader = libsbml.SBMLReader()
    doc = reader.readSBMLFromFile(str(SRC_XML))
    if doc.getNumErrors() > 0:
        for i in range(doc.getNumErrors()):
            err = doc.getError(i)
            if err.getSeverity() >= libsbml.LIBSBML_SEV_ERROR:
                print("ERR:", err.getMessage())
                return 2
    model = doc.getModel()

    # Species: SBO is set via setMetaId requirement for CVTerm to be valid
    n_species = model.getNumSpecies()
    stats = {
        "n_species": n_species,
        "with_hgnc": 0,
        "with_taxonomy": 0,
        "with_neither": 0,
    }
    for i in range(n_species):
        sp = model.getSpecies(i)
        sid = sp.getId()
        ann = ann_by_id.get(sid, {})
        # libSBML requires a metaId on the element receiving annotations
        if not sp.isSetMetaId():
            sp.setMetaId(f"meta_{sid}")

        hgnc = (ann.get("hgnc_symbol") or "").strip()
        taxon = (ann.get("taxonomy") or "").strip()
        had_any = False
        if hgnc:
            add_cv(sp, libsbml.BQB_IS_VERSION_OF, [HGNC_URL + hgnc])
            stats["with_hgnc"] += 1
            had_any = True
        if taxon:
            add_cv(sp, libsbml.BQB_HAS_TAXON, [TAXONOMY_URL + taxon])
            stats["with_taxonomy"] += 1
            had_any = True
        if not had_any:
            stats["with_neither"] += 1

    # Write
    OUT_XML.parent.mkdir(parents=True, exist_ok=True)
    libsbml.writeSBMLToFile(doc, str(OUT_XML))

    # libSBML's serializer can leave bqbiol:* elements without declaring
    # the xmlns:bqbiol prefix on the surrounding <rdf:RDF> block when
    # the parent was a pre-existing CellDesigner annotation. Patch
    # every offending rdf:RDF tag in-place. (Strict XML 1.0 parsers
    # otherwise reject the file with "unbound prefix".)
    import re
    text = OUT_XML.read_text(encoding="utf-8")
    bqbiol_decl = ' xmlns:bqbiol="http://biomodels.net/biology-qualifiers/"'

    def _ensure_bqbiol(match):
        tag = match.group(0)
        if "xmlns:bqbiol" in tag:
            return tag
        # Insert before the closing '>' (handle both >  and  /> just in case)
        return tag[:-1] + bqbiol_decl + ">"

    text = re.sub(r"<rdf:RDF\b[^>]*>", _ensure_bqbiol, text)
    OUT_XML.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_XML} (with xmlns:bqbiol patched into all rdf:RDF blocks)")

    # Sanity-check post-write
    doc2 = libsbml.SBMLReader().readSBMLFromFile(str(OUT_XML))
    m2 = doc2.getModel()
    n_cv = 0; n_hgnc = 0; n_tax = 0
    for i in range(m2.getNumSpecies()):
        sp = m2.getSpecies(i)
        for k in range(sp.getNumCVTerms()):
            cv = sp.getCVTerm(k)
            n_cv += 1
            for r in range(cv.getNumResources()):
                u = cv.getResourceURI(r)
                if "hgnc.symbol" in u:
                    n_hgnc += 1
                elif "taxonomy" in u:
                    n_tax += 1
    stats["post_write_total_cvterm_resources"] = n_cv
    stats["post_write_hgnc_resources"] = n_hgnc
    stats["post_write_taxonomy_resources"] = n_tax

    print()
    print(f"Species:                              {n_species}")
    print(f"  with HGNC injected:                 {stats['with_hgnc']}")
    print(f"  with taxonomy injected:             {stats['with_taxonomy']}")
    print(f"  with neither (no identifier known): {stats['with_neither']}")
    print(f"Round-trip read CVTerm resources:     {n_cv} "
          f"(hgnc={n_hgnc}, taxon={n_tax})")

    OUT_REPORT.write_text(json.dumps(stats, indent=2) + "\n")
    print(f"wrote {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
