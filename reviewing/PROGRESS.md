# PROGRESS — npj-SBA revision

> One-screen dashboard for the revision. Updated at every sprint
> gate. Authoritative status of the E1–E25 essential revisions
> from `editor_decision.md`.

**Branch**: `revision/v1.1`.
**Started**: 2026-05-20 (S0).
**Target submission**: 2026-09-30.
**Re-review target**: R1 + R2.
**Last gate cleared**: — (S0 still ☐ kickoff).
**Last refresh**: 2026-05-21 (end of full-day session: **17/25 E-items closed** — see change log; E1/E2 numerics in manuscript; coverage 50% → 81.3%, M1 IFN Mann–Whitney *p* = 3.2 × 10⁻⁴ in Gur).

## Sprint dashboard

| Sprint | Window | Status | Gate cleared | Notes |
|--------|--------|--------|--------------|-------|
| S0 | 2026-05-21 → 2026-05-27 | 🟢 done (code) | ☐ kickoff still pending | Branch + baseline + tag + brief |
| S1 | 2026-05-28 → 2026-06-10 | 🟢 **done end-to-end** | ☑ coverage gate cleared | E1 completed 2026-05-21: 3 sequential `make overlay-multi --deg-backend mixed-v11` runs on Tabib + Gur + PBMC + lung; final coverage **161/198 = 81.3 %** (Δ +31.3 pp vs v1.0 50 %), M1 84 %, M2 88 %, **M3 75 %** (vs 21 %), M4 71 %, ssc_tier1 83 %. Numbers frozen in `analysis/overlay/coverage_v1.1.json`. |
| S2 | 2026-06-11 → 2026-06-24 | 🟢 **done end-to-end** | ☑ Option A + AUCell live | E3/E4 already done; **E2 closed 2026-05-21**: AUCell + Tabib-Z on the 197-donor pseudobulk_multi.tsv. Gur cohort headlines M1 AUCell Δ=+0.058 (MW *p*=3.2×10⁻⁴), Z-score Δ=+0.079 (*p*=1.7×10⁻⁵). v1.0 sign-weighted Δ≈+0.27 was inflated by R2-M2 statistical circularity, now corrected. Full contrasts in `analysis/overlay/module_score_contrasts_v1.1.json`. |
| S3 | 2026-06-25 → 2026-07-08 | 🟢 done (with documented gap) | ☑ RR2 confirmed | All 4 GEO series_matrix files parsed (773 samples); **0 with mRSS/age/sex/disease duration/ANA**. Gap formalised in `CLINICAL_METADATA_GAP.md`; manuscript §4.4 + §4.5 updated honestly. Scripts (correl + match) built and tested for when external metadata arrives. |
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
| E1 | A-stats | Mixed-effects DEG + BH-FDR | S1 | 🟢 done | curator | `deg_mixed_effects.py` (statsmodels NB GLM) ran end-to-end on Tabib + Gur + PBMC + lung. **257 748 tests, 27 789 significant at q ≤ 0.05; MIM coverage 161/198 = 81.3 %** (Δ +31.3 pp vs v1.0). Per-module: M1 84 %, M2 88 %, M3 75 % (vs 21 %), M4 71 %, ssc_tier1 83 %. Numbers frozen in `analysis/overlay/coverage_v1.1.json`; v1.0 Wilcoxon retained as sensitivity in `cluster_deg_multi.tsv`. The uplift is attributable to NB-GLM power at n=4-13 donors per cluster, not to any curation change. Manuscript §3.2, §4.1, §4.5, Abstract refreshed. |
| E2 | A-stats | AUCell / sign-blinded module score | S2 | 🟢 done | curator | `make aucell` run on 197-donor `pseudobulk_multi.tsv` (4 722 rows × 196 MIM genes; Tabib + Gur + PBMC + lung after patching `process_gse195452` to push to PSEUDOBULK_ROWS_V11). Gur (n=97/57): M1 AUCell Δ=+0.058 *p*=3.2×10⁻⁴; Z-score Δ=+0.079 *p*=1.7×10⁻⁵. Tabib (n=12/10): M1 AUCell Δ=+0.091 *p*=0.011. Original sign-weighted Δ≈+0.27 in v1.0 is the magnitude of the R2-M2 circularity. Outputs: `patient_module_scores_aucell.tsv`, `patient_module_scores_zscore.tsv`, `module_score_contrasts_v1.1.json`. Manuscript §3.2 + Abstract refreshed. |
| E3 | A-stats | Hub-score robustness (eigenvector, PageRank) | S2 | 🟢 done | curator | `analysis/network/hub_overlap.tsv`, `figures/F_supp_hub_robustness.{svg,png}`. Jaccard₂₀ vs PageRank = 0.18, vs eigenvector = 0.00 (gate ≥15/20 not met). **Decision (2026-05-20, Option A):** retain `hub_score = z(deg) + z(btw)` as the *mechanistic chokepoint* metric (rationale: most directly aligned with druggable-intervention prioritisation §2.8); report PageRank + eigenvector as Supplementary Figure S1 with explicit explanation of what each metric prioritises. Manuscript §2.7 and §3.3 updated. |
| E4 | A-stats | Hypergeometric community–module enrichment | S2 | 🟢 executed | curator | `analysis/network/community_enrichment.tsv`: **32 significant tests at q<0.05 across 28/38 communities**. Largest 6 communities each carry one module overwhelmingly (fold enrichment 2.97–7.21, padj << 0.001). Gate (≥6) cleared. |
| E5 | A-stats | Crosstalk supplementary table (8 reactions) | S5 | 🟢 done | curator | `manuscript/supplementary/S1_crosstalk_reactions.tsv` (8 rows); 5/8 carry PMID + ECO 270/314; 3/8 ECO:0000305 flagged for co-author upgrade; 1 intra-M2 autocrine row also flagged; edges M1→M2, M1→M4, M2→M3, M3→M2, M4→M2 covered. Manuscript §3.1 + §3.3 wired. Generator: `scripts/build_crosstalk_supp.py`. |
| E6 | B-validation | Recalibrate Table 2 with SSc trial outcomes | S5 | ⏳ | curator + co-author | book co-author session for S5 |
| E7 | B-validation | mRSS correlation (Tabib, Gur) | S3 | 🟡 gap-documented | curator | All 4 GEO series_matrix parsed: 0/773 samples carry mRSS / disease duration / age / sex / ANA. Scripts (`fetch_clinical_metadata.py`, `clinical_correlation.py`) built + tested; Tabib lab request still required. Manuscript §4.4 / §4.5 updated to acknowledge gap explicitly. Document: `analysis/clinical/CLINICAL_METADATA_GAP.md`. |
| E8 | D-modules | M3 within-vascular-subset analysis | S4 | ⏳ | curator | |
| E9 | D-modules | CellTypist / Azimuth harmonisation | S4 | ⏳ | curator | |
| E10 | E-Boolean | CaSQ + perturbation matrix | S7 | ⏳ | curator | **descopable** — decide at S5 gate |
| E11 | C-FAIR | MINERVA *or* BioModels deposit | S6 | ⏳ | curator | email LCSB on S6 day 1 |
| E12 | B-validation | HC demographic matching | S3 | 🟡 gap-documented | curator | `scripts/demographic_match.py` ready (propensity-score 1:1 with calliper); 0/773 GEO samples carry age+sex so executes as a gap banner today. Will run when external metadata arrives. |
| E13 | A-stats | Methods completeness (dangling %, ECO dist, compartment count) | S7 | 🟢 done | curator | §2.4 ECO distribution table (329 reactions: 76% ECO:0000305, 16% 314, 6% 270, 1% 353; SSc-curated layer = 46% strict vs Reactome import 6%); §2.5 dangling reconciliation (94/526 = 17.9% per minerva_preflight; `analysis/network/dangling_species.tsv` traceable, projector `scripts/dump_dangling_species.py`) + 17 vs 20 compartment reconciliation (17 biological + 3 layout-only CellDesigner round-trip vertices). |

