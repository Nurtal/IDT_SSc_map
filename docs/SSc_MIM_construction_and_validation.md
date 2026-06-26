# SSc-MIM — Construction, data usage & validation (detailed recap)

> **Purpose.** A single, exhaustive reference describing *how the SSc Molecular Interaction Map
> (SSc-MIM) is built, what data feeds it, how that data is used, and how every interaction is
> validated.* It is written for expert reviewers and co-authors.
>
> **Scope.** First module-set of a curated, SBGN-compliant disease map for **diffuse cutaneous
> systemic sclerosis (dcSSc) skin fibrosis**.
>
> Authoritative state lives in the git history and `STATUS.md`; this document explains the *process*.
> Numbers below reflect the current `main` (2026-06-24) unless a snapshot is noted.

---

## 1. At a glance

| Quantity | Value |
|---|---|
| Molecular species | **568** |
| Mechanistic reactions | **308** |
| Cell/tissue compartments | **20** |
| Biological modules | **5** (+ crosstalk layer) |
| Phenotype endpoints (sinks) | **6** |
| Hand-curated SSc-specific reactions | **133** (126 with a primary PMID) |
| PubMed references mined & filled | ~360 (`curation/pubmed_corpus.bib`) |
| Patient single-cell datasets overlaid | **4** (197 donors: 121 SSc / 76 HC) |
| Map species measurable in patient data | **82.6 %** |
| Interactions queued for expert review | **143** |

The map is authored in **CellDesigner**, stored as **SBML Level 2 Version 4** with CellDesigner
annotations (`curation/celldesigner/SSc_MIM_integrated.xml`), annotated to the **MI2CAST** standard,
and released openly (GitHub; Zenodo DOI at v1.0). **Topology is literature-derived; patient omics are
layered on top — they do not define the map structure.**

---

## 2. Standards & conventions

Curation is deliberately **deterministic** (two curators following the rules should produce the same
map). Rules are in `docs/curation/curation_guidelines.md`, adapted from Mazein *et al.* (*Front Bioinform*
2023) and the Disease Maps Project conventions.

- **Editor / notation:** CellDesigner v4.4, SBGN Process Description glyphs (macromolecule, simple
  chemical, complex, nucleic-acid feature, phenotype, process / omitted process; stimulation,
  catalysis, inhibition, necessary-stimulation arcs).
- **Format:** SBML L2V4; validation enforced by CI (`validate_sbml` workflow) on every push.
- **Naming (identifiers):**
  - Human gene/protein → **HGNC primary symbol** (`TGFB1`, `SMAD3`, `IFNAR1`).
  - Proteoform → HGNC + state (`SMAD3_phos`, residue in state variable, e.g. `SMAD3@S423`).
  - Complex → participants joined with `:` (`SMAD2:SMAD3:SMAD4`).
  - Small molecule → ChEBI ID + label; Drug → INN lowercase; Phenotype → `phenotype_<slug>`.
  - `id` unique across the integrated map.
- **Compartments:** fixed vocabulary (extracellular, ECM, plasma_membrane, cytosol, nucleus, ER,
  endosome, mitochondrion, …); cell-type prefix only where mixed-cell modules need it (e.g.
  `EC_cytosol`). New compartments require a documented decision.
- **Reaction granularity:** one reaction per ligand–receptor binding; one per kinase–substrate pair
  (residues collapsed into a state-variable list); transcription as `TF → mRNA(target)` per target.

---

## 3. Map architecture

Five biologically coherent modules plus a crosstalk layer, all draining into six phenotype **endpoints**
("sinks" — the biological and clinical outputs of the disease):

| Module | Biology | Reactions |
|---|---|---|
| **M1 — Type-I interferon** | cGAS–STING, RIG-I/MAVS, TLR3/7/9 → IRF3/7 → ISG signature | 19 |
| **M2 — TGF-β & fibrosis** | latent TGF-β activation → SMAD2/3 → fibroblast→myofibroblast, collagen/ECM | 58 |
| **M3 — EndoMT & vasculopathy** | endothelin, Notch, NO/sGC, HIF → endothelial-to-mesenchymal transition | 27 |
| **M4 — Cytokines (IL-6 / IL-4 / IL-13)** | IL-6/STAT3, IL-4/IL-13/STAT6 → fibroblast/ECM (Th2 cytokine axis) | 11 |
| **M5 — B-cell & autoreactivity** | BCR, CD19/20/22/40, BAFF–APRIL/BCMA, PRDM1/XBP1/IRF4 → autoantibodies | 10 |
| **crosstalk** | inter-module edges (e.g. IL-6→SMAD3, IFN-I→fibroblast) | 8 |

