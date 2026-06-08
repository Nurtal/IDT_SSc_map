#!/usr/bin/env python3
"""Per-reaction Reactome-overlap (originality of the SSc-curated layer).

Answers the reviewer concern "is this just a cleaned-up Reactome copy?" with a measured
number: for each of the 85 SSc-curated reactions, does its directed gene→gene relationship
already exist in the Reactome-derived backbone? A reaction is **Reactome-novel** when none of
its (regulator/reactant gene → product gene) pairs co-occur, in the same direction, in any
backbone reaction.

Method: map every species to its HGNC symbol (`species_annotations.tsv`), parse the integrated
map, split reactions into Reactome-backbone (id not starting `ssc_`) vs SSc-curated, build the
set of directed gene pairs realised by the backbone, then test each SSc reaction's pairs
against it. Phenotype/complex/small-molecule nodes without an HGNC symbol are ignored for the
pairing (they are by definition not in Reactome's gene graph).

Outputs:
    analysis/network/reactome_novelty.tsv    per-SSc-reaction novelty + matched backbone pairs
    analysis/network/reactome_novelty.json   summary (overall + per module)

Run: python3 scripts/reactome_novelty.py  (or make reactome-novelty)
"""
from __future__ import annotations

import csv
import json
import re
from itertools import product
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / "curation/celldesigner/SSc_MIM_integrated.xml"
ANN = ROOT / "curation/annotations/species_annotations.tsv"
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
OUT = ROOT / "analysis/network"
NS = {"s": "http://www.sbml.org/sbml/level2/version4"}


def hgnc_map() -> dict[str, set[str]]:
    """species_id -> set of HGNC symbols (a complex species may map to several)."""
    m: dict[str, set[str]] = {}
    for r in csv.DictReader(ANN.open(), delimiter="\t"):
        sid = r["species_id"]
        sym = (r.get("hgnc_symbol", "") or "").strip()
        syms = set()
        if sym:
            syms.add(sym)
        # also split complex-style ids (SMAD3p_SMAD4__nuc -> SMAD3, SMAD4)
        base = sid.split("__", 1)[0]
        if not base.startswith("phenotype_"):
            for tok in re.split(r"[_:]", base):
                tok = tok.strip().rstrip("p")
                if re.match(r"^[A-Z][A-Z0-9]{1,6}$", tok):
                    syms.add(tok)
        if syms:
            m[sid] = syms
    return m


def reaction_genes(rxn, hg) -> tuple[set[str], set[str]]:
    """Return (input genes = reactants+modifiers, output genes = products)."""
    ins, outs = set(), set()
    for tag, bucket in (("listOfReactants", ins), ("listOfModifiers", ins),
                        ("listOfProducts", outs)):
        for sr in rxn.findall(f"s:{tag}/*", NS):
            bucket |= hg.get(sr.get("species"), set())
    return ins, outs


def main() -> None:
    hg = hgnc_map()
    root = ET.parse(XML).getroot()
    backbone_pairs: set[tuple[str, str]] = set()
    backbone_undirected: set[frozenset] = set()
    ssc_rxns = []
    for rxn in root.findall(".//s:reaction", NS):
        rid = rxn.get("id", "")
        ins, outs = reaction_genes(rxn, hg)
        if rid.startswith("ssc_"):
            ssc_rxns.append((rid, ins, outs))
        else:
            for a, b in product(ins, outs):
                if a != b:
                    backbone_pairs.add((a, b))
                    backbone_undirected.add(frozenset((a, b)))

    rows = []
    for rid, ins, outs in ssc_rxns:
        pairs = [(a, b) for a, b in product(ins, outs) if a != b]
        matched = [(a, b) for a, b in pairs if (a, b) in backbone_pairs]
        matched_undir = [(a, b) for a, b in pairs if frozenset((a, b)) in backbone_undirected]
        # novel = has gene pairs, none directionally in the backbone
        if not pairs:
            verdict = "no-gene-pair"  # phenotype/complex-only edge; not in Reactome by nature
        elif matched:
            verdict = "in-reactome"
        elif matched_undir:
            verdict = "reverse-only"  # same genes, opposite direction in Reactome
        else:
            verdict = "novel"
        rows.append({
            "reaction_id": rid,
            "module": rid.split("_")[1] if rid.startswith("ssc_") else "",
            "n_gene_pairs": len(pairs),
            "verdict": verdict,
            "matched_backbone_pairs": ";".join(f"{a}->{b}" for a, b in matched) or "",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "reactome_novelty.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    from collections import Counter
    dist = Counter(r["verdict"] for r in rows)
    # "absent from Reactome" = novel + reverse-only + no-gene-pair (none is a forward Reactome edge)
    not_in_reactome = sum(dist[k] for k in ("novel", "reverse-only", "no-gene-pair"))
    summary = {
        "n_ssc_reactions": n,
        "verdict_distribution": dict(dist),
        "n_with_no_forward_reactome_equivalent": not_in_reactome,
        "pct_no_reactome_equivalent": round(100 * not_in_reactome / n, 1),
        "n_strictly_novel_genes": dist.get("novel", 0),
        "pct_strictly_novel": round(100 * dist.get("novel", 0) / n, 1),
        "backbone_directed_gene_pairs": len(backbone_pairs),
        "headline": None,
    }
    summary["headline"] = (
        f"{not_in_reactome}/{n} ({summary['pct_no_reactome_equivalent']}%) of SSc-curated "
        f"reactions have no forward Reactome equivalent; {dist.get('novel',0)} encode gene "
        f"pairs absent from the Reactome backbone in either direction."
    )
    (OUT / "reactome_novelty.json").write_text(json.dumps(summary, indent=2))
    print("[reactome-novelty]", summary["headline"])
    print("[reactome-novelty] verdicts:", dict(dist))


if __name__ == "__main__":
    main()
