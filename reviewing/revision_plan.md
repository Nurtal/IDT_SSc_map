# Revision plan — author-side action checklist

> Companion to `editor_decision.md`. Maps each essential revision
> item (E1–E25) to a concrete change in code / curation / text, the
> approximate effort, the touched files, and a status flag.
> Use this file as the live working document during revision.

**Editor recommendation**: Major revision.
**Revision deadline target**: 30 September 2026.
**Re-review expected**: R1 + R2.

---

## Effort summary

| Bucket | Items | Wall-clock |
|--------|-------|-----------|
| Statistical re-analysis (E1–E5, E8, E12) | 7 | ~3 weeks |
| Clinical validation (E6, E7) | 2 | ~2 weeks |
| Resource deposition (E11, E14–E17) | 5 | ~2 weeks |
| Mechanistic modelling (E10) | 1 | 1 week (optional: descope) |
| Cell-type harmonisation (E9) | 1 | 1 week |
| Manuscript / figures (E13, E18–E20, E22, E23, E25) | 7 | ~1 week |
| Engineering polish (E21, E24) | 2 | ~3 days |

Total realistic effort: **8–10 weeks** of focused work for a single
operator. Within the 18-week budget but no buffer for surprises;
recommend descoping E10 (CaSQ) and E18 (Mahoney/Taroni) to a
follow-up if R2-themes consume more time than budgeted.

---

## Item-by-item plan

### E1 — Mixed-effects DEG with FDR

- **What**: Replace per-cluster Wilcoxon with a mixed model (donor as
  random effect) and BH FDR correction across all 4338 tests.
- **Files**: `scripts/build_overlay.py`, `analysis/overlay/cluster_deg_multi.tsv`,
  manuscript §2.6, §3.2, Table 1.
- **Library**: `pydeseq2`, `dreamlet`, or `glmmTMB` (R via rpy2).
- **Expected outcome**: 30–50% fewer significant hits at FDR 0.05;
  MIM coverage drops to ~35–45%. Update all narrative numbers.
- **Status**: ☐ not started.

### E2 — Sign-blinded module activation score (AUCell)

- **What**: Re-derive `patient_module_scores*.tsv` using AUCell
  on the module gene sets directly (no DEG-sign dependence).
- **Files**: new `scripts/score_aucell.py`, `analysis/overlay/patient_module_scores_aucell.tsv`,
  manuscript §2.6, §3.2, Figure 2.
- **Library**: `pyscenic` or a small custom AUC implementation.
- **Expected outcome**: M1 and M2 SSc/HC contrasts persist but
  with smaller effect sizes. Report both AUCell and the original
  score; AUCell becomes primary.
- **Status**: ☐ not started.

### E3 — Hub-score robustness

- **What**: Compute eigenvector centrality and PageRank in
  `network_analysis.py`; report top-20 overlap with current hub-score
  ranking.
- **Files**: `scripts/network_analysis.py`, new supplementary table
  `analysis/network/hub_overlap.tsv`, manuscript §2.7, §3.3.
- **Expected outcome**: ≥15/20 overlap is the goal; if lower, switch
  to PageRank as primary ranking.
- **Status**: ☐ not started.

### E4 — Hypergeometric tests for community–module enrichment

- **What**: For each of the 38 communities, run a hypergeometric
  test on each module label; BH-correct.
- **Files**: `scripts/network_analysis.py` (add `enrichment` block),
  new `analysis/network/community_enrichment.tsv`, manuscript §3.3.
- **Expected outcome**: 6–10 communities significant at q<0.05.
  Re-state §3.3 with the actual count and p-values.
- **Status**: ☐ not started.

### E5 — Crosstalk supplementary table

- **What**: Pull the 8 crosstalk reactions from
  `curation/ssc_curated_reactions.tsv` into a dedicated
  supplementary table with `crosstalk_target_module` column.
- **Files**: `curation/ssc_curated_reactions.tsv` (add column or
  filter), new `manuscript/supplementary/S1_crosstalk_reactions.tsv`.
- **Status**: ☐ not started. Pure data-massaging, ~2 hours.

### E6 — Drug-target recalibration (focuSSced, fresolimumab, RECITAL)

- **What**: Manually annotate Table 2 with `latest_clinical_phase`,
  `SSc_specific_evidence`, `key_limitations`. Cite Khanna 2020
  (focuSSced negative phase 3), Rice 2015 (fresolimumab), Ebata 2021
  (DESIRES rituximab), Ferrarotto 2018 (brontictuzumab toxicity).
- **Files**: manuscript §3.3 Table 2, §4.3, References.
- **Status**: ☐ not started. 1 day of literature + writing.