M4 (the old "IL-6/Th2/B" module) was split on 2026-06-25 into **M4 (cytokine)** and **M5 (B-cell /
autoreactivity)** — this also fixed an annotation bug (IL-4/IL-13 had sat under `ssc_tier1`). M5 is
independently validated (see §6.10).

**Six phenotype endpoints (sinks)** — the biological and clinical outputs the cascades converge on:

| Endpoint | Compartment | Module | Incoming reactions |
|---|---|---|---|
| Myofibroblast activation | cell | M2 (+M3) | 11 |
| Autoantibody production (**autoreactivity**) | extracellular | M5 | 4 |
| Vascular remodelling | cell | M3 | 2 |
| Type-I IFN / ISG signature | cell | M1 | 1 |
| ECM / collagen deposition | ECM | M2 | 1 |
| Skin severity (mRSS) | cell | clinical | 1 |

Four are the canonical biological sinks (myofibroblast, ECM, vascular, ISG); **autoantibody production
captures SSc autoreactivity** (the M5 B-cell output) and **skin severity (mRSS)** is the
clinical-severity readout. Myofibroblast activation is the dominant convergence hub (11 incoming
reactions, including M3→M2 EndoMT edges).

**Modelling rule (verified by `make sink-check`):** every disease-relevant entity must reach an endpoint
in **≤ 6 steps** — current map has **0 violations**. This turns the diagram into a testable model
where any perturbation has a traceable path to a clinical-level read-out.

---

## 4. Construction pipeline

```
Scope → Reactome backbone import → harmonise/dedup → integrate
      → SSc-specific curation (gated discovery) → annotate (PMID/ECO) → QC → release
```

### 4.1 Scope definition
Module boundaries and the per-module **Tier-1 entity tables** are specified in `docs/module_specs/M*.md`
and linted by `scripts/check_module_specs.py` (`make specs-check`). These tables are the contract for
what each module should contain — the first thing experts are asked to challenge.

### 4.2 Reactome backbone import
Canonical pathway scaffolds are imported from **Reactome** per module and converted to CellDesigner:
- M2 TGF-β (pilot R-HSA-2173789), PDGF; M1 type-I IFN; M3 NOTCH1 (R-HSA-1980143); M4 IL-6.
- `scripts/reactome_pilot.py` → `scripts/post_process_reactome.py` (decode/classify) →
  `scripts/harmonise_imports.py` (rename to HGNC, classify reaction types, **de-duplicate species
  across modules**). Targets: `make pilot harmonise`.

### 4.3 Integration
`scripts/integrate_modules.py` (`make integrate`) merges the harmonised module XMLs into the single
`SSc_MIM_integrated.xml`. PMIDs embedded in the Reactome SBML are mined
(`scripts/extract_pmids_from_biopax.py`, `make pmids`) and the bibliography auto-filled from NCBI
E-utils (`scripts/bib_lookup.py`, `make bib-lookup`).

### 4.4 SSc-specific curation layer (the novel content)
The 133 SSc-specific reactions in `curation/ssc_curated_reactions.tsv` are the genuinely new
contribution (Reactome cannot structurally hold autoantibodies, SSc cell states, GWAS-function,
clinical crosstalk). Sources:
- A **systematic 77-paper literature worklist** (24 themes), and
- **Co-author full-text PDFs** (open-access + non-OA), mined for verbatim mechanism sentences.

Provenance of the 133 rows (column `provenance` / `ratification`):

| Provenance | n | Meaning |
|---|---|---|
| `original-curation` (`human-original`) | 40 | hand-curated by the lead curator |
| `fulltext-verified-claude` | 27 | AI-extracted from full text, verbatim-grounded |
| `claude-reclassify` | 10 | reclassified cell-state assertions (conceptual bridges) |
| `claude-lit-mine` | 8 | AI literature-mined, abstract-verified |
| `ai-discovery` (gated) | 48 | proposed via the G0–G4 edge-discovery pipeline (§6) |

