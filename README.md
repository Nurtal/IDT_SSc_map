# SSc-MIM — Skin Fibrosis Molecular Interaction Map in Diffuse Cutaneous Systemic Sclerosis

> First module of a curated, SBGN-compliant Molecular Interaction Map (MIM) for systemic sclerosis (SSc), built in CellDesigner and deployed on MINERVA, with translational overlay of single-cell transcriptomic data from SSc skin biopsies.

**Target deliverable:** Late-breaking abstract — ACR Convergence 2026 (Orlando, 6–11 Nov 2026).
**Submission deadline:** 22 September 2026, 12:00 ET.
**Backup deliverable:** methodological paper for *Frontiers in Bioinformatics* or *npj Systems Biology and Applications*.

---

## Table of contents

- [Rationale](#rationale)
- [Scope](#scope)
- [Methodology](#methodology)
- [Reuse strategy](#reuse-strategy)
- [Translational use case](#translational-use-case)
- [Repository layout](#repository-layout)
- [Tech stack](#tech-stack)
- [Timeline](#timeline)
- [Go / no-go decision points](#go--no-go-decision-points)
- [Roles and resources](#roles-and-resources)
- [Risks and mitigations](#risks-and-mitigations)
- [Fallback plan](#fallback-plan)
- [How to contribute](#how-to-contribute)
- [References](#references)
- [License](#license)

---

## Rationale

Comprehensive disease maps — curated, SBGN-compliant Molecular Interaction Maps (MIMs) built in CellDesigner and deployed via MINERVA — exist for Parkinson's disease (PD map), COVID-19 (COVID-19 Disease Map), rheumatoid arthritis (RA-map / RA-Atlas), the SYSCID coverage of RA / SLE / IBD, and most recently Sjögren's disease (SjD map, 2025).

**No equivalent curated MIM exists for systemic sclerosis to date.** Existing systems-level work on SSc is limited to:

- Co-expression and consensus-clustering networks on skin transcriptomes (Whitfield intrinsic subsets, Mahoney, Taroni).
- Comorbidity networks (e.g. SSc–cancer).
- Targeted sub-networks on individual pathways (TGF-β, IFN, fibrosis).

These resources are **not mechanistic, not SBGN-curated, and not interoperable with the Disease Maps Project ecosystem.** This repository addresses that gap with a focused, defensible first module.

## Scope

This repository hosts the **first module of an SSc disease map**, deliberately restricted in scope so it is achievable, publishable, and extensible.

**Periphery:** Skin fibrosis in diffuse cutaneous SSc (dcSSc).

**Four interconnected sub-modules:**

| ID | Module | Rationale | Druggable handles |
|----|--------|-----------|-------------------|
| M1 | IFN-I signaling (IFNAR / JAK-STAT / ISG signature) | Documented IFN signature in SSc skin and blood; defines the inflammatory subset | Anifrolumab, JAK inhibitors |
| M2 | TGF-β / SMAD / fibroblast → myofibroblast transition | Central fibrotic axis | Pirfenidone, romilkimab, anti–TGF-β |
| M3 | Endothelial-to-mesenchymal transition (EndoMT) and vasculopathy | Bridge between vasculopathy and fibrosis; SSc-specific | Riociguat, endothelin antagonists |
| M4 | IL-6 / IL-4 / IL-13 Th2 axis and B-cell crosstalk | Validated targets in SSc trials | Tocilizumab, rituximab |

**Output phenotypes (sink nodes):** myofibroblast activation, ECM deposition, vascular remodeling, ISG signature — analogous to the eight phenotype anchors used in RA-map.

**Volumetric target:** 200–300 species, 300–450 reactions, 150–250 curated references. In line with the per-module volumes of RA-map and the TGF-β EMT breast cancer map.

## Methodology

The map follows the Disease Maps Project guidelines (Mazein et al., 2018; Ostaszewski et al., 2021; Mazein et al., 2023):

1. **Scoping** with domain experts (SSc clinicians and researchers).
2. **Curation** in CellDesigner using SBGN Process Description notation.
3. **Annotation** using MI2CAST minimum information standard (HGNC, UniProt, PubMed/PMID, evidence codes).
4. **Network analysis** (hubs, modules, centrality) in Cytoscape.
5. **Optional Boolean inference** with CaSQ for perturbation simulation.
6. **Deployment** on MINERVA Platform with semantic zoom and data-overlay capability.
7. **Translational application:** overlay of public single-cell and bulk transcriptomic data from SSc cohorts.

## Reuse strategy

> Re-curating what other Disease Maps Project members have already curated is wasted effort. The project deliberately maximises import and adaptation.

| Source | Use |
|--------|-----|
| **Reactome** | Import of `TGF-beta receptor signaling activates SMADs`, `Interferon alpha/beta signaling`, `IL-6 signaling`, `Signaling by PDGF` (BioPAX/SBML → CellDesigner via MINERVA conversion API) |
| **RA-map / RA-Atlas** (ramap.elixir-luxembourg.org) | Adaptation of JAK-STAT, IL-6, B-cell signaling modules |
| **SYSCID map** | Adaptation of shared immune modules (IFN, NF-κB) |
| **WikiPathways** | EndMT-related pathways as scaffold for module M3 |

**Manual SSc-specific curation focuses on:**

- Inter-module crosstalk (IFN-I → fibroblast activation; EndoMT → perivascular fibroblast).
- SSc-specific or SSc-enriched players: CCL2, CCL18, CXCL4 / PF4, POSTN, COMP, CTGF / CCN2, FRA-2, TBX2, and signaling downstream of Topo-I / RNA-pol-III autoantigen pathways.
- Autocrine myofibroblast loops specific to SSc skin.

Expected split: ~60–70% imported / adapted, ~30–40% manually curated SSc-specific content.

## Translational use case

The map is paired with a **single, clinically-readable use case** to demonstrate utility — this is the piece that makes the abstract competitive at ACR.

**Primary option — single-cell overlay on SSc skin:**

- Dataset: Tabib et al. (*Nat Commun* 2021) and successor scRNAseq SSc skin datasets (e.g. GSE138669).
- Workflow:
  1. Cell-type-specific DEGs (fibroblast subsets SFRP2⁺/PRSS23⁺, myofibroblasts, ECs) projected on the MIM.
  2. Per-patient module activation score, correlated with mRSS and progression.
  3. Druggable hub prioritisation via DGIdb and Open Targets.

**Alternative or complementary — bulk subsetting:**

- Datasets: Whitfield / GENISOS / PRESS cohorts (GSE58095, GSE45485 and equivalents).
- Aim: project the inflammatory / fibroproliferative / normal-like intrinsic subsets onto the MIM and identify subset-discriminating modules and candidate subset-specific targets.

**ACR-friendly deliverable:** one composite figure — global MIM view, subset / patient overlay, prioritised drug-target table — readable as a metro map by a clinician.

## Repository layout

```
ssc-mim/
├── README.md                          # this file
├── LICENSE
├── CITATION.cff
├── docs/
│   ├── scoping_notes.md               # decisions taken during scoping phase
│   ├── curation_guidelines.md         # adapted from Mazein et al. 2023
│   ├── mi2cast_checklist.md           # annotation minimum information
│   └── module_specs/
│       ├── M1_IFN_I.md
│       ├── M2_TGFb_fibrosis.md
│       ├── M3_EndoMT_vasculopathy.md
│       └── M4_IL6_Th2_Bcell.md
├── curation/
│   ├── celldesigner/                  # .xml source files (one per module + integrated)
│   │   ├── M1_IFN_I.xml
│   │   ├── M2_TGFb_fibrosis.xml
│   │   ├── M3_EndoMT_vasculopathy.xml
│   │   ├── M4_IL6_Th2_Bcell.xml
│   │   └── SSc_MIM_integrated.xml
│   ├── imports/                       # raw imports from Reactome, RA-map, SYSCID, WikiPathways
│   ├── annotations/
│   │   ├── species_annotations.tsv    # HGNC, UniProt, Ensembl IDs
│   │   └── reaction_evidence.tsv      # PMIDs, evidence codes, MI2CAST fields
│   └── pubmed_corpus.bib              # all curated references
├── analysis/
│   ├── network/                       # Cytoscape sessions, centrality, communities
│   ├── boolean/                       # CaSQ output (SBML-qual), GINsim / MaBoSS sims
│   └── overlay/
│       ├── tabib_scRNAseq/            # scripts and outputs for the primary use case
│       └── whitfield_bulk/            # alternative / complementary use case
├── minerva/
│   ├── deployment_notes.md
│   └── overlays/                      # data overlays packaged for MINERVA
├── figures/
│   ├── F1_global_MIM.svg
│   ├── F2_overlay_by_subtype.svg
│   └── F3_druggable_targets.svg
├── manuscript/
│   ├── ACR2026_late_breaking_abstract.md
│   └── full_paper_draft.md            # for the methodological journal submission
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── curation_request.md
    │   └── expert_review.md
    └── workflows/
        └── validate_sbml.yml          # SBML / SBGN validation on push
```

## Tech stack

| Step | Tool | Output |
|------|------|--------|
| Diagram editing | **CellDesigner v4.4** (SBGN-PD) | `.xml` SBML files |
| Import / format harmonisation | **MINERVA conversion API**, **CaSQ** | Harmonised CellDesigner diagrams |
| Annotation | CellDesigner notes, MI2CAST fields, stable IDs (HGNC, UniProt, PubMed) | `species_annotations.tsv`, `reaction_evidence.tsv` |
| Hosting / navigation | **MINERVA Platform** (Luxembourg instance or local) | Public URL with semantic zoom and overlay |
| Network analysis | **Cytoscape** with BiNoM plugin | Centrality metrics, community detection |
| Boolean modelling (optional) | **CaSQ** → SBML-qual → **GINsim** / **MaBoSS** | Perturbation simulations |
| Omics overlay | MINERVA data overlay, Python (`anndata`, `scanpy`) | Per-patient / per-subset figures |
| Drug-target prioritisation | DGIdb, Open Targets, ChEMBL | Drug-target table |

CaSQ is developed at Inria Paris (Soliman group), MINERVA at the University of Luxembourg — both within the Disease Maps Project consortium and reachable for collaboration.

## Timeline

The plan runs from **15 May 2026** to the **22 September 2026** late-breaking deadline — 18 weeks.

### Phase 1 — Scoping and groundwork (weeks 1–3 · 15 May → 5 Jun)

- Validate scope with 1–2 SSc clinical experts (co-authorship locked).
- Build the core bibliography (~50 key reviews + ~100 primary papers).
- Install stack (CellDesigner, local MINERVA, CaSQ).
- Final decision on the omics dataset (Tabib scRNAseq, Whitfield bulk, or both).

### Phase 2 — Module curation (weeks 4–11 · 6 Jun → 31 Jul)

| Weeks | Module | Target species | Strategy |
|-------|--------|----------------|----------|
| 4–5 | M1 IFN-I | ~60 | Reactome import + SSc-specific curation |
| 6–7 | M2 TGF-β / fibrosis | ~80 | Reactome + RA-map import + SSc-specific curation |
| 8–9 | M3 EndoMT / vasculopathy | ~60 | Mostly manual (no strong upstream source) |
| 10–11 | M4 IL-6 / Th2 / B cells | ~50 | RA-map import + SSc adaptation |

In parallel: MI2CAST annotation, PubMed / PMID recording.

### Phase 3 — Integration and deployment (weeks 12–14 · 1 Aug → 21 Aug)

- Inter-module SSc-specific crosstalk (critical step).
- One round of expert review (~1 week of expert time, planned in advance).
- MINERVA deployment, semantic-zoom check.
- Cytoscape network analyses (hubs, communities vs manually defined modules).

### Phase 4 — Use case and figures (weeks 15–17 · 22 Aug → 11 Sep)

- scRNAseq (or bulk) overlay on the MIM.
- Perturbed hubs, per-patient / per-subset scoring.
- DGIdb / Open Targets prioritisation.
- Three abstract figures: global MIM, overlay, target table.

### Phase 5 — Writing and submission (weeks 18+ · 12 Sep → 22 Sep)

- ACR late-breaking abstract (300 words + 1–2 figures), 5–7 days of co-author iteration.
- Submission on or before 22 September 2026, 12:00 ET.

## Go / no-go decision points

- **End of week 7 (24 Jul).** If M1 + M2 are not finished, downgrade the scope to three modules or push the target to EULAR 2027 plus the methodological paper alone.
- **End of week 14 (21 Aug).** If expert validation has not happened, submit anyway with a "preliminary" framing in the abstract.

## Roles and resources

- **One lead curator at 0.8–1.0 FTE over four months** — typically a bioinformatics post-doc or third-year PhD student. Without this, the timeline does not hold.
- **One referent SSc rheumatologist** (~10% of time, for validation and co-authorship) — ideally a member of an established SSc study group (EULAR, SCTC, …).
- **One bioinformatician** for the omics overlay (~0.3 FTE during the last two months).
- **MINERVA access** (free) and modest compute (a laptop is enough unless re-running scRNAseq from raw counts).

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Curation slower than planned | high | Weekly quotas, progressive scope downgrade, curator / expert rotation |
| Import incompatibilities (Reactome → CellDesigner) | medium | Test the Reactome import on one pathway in week 1 |
| Late expert validation | medium | Lock the rheumatologist at project start; book three 1-hour meetings in advance |
| Lack of "wow factor" for an ACR clinician reviewer | medium | Invest heavily in the overlay figure and drug-target table |
| Still "preliminary" at submission | low–medium | The late-breaking track accepts ongoing work, but the overlay figure must be complete |

## Fallback plan

- **Missed late-breaking ACR.** Aim for **EULAR 2027** (deadline typically end-January 2027) and publish the full version in *Frontiers in Bioinformatics* in the meantime.
- **Missed all of 2026.** Publish a principal paper in *npj Systems Biology and Applications* in mid-2027, then submit to ACR 2027 with an in-press paper as backing — substantially higher acceptance odds.

## How to contribute

This repository follows the Disease Maps Project conventions.

- **Curation requests** — open an issue using the `curation_request` template, including PMID, claimed interaction (entity A → entity B, sign), supporting evidence excerpt, and proposed module.
- **Expert review** — use the `expert_review` template; reviewers are credited as co-authors when contribution thresholds defined in `CONTRIBUTING.md` are met.
- **Pull requests** — must include updated MI2CAST annotations for every new or modified species / reaction. Automated SBML validation runs on every push.

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
- Vasaikar S. et al. *SYSCID map.* Front Immunol 2023.
- SjD map (Sjögren), bioRxiv 2025.

SSc systems-level work to acknowledge and extend:

- Mahoney J.M. et al. *Systems Level Analysis of Systemic Sclerosis.* PLoS Comput Biol 2015.
- Taroni J.N. et al. — multi-cohort consensus of SSc skin transcriptomes.
- Tabib T. et al. *scRNAseq analysis of skin in SSc.* Nat Commun 2021.

A full BibTeX corpus is maintained in `curation/pubmed_corpus.bib`.

## License

Map content (CellDesigner files, annotations, figures) is released under **CC-BY 4.0**. Code (scripts for analysis, overlay, deployment) is released under the **MIT License**. See `LICENSE` for full terms.
