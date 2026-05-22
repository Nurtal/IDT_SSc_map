#!/usr/bin/env python3
"""E19 — Figure 1 quadrant layout (R1-figures).

Re-renders the global SSc-MIM view with modules in fixed quadrants:

      M1 (IFN-I)     |     M2 (TGF-β / fibrosis)
                     |
   ──────────────────●──────────────────  ← sinks centred
                     |
      M4 (IL-6 Th2)  |     M3 (EndoMT / vasculopathy)

Inter-module crosstalk edges are drawn as curved arcs to keep the
quadrant boundaries visually crisp. SSc-Tier-1 species are placed in
a thin ring around the sinks at the centre because they couple to
multiple modules.

Output:
  figures/F1_global_MIM_quadrant.svg / .png

To regenerate:
  make f1-quadrant
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Patch
import networkx as nx
import numpy as np

INTEGRATED = Path("curation/celldesigner/SSc_MIM_integrated.xml")
OUT_SVG = Path("figures/F1_global_MIM_quadrant.svg")
OUT_PNG = Path("figures/F1_global_MIM_quadrant.png")
SBML_NS = "http://www.sbml.org/sbml/level2/version4"
XHTML_NS = "http://www.w3.org/1999/xhtml"

MODULE_COLOURS = {
    "M1": "#1f77b4",  # blue
    "M2": "#d62728",  # red
    "M3": "#2ca02c",  # green
    "M4": "#9467bd",  # purple
    "ssc_tier1": "#ff7f0e",  # orange
    "?": "#cccccc",
}

# Quadrant centres in plot coordinates. Origin at (0, 0); each quadrant
# occupies a 2×2 box. Sinks are centred on (0, 0).
QUADRANT_CENTRE = {
    "M1": (-1.5, +1.5),
    "M2": (+1.5, +1.5),
    "M3": (+1.5, -1.5),
    "M4": (-1.5, -1.5),
    "ssc_tier1": (0.0, 0.0),
    "sink": (0.0, 0.0),
    "?": (0.0, +2.5),
}
QUADRANT_RADIUS = 1.1


def primary_module(token: str) -> str:
    parts = [p.strip() for p in token.split(",") if p.strip()]
    if not parts:
        return "?"
    pri = parts[0]
    if pri in MODULE_COLOURS or pri in ("sink", "crosstalk"):
        return pri
    return "?"


def is_sink(name: str) -> bool:
    return name.startswith("phenotype_")


def load_graph(xml: Path) -> tuple[nx.Graph, dict[str, str]]:
    tree = ET.parse(xml)
    root = tree.getroot()
    species_modules: dict[str, str] = {}
    g = nx.Graph()
    for sp in root.iter(f"{{{SBML_NS}}}species"):
        sid = sp.get("id") or ""
        mod = "?"
        for p in sp.iter(f"{{{XHTML_NS}}}p"):
            if (p.text or "").startswith("module="):
                mod = primary_module(p.text.split("=", 1)[1])
                break
        species_modules[sid] = mod
        g.add_node(sid, module=mod)
    for rxn in root.iter(f"{{{SBML_NS}}}reaction"):
        parts: set[str] = set()
        for lt in ("listOfReactants", "listOfProducts", "listOfModifiers"):
            ll = rxn.find(f"{{{SBML_NS}}}{lt}")
            if ll is None:
                continue
            for sr in ll:
                sid = sr.get("species") or ""
                if sid:
                    parts.add(sid)
        plist = list(parts)
        for i in range(len(plist)):
            for j in range(i + 1, len(plist)):
                g.add_edge(plist[i], plist[j])
    return g, species_modules


def quadrant_layout(g: nx.Graph) -> dict[str, tuple[float, float]]:
    """Per-module spring layout, translated to the module's quadrant centre."""
    pos: dict[str, tuple[float, float]] = {}
    by_module: dict[str, list[str]] = {}
    for n, d in g.nodes(data=True):
        mod = d.get("module", "?")
        if is_sink(n):
            mod = "sink"
        elif mod not in MODULE_COLOURS:
            mod = "?"
        by_module.setdefault(mod, []).append(n)

    rng = np.random.default_rng(42)
    for mod, members in by_module.items():
        cx, cy = QUADRANT_CENTRE.get(mod, (0.0, 0.0))
        if not members:
            continue
        # Sub-graph spring layout
        sub = g.subgraph(members).copy()
        sub_pos = nx.spring_layout(sub, seed=42, k=0.25,
                                   iterations=80)
        # Re-centre + clip to a unit disk within the quadrant
        coords = np.array(list(sub_pos.values()))
        if len(coords) > 0:
            coords = coords - coords.mean(axis=0)
            scale = QUADRANT_RADIUS / max(0.001, np.max(np.abs(coords)))
            coords = coords * scale
            # tiny jitter so we don't overplot
            coords = coords + rng.normal(0, 0.02, coords.shape)
        for n, (x, y) in zip(sub_pos.keys(), coords):
            pos[n] = (cx + x, cy + y)
    return pos


