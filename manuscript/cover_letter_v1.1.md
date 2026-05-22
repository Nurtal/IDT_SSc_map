# Cover letter — npj Systems Biology and Applications, revision v1.1

> Draft prepared 2026-05-22 against the revision/v1.1 branch.
> Will be pasted into the submission portal (or attached as PDF) at
> the time of v1.1 tag push. `REPLACE_ME` placeholders to be filled
> by the lead author before submission.

---

**To**: Handling editor, *npj Systems Biology and Applications*
**From**: Nathan Foulquier, PhD (LBAI, UMR 1227 Inserm, CHU Brest)
        + co-author REPLACE_ME (rheumatology / internal medicine)
**Date**: REPLACE_ME (target: ≤ 2026-09-30)
**Re**: NPJSBA-2026-MS-XXXX — *SSc-MIM: A Curated, SBGN-Compliant Molecular Interaction Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis* — **Revision v1.1**

---

Dear Editor,

We are grateful for the constructive reviews from R1, R2, and R3, and for your concise editor synthesis. We are pleased to resubmit the manuscript above as revision v1.1, together with a point-by-point response (`manuscript/response_to_reviewers.md`) addressing each of the 25 essential revision items (E1–E25).

## How we approached the revision

The revision was framed as a **statistical and FAIR consolidation, not a re-curation**. The 526-species map content is unchanged; what changes is (i) how the downstream analyses are run, (ii) how the results are framed, and (iii) how the resource is deposited and made reproducible. The branch `revision/v1.1` carries 19 commits between the baseline tag `v1.0-pre-review` and the submission tag `v1.1` (which mints the Zenodo DOI on push), each one mapped to a specific E-item.

## Status of the 25 essential revisions

- **23 of 25 closed** at the data/code level. The cumulative dashboard is `reviewing/PROGRESS.md`; the live status of each E-item is tracked in `reviewing/REVISION_ROADMAP.md`.
- **E7 and E12 — clinical metadata** — remain *gap-documented* rather than closed (see "Adoption of your resource-paper framing" below). We systematically parsed all four GEO `series_matrix.txt.gz` files (773 donor-samples in total) and found **zero** carrying mRSS, disease duration, age, sex, or anti-Scl70 / centromere specificity. The full audit is in `analysis/clinical/CLINICAL_METADATA_GAP.md`. The analytical pipeline (`scripts/clinical_correlation.py`, `scripts/demographic_match.py`) is in place and validated on synthetic data; it will execute the moment cohort metadata becomes available.

## Key quantitative outcomes of the revision

- **Statistical re-analysis (E1, E2)** — replaced per-cluster Wilcoxon with a pseudobulk negative-binomial GLM with donor as a random effect and BH-FDR ≤ 0.05; replaced the DEG-sign-weighted module score with sign-blinded AUCell (R2-M2 circularity resolved). MIM coverage on the same species set rose from 50 % (v1.0) to **81.3 %** (v1.1), with the largest gain in the M3 EndoMT module (21 % → 75 %). M1 (IFN-I) signature in the Gur 2022 cohort: AUCell Δ = +0.058, two-sided Mann–Whitney *p* = 3.2 × 10⁻⁴ (n = 97 SSc / 57 HC).
- **Hub-score robustness (E3) and community enrichment (E4)** — addressed; 32 / 190 hypergeometric tests significant at q < 0.05 across 28 / 38 communities; hub-score top-20 retained as the *chokepoint* metric with PageRank + eigenvector reported in Supplementary Figure S1.
- **Module-specific deepening (E8, E9)** — M3 within-vascular-subset analysis (Supplementary Figure F5) clarifies that the M3 coverage gain is real but mechanistically diffuse, not driven by frank EndoMT TF expression in pseudobulk endothelium; CellTypist 1.7 label-transfer on Tabib agrees with the marker rule at Cohen's κ = 0.92 (coarse) / ARI = 0.70 (raw partition).
- **Drug-table recalibration (E6)** — Table 2 rewritten with three new columns (latest clinical phase, SSc-specific evidence, key limitations), explicitly flagging the gap between hub-score prioritisation (which ranks brontictuzumab and fresolimumab high) and clinical reality (brontictuzumab discontinued in oncology phase 1 with dose-limiting GI toxicity, Ferrarotto 2018; fresolimumab programme discontinued, Rice 2015; only nintedanib carries an SSc indication, SENSCIS).
- **FAIR deposition (E11, E14–E17)** — MIRIAM-annotated SBML variant (`SSc_MIM_integrated.biomodels.xml`, 206 HGNC + 526 taxonomy CVTerms) ready for the BioModels submission portal (submission ID REPLACE_ME); Docker image GHCR workflow on every `vX.Y` tag; Zenodo input-data mirror manifest with SHA-256 digests for the 3.09 GB of source archives; CI workflow for figures; RO-Crate 1.1 manifest at the repository root.
- **Novelty quantification (E18)** — KEGG comparison shows **70.2 %** of the 198 MIM HGNC species are not in any of the three SSc-relevant KEGG pathways (hsa04350, hsa04060, hsa04630). The Mahoney 2015 / Taroni consensus-network edge-list comparison is descoped to a follow-up paper (per the R1 acknowledgement that this descope is acceptable provided the gap is documented).
- **Boolean modelling (E10)** — CaSQ 1.4.4 runs end-to-end on the integrated XML and emits an 83-node, 98-input SBML-qual file (`analysis/boolean/SSc_MIM_integrated.sbml-qual.xml`); ISGF3, JAK1, STAT2, and STAT1 dominate by out-degree, consistent with the topological hub analysis. The full reachable-state-space perturbation matrix is **descoped to a v2.0 Boolean-modelling follow-up paper**, per your explicit allowance.

