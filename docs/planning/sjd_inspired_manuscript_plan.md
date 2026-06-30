# Manuscript plan — "The SSc Map", modelled on the SjD Map

> Written 2026-06-30. Plan for the SSc-MIM resource paper, structured to parallel the **SjD Map**
> (Niarakis et al., *npj Systems Biology and Applications* 2026; PMID 41904187, PMC13230593) — the
> immediate sibling resource in our target journal. All SSc-MIM figures below are the **verified
> current repo values** (audited 2026-06-29/30). Companion to the existing IMRAD draft
> `manuscript/SSc_MIM_manuscript_draft.md`; this document records the *positioning* and the
> *module-framing decision*, not new prose.

## 1. What the SjD Map actually does (verified from full text, not the abstract)

**Hybrid construction — data + knowledge (both):**
1. **Transcriptomics:** differential expression on **3 whole-blood datasets** — GSE51092 (190 SjD/32 HC,
   microarray), UKPSSR (151/29, microarray, NECESSITY consortium), PRECISESADS (304/341, RNA-seq).
   → 1,625 DEGs, 25 shared across all three, 9 linked to IFN → pathway enrichment (137 pathways,
   **43 integrated** into the map).
2. **Literature curation:** systematic PubMed search (`Sjögren AND Human NOT mouse AND (pathways OR
   cytokines OR signal transduction)`, Research/Review, 2010–2024, manual exclusions) + targeted
   "Sjögren + species name" searches.

**Map:** CellDesigner (SBGN process-description), compartmentalised, **MIRIAM**-annotated →
**829 entities / 598 interactions**. *No explicit modules.*

**Validity:** (a) an *annotation score* = number of publications per entity, by category; (b) **external
validation against the OpenTargets database** (coverage of SjD OpenTargets info on the map + UpSet plot).

**Network analysis (two views):** complex network (MINERVA export → Cytoscape → NetworkAnalyzer) and
**Activity Flow** (CaSQ transformation → Cytoscape).

