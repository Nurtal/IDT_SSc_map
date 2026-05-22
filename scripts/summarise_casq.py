#!/usr/bin/env python3
"""E10 — Summarise the CaSQ Boolean network produced from SSc-MIM.

The full reachable-state-space simulation (MaBoSS / GINsim perturbation
matrix on the top-5 hubs) is descoped to a v2.0 follow-up paper per
the editor's E10 + roadmap T5 decision. What we report here is the
structural summary of the SBML-qual / .bnet output:

  - number of Boolean nodes
  - number of regulatory transitions
  - in-degree / out-degree distribution
  - top-5 most-regulated nodes (highest in-degree)
  - top-5 most-influential nodes (highest out-degree)
  - basic shape of attractor space (free vs constrained nodes)

This is enough to demonstrate that the SBGN-to-Boolean inference
*runs* on the full integrated XML, which is the v1.1 deliverable.

Output: `analysis/boolean/casq_summary.json`
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BNET = Path("analysis/boolean/SSc_MIM_integrated.bnet")
SIF  = Path("analysis/boolean/SSc_MIM_integrated.sif")
OUT  = Path("analysis/boolean/casq_summary.json")


def parse_bnet(path: Path):
    nodes: list[tuple[str, str]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("targets,"):
                continue
            if "," in line:
                tgt, rule = line.split(",", 1)
                nodes.append((tgt.strip(), rule.strip()))
    return nodes


def main() -> int:
    nodes = parse_bnet(BNET)
    n = len(nodes)

    # Naive in-degree estimate: count unique node names in the rule.
    # The .bnet rules use & and | combinators; treat any non-operator,
    # non-paren token as a node reference.
    OP = {"&", "|", "!", "(", ")"}
    node_names = {tgt for tgt, _ in nodes}

    in_degree: dict[str, int] = {}
    out_degree: dict[str, int] = {n: 0 for n in node_names}
    for tgt, rule in nodes:
        toks = re.findall(r"[A-Za-z0-9_]+", rule)
        regs = {t for t in toks if t in node_names and t != tgt}
        in_degree[tgt] = len(regs)
        for r in regs:
            out_degree[r] = out_degree.get(r, 0) + 1

    n_constant = sum(1 for tgt, rule in nodes
                     if rule.strip() == tgt.strip())  # self-only rules
    n_free = sum(1 for v in in_degree.values() if v == 0)
    n_regulated = n - n_free

    top_in = sorted(in_degree.items(), key=lambda x: -x[1])[:5]
    top_out = sorted(out_degree.items(), key=lambda x: -x[1])[:5]

    summary = {
        "casq_version": "1.4.4",
        "source": str(BNET),
        "n_boolean_nodes": n,
        "n_regulatory_transitions": sum(in_degree.values()),
        "n_constant_nodes_self_rule": n_constant,
        "n_free_nodes_zero_indegree": n_free,
        "n_regulated_nodes": n_regulated,
        "top_5_in_degree": [
            {"node": k, "in_degree": v} for k, v in top_in
        ],
        "top_5_out_degree": [
            {"node": k, "out_degree": v} for k, v in top_out
        ],
        "deferred_to_v2.0": (
            "Full perturbation-matrix simulation on the top-5 SSc-MIM "
            "hubs (NICD1, SMAD3p_SMAD4, fibroblast_proFibrotic, TGFB1, "
            "ISGF3) via MaBoSS or GINsim is descoped from this revision "
            "(editor's E10 / roadmap T5) and reserved for a v2.0 "
            "Boolean modelling paper. The SBML-qual emitted here is the "
            "input substrate for that future work."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"Boolean network summary:")
    print(f"  total nodes:                  {n}")
    print(f"  total regulatory inputs:      {sum(in_degree.values())}")
    print(f"  free nodes (no input):        {n_free}")
    print(f"  regulated nodes:              {n_regulated}")
    print(f"  constant (self-only rule):    {n_constant}")
    print()
    print("Top-5 by in-degree (most-regulated):")
    for n_, d in top_in:
        print(f"  {n_[:55]:<55s}  k_in={d}")
    print()
    print("Top-5 by out-degree (most-influential):")
    for n_, d in top_out:
        print(f"  {n_[:55]:<55s}  k_out={d}")
    print()
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