def main() -> int:
    g, species_modules = load_graph(INTEGRATED)
    # Drop dangling singletons for the visual
    iso = [n for n in g.nodes() if g.degree(n) == 0]
    g.remove_nodes_from(iso)

    pos = quadrant_layout(g)

    fig, ax = plt.subplots(figsize=(13, 11), dpi=110)
    ax.set_title(
        "Figure 1 — SSc-MIM global view (quadrant layout)\n"
        f"{g.number_of_nodes()} species · {g.number_of_edges()} edges · "
        "modules in fixed positions · phenotype sinks centred · "
        "inter-module edges shown as curved arcs",
        loc="left", fontsize=10,
    )

    # Classify edges by whether they cross module boundaries
    intra_edges, inter_edges = [], []
    for u, v in g.edges():
        m_u = "sink" if is_sink(u) else g.nodes[u].get("module", "?")
        m_v = "sink" if is_sink(v) else g.nodes[v].get("module", "?")
        if m_u == m_v:
            intra_edges.append((u, v))
        else:
            inter_edges.append((u, v, m_u, m_v))

    # Intra-quadrant edges: low-contrast straight lines
    nx.draw_networkx_edges(g, pos, edgelist=intra_edges,
                            ax=ax, alpha=0.10, width=0.35,
                            edge_color="#666")

    # Inter-quadrant ("crosstalk") edges: curved arcs in dark grey
    for u, v, m_u, m_v in inter_edges:
        if u not in pos or v not in pos:
            continue
        x0, y0 = pos[u]; x1, y1 = pos[v]
        arrow = FancyArrowPatch((x0, y0), (x1, y1),
                                 connectionstyle="arc3,rad=0.25",
                                 arrowstyle="-",
                                 alpha=0.20, lw=0.4, color="#333",
                                 zorder=1)
        ax.add_patch(arrow)

    # Plot nodes by module
    for mod in ["M1", "M2", "M3", "M4", "ssc_tier1", "?"]:
        nodes = [n for n in g.nodes()
                 if g.nodes[n].get("module") == mod and not is_sink(n)]
        if not nodes:
            continue
        xs = [pos[n][0] for n in nodes if n in pos]
        ys = [pos[n][1] for n in nodes if n in pos]
        ax.scatter(xs, ys, c=MODULE_COLOURS[mod], s=18,
                    alpha=0.75, edgecolor="white", linewidth=0.4,
                    zorder=2)

    # Sinks: large diamonds at the centre
    sinks = [n for n in g.nodes() if is_sink(n)]
    sx = [pos[n][0] for n in sinks if n in pos]
    sy = [pos[n][1] for n in sinks if n in pos]
    ax.scatter(sx, sy, marker="D", s=240, c="#222",
                edgecolor="white", linewidth=0.9, zorder=4,
                label="sink phenotype")
    for n in sinks:
        if n not in pos: continue
        x, y = pos[n]
        label = (n.replace("phenotype_", "")
                  .replace("__cell", "")
                  .replace("__ext", "")
                  .replace("__ecm", "")
                  .replace("_", " "))
        ax.annotate(label, (x, y), textcoords="offset points",
                     xytext=(0, 12), ha="center", fontsize=9,
                     weight="bold", color="#000",
                     bbox=dict(boxstyle="round,pad=0.2", fc="white",
                                ec="black", alpha=0.85, lw=0.5),
                     zorder=5)

    # Quadrant labels in corners
    quadrant_titles = {
        (-1.5, +2.7): ("M1 — Type-I IFN / cGAS-STING", "M1"),
        (+1.5, +2.7): ("M2 — TGF-β / fibroblast→myofibroblast", "M2"),
        (-1.5, -2.7): ("M4 — IL-6 / Th2 / B-cell", "M4"),
        (+1.5, -2.7): ("M3 — EndoMT / vasculopathy", "M3"),
    }
    for (qx, qy), (label, mod) in quadrant_titles.items():
        ax.text(qx, qy, label, ha="center", va="center",
                fontsize=11, fontweight="bold",
                color=MODULE_COLOURS[mod],
                bbox=dict(boxstyle="round,pad=0.4", fc="white",
                          ec=MODULE_COLOURS[mod], lw=1.5, alpha=0.92))

    # Quadrant separators (very faint)
    ax.axhline(0, color="#aaa", lw=0.6, ls=":", alpha=0.5, zorder=0)
    ax.axvline(0, color="#aaa", lw=0.6, ls=":", alpha=0.5, zorder=0)

    # Legend
    legend = [
        Patch(color=MODULE_COLOURS["M1"], label="M1 IFN-I"),
        Patch(color=MODULE_COLOURS["M2"], label="M2 TGF-β / fibrosis"),
        Patch(color=MODULE_COLOURS["M3"], label="M3 EndoMT / vasculopathy"),
        Patch(color=MODULE_COLOURS["M4"], label="M4 IL-6 / Th2 / B-cell"),
        Patch(color=MODULE_COLOURS["ssc_tier1"], label="SSc Tier-1 (multi-module)"),
        Patch(color="#222", label="sink phenotype (centred)"),
    ]
    ax.legend(handles=legend, loc="lower left", fontsize=8,
              frameon=True, framealpha=0.95)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_axis_off()
    plt.tight_layout()

    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_SVG, format="svg", bbox_inches="tight")
    fig.savefig(OUT_PNG, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_SVG} + {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
