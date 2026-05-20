# REVISION ROADMAP — npj Systems Biology and Applications

> Detailed action plan to address the simulated peer-review run
> (`R1_systems_biology.md`, `R2_scRNAseq_clinical.md`,
> `R3_reproducibility.md`, `editor_decision.md`).
> Companion to `revision_plan.md` — this document is the *executable*
> roadmap with sprint structure, gates, deliverables, file paths and
> success metrics.

- **Decision to address**: Major Revision.
- **Editor essential revisions**: E1–E25 (see `editor_decision.md`).
- **Revision window**: 2026-05-21 → 2026-09-30 (≈ 19 weeks).
- **Re-review target**: R1 + R2.
- **Anchor branch**: `revision/v1.1` (created off `main` at the start
  of Sprint 0); merged back to `main` on submission tag `v1.1`.

---

## Executive summary

The revision is a **statistical and FAIR consolidation**, not a
re-curation. The map content is sound; what changes is (i) how
the analyses are run, (ii) how the results are framed, and (iii)
how the resource is deposited. Five themes (A–E from the editor
decision) become five tracks (T1–T5) here, executed across
seven sprints. Every sprint has a single gate and a clear
go/no-go on whether to keep an item in scope or descope it.

**Critical-path items** (cannot ship without):
E1, E2, E6, E7, E11, E13, E18.

**Descopable to v2.0 follow-up paper**:
E10 (CaSQ Boolean), E18 (Mahoney/Taroni novelty comparison).

---

## Tracks

| Track | Theme | Items | Owner | Wall-clock |
|-------|-------|-------|-------|-----------|
| **T1** | Statistical formalisation | E1, E2, E3, E4 | lead curator | 3 weeks |
| **T2** | External validation | E5, E6, E7, E8, E9, E12 | lead curator | 4 weeks |
| **T3** | Resource & FAIR deposition | E11, E14, E15, E16, E17 | lead curator | 2 weeks |
| **T4** | Manuscript & figures | E13, E18, E19, E20, E22, E23, E25 | lead curator + co-author | 1 week |
| **T5** | Boolean & engineering polish | E10, E21, E24 | lead curator (optional) | 1–2 weeks |

Tracks run partly in parallel; engineering polish (T5) can be
slipped into idle days. Statistical re-analysis (T1) gates
everything downstream because it changes the numbers cited in
the manuscript.

---

## Sprint structure

Seven sprints of two weeks each, plus a final write-up + submission
window. Each sprint ends with a gate that decides whether to
continue, descope, or pivot.

```
S0  2026-05-21 →   1 wk   pre-sprint (branch, baseline, freeze numbers)
S1  2026-05-28 →   2 wk   T1.a — DEG re-analysis (E1)
S2  2026-06-11 →   2 wk   T1.b — Score + network robustness (E2, E3, E4)
S3  2026-06-25 →   2 wk   T2.a — Clinical correlation + demographics (E7, E12)
S4  2026-07-09 →   2 wk   T2.b — M3 subset + cell-type harmonisation (E8, E9)
S5  2026-07-23 →   2 wk   T2.c — Drug-table recalibration + crosstalk (E5, E6)
S6  2026-08-06 →   2 wk   T3 — FAIR deposition (E11, E14, E15, E16, E17)
S7  2026-08-20 →   2 wk   T4 + T5 — figures, novelty, polish (E13, E18–E25)
WR  2026-09-03 →   3 wk   write-up + co-author + submission
```

The wall-clock is **15 weeks** from S0 start to submission tag,
leaving 3 weeks of buffer inside the 18 available. Submission
target: **2026-09-30**.

---

## S0 — Pre-sprint setup (2026-05-21 → 2026-05-27)

### Actions

- [ ] **S0.1** Create branch `revision/v1.1` off `main`.
- [ ] **S0.2** Freeze the **baseline numbers** that will be
  refreshed by T1 — copy
  `analysis/overlay/cluster_deg_multi.tsv`,
  `analysis/overlay/patient_module_scores_multi.tsv`,
  `analysis/network/summary.json` into
  `analysis/baseline_v1.0/` so we can show diffs.
- [ ] **S0.3** Tag the current state `v1.0-pre-review` for
  reproducibility of the submission.
- [ ] **S0.4** Write a `reviewing/PROGRESS.md` that tracks
  E1–E25 in a single table and is updated at every sprint
  gate.
