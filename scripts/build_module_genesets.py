#!/usr/bin/env python3
"""Freeze the five module gene sets before any validation cohort is seen (L2-01, issue #2).

Every L2 analysis reads `analysis/validation/module_genesets.tsv`; none re-derives
module membership. The artefact exists so that gene membership cannot be
adjusted after a result is known. Governed by
`docs/planning/external_validation_prespec.md` §2 (definition amended 2026-11-09,
see its §8).

Membership of module M (M1..M5) is the union of
  (a) every HGNC symbol whose species carries M among its comma-separated
      `module` labels in `curation/annotations/species_annotations.tsv`, and
  (b) every HGNC symbol of a species that is a reactant, product or modifier of
      a reaction whose `module` COLUMN is M in `curation/ssc_curated_reactions.tsv`.
The reaction ID is never read for membership: IDs predate the M4 -> M4/M5 split
and were not renumbered (e.g. `ssc_M4_011` is an M5 reaction).
(b) is what attaches the 64 Tier-1 species (labelled only `ssc_tier1` in the
annotations — COL1A1, POSTN, TMEM173, MB21D1, EDN1 …) to their module.
Reactions in the `crosstalk` column join no module by themselves; their
symbols are reported, and any left in no module is listed.

Detectability: a symbol is `detectable` when it is measured as a gene in the
frozen single-cell pseudobulk (`analysis/overlay/pseudobulk_multi.tsv`, run of
2026-06-26). Per-cohort testability is re-assessed against each cohort's
platform in L2-04; the floor below is applied there too.

Outputs (deterministic — no timestamps; input files identified by SHA-256):
  analysis/validation/module_genesets.tsv           module × symbol, long format
  analysis/validation/module_genesets_summary.json  counts, floor, testability,
                                                    pairwise overlap, provenance

Run:
    python3 scripts/build_module_genesets.py          # write the artefacts
    python3 scripts/build_module_genesets.py --check  # exit 1 if module membership would change
or  make genesets / make genesets-check
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "curation/annotations/species_annotations.tsv"
CURATED = ROOT / "curation/ssc_curated_reactions.tsv"
PSEUDOBULK = ROOT / "analysis/overlay/pseudobulk_multi.tsv"
OUT_DIR = ROOT / "analysis/validation"
OUT_TSV = OUT_DIR / "module_genesets.tsv"
OUT_JSON = OUT_DIR / "module_genesets_summary.json"

MODULES = ("M1", "M2", "M3", "M4", "M5")
CROSSTALK = "crosstalk"
# Annotation labels that are not modules and contribute to none.
NON_MODULE_LABELS = {"ssc_tier1", CROSSTALK, "?", ""}
# Pre-spec §2: fewer than this many detectable symbols -> not testable.
MIN_DETECTABLE = 10
REACTION_FIELDS = ("reactants", "products", "modifiers")
PSEUDOBULK_META = {"donor_id", "cell_type", "condition", "group", "dataset", "tissue", "lib_size"}

DEFINITION = (
    "union of (a) species_annotations `module` labels and (b) symbols of species in "
    "reactions whose ssc_curated_reactions `module` column names the module; reaction "
    "IDs are never read for membership"
)
DETECTABLE_DEFINITION = (
    "symbol measured as a gene in the frozen single-cell pseudobulk "
    "(analysis/overlay/pseudobulk_multi.tsv, run of 2026-06-26)"
)


class GenesetError(ValueError):
    """The inputs do not reconcile; the build must fail rather than emit."""


def _split(field: str | None, sep: str) -> list[str]:
    return [t.strip() for t in (field or "").split(sep) if t.strip()]


def build(
    annotations: list[dict],
    curated: list[dict],
    measured: set[str],
    floor: int = MIN_DETECTABLE,
) -> tuple[list[dict], dict]:
    """Return (long-format rows, summary). Raise GenesetError on any mismatch."""
    species_symbol: dict[str, str] = {}
    from_annotation: dict[str, set[str]] = {m: set() for m in MODULES}
    for row in annotations:
        sid = row["species_id"].strip()
        sym = (row.get("hgnc_symbol") or "").strip()
        species_symbol[sid] = sym
        for label in _split(row.get("module"), ","):
            if label in MODULES:
                if sym:
                    from_annotation[label].add(sym)
            elif label not in NON_MODULE_LABELS:
                raise GenesetError(f"species {sid}: unknown module label {label!r}")

    from_curated: dict[str, set[str]] = {m: set() for m in MODULES}
    crosstalk_symbols: set[str] = set()
    for row in curated:
        rid, module = row["reaction_id"], (row.get("module") or "").strip()
        if module not in MODULES and module != CROSSTALK:
            raise GenesetError(f"reaction {rid}: unknown module {module!r}")
        for field in REACTION_FIELDS:
            for sid in _split(row.get(field), ";"):
                if sid not in species_symbol:
                    raise GenesetError(f"reaction {rid}: species {sid} absent from annotations")
                sym = species_symbol[sid]
                if not sym:
                    continue  # metabolite, complex or state node: no gene to measure
                (crosstalk_symbols if module == CROSSTALK else from_curated[module]).add(sym)

    members = {m: from_annotation[m] | from_curated[m] for m in MODULES}

    # Reconciliation: both sources must be fully contained in the frozen set.
    for m in MODULES:
        for source, syms in (("annotation", from_annotation[m]), ("curated layer", from_curated[m])):
            missing = syms - members[m]
            if missing:
                raise GenesetError(f"{m}: {len(missing)} {source} symbols missing: {sorted(missing)}")

    in_modules: dict[str, list[str]] = {}
    for m in MODULES:
        for sym in members[m]:
            in_modules.setdefault(sym, []).append(m)

    rows = []
    for m in MODULES:
        for sym in sorted(members[m]):
            a, c = sym in from_annotation[m], sym in from_curated[m]
            rows.append({
                "module": m,
                "hgnc_symbol": sym,
                "source": "both" if a and c else ("annotation" if a else "curated_layer"),
                "detectable": "true" if sym in measured else "false",
                "other_modules": ",".join(x for x in in_modules[sym] if x != m),
            })

    per_module = {}
    for m in MODULES:
        detectable = sorted(s for s in members[m] if s in measured)
        per_module[m] = {
            "n_symbols": len(members[m]),
            "n_detectable": len(detectable),
            "n_from_annotation": len(from_annotation[m]),
            "n_from_curated_layer": len(from_curated[m]),
            "n_from_both": len(from_annotation[m] & from_curated[m]),
            "not_detectable": sorted(members[m] - set(detectable)),
            "testable": len(detectable) >= floor,
        }

    all_symbols = set(in_modules)
    summary = {
        "definition": DEFINITION,
        "detectable_definition": DETECTABLE_DEFINITION,
        "min_detectable_symbols": floor,
        "floor_rule": "a module with fewer detectable symbols than the floor is not testable "
                      "and is excluded from the multiple-testing family (pre-spec §2)",
        "modules": list(MODULES),
        "per_module": per_module,
        "not_testable": [m for m in MODULES if not per_module[m]["testable"]],
        "n_distinct_symbols": len(all_symbols),
        "n_distinct_detectable": len(all_symbols & measured),
        "pairwise_overlap": {
            f"{a}|{b}": len(members[a] & members[b]) for a, b in combinations(MODULES, 2)
        },
        "multi_module_symbols": {s: ms for s, ms in sorted(in_modules.items()) if len(ms) > 1},
        "crosstalk_symbols": sorted(crosstalk_symbols),
        "crosstalk_symbols_in_no_module": sorted(crosstalk_symbols - all_symbols),
    }
    return rows, summary


def _read_tsv(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def measured_symbols(pseudobulk: Path) -> set[str]:
    with pseudobulk.open() as fh:
        header = fh.readline().rstrip("\n").split("\t")
    return {c for c in header if c not in PSEUDOBULK_META}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict], summary: dict, inputs: dict[str, Path]) -> tuple[str, str]:
    cols = ["module", "hgnc_symbol", "source", "detectable", "other_modules"]
    tsv = "\t".join(cols) + "\n" + "".join("\t".join(r[c] for c in cols) + "\n" for r in rows)
    summary = dict(summary)
    summary["inputs"] = {
        str(p.relative_to(ROOT)): {"sha256": _sha256(p)} for p in inputs.values()
    }
    return tsv, json.dumps(summary, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed artefacts differ from a fresh build")
    args = ap.parse_args(argv)

    inputs = {"annotations": ANNOTATIONS, "curated": CURATED, "pseudobulk": PSEUDOBULK}
    try:
        rows, summary = build(_read_tsv(ANNOTATIONS), _read_tsv(CURATED), measured_symbols(PSEUDOBULK))
    except GenesetError as e:
        print(f"[FAIL] module gene sets do not reconcile: {e}", file=sys.stderr)
        return 1
    tsv, js = render(rows, summary, inputs)

    if args.check:
        # Membership is what is frozen. The recorded input hashes are the baseline's
        # provenance (tag prespec-baseline): an edit to an input that leaves every
        # module's membership unchanged (a note, a PMID) is not a change to the sets.
        def _sets_only(text: str) -> dict:
            d = json.loads(text)
            d.pop("inputs", None)
            return d
        stale = []
        if not OUT_TSV.exists() or OUT_TSV.read_text() != tsv:
            stale.append(OUT_TSV)
        if not OUT_JSON.exists() or _sets_only(OUT_JSON.read_text()) != _sets_only(js):
            stale.append(OUT_JSON)
        if stale:
            for p in stale:
                print(f"[FAIL] {p.relative_to(ROOT)} differs from a fresh build — the frozen "
                      "module gene sets no longer match the map. Changing them after the "
                      "baseline requires a dated amendment in the pre-spec §8.", file=sys.stderr)
            return 1
        print("[OK] frozen module gene sets match the map.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TSV.write_text(tsv)
    OUT_JSON.write_text(js)
    for m in MODULES:
        pm = summary["per_module"][m]
        flag = "" if pm["testable"] else "  NOT TESTABLE"
        print(f"  {m}: {pm['n_symbols']} symbols, {pm['n_detectable']} detectable{flag}")
    print(f"[OK] wrote {OUT_TSV.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
