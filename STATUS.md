# STATUS — SSc-MIM

> Snapshot for orientation. Updated on every batch.
> Authoritative source for completion state is the git log; this file gives one-screen context.

## Headline  *(updated 2026-06-24)*

- **Integrated map:** **568 species, 308 reactions, 20 compartments** (grew from 526/260 via the
  literature-mining growth batches). SBML validation is enforced in CI (`validate_sbml` workflow on
  every push); last local clean run was at the 526/260 state — re-run needs `python-libsbml`
  (not installed in the current shell).
- **SSc-specific curated layer:** **133 reactions** (`curation/ssc_curated_reactions.tsv`), up from 85.
  By module: M2 58 · M3 27 · M4 11 (cytokine) · M5 10 (B-cell/autoreactivity) · M1 19 · crosstalk 8
  (M4 split into M4+M5 on 2026-06-25, M5 validated — see analysis/overlay/M5_validation.md). Status: 122 confirmed, 6
  phenotype_aggregation (definitional sinks), 4 conceptual_bridge (now sourced).
- **npj-SBA revision v1.1 MERGED** (`1116a3e`) — 23/25 reviewer E-items closed: pseudobulk NB-GLM
  DEG + BH-FDR, mixed-effects re-run (**MIM coverage 50% → 81.3%**), AUCell sign-blinded scoring
  (M1 IFN p=3.2e-4 in Gur cohort), hub robustness (E3), community enrichment (E4), drug-target
  recalibration vs SSc trial reality, CellTypist validation (κ=0.92, ARI=0.70), Docker, RO-Crate,
  pytest+CI, BioModels submission package. Manuscript reframed per editor as a **resource paper**.
- **Reviewer-facing interaction QC (June)** — two new lanes, see below:
  1. **Network growth** — systematic literature worklist (77 papers, 24 themes) + co-author PDF
     mining → SSc reactions 85 → 133.
  2. **Swipe-deck review app** (`review/index.html`, offline, self-contained) — **143 interactions**
     adjudicable one-by-one, with verbatim deciding sentence (PDF/PMC/abstract), in-browser module
     map, literature dossier (403 support / 185 contrary refs), and an **advisory AI verdict per
     interaction**: **101 validate / 28 revise / 4 caution**.
- **Citation integrity (June, in progress)** — the AI verdict pass detected **28 reactions whose
  cited PMID points to an unrelated paper** (the biology is canonical; only the reference is wrong —
  e.g. TGF-β/SMAD reactions cited to a rubella, a Melbourne food survey, or a plant-microfluidics
  paper). Replacement PMIDs are being verified against live PubMed. See
  `curation/ai_review_verdicts.json` (`verdict=revise`).
- **Lead-author metadata filled** — `CITATION.cff` + `.zenodo.json` (Nathan Foulquier,
  ORCID 0000-0003-4620-2794, LBAI U1227 Inserm CDC CHU Brest). Co-author slot still REPLACE_ME.

## What's done (with commit refs)

| Phase | Item | Commit |
|-------|------|--------|
| 0 | Repo bootstrap (LICENSE, .gitignore, CITATION.cff, CONTRIBUTING, issue templates, SBML CI) | `4dcf004` |
| 1 | Curation guidelines (Mazein 2023), MI2CAST checklist, four module specs with Tier-1 tables | `4dcf004` |
| 2 | M1 IFN-I + M2 TGF-β/PDGF + M3 Notch1 + M4 IL-6 Reactome imports, harmonised | `dd5da1d`, `392bb15` |
| QC | **391 SBML L2V4 errors resolved**; source-level fixes in 3 generator scripts | `68d4317` |
| 3 | SSc-specific curation layer + wire into integrated map (518 species / 242 reactions) | `d4107ab` |
| 4 | **Real Tabib 2021 scanpy pipeline** — 64 211 cells, 1 058 DEG; REAL per-donor module scores | `572892f` |
| 4 | Druggable hub prioritisation via DGIdb; F1/F2/F3 figures | earlier |
| 4b | **Multi-dataset overlay** — PBMC + lung ILD; F2_multi 3-panel heatmap | `4136481` |
| 4b | **HGNC alias fix** — 15 alias corrigés, 13 métabolites/isoformes vidés | `c5cb945` |
| 4c | **GSE195452 skin multiome** (Gur 2022) — 154 donors, 100 538 cells; coverage 50%; 58 overlays | `9a40565` |
| 5 | **IMRAD manuscript draft** (Frontiers/npj, ~5 500 words) | `2930648` |
| rev | **npj-SBA revision v1.1** — 23/25 E-items, MIM coverage → 81.3%, AUCell, drug recal, Docker | `1116a3e` |
| pdf | Compile manuscript to PDF with embedded figures | `29a5afc` |
| growth | Systematic lit worklist (77 papers) + OA/non-OA PDF mining → SSc reactions 85 → 133 | `536d36e` |
| review | Contradiction detector + tidy interaction database (CSV) + discarded/excluded enrichment | `f23706d` |
| review | Polarity-aware multi-source dedup + contradiction routing | `9e4dd65` |
| review | **Swipe-deck review app** — verbatim quotes + module map + lit dossier + AI verdicts | `2b09d18` |