- [ ] **S0.5** Co-author kickoff meeting — share
  `editor_decision.md`, `revision_plan.md`, this roadmap.
  Lock co-author availability for Sprint 5 (drug table) and the
  write-up.

### Deliverables

- `revision/v1.1` branch live.
- `analysis/baseline_v1.0/` frozen.
- `reviewing/PROGRESS.md` initial state (all E items
  pending).
- Meeting notes in `docs/standups/2026-05-2X.md`.

### Gate

- ☐ Co-author signs off on the revision scope (descope
  decisions for E10, E18 made explicitly).

---

## S1 — Statistical backbone, part 1 (2026-05-28 → 2026-06-10)

### Goal

Replace the per-cluster Wilcoxon DEG analysis with a
mixed-effects model and BH-FDR correction. Every downstream
number in the manuscript flows from this output.

### Actions

- [ ] **S1.1 (E1)** Implement mixed-effects pseudobulk DEG.
  - File: `scripts/build_overlay.py` (refactor),
    new module `scripts/deg_mixed_effects.py`.
  - Library choice: `pydeseq2` (deseq2 in Python) — robust,
    well-cited, supports random effects via
    `formula = "~ donor + group"`. Fallback: `dreamlet`
    via `rpy2`.
  - Output schema: same as
    `analysis/overlay/cluster_deg_multi.tsv` plus
    `padj`, `model`, `n_donors_ssc`, `n_donors_hc`.
- [ ] **S1.2** Apply BH-FDR per dataset
  (not per cluster — over-conservative). Report both per-dataset
  and global FDR.
- [ ] **S1.3** Re-run the full overlay pipeline:
  `make overlay-multi` against the new DEG function.
- [ ] **S1.4** Update
  `analysis/overlay/build_overlay_multi.report.json` schema
  to include the mixed-effects model formula and the n=donors
  per cluster.
- [ ] **S1.5** Recompute MIM coverage at FDR 0.05; commit the
  new numbers into `analysis/overlay/coverage_v1.1.json`.

### Expected change in numbers

- MIM coverage 50% → likely **35–42%** (FDR is more
  conservative; some n=4 clusters lose all hits).
- M1 coverage 65% → likely **45–55%** (broad signal survives).
- M3 coverage 21% → likely **15–20%** (already low; loses
  one or two species).
- M4 coverage 35% → likely **20–28%** (under-powered PBMC).
- Per-donor scores: directionally identical (SSc > HC) but
  with wider error bars.

### Deliverables

- `scripts/deg_mixed_effects.py` + tests.
- Refreshed `analysis/overlay/cluster_deg_multi.tsv`
  with `padj` and donor counts.
- `analysis/overlay/coverage_v1.1.json` for traceability.
- `reviewing/PROGRESS.md` updated: E1 ✅.

### Gate (S1)

- ☐ `make overlay-multi` runs end-to-end on the new DEG
  pipeline.
- ☐ Coverage drops by no more than 50% (i.e. ≥ 25% global).
  If lower, escalate — may indicate a model-spec issue.
- ☐ Decide whether to keep Wilcoxon as a sensitivity check
  (recommended: yes, report in supplementary).

---

## S2 — Statistical backbone, part 2 (2026-06-11 → 2026-06-24)

### Goal

Replace double-dipping module activation score; benchmark hub
score against alternative centralities; quantify community–module
enrichment with hypergeometric tests.

### Actions

- [ ] **S2.1 (E2)** Implement AUCell scoring.
  - File: `scripts/score_aucell.py` (new).
  - Library: `pyscenic.aucell` or a self-contained
    AUC-on-gene-rank implementation (≈ 80 lines).
  - Run on the four datasets using the **pre-specified**
    module gene sets (M1, M2, M3, M4, SSc-Tier1) — no
    SSc-vs-HC sign weighting.
  - Output:
    `analysis/overlay/patient_module_scores_aucell.tsv`.
- [ ] **S2.2** Also compute a sign-blinded Z-score variant
  (à la Tabib 2021) for robustness. Both metrics reported.
- [ ] **S2.3 (E3)** Add eigenvector centrality + PageRank to
  `scripts/network_analysis.py`. New columns in
  `analysis/network/centrality.tsv`: `eigenvector`,
  `pagerank`. New file
  `analysis/network/hub_overlap.tsv` listing top-20 per
  metric.
