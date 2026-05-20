#!/usr/bin/env python3
"""Sign-blinded module activation scoring via AUCell (E2).

Addresses reviewer R2-M2: the v1.0 per-donor "module activation score"
was the mean of expression weighted by ``sign(log2FC)`` of the same
SSc-vs-HC DEG used to define the score → in-sample double-dipping. The
v1.1 replacement is AUCell (Aibar et al. *Nat Methods* 2017), which
scores each donor against the *pre-specified* module gene set without
any SSc/HC supervision.

Algorithm (per donor / per cell):

1. Rank all detected genes by expression (rank 1 = highest).
2. For each module M with gene set ``G_M``:
   - For each rank ``r`` in ``1..T`` where ``T = auc_max_rank``:
     - ``R(r)`` = number of G_M genes with rank ≤ r.
   - ``AUC = Σ R(r)`` over ``r = 1..T``.
   - Normalised to ``[0, 1]`` by the max-possible AUC
     ``Σ min(r, |G_M|) for r = 1..T``.

The score is **invariant to the SSc/HC label** — it depends only on
the expression rank profile of the donor and the fixed module gene
set. A second metric, **Tabib-style module Z-score**, is also
provided for triangulation (S2.2).

Inputs:
  pseudobulk TSV (donor × gene wide, with donor_id / condition /
  cell_type / dataset / tissue metadata columns).
  species_annotations.tsv → module gene sets.

Outputs:
  analysis/overlay/patient_module_scores_aucell.tsv
  analysis/overlay/patient_module_scores_zscore.tsv

Usage::

    python3 scripts/score_aucell.py \
        --pseudobulk pb.tsv \
        --species-tsv curation/annotations/species_annotations.tsv \
        --out-aucell analysis/overlay/patient_module_scores_aucell.tsv \
        --out-zscore analysis/overlay/patient_module_scores_zscore.tsv

Or as library:

    from score_aucell import aucell_score, module_zscore, load_module_gene_sets
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

log = logging.getLogger("aucell")

MODULES_ORDER = ["M1", "M2", "M3", "M4", "ssc_tier1"]


# ── Module gene sets ───────────────────────────────────────────────────────────

def load_module_gene_sets(tsv: Path) -> dict[str, set[str]]:
    """Return {module: set of HGNC symbols} from species_annotations.tsv.

    Comma-joined module labels (``"M1,M2"``) contribute to each module.
    Cleaned aliases (15 corrections per Phase 4b) are honoured directly
    from the TSV.
    """
    out: dict[str, set[str]] = defaultdict(set)
    with tsv.open() as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            hgnc = (row.get("hgnc_symbol") or "").strip()
            mod  = (row.get("module") or "").strip()
            if not hgnc or not mod:
                continue
            for m in mod.split(","):
                m = m.strip()
                if m and m != "?":
                    out[m].add(hgnc)
    return dict(out)


# ── AUCell ─────────────────────────────────────────────────────────────────────

def aucell_score(expr: np.ndarray, gene_set_mask: np.ndarray,
                 auc_max_rank: int) -> float:
    """Single-vector AUCell score.

    Parameters
    ----------
    expr
        1D array of expression values (any ordering); higher = more expressed.
    gene_set_mask
        Boolean array of the same shape: True where the gene is in the
        module gene set.
    auc_max_rank
        Top-T rank cutoff. Ties at the cutoff are broken arbitrarily
        (numpy argsort kind="stable").

    Returns
    -------
    AUC normalised to [0, 1]. 0 = none of the module genes in the top-T;
    1 = all module genes occupy the top |gene_set| ranks.
    """
    n = expr.shape[0]
    auc_max_rank = max(1, min(auc_max_rank, n))
    m = int(gene_set_mask.sum())
    if m == 0:
        return 0.0

    order = np.argsort(-expr, kind="stable")
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, n + 1)

    set_ranks = ranks[gene_set_mask]
    # Each set gene with rank ≤ T contributes (T - rank + 1) to the AUC
    contribs = np.maximum(0, auc_max_rank - set_ranks + 1)
    auc = float(contribs.sum())

    # Max possible AUC: all m genes pile at the top → ranks 1..m
    # contribute T, T-1, ..., T-m+1 respectively (clipped to ≥ 0).
    max_auc = sum(max(0, auc_max_rank - r + 1) for r in range(1, m + 1))
    return auc / max_auc if max_auc > 0 else 0.0


def module_zscore(expr: np.ndarray, gene_set_mask: np.ndarray) -> float:
    """Tabib-style module Z-score (S2.2).

    Mean of (gene - μ) / σ across module-set genes, where (μ, σ) are
    sample statistics of the full expression vector. Sign-blind — does
    not use SSc/HC labels.
    """
    if not gene_set_mask.any():
        return 0.0
    mu = float(expr.mean())
    sigma = float(expr.std()) or 1.0
    z = (expr - mu) / sigma
    return float(z[gene_set_mask].mean())


# ── Per-donor scoring ──────────────────────────────────────────────────────────

def score_donors(pb_df, module_sets: dict[str, set[str]],
                 auc_max_rank: int | None = None,
                 normalise: bool = True) -> "tuple[list[dict], list[dict], int]":
    """Run AUCell + Z-score per donor on a pseudobulk DataFrame.

    Cells from multiple cell types are aggregated into one per-donor
    pseudobulk (sum across cell types) before scoring. This keeps the
    score interpretable as a *donor-level* readout, matching the
    manuscript framing.

    Returns (aucell_rows, zscore_rows, auc_max_rank_used).
    """
    import pandas as pd
    meta = {"donor_id", "condition", "cell_type", "dataset", "tissue",
            "lib_size", "group"}
    gene_cols = [c for c in pb_df.columns if c not in meta]
    if not gene_cols:
        return [], [], 0

    # Aggregate to one row per donor (sum across cell types)
    donor_keys = ["donor_id", "condition", "dataset", "tissue"]
    have_keys = [k for k in donor_keys if k in pb_df.columns]
    grouped = pb_df.groupby(have_keys, observed=True)[gene_cols].sum().reset_index()

    if normalise:
        lib = grouped[gene_cols].sum(axis=1).replace(0, 1)
        cpm = grouped[gene_cols].div(lib, axis=0) * 1e4
        log_expr = np.log1p(cpm.values)
    else:
        log_expr = np.log1p(grouped[gene_cols].values)

    n_genes = log_expr.shape[1]
    if auc_max_rank is None:
        auc_max_rank = max(1, int(0.05 * n_genes))
    log.info("AUCell on %d donors × %d genes (T = %d)",
             log_expr.shape[0], n_genes, auc_max_rank)

    # Pre-compute gene masks per module
    gene_idx = {g: i for i, g in enumerate(gene_cols)}
    masks: dict[str, np.ndarray] = {}
    for mod, gset in module_sets.items():
        mask = np.zeros(n_genes, dtype=bool)
        for g in gset:
            i = gene_idx.get(g)
            if i is not None:
                mask[i] = True
        masks[mod] = mask
        if mod in MODULES_ORDER:
            log.info("  %s: %d / %d module genes present", mod, int(mask.sum()), len(gset))

    aucell_rows: list[dict] = []
    zscore_rows: list[dict] = []
    for idx, row in grouped.iterrows():
        donor = str(row.get("donor_id", idx))
        cond  = str(row.get("condition", "?"))
        ds    = str(row.get("dataset", "?"))
        tissue = str(row.get("tissue", "?"))
        group = "SSc" if cond.upper() in ("SSC", "SSC_ILD") else "HC"
        expr = log_expr[idx]
        auc_out = {"donor_id": donor, "group": group, "dataset": ds, "tissue": tissue}
        z_out   = dict(auc_out)
        for mod in MODULES_ORDER:
            if mod not in masks:
                auc_out[mod] = 0.0
                z_out[mod]   = 0.0
                continue
            auc_out[mod] = round(aucell_score(expr, masks[mod], auc_max_rank), 4)
            z_out[mod]   = round(module_zscore(expr, masks[mod]), 4)
        aucell_rows.append(auc_out)
        zscore_rows.append(z_out)
    return aucell_rows, zscore_rows, auc_max_rank


# ── I/O ────────────────────────────────────────────────────────────────────────

def read_pseudobulk_tsv(path: Path):
    """Same loader as deg_mixed_effects, kept self-contained."""
    import pandas as pd
    return pd.read_csv(path, sep="\t")


def write_score_tsv(rows: list[dict], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["donor_id", "group", "dataset", "tissue", *MODULES_ORDER]
    with path.open("w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    return len(rows)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pseudobulk",  type=Path, required=True,
                    help="Pseudobulk wide TSV (donor × gene)")
    ap.add_argument("--species-tsv", type=Path,
                    default=Path("curation/annotations/species_annotations.tsv"))
    ap.add_argument("--out-aucell",  type=Path,
                    default=Path("analysis/overlay/patient_module_scores_aucell.tsv"))
    ap.add_argument("--out-zscore",  type=Path,
                    default=Path("analysis/overlay/patient_module_scores_zscore.tsv"))
    ap.add_argument("--auc-max-rank", type=int, default=None,
                    help="Top-T cutoff; default = 5%% of n_genes")
    ap.add_argument("--no-normalise", action="store_true",
                    help="Skip CPM normalisation (e.g. when pseudobulk is already normalised)")
    ap.add_argument("--summary",     type=Path, default=None,
                    help="Optional JSON summary with SSc/HC contrasts per module")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s %(message)s")

    pb = read_pseudobulk_tsv(args.pseudobulk)
    module_sets = load_module_gene_sets(args.species_tsv)
    log.info("loaded %d donor-rows × %d cols from %s",
             len(pb), pb.shape[1], args.pseudobulk)
    log.info("module gene sets: %s",
             {k: len(v) for k, v in module_sets.items() if k in MODULES_ORDER})

    auc_rows, z_rows, T = score_donors(
        pb, module_sets,
        auc_max_rank=args.auc_max_rank,
        normalise=not args.no_normalise,
    )
    n_a = write_score_tsv(auc_rows, args.out_aucell)
    n_z = write_score_tsv(z_rows,   args.out_zscore)
    log.info("wrote %d AUCell rows → %s", n_a, args.out_aucell)
    log.info("wrote %d Z-score rows → %s", n_z, args.out_zscore)

    if args.summary:
        from statistics import fmean, pstdev
        summ: dict = {"auc_max_rank": T, "n_donors": n_a, "by_module": {}}
        for mod in MODULES_ORDER:
            ssc = [float(r[mod]) for r in auc_rows if r["group"] == "SSc"]
            hc  = [float(r[mod]) for r in auc_rows if r["group"] == "HC"]
            if not ssc or not hc:
                continue
            summ["by_module"][mod] = {
                "aucell": {
                    "ssc_mean": round(fmean(ssc), 4),
                    "ssc_sd":   round(pstdev(ssc), 4),
                    "hc_mean":  round(fmean(hc), 4),
                    "hc_sd":    round(pstdev(hc), 4),
                    "delta":    round(fmean(ssc) - fmean(hc), 4),
                },
            }
        args.summary.write_text(json.dumps(summ, indent=2))
        log.info("summary → %s", args.summary)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
