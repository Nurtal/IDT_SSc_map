# ROADMAP — SSc-MIM (Skin Fibrosis Molecular Interaction Map)

> Detailed execution plan for the first module of the Systemic Sclerosis Molecular Interaction Map.
> **Window:** 15 May 2026 → 22 September 2026 (18 weeks).
> **Primary target:** ACR Convergence 2026 late-breaking abstract (deadline 22 Sep 2026, 12:00 ET).
> **Backup target:** methodological paper for *Frontiers in Bioinformatics* / *npj Systems Biology and Applications*.

This roadmap expands the [Timeline](README.md#timeline) section of the README into concrete, dated, actionable steps. Each phase lists: **objectives → tasks → deliverables → acceptance criteria → risks**. Weekly granularity. Go/no-go gates are explicit.

---

## Table of contents

1. [Overview and milestones](#1-overview-and-milestones)
2. [Phase 0 — Pre-flight checklist (week 0, 8–14 May 2026)](#phase-0--pre-flight-checklist-week-0-814-may-2026)
3. [Phase 1 — Scoping and groundwork (weeks 1–3, 15 May → 5 Jun 2026)](#phase-1--scoping-and-groundwork-weeks-13)
4. [Phase 2 — Module curation (weeks 4–11, 6 Jun → 31 Jul 2026)](#phase-2--module-curation-weeks-411)
5. [Phase 3 — Integration and deployment (weeks 12–14, 1 Aug → 21 Aug 2026)](#phase-3--integration-and-deployment-weeks-1214)
6. [Phase 4 — Translational use case and figures (weeks 15–17, 22 Aug → 11 Sep 2026)](#phase-4--translational-use-case-and-figures-weeks-1517)
7. [Phase 5 — Writing and submission (week 18+, 12 Sep → 22 Sep 2026)](#phase-5--writing-and-submission-week-18)
8. [Phase 6 — Post-submission (Oct–Dec 2026)](#phase-6--post-submission-octdec-2026)
9. [Cross-cutting workstreams](#cross-cutting-workstreams)
10. [Go / no-go gates summary](#go--no-go-gates-summary)
11. [Acceptance criteria for the final deliverable](#acceptance-criteria-for-the-final-deliverable)

---

## 1. Overview and milestones

| # | Milestone | Target date | Owner | Hard / soft |
|---|-----------|-------------|-------|-------------|
| M0 | Stack installed, repo skeleton committed | 14 May 2026 | Lead curator | hard |
| M1 | Scope locked, clinical co-author signed on | 5 Jun 2026 | Lead curator + rheumatologist | hard |
| M2 | Module M1 (IFN-I) curated and annotated | 19 Jun 2026 | Lead curator | soft |
| M3 | Module M2 (TGF-β / fibrosis) curated | 3 Jul 2026 | Lead curator | soft |
| M4 | **Go/no-go #1** — M1+M2 done? | 24 Jul 2026 | Lead curator | hard gate |
| M5 | Modules M3 + M4 curated | 31 Jul 2026 | Lead curator | soft |
| M6 | Integrated MIM with inter-module crosstalk | 14 Aug 2026 | Lead curator | hard |
| M7 | **Go/no-go #2** — Expert validation done? | 21 Aug 2026 | Rheumatologist | hard gate |
| M8 | MINERVA deployment public/staged | 21 Aug 2026 | Lead curator | hard |
| M9 | Omics overlay computed, figures drafted | 11 Sep 2026 | Bioinformatician | hard |
| M10 | Abstract submitted to ACR 2026 | ≤22 Sep 2026, 12:00 ET | Lead curator | hard |
| M11 | Full manuscript draft circulated | 30 Nov 2026 | Lead curator | soft |

Cadence: **weekly 30-min stand-up** between lead curator and clinical referent; **bi-weekly 1h review** with the bioinformatics co-investigator.

---

## Phase 0 — Pre-flight checklist (week 0, 8–14 May 2026)

> One week of zero-overhead setup before the clock starts.

### Objectives
- Repo, environment, and accounts ready so week 1 starts on curation, not plumbing.

### Tasks
1. **Repo bootstrap.**
   - Initialise the directory structure described in `README.md` → "Repository layout".
   - Commit `LICENSE` (dual: CC-BY 4.0 for content, MIT for code), `CITATION.cff`, `.gitignore`, `CONTRIBUTING.md` (skeleton).
   - Add `.github/ISSUE_TEMPLATE/curation_request.md` and `expert_review.md`.
   - Add `.github/workflows/validate_sbml.yml` (libSBML / SBGN validation on every push to `curation/celldesigner/*.xml`).
2. **Tooling install (local workstation).**
   - CellDesigner v4.4 (verify SBGN-PD export).
   - Java 11+ runtime (CellDesigner / MINERVA dependencies).
   - CaSQ (`pip install casq`); confirm `casq --help`.
   - Cytoscape 3.10+ with BiNoM, stringApp, yFiles layouts.
   - Python env: `mamba create -n sscmim python=3.11 scanpy anndata pandas pyarrow networkx libsbml`.
   - R env (for bulk transcriptomics): `BiocManager::install(c("limma","edgeR","DESeq2","GEOquery","ComplexHeatmap"))`.
3. **Accounts / access.**
   - Account on MINERVA (Luxembourg public instance) — request curator role.
   - GitHub Action runners verified for the SBML validation workflow.
   - Zotero / BibTeX library `pubmed_corpus.bib` created and shared.
4. **Reading queue.**
   - Mazein 2018, Mazein 2023, Ostaszewski 2021 (Disease Maps methodology) — non-negotiable before week 1.
   - RA-map (Singh 2020) and RA-Atlas (Zerrouk 2022) — reference templates.
   - SjD map (Soret 2025) — closest analogue.

### Deliverables
- Empty but well-structured repo, all tooling running, MINERVA account confirmed.

### Acceptance criteria
- `git status` clean on a fresh clone after `make setup` (or the documented manual steps).
- `casq --help`, CellDesigner GUI, Cytoscape, and `python -c "import scanpy"` all succeed.
- An empty CellDesigner `.xml` file can be pushed and passes the validation workflow.

---

## Phase 1 — Scoping and groundwork (weeks 1–3)

> *15 May → 5 June 2026.* Lock the scientific scope, the co-authors, and the corpus.

### Week 1 (15 May → 22 May) — Scoping kickoff

#### Objectives
- Lock the four-module scope with the clinical referent; identify Tier-1 entities per module.

#### Tasks
1. **Kickoff meeting** (1h) with the SSc rheumatologist:
   - Walk through `docs/scoping_notes.md` draft; agree on the four sub-modules (M1–M4).
   - Confirm output phenotypes (sink nodes): myofibroblast activation, ECM deposition, vascular remodelling, ISG signature.
   - Confirm SSc-specific entities to prioritise: CCL2, CCL18, CXCL4/PF4, POSTN, COMP, CTGF/CCN2, FRA-2, TBX2; Topo-I and RNA-pol-III autoantigen axes.
2. **Co-authorship paperwork.** Email confirmation of co-authorship from rheumatologist (file under `docs/`).
3. **Bibliography sprint, day 1–5.** Collect ~50 key reviews via PubMed; tag in Zotero by module (M1–M4) and by type (review / clinical trial / mechanism / dataset).
4. **Reactome pilot import.** Pull the `TGF-beta receptor signaling activates SMADs` BioPAX/SBML via the MINERVA conversion API. Open in CellDesigner. Document any conversion issues in `docs/import_pilot.md`. *This de-risks the entire import strategy before week 4.*

#### Deliverables
- `docs/scoping_notes.md` v1.0 — agreed scope, sink nodes, SSc-specific entities.
- `docs/import_pilot.md` — Reactome import notes, conversion gotchas, workarounds.
- Updated `curation/pubmed_corpus.bib` with ≥50 references.

#### Acceptance criteria
- Scoping notes signed off by the clinical referent (commit co-authored).
- Reactome TGF-β pathway successfully visible and editable in CellDesigner.

### Week 2 (23 May → 29 May) — Curation guidelines and annotation contract

#### Tasks
1. **Adapt `docs/curation_guidelines.md`** from Mazein 2023 — define:
   - Naming convention (HGNC primary symbol; UniProt for proteoforms).
   - Use of CellDesigner notes vs. annotation panels.
   - Compartment vocabulary (extracellular, plasma_membrane, cytosol, nucleus, ECM).
   - State variables convention (phosphorylation sites, cleaved forms).
2. **MI2CAST checklist** (`docs/mi2cast_checklist.md`):
   - Required fields per reaction: participants (HGNC + UniProt), biological role, evidence (PMID + evidence code), mechanism, taxonomy.
   - Template `reaction_evidence.tsv` columns frozen.
3. **Tier ranking.** For each module, build a Tier-1 / Tier-2 / Tier-3 entity list (Tier-1 = must include, Tier-3 = include if time permits). Store in `docs/module_specs/M{1..4}_*.md`.
4. **Bibliography sprint, day 6–10.** Add ~100 primary papers (mechanistic, SSc-specific).

#### Deliverables
- `docs/curation_guidelines.md` v1.0.
- `docs/mi2cast_checklist.md` v1.0.
- `docs/module_specs/M1_IFN_I.md`, `M2_TGFb_fibrosis.md`, `M3_EndoMT_vasculopathy.md`, `M4_IL6_Th2_Bcell.md` — each with Tier-1/2/3 entity tables.

#### Acceptance criteria
- A reviewer (the rheumatologist or a second curator) can take any Tier-1 entity, find the PMID in the bibliography, and reproduce the annotation contract without further instruction.

### Week 3 (30 May → 5 Jun) — Omics dataset decision and re-use audit

#### Tasks
1. **Omics dataset decision.** Compare:
   - **Primary candidate:** Tabib 2021 (GSE138669) scRNAseq SSc skin — fibroblast subsets SFRP2⁺/PRSS23⁺, myofibroblasts, ECs.
   - **Bulk alternative:** Whitfield / GENISOS / PRESS (GSE58095, GSE45485) — intrinsic subsets (inflammatory / fibroproliferative / normal-like).
   - **Decision criteria:** cohort size, public availability of cell-type-resolved data, time-to-figure, novelty for ACR.
   - **Outcome:** commit a one-page decision memo to `docs/omics_decision.md`. *Default: Tabib scRNAseq for the primary use case; Whitfield bulk held in reserve.*
2. **Re-use audit.** For each module, document which Reactome / RA-map / SYSCID / WikiPathways pathways will be imported and which entities will be manually added. Target the 60–70 % import / 30–40 % manual split.
3. **Risk log.** Open `docs/risks.md` mirroring the table in the README, with one paragraph per row describing the trigger and the chosen mitigation.

#### Deliverables
- `docs/omics_decision.md`.
- Per-module re-use tables embedded in `docs/module_specs/M{1..4}_*.md`.
- `docs/risks.md`.

#### Gate to Phase 2
- **All four module specs frozen** — no further re-scoping during curation except at the go/no-go gate (week 7 / 24 Jul).
- Reactome pilot import confirmed reproducible.
- Rheumatologist signed off the scope.

---

## Phase 2 — Module curation (weeks 4–11)

> *6 June → 31 July 2026.* The bulk of the work. One module roughly every two weeks.

### General per-module workflow

Each two-week block follows the same pattern (adjust the import step to the module):

1. **Day 1–2 — Import.** Pull source pathways (Reactome / RA-map / WikiPathways) via MINERVA conversion or direct SBML export → drop in `curation/imports/M{n}/`.
2. **Day 3–5 — Harmonisation.** In CellDesigner: merge imported entities, normalise names to HGNC, deduplicate, set compartments. Output a clean `curation/celldesigner/M{n}_*.xml`.
3. **Day 6–8 — SSc-specific augmentation.** Add Tier-1 SSc entities and reactions not present in the import. Each new reaction must cite ≥1 primary PMID.
4. **Day 9–10 — Annotation.** Fill `species_annotations.tsv` and `reaction_evidence.tsv` for everything new or modified. MI2CAST compliance is mandatory for all SSc-specific reactions.
5. **Day 11–12 — Quality pass.** Run libSBML validation; visual review against the module spec; check sink-node connectivity.
6. **Day 13–14 — Buffer / write-up.** Update `docs/module_specs/M{n}_*.md` with the as-built entity count, deviations from the spec, and open questions for the next expert review.

### Weeks 4–5 (6 Jun → 19 Jun) — Module M1: IFN-I signaling

- **Target:** ~60 species, ~80 reactions.
- **Imports:** Reactome `Interferon alpha/beta signaling`; SYSCID IFN module; RA-map JAK-STAT block.
- **SSc-specific add-ons:** IFN signature in SSc skin (ISG cluster), CXCL4/PF4 as IFN modulator (van Bon 2014), endogenous nucleic-acid sensing (TLR3/7/9, RIG-I/MAVS, cGAS-STING), TBX2 and FRA-2 as transcriptional outputs.
- **Druggable handles to anchor:** IFNAR1/2 (anifrolumab), JAK1/2/TYK2 (tofacitinib, baricitinib).
- **Sink-node anchoring:** ISG signature output node must connect to ≥3 ISGs (IFI44, MX1, OAS1, ISG15).
- **Deliverable:** `curation/celldesigner/M1_IFN_I.xml` + annotations + updated module spec.

### Weeks 6–7 (20 Jun → 3 Jul) — Module M2: TGF-β / SMAD / fibroblast → myofibroblast

- **Target:** ~80 species, ~120 reactions.
- **Imports:** Reactome `TGF-beta receptor signaling activates SMADs`, `Signaling by PDGF`; RA-map fibroblast block.
- **SSc-specific add-ons:** myofibroblast differentiation markers (αSMA/ACTA2, COL1A1, COL3A1, FN1-EDA), POSTN, COMP, CTGF/CCN2, autocrine TGF-β / CTGF loops, mechano-transduction via YAP/TAZ and integrins αvβ3/αvβ6, CCN family crosstalk.
- **Druggable handles:** TGFBR1 (pirfenidone, fresolimumab), IL-13/IL-4Rα (romilkimab — relevant via crosstalk with M4), PDGFR (nintedanib).
- **Sink-node anchoring:** myofibroblast activation + ECM deposition (collagens, fibronectin-EDA).
- **Deliverable:** `curation/celldesigner/M2_TGFb_fibrosis.xml` + annotations.

### Go / no-go gate #1 — End of week 7 (24 Jul) ⚠️

- **Question:** are M1 and M2 fully curated, annotated, and validated?
- **If yes:** continue to M3 + M4.
- **If no (>2 weeks of slip):**
  - **Option A — Scope downgrade to 3 modules.** Drop M3 (EndoMT) since it is the most manual and the least standardised. Re-baseline M3 work as "future module" in the manuscript.
  - **Option B — Push deliverable to EULAR 2027** (typical deadline end-Jan 2027) and focus on the methodological paper.
  - Decision logged in `docs/decisions/2026-07-24_gate1.md`.

### Weeks 8–9 (4 Jul → 17 Jul) — Module M3: EndoMT and vasculopathy

- **Target:** ~60 species, ~90 reactions. **Highest manual fraction (~70–80%).**
- **Imports:** WikiPathways EndMT-related pathways; selected Reactome vascular biology entries.
- **SSc-specific add-ons:** EndoMT markers (loss of CD31/VE-cadherin, gain of αSMA/N-cadherin/FSP1), endothelin axis (EDN1/EDNRA/EDNRB → bosentan, macitentan), NO/sGC/cGMP axis (riociguat), Notch / Snail / Slug signalling, hypoxia (HIF1A) and Raynaud-related triggers, perivascular fibroblast emergence.
- **Druggable handles:** EDNRA/B (bosentan, macitentan), sGC (riociguat), PDE5 (sildenafil).
- **Sink-node anchoring:** vascular remodelling + crosstalk arrow into the myofibroblast pool of M2.
- **Deliverable:** `curation/celldesigner/M3_EndoMT_vasculopathy.xml` + annotations.
- **Risk:** because the upstream import surface is thin, expect a +25 % time buffer; this is why M3 sits before M4 (more manual = more risk = handle earlier).

### Weeks 10–11 (18 Jul → 31 Jul) — Module M4: IL-6 / IL-4 / IL-13 / B-cell crosstalk

- **Target:** ~50 species, ~80 reactions.
- **Imports:** Reactome `IL-6 signaling`; RA-map IL-6 and B-cell modules; SYSCID NF-κB module.
- **SSc-specific add-ons:** Th2 cytokine axis (IL-4/IL-13 → STAT6, fibroblast activation), tocilizumab target (IL-6R), rituximab target (CD20/MS4A1), B-cell → fibroblast indirect activation, plasma cell autoantibody production (Topo-I / Scl-70, RNA-pol-III, ACA).
- **Druggable handles:** IL-6R (tocilizumab), CD20 (rituximab), IL-4Rα (dupilumab, romilkimab).
- **Sink-node anchoring:** autoantibody production + fibroblast crosstalk arrow into M2.
- **Deliverable:** `curation/celldesigner/M4_IL6_Th2_Bcell.xml` + annotations.

### End-of-Phase-2 checkpoint (31 Jul)

- All four module XMLs pass libSBML validation in CI.
- `species_annotations.tsv` and `reaction_evidence.tsv` are complete for every species and reaction.
- `curation/pubmed_corpus.bib` contains every cited PMID; spot-check 10 random reactions for citation accuracy.
- Aggregate count: 200–300 species, 300–450 reactions, 150–250 references — confirm against the README target.

---

## Phase 3 — Integration and deployment (weeks 12–14)

> *1 August → 21 August 2026.* The riskiest scientific step (inter-module crosstalk) and the one hard external dependency (expert review).

### Week 12 (1 Aug → 7 Aug) — Inter-module crosstalk

#### Tasks
1. **Crosstalk inventory.** In `docs/crosstalk_matrix.md`, enumerate every edge that crosses module boundaries. Minimum set:
   - **M1 → M2:** IFN-I priming of fibroblast pro-fibrotic state; CXCL4/PF4 → fibroblast activation.
   - **M3 → M2:** EndoMT-derived perivascular fibroblasts feeding the myofibroblast pool.
   - **M4 → M2:** IL-4 / IL-13 → STAT6 → ECM gene transcription in fibroblasts; IL-6 → STAT3 → fibroblast activation.
   - **M1 → M4:** IFN-I priming of B cells / autoantibody class-switch.
   - **M2 ↔ M3:** TGF-β driving EndoMT in endothelial cells; reciprocal endothelin → fibroblast activation.
2. **Integration into `SSc_MIM_integrated.xml`.** Merge the four module XMLs in CellDesigner; resolve duplicate species (same HGNC ID = same `id`); add crosstalk reactions; preserve module-of-origin tag in CellDesigner notes for downstream MINERVA submap colouring.
3. **Sink-node closure.** Verify that every Tier-1 species reaches at least one sink (myofibroblast / ECM / vascular remodelling / ISG) via a path of length ≤6 in the unsigned graph.

#### Deliverable
- `curation/celldesigner/SSc_MIM_integrated.xml` v0.9 (pre-review).

### Week 13 (8 Aug → 14 Aug) — Expert review round

#### Tasks
1. **Review package.** Prepare a single PDF export of the integrated map (low-resolution overview + four high-resolution sub-maps) + a 1-page summary with open questions, sent to the rheumatologist and 1–2 additional reviewers (SSc study group contacts, requested in week 1).
2. **Schedule three pre-booked 1-hour sessions** with the rheumatologist: overview walk-through, M1–M2 deep dive, M3–M4 deep dive.
3. **Track review comments** as GitHub issues using the `expert_review` template; label `priority:must-fix` vs `priority:nice-to-have`.
4. **Apply fixes** for every `must-fix` before week 14.

#### Deliverable
- Reviewed `SSc_MIM_integrated.xml` v1.0 (review-ready tag).
- `docs/review_log.md` — every comment, status, resolution.

### Week 14 (15 Aug → 21 Aug) — MINERVA deployment and network analysis

#### Tasks
1. **MINERVA deployment.**
   - Upload integrated map to the Luxembourg MINERVA staging instance.
   - Configure submap colouring per module (M1 blue / M2 red / M3 green / M4 orange — to match the future figures).
   - Configure semantic zoom (overview → module → reaction).
   - Verify search by HGNC, UniProt, PMID.
   - Document deployment in `minerva/deployment_notes.md` with the staging URL.
2. **Cytoscape network analysis.**
   - Export integrated map to `.sif` / SBML.
   - Compute degree, betweenness, closeness centrality.
   - Run community detection (e.g. Louvain, GLay) and compare data-driven communities to the four hand-curated modules.
   - Identify the top-20 hub nodes (intersection of high degree + high betweenness).
   - Save Cytoscape session in `analysis/network/ssc_mim_v1.0.cys`; export centrality table to `analysis/network/centrality.tsv`.
3. **Optional Boolean inference.** Run CaSQ on the integrated map; produce `analysis/boolean/ssc_mim.sbml-qual`. Single sanity simulation in GINsim (TGF-β ON → myofibroblast activation reachable).

#### Deliverables
- Public/staging MINERVA URL.
- `analysis/network/centrality.tsv`, top-20 hubs table.
- (Optional) `analysis/boolean/ssc_mim.sbml-qual`.

### Go / no-go gate #2 — End of week 14 (21 Aug) ⚠️

- **Question:** has the expert review actually happened and been integrated?
- **If yes:** proceed to use case.
- **If no:** continue anyway, but reframe the abstract as "expert validation in progress; preliminary inter-module mechanisms". Note the limitation explicitly. Logged in `docs/decisions/2026-08-21_gate2.md`.

---

## Phase 4 — Translational use case and figures (weeks 15–17)

> *22 August → 11 September 2026.* The piece that makes the abstract competitive.

### Week 15 (22 Aug → 28 Aug) — Omics overlay pipeline

#### Tasks
1. **Data ingestion.**
   - **Primary path (Tabib 2021):** download GSE138669 from GEO; load with `scanpy` (`sc.read_10x_*` if raw, else `read_h5ad`). Save as `analysis/overlay/tabib_scRNAseq/adata.h5ad`.
   - **Reserve path (Whitfield bulk):** download GSE58095 / GSE45485 with `GEOquery` in R; harmonise to gene-symbol-level TPM/log-counts.
2. **QC and cell-type annotation.** Reproduce Tabib's published clusters (fibroblast SFRP2⁺, PRSS23⁺; myofibroblasts; ECs; immune subsets). Sanity-check marker expression.
3. **DEG computation.** Cell-type-specific DEGs SSc vs healthy control, per cluster. Wilcoxon test in `scanpy.tl.rank_genes_groups`, FDR < 0.05, |log2FC| ≥ 0.5. Save per-cluster DEG tables.

#### Deliverables
- `analysis/overlay/tabib_scRNAseq/01_qc.ipynb`, `02_clustering.ipynb`, `03_deg.ipynb`.
- Per-cluster DEG tables (`.tsv`).

### Week 16 (29 Aug → 4 Sep) — MIM projection and scoring

#### Tasks
1. **Map species → gene symbol.** From `species_annotations.tsv` build a deterministic HGNC → MIM species lookup.
2. **Project DEGs.** For each cluster, mark MIM species as "up", "down", or "no change" based on the cluster's DEGs. Save as MINERVA-compatible overlay TSV in `minerva/overlays/tabib_*.tsv`.
3. **Per-patient module score.** Compute, per donor, a module-activation score = mean z-score of MIM species' transcripts, separately per module M1/M2/M3/M4. Save patient × module table.
4. **Correlation with clinical variables.** If available in the dataset metadata, correlate module scores with mRSS, disease duration, autoantibody status. Spearman, BH correction.
5. **Druggable hub prioritisation.** Cross top-20 hubs (from week 14) with DGIdb and Open Targets to flag those with available drugs; output `analysis/overlay/druggable_hubs.tsv` with columns: gene, module, hub_score, drug, max_phase, mechanism.

#### Deliverables
- `analysis/overlay/tabib_scRNAseq/04_projection.ipynb`, `05_scoring.ipynb`, `06_drug_targets.ipynb`.
- `minerva/overlays/tabib_*.tsv`.
- `analysis/overlay/druggable_hubs.tsv`.

### Week 17 (5 Sep → 11 Sep) — Figures

Three figures, all built towards the ACR composite. Each must render cleanly as `.svg` and as 300-dpi `.png` at the abstract's submission resolution.

1. **F1 — Global MIM view (`figures/F1_global_MIM.svg`).** Whole map screenshot from MINERVA at the overview zoom, four submodule colours, sink nodes labelled. Add a small legend.
2. **F2 — Overlay by subtype (`figures/F2_overlay_by_subtype.svg`).** Either:
   - A heatmap of module activation scores (patients × modules) with column annotations for clinical variables, or
   - A side-by-side MIM rendering coloured by DEG status for representative fibroblast subsets (SFRP2⁺ vs healthy).
   - **Choose whichever tells the clearer story to a clinician.**
3. **F3 — Druggable targets (`figures/F3_druggable_targets.svg`).** A two-column figure: left, a sub-network of top-20 hubs with module-of-origin colouring; right, a table of hub × drug × current trial phase in SSc.

#### Acceptance criteria
- A non-bioinformatics rheumatologist can read the three figures unsupported and identify (a) the disease axes, (b) which patients are inflammatory vs fibroproliferative, (c) two or three actionable drug-target ideas.

---

## Phase 5 — Writing and submission (week 18+)

> *12 September → 22 September 2026, 12:00 ET deadline.*

### Days 1–3 (12–14 Sep) — First draft

- Draft the 300-word ACR late-breaking abstract in `manuscript/ACR2026_late_breaking_abstract.md`. Required structure:
  - **Background:** SSc unmet need; absence of curated MIM; gap.
  - **Methods:** CellDesigner + MINERVA, MI2CAST annotation, four modules, integration, scRNAseq overlay.
  - **Results:** map volumetrics, top hubs, patient/subset stratification, drug-target shortlist.
  - **Conclusion:** first SSc MIM; opens path to mechanistic stratification and target prioritisation.
- Circulate to all co-authors with a hard 48-hour review window.

### Days 4–7 (15–18 Sep) — Iteration

- Apply co-author comments. Tighten word count. Decide final figure selection (often 1 figure + 1 table is enough for ACR late-breaking; check current-year limits).
- Final author list, affiliations, conflict-of-interest statements.
- Pre-flight: ACR portal account ready, abstract token claimed, figure files within the size limit.

### Days 8–10 (19–22 Sep) — Submission

- Submit by **noon ET on 22 September 2026**, with a 24-hour safety margin (so target submission on **21 September**).
- Save submission confirmation under `manuscript/submission_confirmation/`.
- Tag the repo: `git tag acr2026-submission && git push --tags`.

### Acceptance criteria for the abstract
- Within ACR word limit and figure-count limit (verify on the ACR Convergence 2026 portal — they change yearly).
- All co-authors have signed off in writing (email archived).
- MINERVA URL works from a clean browser session.
- Repo is public (or shareable on request) at the tagged commit.

---

## Phase 6 — Post-submission (Oct–Dec 2026)

> Even if the abstract is accepted, the methodological paper is the long-lived deliverable.

### October 2026 — Full manuscript
- Expand the abstract into a methods + resource paper for *Frontiers in Bioinformatics* or *npj Systems Biology and Applications* (`manuscript/full_paper_draft.md`).
- Sections: introduction, methods (curation + MI2CAST + import strategy), results (map description + network analysis + overlay), discussion (limitations, future modules: lung fibrosis, GI, kidney, PAH).
- Deposit map in BioModels and on MINERVA production instance.

### November 2026 — ACR presentation prep (if accepted)
- Poster (or e-poster, depending on track). Reuse F1–F3 with higher fidelity.
- One-pager handout summarising the MIM URL, repo URL, and the druggable hub shortlist.

### December 2026 — v1.1 release
- Process post-presentation feedback as GitHub issues.
- Release v1.1 with corrections; archive on Zenodo for a citable DOI; update `CITATION.cff`.

---

## Cross-cutting workstreams

These run continuously, not in any single phase.

### Documentation
- Every module spec (`docs/module_specs/`) is updated **on commit** when an entity is added or removed. No batch updates.
- Every go/no-go decision is logged in `docs/decisions/YYYY-MM-DD_*.md`.

### Quality assurance
- **CI:** libSBML validation on every push to `curation/celldesigner/*.xml` (`.github/workflows/validate_sbml.yml`).
- **Weekly internal QA:** the curator picks 5 random reactions, verifies (a) all participants have HGNC + UniProt, (b) PMID is correct, (c) sign/mechanism matches the cited paper. Log results in `docs/qa_log.md`.

### Reproducibility
- All analysis notebooks (`analysis/**/*.ipynb`) are re-runnable from a clean conda env; pin versions in `environment.yml`.
- Random seeds set everywhere a stochastic step occurs (UMAP, Leiden, community detection).
- Each figure has a build script; no manual Illustrator-only edits — annotations are added in a final layer that is itself committed as `.svg`.

### Communication
- Weekly 30-min stand-up between lead curator and clinical referent (notes in `docs/standups/YYYY-Wnn.md`, two-bullet format: *did / blocked*).
- Bi-weekly 1-hour review with the bioinformatics co-investigator.
- Monthly progress note shared with the SSc study group contacts (kept short to preserve goodwill).

### Outreach
- Week 4: open a draft GitHub Discussion linking the repo to the Disease Maps Project Slack / mailing list — invites curation peers (RA-map, SjD map teams) for informal feedback during Phase 2–3.
- Week 14: announce MINERVA staging URL on the Disease Maps Project channel.

---

## Go / no-go gates summary

| Gate | Date | Question | Yes path | No path |
|------|------|----------|----------|---------|
| G1 | 24 Jul 2026 | M1 + M2 fully curated and annotated? | Continue M3 + M4 | Drop M3, or push to EULAR 2027 + paper-only |
| G2 | 21 Aug 2026 | Expert review completed and integrated? | Proceed with full-confidence framing | Submit with "validation in progress" caveat |
| G3 | 18 Sep 2026 | Abstract co-author sign-off achieved? | Submit on/before 21 Sep | Push to EULAR 2027 |

---

## Acceptance criteria for the final deliverable

The project at submission time (M10, 22 Sep 2026) is considered successful when **all** of the following are true:

1. **Map content.** Integrated `SSc_MIM_integrated.xml` validates; 200–300 species, 300–450 reactions, 150–250 references; MI2CAST-compliant annotations on every species and reaction.
2. **Deployment.** Public or staged MINERVA URL accessible, with semantic zoom and at least one functional data overlay.
3. **Translational use case.** scRNAseq (or bulk) overlay yields a clinically-readable per-patient or per-subset stratification, with a drug-target shortlist of ≥10 entries that includes at least 3 currently in SSc trials.
4. **Figures.** Three figures, ACR-ready, with a non-bioinformatician readable narrative.
5. **Abstract.** Submitted on or before the ACR deadline, all co-authors signed off, MINERVA URL referenced in the abstract or supplementary material.
6. **Repository.** Public-ready (or moments away from it), tagged `acr2026-submission`, CI green.
7. **Backup path open.** Full paper draft outline exists, ready to expand for *Frontiers in Bioinformatics* or *npj Systems Biology and Applications*.

---

*Last updated: 15 May 2026 — start of Phase 1.*
