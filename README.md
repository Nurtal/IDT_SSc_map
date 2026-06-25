# SSc-MIM — Molecular Interaction Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis

> First curated, SBGN-PD-compliant Molecular Interaction Map (MIM) of diffuse cutaneous systemic sclerosis (dcSSc) skin fibrosis. Built in CellDesigner, MI2CAST-annotated, overlaid with four open-access single-cell transcriptomic datasets, and released as a GitHub + Zenodo resource.

[![SBML validate](https://github.com/Nurtal/IDT_SSc_map/actions/workflows/validate_sbml.yml/badge.svg)](https://github.com/Nurtal/IDT_SSc_map/actions)

**Current state (2026-06):** npj-SBA revision **v1.1 merged into `main`**. The SSc-specific layer has grown to **133 hand-curated reactions**; an offline reviewer app (`review/index.html`) and an AI citation-QC pass have been added. See [`STATUS.md`](STATUS.md) and the detailed reference [`docs/SSc_MIM_construction_and_validation.md`](docs/SSc_MIM_construction_and_validation.md).

**Lead author:** Nathan Foulquier — LBAI, UMR 1227 Inserm, CHU Brest. ORCID [0000-0003-4620-2794](https://orcid.org/0000-0003-4620-2794).

**Presentations & overview:**

- 📊 **General overview deck** — [PDF](docs/SSc_MIM_presentation.pdf) · [PPTX](docs/SSc_MIM_presentation.pptx) — what the map is, the four modules, the single-cell overlay, and the endotype workflow.
- 🛠️ **Construction & validation deck** — [PDF](docs/SSc_MIM_construction_deck.pdf) · [PPTX](docs/SSc_MIM_construction_deck.pptx) — how the map is built, the datasets used, and the interaction-validation process.
- 🧬 **Validation & endotypes deck** — [PDF](docs/SSc_MIM_validation_endotypes.pdf) · [PPTX](docs/SSc_MIM_validation_endotypes.pptx) — construction, validation (G0–G4 gates + patient data: datasets, pseudobulk, AUCell), and using the map to characterise SSc endotypes.
- 📚 **All three decks combined** — [PDF](docs/SSc_MIM_decks_combined.pdf) (51 pages, overview → construction → validation+endotypes).
- 📄 Detailed written reference: [`docs/SSc_MIM_construction_and_validation.md`](docs/SSc_MIM_construction_and_validation.md).

---

## Headline numbers (current — `main`, 2026-06)

| Quantity | Value | Notes |
|---|---|---|
| Species | **568** | across 20 cell/tissue compartments |
| Reactions | **308** | **133 are the hand-curated SSc-specific layer** (the original SSc contribution); 126/133 (95%) carry a primary PMID and 73 a direct-assay ECO code. Per module: M1 19 · M2 58 · M3 27 · M4 21 · crosstalk 8. Full evidence stratification in [`analysis/curation/evidence_stratification.md`](analysis/curation/evidence_stratification.md). |
| SBML validation | **0 errors** | libSBML L2v4, enforced in CI (`validate_sbml`) on every push |
| Annotated HGNC species | **236** | distinct HGNC symbols; 198 form the RNA-seq-detectable coverage denominator |
| Single-cell donors integrated | **197** | **121 SSc / 76 HC** across 4 datasets |
| Cells processed | **266 884** | Tabib skin / Gur skin multiome / GSE210395 PBMC / GSE128169 lung |
| MINERVA overlays | **60** | per-(dataset, cluster) overlay TSVs from the multi-dataset run |
| MIM coverage by transcriptomics | **≈50 % (robust) / 81.3 % (permissive)** | Effect-size-gated (≥2-fold, padj ≤ 0.01) = **49.5 % (98/198)**; the 81.3 % NB-GLM figure (161/198) is the permissive upper bound (\|log2FC\| ≥ 0.2). The 50→81 jump is a stringency/power effect, not biology — full grid in [`analysis/overlay/coverage_sensitivity.tsv`](analysis/overlay/coverage_sensitivity.tsv). Per module: M1 84 % · M2 88 % · M3 75 % · M4 71 %. |
| Network communities | **39** | greedy modularity; significant (community, module) hypergeometric enrichment at q < 0.05 |
| Druggable hub–drug interactions | **82** | DGIdb on top hubs; 28 distinct molecular targets |
| Interactions queued for expert review | **143** | reviewer app `review/index.html`; AI verdicts 128 validate / 5 caution |

---

## Table of contents

- [Rationale](#rationale)
- [Scope](#scope)
- [Methodology](#methodology)
- [Reuse strategy](#reuse-strategy)
- [Translational use case](#translational-use-case)
- [Repository layout](#repository-layout)
- [How to reproduce](#how-to-reproduce)
- [Tech stack](#tech-stack)
- [How to contribute](#how-to-contribute)
- [Releases and DOIs](#releases-and-dois)
- [References](#references)
- [License](#license)

The original 2026 ACR-timeline plan and pre-pivot risk register are archived in [`docs/historical_roadmap.md`](docs/historical_roadmap.md).

---

## Rationale

Comprehensive disease maps — curated, SBGN-compliant Molecular Interaction Maps (MIMs) built in CellDesigner and deployed via MINERVA — exist for Parkinson's disease (PD map), COVID-19 (COVID-19 Disease Map), rheumatoid arthritis (RA-map / RA-Atlas), the SYSCID coverage of RA / SLE / IBD, and Sjögren's disease (SjD map, 2025).

**No equivalent curated MIM existed for systemic sclerosis prior to this release.** Existing systems-level work on SSc was limited to:

- Co-expression and consensus-clustering networks on skin transcriptomes (Whitfield intrinsic subsets, Mahoney 2015, Taroni consensus).
- Comorbidity networks (e.g. SSc–cancer).
- Targeted sub-networks on individual pathways (TGF-β, IFN, fibrosis).

These resources are **not mechanistic, not SBGN-curated, and not interoperable with the Disease Maps Project ecosystem.** SSc-MIM addresses that gap with a focused, defensible scope.

## Scope

**Periphery:** Skin fibrosis in diffuse cutaneous SSc (dcSSc), with multi-tissue overlay (skin + PBMC + lung) for external generalisation.

**Four interconnected modules:**

| ID | Module | Rationale | Druggable handles |
|----|--------|-----------|-------------------|
| M1 | IFN-I signalling (cGAS–STING, IFNAR, JAK–STAT, ISG signature) | Documented IFN signature in SSc skin and blood; defines the inflammatory subset | Anifrolumab, JAK inhibitors |
| M2 | TGF-β / SMAD2/3 / fibroblast → myofibroblast transition; non-canonical MAPK/PI3K; YAP/TAZ; ECM remodelling | Central fibrotic axis | Fresolimumab, pirfenidone, nintedanib |
| M3 | Endothelial-to-mesenchymal transition (EndoMT) and vasculopathy; Notch/DLL4/NICD1, endothelin, VEGF | Bridge between vasculopathy and fibrosis; SSc-specific | Brontictuzumab, ambrisentan, macitentan |
| M4 | IL-6 / IL-4 / IL-13 Th2 axis and B-cell crosstalk | Validated targets in SSc trials | Tocilizumab, rituximab, dupilumab |

**Output phenotypes — six endpoints (sink nodes):** myofibroblast activation, ECM/collagen deposition, vascular remodelling, type-I IFN/ISG signature, **autoantibody production (autoreactivity)**, and skin severity (mRSS, clinical readout). The first four are the canonical biological sinks; autoantibody production captures SSc autoreactivity (M4) and mRSS the clinical-severity axis — analogous to the phenotype anchors used in RA-map.

## Methodology

The map follows the Disease Maps Project guidelines (Mazein et al., 2018; Ostaszewski et al., 2021; Mazein et al., 2023):

1. **Scoping** with domain experts (SSc clinicians).
2. **Reactome import** of TGF-β, IFN-α/β, IL-6, Notch1, PDGF pathways → CellDesigner harmonisation.
3. **SSc-specific curation** — 133 hand-curated reactions across the 4 modules (incl. 8 inter-module crosstalk). New edges are added only through a gated edge-discovery pipeline (G0–G4 anti-nonsense gates + human ratification; see [`docs/edge_discovery_protocol.md`](docs/edge_discovery_protocol.md)).
4. **Annotation** using the MI2CAST minimum information standard (HGNC, UniProt, PubMed/PMID, ECO evidence codes).
5. **SBML validation** with libSBML 5.21 (L2v4); 0 errors maintained in CI.
6. **Network analysis** — bipartite projection in NetworkX; degree, betweenness, eigenvector, and PageRank centralities; greedy-modularity communities; hypergeometric (community, module) enrichment.
7. **Multi-tissue single-cell overlay** — scanpy 1.12 pipeline on 4 datasets, pseudobulk DEG with mixed-effects negative-binomial GLM and BH-FDR (revision v1.1; v1.0 baseline used Wilcoxon).
8. **Drug-target prioritisation** via DGIdb v4 against the top 20 hubs.

## Reuse strategy

> Re-curating what other Disease Maps Project members have already curated is wasted effort. The project deliberately maximises import and adaptation.

| Source | Use |
|--------|-----|
| **Reactome** | Imports of `TGF-beta receptor signaling activates SMADs` (R-HSA-2173789), `Interferon alpha/beta signaling`, `IL-6 signaling`, `Notch1 signaling` (R-HSA-1980143), `Signaling by PDGF` |
| **RA-map / RA-Atlas** | Adaptation of JAK-STAT, IL-6, B-cell modules |
| **SYSCID map** | Adaptation of shared immune modules (IFN, NF-κB) |
| **WikiPathways** | EndMT-related pathways as scaffold for module M3 |

The SSc-specific layer has since grown to **133 hand-curated reactions** on top of the Reactome backbone; per-reaction Reactome overlap (originality of the SSc layer) is reported by `make reactome-novelty`.

## Translational use case

Four open-access transcriptomic datasets are overlaid on the MIM:

| Dataset | Tissue | Donors (SSc / HC) | Cells | Source |
|---|---|---|---|---|
| Tabib 2021 (GSE138669) | dcSSc skin | 12 / 10 | 64 211 | scRNA-seq, 10×; *Nat Commun* 12:4384 |
| Gur 2022 (GSE195452) | SSc skin multiome | 97 / 57 | 100 538 | RNA arm; pre-annotated; *Cell* 185:1373 |
| GSE210395 | SSc PBMC, pDC + monocyte-enriched | 4 / 4 | 34 619 | scRNA-seq |
| GSE128169 (Morse 2019) | SSc-ILD lung | 8 / 5 | 67 516 | 10× MEX; *Eur Respir J* 54:1802441 |

**Total: 197 donors (121 SSc / 76 HC).** Each cluster yields a MINERVA-format overlay TSV (`minerva/overlays/`; 60 from the multi-dataset run). Per-donor module activation scores (M1–M4 + SSc-Tier1) are computed from the pseudobulk DEG output; the sign-blinded **AUCell** score (Aibar 2017) replaces the v1.0 DEG-sign-weighted score. Externally-defined patient clusters can be projected the same way to obtain per-cluster module fingerprints and mechanistic hypotheses (see the construction deck and reference doc).

## Repository layout

```
ssc-mim/
├── README.md                          # this file
├── STATUS.md                          # one-screen project status (updated per batch)
├── ROADMAP.md                         # forward-looking phases (Phase 5+ / v1.0 release)
├── reviewing/                         # simulated peer-review + revision-v1.1 sprint plan
│   ├── editor_decision.md
│   ├── R{1,2,3}_*.md
│   ├── REVISION_ROADMAP.md
│   ├── revision_plan.md
│   └── PROGRESS.md
├── manuscript/
│   ├── SSc_MIM_manuscript_draft.md    # IMRAD draft, target: npj Syst Biol Appl
│   ├── ACR2026_late_breaking_abstract.md
│   └── supplementary/
│       └── S1_crosstalk_reactions.tsv # 8 inter-module crosstalk reactions (E5)
├── curation/
│   ├── celldesigner/                  # SBML XMLs (5 module + 1 integrated)
│   ├── imports/                       # Reactome / RA-map / SYSCID source XMLs
│   ├── ssc_curated_reactions.tsv      # 133 SSc-specific reactions
│   ├── staging/                       # edge candidates + G0–G4 validation_report.tsv
│   ├── ai_review_verdicts.json        # per-interaction advisory verdicts
│   ├── pubmed_corpus.bib              # 398 BibTeX entries
│   └── annotations/
│       ├── species_annotations.tsv    # 568 rows; 236 HGNC symbols
│       └── reaction_evidence.tsv      # 292 rows; 281 with PMID (96%)
├── analysis/
│   ├── network/                       # centrality, communities, hub_overlap, dangling_species, community_enrichment
│   ├── overlay/                       # cluster_deg_multi*.tsv, patient_module_scores*.tsv, druggable_hubs.tsv
│   ├── clinical/                      # donor_metadata, CLINICAL_METADATA_GAP.md, correlations (gap-banner v1.1)
│   ├── baseline_v1.0/                 # frozen pre-revision snapshot
│   └── boolean/                       # placeholder for v2.0 CaSQ work
├── review/                           # offline reviewer swipe-deck app (index.html)
├── minerva/
│   └── overlays/                      # per-cluster overlay TSVs (60 multi-dataset)
├── figures/
│   ├── F1_global_MIM.{svg,png}
│   ├── F2_multi_overlay.{svg,png}     # 4-panel skin/skin-Gur/PBMC/lung
│   ├── F3_druggable_targets.{svg,png}
│   └── F_supp_hub_robustness.{svg,png}# Supplementary Figure S1 (E3)
├── scripts/                           # 60 Python scripts; Makefile-orchestrated
├── docs/
│   ├── SSc_MIM_presentation.{pptx,pdf}            # general overview deck
│   ├── SSc_MIM_construction_deck.{pptx,pdf}       # construction & validation deck
│   ├── SSc_MIM_construction_and_validation.md     # detailed written reference
│   ├── module_specs/                  # M1–M4 spec sheets
│   ├── edge_discovery_protocol.md     # the G0–G4 gating procedure
│   ├── curation_guidelines.md
│   └── mi2cast_checklist.md
└── .github/workflows/                 # validate_sbml + lint + scripts-smoke
```

## How to reproduce

```bash
git clone https://github.com/Nurtal/IDT_SSc_map.git
cd IDT_SSc_map
git checkout v1.0-pre-review   # or v1.1 once the revision tag lands

# environment
mamba env create -f environment.yml
conda activate sscmim

# core pipeline (no scRNA-seq data needed)
make validate       # libSBML L2v4 — must be 0 errors
make integrate      # rebuild SSc_MIM_integrated.xml from harmonised modules
make network        # centrality + communities + hypergeometric enrichment
make preflight      # MINERVA-readiness checklist

# multi-dataset overlay (needs Tabib/GSE128169/GSE195452/GSE210395 in data/raw/)
make tabib-fetch    # 594 MB
make overlay-multi  # mixed-effects pseudobulk DEG + BH-FDR (v1.1)
make aucell         # sign-blinded AUCell module scoring (v1.1)
make figures        # F1/F2/F3 + supplementary
```

End-to-end runtime on a 16-core laptop: ≈ 25 min (network + integration + preflight ≈ 1 min; overlay-multi ≈ 20 min; figures ≈ 4 min).

See `Makefile` (`make help` for the full target list) and the Methods §2.9 table in the manuscript for the pinned dependency versions.

## Tech stack

| Step | Tool | Version | Output |
|------|------|---------|--------|
| Diagram editing | CellDesigner (SBGN-PD) | 4.4+ | `.xml` SBML files |
| SBML validation | python-libsbml | 5.21.1 | CI green |
| Annotation | MI2CAST | — | `species_annotations.tsv`, `reaction_evidence.tsv` |
| Network analysis | NetworkX | 3.6.1 | centrality + communities |
| scRNA-seq pipeline | scanpy + anndata | 1.12.1 / 0.12.16 | per-cluster pseudobulks |
| Pseudobulk DEG (revision) | statsmodels NB GLM + BH-FDR | 0.14.6 | `cluster_deg_multi_v11.tsv` |
| Module scoring (revision) | AUCell (sign-blinded) + Tabib Z-score | — | `patient_module_scores_aucell.tsv` |
| Tabular I/O | pandas | 2.3.3 | TSVs in `analysis/` and `manuscript/supplementary/` |
| Figures | matplotlib | 3.10.9 | F1/F2/F3 + supplementary |
| Drug-target prioritisation | DGIdb v4 | (offline JSON) | `druggable_hubs.tsv` |
| Boolean modelling (v2.0 stretch) | CaSQ → SBML-qual → MaBoSS | — | descoped from revision; planned for follow-up paper |
| Hosting (post-publication) | MINERVA Platform | LCSB | overlays in `minerva/overlays/` |

## How to contribute

This repository follows the Disease Maps Project conventions.

- **Curation requests** — open an issue using the `curation_request` template, including PMID, claimed interaction (entity A → entity B, sign), supporting evidence excerpt, and proposed module.
- **Expert review** — use the `expert_review` template; reviewers are credited as co-authors when contribution thresholds defined in `CONTRIBUTING.md` are met.
- **Pull requests** — must include updated MI2CAST annotations for every new or modified species / reaction. Automated SBML validation, spec-lint, and scripts-smoke tests run on every push (`.github/workflows/`).

## RO-Crate

The repository ships an [RO-Crate 1.1](https://w3id.org/ro/crate/1.1) provenance manifest at the root (`ro-crate-metadata.json`) describing every curated artefact, derived analysis output, figure, and pipeline script — plus the four source GEO datasets and the corresponding author. This is the structured-metadata answer to R3-M6 and is intended to be the canonical entry point for FAIR-aware tooling (e.g. ELIXIR data catalogues, WorkflowHub).

## Releases and DOIs

- **v1.0-pre-review** (2026-05-20) — frozen baseline for the simulated peer-review run; numbers reproduced in `analysis/baseline_v1.0/`.
- **v1.1** (2026-05-22) — npj-SBA revision, **merged into `main`** (NB-GLM pseudobulk DEG, AUCell scoring, drug recalibration, Docker, RO-Crate); see `CHANGELOG.md`.
- **v1.0 release** (planned) — GitHub + Zenodo DOI on `git tag v1.0` (webhook to be enabled).

Citation metadata: `CITATION.cff` and `.zenodo.json` (co-author slot pending — `REPLACE_ME` placeholders to be filled before the v1.0 tag).

## References

Core methodology:

- Mazein A. et al. *Systems medicine disease maps: community-driven comprehensive representation of disease mechanisms.* npj Syst Biol Appl 2018.
- Ostaszewski M. et al. *Community-driven roadmap for integrated disease maps.* Brief Bioinform 2019.
- Mazein A. et al. *A guide for developing comprehensive systems biology maps of disease mechanisms.* Front Bioinform 2023.
- Aghakhani S. et al. *Automated inference of Boolean models from molecular interaction maps using CaSQ.* Bioinformatics 2020.

Existing disease maps cited as templates:

- Singh V. et al. *RA-map: an interactive knowledge base for rheumatoid arthritis.* Clin Exp Immunol 2020.
- Zerrouk N. et al. *A Mechanistic Cellular Atlas of the Rheumatic Joint (RA-Atlas).* Front Syst Biol 2022.
- Ostaszewski M. et al. *COVID-19 Disease Map.* Mol Syst Biol 2021.
- Fujita K.A. et al. *Integrating Pathways of Parkinson's Disease in a Molecular Interaction Map.* Mol Neurobiol 2014.

SSc systems-level work to acknowledge and extend:

- Mahoney J.M. et al. *Systems Level Analysis of Systemic Sclerosis.* PLoS Comput Biol 2015.
- Taroni J.N. et al. — multi-cohort consensus of SSc skin transcriptomes.
- Tabib T. et al. *Myofibroblast transcriptome indicates SFRP2hi fibroblast progenitors in systemic sclerosis.* Nat Commun 2021;12:4384. PMID 34282151.
- Gur C. et al. *LGR5 expressing skin fibroblasts define a major cellular hub perturbed in systemic sclerosis.* Cell 2022;185:1373-1388. PMID 35381199.
- Morse C. et al. *Proliferating SPP1/MERTK-expressing macrophages in idiopathic pulmonary fibrosis.* Eur Respir J 2019;54:1802441. PMID 31221805. (GSE128169 lung)
- Yang M. et al. *Clinical phenotypes of patients with systemic sclerosis with distinct molecular signatures in skin.* Arthritis Care Res (Hoboken) 2023;75:1469-1480. PMID 35997480.

A full BibTeX corpus (398 entries) is maintained in `curation/pubmed_corpus.bib`.

## License

Map content (CellDesigner files, annotations, figures) is released under **CC-BY 4.0**. Code (scripts for analysis, overlay, deployment) is released under the **MIT License**. See `LICENSE` for full terms.
