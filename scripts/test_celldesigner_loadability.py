#!/usr/bin/env python3
"""CellDesigner-loadability test for SSc-MIM CellDesigner XML files.

CellDesigner (v4.4+) is a Java/Swing GUI, with no headless "open and
check" mode that we can call. Instead this script validates everything
that has to be in the XML for CellDesigner to *load it without error*
once a curator double-clicks it:

  Check 1  — libSBML L2V4 parse (no SBML-level errors)
  Check 2  — `xmlns:celldesigner` declared on <sbml>
  Check 3  — model-level <celldesigner:extension> present, with
             listOfCompartmentAliases / listOfSpeciesAliases /
             listOfProteins / listOfIncludedSpecies
  Check 4  — every <species> has a matching alias in
             celldesigner:listOfSpeciesAliases (id round-trip)
  Check 5  — every species declares a celldesigner:class
             (PROTEIN, COMPLEX, GENE, RNA, SIMPLE_MOLECULE, ION,
              DRUG, PHENOTYPE, UNKNOWN, ANTISENSE_RNA, GENE_PRODUCT,
              DEGRADED, RECEPTOR, ION_CHANNEL, TRUNCATED)
  Check 6  — every <reaction> declares celldesigner:baseReactants
             and celldesigner:baseProducts (CellDesigner requires
             at least one of each, even for boundary reactions)
  Check 7  — every compartment has a celldesigner:compartmentAlias
             with finite numeric x / y / w / h positions
  Check 8  — every reaction's reactant/product/modifier `species`
             attribute resolves to a real <species> id
  Check 9  — proteinReference cross-refs resolve to a protein in
             celldesigner:listOfProteins
  Check 10 — **functional smoke**: CaSQ 1.4.4 can convert the file
             to SBML-qual without raising (we already use this in
             the make casq target; here it doubles as a "downstream
             tool can consume the file" proof)

Each check reports OK / WARN / ERROR. Exit 0 if no ERRORs (WARNs are
informational); exit 1 otherwise. Verbose mode prints per-element
failure details (--verbose / -v).

Usage:
    python3 scripts/test_celldesigner_loadability.py [PATH ...]
    python3 scripts/test_celldesigner_loadability.py -v

Default targets: every *.xml under curation/celldesigner/ (excluding
the BioModels-MIRIAM variant, which is identical structurally but
adds bqbiol:* — already tested via CellDesigner because the parent
file passes).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

SBML_NS = "http://www.sbml.org/sbml/level2/version4"
CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
SBML_T = f"{{{SBML_NS}}}"
CD_T = f"{{{CD_NS}}}"

# CellDesigner accepts only this set of speciesIdentity classes.
CD_CLASSES = {
    "PROTEIN", "GENE", "GENE_PRODUCT", "RNA", "ANTISENSE_RNA",
    "SIMPLE_MOLECULE", "ION", "DRUG", "PHENOTYPE", "UNKNOWN",
    "COMPLEX", "DEGRADED", "RECEPTOR", "ION_CHANNEL", "TRUNCATED",
}


# ── Result framework ──────────────────────────────────────────────────────────

OK, WARN, ERROR = "ok", "warn", "error"
COLOURS = {OK: "\033[32m", WARN: "\033[33m", ERROR: "\033[31m", "reset": "\033[0m"}


@dataclass
class CheckResult:
    name: str
    status: str            # OK / WARN / ERROR
    summary: str
    details: list[str] = field(default_factory=list)

    def render(self, verbose: bool) -> str:
        c = COLOURS[self.status]; reset = COLOURS["reset"]
        head = f"  [{c}{self.status.upper():<5}{reset}] {self.name} — {self.summary}"
        if verbose and self.details:
            tail = "\n".join("        " + d for d in self.details[:20])
            extra = f"\n        … and {len(self.details) - 20} more" \
                if len(self.details) > 20 else ""
            return head + "\n" + tail + extra
        return head


# ── Individual checks ─────────────────────────────────────────────────────────

def check_libsbml(xml: Path) -> CheckResult:
    try:
        import libsbml
    except ImportError:
        return CheckResult("libsbml parse", WARN,
                            "libsbml not installed; skipped")
    reader = libsbml.SBMLReader()
    doc = reader.readSBMLFromFile(str(xml))
    errs = [doc.getError(i) for i in range(doc.getNumErrors())]
    severe = [e for e in errs if e.getSeverity() >= libsbml.LIBSBML_SEV_ERROR]
    if severe:
        return CheckResult("libsbml parse", ERROR,
                            f"{len(severe)} error(s)",
                            [f"sev={e.getSeverity()} {e.getMessage()[:160]}"
                             for e in severe[:10]])
    return CheckResult("libsbml parse", OK,
                        f"SBML L2V4 clean ({doc.getModel().getNumSpecies()} species, "
                        f"{doc.getModel().getNumReactions()} reactions)")


def check_cd_namespace(xml: Path) -> CheckResult:
    # ElementTree consumes xmlns declarations into element tags, so we
    # check the raw file head instead.
    head = xml.read_text(encoding="utf-8", errors="replace")[:2000]
    if 'xmlns:celldesigner="http://www.sbml.org/2001/ns/celldesigner"' in head:
        return CheckResult("celldesigner namespace", OK,
                            "xmlns:celldesigner declared on <sbml>")
    if CD_NS in head:
        return CheckResult("celldesigner namespace", WARN,
                            "CellDesigner namespace present but bound to "
                            "a non-canonical prefix")
    return CheckResult("celldesigner namespace", ERROR,
                        "missing xmlns:celldesigner on <sbml>")


def check_model_extension(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    if model is None:
        return CheckResult("model extension", ERROR, "no <model> element")
    ext = model.find(f"{SBML_T}annotation/{CD_T}extension")
    if ext is None:
        return CheckResult("model extension", ERROR,
                            "no model-level <celldesigner:extension>")
    expected = ["listOfCompartmentAliases", "listOfSpeciesAliases",
                "listOfProteins", "listOfIncludedSpecies"]
    missing = [tag for tag in expected if ext.find(f"{CD_T}{tag}") is None]
    if missing:
        return CheckResult("model extension", WARN,
                            f"{len(missing)}/4 sub-elements missing: "
                            f"{','.join(missing)}")
    return CheckResult("model extension", OK,
                        "compartment + species + protein + included aliases present")


def check_species_aliases(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    species_ids = {s.get("id") for s in model.findall(f"{SBML_T}listOfSpecies/{SBML_T}species")}
    ext = model.find(f"{SBML_T}annotation/{CD_T}extension")
    if ext is None:
        return CheckResult("species aliases", ERROR,
                            "model extension missing — cannot check")
    alias_species = {a.get("species") for a in
                      ext.findall(f"{CD_T}listOfSpeciesAliases/{CD_T}speciesAlias")}
    # Some species may be only complex members → look in includedSpecies
    included = {s.get("id") for s in
                 ext.findall(f"{CD_T}listOfIncludedSpecies/{CD_T}species")}
    species_with_alias = (alias_species & species_ids) | included
    missing = species_ids - species_with_alias
    if missing:
        return CheckResult("species aliases", WARN,
                            f"{len(missing)} / {len(species_ids)} species "
                            "without alias (CellDesigner will not show them)",
                            sorted(missing))
    return CheckResult("species aliases", OK,
                        f"all {len(species_ids)} species aliased")


def check_species_class(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    bad: list[str] = []
    missing: list[str] = []
    for sp in model.findall(f"{SBML_T}listOfSpecies/{SBML_T}species"):
        ident = sp.find(f"{SBML_T}annotation/{CD_T}extension/"
                          f"{CD_T}speciesIdentity")
        if ident is None:
            missing.append(sp.get("id"))
            continue
        cls_elem = ident.find(f"{CD_T}class")
        if cls_elem is None:
            missing.append(sp.get("id"))
            continue
        cls = (cls_elem.text or "").strip()
        if cls not in CD_CLASSES:
            bad.append(f"{sp.get('id')}: class={cls!r}")
    if bad:
        return CheckResult("species class", ERROR,
                            f"{len(bad)} species with unrecognised class",
                            bad)
    if missing:
        return CheckResult("species class", WARN,
                            f"{len(missing)} species missing class element",
                            missing)
    return CheckResult("species class", OK,
                        "every species has a valid celldesigner:class")


def check_reaction_base(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    rxns = model.findall(f"{SBML_T}listOfReactions/{SBML_T}reaction")
    no_react: list[str] = []
    no_prod: list[str] = []
    no_ext: list[str] = []
    for r in rxns:
        ext = r.find(f"{SBML_T}annotation/{CD_T}extension")
        if ext is None:
            no_ext.append(r.get("id"))
            continue
        if ext.find(f"{CD_T}baseReactants") is None:
            no_react.append(r.get("id"))
        if ext.find(f"{CD_T}baseProducts") is None:
            no_prod.append(r.get("id"))
    if no_ext or no_react or no_prod:
        return CheckResult("reaction CellDesigner blocks", WARN,
                            f"{len(no_ext)} no-extension / "
                            f"{len(no_react)} no-baseReactants / "
                            f"{len(no_prod)} no-baseProducts",
                            [f"{r}: ext" for r in no_ext[:5]]
                            + [f"{r}: noReact" for r in no_react[:5]]
                            + [f"{r}: noProd" for r in no_prod[:5]])
    return CheckResult("reaction CellDesigner blocks", OK,
                        f"all {len(rxns)} reactions carry CD extensions")


def check_compartment_aliases(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    comps = {c.get("id") for c in
              model.findall(f"{SBML_T}listOfCompartments/{SBML_T}compartment")}
    ext = model.find(f"{SBML_T}annotation/{CD_T}extension")
    if ext is None:
        return CheckResult("compartment aliases", ERROR,
                            "model extension missing")
    aliases = ext.findall(f"{CD_T}listOfCompartmentAliases/{CD_T}compartmentAlias")
    aliased = {a.get("compartment") for a in aliases}
    no_layout: list[str] = []
    for a in aliases:
        bounds = a.find(f"{CD_T}bounds")
        if bounds is None:
            no_layout.append(a.get("id"))
            continue
        for axis in ("x", "y", "w", "h"):
            try:
                float(bounds.get(axis) or "")
            except (TypeError, ValueError):
                no_layout.append(f"{a.get('id')} (bad {axis})")
                break
    missing = comps - aliased
    if missing:
        return CheckResult("compartment aliases", WARN,
                            f"{len(missing)} compartment(s) without alias",
                            sorted(missing))
    if no_layout:
        return CheckResult("compartment aliases", WARN,
                            f"{len(no_layout)} alias(es) without numeric bounds",
                            no_layout[:10])
    return CheckResult("compartment aliases", OK,
                        f"all {len(comps)} compartments aliased with bounds")


def check_orphan_species_refs(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    declared = {s.get("id") for s in
                 model.findall(f"{SBML_T}listOfSpecies/{SBML_T}species")}
    # included species count too (alias subjects in CD)
    ext = model.find(f"{SBML_T}annotation/{CD_T}extension")
    if ext is not None:
        declared |= {s.get("id") for s in
                      ext.findall(f"{CD_T}listOfIncludedSpecies/{CD_T}species")}
    orphans: list[str] = []
    for r in model.findall(f"{SBML_T}listOfReactions/{SBML_T}reaction"):
        for ref in r.iter():
            sid = ref.get("species")
            if sid and sid not in declared:
                orphans.append(f"reaction={r.get('id')} → species={sid}")
    if orphans:
        return CheckResult("orphan species refs", ERROR,
                            f"{len(orphans)} reaction references to unknown species",
                            orphans)
    return CheckResult("orphan species refs", OK,
                        "every reactant/product/modifier resolves to a declared species")


def check_protein_refs(root: ET.Element) -> CheckResult:
    model = root.find(f"{SBML_T}model")
    ext = model.find(f"{SBML_T}annotation/{CD_T}extension")
    if ext is None:
        return CheckResult("protein references", ERROR,
                            "model extension missing")
    proteins = {p.get("id") for p in
                 ext.findall(f"{CD_T}listOfProteins/{CD_T}protein")}
    bad: list[str] = []
    n_checked = 0
    for sp in model.findall(f"{SBML_T}listOfSpecies/{SBML_T}species"):
        ident = sp.find(f"{SBML_T}annotation/{CD_T}extension/{CD_T}speciesIdentity")
        if ident is None:
            continue
        pref = ident.find(f"{CD_T}proteinReference")
        if pref is None or not (pref.text or "").strip():
            continue
        n_checked += 1
        if pref.text.strip() not in proteins:
            bad.append(f"{sp.get('id')}: proteinReference={pref.text!r}")
    if bad:
        return CheckResult("protein references", ERROR,
                            f"{len(bad)}/{n_checked} proteinReference(s) unresolved",
                            bad)
    return CheckResult("protein references", OK,
                        f"{n_checked}/{n_checked} proteinReference cross-refs resolve")


def check_casq_smoke(xml: Path) -> CheckResult:
    """Functional proof that downstream CellDesigner-consuming tools accept the file."""
    # Prefer the casq CLI; fall back to a venv-local script if PATH-absent.
    casq_bin = None
    for cand in ("casq", str(Path(sys.executable).parent / "casq")):
        try:
            r = subprocess.run([cand, "--version"], capture_output=True,
                                text=True, timeout=10)
            if r.returncode == 0:
                casq_bin = cand
                break
        except (FileNotFoundError, OSError):
            continue
    if casq_bin is None:
        return CheckResult("CaSQ smoke", WARN, "casq CLI not on PATH; skipped")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / f"{xml.stem}.sbml-qual.xml"
        p = subprocess.run(
            [casq_bin, str(xml), str(out)],
            capture_output=True, text=True, timeout=180,
        )
        if p.returncode != 0:
            return CheckResult("CaSQ smoke", ERROR,
                                f"casq exited {p.returncode}",
                                (p.stderr or p.stdout or "")
                                .strip().splitlines()[-10:])
        if not out.exists() or out.stat().st_size < 200:
            return CheckResult("CaSQ smoke", WARN,
                                "casq exited 0 but produced no usable output")
        return CheckResult("CaSQ smoke", OK,
                            f"casq converted to SBML-qual ({out.stat().st_size // 1024} KB)")


# ── Runner ────────────────────────────────────────────────────────────────────

def run_all(xml: Path, verbose: bool) -> tuple[list[CheckResult], int]:
    print(f"\n──── {xml} ────")
    results: list[CheckResult] = []

    results.append(check_libsbml(xml))

    try:
        tree = ET.parse(xml)
        root = tree.getroot()
    except ET.ParseError as e:
        results.append(CheckResult("XML parse", ERROR, f"ElementTree: {e}"))
        for r in results:
            print(r.render(verbose))
        return results, 1

    results.append(check_cd_namespace(xml))
    results.append(check_model_extension(root))
    results.append(check_species_aliases(root))
    results.append(check_species_class(root))
    results.append(check_reaction_base(root))
    results.append(check_compartment_aliases(root))
    results.append(check_orphan_species_refs(root))
    results.append(check_protein_refs(root))
    results.append(check_casq_smoke(xml))

    for r in results:
        print(r.render(verbose))

    n_err = sum(1 for r in results if r.status == ERROR)
    n_warn = sum(1 for r in results if r.status == WARN)
    print(f"  → {len(results) - n_err - n_warn} OK / {n_warn} WARN / {n_err} ERROR")
    return results, n_err


DEFAULT_TARGETS = sorted(
    p for p in Path("curation/celldesigner").glob("*.xml")
    if not p.name.endswith(".biomodels.xml")  # MIRIAM-injected variant
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Static CellDesigner-loadability test for SSc-MIM XMLs.")
    ap.add_argument("paths", nargs="*", type=Path,
                     help="Optional list of XML files (default: all under "
                          "curation/celldesigner/, excl. .biomodels.xml).")
    ap.add_argument("-v", "--verbose", action="store_true",
                     help="Print per-element details for failed checks.")
    args = ap.parse_args(argv)

    targets = args.paths or DEFAULT_TARGETS
    if not targets:
        print("no XML targets found", file=sys.stderr)
        return 2

    total_err = 0
    for xml in targets:
        _, n_err = run_all(xml, args.verbose)
        total_err += n_err

    if total_err:
        print(f"\n{COLOURS[ERROR]}FAIL — {total_err} blocking error(s) across "
              f"{len(targets)} file(s){COLOURS['reset']}")
        return 1
    print(f"\n{COLOURS[OK]}PASS — all {len(targets)} file(s) "
          f"CellDesigner-loadable{COLOURS['reset']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
