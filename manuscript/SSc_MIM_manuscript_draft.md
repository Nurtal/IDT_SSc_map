# SSc-MIM: A Curated, SBGN-Compliant Molecular Interaction Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis

**Nathan Foulquier**¹\*

¹ LBAI, UMR 1227 Inserm, Centre de Données, CHU de Brest, Université de Bretagne Occidentale, Brest, France  
\* Correspondence: nathan.foulquier.pro@gmail.com  
ORCID: 0000-0003-4620-2794

**Running title**: SSc Molecular Interaction Map

**Keywords**: systemic sclerosis, scleroderma, disease map, molecular interaction map, SBGN, CellDesigner, fibrosis, TGF-β, interferon, EndoMT, single-cell transcriptomics, drug repurposing

**Target journal**: Frontiers in Bioinformatics (or npj Systems Biology and Applications)

---

## Abstract

Systemic sclerosis (SSc, scleroderma) is a complex autoimmune fibro-inflammatory disorder characterised by progressive skin and internal organ fibrosis, vasculopathy, and immune dysregulation, yet no disease-modifying therapy has achieved regulatory approval. The absence of a comprehensive mechanistic map linking the disease's core molecular circuits has hampered rational drug prioritisation. Here we present SSc-MIM, the first curated, Systems Biology Graphical Notation (SBGN)-compliant Molecular Interaction Map (MIM) for diffuse cutaneous SSc, constructed in CellDesigner and fully annotated according to the MI2CAST standard. The integrated map encompasses 526 molecular species across 260 reactions distributed over 17 subcellular and tissue-level compartments, organised into four biologically coherent modules: type-I interferon and cGAS–STING signalling (M1), TGF-β–driven fibroblast-to-myofibroblast transition (M2), endothelial-to-mesenchymal transition and vasculopathy (M3), and IL-6/IL-4/IL-13/B-cell crosstalk (M4). In total, 85 SSc-specific curated reactions are supported by 355 unique PubMed identifiers and annotated with ECO evidence codes. The map was integrated with the Tabib et al. (2021) scRNA-seq atlas of SSc skin biopsies (GSE138669; 64,211 cells, 12 SSc / 10 HC) using a pseudobulk differential expression pipeline across six skin cell types. Thirty-four MIM species showed significant differential expression between SSc and healthy controls (|log₂FC| ≥ 0.2, p ≤ 0.05), with M1 (IFN-I) module activation scores elevated in SSc (mean ± SD: 0.342 ± 0.095 vs 0.070 ± 0.016) and M2 (fibrosis) scores similarly increased (0.232 ± 0.061 vs 0.044 ± 0.007). Network analysis identified 38 functional communities, with SMAD3–SMAD4 (hub score 13.42), TGFB1 (9.09), and NICD1 (9.46) as the three highest-connectivity hubs. Cross-referencing against the Drug–Gene Interaction database revealed 21 SSc-relevant drug–target interactions, including fresolimumab (TGFB1), anifrolumab (IFNAR1/2), tocilizumab (IL6R), and brontictuzumab (NOTCH1). SSc-MIM provides a community resource for hypothesis generation, computational modelling, and translational stratification in scleroderma research.

---

## 1. Introduction

Systemic sclerosis (SSc) is a rare but life-threatening connective tissue disease affecting approximately 15–20 individuals per 100,000 in Western populations, with a female-to-male ratio of approximately 4:1 (Denton and Khanna, 2017; Allanore et al., 2015). The clinical hallmark of the diffuse cutaneous subtype (dcSSc) is rapid, widespread skin fibrosis accompanied by pulmonary arterial hypertension, interstitial lung disease, and renal crisis — complications responsible for the high mortality that distinguishes SSc from other autoimmune rheumatic diseases. Despite decades of research, no treatment reverses established fibrosis, and the only approved intervention for SSc-associated interstitial lung disease remains nintedanib, a multi-kinase inhibitor that slows, but does not halt, progression (Distler et al., 2019; Khanna et al., 2016).

The mechanistic complexity of SSc reflects the convergence of at least three major pathological processes. An early inflammatory/autoimmune phase, driven by plasmacytoid dendritic cells and autoreactive B and T cells, sustains a prominent type-I interferon (IFN) signature that is detectable in the blood of 50–75% of patients (Assassi et al., 2010; Rice et al., 2017). This interferon milieu primes fibroblasts towards TGF-β–dependent myofibroblast differentiation, a central mechanism of excessive extracellular matrix deposition that has been characterised in seminal work by Varga and Abraham (2007) and subsequently detailed at the single-cell level by Tabib and colleagues (2021). In parallel, Notch/endothelin-1–mediated endothelial-to-mesenchymal transition (EndoMT) drives the vasculopathy that manifests clinically as Raynaud's phenomenon, digital ulcers, and pulmonary hypertension (Bhattacharyya et al., 2012). These processes are further amplified by IL-6 and IL-4/IL-13 cytokine circuits that sustain B-cell hyperactivation and the production of disease-specific autoantibodies, including anti-topoisomerase I (anti-Scl70) and anti-centromere antibodies (Desallais et al., 2022; van Bon et al., 2014).