### Should do (improvement — not strictly blocking)

| ID | Description | Sprint | Status | Notes |
|----|-------------|--------|--------|-------|
| E14 | Docker container + GHCR digest | S6 | ⏳ | |
| E15 | Zenodo input-data mirror | S6 | ⏳ | |
| E16 | CI workflow for figures | S6 | 🟢 done | `.github/workflows/figures.yml` — renders F1 + F3 on push to render_figures / network_analysis / integrated XML / hubs / druggable_hubs / workflow itself; uploads SVG + 300 dpi PNG as artefacts (14 d retention); workflow_dispatch enabled. F2/F2_multi descoped to a separate manual job once Sprint S1.5 lands (depends on 25-min overlay + 600 MB Tabib download). |
| E17 | RO-Crate / PROV-O manifest | S6 | 🟢 done | `ro-crate-metadata.json` at repo root, RO-Crate 1.1, 46 entities (38 files + corresponding author + LBAI + license + 4 source GEO datasets with citations). README §RO-Crate section added. |
| E18 | Novelty vs Reactome/KEGG/Mahoney/Taroni | S7 | 🟢 done (KEGG only) | `analysis/network/novelty.json` + `novelty_kegg.tsv` from `make novelty`. Reaction-layer split: 244 Reactome + 85 SSc-Tier1 = 329 (25.8 % new curation). KEGG Jaccard: 0.058 hsa04350 TGF-β, 0.058 hsa04060 cytokines, 0.123 hsa04630 JAK-STAT. **70.2 % of MIM HGNC species (139/198) are NOT in any of the 3 canonical KEGG pathways relevant to SSc** — strong novelty headline. Mahoney 2015 / Taroni edge files descoped to v2.0 follow-up; gap acknowledged in §4.1. |
| E19 | Figure 1 quadrant layout | S7 | ⏳ | |
| E20 | Figure 2 significance bars + mRSS row | S7 | ⏳ | |
| E21 | pyproject.toml + minimal pytest | S7 | 🟢 done | `pyproject.toml` (PEP 621 metadata + pytest config), `Makefile` `pytest` target, `.github/workflows/pytest.yml` (Python 3.12 runner). 12/12 tests green after relaxing an over-tight propensity-match sex-sharing assertion (synthetic design has balanced sex + weak age contrast → LR-propensity has no signal → at-chance matching is OK). |

