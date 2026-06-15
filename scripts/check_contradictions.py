#!/usr/bin/env python3
"""Flag contradictory SSc-curated interactions for human adjudication.

The edge-discovery pipeline grounds each interaction against one source independently; it does
NOT detect when two curated edges (from different sources) assert opposite signs on the same
directed gene pair. This script closes that gap: it does not delete anything — it surfaces
conflicts so the reviewer/co-author can arbitrate.

A conflict = the same directed gene pair (regulator -> target) is asserted with a *promoting*
type by one reaction and a *suppressing* type by another:
    PROMOTE  = activation, transcription, contributes, catalysis, phosphorylation
    SUPPRESS = inhibition, degradation
(binding / state_change / transport / dissociation are treated as sign-neutral and ignored.)

Outputs:
    analysis/curation/contradictions.tsv   one row per conflicting gene pair
Also exposes get_contradiction_flags() -> {reaction_id: "conflicts_with: ..."} for the DB builder.

Run: python3 scripts/check_contradictions.py   (or make check-contradictions)
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
OUT = ROOT / "analysis/curation/contradictions.tsv"

GENE_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
PROMOTE = {"activation", "transcription", "contributes", "catalysis", "phosphorylation"}
SUPPRESS = {"inhibition", "degradation"}


def genes(field: str) -> list[str]:
    out = []
    for chunk in re.split(r";", field or ""):
        base = chunk.split("__", 1)[0]
        if not base or base.startswith("phenotype_"):
            continue
        for tok in re.split(r"[_:]", base):
            tok = tok.strip().rstrip("p")
            if GENE_RE.match(tok) and tok not in out:
                out.append(tok)
    return out


def polarity(rxn_type: str) -> str:
    t = (rxn_type or "").strip()
    if t in PROMOTE:
        return "promote"
    if t in SUPPRESS:
        return "suppress"
    return "neutral"


def analyse() -> tuple[list[dict], dict[str, str]]:
    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    # directed gene pair -> {polarity -> [reaction_ids]}
    pairs: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        pol = polarity(r["type"])
        if pol == "neutral":
            continue
        regs = genes(r["reactants"]) + genes(r.get("modifiers", ""))
        tgts = genes(r["products"])
        for a, b in product(regs, tgts):
            if a != b:
                pairs[(a, b)][pol].append(r["reaction_id"])

    conflicts = []
    flags: dict[str, str] = {}
    for (a, b), pol in pairs.items():
        if pol.get("promote") and pol.get("suppress"):
            conflicts.append({
                "gene_pair": f"{a}->{b}",
                "promote_reactions": ";".join(sorted(set(pol["promote"]))),
                "suppress_reactions": ";".join(sorted(set(pol["suppress"]))),
            })
            for rid in set(pol["promote"]):
                flags[rid] = f"conflict on {a}->{b}: suppressed by {';'.join(sorted(set(pol['suppress'])))}"
            for rid in set(pol["suppress"]):
                flags[rid] = f"conflict on {a}->{b}: promoted by {';'.join(sorted(set(pol['promote'])))}"
    return conflicts, flags


def get_contradiction_flags() -> dict[str, str]:
    return analyse()[1]


def main() -> None:
    conflicts, flags = analyse()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["gene_pair", "promote_reactions", "suppress_reactions"],
                           delimiter="\t")
        w.writeheader()
        w.writerows(conflicts)
    print(f"[contradictions] {len(conflicts)} conflicting gene pair(s); "
          f"{len(flags)} reaction(s) flagged -> {OUT}")
    for c in conflicts:
        print(f"  {c['gene_pair']}: promote[{c['promote_reactions']}] vs suppress[{c['suppress_reactions']}]")
    if not conflicts:
        print("  (no sign contradictions among curated SSc interactions)")


if __name__ == "__main__":
    main()
