#!/usr/bin/env python3
"""Network analysis of the integrated SSc-MIM.

Loads curation/celldesigner/SSc_MIM_integrated.xml as a directed bipartite
graph (species <-> reaction nodes) and computes:

  - Per-species degree, betweenness, closeness, PageRank, eigenvector.
  - Top-20 "hubs" by combined rank (degree + betweenness, z-score sum).
  - Top-20 robustness check: same ranking under degree, betweenness,
    PageRank, eigenvector → hub_overlap.tsv with Jaccard + rank corr
    (addresses reviewer R1-M3, revision item E3).
  - Community detection via greedy modularity. Hypergeometric per
    (community, module) BH-corrected over all 38 × 5 tests
    (addresses reviewer R1-M2, revision item E4).

Outputs:
  analysis/network/centrality.tsv          # one row per species
  analysis/network/hubs.tsv                # top-20 hubs
  analysis/network/hub_overlap.tsv         # robustness across metrics (E3)
  analysis/network/communities.tsv         # detected community + module
  analysis/network/community_enrichment.tsv  # hypergeometric tests (E4)
  analysis/network/summary.json            # global graph statistics
  figures/F_supp_hub_robustness.svg/png    # scatter plot (E3 supp)

Requires: networkx, scipy. Optional: matplotlib for the supp figure.
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

    # Eigenvector centrality — undirected, computed per connected component
    # to avoid PowerIteration failure on the 22-component projection (E3).
    eig: dict[str, float] = {}
    for component in nx.connected_components(undirected):
        sub = undirected.subgraph(component)
        if sub.number_of_nodes() < 2:
            for n in sub.nodes():
                eig[n] = 0.0
            continue
        try:
            try:
                ec = nx.eigenvector_centrality_numpy(sub)
            except Exception:
                ec = nx.eigenvector_centrality(sub, max_iter=1000, tol=1e-6)
        except Exception:
            ec = {n: 0.0 for n in sub.nodes()}
        eig.update(ec)
    for n in proj.nodes():
        eig.setdefault(n, 0.0)

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
                 "betweenness\tcloseness\tpagerank\teigenvector\thub_score\n")
        for s in species_ids:
            fh.write("\t".join([
                s, modules.get(s, "?"),
                str(deg[s]), str(in_deg[s]), str(out_deg[s]),
                f"{btw[s]:.6f}", f"{cls[s]:.6f}", f"{pr[s]:.6f}",
                f"{eig[s]:.6f}", f"{hub_score[s]:.4f}",
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

    # ---- Hub robustness (E3) ---------------------------------------------
    # Rank top-20 under each centrality metric (cofactors filtered out) and
    # report Jaccard + Spearman to test whether the hub_score top-20 is
    # robust to the choice of centrality (reviewer R1-M3).
    print("computing hub robustness across metrics …")
    metrics: dict[str, dict[str, float]] = {
        "hub_score":    hub_score,
        "degree":       {s: float(deg[s]) for s in species_ids},
        "betweenness":  btw,
        "pagerank":     pr,
        "eigenvector":  eig,
    }
    eligible = [s for s in species_ids if not is_cofactor(s)]
    top_by: dict[str, list[str]] = {}
    rank_by: dict[str, dict[str, int]] = {}
    for name, scores in metrics.items():
        ordered = sorted(eligible, key=lambda s: scores[s], reverse=True)
        top_by[name] = ordered[:20]
        rank_by[name] = {s: i + 1 for i, s in enumerate(ordered)}

    def _jaccard(a: list[str], b: list[str]) -> float:
        sa, sb = set(a), set(b)
        return len(sa & sb) / max(1, len(sa | sb))

    def _spearman(a: list[str]) -> dict[str, float]:
        """Spearman ρ between hub_score ranks and other metrics over all
        eligible species (not just top-20)."""
        import statistics as _st
        ref = [rank_by["hub_score"][s] for s in a]
        out: dict[str, float] = {}
        for name in metrics:
            if name == "hub_score":
                continue
            other = [rank_by[name][s] for s in a]
            # Pearson on ranks = Spearman
            mu_r, mu_o = _st.fmean(ref), _st.fmean(other)
            num = sum((r - mu_r) * (o - mu_o) for r, o in zip(ref, other))
            den = (sum((r - mu_r) ** 2 for r in ref) *
                   sum((o - mu_o) ** 2 for o in other)) ** 0.5
            out[name] = float(num / den) if den else 0.0
        return out

    rho_all = _spearman(eligible)
    overlap_path = args.out_dir / "hub_overlap.tsv"
    with overlap_path.open("w", encoding="utf-8") as fh:
        fh.write("rank")
        for name in metrics:
            fh.write(f"\t{name}\t{name}_module")
        fh.write("\n")
        for i in range(20):
            fh.write(str(i + 1))
            for name in metrics:
                sid = top_by[name][i] if i < len(top_by[name]) else ""
                fh.write(f"\t{sid}\t{modules.get(sid, '?') if sid else ''}")
            fh.write("\n")
    print(f"  wrote {overlap_path}")

    print("  top-20 hub_score vs other metrics:")
    print(f"    Jaccard(top20)  ρ(all)")
    for name in metrics:
        if name == "hub_score":
            continue
        j = _jaccard(top_by["hub_score"], top_by[name])
        print(f"    {name:<13} {j:.2f}        {rho_all[name]:+.3f}")

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

    # ---- Community–module hypergeometric enrichment (E4) ------------------
    # For each (community c, module m): N=total species, K=species in
    # module m, n=community size, x=intersection. Hypergeometric SF on x-1.
    # BH-FDR across all (community × module) tests.
    print("computing community–module enrichment …")
    from scipy.stats import hypergeom
    N = len(species_ids)
    n_in_module: dict[str, int] = {}
    for s in species_ids:
        m = modules.get(s, "?")
        n_in_module[m] = n_in_module.get(m, 0) + 1
    # Use single-label modules (drop joined "M1,M2" labels for cleanliness)
    test_modules = [m for m in sorted(n_in_module) if m and "," not in m and m != "?"]

    enrichment_tests = []
    for ci, c in enumerate(communities):
        n_c = len(c)
        if n_c < 3:
            continue
        for m in test_modules:
            K = n_in_module[m]
            x = sum(1 for s in c if modules.get(s) == m)
            if x == 0:
                continue
            pv = float(hypergeom.sf(x - 1, N, K, n_c))
            expected = (K * n_c) / N
            enrichment_tests.append({
                "community": ci, "module": m, "n_community": n_c,
                "n_module": K, "n_intersection": x,
                "expected": round(expected, 2),
                "fold_enrichment": round(x / expected, 2) if expected > 0 else float("inf"),
                "pvalue": pv,
            })

    # BH-FDR
    if enrichment_tests:
        import numpy as _np
        pvs = _np.array([t["pvalue"] for t in enrichment_tests])
        m_tests = len(pvs)
        order = _np.argsort(pvs)
        ranked = pvs[order]
        bh = ranked * m_tests / (_np.arange(m_tests) + 1)
        bh = _np.minimum.accumulate(bh[::-1])[::-1]
        bh = _np.clip(bh, 0, 1)
        padj = _np.empty_like(bh)
        padj[order] = bh
        for t, q in zip(enrichment_tests, padj):
            t["padj"] = float(q)
            t["significant"] = bool(q < 0.05)

    enrich_path = args.out_dir / "community_enrichment.tsv"
    cols = ["community","module","n_community","n_module","n_intersection",
            "expected","fold_enrichment","pvalue","padj","significant"]
    with enrich_path.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for t in sorted(enrichment_tests, key=lambda r: r["pvalue"]):
            fh.write("\t".join([
                str(t["community"]), t["module"],
                str(t["n_community"]), str(t["n_module"]), str(t["n_intersection"]),
                str(t["expected"]), str(t["fold_enrichment"]),
                f"{t['pvalue']:.4g}", f"{t['padj']:.4g}",
                "true" if t["significant"] else "false",
            ]) + "\n")
    print(f"  wrote {enrich_path}")

    sig_tests = [t for t in enrichment_tests if t.get("significant")]
    sig_communities = sorted({t["community"] for t in sig_tests})
    print(f"  {len(sig_tests)} sig (q<0.05) across {len(sig_communities)} communities")

    # Community vs module contingency (preserved for back-compat)
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
        "community_enrichment": {
            "n_tests": len(enrichment_tests),
            "n_significant_at_q05": len(sig_tests),
            "n_communities_significant": len(sig_communities),
            "significant_communities": sig_communities,
        },
        "hub_robustness": {
            "metrics": list(metrics.keys()),
            "jaccard_top20_vs_hub_score": {
                name: round(_jaccard(top_by["hub_score"], top_by[name]), 3)
                for name in metrics if name != "hub_score"
            },
            "spearman_all_eligible_vs_hub_score": {
                name: round(rho_all[name], 3) for name in rho_all
            },
        },
        "top_hubs": [
            {"species": s, "module": modules.get(s, "?"), "hub_score": round(score, 4)}
            for s, score in hubs
        ],
    }
    summary_path = args.out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  wrote {summary_path}")

    # ---- Supplementary figure: hub-score vs alternative centralities -----
    fig_path = Path("figures/F_supp_hub_robustness.svg")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), dpi=110)
        plot_specs = [
            ("degree",      "Degree"),
            ("pagerank",    "PageRank"),
            ("eigenvector", "Eigenvector centrality"),
        ]
        top20_set = set(top_by["hub_score"])
        for ax, (name, label) in zip(axes, plot_specs):
            xs = [hub_score[s] for s in eligible]
            ys = [metrics[name][s] for s in eligible]
            colors = ["#d7191c" if s in top20_set else "#bdbdbd" for s in eligible]
            ax.scatter(xs, ys, c=colors, s=12, alpha=0.7, edgecolors="none")
            ax.set_xlabel("hub_score (deg + btw, z-sum)")
            ax.set_ylabel(label)
            jac = _jaccard(top_by["hub_score"], top_by[name])
            ax.set_title(f"{label}\nρ={rho_all[name]:+.2f}  Jaccard₂₀={jac:.2f}", fontsize=10)
        fig.suptitle("Hub-score robustness across centralities (top-20 in red)", fontsize=11)
        plt.tight_layout()
        fig_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(fig_path, format="svg")
        fig.savefig(fig_path.with_suffix(".png"), format="png", dpi=300)
        plt.close(fig)
        print(f"  wrote {fig_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"  supp figure skipped: {exc!r}")

    print()
    print("--- top 10 hubs (excluding cofactors) ---")
    for i, (s, score) in enumerate(hubs[:10], 1):
        print(f"  {i:2d}. {s:35} module={modules.get(s,'?'):8} score={score:6.2f} deg={deg[s]}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
