#!/usr/bin/env python3
"""Analysis B — genetic support for the module structure (issue #18).

Governed by `docs/planning/external_validation_prespec.md` §4. Germline
association cannot be a consequence of disease state, so this axis is
orthogonal to the transcriptomic one. Adapter only: it fetches and parses the
GWAS Catalog snapshot; the record shape and BH adjustment are validation_core's.

Trait: systemic sclerosis, resolved in EFO to MONDO_0005100, plus its
hierarchical descendants in EFO (OLS, 2026-11-10). Associations with
p <= 5e-8 only; genes = mapped genes and author-reported genes as deposited,
resolved to current approved HGNC symbols, protein-coding only.

Tests (hypergeometric, over-representation; BH across the five modules):
  primary     each module vs the protein-coding universe;
  control     each module vs the within-map universe (all map symbols), so an
              enrichment that only reflects "the map is made of well-studied
              immune genes" does not survive; plus the Reactome-backbone
              symbols vs the protein-coding universe, as a reference level.
Secondary source (DisGeNET) is reported separately, never merged; it now
requires authenticated API access and is recorded as not executed.

Run:
    python3 scripts/validate_genetic_support.py --fetch   # snapshot GWAS Catalog into data/raw/gwas/
    python3 scripts/validate_genetic_support.py           # analyse the snapshot
    python3 scripts/validate_genetic_support.py --check   # exit 1 if the output would change
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

from scipy.stats import hypergeom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import screen_cohorts as sc  # noqa: E402
import validation_core as vc  # noqa: E402

SNAPSHOT = ROOT / "data/raw/gwas/gwas_catalog_ssc_associations.json"
ANNOTATIONS = ROOT / "curation/annotations/species_annotations.tsv"
OUT = ROOT / "analysis/validation/genetic_support.json"
API = "https://www.ebi.ac.uk/gwas/rest/api/v2"
MODULES = ("M1", "M2", "M3", "M4", "M5")
GWS = 5e-8

TRAITS = {  # resolved 2026-11-10: EFO/OLS hierarchicalDescendants of MONDO_0005100
    "MONDO_0005100": "systemic sclerosis",
    "MONDO_0005019": "diffuse scleroderma",
    "MONDO_0016358": "limited cutaneous systemic sclerosis",
    "EFO_1001017": "limited scleroderma",
    "EFO_0008536": "anti-centromere-antibody-positive systemic scleroderma",
    "EFO_0008537": "anti-topoisomerase-I-antibody-positive systemic scleroderma",
}

# Pre-spec §4.5, verbatim (registered 2026-09-10). "expect_significant": what the
# prediction implies for padj <= 0.05 in the primary test (None = either outcome).
PREDICTIONS = {
    "M1": {"prediction": "strong", "expect_significant": True},
    "M5": {"prediction": "strong", "expect_significant": True},
    "M4": {"prediction": "weak to moderate", "expect_significant": None},
    "M2": {"prediction": "absent or weak", "expect_significant": False},
    "M3": {"prediction": "absent or weak", "expect_significant": False},
}

NON_INDEPENDENCE = (
    "Partly non-independent: the curated layer was built from SSc literature, some of it genetic, so a "
    "locus can be in the map because it was a GWAS hit (pre-spec §4.4). Mitigated, not removed, by the "
    "within-map control and by reading the per-module pattern rather than the global overlap."
)


# ── fetch (network) ────────────────────────────────────────────────────────────

def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ssc-mim-genetic-support"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001 - transient EBI errors; retried
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch() -> None:
    associations = {}
    for efo in TRAITS:
        page = 0
        while True:
            d = _get(f"{API}/associations?efo_id={efo}&size=100&page={page}")
            for a in d.get("_embedded", {}).get("associations", []):
                associations[a["association_id"]] = a
            if page + 1 >= d["page"]["totalPages"]:
                break
            page += 1
    for aid, a in associations.items():
        if a.get("p_value") is not None and a["p_value"] <= GWS:
            loci = _get(f"{API}/associations/{aid}/loci").get("_embedded", {}).get("loci", [])
            a["author_reported_genes"] = sorted({g["gene_name"] for l in loci
                                                 for g in (l.get("author_reported_genes") or [])
                                                 if g.get("gene_name")})
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps({
        "source": API, "downloaded": time.strftime("%Y-%m-%d"), "traits": TRAITS,
        "associations": [associations[k] for k in sorted(associations)],
    }, indent=1, sort_keys=True))


# ── analysis (offline) ─────────────────────────────────────────────────────────

def gwas_genes(snapshot: dict, hgnc: sc.Hgnc, protein_coding: set[str]) -> dict[str, list[str]]:
    """{approved protein-coding symbol: [association accession ids]} at p <= 5e-8."""
    out: dict[str, set[str]] = {}
    for a in snapshot["associations"]:
        if a.get("p_value") is None or a["p_value"] > GWS:
            continue
        if not {t["efo_id"] for t in a.get("efo_traits", [])} & set(TRAITS):
            continue
        for g in set(a.get("mapped_genes") or []) | set(a.get("author_reported_genes") or []):
            for part in str(g).replace(";", ",").split(","):
                sym = hgnc.current(part.strip())
                if sym in protein_coding:
                    out.setdefault(sym, set()).add(a["accession_id"])
    return {k: sorted(v) for k, v in sorted(out.items())}


def protein_coding_universe() -> set[str]:
    with sc.HGNC.open(newline="") as fh:
        return {r["symbol"] for r in csv.DictReader(fh, delimiter="\t")
                if r.get("status") == "Approved" and r.get("locus_group") == "protein-coding gene"}


def backbone_symbols(hgnc: sc.Hgnc) -> set[str]:
    with ANNOTATIONS.open() as fh:
        return {hgnc.map_symbol(r["hgnc_symbol"].strip()) for r in csv.DictReader(fh, delimiter="\t")
                if r["hgnc_symbol"].strip() and "imported from" in (r.get("notes") or "")}


def enrichment(members: set[str], hits: set[str], universe: set[str]) -> dict:
    m = members & universe
    N, K, n = len(universe), len(hits & universe), len(m)
    x = len(m & hits)
    expected = K * n / N if N else 0.0
    return {"n_universe": N, "n_gwas_in_universe": K, "n_members": n, "n_overlap": x,
            "expected": round(expected, 3), "fold": round(x / expected, 3) if expected else None,
            "p": float(hypergeom.sf(x - 1, N, K, n)) if x else 1.0,
            "overlap_genes": sorted(m & hits)}


def run() -> dict:
    snap = json.loads(SNAPSHOT.read_text())
    hgnc = sc.Hgnc(sc.HGNC)
    pc = protein_coding_universe()
    gw = gwas_genes(snap, hgnc, pc)
    hits = set(gw)
    sets = {m: {hgnc.map_symbol(s) for s in v} for m, v in sc.frozen_genesets().items()}
    map_symbols = set().union(*sets.values())

    out = {}
    for label, universe in (("primary_protein_coding", pc), ("control_within_map", map_symbols & pc)):
        results = []
        for m in MODULES:
            e = enrichment(sets[m], hits, universe)
            r = vc.Result(module=m, source=f"GWAS Catalog | {label}", testable=True,
                          n_detectable=e["n_members"],
                          registered_prediction=PREDICTIONS[m]["prediction"],
                          direction="enriched" if e["fold"] and e["fold"] > 1 else "not enriched",
                          effect_size=e["fold"], p=e["p"], extra=e)
            results.append(r)
        family = vc.adjust_family(results)
        for r in results:
            exp = PREDICTIONS[r.module]["expect_significant"]
            sig = r.padj <= vc.ALPHA and r.direction == "enriched"
            r.extra["significant"] = sig
            # Predictions (§4.5) are about the primary test; the control only qualifies it.
            r.extra["prediction_met"] = (None if exp is None or label != "primary_protein_coding"
                                         else sig == exp)
        out[label] = {"family": family, "results": [r.to_dict() for r in results]}

    primary = {r["module"]: r["extra"]["significant"] for r in out["primary_protein_coding"]["results"]}
    return {
        "analysis": "B — genetic support for the module structure",
        "prespec": "docs/planning/external_validation_prespec.md §4",
        "gwas_catalog": {
            "api": snap["source"], "downloaded": snap["downloaded"],
            "traits": snap["traits"], "threshold": GWS,
            "n_associations_snapshot": len(snap["associations"]),
            "n_gwas_genes_protein_coding": len(gw),
            "genes": gw,
        },
        "map": {"n_symbols": len(map_symbols), "n_gwas_in_map": len(map_symbols & hits),
                "map_vs_protein_coding": enrichment(map_symbols, hits, pc),
                "reactome_backbone_vs_protein_coding": enrichment(backbone_symbols(hgnc), hits, pc)},
        **out,
        "registered_predictions": PREDICTIONS,
        "falsification_check": {
            "rule": "the §4.5 prediction is falsified if enrichment is uniform across modules",
            "significant_modules_primary": sorted(m for m, s in primary.items() if s),
            "uniform": len(set(primary.values())) == 1,
        },
        "non_independence": NON_INDEPENDENCE,
        "secondary_source": {
            "name": "DisGeNET",
            "status": "not executed",
            "reason": "the DisGeNET API now requires an authenticated account (API key); no key is "
                      "configured for this pipeline. Reported as a gap; no substitute source is merged "
                      "into the primary result.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="snapshot the GWAS Catalog first (network)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the output would change")
    args = ap.parse_args(argv)
    if args.fetch:
        fetch()
    if not SNAPSHOT.exists():
        print("[FAIL] no GWAS snapshot; run with --fetch", file=sys.stderr)
        return 1
    text = json.dumps(run(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        print(("[OK] " if ok else "[FAIL] ") + f"{OUT.relative_to(ROOT)}")
        return 0 if ok else 1
    OUT.write_text(text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
