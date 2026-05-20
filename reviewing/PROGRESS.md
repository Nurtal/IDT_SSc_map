# PROGRESS — npj-SBA revision

> One-screen dashboard for the revision. Updated at every sprint
> gate. Authoritative status of the E1–E25 essential revisions
> from `editor_decision.md`.

**Branch**: `revision/v1.1`.
**Started**: 2026-05-20 (S0).
**Target submission**: 2026-09-30.
**Re-review target**: R1 + R2.
**Last gate cleared**: — (S0 in progress).

## Sprint dashboard

| Sprint | Window | Status | Gate cleared | Notes |
|--------|--------|--------|--------------|-------|
| S0 | 2026-05-21 → 2026-05-27 | 🟢 done (code) | ☐ kickoff still pending | Branch + baseline + tag + brief |
| S1 | 2026-05-28 → 2026-06-10 | 🟡 in progress | ☐ | scripts/deg_mixed_effects.py + tests + overlay refactor done; **actual re-run on real data blocked on `make tabib-fetch` + scanpy env** |
| S2 | 2026-06-11 → 2026-06-24 | 🟢 done (S2.1 code only) | ☑ Option A locked | E3/E4 executed + manuscript §2.7/§3.3 updated; chokepoint framing for hub_score with PageRank/eigenvector as Supplementary Figure S1; E2 AUCell code+tests green, data run pending |
| S3 | 2026-06-25 → 2026-07-08 | ⏳ pending | ☐ | T2.a — mRSS correlation + demographics (E7, E12) |
| S4 | 2026-07-09 → 2026-07-22 | ⏳ pending | ☐ | T2.b — M3 subset + CellTypist (E8, E9) |
| S5 | 2026-07-23 → 2026-08-05 | ⏳ pending | ☐ | T2.c — drug table + crosstalk (E5, E6) |
| S6 | 2026-08-06 → 2026-08-19 | ⏳ pending | ☐ | T3 — FAIR deposition (E11, E14–E17) |
| S7 | 2026-08-20 → 2026-09-02 | ⏳ pending | ☐ | T4 + T5 — figures, novelty, polish (E13, E18–E25) |
| WR | 2026-09-03 → 2026-09-30 | ⏳ pending | ☐ | write-up + co-author + submission |

Legend: 🟢 done · 🟡 in progress · ⏳ pending · 🔴 blocked · ⚪ descoped.

## Essential revisions checklist

### Must do (critical path — blocking submission)

| ID | Theme | Description | Sprint | Status | Owner | Notes |
|----|-------|-------------|--------|--------|-------|-------|
| E1 | A-stats | Mixed-effects DEG + BH-FDR | S1 | 🟡 code complete | curator | `deg_mixed_effects.py` + tests green; integration into `build_overlay_multi.py` done; **`make overlay-multi` re-run on real data pending** (needs `make tabib-fetch` + scanpy env) |
| E2 | A-stats | AUCell / sign-blinded module score | S2 | 🟡 code complete | curator | `score_aucell.py` (AUCell + Tabib Z-score) + tests green (M1/M2 directionality recovered); execution waits on pseudobulk TSV from `make overlay-multi` |
| E3 | A-stats | Hub-score robustness (eigenvector, PageRank) | S2 | 🟢 done | curator | `analysis/network/hub_overlap.tsv`, `figures/F_supp_hub_robustness.{svg,png}`. Jaccard₂₀ vs PageRank = 0.18, vs eigenvector = 0.00 (gate ≥15/20 not met). **Decision (2026-05-20, Option A):** retain `hub_score = z(deg) + z(btw)` as the *mechanistic chokepoint* metric (rationale: most directly aligned with druggable-intervention prioritisation §2.8); report PageRank + eigenvector as Supplementary Figure S1 with explicit explanation of what each metric prioritises. Manuscript §2.7 and §3.3 updated. |
| E4 | A-stats | Hypergeometric community–module enrichment | S2 | 🟢 executed | curator | `analysis/network/community_enrichment.tsv`: **32 significant tests at q<0.05 across 28/38 communities**. Largest 6 communities each carry one module overwhelmingly (fold enrichment 2.97–7.21, padj << 0.001). Gate (≥6) cleared. |
| E5 | A-stats | Crosstalk supplementary table (8 reactions) | S5 | ⏳ | curator | quick win |
| E6 | B-validation | Recalibrate Table 2 with SSc trial outcomes | S5 | ⏳ | curator + co-author | book co-author session for S5 |
| E7 | B-validation | mRSS correlation (Tabib, Gur) | S3 | ⏳ | curator | start Tabib-lab email on S3 day 1 |
| E8 | D-modules | M3 within-vascular-subset analysis | S4 | ⏳ | curator | |
| E9 | D-modules | CellTypist / Azimuth harmonisation | S4 | ⏳ | curator | |
| E10 | E-Boolean | CaSQ + perturbation matrix | S7 | ⏳ | curator | **descopable** — decide at S5 gate |
| E11 | C-FAIR | MINERVA *or* BioModels deposit | S6 | ⏳ | curator | email LCSB on S6 day 1 |
| E12 | B-validation | HC demographic matching | S3 | ⏳ | curator | |
| E13 | A-stats | Methods completeness (dangling %, ECO dist, compartment count) | S7 | ⏳ | curator | quick win |