## Inventory

| Artifact | Count | Notes |
|----------|-------|-------|
| `curation/celldesigner/SSc_MIM_integrated.xml` | **568 species / 308 reactions / 20 compartments** | CI-validated SBML L2V4 |
| `curation/ssc_curated_reactions.tsv` | **133 reactions** | SSc-specific layer (M2 58 / M3 27 / M4 21 / M1 19 / crosstalk 8) |
| `curation/annotations/species_annotations.tsv` | 526 rows, 198 HGNC symbols | 196/198 detectable by RNA-seq |
| `curation/pubmed_corpus.bib` | 361 BibTeX entries | 358 filled; 3 seed TODOs |
| `curation/ai_review_verdicts.json` | 133 verdicts | 101 validate / 28 revise / 4 caution |
| `curation/evidence_dossier.json` | 133 reactions | 403 support refs / 185 contrary refs (real PMIDs) |
| `analysis/curation/interaction_database.csv` | **143 interactions** | reviewer-ready snapshot embedded in the app |
| `analysis/overlay/` | cluster_deg_multi.tsv (4 338 entries), 197 donor scores | 4 datasets (skin Tabib+Gur / PBMC / lung), all REAL |
| `minerva/overlays/` | 58 cluster TSVs | ready for MINERVA import |
| `figures/` | F1 + F2 (AUCell heatmap v1.1) + F3 + F2_multi | SVG + 300 dpi PNG |
| `review/index.html` | 1 file (offline app) | swipe deck, no server/CDN needed |
| `manuscript/SSc_MIM_manuscript_draft.md` (+ PDF) | resource-paper draft | npj-SBA revision numbers |

## Delivery target

**Primary v1.0 delivery: GitHub repo + Zenodo DOI release.** MINERVA deployment is a post-publication
stretch goal — the map content is the deliverable, hosting is one rendering of it. Co-author is locked
(médecine interne, ARD-published on SSc).

## What's left

- ✅ 🟢 **Auto lanes COMPLETE**: integration, SBML QC, network analysis, real scRNA-seq overlay
  (4 datasets, MIM coverage 81.3%), HGNC annotations, DGIdb drug prioritisation, all figures,
  manuscript draft + v1.1 revision, growth batches (133 SSc reactions), review app + AI verdicts.
- 🟡 **In progress**: citation integrity sweep (28 `revise` PMIDs → verified replacements);
  manuscript polish.
- 🟡 **M5 split — propagation almost complete, 2 items remain** (M4 → M4 cytokines + M5 B-cell/
  autoreactivity, validated; see `analysis/overlay/M5_validation.md`):
  - **(a) Overlay re-run on the grown 5-module map** — the transcriptomic-overlay numbers in the
    manuscript §3.2/§4.4 (coverage grid 49.5/81.3%, per-module M1–M4 coverage, 26 Gur species, AUCell
    contrasts) are a **flagged v1.1 snapshot** computed on the 198-symbol annotation. Re-deriving them
    on the current 568/308/133 map + 5 modules needs the **raw scRNA-seq archives in `data/raw/`**
    (Zenodo input mirror, ~3 GB, gitignored). Once present: `make overlay-multi && make aucell`, then
    refresh manuscript §3.2/§4.4 and `coverage_v1.1.json`. **Blocker: raw data not in local tree.**
  - **(b) SBML XML re-annotation + F1 5-panel** — the integrated `SSc_MIM_integrated.xml` still tags
    the B-cell species `module=M4` in its CellDesigner notes (the split currently lives in
    `species_annotations.tsv` + `ssc_curated_reactions.tsv`, which drive AUCell). Re-tag the XML
    species notes to M5 and regenerate **F1** as a five-panel quadrant layout (`render_f1_quadrant.py`,
    currently 4-quadrant; caption already flags this). No raw data needed — scriptable.
- 🔴 **Human-only blockers (binding)**:
  1. **Expert/co-author manual review** of the 143 interactions via the swipe-deck app
     (presentation to expert biologists scheduled 2026-06-25).
  2. CellDesigner GUI wiring (visual round-trip; outstanding stubs).
  3. `.zenodo.json` co-author slot (2× REPLACE_ME).
  4. GitHub → Zenodo webhook toggle (one-time) + `git tag v1.0 && git push --tags`.

## How to verify the current state

```bash
git status                           # working tree clean
make lint                            # specs + bib linters pass
make validate                        # libSBML validation (needs python-libsbml; CI also runs this)
open review/index.html               # reviewer app (offline)
make review                          # rebuild interaction DB + app after curation changes
```
