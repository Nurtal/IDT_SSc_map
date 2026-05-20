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
| S0 | 2026-05-21 → 2026-05-27 | 🟡 in progress | ☐ | Branch + baseline + tag done; awaiting co-author kickoff |
| S1 | 2026-05-28 → 2026-06-10 | ⏳ pending | ☐ | T1.a — DEG re-analysis (E1) |
| S2 | 2026-06-11 → 2026-06-24 | ⏳ pending | ☐ | T1.b — AUCell + hub robustness + community enrichment (E2, E3, E4) |
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
| E1 | A-stats | Mixed-effects DEG + BH-FDR | S1 | ⏳ | curator | baseline frozen in `analysis/baseline_v1.0/` |
| E2 | A-stats | AUCell / sign-blinded module score | S2 | ⏳ | curator | |
| E3 | A-stats | Hub-score robustness (eigenvector, PageRank) | S2 | ⏳ | curator | |
| E4 | A-stats | Hypergeometric community–module enrichment | S2 | ⏳ | curator | |
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
| Top hub | SMAD3p_SMAD4 (13.42) | — | TBD (PageRank/eigenvector) | — |
| Significant communities (q<0.05) | not reported | — | TBD | — |
| Skin SSc/HC M1 score | 0.342 vs 0.070 (sign-weighted) | — | TBD (AUCell) | — |
| ρ(M1, mRSS) | not measured | — | — | TBD (S3) |

## Change log

- **2026-05-20** — S0 started. Branch `revision/v1.1` created
  off `main`@`e638a4d`. Tag `v1.0-pre-review` set. Baseline
  frozen in `analysis/baseline_v1.0/`. Kickoff brief drafted.

---

*Update this file at every sprint gate. Commit as part of the
sprint-close commit on `revision/v1.1`.*
