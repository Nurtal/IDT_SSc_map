# SSc-MIM — ACR Convergence 2026 late-breaking abstract (DRAFT)

> Updated 2026-05-22 with v1.1 revision numbers (mixed-effects NB GLM +
> BH-FDR, sign-blinded AUCell, recalibrated drug table).
> Word target: 300 (ACR late-breaking limit — verify on portal before
> submission). Current body word count: ~295.

## Title

A Curated, SBGN-Compliant Molecular Interaction Map of Diffuse Cutaneous
Systemic Sclerosis with Multi-Tissue Single-Cell Transcriptomic Overlay
and Clinically-Recalibrated Drug-Target Prioritisation

## Authors

[TO BE FILLED: Nathan Foulquier¹, co-author² (rheumatology / internal
medicine), co-investigators from SSc study group]
¹ LBAI, UMR 1227 Inserm, CHU Brest, France
² REPLACE_ME

## Background

No curated mechanistic disease map exists for systemic sclerosis (SSc).
Available systems-level resources are limited to co-expression networks
and partial pathway diagrams, none interoperable with the Disease Maps
Project. We present SSc-MIM, the first SBGN-compliant Molecular
Interaction Map (MIM) for diffuse cutaneous SSc, paired with a
four-tissue single-cell transcriptomic overlay and a drug landscape
recalibrated against actual SSc clinical-trial outcomes.

## Methods

SSc-MIM was built in CellDesigner across four modules: M1 (type-I
IFN/cGAS–STING), M2 (TGF-β fibroblast-to-myofibroblast), M3
(EndoMT/vasculopathy), M4 (IL-6/IL-4/IL-13/B-cell). Reactome content
was augmented with 85 SSc-specific curated reactions (355 PMIDs,
MI2CAST-annotated). Four public scRNA-seq cohorts were integrated:
GSE138669 (Tabib, n=22), GSE195452 (Gur, n=154), GSE210395 PBMC (n=8),
GSE128169 SSc-ILD lung (n=13) — 266,884 cells, 197 donors (117 SSc /
80 HC). Differential expression used a pseudobulk negative-binomial GLM
with donor random effect and BH-FDR ≤ 0.05; per-donor module scores used
sign-blinded AUCell.

## Results

The map encompasses 526 species, 260 reactions, 17 compartments.
Transcriptomic overlay recovered **161/198 (81 %)** of detectable MIM
species (M1 84 %, M2 87 %, M3 75 %, M4 71 %). M1 (IFN-I) AUCell scores
were significantly higher in SSc than HC skin in the Gur cohort
(Δ = +0.058, Mann–Whitney *p* = 3.2×10⁻⁴; n=97/57) and the Tabib cohort
(Δ = +0.091, *p* = 0.011). Network analysis identified 38 communities;
SMAD3–SMAD4, TGFB1 and NICD1 were the top three hubs. DGIdb returned
21 SSc-relevant drug-target interactions; clinical-trial recalibration
identifies nintedanib (SENSCIS) as the only SSc-indicated agent,
rituximab (DESIRES, RECITAL) as the strongest B-cell candidate,
tocilizumab as IL-6-high-subset-specific (focuSSced), and JAK inhibitors
as the emerging multi-axis convergence.

## Conclusion

SSc-MIM is the first curated SBGN disease map for SSc, providing a
mechanistic scaffold for pathway modelling and a clinically-grounded
framework for drug repurposing in dcSSc. Openly released on GitHub
(CC-BY-4.0 / MIT) with Zenodo DOI and BioModels deposit pending.

---

## Notes for editing

- Body word count target: ≤ 300 (ACR late-breaking limit — verify on portal).
- Author block must be filled before submission; co-author affiliation TBC.
- Zenodo DOI placeholder — fill after `git push --tags` triggers minting.
- BioModels submission ID — fill once received from the portal.
- One composite figure allowed.

## Figures

| ID | File | Status | Use |
|----|------|--------|-----|
| F1 | `figures/F1_global_MIM_quadrant.svg` | ready (v1.1) | global view, modules in fixed quadrants |
| F2 | `figures/F2_multi_overlay_aucell.svg` | ready (v1.1) | AUCell heatmap with MW significance bars |
| F3 | `figures/F3_druggable_targets.svg` | ready | druggable hub network |

For the single ACR composite, F2_multi_overlay_aucell is the most
clinically eloquent and is the recommended pick.

## What changed vs the 2026-05-19 draft (v1.0 numbers)

- Coverage 50 % → **81.3 %** (NB GLM + BH-FDR; v1.0 was per-cluster
  Wilcoxon at raw p ≤ 0.05 with no multiple-testing correction)
- Module scores: removed the v1.0 sign-weighted "0.342±0.095 vs 0.070±0.016"
  contrast (R2-M2 statistical-circularity issue) — replaced with
  AUCell + Mann–Whitney *p* in the well-powered Gur cohort
- Compartments stated as 17 (biologically meaningful), not 20 (raw SBML
  count including 3 layout-only CellDesigner round-trip vertices)
- Drug landscape: clinically-recalibrated (focuSSced, SENSCIS, DESIRES,
  RECITAL) instead of the original DGIdb-only listing
- Methods: explicit mention of mixed-effects pseudobulk GLM + BH-FDR
  (signals statistical rigour to the ACR clinical audience)
- F1 figure now references the v1.1 quadrant layout; F2 references the
  v1.1 AUCell + significance-bars version
