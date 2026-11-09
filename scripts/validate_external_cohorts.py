#!/usr/bin/env python3
"""Analysis A — replicate the five modules in the frozen independent skin cohorts (issue #17).

Governed by `docs/planning/external_validation_prespec.md` §3. Thin adapter:
this script parses the two frozen cohorts and the committed single-cell
pseudobulk; scoring, the contrast, the family adjustment and the verdicts are
`validation_core`'s.

Two steps, committed separately so the order is auditable:

  --references   Reference directions, recomputed on the frozen gene sets from
                 the committed single-cell pseudobulk (pre-spec §8 amendment of
                 2026-11-09). Reference dataset: Gur 2022 skin (GSE195452, 97 SSc /
                 57 HC, the largest skin dataset), AUCell per donor exactly as in
                 the published overlay (`score_aucell.score_donors`). Whole tissue
                 for M1, M3, M4, M5; M2 restricted to fibroblast cell types
                 (pre-spec §3.5): every `Fibro_*` type except the unannotated
                 `Fibro_Bad`. Writes analysis/validation/reference_directions.json.
                 Reads no bulk cohort.

  (default)      Scores the frozen cohorts (analysis/validation/cohort_screening.json,
                 cohort_samples.tsv) and writes analysis/validation/external_replication.json.

Scoring (pre-spec §3.3, fixed before execution):
  - gene level: GSE58095 probes -> mean of the probes of each resolved symbol;
    GSE130955 Ensembl FPKM -> summed per resolved symbol, then log2(x + 1);
  - singscore over the full measured transcriptome (primary), mean per-gene
    z-score across samples (sensitivity); module membership only;
  - SSc vs HC, two-sided Mann-Whitney, rank-biserial effect; BH over the
    family declared at screening (the sensitivity score has its own family).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import tarfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import screen_cohorts as sc  # noqa: E402
import validation_core as vc  # noqa: E402

VAL = ROOT / "analysis/validation"
PSEUDOBULK = ROOT / "analysis/overlay/pseudobulk_multi.tsv"
REFERENCES = VAL / "reference_directions.json"
OUT = VAL / "external_replication.json"

MODULES = vc_modules = ("M1", "M2", "M3", "M4", "M5")
REFERENCE_DATASET = "gse195452"
FIBROBLAST_RESTRICTED = {"M2"}
EXCLUDED_FIBRO_TYPES = {"Fibro_Bad"}

# Pre-spec §3.6, verbatim (registered 2026-09-10, before execution).
PREDICTIONS = {
    "M1": {"direction": "up", "confidence": "high"},
    "M2": {"direction": "up", "confidence": "high"},
    "M3": {"direction": "null or weak", "confidence": "low"},
    "M4": {"direction": "up, modest", "confidence": "medium"},
    "M5": {"direction": "null in skin", "confidence": "medium"},
}

CAVEATS = [
    "Bulk tissue cannot separate a shift in cell composition from module activation (pre-spec §3.5).",
    "M5 is carried by rare B and plasma cells in skin; a null M5 in skin bulk is expected and is not "
    "evidence against M5, validated in blood (GSE45536).",
    "GSE130955 donor overlap with Tabib 2021 cannot be excluded from public records (at most 12 of 48 SSc); "
    "see cohort_screening.json.",
    "GSE130955 (PRESS) and GSE58095 (GENISOS) were both generated at UTHealth Houston; they are distinct "
    "cohorts (early vs established disease) but not independent laboratories.",
]


# ── references ─────────────────────────────────────────────────────────────────

def frozen_sets() -> dict[str, set[str]]:
    return sc.frozen_genesets()


def reference_directions() -> dict:
    import pandas as pd
    import score_aucell as sa
    pb = pd.read_csv(PSEUDOBULK, sep="\t")
    pb = pb[pb["dataset"] == REFERENCE_DATASET]
    fibro = pb[pb["cell_type"].str.startswith("Fibro_") & ~pb["cell_type"].isin(EXCLUDED_FIBRO_TYPES)]
    sets = frozen_sets()
    out = {}
    for scope, df, mods in (("whole_tissue", pb, [m for m in MODULES if m not in FIBROBLAST_RESTRICTED]),
                            ("fibroblast_restricted", fibro, sorted(FIBROBLAST_RESTRICTED))):
        auc_rows, _, t = sa.score_donors(df, {m: sets[m] for m in mods})
        for m in mods:
            ssc = [r[m] for r in auc_rows if r["group"] == "SSc"]
            hc = [r[m] for r in auc_rows if r["group"] == "HC"]
            c = vc.contrast(ssc, hc)
            out[m] = {
                "scope": scope,
                "direction": c.direction if c.direction in (vc.UP, vc.DOWN) else None,
                "effect_size": c.effect_size, "delta": c.delta, "p": c.p,
                "n_ssc": c.n_case, "n_hc": c.n_control, "auc_max_rank": t,
            }
    return {
        "source": "analysis/overlay/pseudobulk_multi.tsv (frozen single-cell run of 2026-06-26)",
        "dataset": "GSE195452 (Gur 2022 skin)",
        "metric": "AUCell per donor (score_aucell.score_donors), frozen gene sets",
        "fibroblast_cell_types": sorted(set(fibro["cell_type"])),
        "rule": "direction = sign of the rank-biserial SSc-vs-HC effect; M2 from fibroblast types only",
        "modules": out,
    }


# ── bulk cohorts ───────────────────────────────────────────────────────────────

def expression_gse58095(hgnc: sc.Hgnc) -> tuple[list[str], list[str], np.ndarray]:
    """genes × samples (log2 as deposited), probes averaged per resolved symbol."""
    probe_sym: dict[str, set[str]] = {}
    with gzip.open(sc.GPL10558_ANNOT, "rt", errors="replace") as fh:
        header = None
        for line in fh:
            if header is None:
                if line.startswith("ID\t"):
                    header = line.rstrip("\n").split("\t")
                    i_id, i_sym = header.index("ID"), header.index("Gene symbol")
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) > i_sym and p[i_sym]:
                syms = {hgnc.current(s) for s in p[i_sym].split("///") if s}
                if len(syms) == 1:   # multi-gene probes are ambiguous: dropped
                    probe_sym[p[i_id]] = syms
    sums: dict[str, np.ndarray] = {}
    counts: dict[str, int] = {}
    samples: list[str] = []
    with gzip.open(sc.RAW / "gse58095/GSE58095_series_matrix.txt.gz", "rt", errors="replace") as fh:
        in_tbl = False
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                in_tbl = True
                samples = [s.strip('"') for s in next(fh).rstrip("\n").split("\t")[1:]]
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if not in_tbl:
                continue
            p = line.rstrip("\n").split("\t")
            pid = p[0].strip('"')
            if pid not in probe_sym:
                continue
            vals = np.array([float(x) if x not in ("", "null", "NA") else np.nan for x in p[1:]])
            sym = next(iter(probe_sym[pid]))
            sums[sym] = sums.get(sym, 0) + np.nan_to_num(vals)
            counts[sym] = counts.get(sym, 0) + 1
    genes = sorted(sums)
    return genes, samples, np.array([sums[g] / counts[g] for g in genes])


def expression_gse130955(hgnc: sc.Hgnc, wanted: set[str]) -> tuple[list[str], list[str], np.ndarray]:
    """genes × samples, log2(FPKM + 1), FPKM summed per resolved symbol."""
    per_sample: dict[str, dict[str, float]] = {}
    with tarfile.open(sc.RAW / "gse130955/GSE130955_RAW.tar") as t:
        for m in t.getmembers():
            gsm = m.name.split("_", 1)[0]
            if gsm not in wanted:
                continue
            text = gzip.decompress(t.extractfile(m).read()).decode()
            d: dict[str, float] = {}
            for ln in text.splitlines()[1:]:
                eid, val = ln.split("\t")
                sym = hgnc.ensembl.get(eid.split(".", 1)[0])
                if sym:
                    d[sym] = d.get(sym, 0.0) + float(val)
            per_sample[gsm] = d
    samples = sorted(per_sample)
    genes = sorted(set.intersection(*(set(d) for d in per_sample.values())))
    mat = np.array([[per_sample[s][g] for s in samples] for g in genes])
    return genes, samples, np.log2(mat + 1)


def cohort_arms(accession: str) -> dict[str, str]:
    with (VAL / "cohort_samples.tsv").open() as fh:
        return {r["gsm"]: r["arm"] for r in csv.DictReader(fh, delimiter="\t")
                if r["cohort"] == accession and r["arm"] in ("SSc", "HC")}


def score_cohort(accession, genes, samples, mat, arms, sets, hgnc, refs, score_fn):
    keep = [i for i, s in enumerate(samples) if s in arms]
    mat = mat[:, keep]
    grp = np.array([arms[samples[i]] for i in keep])
    index = {g: i for i, g in enumerate(genes)}
    results = []
    for m in MODULES:
        mask = np.zeros(len(genes), dtype=bool)
        for sym in sets[m]:
            i = index.get(hgnc.map_symbol(sym))
            if i is not None:
                mask[i] = True
        s = score_fn(mat, mask)
        r = vc.make_result(m, accession, int(mask.sum()), s[grp == "SSc"], s[grp == "HC"],
                           reference_direction=refs[m]["direction"],
                           registered_prediction=f"{PREDICTIONS[m]['direction']} ({PREDICTIONS[m]['confidence']})")
        results.append(r)
    return results


def run() -> dict:
    refs = json.loads(REFERENCES.read_text())["modules"]
    screening = json.loads((VAL / "cohort_screening.json").read_text())
    frozen = screening["frozen_cohorts"]
    sets = frozen_sets()
    hgnc = sc.Hgnc(sc.HGNC)
    expr = {}
    if "GSE58095" in frozen:
        expr["GSE58095"] = expression_gse58095(hgnc)
    if "GSE130955" in frozen:
        expr["GSE130955"] = expression_gse130955(hgnc, set(cohort_arms("GSE130955")))

    report = {}
    for label, fn in (("primary_singscore", vc.singscore), ("sensitivity_zscore", vc.zscore_score)):
        results = []
        for acc in frozen:
            genes, samples, mat = expr[acc]
            results += score_cohort(acc, genes, samples, mat, cohort_arms(acc), sets, hgnc, refs, fn)
        family = vc.adjust_family(results)
        declared = set(screening["family"]["testable"])
        got = {f"{r.module}|{r.source}" for r in results if r.testable}
        if got != declared:
            raise RuntimeError(f"testable family differs from screening: {sorted(got ^ declared)}")
        decidable = [r for r in results if r.reference_direction in (vc.UP, vc.DOWN)]
        verdicts = vc.decide(decidable)
        report[label] = {
            "family": family,
            "verdicts": {m: verdicts.get(m, "undecidable: no reference direction") for m in MODULES},
            "results": [r.to_dict() for r in results],
        }
    return {
        "analysis": "A — replication of module activation in independent bulk skin cohorts",
        "prespec": "docs/planning/external_validation_prespec.md §3",
        "decision_rule": "padj <= 0.05 and reference direction in every testable cohort -> replicated; "
                         "some but not all -> partial; none -> not_replicated; any significant opposite -> "
                         "contradicted (validation_core.decide)",
        "cohorts": {acc: {"n_ssc": int(sum(a == "SSc" for a in cohort_arms(acc).values())),
                          "n_hc": int(sum(a == "HC" for a in cohort_arms(acc).values())),
                          "n_genes_scored": len(expr[acc][0])} for acc in frozen},
        "reference_directions": refs,
        "registered_predictions": PREDICTIONS,
        "caveats": CAVEATS,
        **report,
    }


def _dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=float) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--references", action="store_true", help="only (re)compute the reference directions")
    ap.add_argument("--check", action="store_true", help="exit 1 if the output would change")
    args = ap.parse_args(argv)
    target, payload = (REFERENCES, reference_directions) if args.references else (OUT, run)
    text = _dump(payload())
    if args.check:
        ok = target.exists() and target.read_text() == text
        print(("[OK] " if ok else "[FAIL] ") + f"{target.relative_to(ROOT)} "
              + ("matches a fresh run" if ok else "differs from a fresh run"))
        return 0 if ok else 1
    target.write_text(text)
    print(f"[OK] wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
