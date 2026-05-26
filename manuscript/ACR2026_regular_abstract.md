# SSc-MIM — ACR Convergence 2026 regular abstract (DRAFT)

> Generated 2026-05-26 against the v1.1 revision content.
> Word target: ≤ 250 (ACR regular abstract limit — verify on portal
> before submission; ACR counts the body sections only, not title /
> authors / institutional addresses).
> Current body word count: ~248.

## Title

From Mechanistic Map to Clinical Decision: A Curated Molecular Atlas of
Diffuse Cutaneous Systemic Sclerosis with Trial-Grounded Drug Repurposing

## Authors

Nathan Foulquier¹\*, REPLACE_ME² (rheumatology / internal medicine), [optional further co-investigators from the SSc study group]

¹ LBAI, UMR 1227 Inserm, CHU Brest, France
² REPLACE_ME
\* Presenting author — nathan.foulquier.pro@gmail.com

## Background

Systemic sclerosis (SSc) lacks a curated mechanistic disease map; existing
systems-level resources are co-expression networks or partial pathway
diagrams without standardised provenance. We constructed SSc-MIM, the first
SBGN-compliant Molecular Interaction Map of diffuse cutaneous SSc, and
applied it to multi-tissue single-cell transcriptomics and
clinical-trial-grounded drug prioritisation.

## Methods

SSc-MIM was built in CellDesigner across four modules — M1 type-I IFN,
M2 TGF-β fibroblast-to-myofibroblast, M3 EndoMT/vasculopathy, M4
IL-6/Th2/B-cell — with 85 SSc-specific curated reactions (355 PMIDs,
MI2CAST-annotated). Four scRNA-seq cohorts were integrated: Tabib
(GSE138669, n=22), Gur (GSE195452, n=154), GSE210395 PBMC (n=8), Morse
SSc-ILD (GSE128169, n=13) — 266,884 cells, 197 donors (117 SSc/80 HC).
Pseudobulk differential expression used a negative-binomial GLM with
donor random effect and BH-FDR ≤ 0.05; per-donor module scores used
sign-blinded AUCell. Top-hub drug targets were cross-referenced against
actual SSc trial outcomes.

## Results

The map encompasses 526 species and 260 reactions across 17 compartments.
Transcriptomic overlay recovered **161/198 (81 %)** of detectable MIM
species (M1 84 %, M2 87 %, M3 75 %, M4 71 %). The M1 IFN AUCell score was
significantly elevated in SSc skin in Gur (Δ = +0.058, Mann–Whitney
*p* = 3.2 × 10⁻⁴; n=97/57) and Tabib (*p* = 0.011). Recalibration
identified nintedanib (SENSCIS) as the only SSc-indicated agent,
rituximab (DESIRES, RECITAL) as the strongest B-cell candidate,
tocilizumab as IL-6-high-subset-specific (focuSSced), and JAK inhibitors
as emerging multi-axis convergence.

## Conclusion

SSc-MIM is the first curated SBGN disease map for SSc, providing a
mechanistic scaffold and a clinically-grounded framework for drug
repurposing in dcSSc. Openly released; Zenodo and BioModels deposits
pending.

---

## Notes for editing

- Body word count target: ≤ 250 (ACR Convergence regular abstract).
- Author block must be filled before submission (co-author affiliation TBC).
- ACR portal allows one composite figure for abstracts accepted to poster /
  oral presentation; the recommended pick is `figures/F2_multi_overlay_aucell.svg`
  (the AUCell 4-panel heatmap with Mann–Whitney significance bars — most
  clinically eloquent panel and directly traces the headline statistic).
- The companion late-breaking abstract (300 words) is preserved at
  `manuscript/ACR2026_late_breaking_abstract.md` for the September deadline,
  in case the regular June submission is missed.

## Difference vs the late-breaking draft

- Tighter (≤250 vs ≤300 words) — methods and drug paragraph compressed,
  Conclusion stripped to two sentences
- Author affiliation block kept short (ACR regular asks for primary
  institution only; secondary co-investigators move to acknowledgements)
- "ACR Convergence 2026" is not mentioned in the abstract body — only the
  metadata around it
- No mention of FAIR / Docker / RO-Crate — that level of methods detail
  belongs to the npj-SBA companion paper, not to an ACR clinical-audience
  abstract
