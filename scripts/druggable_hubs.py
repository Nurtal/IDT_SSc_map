#!/usr/bin/env python3
"""Cross-reference SSc-MIM hubs with DGIdb drug-gene interactions.

Reads:
  - analysis/network/hubs.tsv             (top-20 hubs with module + hub_score)
  - curation/annotations/species_annotations.tsv (HGNC symbol per species)

For each hub, extract one or more canonical HGNC symbols (the script
walks complex names like SMAD3p_SMAD4 → [SMAD3, SMAD4]). Then query the
DGIdb v4 GraphQL endpoint for known drug-gene interactions.

Output: analysis/overlay/druggable_hubs.tsv
  columns: rank, hub_species, module, hgnc_symbol, hub_score, drug,
           drug_class, interaction_types, sources, score, ssc_context

Stdlib-only; network call required.

Known SSc-relevant drugs are added as a separate column flag based on a
small hard-coded mapping (anifrolumab, tocilizumab, rituximab,
nintedanib, pirfenidone, riociguat, bosentan, macitentan, sildenafil,
romilkimab, fresolimumab, dupilumab, belimumab, ruxolitinib,
tofacitinib, baricitinib).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path


DGIDB_GRAPHQL = "https://dgidb.org/api/graphql"
USER_AGENT = "SSc-MIM-druggable/0.1"

# Known SSc-trial drug *targets* — queried explicitly so the abstract's
# clinical shortlist appears even when the receptor isn't in the top-20
# hub list (which tends to be dominated by intracellular TFs).
SSC_TRIAL_TARGETS = [
    "IL6R", "IFNAR1", "IFNAR2", "IL4R", "IL13RA1", "EDNRA", "EDNRB",
    "PDGFRA", "PDGFRB", "TGFBR1", "MS4A1", "CD19", "CD20",
    "KDR", "NOTCH1", "NOTCH3", "TLR3", "TLR7", "TLR9", "TBK1",
    "TMEM173", "PDE5A", "NOS3", "GUCY1A1", "BTK",
    "STAT3", "STAT6", "TYK2", "BAFF",
]

SSC_RELEVANT_DRUGS = {
    "ANIFROLUMAB": "anti-IFNAR1 (anifrolumab) — SLE-approved, SSc trial rationale",
    "TOCILIZUMAB": "anti-IL6R (tocilizumab) — focuSSced trial (Khanna 2016, +FVC)",
    "SARILUMAB": "anti-IL6R (sarilumab) — exploratory",
    "RITUXIMAB": "anti-CD20 (rituximab) — RECITAL trial in SSc-ILD",
    "INEBILIZUMAB": "anti-CD19 — exploratory",
    "BELIMUMAB": "anti-BAFF — exploratory SSc",
    "DUPILUMAB": "anti-IL4Ra — Th2 axis repurposing",
    "ROMILKIMAB": "anti-IL13 — SSc skin trial",
    "FRESOLIMUMAB": "anti-TGFb1/2/3 — SSc skin trial",
    "NINTEDANIB": "PDGFR/FGFR/VEGFR inhibitor — SENSCIS SSc-ILD approved",
    "PIRFENIDONE": "anti-fibrotic (multifactorial) — LOTUSS / focuSSced add-on",
    "RIOCIGUAT": "sGC stimulator — RISE-SSc PAH",
    "BOSENTAN": "endothelin antagonist EDNRA/B — SSc digital ulcers",
    "MACITENTAN": "endothelin antagonist — PAH",
    "AMBRISENTAN": "endothelin antagonist — PAH",
    "SILDENAFIL": "PDE5 inhibitor — Raynaud / digital ulcers",
    "TADALAFIL": "PDE5 inhibitor — Raynaud",
    "ILOPROST": "prostacyclin analogue — Raynaud / PAH",
    "EPOPROSTENOL": "prostacyclin — PAH",
    "TREPROSTINIL": "prostacyclin — PAH",
    "SELEXIPAG": "IP receptor agonist — PAH",
    "TOFACITINIB": "JAK1/3 — SSc repurposing rationale",
    "BARICITINIB": "JAK1/2 — SSc repurposing",
    "RUXOLITINIB": "JAK1/2 — SSc repurposing",
    "PAMREVLUMAB": "anti-CTGF — fibrosis exploratory",
    "IBRUTINIB": "BTK inhibitor — B-cell axis repurposing",
}


# Translate complex / phospho-form ids into the canonical HGNC symbols
# they're composed of.
HGNC_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,8})\b")


def split_complex_to_hgnc(species_id: str, hgnc_index: set[str]) -> list[str]:
    """Best-effort decomposition of a species id into HGNC symbols.

    Strips compartment suffix (__xxx), strips leading p_ (phospho), strips
    isoform suffixes (_iso<N>), then matches alphanumeric tokens that look
    like HGNC symbols, optionally restricting to those in hgnc_index when
    that set is non-empty.
    """
    base = species_id.split("__", 1)[0]
    base = re.sub(r"^p_minus_|^p_|^phospho_", "", base)
    base = re.sub(r"_iso\d+$", "", base)
    base = re.sub(r"_repressed$|_active$|_dimer$|_complex$", "", base)
    # Replace common SSc-MIM separators with spaces
    base = base.replace("_x_", " ").replace("_minus_", "-").replace("_", " ")
    tokens = HGNC_RE.findall(base)
    if hgnc_index:
        tokens = [t for t in tokens if t in hgnc_index]
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def load_hgnc_index(tsv: Path) -> set[str]:
    """Build a set of HGNC symbols seen in species_annotations.tsv (col 2)."""
    if not tsv.exists():
        return set()
    out: set[str] = set()
    with tsv.open() as fh:
        next(fh)  # header
        for row in csv.reader(fh, delimiter="\t"):
            if len(row) >= 2 and row[1]:
                out.add(row[1])
    return out


def dgidb_query_single(symbol: str) -> list[dict]:
    """Query DGIdb GraphQL for interactions of a single symbol.

    DGIdb returns matched genes by `longName`, which doesn't trivially
    round-trip to the query symbol; querying one at a time keeps the
    mapping unambiguous.
    """
    query = """
    query Interactions($names: [String!]!) {
      genes(names: $names) {
        nodes {
          longName
          conceptId
          interactions {
            drug { name approved }
            interactionTypes { type }
            sources { sourceDbName }
            interactionScore
          }
        }
      }
    }"""
    body = json.dumps({
        "query": query,
        "variables": {"names": [symbol]},
    }).encode("utf-8")
    req = urllib.request.Request(
        DGIDB_GRAPHQL,
        data=body,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    nodes = (data.get("data", {}).get("genes", {}) or {}).get("nodes", []) or []
    out: list[dict] = []
    for node in nodes:
        out.extend(node.get("interactions") or [])
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hubs", type=Path, default=Path("analysis/network/hubs.tsv"))
    ap.add_argument(
        "--species-tsv",
        type=Path,
        default=Path("curation/annotations/species_annotations.tsv"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("analysis/overlay/druggable_hubs.tsv"),
    )
    args = ap.parse_args(argv[1:])

    if not args.hubs.exists():
        print(f"missing hubs file; run `make network` first: {args.hubs}", file=sys.stderr)
        return 2

    hubs: list[dict[str, str]] = []
    with args.hubs.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            hubs.append(row)

    if not hubs:
        print("no hubs found", file=sys.stderr)
        return 1

    hgnc_index = load_hgnc_index(args.species_tsv)
    print(f"loaded {len(hubs)} hubs; HGNC index has {len(hgnc_index)} symbols")

    # Map each hub to its decomposed HGNC symbols
    hub_symbols: dict[str, list[str]] = {}
    all_symbols: set[str] = set()
    for hub in hubs:
        sid = hub["species"]
        syms = split_complex_to_hgnc(sid, hgnc_index)
        # Always include the species' own primary HGNC (the "base" prefix)
        # when it looks like one and isn't already present.
        base = sid.split("__", 1)[0]
        if base.isupper() and "_" not in base and len(base) <= 12 and base not in syms:
            syms.insert(0, base)
        hub_symbols[sid] = syms
        all_symbols.update(syms)
    print(f"decomposed into {len(all_symbols)} unique HGNC symbols to query")

    # Also sweep the known SSc-trial drug targets — even if they're not in
    # the top-20 hub list, they're what a rheumatology audience expects to
    # see (IL6R/tocilizumab, IFNAR1/anifrolumab, etc.).
    query_set = set(all_symbols) | set(SSC_TRIAL_TARGETS)
    print(f"sweeping {len(query_set)} symbols ({len(SSC_TRIAL_TARGETS)} SSc-trial targets included)")

    # Query DGIdb per-symbol (avoids ambiguous many-to-many resolution)
    import time
    interactions_by_symbol: dict[str, list[dict]] = {}
    for i, sym in enumerate(sorted(query_set)):
        try:
            interactions_by_symbol[sym] = dgidb_query_single(sym)
            print(f"  [{i+1:2}/{len(query_set)}] {sym}: {len(interactions_by_symbol[sym])} interaction(s)")
        except Exception as exc:  # noqa: BLE001
            print(f"  [err] {sym}: {exc!r}", file=sys.stderr)
            interactions_by_symbol[sym] = []
        time.sleep(0.15)

    # Build the output rows
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_cols = [
        "rank", "hub_species", "module", "hub_score",
        "hgnc_symbol", "drug", "approved",
        "interaction_types", "sources", "score", "ssc_context",
    ]
    n_rows = 0
    n_ssc_relevant = 0
    with args.out.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(out_cols) + "\n")
        for hub in hubs:
            for sym in hub_symbols[hub["species"]]:
                inter = interactions_by_symbol.get(sym, [])
                if not inter:
                    fh.write("\t".join([
                        hub["rank"], hub["species"], hub["module"], hub["hub_score"],
                        sym, "", "", "", "", "", "",
                    ]) + "\n")
                    n_rows += 1
                    continue
                # Sort by interactionScore desc, take top 5 to keep the table tight
                inter_sorted = sorted(
                    inter,
                    key=lambda x: x.get("interactionScore") or 0,
                    reverse=True,
                )[:5]
                for it in inter_sorted:
                    drug = it.get("drug", {}) or {}
                    drug_name = (drug.get("name") or "").upper()
                    approved = "yes" if drug.get("approved") else "no"
                    itypes = ";".join(t.get("type", "") for t in (it.get("interactionTypes") or []))
                    sources = ";".join(s.get("sourceDbName", "") for s in (it.get("sources") or []))
                    score = str(it.get("interactionScore") or "")
                    ssc_ctx = SSC_RELEVANT_DRUGS.get(drug_name, "")
                    if ssc_ctx:
                        n_ssc_relevant += 1
                    fh.write("\t".join([
                        hub["rank"], hub["species"], hub["module"], hub["hub_score"],
                        sym, drug_name, approved, itypes, sources, score, ssc_ctx,
                    ]) + "\n")
                    n_rows += 1

        # Append the SSc-trial-target sweep rows separately (these may or
        # may not coincide with hub HGNCs).
        seen_pairs: set[tuple[str, str]] = set()
        for sym in SSC_TRIAL_TARGETS:
            for it in interactions_by_symbol.get(sym, []):
                drug = it.get("drug", {}) or {}
                drug_name = (drug.get("name") or "").upper()
                ctx = SSC_RELEVANT_DRUGS.get(drug_name, "")
                if not ctx:
                    continue
                key = (sym, drug_name)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                approved = "yes" if drug.get("approved") else "no"
                itypes = ";".join(t.get("type", "") for t in (it.get("interactionTypes") or []))
                sources = ";".join(s.get("sourceDbName", "") for s in (it.get("sources") or []))
                score = str(it.get("interactionScore") or "")
                fh.write("\t".join([
                    "ssc_target", f"target__{sym}", "-", "-",
                    sym, drug_name, approved, itypes, sources, score, ctx,
                ]) + "\n")
                n_rows += 1
                n_ssc_relevant += 1
    print(f"[ok] wrote {args.out}: {n_rows} rows; {n_ssc_relevant} flagged as SSc-relevant")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