Every AI-touched row is tagged, reversible (one TSV row), and carries its grounding quote in `notes`.

---

## 5. Evidence & provenance model

### 5.1 Two provenance layers — the honest denominator
The headline reaction count mixes two layers; conflating them inflates apparent SSc-specific depth:

| Layer | Reactions | With PMID | Experimental ECO |
|---|---|---|---|
| **Reactome backbone** (`reaction_evidence.tsv`) | 159 | 158 (99 %) | 0 (propagates curator inference) |
| **SSc-specific** (`ssc_curated_reactions.tsv`) | **133** | 126 (95 %) | majority experimental (see 5.2) |

The SSc-specific layer is the correct denominator for "how much new SSc curation this resource adds".

### 5.2 Tiered citation policy (ECO codes), current distribution
Each SSc reaction carries an **ECO evidence code**; experimental evidence ranks above inference:

| ECO | Meaning | n |
|---|---|---|
| `ECO:0000314` | direct assay (experimental) | 73 |
| `ECO:0000033` | traceable author statement | 27 |
| `ECO:0000270` | expression pattern | 20 |
| `ECO:0000305` | curator inference (no direct experiment) | 9 |
| `ECO:0000353` | physical interaction | 2 |
| `ECO:0000315` | mutant phenotype | 2 |

### 5.3 Curation-status taxonomy
| status | n | Meaning |
|---|---|---|
| `confirmed` | 122 | primary citation in place |
| `phenotype_aggregation` | 6 | definitional phenotype sinks (no single molecular interaction to source) |
| `conceptual_bridge` | 4 | honest reclassification of cell-state assertions (now sourced) |
| `to_complete` | 1 | `ssc_M2_012` POSTN — citation removed + mechanism under expert review |

### 5.4 Reaction-type vocabulary
Controlled set: binding, catalysis, phosphorylation, transcription, activation, inhibition,
state_change, transport, degradation, dissociation, contributes. Any auto-inferred type is traced in
`notes` and reversible. Guard: `make evidence-lint` fails CI if any SSc reaction is left untriaged
(no undeclared "inference debt").

---

## 6. Interaction validation process

Validation is layered: **machine gates → automated review → human ratification.** The governing rule
is *the curated map is never written speculatively.*

### 6.1 Edge-discovery protocol (adding a new interaction)
`docs/curation/edge_discovery_protocol.md`. Pipeline:
```
SSc papers → candidate edges (staging) → G0–G4 gates → human ratification → promote → wire/audit/lint
```
1. **Stage** in `curation/staging/ssc_edge_candidates.tsv` (never the curated TSV). Each candidate
   carries a **verbatim supporting sentence** from the source paper.
2. **Fetch** source text (`make corpus-fetch`): Europe PMC OA full text or abstract, cached.
3. **Gate** (`make validate-edges` → `validation_report.tsv`).
4. **Ratify**: a human sets `decision = promote` (default empty = held).
5. **Promote** (`make promote-edges`): only PASS + `decision=promote` rows are appended, tagged
   `AI-proposed (discovery)`, quote preserved — one reversible row each.
6. **Rebuild**: `make wire network evidence-audit evidence-lint preflight`.

### 6.2 The five gates (G0–G4) — `scripts/validate_edge_candidates.py`
| Gate | Check | Failure |
|---|---|---|
| **G0 schema** | required fields present; `type` in controlled vocabulary | REJECT |
| **G1 HGNC** | every gene entity is an official HGNC symbol (HGNC REST, cached) | REJECT (alias → FLAG) |
| **G2 grounding** | the supporting quote is a **verbatim substring of the cached source text** | **REJECT** — anti-hallucination keystone |
| **G3 novelty** | the (input→product) gene pair is not already an SSc reaction (dedup hard reject); not a forward Reactome pair (advisory flag) | REJECT (dup) / FLAG |
| **G4 evidence** | numeric PMID present; corpus text available (SSc context) | FLAG |

Verdicts: **PASS** (clean) / **FLAG** (soft issue) / **REJECT** (hard fail). **If the quote is not
literally in the paper, the edge is rejected** — this is the core defence against fabricated biology.

### 6.3 Negative-control fixture
A deliberately fabricated edge (`cand_negctrl`: FOXP3→COL1A1 with an invented quote and a decoy PMID)
is kept in `ssc_edge_candidates.tsv`. The G2 grounding gate must reject it (`REJECT G2:NOT_GROUNDED`)
on every run — a live, self-testing proof that the anti-hallucination gate works. It is excluded from
the reviewer app so it never reaches a human as if legitimate.