### E7 — mRSS correlation

- **What**: Pull mRSS metadata for Tabib 2021 SSc donors from GEO
  series matrix; compute Spearman ρ vs M1 and M2 module scores; add
  bootstrap CIs.
- **Files**: `scripts/clinical_correlation.py` (new), supplementary
  Figure S2, manuscript §3.2 / §4.4.
- **Risk**: mRSS may not be in the GEO metadata; fallback is to
  contact the Tabib lab or use disease duration as a proxy.
- **Status**: ☐ not started. Highest-leverage item for clinical
  framing.

### E8 — M3 within-vascular-subset analysis

- **What**: Re-run scoring restricted to Vascular_ACKR1, Vascular_RBP7,
  Peri_RGS5, Peri_TGFBI clusters from Gur 2022. Plot a heatmap of
  EndoMT markers (SNAI2, ACTA2, CDH5, FN1, CDH2, ZEB1) on these
  clusters.
- **Files**: `scripts/m3_vascular_subset.py` (new),
  `figures/F4_M3_vascular.svg` (new supplementary), §3.2, §4.5.
- **Status**: ☐ not started.

### E9 — CellTypist / Azimuth harmonisation

- **What**: Apply CellTypist `Immune_All_Low.pkl` and
  `Healthy_Adult_Skin.pkl` references to all four datasets; report
  Cohen's κ vs original labels.
- **Files**: `scripts/celltypist_harmonise.py` (new),
  `analysis/overlay/celltypist_labels.tsv`, supplementary table S2.
- **Status**: ☐ not started.

### E10 — CaSQ + perturbation matrix (or descope)

- **Option A — Run**: `casq` on the integrated XML →
  SBML-qual → `MaBoSS` perturbation simulation. Report KO/KI of
  the top-5 hubs and the change in the 4 sink phenotypes.
- **Option B — Descope**: rewrite §4.5 to position Boolean modelling
  as a v2.0 deliverable; remove "Boolean-readiness" framing from
  abstract and conclusion.
- **Recommendation**: descope unless the author has CaSQ familiarity
  and ~1 week of buffer. The map's value does not depend on a
  Boolean run.
- **Status**: ☐ pending decision.

### E11 — MINERVA / BioModels deposit

- **What**: One of (i) deploy on MINERVA Luxembourg public instance
  (requires curator-role grant, ~3 weeks elapsed); (ii) deposit on
  BioModels with curated MIRIAM URIs; (iii) state a deposit target
  date in the Data Availability Statement and provide the
  draft submission.
- **Files**: `minerva/deployment_notes.md`, manuscript §2.9, Data
  Availability.
- **Status**: ☐ pending decision. Critical for npj-SBA acceptability.

### E12 — Demographic matching for HC

- **What**: Compile age, sex per donor from each GEO metadata file.
  Re-run module scoring restricted to age/sex-matched HC subsets.
- **Files**: `scripts/demographic_check.py` (new), supplementary
  Table S3, §3.2 sensitivity paragraph.
- **Status**: ☐ not started.

### E13 — Methods completeness

- **What**: Add to §2.5 the final dangling fraction (17.9%), the
  ECO code distribution, and the compartment count reconciliation
  (17 in manuscript vs 20 in STATUS.md — pick one and stick to it).
- **Files**: manuscript §2.4, §2.5, Methods table.
- **Status**: ☐ not started. ~2 hours.

### E14 — Container image

- **What**: `Dockerfile` based on `micromamba-base`; build + push
  via GitHub Action on `v1.0` tag; cite digest in Methods §2.9.
- **Files**: `Dockerfile` (new), `.github/workflows/docker.yml`
  (new), README "How to reproduce" section.
- **Status**: ☐ not started.

### E15 — Zenodo mirror of input data

- **What**: Tar and upload the four GEO archives (decompressed RAW
  matrices + metadata) to a Zenodo dataset deposit; cite DOI.
- **Files**: `data/MIRROR.md` (new), Data Availability section.
- **Caveat**: ~5 GB; within Zenodo free tier.
- **Status**: ☐ not started.

### E16 — Figures regenerated in CI

- **What**: Add `figures` job to `.github/workflows/`; run
  `make figures` and upload as artefact.
- **Files**: `.github/workflows/figures.yml` (new).
- **Status**: ☐ not started.

### E17 — RO-Crate / PROV manifest

- **What**: Run `ro-crate-py` to generate `ro-crate-metadata.json`;
  cite in README.
- **Files**: `ro-crate-metadata.json` (new), README.
- **Status**: ☐ not started.

### E18 — Novelty vs Reactome / KEGG / Mahoney / Taroni