- [ ] **S2.4 (E4)** Hypergeometric tests for community–module
  enrichment.
  - In `scripts/network_analysis.py`, add an `enrichment`
    block: for each (community, module) pair, compute the
    hypergeometric p-value (`scipy.stats.hypergeom.sf`),
    BH-correct across all 38×5 = 190 tests.
  - Output: `analysis/network/community_enrichment.tsv`
    (`community`, `module`, `n_species`, `expected`,
    `pvalue`, `padj`, `significant`).

### Deliverables

- `scripts/score_aucell.py`, `analysis/overlay/patient_module_scores_aucell.tsv`.
- `scripts/network_analysis.py` extended.
- `analysis/network/hub_overlap.tsv`, `community_enrichment.tsv`.
- Supplementary Figure S1 draft: hub-score vs eigenvector
  vs PageRank scatter (3 panels).

### Gate (S2)

- ☐ Top-20 hubs by hub-score share ≥ 15/20 with eigenvector
  or PageRank ranking. If not, switch primary ranking to
  PageRank and update §3.3 narrative.
- ☐ At least 6 communities significant at q < 0.05; re-state
  the "six largest communities" claim with the exact number.

---

## S3 — Clinical correlation + demographics (2026-06-25 → 2026-07-08)

### Goal

Anchor the patient-stratification claim in real clinical metadata
(mRSS, disease duration, demographics). Highest-leverage item
for the npj-SBA audience.

### Actions

- [ ] **S3.1 (E7)** mRSS extraction.
  - For Tabib 2021 (GSE138669): parse the `series_matrix.txt`
    for `!Sample_characteristics_ch1` rows containing
    `modified rodnan` or `mRSS`. If absent, contact
    corresponding author via email.
  - Fallback: use **disease duration** (months since
    Raynaud onset) as a continuous covariate; this is
    universally available in SSc GEO metadata.
  - For Gur 2022 (GSE195452): parse `series_matrix.txt`,
    extract mRSS, disease duration, ANA specificity
    (Scl-70 / centromere / RNA-pol-III).
  - Output: `analysis/clinical/donor_metadata.tsv`.
- [ ] **S3.2** Correlate M1, M2, M3, M4 AUCell scores with
  mRSS — Spearman ρ + 1000-iteration bootstrap CI.
  - New script: `scripts/clinical_correlation.py`.
  - Output: `analysis/clinical/module_mrss_correlation.tsv`.
  - New supplementary figure F4: per-module scatter plot.
- [ ] **S3.3 (E12)** Demographic matching of HC.
  - Extract age, sex per donor from each dataset.
  - Sensitivity analysis: re-run mRSS / module-score
    contrast restricted to a propensity-matched HC subset
    (using `scikit-learn` `LogisticRegression` or
    `pymatch`).
  - Output: `analysis/clinical/demographics.tsv` +
    `analysis/clinical/sensitivity_matched_hc.tsv`.

### Risk

If mRSS is not in any GEO metadata file, the email-the-Tabib-lab
fallback can take 2–4 weeks; budget it as a parallel item from
S3.1 (start the email on the first day of S3).

### Deliverables

- `analysis/clinical/donor_metadata.tsv` + correlations.
- New §3.4 paragraph + supplementary figure F4 + Table S5.
- Conditional: if ρ(M1, mRSS) > 0.3 with p < 0.05, **promote
  to a main-text finding**; otherwise soften to "exploratory".

### Gate (S3)

- ☐ At least one of (mRSS / disease duration / ANA) recovered
  for ≥ 50% of SSc donors across datasets.
- ☐ ρ(M1, clinical) reported with CI; sign and magnitude
  recorded in `PROGRESS.md`.

---

## S4 — M3 subset analysis + cell-type harmonisation (2026-07-09 → 2026-07-22)

### Goal

Close the M3 / EndoMT gap as far as the data allow. Harmonise
cell-type labels across the four datasets so that cross-tissue
claims rest on a uniform ontology.

### Actions

