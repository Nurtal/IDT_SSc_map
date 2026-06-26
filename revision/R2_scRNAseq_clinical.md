# Reviewer 2 — Single-cell transcriptomics and clinical SSc

**Manuscript**: SSc-MIM: A Curated, SBGN-Compliant Molecular
Interaction Map of Skin Fibrosis in Diffuse Cutaneous Systemic
Sclerosis
**Author**: N. Foulquier
**Target journal**: npj Systems Biology and Applications
**Reviewer expertise**: scRNA-seq pipelines (scanpy / Seurat), SSc
clinical phenotyping, mRSS scoring, drug-trial design in SSc
(focuSSced, faSScinate, SENSCIS, FocuSSced, EUSTAR cohort).

---

## Overall recommendation

**Major revision.** The integration of four open-access scRNA-seq
datasets across skin (two), PBMC and lung is genuinely useful and the
50% MIM coverage is a reasonable result. However, the
clinical–biological interpretation goes beyond what the analysis
actually shows in several places, the statistics of the SSc-vs-HC
comparison are not robust to the underlying design (pseudobulk on
heterogeneous donor numbers), and the M3/EndoMT gap is more
fundamental than the manuscript acknowledges. The drug-repurposing
table should be calibrated against actual SSc trial outcomes.

---

## Major points

### M1. Donor counts, statistical power, batch effects

The four datasets contribute very different donor numbers (Tabib
n=22, Gur n=154, PBMC n=8, lung n=13). Pseudobulk Wilcoxon
comparisons with n=4 SSc vs n=4 HC (PBMC) and n=8 SSc vs n=5 HC
(lung) are severely underpowered, especially after multiple
hypothesis correction across ~200 MIM-mapped genes × 58 clusters.
Please:

- Report **per-comparison sample sizes** (SSc, HC) in every cluster
  used for testing, in a supplementary table. Some clusters in
  Gur 2022 may have <10 donors with non-zero counts after QC; those
  clusters should be flagged.
- Apply a **mixed-effects model** with donor as random effect
  (e.g. `glmmTMB`, `edgeR-LRT` with `donor` blocking, or
  `dreamlet`/`muscat` for pseudobulk) instead of plain Wilcoxon.
  Wilcoxon at n=4 has minimum p ≈ 0.029 (1/Cn,k) and cannot survive
  BH correction across 4338 tests.
- **Disclose multiple-testing correction.** The manuscript says
  "p ≤ 0.05" but does not state whether this is raw, FDR-adjusted
  per cluster, or per dataset. Given 4338 DEG tests, BH or
  Storey-q is essential. Please re-run with FDR ≤ 0.05 and report
  the change in the 98-species MIM coverage. I expect the M3 21%
  number to be unaffected (genuinely undetected), but M2 and M4
  fractions will likely move.

### M2. Module activation score — composite but unweighted

The score is defined as "the mean of gene-level expression weighted
by the sign of the DEG log₂FC" (§2.6). This has two problems:

- The score is **biased by gene panel size**. M1 has 37 detectable
  species, M3 has 24. A naïve mean cannot be compared directly
  across modules.
- The score uses **sign-weighting from the same data**, which is a
  form of double-dipping. The 0.342 vs 0.070 contrast in M1 is
  almost guaranteed by construction once the DEG set is selected
  on SSc-vs-HC sign.

Please re-state the score using an independent, sign-blinded
formulation. Two standard options:

- **AUCell** (Aibar 2017) — module enrichment without
  expression-derived signs.
- **Module Z-score** as in Tabib 2021 — average z-score across the
  pre-specified gene set, computed per donor.

Re-running with AUCell or a Tabib-style Z-score, on a held-out
gene set (or on the Whitfield 2003 intrinsic-subset signature as a
positive control), would substantially strengthen the patient
stratification claim. Without it, the manuscript reports an
in-sample optimistic effect.

### M3. M3/EndoMT coverage gap — biology vs methodology

§4.5 attributes the M3 coverage gap (21%) to legitimate biology
(transitional cells too rare, post-translational regulation of
NICD1, etc.). I largely agree, but the manuscript should:

- Quantify the **fraction of cells in each dataset annotated as
  endothelial / pericyte / vascular**. If <5% of cells, the
  pseudobulk simply cannot reach significance, and this should be
  reported explicitly.
- Test whether **scoring within the endothelial/pericyte subset
  alone** (rather than per-donor across all cells) recovers M3
  signal. The Gur 2022 vascular clusters (Vascular_ACKR1,
  Vascular_RBP7, Peri_RGS5, Peri_TGFBI) are the natural place to
  test EndoMT — a 4-cluster heatmap of SNAI2, ACTA2, CDH5, FN1,
  CDH2, ZEB1 expression would clinch the story.