- **What**: Compute Jaccard of SSc-MIM species ∪ reactions vs each
  comparator. For the consensus networks, request the network
  edge files from Mahoney 2015 supplementary; intersect hubs.
- **Files**: `scripts/novelty_comparison.py` (new), supplementary
  Figure S3.
- **Recommendation**: descope to "Reactome only" if time-limited;
  Mahoney/Taroni comparison is more valuable but harder.
- **Status**: ☐ not started.

### E19 — Figure 1 quadrant layout

- **What**: Re-layout the global MIM with modules in fixed quadrants
  (M1 NE, M2 SE, M3 SW, M4 NW), sinks centred, crosstalk arcs.
- **Files**: `scripts/make_figure1.py` (or whatever generates F1),
  `figures/F1_global_MIM.{svg,png}`.
- **Status**: ☐ not started.

### E20 — Figure 2 significance bars + mRSS annotation

- **What**: Add asterisks per panel header (Wilcoxon/Mann-Whitney
  p-value of SSc vs HC); add row-side mRSS / disease-duration color
  bar where available.
- **Files**: `scripts/make_figure2.py`, `figures/F2_multi_overlay.{svg,png}`.
- **Status**: ☐ not started.

### E21 — Packaging + pytest

- **What**: Minimal `pyproject.toml`, move scripts under
  `src/ssc_mim/`, add `tests/` with 4–6 golden-file tests.
- **Files**: `pyproject.toml`, `src/ssc_mim/`, `tests/`.
- **Status**: ☐ not started.

### E22 — Dependency citation table

- **What**: Methods §2.9 — add a table with scanpy / libSBML /
  NetworkX / pandas / matplotlib versions and references.
- **Files**: manuscript §2.9.
- **Status**: ☐ not started. ~1 hour.

### E23 — README refresh

- **What**: Move legacy timeline to `docs/historical_roadmap.md`;
  update README front-matter to reflect Phase 4c complete + Zenodo
  DOI + BioModels deposit (when assigned).
- **Files**: `README.md`, `docs/historical_roadmap.md` (new).
- **Status**: ☐ not started.

### E24 — Doublet / cell-cycle / resolution

- **What**: Add Scrublet to `build_overlay.py`; report
  doublet fractions and cell-cycle score per cluster.
- **Files**: `scripts/build_overlay.py`, supplementary tables.
- **Status**: ☐ not started.

### E25 — Hinchcliff 2023 reference confirmation

- **What**: PubMed lookup for confirmed PMID / DOI.
- **Files**: `curation/pubmed_corpus.bib`, manuscript References.
- **Status**: ☐ not started. 5 minutes.

---

## Suggested execution order

Week 1–2: **E1, E2, E3, E4** — statistical backbone.
  All downstream numbers depend on these.

Week 3: **E5, E13, E22, E23, E25** — easy text / table fixes.

Week 4: **E7, E12** — clinical metadata work. Highest leverage.

Week 5: **E6, E8** — drug-target table + M3 vascular subset.

Week 6: **E9** — cell-type harmonisation.

Week 7–8: **E11, E14, E15, E16, E17, E21** — deposition + engineering.

Week 9: **E19, E20** — figures.

Week 10: **E18** — novelty comparison (or descope).

Week 11–12: **E10** if pursued; otherwise descope and rewrite §4.5.

Week 13–14: integration, writing, point-by-point response, buffer.

Week 15–18: buffer for surprises, co-author iteration, submission.

---

## Risk register for the revision

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| FDR re-analysis removes much of M3/M4 coverage | medium | already low; soften narrative pre-emptively |
| mRSS metadata not in GEO | medium | contact Tabib lab; use disease duration as proxy |
| MINERVA deployment slips | high | fall back on BioModels deposit (E11.ii) |
| CaSQ inference fails on complex SBML | medium | descope to v2.0 (E10.B) |
| Reviewer 2 disagrees with sign-blinded score | low | report both; AUCell is well-known |

---

## Author response template — point-by-point

For each reviewer comment, the response should follow this shape:

> **R1-M1 (novelty quantification vs Reactome)** — We thank the
> reviewer for raising this. We now report (Methods §2.X, new
> Supplementary Table S4) that of the 260 reactions in SSc-MIM, 175
> (67%) are derived from Reactome import, 8 (3%) are crosstalk
> reactions formalising cross-module mechanisms, and 77 (30%) are
> SSc-specific Tier-1 curations not present in Reactome. Of the
> 355 unique PMIDs, 222 (63%) are from SSc-specific primary
> literature... [continue]

Use the same template for every comment, and bold the key
quantitative claim that addresses the reviewer's concern.

---

*Last updated: 2026-05-20, generated alongside the simulated peer
review run.*