- [ ] **S4.1 (E8)** Vascular-subset scoring.
  - New script: `scripts/m3_vascular_subset.py`.
  - Filter Gur 2022 to `Vascular_ACKR1`, `Vascular_RBP7`,
    `Peri_RGS5`, `Peri_TGFBI`; re-run AUCell on M3 module
    within this subset.
  - Plot SNAI2, ACTA2, CDH5, FN1, CDH2, ZEB1, ZEB2 expression
    per cluster, per donor, SSc vs HC. Heatmap + violin.
  - Output: supplementary figure F5
    (`figures/F5_M3_vascular.svg`).
- [ ] **S4.2** Cell-fraction table — per dataset, fraction of
  cells annotated as endothelial / pericyte / vascular. Adds
  the denominator to the "why M3 is hard" argument in §4.5.
- [ ] **S4.3 (E9)** CellTypist harmonisation.
  - Install CellTypist; download
    `Immune_All_Low.pkl`, `Healthy_Adult_Skin.pkl`,
    and lung-relevant references.
  - Apply to the four datasets.
  - Compare to original labels — Cohen's κ.
  - Output: `analysis/overlay/celltypist_labels.tsv`,
    supplementary Table S2.
- [ ] **S4.4** Optional pseudotime — if time allows, run
  Slingshot or Monocle3 on Gur 2022 vascular clusters to
  show an EndoMT trajectory. This is gold-standard but
  ~3 days of work; if behind schedule, **descope** to a
  v2.0 follow-up.

### Deliverables

- Figure F5 + supplementary tables S2, S6.
- Updated §4.5 narrative with the cell-fraction denominator.

### Gate (S4)

- ☐ CellTypist κ ≥ 0.6 on at least three of the four
  datasets — confirms the cross-tissue cell-type claim.
- ☐ Decision on pseudotime — keep or descope; if descoped,
  add a paragraph in §4.5 acknowledging this as future work.

---

## S5 — Drug-table recalibration + crosstalk supplementary (2026-07-23 → 2026-08-05)

### Goal

Make Table 2 robust to clinical-trial reality; turn the 8
crosstalk reactions into an audit-grade supplementary table.

### Actions

- [ ] **S5.1 (E6)** Drug-target recalibration.
  - Manually annotate every row of Table 2 with:
    `latest_clinical_phase`,
    `SSc_specific_evidence` (trial name + readout),
    `key_limitations`.
  - Required citations to add to `pubmed_corpus.bib`:
    - Khanna 2020 — focuSSced phase 3 negative.
    - Rice 2015 — fresolimumab transcriptomic study.
    - Ebata 2021 — DESIRES rituximab.
    - Ferrarotto 2018 — brontictuzumab phase 1 GI tox.
    - Distler 2019 — SENSCIS / nintedanib (already cited).
    - Skaug 2020 *Ann Rheum Dis* — IFN-high/low SSc.
  - This is a **co-author item** — book the co-author for
    a 2-hour review session in this sprint.
- [ ] **S5.2 (E5)** Crosstalk supplementary table.
  - From `curation/ssc_curated_reactions.tsv`, extract the
    8 crosstalk rows; add `crosstalk_source_module` and
    `crosstalk_target_module` columns; ensure each has a
    PMID + ECO code stricter than 305.
  - Output:
    `manuscript/supplementary/S1_crosstalk_reactions.tsv`.
  - In the manuscript §3.1, cite the supplementary table.

### Deliverables

- Revised Table 2 with three new columns and updated narrative
  in §3.3 + §4.3.
- Supplementary Table S1 (crosstalk).
- Co-author sign-off on the drug-table content.

### Gate (S5)

- ☐ All 11 drug targets carry a clinical-phase annotation.
- ☐ Co-author signs off in writing (email or
  `docs/standups/2026-07-XX.md`).

---

## S6 — FAIR deposition (2026-08-06 → 2026-08-19)

### Goal

Move the resource from "GitHub-only" to "Disease Maps Project
citizen". Get MINERVA or BioModels live before submission.

### Actions

- [ ] **S6.1 (E11)** Decision: MINERVA *or* BioModels deposit.
  - **Path A — MINERVA (preferred)**: contact the
    MINERVA team at LCSB Luxembourg for a curator-role
    grant on the public instance; upload
    `curation/celldesigner/SSc_MIM_integrated.xml`;
    create per-module overlays from `minerva/overlays/`.
    Expected elapsed: 2–3 weeks. **Start the email on
    day 1 of S6.**
  - **Path B — BioModels (fallback)**: emit a
    MIRIAM-annotated SBML (E14 here as a prerequisite);
    submit via the BioModels submission portal; expected
    elapsed: 1–4 weeks.
  - Path A and B are **not mutually exclusive** — submit
    BioModels regardless, and chase MINERVA opportunistically.