- Acknowledge that EndoMT is canonically defined by *coordinated*
  loss of endothelial markers and gain of mesenchymal markers, and
  that DEG analysis on a heterogeneous endothelial population mixes
  EndoMT-committed and uncommitted cells. A pseudotime analysis
  (Slingshot / Monocle3) on the vascular clusters would be the
  gold standard but is acceptable as a future direction if
  acknowledged.

### M4. Drug-target priorities — calibration against SSc trial reality

Table 2 lists 11 drug targets with named candidate molecules. As a
reviewer with SSc-trial familiarity I would expect:

- **focuSSced (tocilizumab)** failed its mRSS primary endpoint in
  Phase 3 (Khanna et al. *Lancet Resp Med* 2020). The manuscript
  cites the Phase 2 faSScinate trial (Khanna 2016) but not the
  Phase 3 failure. This is essential context: it shows that
  network hub-score alone does not predict trial success, and the
  Discussion should explicitly address why.
- **Fresolimumab** (Rice et al. *J Clin Invest* 2015 — anti-TGF-β1/2/3
  in dcSSc skin) showed transcriptomic but not clinical benefit
  and was discontinued. Should be cited.
- **Rituximab** showed mixed results — DESIRES trial (Ebata 2021,
  *Lancet Rheum* 2021) suggested some benefit in skin and lung;
  RECITAL did not separate clearly. The manuscript over-simplifies.
- **Brontictuzumab** has reported on-target GI toxicity in the
  Phase 1 oncology trial (Ferrarotto 2018). This is a real
  limitation for SSc repurposing and should be flagged. The
  Notch pathway in SSc may be better targeted by gamma-secretase
  inhibitors (e.g. RG-4733, currently in non-SSc oncology trials),
  which the manuscript does not mention.
- **Anifrolumab** (anti-IFNAR1) has SLE approval but the only
  SSc evidence is preclinical / a phase 1 study with limited
  efficacy signal. Please down-weight from "approved" framing.

A revised Table 2 should add columns for `latest_clinical_phase`,
`SSc_specific_evidence` (trial name + outcome), and `key_limitations`.

### M5. Cell-type harmonisation across datasets

The four datasets use distinct cluster nomenclatures (Tabib
"myofibroblast" vs Gur "Fibro_ACTA2" vs lung "CXCL12⁺ fibroblast").
For the cross-tissue interpretation to hold, these must be
harmonised at a common ontology level. Please:

- Apply CellTypist or Azimuth annotation to all four datasets to
  produce a uniform Cell Ontology / CL term per cluster.