## Adoption of your resource-paper framing

We took to heart the closing note of your decision letter:

> *"I would also encourage you to discuss with the editor whether to split the work into a methods/resource paper (current draft, with the revisions above) and a stratification paper (mRSS correlation, patient subgroups, validation in PRESS/EUSTAR). The current draft is strongest as a resource paper; the patient stratification claims in §4.4 are the most extrapolated and could be the kernel of a stronger second paper once external validation is available."*

We have adopted this split. The revised §4.4 now positions SSc-MIM explicitly as a **resource paper** (curated map + transcriptomic coverage benchmark + network druggability analysis + FAIR release), and reserves the patient-stratification analysis for a planned follow-up study conditional on access to a clinically-annotated SSc cohort. The abstract has been adjusted in the same direction; "translational stratification" has been replaced with "community resource for mechanistic hypothesis generation and computational modelling". The infrastructure for the stratification paper (correlation + matching pipeline, gap-documentation) is in place on the same branch so that the follow-up can be executed the moment a clinically-annotated cohort becomes available — including via a request now pending with the corresponding author of GSE138669 (Tabib, Lafyatis group, Pittsburgh).

## What is in the submission package

| File | Purpose |
|---|---|
| `manuscript/SSc_MIM_manuscript_v1.1.md` (this revision) | Revised IMRAD manuscript |
| `manuscript/response_to_reviewers.md` | Point-by-point response (E1–E25) |
| `manuscript/supplementary/S1_crosstalk_reactions.tsv` | Supplementary Table S1 (E5) |
| `figures/F1_global_MIM_quadrant.svg` / `.png` | Figure 1, quadrant layout (E19) |
| `figures/F2_multi_overlay_aucell.svg` / `.png` | Figure 2, AUCell with MW significance (E20) |
| `figures/F3_druggable_targets.svg` / `.png` | Figure 3 |
| `figures/F_supp_hub_robustness.svg`, `figures/F5_M3_vascular.svg` | Supplementary Figures |
| GitHub repository | https://github.com/Nurtal/IDT_SSc_map (tagged `v1.1`) |
| Zenodo DOI | REPLACE_ME (minted on `v1.1` tag push) |
| BioModels submission ID | REPLACE_ME (pending lead-author upload of the MIRIAM-annotated SBML) |
| `ro-crate-metadata.json` | RO-Crate 1.1 manifest at repository root |
| Docker image | `ghcr.io/Nurtal/idt_ssc_map:v1.1` (digest REPLACE_ME, minted on tag push) |

## Reviewer re-allocation

We agree with the assessment that R1 and R2 should be returned the revision and that R3's concerns are addressable without re-review.

## Reproducibility envelope

`mamba env create -f environment.yml && conda activate sscmim && make auto` on a fresh clone at tag `v1.1` reproduces every TSV in `analysis/` and every figure in `figures/`. Headline-number traceability:

| Number cited | Source artefact | Make target |
|---|---|---|
| MIM coverage 81.3 % | `analysis/overlay/coverage_v1.1.json` | `make overlay-multi` |
| M1 AUCell Gur Δ = +0.058, *p* = 3.2 × 10⁻⁴ | `analysis/overlay/module_score_contrasts_v1.1.json` | `make aucell` |
| Community enrichment 32 sig / 28 communities | `analysis/network/community_enrichment.tsv` | `make network` |
| KEGG novelty 70.2 % | `analysis/network/novelty.json` | `make novelty` |
| CellTypist κ = 0.92 | `analysis/overlay/celltypist_kappa.json` | `make celltypist` |

---

We thank you again for the thoughtful review process and look forward to your decision.

Sincerely,

Nathan Foulquier, PhD
Data scientist, LBAI — Inserm UMR 1227
CHU Brest, France
ORCID 0000-0003-4620-2794

REPLACE_ME, MD, PhD
Co-author, REPLACE_ME affiliation
