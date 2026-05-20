# Editor decision — npj Systems Biology and Applications

**Manuscript ID** (placeholder): NPJSBA-2026-MS-XXXX
**Title**: SSc-MIM: A Curated, SBGN-Compliant Molecular Interaction
Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis
**Corresponding author**: Nathan Foulquier (LBAI, UMR 1227 Inserm,
CHU Brest)
**Article type**: Research Article
**Date of editor synthesis**: 2026-05-20

---

## Decision

**Major Revision.**

I have now received and read three reports on your manuscript. All
three reviewers agree that the work addresses a real and current gap
(no curated SBGN MIM exists for systemic sclerosis), that the scope is
appropriate for npj Systems Biology and Applications, and that the
construction methodology is sound. Equally consistently, however, all
three identify substantive issues that must be resolved before the
manuscript can be considered for publication. None of the issues raise
fundamental concerns about the validity of the resource; they target
the *statistical formalisation* of claims, the *external validation*
of priorities, and the *FAIR / community-resource* dimension which is
central to npj-SBA's mission.

I am therefore offering a Major Revision. I anticipate that the
revised version will be returned to at least Reviewers 1 and 2 (R3's
concerns are mostly addressable without re-review).

---

## Editor's summary of reviewer convergence

The three reviewers' major points cluster naturally into five themes.
I list them in priority order; the revised manuscript should address
each.

### Theme A — Statistical formalisation of the analyses

- Hub-score definition is non-standard (R1-M3); please benchmark
  against a classical centrality (eigenvector or PageRank) and
  confirm the top-20 list is robust.
- Pseudobulk Wilcoxon at n=4–13 donors per dataset, with 4338 tests,
  is underpowered and lacks formal FDR correction (R2-M1). A
  mixed-effects model with donor blocking is required.
- The module activation score double-dips by using SSc-vs-HC sign
  for both DEG selection and scoring (R2-M2). Re-run with AUCell or
  a Tabib-style independent Z-score.