- [ ] **S6.2 (E14)** Container image.
  - Write `Dockerfile` based on `mambaorg/micromamba:1.5`.
  - Add `.github/workflows/docker.yml` that builds and
    pushes to `ghcr.io/Nurtal/idt_ssc_map:v1.1` on a
    `v1.1` tag.
  - Cite the SHA-256 digest in manuscript §2.9.
- [ ] **S6.3 (E15)** Zenodo input-data mirror.
  - Tar each of the four GEO archives + their checksums.
  - Upload to a Zenodo "Dataset" deposit (one DOI for the
    whole mirror).
  - Record SHA-256 and DOI in `data/MIRROR.md`.
- [ ] **S6.4 (E16)** CI for figures.
  - Add `.github/workflows/figures.yml` that runs
    `make figures` and uploads PNGs as a workflow
    artefact.
  - Optional: pHash diff against committed figures with
    threshold.
- [ ] **S6.5 (E17)** RO-Crate manifest.
  - Run `ro-crate-py` to generate
    `ro-crate-metadata.json` at the repo root.
  - Reference in README and `.zenodo.json`.

### Deliverables

- BioModels submission ID (or MINERVA link).
- `Dockerfile` + GHCR image digest.
- `data/MIRROR.md` + Zenodo DOI.
- `.github/workflows/figures.yml`.
- `ro-crate-metadata.json`.
- Updated Data Availability Statement in the manuscript.

### Gate (S6)

- ☐ One of (BioModels submission, MINERVA live) is achieved.
- ☐ Container image builds in CI on the `v1.1-rc` tag.
- ☐ Zenodo DOI for input-data mirror minted.

---

## S7 — Manuscript polish + novelty comparison (2026-08-20 → 2026-09-02)

### Goal

Tighten the prose, regenerate the figures, quantify novelty,
finalise methods completeness.

### Actions

- [ ] **S7.1 (E13)** Methods completeness.
  - In §2.4: ECO code distribution table.
  - In §2.5: dangling fraction (17.9%), compartment count
    reconciliation (pick 17 or 20 and stick to it).
  - In §2.7: hub-score robustness as an addendum.
- [ ] **S7.2 (E18)** Novelty vs Reactome / KEGG / Mahoney /
  Taroni.
  - Scripted comparison:
    - **vs Reactome**: of the 260 reactions, count those
      derived from the 5 imported pathways vs SSc-Tier1
      additions. (Already 67% / 30% / 3% per the audit —
      just commit to numbers in the paper.)
    - **vs KEGG**: cross-reference HGNC symbols against
      KEGG pathway memberships (`hsa04350`,
      `hsa04060`, `hsa04630`); report Jaccard.
    - **vs Mahoney 2015 / Taroni**: download their
      network edge files (Mahoney's PLoS Comput Biol
      supplement is downloadable; Taroni's GitHub
      should have edges). Intersect top hubs.
  - Output: supplementary Figure S3 + Table S7.
  - **Descope option**: if Mahoney/Taroni edge files are
    not retrievable in 2 days, restrict to the
    Reactome/KEGG comparison and add a sentence
    acknowledging the gap. Reviewer R1 will accept this.
- [ ] **S7.3 (E19)** Figure 1 quadrant layout. Re-render
  with modules in fixed quadrants, sinks centred, crosstalk
  arcs across quadrants.
- [ ] **S7.4 (E20)** Figure 2 significance bars + mRSS
  annotations.
- [ ] **S7.5 (E22)** Dependency citation table in §2.9.
- [ ] **S7.6 (E23)** README refresh — move legacy timeline to
  `docs/historical_roadmap.md`.
- [ ] **S7.7 (E25)** Confirm Hinchcliff 2023 PMID/DOI.

### Optional (T5)

- [ ] **S7.8 (E10)** CaSQ + perturbation matrix — **only if
  S3 and S6 land on time**. Else descope.
- [ ] **S7.9 (E21)** `pyproject.toml` + minimal pytest.
- [ ] **S7.10 (E24)** Doublet detection + cell-cycle reporting
  in supplementary methods.

