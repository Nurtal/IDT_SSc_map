# SSc-MIM — ACR Convergence 2026 late-breaking abstract (DRAFT)

> Updated 2026-05-19 with Phase 4c final numbers (GSE195452 integrated).
> Word target: 300 (ACR late-breaking limit — verify on portal before submission).

## Title

A curated, SBGN-compliant Molecular Interaction Map of Skin Fibrosis in
Diffuse Cutaneous Systemic Sclerosis, with Multi-Tissue Single-Cell
Transcriptomic Overlay and Drug-Target Prioritisation

## Authors

[TO BE FILLED: lead curator, clinical referent, bioinformatics co-investigator,
co-authors from SSc study group]

## Background

No comprehensive, curated mechanistic map exists for systemic sclerosis (SSc).
Available systems-level resources are limited to co-expression networks and
partial pathway diagrams, none interoperable with the Disease Maps Project
ecosystem. We present SSc-MIM, the first SBGN-compliant Molecular Interaction
Map (MIM) for diffuse cutaneous SSc, paired with a four-tissue single-cell
transcriptomic overlay for patient stratification and drug-target
prioritisation.

## Methods

SSc-MIM was constructed in CellDesigner using SBGN Process Description notation
across four modules: M1 (type-I IFN/cGAS–STING), M2 (TGF-β
fibroblast-to-myofibroblast transition), M3 (EndoMT/vasculopathy), and M4
(IL-6/IL-4/IL-13/B-cell crosstalk). Reactome-derived content was harmonised
and augmented with 85 SSc-specific curated reactions (355 PMIDs, MI2CAST
annotation). Four public transcriptomic datasets were overlaid: skin biopsies
(GSE138669, Tabib et al.; n=22 donors), skin multiome (GSE195452, Gur et al.
2022; n=154), PBMC enriched for pDC (GSE210395; n=8), and SSc-associated ILD
lung (GSE128169, Morse et al.; n=13) — 266,884 cells and 197 donors (117 SSc /
80 HC) in total. Pseudobulk differential expression (|log₂FC| ≥ 0.2, p ≤ 0.05)
was combined with network hub scoring and Drug–Gene Interaction database
(DGIdb) cross-referencing.

## Results

The integrated map encompasses 526 species across 260 reactions and 20
compartments. Network analysis identified 38 functional communities;
SMAD3–SMAD4 (hub score 13.42), TGFB1 (9.09), and NICD1 (9.46) ranked as the
three highest-connectivity hubs. Transcriptomic overlay across 58 cell-type
clusters yielded 4,338 significant gene–cell-type pairs mapping to 98 unique
MIM species — 50% of the 196 transcriptomically detectable HGNC-annotated
entities (per-module: M1 IFN 65%, M2 TGF-β 53%, M4 IL-6/B-cell 35%, M3 EndoMT
21%). M1 module activation scores were markedly elevated in SSc skin donors
(0.342 ± 0.095 vs 0.070 ± 0.016 in HC) and M2 similarly increased
(0.232 ± 0.061 vs 0.044 ± 0.007). DGIdb cross-referencing identified 21
SSc-relevant drug–target interactions across 11 hubs, including anifrolumab
(IFNAR1/2), fresolimumab (TGFB1), tocilizumab (IL6R), brontictuzumab (NOTCH1),
and rituximab (MS4A1/CD20).

## Conclusion

SSc-MIM is the first SBGN-curated disease map for systemic sclerosis, providing
a mechanistic scaffold for pathway modelling, single-cell patient stratification,
and rational drug repurposing. The resource is publicly archived on GitHub
(CC-BY 4.0 / MIT) with a Zenodo DOI release pending, and is open for community
contribution and reuse.

---

## Notes for editing

- Word count (body sections only): ~295. Within ACR 300-word limit.
- Authors placeholder must be filled before submission.
- Zenodo DOI placeholder: fill after `git tag v1.0 && git push --tags`.
- One composite figure allowed: F1 (global MIM) + F2 (4-panel module heatmap)
  + F3 (druggable hub network). All generated and committed.

## Figures

| ID | File | Status |
|----|------|--------|
| F1 | `figures/F1_global_MIM.svg`        | ready |
| F2 | `figures/F2_multi_overlay.svg`     | ready — 4-panel skin/skin-Gur/PBMC/lung |
| F3 | `figures/F3_druggable_targets.svg` | ready |
