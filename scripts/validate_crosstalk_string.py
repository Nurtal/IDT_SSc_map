#!/usr/bin/env python3
"""Angle-2 validation of the 3 weak crosstalk rows via STRING-DB v12.

The 8 inter-module crosstalk reactions in
``manuscript/supplementary/S1_crosstalk_reactions.tsv`` (E5) carry a
``quality_flag`` column. 5/8 are validated by primary literature
(ECO:0000270 or ECO:0000314 + PMID). The remaining 3 are
curator-inference rows (ECO:0000305, no PMID):

    ssc_crosstalk_001  M1 → M2  IFN-I primes pro-fibrotic fibroblast
    ssc_crosstalk_003  M1 → M4  IFN-I primes pDC + B-cell activation
    ssc_crosstalk_007  M3 → M2  EndMT-derived perivascular fibroblasts

For each of these we cross-check against STRING-DB v12 (REST API,
no auth) at species 9606 (Homo sapiens). The target side of each
row is a *phenotype* (cellular state, not a gene), so we expand it
to a panel of marker / effector genes that biologically define that
state, then test every (source_gene × target_marker) pair.

A pair is considered "STRING-confirmed" when its ``combined_score``
is ≥ 0.700 (STRING's "high-confidence" cutoff). A row is considered
"STRING-validated" when at least one such pair exists.

Outputs:
    analysis/network/crosstalk_string_validation.tsv    per-pair detail
    analysis/network/crosstalk_string_validation.json   summary
    manuscript/supplementary/S1_crosstalk_reactions.tsv updated
                                                        in place with a
                                                        new column
                                                        string_validation

Run with:
    make crosstalk-validate
or directly:
    python3 scripts/validate_crosstalk_string.py
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

STRING_API = "https://string-db.org/api/json/network"
STRING_TAXON = 9606  # Homo sapiens
CONFIDENCE = 0.700   # STRING high-confidence cutoff
TIMEOUT = 30

S1 = Path("manuscript/supplementary/S1_crosstalk_reactions.tsv")
OUT_TSV = Path("analysis/network/crosstalk_string_validation.tsv")
OUT_JSON = Path("analysis/network/crosstalk_string_validation.json")

# Map each phenotype-style target to its biologically defining marker
# / effector gene set. Sources of these panels:
#   - fibroblast_proFibrotic     SMAD3, TGFB1, COL1A1, ACTA2, POSTN
#                                — canonical SSc-myofibroblast effectors
#   - pDC_activated              IRF7, TLR7, IL3RA, IRF8
#                                — canonical pDC IFN-producing identity
#   - BCR_activated              CD40, CD79A, CD79B, MS4A1
#                                — canonical BCR signalling complex
#   - phenotype_myofibroblast_*  ACTA2, FAP, COL1A1, POSTN, CTHRC1
#                                — Tabib 2021 myofibroblast signature
PHENOTYPE_PANEL: dict[str, list[str]] = {
    "fibroblast_proFibrotic":            ["SMAD3", "TGFB1", "COL1A1", "ACTA2", "POSTN"],
    "pDC_activated":                     ["IRF7", "TLR7", "IL3RA", "IRF8"],
    "BCR_activated":                     ["CD40", "CD79A", "CD79B", "MS4A1"],
    "phenotype_myofibroblast_activation":["ACTA2", "FAP", "COL1A1", "POSTN", "CTHRC1"],
}

# The 3 weak rows we want to test. (Source genes hand-extracted from
# reactants/modifiers; phenotype target hand-extracted from products.)
WEAK_ROWS: list[dict] = [
    {
        "reaction_id":      "ssc_crosstalk_001",
        "source_module":    "M1",
        "target_module":    "M2",
        "source_genes":     ["IFNB1", "IFNA1"],
        "target_phenotype": "fibroblast_proFibrotic",
    },
    {
        "reaction_id":      "ssc_crosstalk_003",
        "source_module":    "M1",
        "target_module":    "M4",
        "source_genes":     ["IFNB1", "IFNA1"],
        "target_phenotype": "pDC_activated_OR_BCR_activated",
    },
    {
        "reaction_id":      "ssc_crosstalk_007",
        "source_module":    "M3",
        "target_module":    "M2",
        "source_genes":     ["CDH2", "FAP"],
        "target_phenotype": "phenotype_myofibroblast_activation",
    },
]


@dataclass
class PairResult:
    reaction_id: str
    source_gene: str
    target_gene: str
    target_phenotype: str
    combined_score: float | None
    string_confirmed: bool

    def as_row(self) -> dict[str, str]:
        return {
            "reaction_id":         self.reaction_id,
            "source_gene":         self.source_gene,
            "target_gene":         self.target_gene,
            "target_phenotype":    self.target_phenotype,
            "combined_score":      f"{self.combined_score:.3f}" if self.combined_score is not None else "",
            "string_confirmed":    "yes" if self.string_confirmed else "no",
        }


def query_string(genes: list[str]) -> list[dict]:
    """Hit the STRING REST `network` endpoint and return the edge list.

    Returns an empty list on network/API failure (logged to stderr).
    """
    if len(genes) < 2:
        return []
    payload = {
        "identifiers":    "%0d".join(genes),
        "species":        str(STRING_TAXON),
        "network_flavor": "evidence",
        "caller_identity": "ssc-mim-revision-v1.1",
    }
    url = STRING_API + "?" + urllib.parse.urlencode(payload, safe="%0d")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [warn] STRING query failed for {genes}: {e}", file=sys.stderr)
        return []


def main() -> int:
    if not S1.exists():
        raise SystemExit(f"missing {S1}")

    all_pairs: list[PairResult] = []
    summary: dict[str, dict] = {}

    for row in WEAK_ROWS:
        rid = row["reaction_id"]
        srcs = row["source_genes"]

        # Resolve the target panel(s)
        phen_key = row["target_phenotype"]
        if phen_key == "pDC_activated_OR_BCR_activated":
            targets = sorted(set(PHENOTYPE_PANEL["pDC_activated"]
                                  + PHENOTYPE_PANEL["BCR_activated"]))
        else:
            targets = list(PHENOTYPE_PANEL[phen_key])

        print(f"\n[{rid}] {row['source_module']} → {row['target_module']}")
        print(f"  source genes: {srcs}")
        print(f"  target panel: {targets}")

        # Single STRING call with the full union (cheaper + lets STRING
        # build the joint network in one pass)
        query_set = sorted(set(srcs + targets))
        edges = query_string(query_set)
        # Build a lookup keyed on (preferredName_A, preferredName_B)
        edge_score: dict[tuple[str, str], float] = {}
        for e in edges:
            a, b = e.get("preferredName_A"), e.get("preferredName_B")
            try:
                cs = float(e.get("score", 0))
            except (TypeError, ValueError):
                cs = 0.0
            edge_score[(a, b)] = cs
            edge_score[(b, a)] = cs

        # Score every source × target pair
        n_pairs = n_confirmed = 0
        max_score = 0.0
        for s in srcs:
            for t in targets:
                cs = edge_score.get((s, t))
                confirmed = cs is not None and cs >= CONFIDENCE
                all_pairs.append(PairResult(
                    reaction_id=rid,
                    source_gene=s,
                    target_gene=t,
                    target_phenotype=phen_key,
                    combined_score=cs,
                    string_confirmed=confirmed,
                ))
                n_pairs += 1
                if confirmed:
                    n_confirmed += 1
                if cs is not None and cs > max_score:
                    max_score = cs

        sym = "✓" if n_confirmed > 0 else "✗"
        print(f"  {sym} {n_confirmed}/{n_pairs} pairs at STRING ≥ {CONFIDENCE}; "
              f"max combined_score = {max_score:.3f}")

        summary[rid] = {
            "source_module":    row["source_module"],
            "target_module":    row["target_module"],
            "source_genes":     srcs,
            "target_panel":     targets,
            "n_pairs_tested":   n_pairs,
            "n_pairs_confirmed_ge_700": n_confirmed,
            "max_combined_score": round(max_score, 3),
            "string_validated": n_confirmed > 0,
        }
        # be polite to the API
        time.sleep(1.0)

    # ── Write per-pair TSV ────────────────────────────────────────────
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="") as fh:
        fields = ["reaction_id", "source_gene", "target_gene",
                  "target_phenotype", "combined_score", "string_confirmed"]
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for p in all_pairs:
            w.writerow(p.as_row())
    print(f"\nwrote {OUT_TSV} ({len(all_pairs)} pairs)")

    # ── Write summary JSON ────────────────────────────────────────────
    OUT_JSON.write_text(json.dumps({
        "string_api":           STRING_API,
        "string_taxon":         STRING_TAXON,
        "confidence_threshold": CONFIDENCE,
        "phenotype_panels":     PHENOTYPE_PANEL,
        "rows":                 summary,
    }, indent=2) + "\n")
    print(f"wrote {OUT_JSON}")

    # ── Patch Supplementary Table S1 with the validation column ───────
    rows = list(csv.DictReader(S1.open(), delimiter="\t"))
    fields = list(rows[0].keys())
    if "string_validation" not in fields:
        # insert just after quality_flag for readability
        insert_at = fields.index("quality_flag") + 1
        fields = fields[:insert_at] + ["string_validation"] + fields[insert_at:]
    for r in rows:
        s = summary.get(r["reaction_id"])
        if s is None:
            r.setdefault("string_validation", "n/a (literature-validated; not tested)")
        else:
            if s["string_validated"]:
                r["string_validation"] = (
                    f"STRING-confirmed: {s['n_pairs_confirmed_ge_700']}/"
                    f"{s['n_pairs_tested']} pairs ≥ 0.700 "
                    f"(max={s['max_combined_score']:.3f})"
                )
            else:
                r["string_validation"] = (
                    f"STRING-not-confirmed: 0/{s['n_pairs_tested']} pairs "
                    f"≥ 0.700 (max={s['max_combined_score']:.3f})"
                )
    with S1.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"updated {S1} with `string_validation` column")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