- Community–module enrichment claim ("six largest communities are
  significantly enriched for single modules") lacks the
  hypergeometric p-values (R1-M2).

### Theme B — External validation of priorities

- Correlate module activation scores with clinical mRSS in the Tabib
  donors and with disease duration / ANA specificity in the Gur
  donors (R2-M6, R2-C1). If correlations hold, foreground them; if
  not, retract the stratification claim.
- Recalibrate the drug-target table against actual SSc trial
  outcomes (focuSSced failure, fresolimumab discontinuation, RECITAL
  ambiguous, brontictuzumab GI toxicity in oncology phase 1)
  (R2-M4). Add `latest_clinical_phase`, `SSc_specific_evidence`, and
  `key_limitations` columns to Table 2.
- Quantify novelty against Reactome / KEGG (R1-M1.i–iii) and against
  the Mahoney 2015 / Taroni consensus networks (R1-M1).

### Theme C — Resource accessibility and FAIR compliance

- Either deploy on MINERVA at publication time or commit to a deposit
  date (R1-M5). The current GitHub+Zenodo-only release is below the
  npj-SBA community norm for systems biology resources.
- Deposit a MIRIAM-annotated SBML at BioModels (R3-M4). This is the
  expected standard.
- Provide a Docker / Apptainer image with cited digest (R3-M1).
- Add an RO-Crate or PROV-O provenance manifest (R3-M6).
- Mirror input datasets to Zenodo with checksums recorded (R3-M2).

### Theme D — Module-specific deepening

- M3 / EndoMT gap: report endothelial / pericyte cell fractions per
  dataset, run scoring restricted to vascular subsets, optionally
  pseudotime analysis on Gur 2022 vascular clusters (R2-M3).
- M3 hub definition: NICD1 is a cleavage product, not detectable by
  RNA-seq; the manuscript discusses this but should add the
  systematic table of "structurally undetectable" species to clarify
  the denominator (R1-m9, R2-M3).
- Cell-type harmonisation across the four datasets via CellTypist or
  Azimuth (R2-M5).

### Theme E — Boolean / mechanistic-modelling readiness

- The manuscript repeatedly invokes future Boolean modelling but does
  not demonstrate that CaSQ inference works on the integrated XML
  (R1-M4). Either run CaSQ and report a perturbation matrix on the
  top-5 hubs, or soften the language to "v2.0 deliverable, to be
  reported separately".

---

## Essential revisions (consolidated checklist)

The following must be addressed in a point-by-point response.
Numbers in brackets cross-reference the reviewer reports.

### Must do

- [ ] **E1.** Statistical re-analysis with mixed-effects DEG + BH-FDR
  correction; update §3.2 and Table 1 with corrected MIM coverage.
  *(R2-M1)*
- [ ] **E2.** Replace double-dipping module activation score with
  AUCell or a Tabib-style sign-blinded Z-score; update Figure 2 and
  §3.2 module-score numbers. *(R2-M2)*
- [ ] **E3.** Hub-score robustness analysis: report top-20 overlap
  with eigenvector or PageRank ranking. *(R1-M3)*
- [ ] **E4.** Hypergeometric tests for community–module enrichment,
  BH-corrected, with per-community p-values. *(R1-M2)*
- [ ] **E5.** Per-crosstalk-reaction supplementary table (the 8
  inter-module edges) with PMID, mechanism, ECO. *(R1-M2)*
- [ ] **E6.** Recalibrate Table 2 (drug priorities) against actual
  SSc clinical-trial outcomes; add focuSSced failure, fresolimumab
  discontinuation, RECITAL ambiguity, brontictuzumab toxicity.
  *(R2-M4)*
- [ ] **E7.** Correlate M1 and M2 module scores with mRSS for the
  Tabib donors; report Spearman ρ and bootstrap CI. *(R2-C1, R2-M6)*
- [ ] **E8.** Restrict M3 analysis to vascular / pericyte subsets;
  report SNAI2, ACTA2, CDH5, FN1, CDH2 in Gur 2022 Vascular_ACKR1,
  Vascular_RBP7, Peri_RGS5, Peri_TGFBI. *(R2-M3)*
- [ ] **E9.** CellTypist / Azimuth harmonised cell labels across the
  four datasets, with κ vs published labels. *(R2-M5)*
- [ ] **E10.** Either run CaSQ on the integrated XML and report a
  Boolean perturbation matrix, or soften §4.5 to make Boolean
  modelling an out-of-scope v2.0 deliverable. *(R1-M4)*
- [ ] **E11.** MINERVA deployment or, failing that, a public BioModels
  deposit; report the persistent identifier in the Data Availability
  Statement. *(R1-M5, R3-M4)*
- [ ] **E12.** Demographic matching for HC subsets across the four
  datasets; sensitivity analysis. *(R2-M7)*
- [ ] **E13.** Sink-node connectivity, dangling fraction, ECO code
  distribution, compartment count reconciliation (17 vs 20) reported
  in Methods. *(R1-m1, m3, m6, M1)*

### Should do

- [ ] **E14.** Container image (Docker/Apptainer) with digest cited in
  Methods. *(R3-M1)*
- [ ] **E15.** Zenodo-mirror the four input datasets, record SHA-256.
  *(R3-M2)*
- [ ] **E16.** CI workflow that regenerates the three main figures.
  *(R3-M3)*
- [ ] **E17.** RO-Crate or PROV-O manifest at repo root. *(R3-M6)*
- [ ] **E18.** Quantitative novelty comparison vs Reactome / KEGG and
  vs Mahoney 2015 / Taroni consortium consensus networks.
  *(R1-M1, R1-novelty section)*
- [ ] **E19.** Improved Figure 1 readability (quadrant layout with
  modules in fixed positions). *(R1-figures)*
- [ ] **E20.** Significance bars on Figure 2 panel headers; mRSS row
  annotation. *(R1-figures, R2-C1)*
- [ ] **E21.** Add `pyproject.toml` and a minimal `pytest` suite.
  *(R3-m2, m3)*

### Nice to do

- [ ] **E22.** Cite scanpy, libSBML, NetworkX, pandas in Methods
  table with version + reference. *(R3-m4)*
- [ ] **E23.** Refresh README to reflect Phase 4c state.
  *(R3-m1)*
- [ ] **E24.** Doublet detection, cell-cycle regression, Leiden
  resolution justification. *(R2-m2, m3, m4)*
- [ ] **E25.** Update reference 4 (Hinchcliff 2023) with confirmed
  PMID/DOI. *(R1-m8)*

---

## Reviewer recommendations at a glance

| Reviewer | Expertise | Recommendation | Re-review willing |
|----------|-----------|----------------|--------------------|
| R1 | Systems biology / disease maps | Major revision | yes |
| R2 | scRNA-seq / clinical SSc | Major revision | yes |
| R3 | Reproducibility / FAIR | Minor-to-major | not required |

The decision aligns with the **majority** recommendation. R3's more
favourable view reflects the strong software baseline; R1 and R2
correctly identify the *scientific* gaps that determine acceptability
in npj-SBA.

---

## Timeline

The author has indicated a v1.0 / Zenodo release target of August 2026
and the manuscript was drafted on 2026-05-19. I propose:

- **Revision returned** by: **30 September 2026** (≈ 18 weeks).
- **Re-review (R1 + R2)** by: end October 2026.
- **Final decision target**: mid November 2026.

This is compatible with the journal's median revision turnaround and
gives the author time for the FDR re-analysis (E1–E2) and the
mRSS correlation (E7) which are the most data-intensive items.

If the author elects to descope E10 (CaSQ) and E18 (Mahoney/Taroni
comparison) to a follow-up paper, this is acceptable provided that
the manuscript language is softened correspondingly.

---

## A note to the author

This is genuinely promising work. The map content, the multi-dataset
overlay, and the software hygiene are all above the journal baseline.
The current criticisms cluster around *quantifying claims that the
draft makes qualitatively*. Replacing narrative with numbers in the
five themes above should produce a manuscript that I would expect to
recommend for acceptance.

I would also encourage you to discuss with the editor whether to
split the work into a **methods/resource paper** (current draft, with
the revisions above) and a **stratification paper** (mRSS correlation,
patient subgroups, validation in PRESS/EUSTAR). The current draft is
strongest as a resource paper; the patient stratification claims in
§4.4 are the most extrapolated and could be the kernel of a stronger
second paper once external validation is available.

---

*Handling editor — npj Systems Biology and Applications*
*2026-05-20*