**Deployment:** **MINERVA ELIXIR-Luxembourg** (https://sjdmap.elixir-luxembourg.org/).

**Methods section order (a proven npj-SBA template to mirror):** Datasets · Statistical analyses ·
Map construction process/standards/annotations · Workflow · Curation criteria (literature enrichment) ·
Visualisation and overlays · Coverage and weights · Ethics · Computational resources/runtimes.

## 2. Construction-philosophy difference (assume it — it favours us)

| | SjD Map | SSc-MIM |
|---|---|---|
| **Construction logic** | **omics-driven**: DEG/enrichment *seeds* the map (43 pathways) + literature | **curation-driven**: Reactome backbone + 133 literature-curated SSc reactions; omics is a *corroboration overlay*, not the seed |
| **Induced bias** | what is not DE *in blood* can be missed | captures post-translational signalling (phospho, complexes, translocation) invisible to bulk DEG |
| **Omics** | 3 **bulk blood** cohorts | **4 scRNA-seq multi-tissue** (skin/PBMC/lung; 197 donors, 266,884 cells) **+ 1 bulk blood** (GSE45536, M5 validation) = **5 datasets** |
| **Structure** | 829 entities / 598 interactions, non-modular | 568 species / 308 reactions / 20 compartments, **5 modules** |
| **External validation** | OpenTargets (knowledge base) | transcriptomic coverage (53%/82.6%) + **independent cohort for M5** (GSE45536, p=1.3×10⁻⁴) |
| **Network** | complex network + Activity Flow (CaSQ) | NetworkX centralities + 39 communities; CaSQ/MaBoSS = v2.0 stretch |
| **Drug targets** | mentioned | **DGIdb: 82 hub–drug pairs / 28 targets**, recalibrated vs SSc trials |
| **Curation rigour** | PubMed search + manual filters | **gated edge-discovery (G0–G4)** + verbatim grounding (G2) + reaction↔PMID concordance audit |

**Headline message:** SSc-MIM is the SSc counterpart of the SjD Map within the Disease Maps Project,
**inverting the logic** (curation-first, omics-for-corroboration), and adding single-cell multi-tissue
overlay, a modular structure, and gated citation-integrity curation.

## 3. Module-framing decision (the key methodological stance — settled 2026-06-30)

See memory `ssc-mim-module-framing`. The 5 modules (M1 IFN-I · M2 TGF-β/fibrosis · M3 EndoMT/
vasculopathy · M4 cytokines · M5 B-cell/autoreactivity) are presented as an **expert-defined
pathophysiological scaffold** — the Disease Maps convention — **not** as a data-driven discovery.

- **Primary justification = external validity** (the strong, non-circular argument):
  - module-level transcriptomic activation (M1 IFN, Gur cohort, AUCell Δ=+0.077, p=6.4×10⁻⁸);
  - the independent M5 cohort (GSE45536, p=1.3×10⁻⁴; autoantigen core TOP1/CENPB p=1.7×10⁻¹⁰);
  - clinical/therapeutic correspondence (axes ↔ serological subsets ↔ trial drug classes:
    anifrolumab/JAKi→M1, nintedanib/pirfenidone→M2, ERAs→M3, tocilizumab/dupilumab→M4, rituximab→M5).
- **Modules are the operational unit** of the paper: per-donor AUCell module scores, the M5 validation,
  and the drug-class mapping are all module-level. This is *why* talking about modules makes sense —
  they are load-bearing, not decorative. Unlabelled communities cannot carry this.
- **Unsupervised community detection = secondary internal-consistency check, with the circularity
  stated openly** (greedy modularity runs on the curated graph, so communities reflect curation density;
  they corroborate, they do not independently prove). Re-mapped concordance (topology unchanged by the
  M4→M5 relabel) recovers **all 5 modules** as significantly enriched communities (hypergeometric
  q<0.05, fold 2.7–8.9×); **M5 is the cleanest** (16/19 species in one community, 8.9×). Re-run
  `make network` on the 5-module map (needs a networkx env) to produce these in-pipeline for the figure.
- **Boundary edges are an assumed curatorial choice** → keep the explicit **crosstalk** category
  (8 inter-module reactions).

One-sentence framing for the paper:
> *Modules are an expert-defined pathophysiological reading frame — the convention for curated disease
> maps — whose biological reality is supported externally by module-level transcriptomic activation and
> an independent cohort, and which serve as the operational unit for omics overlay, scoring and drug
> mapping; unsupervised community detection is reported as an internal-consistency check.*

## 4. Title options
- **A** *The SSc Map: a multi-tissue single-cell-anchored molecular interaction map of diffuse cutaneous
  systemic sclerosis skin fibrosis* (SjD register).
- **B** *SSc-MIM: a curated, SBGN-compliant molecular interaction map of skin fibrosis in dcSSc*
  (current draft title).

## 5. Abstract (1 structured paragraph, ~200 words, Nature/SjD format)
Unmet need in dcSSc → curated SBGN MIM built in CellDesigner → **curation-first construction**
(Reactome + 133 literature-curated SSc reactions, 5 modules, MI2CAST/MIRIAM, 0 SBML errors) →
**corroboration overlay**: 4 multi-tissue scRNA-seq datasets (197 donors / 266,884 cells) →
coverage 53%/82.6% → map of 568 species / 308 reactions / 20 compartments → network analysis
(39 communities) + druggable hubs (DGIdb, recalibrated to SSc trials) → **external validation of the
M5 module** (GSE45536, p=1.3×10⁻⁴) → FAIR release (GitHub/Zenodo DOI, RO-Crate, Docker, offline review
app) → integrative framework for mechanistic hypothesis generation and modelling.

## 6. Results — mirror of the SjD Map sequence

| # | Section (SjD parallel) | SSc-MIM content (verified numbers) | Figure |
|---|---|---|---|
| 3.1 | **Architecture & scope** *(≈ "Map building")* | 5 modules; 568/308/20; originality vs Reactome | **F1** global map (pentagon) |
| 3.2 | **Curation & evidence provenance** *(≈ "Curation criteria" + "annotation score")* | 133 reactions, gated G0–G4 + verbatim grounding, MI2CAST; **125/133 (94%) with a primary PMID** post concordance audit; ECO×PMID stratification | **T1** evidence stratification |
| 3.3 | **Multi-tissue single-cell overlay** *(≈ "Gene expression"+"enrichment", as overlay)* | 4 datasets, 62 cluster overlays, pseudobulk NB-GLM+BH-FDR; coverage 53/82.6% (sensitivity grid); AUCell M1-IFN ↑ in SSc (Gur p=6.4×10⁻⁸) | **F2** 4-panel heatmap |
| 3.4 | **Network topology, module validity & druggable hubs** *(≈ "complex network")* | centralities, 39 communities, **module↔community concordance (all 5 recovered, q<0.05, fold 2.7–8.9×)**; DGIdb 82 pairs/28 targets recalibrated focuSSced/SENSCIS/RECITAL | **F3** druggable subnetwork (+ module×community concordance panel) |
| 3.5 | **External validation of module M5** *(≈ "external validation")* | M4→M5 split; GSE45536 (99 SSc/24 HC bulk blood), M5 p=1.3×10⁻⁴, autoantigen core p=1.7×10⁻¹⁰ | **F4 (=F7)** |
| 3.6 | **Availability & functionality** *(≈ "Functionality")* | GitHub+Zenodo DOI, RO-Crate, SBML MIRIAM (BioModels), Docker, offline review app, MINERVA as target | — |

## 7. Methods (sections mirroring SjD)
Datasets (the 5, with an availability/release table like their Table 2) · Scope & modules · Reactome
import + harmonisation · **Gated edge-discovery pipeline (G0–G4) + Tier-1 curation** · MI2CAST/MIRIAM
annotation · SBML L2v4 validation (CI) · scanpy/pseudobulk NB-GLM overlay + AUCell · **Coverage &
weights** (mirror their definition) · NetworkX analysis + module↔community concordance · DGIdb ·
reproducibility (environment.yml, Docker, RO-Crate, CI).

## 8. Discussion
SSc-MIM in the Disease Maps ecosystem (**head-to-head with the SjD Map**: single-cell + multi-tissue +
curation-first + modular as our additions) · TGF-β–IFN axis as organising principle · Notch/EndoMT
under-targeted · coverage = **corroboration, not validation** (post-translational argument) · limits
(no clinical stratification — GEO metadata gap; MINERVA to deploy) · future (MINERVA, CaSQ→MaBoSS
Boolean v2.0).

## 9. Add-on analyses to maximise parity with the SjD Map (optional, high yield)
1. **OpenTargets-style external validation** — replicate their cross-check: coverage of SSc OpenTargets
   targets on SSc-MIM + UpSet plot. Gives an exact counterpart to their Fig. 4 and a *knowledge-based*
   validation alongside the transcriptomic one. (~1 day, new analysis.)
2. **Activity-Flow view via CaSQ** — run `SSc_MIM_integrated.xml` through CaSQ → import to Cytoscape
   (their Fig. 6). Nearly free (the SBML exists) and seeds the Boolean v2.0 milestone cleanly.

## 10. What exists vs what to add
- **Already drafted** (`manuscript/SSc_MIM_manuscript_draft.md`, ~11.7k words): 3.1 / 3.3 / 3.4 +
  Methods + Discussion.
- **To add for SjD parity:** (a) Results 3.2 curation/evidence-provenance; (b) Results 3.5 as a
  standalone M5 validation section; (c) the module↔community concordance panel + external-validity
  framing of the modules (§3 above); (d) structured-format abstract; (e) cite the SjD Map as sibling;
  (f) optionally the two add-ons (§9).

## 11. Open action items
- Re-run `make network` on the 5-module map (networkx env) to regenerate `community_enrichment.tsv`
  with M5 and produce the concordance figure in-pipeline (current file is pre-M5-split, 2026-06-09).
- Resolve the v1.0 release blocker before any tag: `.zenodo.json` still has a `REPLACE_ME` co-author
  entry (see ROADMAP acceptance criteria).