- Report the agreement (Cohen's κ or accuracy) between
  CellTypist labels and the original cluster labels.

Without this, claims like "M2 captures both skin and lung
fibrosis" rely on labels that the authors did not produce or
verify.

### M6. Clinical metadata — mRSS, disease duration, autoantibody status

Patient-level stratification (§4.4) is proposed but the manuscript
does not link module scores to any clinical variable. The Tabib
dataset has mRSS available in the GEO metadata; the Gur 2022 paper
reports skin disease duration and ANA specificity. Please:

- Pull mRSS for the 12 Tabib SSc donors and test correlation with
  M1 and M2 scores (Spearman, with bootstrap CI). If the
  correlation is significant and positive, this is a strong
  validation finding that should be highlighted. If not, the
  stratification claim should be retracted.
- Stratify the Gur 2022 donors by published clinical phenotype
  (early vs late, ANA specificity) and re-plot module scores.

### M7. Healthy-control definition

The HC group spans four different studies with different recruitment
criteria. No mention is made of age, sex, ethnicity or smoking
matching. For an SSc–HC contrast to be interpretable, please:

- Report demographic distributions per dataset.
- If possible, restrict to age- and sex-matched HC subsets and
  re-run module scoring. Even a sensitivity analysis would help.

---

## Minor points

### m1. Methods §2.6 — QC thresholds

The thresholds (200–6000 genes, <25% mito) are standard but should
be referenced (typically Luecken & Theis 2019 *Mol Syst Biol*). The
choice of 25% mito (vs the more common 10–20%) should be justified
for skin tissue, where higher mito content is expected.

### m2. Doublet detection

Not mentioned. Please add Scrublet or DoubletFinder, especially
for the multiome dataset where droplet-doublet rates are higher.

### m3. Cell-cycle regression

Some clusters (proliferating fibroblasts, especially in lung ILD)
may be driven by cell-cycle genes. Please report whether
cell-cycle scoring was applied and whether it affected clustering.

### m4. Resolution choice for Leiden

The chosen resolutions (skin 0.35, PBMC 0.5, lung 0.4) are
plausible but not justified. A `scIB` or `ClusTree` analysis
would justify the choices and is now standard.

### m5. SSc-ILD overlap with manuscript scope

The manuscript states the map covers dcSSc skin. The inclusion of
lung ILD overlay is a real strength, but the abstract should
clarify whether the map *itself* models SSc-ILD or whether the
lung dataset is used only to demonstrate the cross-tissue
generality of the M2 module (which I think is the case).

### m6. Gene-symbol alias clean-up — record of changes

15 alias corrections (BCMA→TNFRSF17, FSP1→S100A4 etc.) are
mentioned in STATUS.md but not in the manuscript. Please add as a
supplementary table; this is exactly the kind of provenance
information that reviewers and downstream users care about.

### m7. Detectability denominator (196/198)

§3.2 reports 196/198 (99%) detectable. The 2/198 undetected
species should be named — they are likely small / lowly-expressed
genes and the reasons are worth disclosing.

### m8. Lung ILD vs IPF

For the lung dataset (Morse 2019, GSE128169), please confirm
whether the SSc-ILD vs HC contrast is preserved when controlling
for ILD severity. Also note that aberrant basaloid cells (Adams
2020) are a distinct lung myofibroblast population in IPF/ILD
that the current MIM does not represent. Worth mentioning as a
known coverage gap.

### m9. ECM modules — granularity

COL1A1 is listed as a hub (rank 14). But COL1A1 expression is
present in essentially every fibroblast population in skin and
lung; the fact that it reaches significance does not mean it is
SSc-discriminative. Please add log₂FC values, not only
significance, for the top fibrosis-module hits.

### m10. SSc-MIM as a "first" map — geographical claim

"The first SBGN-compliant MIM for dcSSc" — please check that no
prior map exists in BioModels or in MINERVA hosted instances. A
quick check against the Disease Maps Project registry (covid19.dn,
parkinson, ra, sjd) appears to confirm the claim, but a sentence
documenting the negative finding would be reassuring.

---

## Specific clinical-interpretation concerns

### C1. mRSS connection

The manuscript repeatedly invokes mRSS (modified Rodnan Skin Score)
but never tests against it. For an SSc audience this is the single
most important external biomarker. Without it, the "patient
stratification" framing is hypothesis-only.

### C2. IFN-low vs IFN-high subgroups

The M1 distribution in Figure 2 looks bimodal in the skin biopsies
panel. If you can show that the bimodality corresponds to
clinically described IFN-high / IFN-low subgroups (Assassi 2010,
Skaug 2020 *Ann Rheum Dis*) this would be a major clinical finding
and should be foregrounded.

### C3. Lung ILD module M1 signal

§3.2 implies that the lung ILD dataset contributes mainly to M2.
But SSc-ILD is also characterised by alveolar IFN signatures
(Distler 2019, Khanna 2020). Please report the M1 score in the
lung dataset and explicitly state whether IFN is detected in
alveolar macrophages or pneumocytes.

### C4. Anti-Scl70 vs anticentromere stratification

The M4 module captures autoantibody output. Patients in Tabib 2021
include anti-topoisomerase-positive donors (dcSSc majority) and a
small number of anti-centromere-positive donors. Module M4 scores
likely differ between these subsets. If donor-level autoantibody
status is available, please stratify.

---

## Reproducibility / data provenance check

I pulled the four GEO accessions:
- GSE138669 (Tabib 2021) — available, 22 samples confirmed.
- GSE195452 (Gur 2022) — available, "Cell" reference confirmed.
- GSE210395 — available, pDC/monocyte enrichment confirmed.
- GSE128169 (Morse 2019) — available.

These are appropriate choices and the multi-tissue framing is
well-justified. The processing scripts
(`scripts/fetch_geo.py`, `scripts/build_overlay.py`) are present
and look reasonable on inspection.

---

## Summary of essential revisions (R2)

1. Re-run DEG with mixed-effects model + FDR correction; report
   per-cluster donor counts (M1).
2. Re-run module activation score with AUCell or independent
   Tabib-style Z-score; report the result (M2).
3. Add an endothelial/pericyte-subset M3 analysis (M3).
4. Recalibrate Table 2 with actual SSc trial phase + outcomes
   (M4).
5. Apply CellTypist / Azimuth for harmonised cell-type labels
   across datasets (M5).
6. Correlate module scores with mRSS where available; if no
   correlation, soften the stratification claim (M6, C1).
7. Report demographic matching for HC subsets (M7).

These changes are reachable from the existing data and code in
~6–8 weeks of curator + bioinformatician time. They would
substantially upgrade the manuscript from "interesting resource"
to "validated stratification tool".

---

*Confidential to the editor: I would be willing to re-review,
particularly to verify the FDR re-analysis and the mRSS correlation.*