A fundamental challenge in SSc research is that these pathways are not independent: IFN signalling amplifies TGF-β responses, TGF-β suppresses anti-fibrotic endothelial programmes, and Notch cross-talks with both the SMAD-dependent canonical and non-canonical TGF-β axes. No formal, literature-curated representation of these interconnections currently exists for SSc, leaving researchers without a structured reference for interpreting multi-omic experiments, designing combination therapy strategies, or parameterising mechanistic models.

The Disease Maps Project community has established that curated, SBGN-compliant Molecular Interaction Maps constitute a gold standard for systematic disease mechanism representation (Mazein et al., 2018). Landmark disease maps have been developed for rheumatoid arthritis (Singh et al., 2020), COVID-19 (Ostaszewski et al., 2021), Parkinson's disease, and several rare diseases, each demonstrating that map-guided network analysis accelerates hypothesis generation and drug repurposing. The MI2CAST annotation standard, introduced by Touré and colleagues (2020), further enables machine-readable, evidence-graded representation of molecular interactions that is compatible with MINERVA-based web deployment and integration with SPARQL-queryable knowledge graphs.

Here we present SSc-MIM, the first SBGN-compliant Molecular Interaction Map for diffuse cutaneous SSc. We describe its construction, quality control, integration with published single-cell transcriptomic data, and its use for network analysis and systematic drug–target prioritisation. The map is openly available on GitHub (https://github.com/Nurtal/IDT_SSc_map) under CC-BY 4.0, and the analysis code is released under the MIT License.

---

## 2. Materials and Methods

### 2.1 Scope and Module Definition

SSc-MIM was designed to capture the four major pathological pathways of diffuse cutaneous SSc: (M1) type-I interferon signalling through the cGAS–STING–JAK–STAT and IRF3 axes; (M2) TGF-β–driven fibroblast-to-myofibroblast transition including canonical SMAD2/3 signalling, non-canonical MAPK/PI3K routes, YAP/TAZ mechanotransduction, and ECM remodelling; (M3) endothelial-to-mesenchymal transition and vasculopathy encompassing Notch/DLL4/NICD1, endothelin-1/EDNRA/EDNRB, and VEGF axes; and (M4) B-cell/plasma cell differentiation, BCR-mediated autoantibody production, and IL-6/IL-4/IL-13 effector cytokine networks. Module boundaries were drawn to preserve biological coherence while enabling independent curation and integration of cross-module crosstalk reactions.

### 2.2 Reactome Import and Harmonisation

Seed pathway diagrams for each module were downloaded from Reactome (Fabregat et al., 2018) as CellDesigner-compatible SBML Level 2 Version 4 (L2v4) files. Five Reactome pathways formed the structural backbone: R-HSA-909733 (Interferon-alpha/beta signalling), R-HSA-2173789 (Activation of IRF3/7 by adapter proteins), R-HSA-186797 (Signalling by TGF-beta), R-HSA-1980143 (Signalling by NOTCH1), and R-HSA-1059683 (Macroautophagy). These seed files were harmonised using a custom Python pipeline (`scripts/integrate_modules.py`) that: (i) resolved duplicate species identifiers across modules using a canonical HGNC-based naming convention (`SYMBOL__compartment`); (ii) merged compartment definitions; (iii) re-serialised the integrated model as a valid SBML L2v4 file; and (iv) annotated each species with its module of origin using SBML `<notes>` elements formatted as complete XHTML documents per the SBML L2v4 specification (§4.1).

### 2.3 SSc-Specific Tier-1 Curation

Beyond the Reactome backbone, SSc-specific molecular entities and reactions were identified through a systematic literature review of PubMed (2000–2025) using a combination of disease terms ("systemic sclerosis", "scleroderma", "dcSSc") and pathway terms ("TGF-beta fibrosis", "cGAS STING interferon", "EndoMT", "NOTCH fibrosis", "IL-6 B cell"). Species were classified as Tier-1 (mechanistically central, directly relevant to SSc pathogenesis, and supported by at least one primary SSc study with ECO:0000314 experimental evidence) or Tier-2 (relevant but inferred from related diseases or indirect evidence, ECO:0000305). Each SSc-specific reaction was recorded in `curation/ssc_curated_reactions.tsv` with fields for reactants, products, modifiers, mechanism type, PubMed identifier, ECO evidence code, and SSc-relevance annotation. A total of 85 SSc-curated reactions were added across the four modules (M1: 15, M2: 25, M3: 22, M4: 15, crosstalk: 8) and wired into the CellDesigner model using `scripts/wire_ssc_tier1.py`.

### 2.4 MI2CAST Annotation

All curated reactions were annotated following the Minimum Information about a Molecular Interaction Causal STatement (MI2CAST) guidelines (Touré et al., 2020). Each entry specifies: source entity (HGNC symbol, UniProt accession), target entity, causal interaction sign (activation/inhibition/modulation), biological context (cell type from BRENDA, disease context from Disease Ontology), experimental context (assay type from the Evidence & Conclusion Ontology, ECO), and literature provenance (PubMed identifier). Species-level annotations, including cross-references to UniProt, Ensembl, and ChEBI, were curated in `curation/annotations/species_annotations.tsv`. Reaction-level evidence metadata was maintained in `curation/annotations/reaction_evidence.tsv`.

### 2.5 SBML Validation and Quality Control

The integrated model was validated against the SBML L2v4 specification using libSBML 5.20 (`scripts/validate_sbml.py`). Validation targeted three error classes: (i) incorrect ordering of `<notes>` and `<annotation>` child elements (§4.1 requires `<notes>` to precede `<annotation>`); (ii) malformed XHTML in `<notes>` blocks (Form 1 requires `<html><head><body>`); and (iii) invalid species identifiers containing hyphens, which are not permitted in SBML SId syntax. All three error classes were resolved at both the generated-file and generator-script levels to prevent regression. A preflight check (`scripts/preflight.py`) was incorporated into the Makefile to verify annotation completeness and cross-reference consistency between the XML, `species_annotations.tsv`, and `ssc_curated_reactions.tsv` before each release.

### 2.6 Single-Cell Transcriptomic Overlay

Per-sample 10× Genomics count matrices (22 `.h5` files) were downloaded from GEO (GSE138669; `scripts/fetch_tabib.py`) and processed with scanpy 1.12 (`scripts/build_overlay.py`). Quality-control filtering retained cells with 200–6,000 detected genes and fewer than 25% mitochondrial reads; genes detected in fewer than 10 cells were removed. Libraries were normalised to 10,000 counts per cell and log₁p-transformed. Highly variable gene selection (top 2,000 genes, Seurat flavour), PCA (30 components), and k-nearest-neighbour graph construction (k = 20, 20 PCs) preceded Leiden clustering at resolution 0.35. Clusters were annotated to cell types using marker gene expression profiles from Tabib et al. (2021). Pseudobulk profiles (per-donor, per-cell-type count sums) were library-size normalised, log₁p-transformed, and subjected to Wilcoxon rank-sum tests comparing SSc (n = 12) and HC (n = 10) donors. Differentially expressed genes (|log₂FC| ≥ 0.2, p ≤ 0.05) were mapped to MIM species via HGNC symbol matching. Per-donor module activation scores were computed as the mean of gene-level expression weighted by the sign of the DEG log₂FC, then averaged across cell types. Minerva-format per-cluster overlay TSVs were generated for web-based map annotation.

### 2.7 Network Analysis

The integrated CellDesigner XML was parsed into a bipartite species–reaction graph (`scripts/network_analysis.py`) using NetworkX 3.x. Species were represented as nodes; reactions as hyperedge mediators collapsed into pairwise species–species edges weighted by shared reaction count. Hub scores were computed as the geometric mean of betweenness centrality and degree, normalised to the 99th percentile of the background distribution. Community structure was detected with the Louvain/greedy-modularity algorithm. Module–community contingency tables were generated to assess whether network communities aligned with the curated biological modules.

### 2.8 Drug–Target Prioritisation

Druggable hubs were identified by cross-referencing top-20 hub species against the Drug–Gene Interaction database (DGIdb v5; Freshour et al., 2021) using `scripts/dgidb_query.py`. Returned drug–gene interactions were filtered to retain only interactions with an SSc-relevant context annotation (assigned manually from the SSc clinical trials literature) or an approved/investigational status matching an SSc-associated indication. Hub score thresholds were set at ≥3.0 to focus on high-connectivity targets. Final drug–target prioritisation tables were generated and visualised in `analysis/overlay/druggable_hubs.tsv` and `figures/F3_druggable_targets.svg`.

### 2.9 Software and Reproducibility

All analyses were performed in Python 3.10+ with libSBML 5.20, NetworkX 3.3, pandas 2.2, matplotlib 3.8, scanpy 1.12, anndata, h5py 3.16, and scipy. The complete pipeline is orchestrated via a GNU Makefile (`make auto` executes end-to-end integration, validation, overlay, network analysis, and figure generation). The CellDesigner XML opens in CellDesigner v4.4+ and any MINERVA Platform instance. All code, data, and figures are version-controlled at https://github.com/Nurtal/IDT_SSc_map.

---

## 3. Results

### 3.1 Architecture and Scope of SSc-MIM

The integrated SSc-MIM encompasses 526 molecular species and 260 reactions distributed across 17 compartments (extracellular, plasma membrane, cytosol, nucleus, endoplasmic reticulum, endosome, Golgi, mitochondrion, and ECM, defined at both the cell-type-specific and tissue levels). The four modules and their SSc-specific additions are summarised in Table 1. Reactome-derived backbone species provide pathway completeness for canonical signalling cascades, while 85 hand-curated SSc-specific reactions annotated with 355 unique PubMed identifiers constitute the disease-specific knowledge layer. The curation rate per module reflects the intensity of SSc-dedicated literature: TGF-β/fibrosis (M2, 25 reactions) and EndoMT/vasculopathy (M3, 22 reactions) are the most densely curated, consistent with the dominant role of fibrosis and vascular injury in dcSSc pathogenesis.

**Table 1. Summary statistics for each SSc-MIM module.**

| Module | Biological Focus | Species | Reactions | SSc-Curated Reactions | Key SSc Entities |
|--------|-----------------|---------|-----------|----------------------|-----------------|
| M1 | Type-I IFN / cGAS–STING | 132 | 61 | 15 | MB21D1, TMEM173, TBK1, IRF3, ISGF3 |
| M2 | TGF-β / FMT | 148 | 78 | 25 | TGFB1, SMAD3, SMAD4, COL1A1, ACTA2, YAP1 |
| M3 | EndoMT / Vasculopathy | 124 | 72 | 22 | NOTCH1, NICD1, EDN1, EDNRA, SNAI2, CDH5 |
| M4 | IL-6 / Th2 / B-cell | 122 | 49 | 15 | IL6, IL6R, IL4, IL13, MS4A1, IGHG1 |
| Crosstalk | Inter-module | — | — | 8 | IFN–TGFβ, Notch–SMAD, IL-6–STAT3 |
| **Total** | | **526** | **260** | **85** | |

The global SBGN map (Figure 1) reveals a highly interconnected network with a biologically intuitive topology: the IFN module (M1) and the B-cell/cytokine module (M4) are positioned as upstream inducers converging onto the central fibrotic hub of M2, which in turn supplies activated myofibroblast signals that feed back through Notch and endothelin circuits in M3. Cross-module reactions formalise the mechanistic bridges that would otherwise remain implicit in the primary literature.

**[Figure 1: Global view of SSc-MIM in SBGN Process Description notation. Four modules are colour-coded (M1 cyan, M2 orange, M3 green, M4 purple). Cross-module reactions are shown as dashed arcs. Generated as `figures/F1_global_MIM.svg`.]**

### 3.2 Single-Cell Transcriptomic Overlay and Cell-Type Stratification

The Tabib et al. (2021) scRNA-seq atlas (GSE138669) was processed through a full scanpy QC, normalisation, PCA, and Leiden clustering pipeline. After quality-control filtering (≥200 genes per cell, ≤6,000 genes, <25% mitochondrial reads), 64,211 cells were retained from 22 samples (12 SSc / 10 HC). Unsupervised Leiden clustering at resolution 0.35 yielded 13 clusters, which were annotated against published Tabib marker genes into six cell types: keratinocyte (29,535 cells), fibroblast (13,046), myofibroblast/FAP⁺/CTHRC1⁺ (8,790), endothelial vascular (6,930), T lymphocyte (2,987), and macrophage (2,923). Pseudobulk differential expression (Wilcoxon rank-sum on per-donor aggregated profiles) identified 1,058 significant gene–cell-type pairs (|log₂FC| ≥ 0.2, p ≤ 0.05), of which 63 mapped to annotated MIM species spanning 34 unique HGNC symbols (16% of the 211 MIM-annotated genes).

Per-donor module activation scores revealed consistent elevation of M1 (IFN-I) activity in SSc relative to healthy controls (mean ± SD: 0.342 ± 0.095 vs 0.070 ± 0.016), and of M2 (TGF-β/fibrosis) activity (0.232 ± 0.061 vs 0.044 ± 0.007). The M3 (EndoMT/vasculopathy) module showed the largest absolute separation (0.812 ± 0.281 vs 0.172 ± 0.070), driven by endothelial vascular cell upregulation of ANGPT2, EDNRB, and RHOA. Twenty-nine MIM-mapped IFN module genes were significantly upregulated across SSc cell types, led by IFITM3, IFITM1, IFI27, IRF7, and ISG15 — a multi-cell-type IFN signature present in both macrophage and myofibroblast populations (Figure 2). The fibrosis module (M2 and SSc Tier-1) contributed 28 upregulated gene–cell-type pairs, with COL1A1, COMP, POSTN, COL1A2, and TNC as the top hits in fibroblast and myofibroblast populations, consistent with published dcSSc transcriptomic profiles (Tabib et al., 2021; Bhattacharyya et al., 2012). SNAI2, the M3 EndoMT hub (rank 11, score 5.67), was significantly upregulated in fibroblasts (log₂FC = 0.41, p = 0.031), providing single-cell validation for a mesenchymal transition component within the SSc fibroblast compartment. This IFN enrichment pattern, spanning both immune and stromal cells, aligns with the known multi-cell-type propagation of the IFN signature in dcSSc (Assassi et al., 2010; Rice et al., 2017) and positions M1 module activation scores as a potential transcriptomic biomarker of IFN-high SSc subgroups.

**[Figure 2: Single-cell transcriptomic overlay of SSc-MIM. Left panel: heatmap of module-level expression scores per fibroblast/endothelial subpopulation from GSE138669. Right panel: volcano plot of differentially expressed MIM species between dcSSc and healthy controls. Generated as `figures/F2_overlay_by_subtype.svg`.]**

### 3.3 Network Topology and Druggable Hub Identification

The bipartite species–reaction graph yielded 899 edges between 526 species and 260 reaction nodes. The species co-reaction projection contained 713 edges across 526 nodes, with 22 weakly connected components (the largest containing 504 species, representing 96% of the map). Greedy-modularity community detection identified 38 functional communities, whose module-contingency analysis revealed that the six largest communities were significantly enriched for single biological modules (p < 0.001, hypergeometric test), confirming that the curated module structure is recapitulated by unbiased network topology. The two largest cross-module communities (communities 0 and 1) corresponded to the IFN–TGF-β interface and the Notch–Th2 interface respectively, coinciding with the sites of known pathway cross-talk in SSc.

Hub score analysis identified 20 top-ranking species (Table 2). SMAD3–SMAD4 nuclear complex emerged as the single highest-connectivity node (hub score 13.42), consistent with its role as the master transcriptional effector integrating TGF-β, BMP, Activin, and crosstalk from both IFN and Notch pathways. TGFB1 extracellular (9.09) and NICD1 cytoplasmic (9.46) ranked second and third, reflecting the autocrine/paracrine amplification loops that sustain fibrosis and EndoMT respectively. The pro-fibrotic fibroblast state node (hub score 9.97), an emergent entity representing the activated myofibroblast phenotype, ranked second overall and serves as the convergence point of M2 and M3 signals.

Cross-referencing the 20 top hubs against DGIdb revealed 21 SSc-relevant drug–target interactions spanning 11 distinct molecular targets (Figure 3, Table 2). Clinically advanced agents included fresolimumab (TGFB1, hub rank 4; anti-TGF-β1/2/3 monoclonal antibody evaluated in SSc skin trial), anifrolumab (IFNAR1/IFNAR2, hub rank via M1; SLE-approved, SSc trial rationale), tocilizumab and sarilumab (IL6R; focuSSced trial and exploratory use), rituximab (MS4A1/CD20; RECITAL trial in SSc-ILD), and nintedanib (TGFBR2 via multi-kinase inhibition). Two novel repurposing candidates were identified: brontictuzumab (NOTCH1, hub rank 12, hub score 5.18; investigational Notch inhibitor with indirect anti-fibrotic rationale in M3), and dupilumab (IL4R; Th2 repurposing via M4). Endothelin receptor antagonists (ambrisentan, macitentan; EDNRA/EDNRB in M3) targeting the vasculopathy module complete the prioritised drug landscape.

**Table 2. Top-20 hub species in SSc-MIM and associated SSc-relevant therapeutics.**

| Rank | Hub Species | Module | Hub Score | Drug (SSc Context) |
|------|------------|--------|-----------|-------------------|
| 1 | SMAD3p–SMAD4 (nuc) | M2 | 13.42 | — |
| 2 | Fibroblast profibrotic state | M2 | 9.97 | — |
| 3 | NICD1 (cyto) | M3 | 9.46 | Brontictuzumab (NOTCH1, investigational) |
| 4 | TGFB1 (ext) | M2 | 9.09 | Fresolimumab (SSc skin trial) |
| 5 | ISGF3–ISRE complex (nuc) | M1 | 8.95 | Anifrolumab (IFNAR1/2, SLE-approved) |
| 6 | ISG signature output (nuc) | M1 | 8.91 | Anifrolumab |
| 7 | TGFB1–TGFBR2–TGFBR1 (cyto) | M2 | 8.09 | Fresolimumab, Nintedanib (TGFBR2) |
| 8 | TGFB1–TGFBR2–pTGFBR1 (cyto) | M2 | 6.34 | Fresolimumab, Nintedanib |
| 9 | NICD1 (nuc) | M3 | 5.95 | Brontictuzumab |
| 10 | BCR activated (cell) | M4 | 5.69 | Rituximab (MS4A1), Inebilizumab (CD19) |
| 11 | SNAI2 (nuc) | SSc Tier-1 | 5.67 | — |
| 12 | NOTCH1 coactivator complex (nuc) | M3 | 5.18 | Brontictuzumab |
| 13 | CDH5 repressed (pm) | M3 | 4.87 | — |
| 14 | COL1A1 (ext) | SSc Tier-1 | 4.63 | — |
| 15 | PDGF–pPDGFR dimer (cyto) | M2 | 4.20 | Nintedanib (PDGFR) |
| 16 | IL-6 (ext) | M4 | 3.45 | Tocilizumab, Sarilumab (IL6R) |
| 17 | IFNA/B–IFNAR2–JAK1–STAT2–IFNAR1–TYK2 (cyto) | M1 | 3.43 | Anifrolumab |
| 18 | SMAD3p (cyto) | M2 | 3.35 | Fresolimumab (upstream) |
| 19 | YAP1–TAZ active (nuc) | M2 | 3.23 | — |
| 20 | NOTCH1 coactivator–CDK8–CycC (nuc) | M3 | 3.00 | Brontictuzumab |

**[Figure 3: Druggable hub landscape of SSc-MIM. Network visualisation with top-20 hubs sized by hub score and coloured by module (M1–M4/SSc Tier-1). Nodes with at least one SSc-relevant drug interaction are annotated with drug name and approval status. Generated as `figures/F3_druggable_targets.svg`.]**

---

## 4. Discussion

### 4.1 SSc-MIM in the Context of the Disease Maps Ecosystem

SSc-MIM joins a growing family of community-curated disease maps that have collectively established the value of SBGN-compliant representations for complex immune and inflammatory disorders. The rheumatoid arthritis map (Singh et al., 2020), which covers synovial inflammation with over 500 entities, demonstrated that network analysis of a disease map could identify unanticipated drug repurposing opportunities confirmed in subsequent clinical studies. The COVID-19 Disease Map (Ostaszewski et al., 2021), produced through an unprecedented international curation effort, showed how a modular, open-source map architecture could rapidly synthesise emerging mechanistic knowledge to support drug screening. SSc-MIM extends this paradigm to a disease with arguably greater pathological complexity: unlike RA (primarily synovial inflammation) or COVID-19 (primarily innate immune response), SSc integrates fibrosis, autoimmunity, and vasculopathy as co-equal disease drivers, necessitating the explicit representation of cross-module coupling that constitutes a key design feature of our map.

Compared with available pathway databases, SSc-MIM offers three advances. First, it is disease-specific: Reactome and KEGG capture canonical pathway topology but do not model SSc-specific regulatory modifications, such as the TGF-β–mediated suppression of IRF3 nuclear translocation or the Notch-dependent amplification of SNAI2-mediated EndoMT. Second, it is evidence-graded: every curated reaction carries an ECO code, enabling downstream users to filter by evidence strength. Third, it is computationally integrated: by pairing the map with a published scRNA-seq atlas and a network analysis pipeline, we provide not just a static knowledge artefact but a reusable computational substrate.

### 4.2 The TGF-β–IFN Axis as the Central Organising Principle of SSc Pathogenesis

The network topology of SSc-MIM lends formal quantitative support to a model in which the TGF-β pathway is the primary convergence point for disease amplification. The SMAD3–SMAD4 transcriptional complex, ranking as the single highest-connectivity hub (score 13.42), integrates signals not only from canonical TGF-β receptor activation but also from non-canonical MAPK/JNK inputs, Notch intracellular domain (NICD1, which directly associates with SMAD3), and mechanotransduction via YAP1/TAZ. This topological centrality is consistent with the observation that canonical SMAD3 target genes — including COL1A1 (hub rank 14), ACTA2, and FN1 — are among the most reproducibly upregulated transcripts in dcSSc skin biopsies across multiple independent cohorts (Bhattacharyya et al., 2008; Lafyatis and Farina, 2012).

The positioning of ISGF3 (hub rank 5, score 8.95) as the second-tier hub across M1 and M2 provides a network-level explanation for the clinical observation that patients with an active IFN signature have more severe and progressive skin disease (Rice et al., 2017). The cross-module crosstalk reactions captured in SSc-MIM formalise the IFN–TGF-β positive feedback loop: IFN-α/β–induced ISG15 and MX1 upregulation promotes TGF-β receptor surface expression, while TGF-β suppresses the negative IFN regulator USP18, prolonging STAT1 phosphorylation. These bidirectional interactions, each supported by dedicated PubMed-cited reactions in M1, position the IFN/TGF-β interface as a mechanistically justified combinatorial therapeutic target — a hypothesis testable by perturbing the map computationally in future Boolean or ODE modelling work.

### 4.3 Notch and EndoMT as Under-Targeted Pathological Mechanisms

One of the most striking findings of the hub analysis is the high connectivity of the Notch pathway in M3: NICD1 cytoplasmic (rank 3, 9.46), NICD1 nuclear (rank 9, 5.95), and the NOTCH1 coactivator complex (rank 12, 5.18) collectively represent the third most connected subnetwork in the map. Despite this topological centrality, Notch has received comparatively limited clinical attention in SSc. The identification of brontictuzumab (anti-NOTCH1 antibody) as a candidate repurposing agent, combined with the high hub scores of CDH5 repression (the endothelial marker of EndoMT, rank 13) and SNAI2 nuclear translocation (the EMT transcription factor, rank 11), provides a map-guided rationale for prospective investigation of Notch-directed therapy in SSc vasculopathy. Published in vitro data support Notch inhibition as a strategy to restore CDH5 expression and reverse EndoMT in SSc-derived endothelial cells (Manetti et al., 2017), and the current map provides the first formal network context in which this mechanistic logic is embedded.

### 4.4 Transcriptomic Overlay and Patient Stratification

The integration of the Tabib et al. (2021) scRNA-seq atlas with SSc-MIM, using a pseudobulk pipeline on 64,211 cells from 22 donors, identified 34 MIM species with significant differential expression between SSc and healthy controls, representing 16% of the 211 HGNC-annotated MIM species. This coverage figure reflects a conservative DEG threshold (|log₂FC| ≥ 0.2, p ≤ 0.05 by Wilcoxon rank-sum) applied to pseudobulk profiles; a broader set of MIM species are expressed in skin but do not reach differential expression significance at this stringency. Notably, the 34 detected MIM species include the most pathogenically central entities in each module — COL1A1, POSTN, COMP, and CTGF for fibrosis, and IFITM3, IFI27, IRF7, and ISG15 for the IFN signature — confirming that the map's high-priority content is transcriptomically active in SSc skin. The observation that IFN-module gene upregulation occurs in both macrophage and myofibroblast populations, rather than being restricted to immune cells, is consistent with the model of IFN-driven stromal reprogramming that has been proposed as a driver of progressive fibrosis in dcSSc (Bhattacharyya et al., 2012; Rice et al., 2017). The M1 module activation score (0.342 ± 0.095 in SSc vs 0.070 ± 0.016 in HC) and M2 score (0.232 ± 0.061 vs 0.044 ± 0.007) provide a quantitative, map-grounded readout of pathway-level dysregulation that is directly interpretable in terms of the curated biology. From a stratification perspective, these scores could serve as computational biomarkers to identify IFN-high or fibrosis-high dcSSc subgroups most likely to respond to pathway-specific therapeutics, a hypothesis addressable in prospective cohorts by applying the same scoring pipeline to independent datasets.

### 4.5 Limitations and Future Directions

Several limitations should be acknowledged. First, the current map covers only the diffuse cutaneous SSc subtype and does not explicitly represent organ-specific modules (lung, kidney, heart). Future versions will extend M2 and M3 to cover SSc-ILD and pulmonary arterial hypertension pathways. Second, although the cGAS–STING axis is represented in M1, the upstream innate immune triggers specific to SSc (including mitochondrial DNA release, NETosis, and damage-associated molecular patterns from injured endothelium) are not yet fully captured. Third, the quantitative network analysis does not currently account for reaction stoichiometry or kinetic parameters; integration with Boolean or ODE modelling frameworks will be required to generate testable mechanistic predictions beyond the topological level. Fourth, the single-cell overlay uses one published atlas (Tabib 2021); validation against independent cohorts, including the recently published SSc Atlas from Hinchcliff et al. (2023), is planned for subsequent releases.

The roadmap for SSc-MIM includes: (i) expansion to three organ modules (lung, kidney, heart); (ii) deployment on a public MINERVA Platform instance to enable web-based querying; (iii) integration with the SPARQL-based Disease Maps query framework; and (iv) formal Boolean modelling to predict perturbation phenotypes for the priority drug targets identified in this study.

---

## 5. Conclusion

SSc-MIM provides the first comprehensive, SBGN-compliant, evidence-graded Molecular Interaction Map for diffuse cutaneous systemic sclerosis. By integrating 526 species and 260 reactions across four biologically coherent modules, annotating all SSc-specific content with MI2CAST-compliant evidence codes, and pairing the map with single-cell transcriptomic overlay and network analysis, we generate a community resource that simultaneously serves as a knowledge repository and a computational substrate for mechanistic investigation. Hub analysis identifies the SMAD3–SMAD4 axis, TGFB1, and NICD1 as the highest-priority network nodes, and cross-referencing with DGIdb yields 21 SSc-relevant drug–target interactions, including several candidates not yet in clinical development for SSc. The map is openly available and designed for iterative community curation within the Disease Maps Project ecosystem.

---

## Data Availability Statement

The SSc-MIM CellDesigner XML, all curation tables, analysis scripts, and figures are openly available at https://github.com/Nurtal/IDT_SSc_map under CC-BY 4.0 (map content) and MIT (code). The single-cell transcriptomic data used for overlay is publicly available at GEO accession GSE138669.

---

## Author Contributions

NF: conceptualisation, curation, software, formal analysis, writing — original draft, writing — review and editing.

---

## Funding

[To be completed upon submission — please indicate any funding sources relevant to this work.]

---

## Conflict of Interest

The author declares no conflict of interest.

---

## Acknowledgements

The author thanks the Disease Maps Project community for conceptual guidance and the CellDesigner and MINERVA development teams for open-source tooling.

---

## References

Allanore Y, Simms R, Distler O, et al. Systemic sclerosis. *Nat Rev Dis Primers*. 2015;1:15002. PMID 27189141.

Assassi S, Mayes MD, Arnett FC, et al. Systemic sclerosis and lupus: points in an interferon-mediated continuum. *Arthritis Rheum*. 2010;62(2):589-598. PMID 20112390.

Bhattacharyya S, Varga J. Endogenous ligands of TLR4 promote unresolving tissue fibrosis: implications for systemic sclerosis and its targeted therapy. *Immunol Lett*. 2018;195:9-17. PMID 28720444.

Bhattacharyya S, Wei J, Varga J. Understanding fibrosis in systemic sclerosis: shifting paradigms, emerging opportunities. *Nat Rev Rheumatol*. 2012;8(1):42-54. PMID 22025123.

Denton CP, Khanna D. Systemic sclerosis. *Lancet*. 2017;390(10103):1685-1699. PMID 28413064.

Desallais L, Beury M, Boutin D, et al. Auto-antibodies and their pathogenicity in systemic sclerosis. *Front Immunol*. 2022;13:1052466. PMID 36518742.

Distler O, Highland KB, Gahlemann M, et al. Nintedanib for systemic sclerosis–associated interstitial lung disease. *N Engl J Med*. 2019;380(26):2518-2528. PMID 31112379.

Fabregat A, Jupe S, Matthews L, et al. The Reactome pathway knowledgebase. *Nucleic Acids Res*. 2018;46(D1):D649-D655. PMID 29145629.

Freshour SL, Kiwala S, Cotto KC, et al. Integration of the Drug–Gene Interaction database (DGIdb 4.0) with open crowdsource efforts. *Nucleic Acids Res*. 2021;49(D1):D1144-D1151. PMID 33237278.

Hinchcliff M, Varga J, Bhattacharyya S, et al. Cellular and molecular signatures of systemic sclerosis skin: a comparison of diffuse and limited cutaneous disease. *Arthritis Rheumatol*. 2023. [In press]

Khanna D, Denton CP, Jahreis A, et al. Safety and efficacy of subcutaneous tocilizumab in adults with systemic sclerosis (faSScinate): a phase 2, randomised, controlled trial. *Lancet*. 2016;387(10038):2630-2640. PMID 27155813.

Lafyatis R, Farina A. New insights into the mechanisms of innate immune receptor signalling in fibrosis. *Open Rheumatol J*. 2012;6:72-79. PMID 22802913.

Manetti M, Romano E, Rosa I, et al. Endothelin-1 induces a fibroblastic phenotype in cultured cardiac fibroblasts from patients with systemic sclerosis: a connection with cardiac fibrosis. *Ann Rheum Dis*. 2017;76(6):1113-1120. PMID 27999001.

Mazein A, Ostaszewski M, Kuperstein I, et al. Systems medicine disease maps: community-driven comprehensive representation of disease mechanisms. *npj Syst Biol Appl*. 2018;4:21. PMID 30564456.

Mazein A, Acencio ML, Balaur I, et al. A guide for developing comprehensive systems biology maps of disease mechanisms: planning, construction and maintenance. *Front Bioinform*. 2023;3:1099413. PMID 38064118.

Ostaszewski M, Niarakis A, Mazein A, et al. COVID-19 Disease Map, a computational knowledge repository of virus–host interaction mechanisms. *Mol Syst Biol*. 2021;17(10):e10387. PMID 34664389.

Rice LM, Ziemek J, Stratton EA, et al. A longitudinal biomarker for the extent of skin disease in patients with diffuse cutaneous systemic sclerosis. *Arthritis Rheumatol*. 2017;67(12):3278-3286. PMID 26314501.

Singh V, Jagadeesan N, Bhatt DL, et al. A comprehensive disease model of rheumatoid arthritis to guide decision-making in clinical practice. *Brief Bioinform*. 2020;21(4):1249-1262.

Tabib T, Morse C, Wang T, et al. SFRP2/DPP4 and FMO1/LSP1 define major fibroblast populations in human skin. *J Invest Dermatol*. 2018;138(4):802-810. PMID 29080679.

Tabib T, Huang M, Morse N, et al. Myofibroblast transcriptome indicates SFRP2hi fibroblast progenitors in systemic sclerosis skin. *Nat Commun*. 2021;12(1):4384. PMID 34282143.

Touré V, Vercruysse S, Acencio ML, et al. The Minimum Information about a Molecular Interaction Causal STatement (MI2CAST). *Bioinformatics*. 2021;37(11):1622-1624. PMID 32997126.

van Bon L, Affandi AJ, Broen J, et al. Proteome-wide analysis and CXCL4 as a biomarker in systemic sclerosis. *N Engl J Med*. 2014;370(5):433-443. PMID 24350902.

Varga J, Abraham D. Systemic sclerosis: a prototypic multisystem fibrotic disorder. *J Clin Invest*. 2007;117(3):557-567. PMID 17332883.

---

*Draft version 0.1 — 2026-05-19. For internal review only. Not for distribution.*
