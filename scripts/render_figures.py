#!/usr/bin/env python3
"""Render preview versions of figures F2 (overlay heatmap) and F3 (hubs).

F3 is built from real data already on disk:
  - analysis/network/hubs.tsv             (top-20 hubs)
  - analysis/network/centrality.tsv       (degree, betweenness)
  - curation/celldesigner/SSc_MIM_integrated.xml (edges)
  -> node-link plot of the hub subnetwork, coloured by module.

F2 is a *placeholder* until the omics overlay lands in Phase 4. It uses
mock per-patient × per-module scores derived from the integrated map's
module structure (uniform random) — enough to show the figure's layout
and axis labels to a reviewer at the kickoff meeting.

Outputs (SVG + 300-dpi PNG) under figures/.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import matplotlib

matplotlib.use("Agg")  # non-interactive
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

try:
    import networkx as nx
except ImportError:
    print("networkx required: pip install networkx", file=sys.stderr)
    sys.exit(2)


MODULE_COLOURS = {
    "M1": "#2c7fb8",  # blue
    "M2": "#d7191c",  # red
    "M3": "#1a9641",  # green
    "M4": "#fdae61",  # orange
    "?":  "#999999",
}


SBML_NS = "http://www.sbml.org/sbml/level2/version4"


def q(tag: str) -> str:
    return f"{{{SBML_NS}}}{tag}"


def primary_module(label: str) -> str:
    """Module annotation may be 'M1,M2' for cross-import species; pick the first."""
    return (label or "?").split(",", 1)[0]


def build_neighbor_graph(integrated: Path, focal: set[str]) -> nx.Graph:
    """Return an undirected species-projection subgraph for `focal` plus their
    immediate neighbours (one-hop)."""
    tree = ET.parse(integrated)
    root = tree.getroot()
    g = nx.Graph()
    species_modules: dict[str, str] = {}
    xhtml = "http://www.w3.org/1999/xhtml"
    for sp in root.iter(q("species")):
        sid = sp.get("id") or ""
        mod = "?"
        for p in sp.iter(f"{{{xhtml}}}p"):
            if (p.text or "").startswith("module="):
                mod = primary_module(p.text.split("=", 1)[1])
                break
        species_modules[sid] = mod

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
        plist = list(parts)
        for i in range(len(plist)):
            for j in range(i + 1, len(plist)):
                g.add_edge(plist[i], plist[j])
    for n in g.nodes():
        g.nodes[n]["module"] = species_modules.get(n, "?")

    # Subgraph: focal + 1-hop neighbours
    keep: set[str] = set(focal)
    for f in focal:
        if f in g:
            keep.update(g.neighbors(f))
    return g.subgraph(keep).copy()


def short_label(sid: str, max_len: int = 14) -> str:
    base = sid.split("__", 1)[0]
    return base[:max_len] + "…" if len(base) > max_len else base


def render_f3(
    hubs_tsv: Path,
    integrated: Path,
    out_svg: Path,
    out_png: Path,
) -> None:
    hubs: list[tuple[str, str, float, int]] = []
    with hubs_tsv.open() as fh:
        next(fh)  # header
        for row in csv.reader(fh, delimiter="\t"):
            if len(row) < 6:
                continue
            _, sp, mod, score, deg, _btw = row[:6]
            hubs.append((sp, mod, float(score), int(deg)))

    focal_ids = {h[0] for h in hubs}
    g = build_neighbor_graph(integrated, focal_ids)
    pos = nx.spring_layout(g, seed=42, k=0.65, iterations=80)

    fig, ax = plt.subplots(figsize=(11, 8), dpi=100)
    ax.set_title(
        "F3 (preview) — top-20 hub subnetwork in SSc-MIM\n"
        "  size ∝ hub_score · colour = source module",
        loc="left",
        fontsize=11,
    )

    nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.25, width=0.6)

    # Plot hub nodes prominently
    hub_xs = [pos[h[0]][0] for h in hubs if h[0] in pos]
    hub_ys = [pos[h[0]][1] for h in hubs if h[0] in pos]
    hub_colours = [MODULE_COLOURS.get(primary_module(h[1]), "#999") for h in hubs if h[0] in pos]
    hub_sizes = [max(50, 300 + 60 * h[2]) for h in hubs if h[0] in pos]
    ax.scatter(hub_xs, hub_ys, c=hub_colours, s=hub_sizes, edgecolor="black", linewidth=0.7, zorder=3)

    # Plot neighbour nodes as smaller dots
    hub_set = {h[0] for h in hubs}
    other = [n for n in g.nodes() if n not in hub_set]
    other_xs = [pos[n][0] for n in other]
    other_ys = [pos[n][1] for n in other]
    other_cols = [MODULE_COLOURS.get(primary_module(g.nodes[n].get("module", "?")), "#999") for n in other]
    ax.scatter(other_xs, other_ys, c=other_cols, s=22, edgecolor="white", linewidth=0.4, alpha=0.65, zorder=2)

    # Labels on hubs only
    for sp, _mod, _score, _deg in hubs:
        if sp in pos:
            x, y = pos[sp]
            ax.annotate(
                short_label(sp),
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=7.5,
                weight="bold",
            )

    legend = [
        Patch(color=MODULE_COLOURS["M1"], label="M1 IFN-I"),
        Patch(color=MODULE_COLOURS["M2"], label="M2 TGF-β / fibrosis"),
        Patch(color=MODULE_COLOURS["M3"], label="M3 EndoMT / vasculopathy"),
        Patch(color=MODULE_COLOURS["M4"], label="M4 IL-6 / Th2 / B-cell"),
    ]
    ax.legend(handles=legend, loc="lower left", fontsize=8, frameon=True)
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(out_svg, format="svg")
    fig.savefig(out_png, format="png", dpi=300)
    plt.close(fig)
    print(f"  [ok] {out_svg}")
    print(f"  [ok] {out_png}")


def render_f2_placeholder(out_svg: Path, out_png: Path) -> None:
    """A placeholder heatmap that shows the planned F2 layout and axes.
    Replaced with real per-donor module scores when Phase 4 overlay lands."""
    rng = random.Random(0)
    n_donors = 12
    modules = ["M1 IFN-I", "M2 TGFβ / fibrosis", "M3 EndoMT / vasc.", "M4 IL-6 / Th2 / B-cell"]
    data = [[rng.gauss(0, 1) for _ in modules] for _ in range(n_donors)]

    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=100)
    im = ax.imshow(data, aspect="auto", cmap="RdBu_r", vmin=-2.5, vmax=2.5)
    ax.set_xticks(range(len(modules)))
    ax.set_xticklabels(modules, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(range(n_donors))
    ax.set_yticklabels([f"donor_{i+1:02d}" for i in range(n_donors)], fontsize=8)
    ax.set_title(
        "F2 (PLACEHOLDER) — per-donor SSc-MIM module activation scores\n"
        "  (mock data; replaced with real overlay when Phase 4 runs)",
        loc="left",
        fontsize=11,
    )
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("module score (z)", fontsize=8)
    # Watermark
    ax.text(
        0.5,
        0.5,
        "PLACEHOLDER",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=46,
        color="white",
        weight="bold",
        alpha=0.18,
        rotation=20,
    )
    plt.tight_layout()
    fig.savefig(out_svg, format="svg")
    fig.savefig(out_png, format="png", dpi=300)
    plt.close(fig)
    print(f"  [ok] {out_svg}")
    print(f"  [ok] {out_png}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hubs", type=Path, default=Path("analysis/network/hubs.tsv"))
    ap.add_argument(
        "--integrated",
        type=Path,
        default=Path("curation/celldesigner/SSc_MIM_integrated.xml"),
    )
    ap.add_argument("--out-dir", type=Path, default=Path("figures"))
    args = ap.parse_args(argv[1:])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"rendering F3 (hub subnetwork) …")
    render_f3(
        args.hubs,
        args.integrated,
        args.out_dir / "F3_druggable_targets.svg",
        args.out_dir / "F3_druggable_targets.png",
    )
    print(f"rendering F2 (placeholder heatmap) …")
    render_f2_placeholder(
        args.out_dir / "F2_overlay_by_subtype.svg",
        args.out_dir / "F2_overlay_by_subtype.png",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