### 6.4 Structural validation
- **SBML validation** (`scripts/validate_sbml.py`, `make validate`) — libSBML L2V4; enforced in CI.
- **Sink-connectivity audit** (`make sink-check`) — every entity reaches a phenotype sink ≤6 steps.
- **CellDesigner-loadability** static test (`make celldesigner-check`).
- **MINERVA-readiness preflight** (`make preflight`).

### 6.5 Contradiction detection
`scripts/check_contradictions.py` (`make check-contradictions`) flags any gene pair given **opposite
polarities** (activation vs inhibition) by different sources, routing them to human arbitration.
Current map: 0 unresolved contradictions after polarity-aware multi-source dedup.

### 6.6 Automated citation review (AI verdict pass)
Built on a **literature dossier** and **reading packets**:
- `scripts/mine_evidence_dossier.py` (`make dossier`): for every interaction, a PubMed pass returns
  **candidate supporting** references and a **separate "possibly contrary"** list (null-result or
  opposite-direction cues). All are real PMIDs retrieved by query — none fabricated.
- `scripts/build_reading_packets.py` (`make reading-packets`): fetches the abstracts and assembles a
  per-interaction reading packet (claim + mechanism + deciding quote + every support/contrary abstract).
- An **advisory verdict** per interaction is recorded in `curation/ai_review_verdicts.json` after
  reading the packet: **validate / revise / caution**. Current: **128 validate / 5 caution**
  (after the citation sweep below).

### 6.7 Citation-integrity sweep (2026-06-24)
The review pass detected **28 reactions whose cited PMID pointed to an unrelated paper** (biology
canonical, citation a data-entry slip — e.g. a TGF-β reaction cited to a rubella study, a Melbourne
food survey, or a plant-microfluidics paper). For each, a replacement PMID was **retrieved and
verified against live PubMed** (no PMID cited from memory), applied to the source TSV with a
traceability note, and the verdict updated. One case (`ssc_M2_012`, POSTN) was downgraded to
`caution` (mechanism question, not just citation). Full table: `curation/citation_revise_report.md`.

### 6.8 Reviewer adjudication app
`review/index.html` — an offline, self-contained swipe-deck app that snapshots the **interaction
database** (`analysis/curation/interaction_database.csv`, **143 interactions**, built by
`scripts/build_interaction_db.py`). Each card shows: regulator→target, mechanism, SSc relevance, the
**verbatim deciding sentence** (from local PDF / PMC full text / PubMed abstract, via
`scripts/mine_pdf_quotes.py`), source links, ECO/provenance, the advisory AI verdict, the literature
dossier, and an in-browser module map. Reviewer decisions (accept/reject/note) persist locally and
export to CSV/JSON. Discarded/excluded edges are included so the reviewer keeps full control.

### 6.9 Human ratification (binding)
The final gate is **co-author / expert sign-off**: the corresponding author ratifies the biology
(`decision=promote`, per-row `ratification` tag) and adjudicates the 143 interactions via the app.
AI proposes and self-gates; the human decides. `make ratification-worksheet` produces a
tick-and-correct sheet for the proposed SSc citations.

### 6.10 Module-level validation (M5, B-cell / autoreactivity)
When M4 was split, the new **M5** module was validated on patient data (full report:
`analysis/overlay/M5_validation.md`, figure `figures/F7_M5_validation.png`):
- **Internal** — on a B/plasma-restricted pseudobulk (Gur cohort, 61 SSc / 19 HC), M5 AUCell is
  higher in SSc (0.085 vs 0.047, p=0.046) and is the **only** significant module in that compartment
  → the signal is specific to autoreactivity (whole-tissue scoring missed it: B/plasma cells are too
  rare to surface in the top-5 % ranking).
- **External** — on **GSE45536** (Streicher *et al.*, 99 scleroderma / 24 healthy whole-blood, GPL570),
  M5 separates SSc from HC (p=1.3×10⁻⁴). Sub-signatures: the SSc **autoantigen targets TOP1
  (anti-Scl-70) and CENPB (anti-centromere) are strongly elevated** (p=1.7×10⁻¹⁰), while circulating
  B/plasma abundance is reduced (peripheral lymphopenia). The M1/IFN positive control is elevated in
  SSc in both datasets (p=3.8×10⁻⁵), validating the scoring method.