### Deliverables

- Refreshed manuscript draft (all numbers updated).
- Refreshed Figures F1, F2 (others as needed).
- Supplementary Tables S1–S7, Figures F4, F5.
- All Methods sections complete.

### Gate (S7)

- ☐ All E1–E13 essential items closed in `PROGRESS.md`.
- ☐ Decision on E10 (CaSQ): done or descoped with rewritten
  §4.5 paragraph.

---

## WR — Write-up and submission (2026-09-03 → 2026-09-30)

### Goal

Co-author iteration, point-by-point response, submission.

### Actions

- [ ] **WR.1** Lead curator drafts the **point-by-point
  response** using the template in `revision_plan.md`.
  Format: every reviewer comment quoted, bold the
  quantitative answer, cite the new manuscript paragraph.
- [ ] **WR.2** Co-author iteration — at least two rounds
  (Sept 7–14 and Sept 21–25).
- [ ] **WR.3** Final read-through: cross-reference all
  numbers in the abstract, results, discussion against the
  baseline-v1.1 outputs (`analysis/overlay/coverage_v1.1.json`
  etc.). No orphan numbers.
- [ ] **WR.4** Update `CITATION.cff` + `.zenodo.json` with
  v1.1 metadata.
- [ ] **WR.5** Tag `v1.1` on `main` after merge; trigger
  Zenodo DOI mint for the new release.
- [ ] **WR.6** Submit to npj-SBA with the cover letter,
  manuscript, supplementary, point-by-point response.

### Deliverables

- `manuscript/SSc_MIM_manuscript_v1.1.md` (revised draft).
- `manuscript/response_to_reviewers.md` (point-by-point).
- Submission package zip in
  `manuscript/submission_v1.1/`.
- Git tag `v1.1` + Zenodo DOI.

### Gate (WR — submission gate)

- ☐ Co-author signs off on the revised manuscript and
  point-by-point response.
- ☐ All numbers in abstract / Table 1 / Table 2 / Figure 2
  traceable to `analysis/baseline_v1.1/`.
- ☐ All essential E items closed (E1–E13 + selected E14+).

---

## Decision points (go / no-go gates)

| Gate | Date | Question | If yes | If no |
|------|------|----------|--------|-------|
| G-S0 | 2026-05-27 | Co-author signs off on revision scope? | proceed S1 | renegotiate descopes |
| G-S1 | 2026-06-10 | Mixed-effects DEG coverage ≥ 25%? | proceed S2 | inspect model spec, may extend S1 by 1 wk |
| G-S2 | 2026-06-24 | Hub-score top-20 stable across centralities? | proceed S3 | switch to PageRank, update §3.3 |
| G-S3 | 2026-07-08 | mRSS / clinical correlation produced? | proceed S4, foreground in main text | soften §4.4, keep exploratory |
| G-S4 | 2026-07-22 | CellTypist κ ≥ 0.6 on ≥ 3 datasets? | proceed S5 | descope harmonisation claim |
| G-S5 | 2026-08-05 | Co-author Table 2 sign-off? | proceed S6 | extend S5 by 1 wk |
| G-S6 | 2026-08-19 | BioModels or MINERVA live? | proceed S7 | submit with "in submission" framing |
| G-S7 | 2026-09-02 | E1–E13 closed? | enter WR | extend by 1 wk eating buffer |
| G-WR | 2026-09-30 | Submission package complete + signed off? | submit | push to 2026-10-07 (still inside Major-Revision window) |

---

## Risk register (revision-specific)

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| RR1 | FDR re-analysis tanks M3/M4 coverage | medium | high | pre-emptively soften narrative; report M1+M2 as primary, M3+M4 as exploratory |
| RR2 | mRSS not in GEO metadata | medium | high | email Tabib lab on day 1 of S3; fallback to disease-duration proxy |
| RR3 | MINERVA curator-role grant slow | high | medium | run BioModels in parallel; never depend on MINERVA alone |
| RR4 | CaSQ inference fails on integrated XML | medium | low | descope to v2.0; soften §4.5 |
| RR5 | Co-author bandwidth slips in August | medium | high | book the Aug 5 (S5 gate) and Sept 7 (WR) sessions on the calendar in S0 |
| RR6 | Mahoney/Taroni edge files irretrievable | medium | low | restrict E18 to Reactome/KEGG; add note |
| RR7 | Reviewer 2 disputes AUCell choice | low | medium | report Wilcoxon + Tabib Z + AUCell; methods triangulate |
| RR8 | Docker image not reproducible in CI | low | medium | pin micromamba digest, lock environment.yml |
| RR9 | Zenodo input-mirror exceeds free quota | low | low | use sample subsets or request quota increase |
| RR10 | Submission deadline slip beyond Major-Revision window | low | high | weekly progress check; if 2+ weeks behind by S5, descope T5 aggressively |

