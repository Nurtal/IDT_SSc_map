#!/usr/bin/env python3
"""Anti-nonsense gates for candidate SSc edges (edge-discovery G0–G4).

Reads candidate edges from curation/staging/ssc_edge_candidates.tsv and runs each through
five hard gates. Nothing in this file is ever written to the curated map — it only sorts
candidates into PASS / FLAG / REJECT so a human can ratify the PASS set (promote_edges.py).

  G0 schema     required fields present; `type` in the controlled vocabulary
  G1 HGNC       every gene-like entity is an official HGNC symbol (HGNC REST, cached)
  G2 grounding  the `supporting_quote` is a verbatim substring of the source paper text
                (curation/staging/corpus/<pmid>.txt) — the core anti-hallucination gate
  G3 novelty    the (input gene → product gene) pair is not already an SSc reaction, and
                (advisory) not a forward Reactome-backbone pair
  G4 evidence   numeric source PMID present; corpus text available (SSc-context by corpus)

A candidate REJECTs if any of G0/G1/G2/G3-dup fails; FLAGs on softer issues (HGNC alias,
Reactome overlap, missing corpus); PASSes only when clean.

Outputs:
    curation/staging/validation_report.tsv
Run: python3 scripts/validate_edge_candidates.py  (or make validate-edges)
"""
from __future__ import annotations

import csv
import json
import re
import urllib.request
from itertools import product
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "curation/staging/ssc_edge_candidates.tsv"
CORPUS = ROOT / "curation/staging/corpus"
HGNC_CACHE = ROOT / "curation/staging/hgnc_cache.json"
REPORT = ROOT / "curation/staging/validation_report.tsv"
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
XML = ROOT / "curation/celldesigner/SSc_MIM_integrated.xml"
ANN = ROOT / "curation/annotations/species_annotations.tsv"
NS = {"s": "http://www.sbml.org/sbml/level2/version4"}
UA = "SSc-MIM-hgnc/0.1 (mailto:nathan.foulquier.pro@gmail.com)"

TYPES = {"binding", "catalysis", "phosphorylation", "transcription", "activation",
         "inhibition", "state_change", "transport", "degradation", "dissociation", "contributes"}
GENE_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")


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


def load_hgnc_cache() -> dict:
    return json.loads(HGNC_CACHE.read_text()) if HGNC_CACHE.exists() else {}


def hgnc_official(sym: str, cache: dict) -> bool:
    if sym in cache:
        return cache[sym]
    url = f"https://rest.genenames.org/fetch/symbol/{sym}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        d = json.loads(urllib.request.urlopen(req, timeout=20).read())
        ok = d.get("response", {}).get("numFound", 0) >= 1
    except Exception:
        ok = None  # network failure -> unknown, treat as flag not reject
    cache[sym] = ok
    return ok


def existing_ssc_pairs() -> set[tuple[str, str]]:
    pairs = set()
    for r in csv.DictReader(SSC.open(), delimiter="\t"):
        ins = genes(r["reactants"]) + genes(r.get("modifiers", ""))
        outs = genes(r["products"])
        for a, b in product(ins, outs):
            pairs.add((a, b))
    return pairs


def backbone_pairs() -> set[tuple[str, str]]:
    hg = {}
    for r in csv.DictReader(ANN.open(), delimiter="\t"):
        sym = (r.get("hgnc_symbol", "") or "").strip()
        if sym:
            hg.setdefault(r["species_id"], set()).add(sym)
    pairs = set()
    for rxn in ET.parse(XML).getroot().findall(".//s:reaction", NS):
        if rxn.get("id", "").startswith("ssc_"):
            continue
        ins, outs = set(), set()
        for tag, b in (("listOfReactants", ins), ("listOfModifiers", ins), ("listOfProducts", outs)):
            for sr in rxn.findall(f"s:{tag}/*", NS):
                b |= hg.get(sr.get("species"), set())
        for a, c in product(ins, outs):
            pairs.add((a, c))
    return pairs


def corpus_text(pmid: str) -> str | None:
    f = CORPUS / f"{pmid}.txt"
    return re.sub(r"\s+", " ", f.read_text()).lower() if f.exists() else None


def main() -> None:
    if not CAND.exists():
        print(f"[validate] no candidates at {CAND}")
        return
    cands = list(csv.DictReader(CAND.open(), delimiter="\t"))
    hgnc_cache = load_hgnc_cache()
    ssc_pairs = existing_ssc_pairs()
    bb_pairs = backbone_pairs()

    rows = []
    for c in cands:
        cid = c.get("candidate_id", "?")
        problems, flags = [], []
        # G0 schema
        for col in ("type", "reactants", "products", "source_pmid", "supporting_quote", "mechanism"):
            if not (c.get(col, "") or "").strip():
                problems.append(f"G0:missing[{col}]")
        if (c.get("type", "") or "").strip() not in TYPES:
            problems.append(f"G0:bad_type[{c.get('type','')}]")
        # G1 HGNC
        all_genes = genes(c.get("reactants", "")) + genes(c.get("products", "")) + genes(c.get("modifiers", ""))
        for g in all_genes:
            ok = hgnc_official(g, hgnc_cache)
            if ok is False:
                flags.append(f"G1:not_official_HGNC[{g}]")  # likely alias/typo — fixable, not nonsense
            elif ok is None:
                flags.append(f"G1:HGNC_unverified[{g}]")
        # G2 grounding
        pmid = (c.get("source_pmid", "") or "").strip()
        quote = re.sub(r"\s+", " ", (c.get("supporting_quote", "") or "")).strip().lower()
        txt = corpus_text(pmid)
        if txt is None:
            flags.append("G2:no_corpus")
        elif len(quote) < 12:
            problems.append("G2:quote_too_short")
        elif quote not in txt:
            problems.append("G2:NOT_GROUNDED")
        # G3 novelty / dedup
        ins = genes(c.get("reactants", "")) + genes(c.get("modifiers", ""))
        outs = genes(c.get("products", ""))
        cpairs = [(a, b) for a, b in product(ins, outs) if a != b]
        if cpairs and all(p in ssc_pairs for p in cpairs):
            problems.append("G3:DUP_existing_ssc")
        if any(p in bb_pairs for p in cpairs):
            flags.append("G3:reactome_overlap")
        # G4 evidence
        if not pmid.isdigit():
            problems.append("G4:bad_pmid")

        verdict = "REJECT" if problems else ("FLAG" if flags else "PASS")
        rows.append({"candidate_id": cid, "verdict": verdict,
                     "problems": ";".join(problems), "flags": ";".join(flags),
                     "mechanism": c.get("mechanism", "")[:80]})

    HGNC_CACHE.write_text(json.dumps(hgnc_cache, indent=0))
    with REPORT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    dist = Counter(r["verdict"] for r in rows)
    print(f"[validate] {len(rows)} candidates -> {dict(dist)}")
    for r in rows:
        if r["verdict"] != "PASS":
            print(f"  {r['verdict']:6} {r['candidate_id']}: {r['problems']} {r['flags']}")
    print(f"[validate] report -> {REPORT}")


if __name__ == "__main__":
    main()