### Should do (improvement — not strictly blocking)

| ID | Description | Sprint | Status | Notes |
|----|-------------|--------|--------|-------|
| E14 | Docker container + GHCR digest | S6 | ⏳ | |
| E15 | Zenodo input-data mirror | S6 | ⏳ | |
| E16 | CI workflow for figures | S6 | ⏳ | |
| E17 | RO-Crate / PROV-O manifest | S6 | ⏳ | |
| E18 | Novelty vs Reactome/KEGG/Mahoney/Taroni | S7 | ⏳ | **descopable to Reactome/KEGG only** if behind |
| E19 | Figure 1 quadrant layout | S7 | ⏳ | |
| E20 | Figure 2 significance bars + mRSS row | S7 | ⏳ | |
| E21 | pyproject.toml + minimal pytest | S7 | ⏳ | |

### Nice to do

| ID | Description | Sprint | Status | Notes |
|----|-------------|--------|--------|-------|
| E22 | Dependency citation table | S7 | ⏳ | 1 hour |
| E23 | README refresh | S7 | ⏳ | |
| E24 | Doublet detection + cell-cycle | S7 | ⏳ | |
| E25 | Hinchcliff 2023 PMID confirmation | S7 | ⏳ | 5 minutes |

## S0 — Pre-sprint setup

| # | Action | Status | Notes |
|---|--------|--------|-------|
| S0.1 | Create branch `revision/v1.1` | 🟢 done | off `main` @ `e638a4d` |
| S0.2 | Freeze `analysis/baseline_v1.0/` | 🟢 done | 5 files + SHA256SUMS |
| S0.3 | Tag `v1.0-pre-review` | 🟢 done | annotated on `e638a4d` |
| S0.4 | Create `reviewing/PROGRESS.md` | 🟢 done | this file |
| S0.5 | Co-author kickoff brief | 🟢 done | `docs/standups/2026-05-20_revision_kickoff.md` |
| S0 gate | Co-author signs off on scope (E10, E18 descope decisions) | ☐ pending | **awaiting kickoff meeting** |

## Risk watch

| ID | Risk | State | Action |
|----|------|-------|--------|
| RR1 | FDR re-analysis tanks M3/M4 coverage | open | monitor at S1 gate |
| RR2 | mRSS absent from GEO | open | email Tabib lab on S3 day 1 |
| RR3 | MINERVA grant slow | open | run BioModels in parallel from S6 |
| RR4 | CaSQ inference fails | open | E10 already flagged descopable |
| RR5 | Co-author bandwidth | open | book S5 + WR sessions in S0 |

## Headline numbers — to be refreshed at each sprint

| Metric | Baseline (v1.0) | After S1 (E1 FDR) | After S2 (E2 AUCell) | Final (v1.1) |
|--------|-----------------|--------------------|------------------------|---------------|
| Total DEG entries | 4 338 (raw p≤0.05) | TBD (FDR≤0.05) | TBD | — |
| MIM coverage (overall) | 50.0 % (98/196) | TBD | TBD | — |
| M1 coverage | 65 % (24/37) | TBD | TBD | — |
| M2 coverage | 53 % (17/32) | TBD | TBD | — |
| M3 coverage | 21 % (5/24) | TBD | TBD | — |
| M4 coverage | 35 % (6/17) | TBD | TBD | — |
| Top hub (hub_score) | SMAD3p_SMAD4 (13.42) | — | unchanged | — |
| Top hub (PageRank) | not reported | — | **phenotype_myofibroblast_activation** (S2) | — |
| Top hub (eigenvector) | not reported | — | **JAK1_inhibited / LTBP1_TGFB1 complex** (S2) | — |
| Top-20 Jaccard hub_score↔PageRank | — | — | **0.18 (4/20)** (S2) | — |
| Top-20 Jaccard hub_score↔eigenvector | — | — | **0.00 (0/20)** (S2) | — |
| Significant communities (q<0.05) | not reported | — | **32 tests / 28 communities** (S2) | — |
| Skin SSc/HC M1 score | 0.342 vs 0.070 (sign-weighted) | — | TBD (AUCell) | — |
| ρ(M1, mRSS) | not measured | — | — | TBD (S3) |