---

## Acceptance criteria for the revision

The revision is ready when **all of the following** are true.

### Code / data

- `make auto` on a fresh clone reproduces every number in the
  manuscript end-to-end.
- `analysis/overlay/coverage_v1.1.json` matches §3.2 numbers
  to ≥ 2 decimal places.
- `analysis/clinical/module_mrss_correlation.tsv` exists or
  the §4.4 framing is softened.
- `analysis/network/community_enrichment.tsv` exists; §3.3
  cites it.
- Docker image is build-able and tag-pushed.
- BioModels submission ID or MINERVA URL is in §2.9.

### Manuscript

- Abstract caveat on module-coverage heterogeneity (per R1-m9).
- Table 2 has `latest_clinical_phase`, `SSc_specific_evidence`,
  `key_limitations`.
- §4.3 cites Khanna 2020 (focuSSced failure) and Rice 2015
  (fresolimumab).
- §4.5 either reports CaSQ results or rewrites Boolean as v2.0.
- All numbers in abstract / Table 1 / Table 2 traceable to a
  file under `analysis/`.
- Reference list refreshed (Hinchcliff confirmed, Khanna 2020,
  Rice 2015, Ebata 2021, Ferrarotto 2018 added).

### Process

- `reviewing/PROGRESS.md` shows all E1–E13 as ✅.
- Point-by-point response covers every reviewer comment.
- Co-author signs off in writing on the final draft.
- Git tag `v1.1` pushed; Zenodo DOI minted; both cited in the
  cover letter.

---

## Out-of-scope items (parked for v2.0)

The following came up in the review but are **explicitly
deferred** to a follow-up paper, with the agreement that this
will be stated honestly in the limitations:

- CaSQ + MaBoSS Boolean perturbation simulation (E10).
- Mahoney 2015 / Taroni consensus-network overlap (E18, full).
- Pseudotime trajectory analysis of EndoMT in Gur 2022
  vascular clusters (S4.4).
- M3-targeted single-cell profiling of SSc digital ulcer
  biopsies (future dataset acquisition).
- Lung M1 alveolar IFN analysis (Distler 2019 / Khanna 2020
  context, R2-C3).
- Anti-Scl70 vs anti-centromere stratification (R2-C4) — needs
  serology metadata not in current datasets.
- v2.0 organ extensions (pulmonary arterial hypertension,
  renal, GI).

These should be listed as "Future directions" in the revised
§4.5, with a one-line rationale each.

---

## Communication plan

- **Co-author sync**: bi-weekly 30-min call at every sprint
  boundary (S0, S1 end, S2 end, ...). Live notes in
  `docs/standups/`.
- **PROGRESS.md** updated at every sprint gate. This is the
  authoritative status — replaces ad-hoc emails.
- **GitHub project board**: optionally create a "revision"
  board on the GitHub repo with the E1–E25 cards.
- **Editor**: no contact during revision unless a major
  descoping decision (E10, E18) is forced — in which case
  email a heads-up.

---

## How to use this document

1. **Start with `PROGRESS.md`** (created in S0). It is the
   1-screen status table. This roadmap is the playbook;
   `PROGRESS.md` is the dashboard.
2. **Before each sprint**: re-read the sprint section here,
   update goals if the previous gate moved the picture.
3. **At each gate**: run the gate-check questions; update
   `PROGRESS.md`; commit + tag the sprint outcome on the
   `revision/v1.1` branch (`sprint-S1`, `sprint-S2`, ...).
4. **If schedule slips by > 1 week** in any sprint, escalate
   to descoping decisions (T5 first, then T2 nice-to-haves).

---

*Generated 2026-05-20 alongside the simulated peer-review run.
Living document — update at every sprint gate.*
