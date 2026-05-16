#!/usr/bin/env python3
"""Network analysis of the integrated SSc-MIM.

Loads curation/celldesigner/SSc_MIM_integrated.xml as a directed bipartite
graph (species <-> reaction nodes) and computes:

  - Per-species degree, betweenness, closeness, PageRank.
  - Top-20 "hubs" by combined rank (degree + betweenness, z-score sum).
  - Community detection via greedy modularity (NetworkX built-in;
    Louvain via python-louvain would need an extra dep). Compare detected
    communities to the four hand-defined modules from species notes.

Outputs:
  analysis/network/centrality.tsv     # one row per species
  analysis/network/hubs.tsv           # top-20 hubs
  analysis/network/communities.tsv    # one row per species: detected community + manual module
  analysis/network/summary.json       # global graph statistics

Requires: networkx (pip install networkx).
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
    print(
        "networkx is required. Install with: pip install networkx\n"
        "(Or activate the sscmim conda env from environment.yml.)",
        file=sys.stderr,
    )
    sys.exit(2)


SBML_NS = "http://www.sbml.org/sbml/level2/version4"
XHTML_NS = "http://www.w3.org/1999/xhtml"


def q(tag: str, ns: str = SBML_NS) -> str:
    return f"{{{ns}}}{tag}"


def species_module(sp: ET.Element) -> str:
    for p in sp.iter(f"{{{XHTML_NS}}}p"):
        if (p.text or "").startswith("module="):
            return p.text.split("=", 1)[1].strip()
    return "?"


def build_graph(integrated_xml: Path) -> tuple[nx.DiGraph, dict[str, str]]:
    """Build a directed graph: species -> reaction -> species.

    Returns (graph, species_module_map).
    """
    tree = ET.parse(integrated_xml)
    root = tree.getroot()

    species_modules: dict[str, str] = {}
    for sp in root.iter(q("species")):
        sid = sp.get("id") or ""
        species_modules[sid] = species_module(sp)

    g = nx.DiGraph()
    for sid in species_modules:
        g.add_node(sid, kind="species", module=species_modules[sid])

    for rxn in root.iter(q("reaction")):
        rid = rxn.get("id") or ""
        g.add_node(rid, kind="reaction")
        # reactants -> reaction
        lor = rxn.find(q("listOfReactants"))
        if lor is not None:
            for sr in lor.findall(q("speciesReference")):
                sp = sr.get("species") or ""
                if sp:
                    g.add_edge(sp, rid)
        # reaction -> products
        lop = rxn.find(q("listOfProducts"))
        if lop is not None:
            for sr in lop.findall(q("speciesReference")):
                sp = sr.get("species") or ""
                if sp:
                    g.add_edge(rid, sp)
        # modifiers act on the reaction as bidirectional context
        lom = rxn.find(q("listOfModifiers"))
        if lom is not None:
            for ms in lom.findall(q("modifierSpeciesReference")):
                sp = ms.get("species") or ""
                if sp:
                    g.add_edge(sp, rid)

    return g, species_modules


def species_projection(g: nx.DiGraph) -> nx.DiGraph:
    """Project the bipartite graph to species-only (species i -> species j
    if there exists a reaction r with i -> r -> j)."""
    proj = nx.DiGraph()
    for n, data in g.nodes(data=True):
        if data.get("kind") == "species":
            proj.add_node(n, **data)
    for r, data in g.nodes(data=True):
        if data.get("kind") != "reaction":
            continue
        preds = list(g.predecessors(r))
        succs = list(g.successors(r))
        for p in preds:
            for s in succs:
                if p != s:
                    proj.add_edge(p, s)
    return proj


def zscore(values: list[float]) -> list[float]:
    if not values:
        return []
    mu = statistics.fmean(values)
    sigma = statistics.pstdev(values) or 1.0
    return [(v - mu) / sigma for v in values]


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
    args = ap.parse_args(argv[1:])

    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading {args.integrated} …")
    g, modules = build_graph(args.integrated)
    n_species = sum(1 for _, d in g.nodes(data=True) if d.get("kind") == "species")
    n_reactions = sum(1 for _, d in g.nodes(data=True) if d.get("kind") == "reaction")
    print(f"  bipartite graph: {n_species} species, {n_reactions} reactions, "
          f"{g.number_of_edges()} edges")

    proj = species_projection(g)
    print(f"  species projection: {proj.number_of_nodes()} nodes, "
          f"{proj.number_of_edges()} edges")

    # ---- Centrality on the species projection ----------------------------
    print("computing centrality …")
    deg = dict(proj.degree())
    in_deg = dict(proj.in_degree())
    out_deg = dict(proj.out_degree())
    # Betweenness on the undirected projection — directed gives many zeroes
    undirected = proj.to_undirected()
    btw = nx.betweenness_centrality(undirected)
    cls = nx.closeness_centrality(undirected)
    try:
        pr = nx.pagerank(proj, alpha=0.85, max_iter=200)
    except nx.PowerIterationFailedConvergence:
        pr = {n: 0.0 for n in proj.nodes()}

    species_ids = sorted(proj.nodes())
    deg_vals = [float(deg[s]) for s in species_ids]
    btw_vals = [btw[s] for s in species_ids]
    z_deg = dict(zip(species_ids, zscore(deg_vals)))
    z_btw = dict(zip(species_ids, zscore(btw_vals)))
    hub_score = {s: z_deg[s] + z_btw[s] for s in species_ids}

    # centrality.tsv
    cent_path = args.out_dir / "centrality.tsv"
    with cent_path.open("w", encoding="utf-8") as fh:
        fh.write("species\tmodule\tdegree\tin_degree\tout_degree\t"
                 "betweenness\tcloseness\tpagerank\thub_score\n")
        for s in species_ids:
            fh.write("\t".join([
                s, modules.get(s, "?"),
                str(deg[s]), str(in_deg[s]), str(out_deg[s]),
                f"{btw[s]:.6f}", f"{cls[s]:.6f}", f"{pr[s]:.6f}",
                f"{hub_score[s]:.4f}",
            ]) + "\n")
    print(f"  wrote {cent_path}")

    # hubs.tsv — top-20 by hub_score, skipping cofactors
    COFACTORS = {"ATP", "ADP", "GTP", "GDP", "H2O", "Pi", "PPi", "AMP", "GMP"}
    def is_cofactor(sid: str) -> bool:
        # ID format: "<name>__<comp_short>"; check the name part
        base = sid.split("__", 1)[0]
        return base in COFACTORS

    hubs = sorted(
        ((s, hub_score[s]) for s in species_ids if not is_cofactor(s)),
        key=lambda x: x[1],
        reverse=True,
    )[:20]
    hubs_path = args.out_dir / "hubs.tsv"
    with hubs_path.open("w", encoding="utf-8") as fh:
        fh.write("rank\tspecies\tmodule\thub_score\tdegree\tbetweenness\n")
        for i, (s, score) in enumerate(hubs, 1):
            fh.write(f"{i}\t{s}\t{modules.get(s,'?')}\t{score:.4f}\t{deg[s]}\t{btw[s]:.6f}\n")
    print(f"  wrote {hubs_path}")

    # ---- Communities (greedy modularity) --------------------------------
    print("detecting communities …")
    try:
        comm_iter = nx.community.greedy_modularity_communities(undirected)
        communities = [set(c) for c in comm_iter]
    except Exception as exc:  # noqa: BLE001
        print(f"  community detection failed: {exc!r}; using one cluster")
        communities = [set(species_ids)]
    print(f"  detected {len(communities)} communities")

    comm_of: dict[str, int] = {}
    for ci, c in enumerate(communities):
        for s in c:
            comm_of[s] = ci

    comm_path = args.out_dir / "communities.tsv"
    with comm_path.open("w", encoding="utf-8") as fh:
        fh.write("species\tdetected_community\tmanual_module\n")
        for s in species_ids:
            fh.write(f"{s}\t{comm_of.get(s, -1)}\t{modules.get(s, '?')}\n")
    print(f"  wrote {comm_path}")

    # Community vs module contingency
    contingency: dict[tuple[int, str], int] = {}
    for s in species_ids:
        key = (comm_of.get(s, -1), modules.get(s, "?"))
        contingency[key] = contingency.get(key, 0) + 1

    summary = {
        "integrated_xml": str(args.integrated),
        "bipartite_graph": {
            "n_species": n_species,
            "n_reactions": n_reactions,
            "n_edges": g.number_of_edges(),
        },
        "species_projection": {
            "n_nodes": proj.number_of_nodes(),
            "n_edges": proj.number_of_edges(),
            "n_weakly_connected_components": nx.number_weakly_connected_components(proj),
            "avg_in_degree": statistics.fmean(in_deg.values()) if in_deg else 0,
            "avg_out_degree": statistics.fmean(out_deg.values()) if out_deg else 0,
        },
        "communities": {
            "count": len(communities),
            "sizes": sorted([len(c) for c in communities], reverse=True),
        },
        "community_module_contingency": {
            f"comm{ci}__{mod}": n for (ci, mod), n in sorted(contingency.items())
        },
        "top_hubs": [
            {"species": s, "module": modules.get(s, "?"), "hub_score": round(score, 4)}
            for s, score in hubs
        ],
    }
    summary_path = args.out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  wrote {summary_path}")

    print()
    print("--- top 10 hubs (excluding cofactors) ---")
    for i, (s, score) in enumerate(hubs[:10], 1):
        print(f"  {i:2d}. {s:35} module={modules.get(s,'?'):8} score={score:6.2f} deg={deg[s]}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
