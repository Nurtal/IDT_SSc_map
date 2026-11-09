#!/usr/bin/env python3
"""Validation core — the only place the L2 decision rules live (issue #9).

Applies `docs/planning/external_validation_prespec.md` §2–§3 uniformly. Every
analysis (bulk cohorts, M5 blood precedent, …) parses its own source and hands
this module plain arrays; nothing here reads a file or knows about GEO, GWAS
Catalog or OpenTargets.

Provides:
  singscore(expr, mask)          rank-based, sign-blind per-sample score (primary)
  zscore_score(expr, mask)       mean per-feature z-score per sample (sensitivity;
                                 the M5 precedent's score)
  contrast(case, control)        two-sided Mann-Whitney U + rank-biserial effect
  testable(n_detectable, floor)  pre-spec §2 size floor
  adjust_family(results)         BH over the testable results only; records the family
  cohort_outcome(result, ref)    per-cohort: meets / contradicts / neither
  module_verdict(outcomes)       replicated | partial | not_replicated | contradicted

Decision rule (pre-spec §3.4), as implemented:
  - a cohort *meets* the criteria when padj <= ALPHA and the effect has the
    reference direction; it *contradicts* when padj <= ALPHA in the opposite
    direction;
  - across the module's testable cohorts: any contradiction -> contradicted
    (reported on its own line, never absorbed); otherwise all cohorts meet ->
    replicated; some but not all -> partial; none -> not_replicated.
  "Replicated" therefore requires every testable cohort. The pre-spec's "at
  least half" clause is subsumed by its "some but not all is partial" clause,
  which this reads as taking precedence (spec user story 18: inconsistent
  replication is not rounded up).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
from scipy.stats import mannwhitneyu, rankdata

ALPHA = 0.05
MIN_DETECTABLE = 10  # pre-spec §2; also recorded in analysis/validation/module_genesets_summary.json

UP, DOWN = "up", "down"
REPLICATED, PARTIAL, NOT_REPLICATED, CONTRADICTED = (
    "replicated", "partial", "not_replicated", "contradicted")
MEETS, CONTRADICTS, NEITHER = "meets", "contradicts", "neither"


# ── scoring (sign-blind: membership only, no weights, no contrast used) ─────────

def singscore(expr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Unidirectional singscore (Foroutan et al. 2018) per sample.

    expr: genes × samples; mask: boolean over genes (module membership).
    Genes are ranked ascending within each sample (ties averaged); the mean rank
    of the module genes is rescaled to [-0.5, 0.5] between its theoretical
    minimum and maximum. Missing values are excluded per sample.
    """
    expr = np.asarray(expr, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    out = np.full(expr.shape[1], np.nan)
    for j in range(expr.shape[1]):
        col = expr[:, j]
        ok = ~np.isnan(col)
        sel = mask & ok
        n, N = int(sel.sum()), int(ok.sum())
        if n == 0 or n == N:
            continue
        ranks = np.full(col.shape, np.nan)
        ranks[ok] = rankdata(col[ok])
        mean_rank = float(np.mean(ranks[sel]))
        lo, hi = (n + 1) / 2, N - (n - 1) / 2
        out[j] = (mean_rank - lo) / (hi - lo) - 0.5
    return out


def zscore_score(expr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean of per-feature z-scores (across samples) over the module, per sample.

    Exactly the GSE45536 M5 precedent's score (population SD; zero SD -> 1).
    """
    mat = np.asarray(expr, dtype=float)[np.asarray(mask, dtype=bool)]
    if mat.size == 0:
        return np.full(np.asarray(expr).shape[1], np.nan)
    mu = np.nanmean(mat, axis=1, keepdims=True)
    sd = np.nanstd(mat, axis=1, keepdims=True)
    sd[sd == 0] = 1
    return np.nanmean((mat - mu) / sd, axis=0)


# ── contrast ───────────────────────────────────────────────────────────────────

@dataclass
class Contrast:
    n_case: int
    n_control: int
    mean_case: float
    mean_control: float
    delta: float
    effect_size: float  # rank-biserial r in [-1, 1]; > 0 means case higher
    p: float

    @property
    def direction(self) -> str:
        return UP if self.effect_size > 0 else (DOWN if self.effect_size < 0 else "none")


def contrast(case, control) -> Contrast:
    """Two-sided Mann-Whitney U, case vs control, with rank-biserial effect size."""
    c = np.asarray(case, dtype=float); c = c[~np.isnan(c)]
    h = np.asarray(control, dtype=float); h = h[~np.isnan(h)]
    res = mannwhitneyu(c, h, alternative="two-sided")
    r = 2.0 * float(res.statistic) / (len(c) * len(h)) - 1.0
    return Contrast(len(c), len(h), float(np.mean(c)), float(np.mean(h)),
                    float(np.mean(c) - np.mean(h)), r, float(res.pvalue))


# ── result record, family, decision ────────────────────────────────────────────

@dataclass
class Result:
    """One (module × source) test. The single shape every L2 analysis emits."""
    module: str
    source: str
    testable: bool
    n_detectable: int
    reference_direction: str | None = None   # from the frozen single-cell contrasts
    registered_prediction: str | None = None  # pre-spec §3.6, verbatim
    direction: str | None = None
    effect_size: float | None = None
    delta: float | None = None
    n_case: int | None = None
    n_control: int | None = None
    p: float | None = None
    padj: float | None = None
    outcome: str | None = None
    verdict: str | None = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def testable(n_detectable: int, floor: int = MIN_DETECTABLE) -> bool:
    return n_detectable >= floor


def make_result(module: str, source: str, n_detectable: int, case=None, control=None,
                reference_direction: str | None = None,
                registered_prediction: str | None = None,
                floor: int = MIN_DETECTABLE) -> Result:
    """Build a Result; a module below the floor is recorded untested."""
    r = Result(module, source, testable(n_detectable, floor), n_detectable,
               reference_direction, registered_prediction)
    if r.testable:
        c = contrast(case, control)
        r.direction, r.effect_size, r.delta = c.direction, c.effect_size, c.delta
        r.n_case, r.n_control, r.p = c.n_case, c.n_control, c.p
    return r


def bh(pvalues) -> list[float]:
    p = np.asarray(pvalues, dtype=float)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p)
    adj = p[order] * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.clip(adj, 0, 1)
    return out.tolist()


def adjust_family(results: list[Result]) -> dict:
    """BH over the testable results only (pre-spec §3.4). Returns the family record."""
    family = [r for r in results if r.testable]
    for r, q in zip(family, bh([r.p for r in family])):
        r.padj = q
    return {
        "method": "Benjamini-Hochberg",
        "alpha": ALPHA,
        "members": [f"{r.module}|{r.source}" for r in family],
        "excluded_not_testable": [f"{r.module}|{r.source}" for r in results if not r.testable],
    }


def cohort_outcome(r: Result, alpha: float = ALPHA) -> str | None:
    """meets / contradicts / neither for one testable, adjusted result."""
    if not r.testable:
        return None
    if r.padj is None:
        raise ValueError(f"{r.module}|{r.source}: adjust_family() before deciding")
    if r.reference_direction not in (UP, DOWN):
        raise ValueError(f"{r.module}|{r.source}: no reference direction to decide against")
    if r.padj > alpha or r.direction not in (UP, DOWN):
        return NEITHER
    return MEETS if r.direction == r.reference_direction else CONTRADICTS


def module_verdict(outcomes: list[str | None]) -> str | None:
    """Combine one module's per-cohort outcomes (None = not testable there)."""
    tested = [o for o in outcomes if o is not None]
    if not tested:
        return None
    if CONTRADICTS in tested:
        return CONTRADICTED
    n_meet = tested.count(MEETS)
    if n_meet == len(tested):
        return REPLICATED
    return PARTIAL if n_meet else NOT_REPLICATED


def decide(results: list[Result], alpha: float = ALPHA) -> dict[str, str | None]:
    """Fill each result's outcome and verdict; return {module: verdict}."""
    by_module: dict[str, list[Result]] = {}
    for r in results:
        r.outcome = cohort_outcome(r, alpha)
        by_module.setdefault(r.module, []).append(r)
    verdicts = {}
    for m, rs in by_module.items():
        v = module_verdict([r.outcome for r in rs])
        verdicts[m] = v
        for r in rs:
            r.verdict = v
    return verdicts