---

## 7. Patient data — what is used and how

> **Important:** the omics data is used to **ground, validate and read out** the map — it does **not**
> define the map topology (which is literature-curated).

### 7.1 The four datasets (citations verified against PubMed)
| GEO accession | Reference | Tissue | Platform | Donors (SSc/HC) |
|---|---|---|---|---|
| **GSE195452** | Gur C *et al.* **Cell** 2022;185:1373-1388 (PMID 35381199) | Skin (multiome) | scRNA-seq | 154 (97 / 57) |
| **GSE138669** | Tabib T *et al.* **Nat Commun** 2021;12:4384 (PMID 34282151) | Skin | 10x scRNA-seq | 22 (12 / 10) |
| **GSE128169** | Morse C *et al.* **Eur Respir J** 2019;54:1802441 (PMID 31221805) | Lung (ILD) | 10x scRNA-seq | 13 (8 / 5) |
| **GSE210395** | GEO — no linked publication | PBMC | scRNA-seq | 8 (4 / 4) |

**Total: 197 donors (121 SSc / 76 HC).** Skin cohorts (≈100k and 64k annotated cells) give the
fibroblast-subset resolution that M2/M3 model; lung (SSc-ILD) and PBMC extend the map beyond skin.
Raw archives are SHA-256-pinned in `data/MIRROR.md` for a reproducible input envelope (Zenodo mirror).

### 7.2 Overlay pipeline (`scripts/build_overlay_multi.py`, `make overlay-multi`)
1. **Re-process** each dataset from raw counts with **scanpy** (QC, normalisation, Leiden clustering,
   cell-type annotation).
2. **Pseudobulk** per donor; **differential expression** SSc-vs-HC with a **mixed-effects negative-
   binomial GLM** (`scripts/deg_mixed_effects.py`) + **Benjamini-Hochberg FDR** (q=0.05).
   (Legacy Wilcoxon backend retained via `--deg-backend wilcoxon-v10`.)
3. **Map onto species**: differentially-expressed genes are matched to map species → **coverage**.
4. **Per-donor module scoring** with **AUCell** (`scripts/score_aucell.py`, `make aucell`): each
   patient becomes a **5-module activation vector** (M1–M5 + Tier-1). M5 (B-cell) is scored on a
   B/plasma-restricted pseudobulk (`scripts/build_bplasma_pseudobulk.py`), since B/plasma cells are
   too rare to surface in a whole-tissue ranking.
5. **MINERVA overlays** (60 TSVs in `minerva/overlays/`) colour the map by cluster/dataset.

### 7.3 Validation results
- **Coverage = 82.6 %** of detectable map species observed in patient data (195/236;
  `analysis/overlay/coverage_v1.1.json`): M1 82 % · M2 87 % · M3 79 % · M4 72 % · M5 100 % · Tier-1 80 %.
- **Biological check (AUCell, SSc vs HC, Mann-Whitney):** M1/type-I IFN significantly elevated in SSc
  **skin** — Gur p = 6.4×10⁻⁸, Tabib p = 5.8×10⁻³ (`module_score_contrasts_v1.1.json`).
- **Cell-type annotation validated** independently with **CellTypist** (Adult_Human_Skin): κ = 0.92,
  ARI = 0.70 vs marker-based labels (`make celltypist`).
- **Coverage sensitivity** swept over a (p-adj, |log2FC|) grid (`make coverage-sensitivity`).

---

## 8. Downstream analyses enabled

- **Network analysis** (`scripts/network_analysis.py`, `make network`): centrality, top hubs,
  Leiden communities. Emergent hubs match known SSc biology (TGF-β:receptor, SMAD3–SMAD4, ISG
  signature, PDGFR). Hub robustness checked under edge perturbation.
- **Novelty vs Reactome/KEGG** (`make novelty reactome-novelty`): Jaccard/per-reaction overlap shows
  the SSc-specific layer is largely Reactome-novel.
- **Druggable-hub prioritisation** (`scripts/druggable_hubs.py`, `make druggable`): hubs × DGIdb →
  recovers targets already in SSc trials (tocilizumab/IL-6, nintedanib, romilkimab/IL-13,
  pamrevlumab/CCN2, bosentan/endothelin); table recalibrated against real SSc trial outcomes.