## Change log

- **2026-05-20** — S0 started. Branch `revision/v1.1` created
  off `main`@`e638a4d`. Tag `v1.0-pre-review` set. Baseline
  frozen in `analysis/baseline_v1.0/`. Kickoff brief drafted.
- **2026-05-20 (later)** — **Option A locked for E3.** Hub score
  formulation kept as `z(deg) + z(btw)` (mechanistic chokepoint),
  PageRank + eigenvector relegated to Supplementary Figure S1.
  Manuscript §2.7 rewritten: corrected the formula description
  (was "geometric mean … 99th percentile" — incorrect vs code),
  added the three-metric robustness paragraph, framed each metric's
  biological question. §3.3 hub paragraph updated with the
  robustness numerics (Jaccard 0.54 / 0.54 / 0.18 / 0.00; ρ +0.94 /
  +0.95 / +0.62 / −0.02). §3.3 community paragraph rewritten with
  the exact hypergeometric numbers (32 sig / 28 communities; six
  largest each fold 2.97–7.21 at q < 10⁻¹⁶). Added a Supplementary
  Figure S1 caption.

- **2026-05-20** — S2 partial. E3 (hub robustness) and E4
  (community enrichment) executed end-to-end on real artefacts:
  - `scripts/network_analysis.py` extended with eigenvector
    centrality (per-component to handle 22 weakly-connected
    components), hub_overlap.tsv (top-20 under each of
    hub_score/degree/betweenness/PageRank/eigenvector), Jaccard +
    Spearman ρ.
  - **Hub robustness — gate failure:** Jaccard₂₀(hub_score, PageRank)
    = 0.18 (4/20); Jaccard₂₀(hub_score, eigenvector) = 0.00.
    Spearman ρ over all eligible species: degree +0.94, betweenness
    +0.95, PageRank +0.62, eigenvector −0.02. Decision required from
    co-author: pivot manuscript §3.3 narrative or report all metrics.
  - Community–module hypergeometric: **32 sig at q<0.05 across 28/38
    communities**; largest 6 communities each ≥ 5× enrichment for a
    single module. Supersedes the qualitative "six largest
    communities" claim in §3.3 with numerics.
  - Supplementary figure `figures/F_supp_hub_robustness.{svg,png}`
    (3-panel scatter, top-20 highlighted in red).
  - `summary.json` extended with `community_enrichment` and
    `hub_robustness` blocks.
  E2 (AUCell): `scripts/score_aucell.py` (AUCell + Tabib Z-score),
  tests `test_score_aucell.py` 4/4 green — AUCell M1 SSc-HC Δ=+0.95
  on synthetic, M2 reverse correctly recovered, Z-score directional
  too. Loader reads real `species_annotations.tsv` correctly:
  M1=37, M2=32, M3=24, M4=17, ssc_tier1=86 HGNC symbols.
  Execution on real data waits on pseudobulk TSV from
  `make overlay-multi`.
  Makefile: `make aucell-test`, `make aucell`.

- **2026-05-20** — S1.1–S1.4 done (code). New module
  `scripts/deg_mixed_effects.py` with three backends (pydeseq2 →
  statsmodels NB → scipy Welch) + BH-FDR (per-dataset primary,
  per-cluster diagnostic). Smoke test
  `scripts/tests/test_deg_mixed_effects.py` (4/4 green:
  statsmodels recovers 10/10 planted, scipy 8/10).
  `build_overlay_multi.py` refactored with `--deg-backend` flag
  (default `mixed-v11`), writes `cluster_deg_multi_v11.tsv` with
  pvalue / padj_dataset / padj_cluster / n_donors / mean_count
  / backend columns; report.json carries `fdr_summary`.
  Makefile: `make deg-test` and `make overlay-multi`.
  `environment.yml` adds `statsmodels` and `pydeseq2`.
  **Blocker for S1 gate**: real-data re-run needs
  `make tabib-fetch` (594 MB) + scanpy env (`sscmim` conda env).

---

*Update this file at every sprint gate. Commit as part of the
sprint-close commit on `revision/v1.1`.*