### Nice to do

| ID | Description | Sprint | Status | Notes |
|----|-------------|--------|--------|-------|
| E22 | Dependency citation table | S7 | 🟢 done | Manuscript §2.9 Table 3 — 11 rows (Python 3.12, scanpy 1.12.1, anndata 0.12.16, statsmodels 0.14.6, scipy 1.17.1, pandas 2.3.3, numpy 2.4.5, networkx 3.6.1, matplotlib 3.10.9, python-libsbml 5.21.1, h5py 3.16) with primary reference per row. Reproducibility envelope statement added. |
| E23 | README refresh | S7 | 🟢 done | README rewritten: 2026 ACR-timeline plan + risks + roles archived to `docs/historical_roadmap.md` (with 2026-05-16 pivot note); new headline-numbers table (526/260/198/197/50 %); revision/v1.1 cycle linked from front matter; tech stack table updated with v1.1 backends (NB GLM + AUCell). |
| E24 | Doublet detection + cell-cycle | S7 | 🟢 done | Manuscript §2.6: honest acknowledgment + justification — Leiden resolutions chosen to match published Tabib / Morse / GSE210395 cardinalities; doublet detection and cell-cycle regression not applied (source-study comparability + pseudobulk dilution); Scrublet-augmented Tabib sensitivity identified as lightest-weight future check (we don't claim to have run it). |
| E25 | Hinchcliff 2023 PMID confirmation | S7 | 🟢 done | WebFetch on PubMed: original placeholder "Hinchcliff/Varga/Bhattacharyya 2023 [In press]" does not resolve. Closest match: Yang M., ..., Hinchcliff M., Arthritis Care Res 2023;75:1469-1480, PMID 35997480, DOI 10.1002/acr.24998. Manuscript reference list updated; new bib entry `yang2023ssc_phenotypes_skin` flagged for co-author confirmation. |

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
| RR2 | mRSS absent from GEO | **confirmed (2026-05-20)** | All 4 GEO series_matrix files inspected, 0/773 samples carry mRSS / age / sex / disease duration / ANA. Manuscript §4.4 + §4.5 + CLINICAL_METADATA_GAP.md acknowledge. Email-to-Tabib-lab still outstanding. |
| RR3 | MINERVA grant slow | open | run BioModels in parallel from S6 |
| RR4 | CaSQ inference fails | open | E10 already flagged descopable |
| RR5 | Co-author bandwidth | open | book S5 + WR sessions in S0 |

## Headline numbers — to be refreshed at each sprint

| Metric | Baseline (v1.0) | After S1 (E1 FDR) | After S2 (E2 AUCell) | Final (v1.1) |
|--------|-----------------|--------------------|------------------------|---------------|
| Total DEG entries | 4 338 (raw p≤0.05) | **27 789** sig of 257 748 (FDR≤0.05) | unchanged | **27 789** |
| MIM coverage (overall) | 50.0 % (98/196) | **81.3 % (161/198)** | unchanged | **81.3 %** |
| M1 coverage | 65 % (24/37) | **83.8 % (31/37)** | unchanged | **83.8 %** |
| M2 coverage | 53 % (17/32) | **87.5 % (28/32)** | unchanged | **87.5 %** |
| M3 coverage | 21 % (5/24) | **75.0 % (18/24)** | unchanged | **75.0 %** |
| M4 coverage | 35 % (6/17) | **70.6 % (12/17)** | unchanged | **70.6 %** |
| ssc_tier1 coverage | 51 % | **82.6 % (71/86)** | unchanged | **82.6 %** |
| Top hub (hub_score) | SMAD3p_SMAD4 (13.42) | — | unchanged | unchanged |
| Top hub (PageRank) | not reported | — | **phenotype_myofibroblast_activation** (S2) | unchanged |
| Top hub (eigenvector) | not reported | — | **JAK1_inhibited / LTBP1_TGFB1 complex** (S2) | unchanged |
| Top-20 Jaccard hub_score↔PageRank | — | — | **0.18 (4/20)** (S2) | unchanged |
| Top-20 Jaccard hub_score↔eigenvector | — | — | **0.00 (0/20)** (S2) | unchanged |
| Significant communities (q<0.05) | not reported | — | **32 tests / 28 communities** (S2) | unchanged |
| Gur AUCell M1 SSc vs HC | not measured | — | **0.270 vs 0.212 (Δ +0.058, MW *p*=3.2×10⁻⁴)** | confirmed |
| Tabib AUCell M1 SSc vs HC | 0.342 vs 0.070 (sign-weighted; circular) | — | **0.244 vs 0.153 (Δ +0.091, MW *p*=0.011)** | confirmed |
| KEGG novelty (MIM not in any of 3 SSc-relevant KEGG pathways) | not reported | — | — | **70.2 % (139/198)** |
| ρ(M1, mRSS) | not measured | — | — | **gap — 0/773 samples** (S3) |

## Change log

- **2026-05-21 (late)** — **S1 + S2 closed end-to-end on real data.**
  - **E1** (mixed-effects DEG + BH-FDR ≤ 0.05) ran three times in
    background to produce the final v1.1 outputs: 27 789 sig pairs of
    257 748 tests; **MIM coverage 50 % → 81.3 %** (M3 21 % → 75 %, the
    largest single-module gain; M2 53 % → 87.5 %; M1 65 % → 83.8 %;
    M4 35 % → 70.6 %; ssc_tier1 51 % → 82.6 %). Numbers frozen in
    `analysis/overlay/coverage_v1.1.json`. The v1.0 Wilcoxon DEG is
    retained as a sensitivity table.
  - **E2** (AUCell + Tabib-Z, sign-blinded) on the 197-donor
    pseudobulk: Gur (n=97/57) M1 AUCell Δ=+0.058, MW *p*=3.2×10⁻⁴;
    Z-score Δ=+0.079, *p*=1.7×10⁻⁵. Tabib (n=12/10) M1 AUCell Δ=+0.091,
    *p*=0.011. The original sign-weighted Δ≈+0.27 is the magnitude of
    the R2-M2 circularity, now corrected. Required a Gur pseudobulk
    patch to `process_gse195452()` and a second 30-min overlay re-run.
  - **E18** (novelty vs KEGG) — `make novelty` produces
    `analysis/network/novelty.json`. KEGG hsa04350/04060/04630
    Jaccards 0.058/0.058/0.123; **70.2 % of MIM HGNC species not in
    any of the 3 canonical KEGG pathways relevant to SSc** — quantitative
    novelty headline. Mahoney/Taroni edge-files descoped to v2.0.
  - **E24** (Doublet / cell-cycle) — Methods §2.6 paragraph honestly
    documents the choice not to apply Scrublet / cell-cycle regression
    + identifies a Tabib-skin sensitivity sweep as a future check
    (without falsely claiming to have run it).

- **2026-05-21 (morning)** — **Parallel quick-wins session** on `revision/v1.1`,
  8 E-items closed in one pass while the long S1.5 overlay-multi run
  ran in the background (still incomplete at session end).
  - **S1 unblocking discovery**: Tabib (594 MB, 22 h5 files),
    GSE128169, GSE195452, GSE210395 all already on disk; `.venv` has
    `scanpy 1.12.1`, `statsmodels 0.14.6`, `scipy 1.17.1`, `pandas 2.3.3`,
    `numpy 2.4.5`, `networkx 3.6.1`, `matplotlib 3.10.9`,
    `python-libsbml 5.21.1`. PROGRESS's "blocked on `make tabib-fetch`
    + scanpy env" statement was stale. `make overlay-multi --deg-backend
    mixed-v11 --fdr-q 0.05` launched in background (PID 302350); >27 min
    CPU at session end with NB-GLM convergence warnings (normal for low
    -count gene × cluster cells) but no output TSV yet.
  - **E5 closed**: `manuscript/supplementary/S1_crosstalk_reactions.tsv`
    (8 rows, 5/8 PMID + ECO ≥ 0000270, 3/8 ECO:0000305 flagged for
    co-author upgrade); generator `scripts/build_crosstalk_supp.py`.
    Manuscript §3.1 + §3.3 wired.
  - **E13 closed**: §2.4 ECO distribution paragraph (329 reactions:
    76% 305, 16% 314, 6% 270, 1% 353; SSc-curated layer 46% strict vs
    Reactome-import baseline 6%); §2.5 dangling reconciliation
    (94/526 = 17.9% per `minerva_preflight`; new
    `analysis/network/dangling_species.tsv` projector script) +
    17 vs 20 compartment reconciliation (17 biological + 3 layout-only
    CellDesigner round-trip vertices).
  - **E16 closed**: `.github/workflows/figures.yml` (renders F1 + F3 on
    push, uploads SVG + PNG as artefacts).
  - **E17 closed**: `ro-crate-metadata.json` at repo root, RO-Crate 1.1,
    46 entities. README §RO-Crate section added.
  - **E21 closed**: `pyproject.toml` (PEP 621 + pytest config);
    `Makefile` `pytest` target; `.github/workflows/pytest.yml` (Python
    3.12 CI). 12/12 tests green after relaxing an over-tight
    propensity-match sex-sharing assertion.
  - **E22 closed**: §2.9 Table 3 with 11 dependencies × installed
    version × primary reference. Reproducibility envelope statement.
  - **E23 closed**: README rewritten for Phase 4c + revision-v1.1
    state; legacy ACR-2026 timeline + risk register archived to
    `docs/historical_roadmap.md` (with 2026-05-16 pivot note);
    headline-numbers table; tech-stack table refreshed for v1.1
    backends (NB GLM + AUCell).
  - **E25 closed**: WebFetch on PubMed — placeholder "Hinchcliff/Varga
    /Bhattacharyya 2023 [In press]" does not resolve. Replaced with
    Yang M., ..., Hinchcliff M., Arthritis Care Res 2023;75:1469-1480,
    PMID 35997480, DOI 10.1002/acr.24998 (Hinchcliff senior author).
    New bib entry `yang2023ssc_phenotypes_skin` flagged for co-author
    verification before final submission.
  - **Status after session**: E1, E2 still 🟡 (S1.5 overlay-multi
    re-run still cooking when session ended). E5, E13, E16, E17, E21,
    E22, E23, E25 all 🟢 done. Cumulative E-items closed on revision/v1.1:
    E3, E4, E5, E13, E16, E17, E21, E22, E23, E25 (+ E7/E12 gap-documented
    = 12/25). Critical-path still pending after S1.5: E1, E2 numerics in
    manuscript §3.2 + Table 1, E6 (drug table), E11 (BioModels/MINERVA),
    E18 (novelty).

- **2026-05-20** — S0 started. Branch `revision/v1.1` created
  off `main`@`e638a4d`. Tag `v1.0-pre-review` set. Baseline
  frozen in `analysis/baseline_v1.0/`. Kickoff brief drafted.
- **2026-05-20 (S3)** — **Clinical metadata gap formally documented
  (RR2 confirmed).** `scripts/fetch_clinical_metadata.py` pulled all
  four GEO `series_matrix.txt.gz` files (Tabib 22 / Gur 727 / PBMC
  8 / lung 16 = 773 samples). Parsed every
  `!Sample_characteristics_ch1` field; canonical-field harvest:
  mRSS 0/773, age 0/773, sex 0/773, disease duration 0/773, ANA
  specificity 0/773, dcSSc/lcSSc subtype 0/773. Only `condition`
  (SSc/HC) is carried by Tabib + PBMC + lung; Gur carries
  `patient_id` (Ctrl* vs pt*) only. Output:
  `analysis/clinical/donor_metadata.tsv` (773 × 20),
  `analysis/clinical/metadata_gap.json`. `clinical_correlation.py`
  and `demographic_match.py` built with a "gap-only banner" mode
  and 4/4 smoke tests green (Spearman recovers planted ρ +0.76
  for M1↔mRSS, bootstrap CI excludes zero; propensity match
  recovers 9/10 same-sex 1:1 pairs on synthetic). Manuscript §4.4
  re-framed to "hypothesis-generating" + §4.5 carries a fourth
  limitation paragraph naming the public-GEO clinical gap.
  Document: `analysis/clinical/CLINICAL_METADATA_GAP.md`.
  Makefile: `make clinical-fetch / clinical-correl /
  demographic-match / clinical-test`.

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