- **Boolean / executable model** (`scripts/boolean_inference.py`, `make casq boolean`): CaSQ converts
  the SBGN-PD map to SBML-qual for GINsim/BioLQM/MaBoSS.
- **Endotype characterisation workflow:** because each donor/cluster becomes a module-activation
  vector and its DEGs light up specific sub-circuits, **externally-defined patient clusters can be
  projected onto the map** (same AUCell + per-cluster DEG + MINERVA machinery, any cluster label) to
  obtain, per cluster: a **module fingerprint**, **mechanistic hypotheses** (which sub-circuits
  differ, e.g. STING→IRF3 vs TGF-β→SMAD3→collagen), and **candidate cluster-matched targets**.

---

## 9. Reproducibility & release

- **Pipeline:** `make auto` runs the whole automated lane end-to-end; `make lint` / `make validate`
  run all content + SBML linters. `make pytest` runs the test suite (no data needed).
- **CI:** GitHub Actions — `validate_sbml`, `lint`, `scripts-smoke`, figures-CI.
- **Containerisation:** `Dockerfile` / `.github/workflows/docker.yml` for a pinned environment.
- **Provenance & metadata:** `ro-crate-metadata.json` (RO-Crate manifest), MIRIAM/CVTerm injection
  for **BioModels** submission (`make biomodels`), `CITATION.cff` + `.zenodo.json`.
- **Input-data mirror:** `data/MIRROR.md` + `data/MIRROR.sha256` (SHA-256-pinned GEO archives).
- **Release:** GitHub + **Zenodo DOI** at `git tag v1.0`; `make release` pre-flights.

---

## 10. Artifact map (where to look)

| Path | Contents |
|---|---|
| `curation/celldesigner/SSc_MIM_integrated.xml` | the integrated SBML map (568 sp / 308 rx / 20 comp) |
| `curation/ssc_curated_reactions.tsv` | the 133 SSc-specific reactions (source of truth) |
| `curation/annotations/` | species annotations (HGNC) + reaction evidence (PMID/ECO) |
| `curation/staging/` | edge candidates + G0–G4 `validation_report.tsv` (gating) |
| `curation/ai_review_verdicts.json` | per-interaction advisory verdicts |
| `curation/citation_revise_report.md` | the 28 corrected citations (wrong → verified) |
| `curation/pubmed_corpus.bib` | bibliography (~360 entries) |
| `analysis/curation/interaction_database.csv` | reviewer-ready 143-interaction database |
| `analysis/overlay/` | DEG, coverage, per-donor AUCell scores, contrasts |
| `analysis/network/` | hubs, communities, novelty |
| `minerva/overlays/` | 60 MINERVA overlay TSVs |
| `review/index.html` | offline reviewer swipe-deck app |
| `docs/module_specs/M*.md` | per-module scope + Tier-1 tables |
| `docs/curation/curation_guidelines.md`, `docs/curation/edge_discovery_protocol.md` | the rules + the gate procedure |
| `figures/` | F1 map, F2 AUCell overlay, F3 druggable hubs, F6 endotype profiles |
| `STATUS.md`, `ROADMAP.md` | state + plan |

---

## 11. Limitations & honest caveats

- **Topology is curated, not learned.** The map encodes literature-supported mechanisms; it is a
  hypothesis scaffold, not a statistically inferred network.
- **Reactome backbone propagates curator-inference ECO** by default — the SSc-specific layer (133
  reactions) is the honest measure of new curation depth.
- **Coverage ≠ validation of every edge.** 81.3 % means most map species are *measurable* in patient
  data, not that every reaction is independently confirmed.
- **Per-donor module deltas are modest outside M1/skin**; the strong, reproducible signal is the
  type-I IFN axis in skin. Endotype use is presented as a **capability/direction**, not a finished
  stratification.
- **Some structural scaffolds await GUI wiring** (CellDesigner round-trip of remaining stubs).
- **AI assistance is gated and reversible**, but **human ratification of the biology is the binding
  step** and is still in progress for the 143 interactions.
- **GSE210395** has no linked publication; it is used by accession only and cited as such.
- `ssc_M2_012` (POSTN) is intentionally left `to_complete` pending an expert mechanism decision.
