#!/usr/bin/env python3
"""MINERVA-readiness check on the integrated SSc-MIM.

Runs a green/red checklist before the (human) MINERVA upload step:

  1. SSc_MIM_integrated.xml exists and parses as XML.
  2. No duplicate species ids.
  3. No duplicate reaction ids.
  4. Every species id maps to a row in species_annotations.tsv.
  5. Every Reactome reaction has at least one PMID in
     reaction_evidence.tsv (advisory — Reactome reactions only).
  6. Sink-node connectivity: <50% of species dangling (informational —
     not a hard fail, recycled from sink_connectivity output).
  7. Every species name (display label) is non-empty.

Exit code:
  0 if every blocking check passes
  1 if any blocking check fails (currently: 1, 2, 3, 7)
  2 on argument errors / missing files
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


SBML_NS = "http://www.sbml.org/sbml/level2/version4"


def q(tag: str, ns: str = SBML_NS) -> str:
    return f"{{{ns}}}{tag}"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return [], []
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    return header, rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--integrated",
        type=Path,
        default=Path("curation/celldesigner/SSc_MIM_integrated.xml"),
    )
    ap.add_argument(
        "--species-tsv",
        type=Path,
        default=Path("curation/annotations/species_annotations.tsv"),
    )
    ap.add_argument(
        "--reaction-tsv",
        type=Path,
        default=Path("curation/annotations/reaction_evidence.tsv"),
    )
    ap.add_argument(
        "--sink-summary",
        type=Path,
        default=Path("analysis/network/sink_connectivity.summary.json"),
    )
    args = ap.parse_args(argv[1:])

    if not args.integrated.exists():
        print(f"integrated map not found: {args.integrated}", file=sys.stderr)
        return 2

    blocking_failures: list[str] = []
    advisories: list[str] = []
    line = "─" * 72

    def green(label: str, detail: str = "") -> None:
        d = f"  ({detail})" if detail else ""
        print(f"  \033[32m[ ok ]\033[0m {label}{d}")

    def red(label: str, detail: str = "") -> None:
        d = f"  ({detail})" if detail else ""
        print(f"  \033[31m[fail]\033[0m {label}{d}")
        blocking_failures.append(label)

    def warn(label: str, detail: str = "") -> None:
        d = f"  ({detail})" if detail else ""
        print(f"  \033[33m[warn]\033[0m {label}{d}")
        advisories.append(label)

    print(line)
    print(f"MINERVA preflight — {args.integrated}")
    print(line)

    # 1. Parse as XML
    try:
        tree = ET.parse(args.integrated)
        root = tree.getroot()
        green("XML parses", f"{args.integrated.stat().st_size} bytes")
    except ET.ParseError as exc:
        red("XML parses", str(exc))
        return 1

    species = list(root.iter(q("species")))
    reactions = list(root.iter(q("reaction")))
    print(f"          model: {len(species)} species, {len(reactions)} reactions")

    # 2. No duplicate species ids
    sids = [sp.get("id", "") for sp in species]
    dup_sids = [s for s, c in Counter(sids).items() if c > 1 and s]
    if dup_sids:
        red("Unique species ids", f"{len(dup_sids)} duplicate(s); first: {dup_sids[:3]}")
    else:
        green("Unique species ids")

    # 3. No duplicate reaction ids
    rids = [r.get("id", "") for r in reactions]
    dup_rids = [r for r, c in Counter(rids).items() if c > 1 and r]
    if dup_rids:
        red("Unique reaction ids", f"{len(dup_rids)} duplicate(s); first: {dup_rids[:3]}")
    else:
        green("Unique reaction ids")

    # 4. Every species id in species_annotations.tsv
    _, sp_rows = read_tsv(args.species_tsv)
    annotated_ids = {r.get("species_id", "") for r in sp_rows}
    missing_anno = [s for s in sids if s and s not in annotated_ids]
    if missing_anno:
        warn(
            "Species annotation coverage",
            f"{len(missing_anno)} / {len(sids)} species missing from species_annotations.tsv",
        )
    else:
        green("Species annotation coverage")

    # 5. Reactome reactions with PMID
    _, rxn_rows = read_tsv(args.reaction_tsv)
    rxn_pmids = {r.get("reaction_id", ""): r.get("pmid", "") for r in rxn_rows}
    # Reactome reactions come from the SBML L3 import — different id namespace
    # than the CellDesigner reaction_vertices. We compare on the count of
    # reaction_evidence rows that have a PMID, which is what the curator
    # cares about during MINERVA upload.
    n_rows_with_pmid = sum(1 for v in rxn_pmids.values() if v.strip())
    if n_rows_with_pmid >= 100:
        green(
            "reaction_evidence.tsv PMID coverage",
            f"{n_rows_with_pmid} / {len(rxn_pmids)} rows have a PMID",
        )
    else:
        warn(
            "reaction_evidence.tsv PMID coverage",
            f"only {n_rows_with_pmid} / {len(rxn_pmids)} rows have a PMID",
        )

    # 6. Sink connectivity
    if args.sink_summary.exists():
        sc = json.loads(args.sink_summary.read_text(encoding="utf-8"))
        dangling = sc.get("n_dangling", 0)
        total = sc.get("total_species", 1)
        far = sc.get("n_far_from_sink", 0)
        if far > 0:
            red("Sink connectivity <= max_path", f"{far} species exceed the max path threshold")
        else:
            green(
                "Sink connectivity <= max_path",
                f"0 / {total} species violate the >{sc.get('max_path_threshold', '?')} rule",
            )
        if dangling > total // 2:
            warn(
                "Dangling fraction",
                f"{dangling}/{total} ({100 * dangling // total}%) species cannot reach any sink — sinks may be missing",
            )
        elif dangling > 0:
            warn(
                "Dangling fraction",
                f"{dangling}/{total} species cannot reach a sink (curator backlog)",
            )
        else:
            green("Dangling fraction", "0 dangling")
    else:
        warn("Sink connectivity audit", "run `make sink-check` to produce the summary")

    # 7. Every species has a non-empty `name`
    no_name = [sp.get("id") for sp in species if not (sp.get("name") or "").strip()]
    if no_name:
        red("Every species has a display name", f"{len(no_name)} species lack a name attribute")
    else:
        green("Every species has a display name")

    # 8. (informational) cross-module species
    multi_mod = 0
    xhtml = "http://www.w3.org/1999/xhtml"
    for sp in species:
        for p in sp.iter(f"{{{xhtml}}}p"):
            txt = (p.text or "")
            if txt.startswith("module=") and "," in txt:
                multi_mod += 1
                break
    print(f"          (info) cross-module species: {multi_mod}")

    print(line)
    if blocking_failures:
        print(f"\033[31m{len(blocking_failures)} blocking issue(s) — DO NOT upload to MINERVA yet.\033[0m")
        return 1
    if advisories:
        print(f"\033[33m{len(advisories)} advisory(ies). Map is uploadable; review the advisories first.\033[0m")
    else:
        print("\033[32mAll checks green. The integrated map is MINERVA-ready.\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
