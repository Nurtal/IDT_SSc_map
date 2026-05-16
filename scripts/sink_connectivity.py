#!/usr/bin/env python3
"""Sink-node connectivity audit on the integrated SSc-MIM.

Verifies the "every Tier-1 species reaches a sink in ≤ 6 steps" rule from
docs/scoping_notes.md. Sinks are looked up by id-prefix patterns matching
the four planned phenotype anchors:

  M1  ISG signature        — ISG_signature, IFI44*, ISG15, IFIT1, OAS_family,
                              MX_family, RSAD2
  M2  myofibroblast/ECM    — ACTA2, COL1A1, COL3A1, FN1, POSTN, COMP, CTGF
                              (most are SSc Tier-1 placeholders not yet
                               imported — flagged accordingly)
  M3  vascular remodelling — HIF1A, NOTCH1_Coactivator_Complex_*, NICD1
  M4  autoAb / Th2 output  — STAT3 (incl. complexes), STAT6, p_Y701_STAT1*

For every species, compute the shortest path length in the species
projection of the integrated map to the nearest sink. Report:

  - dangling species (no path to any sink)
  - far-from-sink species (path > 6)
  - per-module distance distribution

Outputs:
  analysis/network/sink_connectivity.tsv
  analysis/network/sink_connectivity.summary.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    import networkx as nx
except ImportError:
    print("networkx is required. Install with: pip install networkx", file=sys.stderr)
    sys.exit(2)


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
XHTML_NS = "http://www.w3.org/1999/xhtml"


SINK_PATTERNS: dict[str, list[str]] = {
    "M1_ISG_signature": ["ISG_signature__", "IFI44", "ISG15__", "IFIT1__", "IFIT3__",
                          "OAS_family__", "MX_family__", "RSAD2__", "IFI27__", "IFI6__",
                          "phenotype_ISG_signature"],
    "M2_ECM_myofibroblast": ["ACTA2__", "COL1A1__", "COL3A1__", "FN1__", "POSTN__",
                              "COMP__", "CTGF__", "CCN2__",
                              "phenotype_myofibroblast_activation", "phenotype_ECM_deposition"],
    "M3_vascular_remodelling": ["HIF1A__nuc", "NOTCH1_Coactivator_Complex_",
                                  "NICD1__", "phenotype_vascular_remodelling"],
    "M4_Th2_autoAb_output": ["STAT3__", "STAT6__",
                              "p_Y705_STAT3", "p_Y701_STAT1", "STAT1_STAT3__",
                              "phenotype_autoAb_production"],
}


def q(tag: str, ns: str = SBML_NS) -> str:
    return f"{{{ns}}}{tag}"


def species_module(sp: ET.Element) -> str:
    for p in sp.iter(f"{{{XHTML_NS}}}p"):
        if (p.text or "").startswith("module="):
            return p.text.split("=", 1)[1].strip()
    return "?"


def is_match(sid: str, patterns: list[str]) -> bool:
    return any(pat in sid for pat in patterns)


def build_species_projection(path: Path) -> tuple[nx.Graph, dict[str, str]]:
    """Undirected species projection: species ~ species if they share a reaction."""
    tree = ET.parse(path)
    root = tree.getroot()
    modules: dict[str, str] = {}
    species_ids: list[str] = []
    for sp in root.iter(q("species")):
        sid = sp.get("id") or ""
        if sid:
            species_ids.append(sid)
            modules[sid] = species_module(sp)

    g = nx.Graph()
    g.add_nodes_from(species_ids)

    for rxn in root.iter(q("reaction")):
        parts: set[str] = set()
        for lt in ("listOfReactants", "listOfProducts", "listOfModifiers"):
            ll = rxn.find(q(lt))
            if ll is None:
                continue
            for sr in ll:
                sid = sr.get("species") or ""
                if sid:
                    parts.add(sid)
        # connect every pair in this reaction
        plist = list(parts)
        for i in range(len(plist)):
            for j in range(i + 1, len(plist)):
                g.add_edge(plist[i], plist[j])
    return g, modules


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--integrated",
        type=Path,
        default=Path("curation/celldesigner/SSc_MIM_integrated.xml"),
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("analysis/network"),
    )
    ap.add_argument(
        "--max-path",
        type=int,
        default=6,
        help="threshold path length (per scoping_notes.md)",
    )
    args = ap.parse_args(argv[1:])
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading {args.integrated} …")
    g, modules = build_species_projection(args.integrated)
    print(f"  species projection: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")

    # Identify sinks
    sinks_by_sink: dict[str, list[str]] = {}
    for sink_name, patterns in SINK_PATTERNS.items():
        sinks_by_sink[sink_name] = [s for s in g.nodes() if is_match(s, patterns)]
        print(f"  sink '{sink_name}': {len(sinks_by_sink[sink_name])} candidate node(s)")
    all_sinks = {s for lst in sinks_by_sink.values() for s in lst}
    if not all_sinks:
        print("no sink nodes detected — check SINK_PATTERNS", file=sys.stderr)
        return 1

    # For each species: shortest distance to nearest sink (within each sink group)
    print("computing shortest paths …")
    rows: list[dict[str, str]] = []
    distances_per_module: dict[str, list[int]] = {}
    dangling: list[str] = []
    far: list[str] = []
    for sid in sorted(g.nodes()):
        per_sink: dict[str, int] = {}
        for sink_name, sink_nodes in sinks_by_sink.items():
            best = None
            for sk in sink_nodes:
                if sk == sid:
                    best = 0
                    break
                try:
                    d = nx.shortest_path_length(g, sid, sk)
                except nx.NetworkXNoPath:
                    continue
                except nx.NodeNotFound:
                    continue
                if best is None or d < best:
                    best = d
            per_sink[sink_name] = best if best is not None else -1

        # Overall nearest sink (any of the four)
        finite = [d for d in per_sink.values() if d >= 0]
        nearest = min(finite) if finite else -1

        mod = modules.get(sid, "?")
        distances_per_module.setdefault(mod, []).append(nearest)
        if nearest < 0:
            dangling.append(sid)
        elif nearest > args.max_path:
            far.append(sid)

        rows.append({
            "species_id": sid,
            "module": mod,
            "nearest_sink_distance": str(nearest),
            "to_M1_ISG_signature": str(per_sink["M1_ISG_signature"]),
            "to_M2_ECM_myofibroblast": str(per_sink["M2_ECM_myofibroblast"]),
            "to_M3_vascular_remodelling": str(per_sink["M3_vascular_remodelling"]),
            "to_M4_Th2_autoAb_output": str(per_sink["M4_Th2_autoAb_output"]),
            "is_sink": "yes" if sid in all_sinks else "no",
        })

    # Write TSV
    tsv = args.out_dir / "sink_connectivity.tsv"
    cols = ["species_id", "module", "nearest_sink_distance",
            "to_M1_ISG_signature", "to_M2_ECM_myofibroblast",
            "to_M3_vascular_remodelling", "to_M4_Th2_autoAb_output", "is_sink"]
    with tsv.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(r[c] for c in cols) + "\n")
    print(f"  wrote {tsv}")

    # Summary
    summary = {
        "integrated_xml": str(args.integrated),
        "total_species": len(rows),
        "max_path_threshold": args.max_path,
        "n_dangling": len(dangling),
        "n_far_from_sink": len(far),
        "sinks_detected_per_anchor": {k: len(v) for k, v in sinks_by_sink.items()},
        "distance_distribution_per_module": {
            mod: {
                "n": len(ds),
                "median": statistics.median([d for d in ds if d >= 0]) if any(d >= 0 for d in ds) else None,
                "max": max([d for d in ds if d >= 0], default=None),
                "dangling": sum(1 for d in ds if d < 0),
            }
            for mod, ds in distances_per_module.items()
        },
        "dangling_sample": dangling[:25],
        "far_from_sink_sample": far[:25],
    }
    summary_path = args.out_dir / "sink_connectivity.summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  wrote {summary_path}")

    print()
    print(f"--- summary ---")
    print(f"  total species:     {len(rows)}")
    print(f"  dangling (no sink reachable): {len(dangling)}")
    print(f"  far from sink (> {args.max_path}): {len(far)}")
    print(f"  per-module distance to nearest sink:")
    for mod, ds in sorted(distances_per_module.items()):
        finite = [d for d in ds if d >= 0]
        median = statistics.median(finite) if finite else "n/a"
        mx = max(finite) if finite else "n/a"
        print(f"    {mod}: n={len(ds)}  median={median}  max={mx}  dangling={sum(1 for d in ds if d < 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
