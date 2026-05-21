# SSc-MIM — Molecular Interaction Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis

> First curated, SBGN-PD-compliant Molecular Interaction Map (MIM) of diffuse cutaneous systemic sclerosis (dcSSc) skin fibrosis. Built in CellDesigner, MI2CAST-annotated, overlaid with four open-access single-cell transcriptomic datasets, and released as a GitHub + Zenodo resource.

[![SBML validate](https://github.com/Nurtal/IDT_SSc_map/actions/workflows/validate_sbml.yml/badge.svg)](https://github.com/Nurtal/IDT_SSc_map/actions)

**Current state (2026-05-21):** Phase 4c complete; npj-SBA major-revision sprint cycle in progress on branch [`revision/v1.1`](https://github.com/Nurtal/IDT_SSc_map/tree/revision/v1.1). See [`reviewing/REVISION_ROADMAP.md`](reviewing/REVISION_ROADMAP.md) and [`reviewing/PROGRESS.md`](reviewing/PROGRESS.md) for live status.

**Lead author:** Nathan Foulquier — LBAI, UMR 1227 Inserm, CHU Brest. ORCID [0000-0003-4620-2794](https://orcid.org/0000-0003-4620-2794).

---

## Headline numbers (Phase 4c, v1.0 baseline)

| Quantity | Value | Notes |
|---|---|---|
| Species | **526** | 17 biologically meaningful compartments (20 raw SBML declarations) |
| Reactions | **260** | 244 Reactome-derived + 85 SSc-curated; 198/244 (81%) carry a PMID |
| SBML validation | **0 errors** | libSBML L2v4 across 5 module XMLs + integrated |
| Annotated HGNC species | **198** | 196 (99%) RNA-seq-detectable; 15 alias corrections + 13 non-gene removals applied |
| Single-cell donors integrated | **197** | 117 SSc / 80 HC across 4 datasets |
| Cells processed | **266 884** | Tabib skin / Gur skin multiome / GSE210395 PBMC / GSE128169 lung |
| Cell-type clusters | **58** | per-(dataset, cluster) MINERVA overlay TSVs |
| MIM coverage by transcriptomics | **50.0 %** | 98/196 detectable species hit by ≥ 1 DEG (v1.0 raw-p baseline; revision-v1.1 number under BH-FDR pending S1 re-run) |
| Network communities | **38** | greedy modularity; 32 significant (community, module) hypergeometric tests at q < 0.05 (revision-v1.1) |
| Druggable interactions | **21** | DGIdb v4 on top 20 hubs; 11 distinct molecular targets |

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

**Output phenotypes (sink nodes):** myofibroblast activation, ECM deposition, vascular remodelling, ISG signature — analogous to the eight phenotype anchors used in RA-map.

## Methodology

The map follows the Disease Maps Project guidelines (Mazein et al., 2018; Ostaszewski et al., 2021; Mazein et al., 2023):

1. **Scoping** with domain experts (SSc clinicians).
2. **Reactome import** of TGF-β, IFN-α/β, IL-6, Notch1, PDGF pathways → CellDesigner harmonisation.
3. **SSc-specific Tier-1 curation** — 85 hand-curated reactions across the 4 modules (incl. 8 inter-module crosstalk; see [`manuscript/supplementary/S1_crosstalk_reactions.tsv`](manuscript/supplementary/S1_crosstalk_reactions.tsv)).
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

Final split realised in v1.0: 67% Reactome-derived / 30% SSc-Tier-1 manually curated / 3% reused stubs.

## Translational use case

Four open-access transcriptomic datasets are overlaid on the MIM:

| Dataset | Tissue | Donors (SSc / HC) | Cells | Source |
|---|---|---|---|---|
| Tabib 2021 (GSE138669) | dcSSc skin | 12 / 10 | 64 211 | scRNA-seq, 10× |
| Gur 2022 (GSE195452) | SSc skin multiome | 98 / 58 | 100 538 | RNA arm; pre-annotated |
| GSE210395 | SSc PBMC, pDC + monocyte-enriched | 4 / 4 | 34 619 | scRNA-seq |
| GSE128169 (Morse 2019) | SSc-ILD lung | 8 / 5 | 67 516 | 10× MEX |

Each cluster yields a MINERVA-format overlay TSV (`minerva/overlays/`, 58 files). Per-donor module activation scores (M1–M4 + SSc-Tier1) are computed from the pseudobulk DEG output; in revision v1.1 the sign-blinded **AUCell** score replaces the v1.0 DEG-sign-weighted score (see `reviewing/REVISION_ROADMAP.md` E2).

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
│   ├── ssc_curated_reactions.tsv      # 85 SSc-specific Tier-1 reactions
│   ├── pubmed_corpus.bib              # 362 BibTeX entries
│   └── annotations/
│       ├── species_annotations.tsv    # 526 rows; 198 HGNC propres
│       └── reaction_evidence.tsv      # 244 rows; 198 with PMID (81%)
├── analysis/
│   ├── network/                       # centrality, communities, hub_overlap, dangling_species, community_enrichment
│   ├── overlay/                       # cluster_deg_multi*.tsv, patient_module_scores*.tsv, druggable_hubs.tsv
│   ├── clinical/                      # donor_metadata, CLINICAL_METADATA_GAP.md, correlations (gap-banner v1.1)
│   ├── baseline_v1.0/                 # frozen pre-revision snapshot
│   └── boolean/                       # placeholder for v2.0 CaSQ work
├── minerva/
│   └── overlays/                      # 58 per-cluster TSVs
├── figures/
│   ├── F1_global_MIM.{svg,png}
│   ├── F2_multi_overlay.{svg,png}     # 4-panel skin/skin-Gur/PBMC/lung
│   ├── F3_druggable_targets.{svg,png}
│   └── F_supp_hub_robustness.{svg,png}# Supplementary Figure S1 (E3)
├── scripts/                           # 18 Python scripts; Makefile-orchestrated
├── docs/
│   ├── historical_roadmap.md          # archived ACR-2026 plan (pre-pivot)
│   ├── module_specs/                  # M1–M4 spec sheets
│   ├── standups/                      # per-sprint co-author notes
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

## Releases and DOIs

- **v1.0-pre-review** (2026-05-20) — frozen baseline for the simulated peer-review run; numbers reproduced in `analysis/baseline_v1.0/`.
- **v1.1** (planned 2026-09-30) — major-revision submission to npj Systems Biology and Applications; will mint a Zenodo DOI on tag push (webhook to be enabled).

Citation metadata: `CITATION.cff` and `.zenodo.json` (co-author slot pending — `REPLACE_ME` placeholders to be filled before the v1.1 tag).

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
- Tabib T. et al. *scRNAseq analysis of skin in SSc.* Nat Commun 2021.
- Gur C. et al. *LGR5 expressing skin fibroblasts define a major cellular hub perturbed in scleroderma.* (GSE195452 multiome) 2022.
- Yang M. et al. *Clinical phenotypes of patients with systemic sclerosis with distinct molecular signatures in skin.* Arthritis Care Res (Hoboken) 2023;75:1469-1480. PMID 35997480.

A full BibTeX corpus (362 entries) is maintained in `curation/pubmed_corpus.bib`.

## License

Map content (CellDesigner files, annotations, figures) is released under **CC-BY 4.0**. Code (scripts for analysis, overlay, deployment) is released under the **MIT License**. See `LICENSE` for full terms.
