# Journal — SSc-MIM

> Running log of all actions taken on the project. Newest entries at the bottom of each day.
> Conventions:
> - **Date** in `YYYY-MM-DD` (ISO 8601). One H2 per day.
> - Each entry: `### HH:MM — <short title>` followed by what was done, why, and (if relevant) what is blocked / what is next.
> - Cross-link the [[ROADMAP]] phase or milestone in each entry when applicable.
> - Commits are referenced by short SHA once they exist.

---

## 2026-05-15 — Phase 0 / Phase 1 kickoff

### 09:00 — Project bootstrap

Today is the official start date of the project per the ROADMAP (15 May 2026, week 1 of Phase 1). Phase 0 (pre-flight, week 0) had not been executed yet, so the first action is to do Phase 0 in compressed form before week 1 substantive work begins.

State of the repo at start:
- `README.md` and `ROADMAP.md` committed.
- No other files.
- Branch: `main`.

Plan for today:
1. Create `journal.md` (this file).
2. Scaffold the full directory layout described in `README.md` → "Repository layout".
3. Write the foundational repo files: `LICENSE`, `CITATION.cff`, `.gitignore`, `CONTRIBUTING.md`.
4. Add the two GitHub issue templates and the SBML validation workflow.
5. Seed all Phase 1 documentation stubs (`docs/scoping_notes.md`, `docs/curation_guidelines.md`, `docs/mi2cast_checklist.md`, `docs/risks.md`, `docs/import_pilot.md`, and the four `docs/module_specs/M*.md`).
6. Seed empty annotation tables and the BibTeX corpus placeholder.
7. Stop before committing — ask the user before the first commit.

Tracked as tasks #1–#11 in the in-conversation task list.

Not in scope for this session (require external systems or human input):
- Installing CellDesigner, MINERVA, CaSQ, Cytoscape (local GUI tooling).
- Requesting the MINERVA curator role on the Luxembourg instance.
- The kickoff meeting with the SSc rheumatologist (Phase 1 / week 1).
- Reactome pilot import (needs the MINERVA conversion API + CellDesigner).
- Bibliography sprint (needs PubMed access from a user-side environment).

These will be marked as open items in the relevant `docs/` files so they are not forgotten.

### 10:30 — Repo skeleton created

Created the full directory layout described in `README.md` § "Repository layout":

```
docs/, docs/module_specs/, docs/decisions/, docs/standups/
curation/celldesigner/, curation/imports/{M1,M2,M3,M4}/, curation/annotations/
analysis/{network,boolean}/, analysis/overlay/{tabib_scRNAseq,whitfield_bulk}/
minerva/overlays/, figures/, manuscript/submission_confirmation/
.github/{ISSUE_TEMPLATE,workflows}/, scripts/
```

`.gitkeep` placeholders added to empty subdirectories so they are tracked.

Noted on the way: a pre-existing `.venv/` Python virtualenv (Python 3.12) sits at the repo root. Covered by the rewritten `.gitignore`.

### 11:00 — Foundation files written

- `LICENSE` — dual licence (CC-BY 4.0 for map content + MIT for code), with explicit per-path scoping in the preamble.
- `CITATION.cff` (CFF 1.2.0) — placeholder author / repository URL fields (marked `REPLACE_ME` for the lead curator to fill in week 1).
- `.gitignore` rewritten from the single-line stub to a comprehensive list: OS junk, IDE files, Python (`.venv/`, `__pycache__`, notebooks checkpoints), R, CellDesigner backups, large data formats (`*.h5ad`, `*.mtx`, `GSE*/`, FASTQ/BAM), MINERVA cache, LaTeX intermediates, secrets.
- `CONTRIBUTING.md` — curation-request workflow, expert-review workflow, PR rules (MI2CAST annotations required, CI gate), coding style, co-authorship policy (CRediT/ICMJE-inspired thresholds).

### 11:30 — GitHub templates and CI

- `.github/ISSUE_TEMPLATE/curation_request.md` — structured form: PMID, claim (A → B, sign, mechanism), evidence excerpt, MI2CAST pre-fill.
- `.github/ISSUE_TEMPLATE/expert_review.md` — scope selector, comment classification (must-fix / nice-to-have / discussion), declarations of interest.
- `.github/workflows/validate_sbml.yml` — GitHub Actions workflow that installs `python-libsbml==5.20.4` and runs the validator on every push touching `curation/celldesigner/**.xml`.
- `scripts/validate_sbml.py` — libSBML-based validator. Walks an input directory, skips empty placeholders, reports info / warning / error / fatal levels, exits non-zero on error or fatal.

Smoke-tested the validator locally: it correctly exits 2 (libsbml not installed) on the host machine; CI installs the dep, so this is fine. Marked `[ok] no XML files yet` as the expected initial CI run output.

### 12:15 — Phase 1 documentation scaffolded

All Phase 1 docs created with real seeded content (not just headers):

- `docs/scoping_notes.md` — disease + periphery + four modules + four sink phenotypes + SSc-specific entity priorities + volumetric target + decisions log + open items.
- `docs/curation_guidelines.md` — adapted from Mazein 2023: tooling, naming, fixed compartment vocabulary, SBGN-PD glyph mapping, state-variable conventions, reaction granularity rules, crosstalk handling, annotation contract, common pitfalls, versioning.
- `docs/mi2cast_checklist.md` — MI2CAST fields with mapping to TSV columns, ECO code cheat-sheet (314 / 353 / 270 / 315 / 305 / etc.), context vocabularies for SSc, a minimal worked example.
- `docs/risks.md` — eight risks (six from the README table + two additions: reproducibility regression R6 and MINERVA tooling drift R8). Each with trigger / mitigation / owner.
- `docs/import_pilot.md` — Reactome → CellDesigner pilot procedure on `R-HSA-2173789` (TGF-β receptor signalling activates SMADs), pre-flight, expected outcomes, decision template.

Four module specs created with **Tier-1 entity tables**, sink-node mapping, druggable handles, crosstalk edges in/out, Tier-2/3 candidates, and open expert-review questions:

- `docs/module_specs/M1_IFN_I.md` — IFNAR/JAK/STAT/ISG, cGAS-STING / RIG-I / TLR sensing, CXCL4/PF4 hook.
- `docs/module_specs/M2_TGFb_fibrosis.md` — TGF-β latent activation, canonical SMADs, non-canonical (MAPK, PI3K, RhoA, YAP/TAZ), myofibroblast markers, ECM, matricellular (POSTN/COMP/CTGF/TNC), FRA-2/TBX2.
- `docs/module_specs/M3_EndoMT_vasculopathy.md` — endothelin axis, NO/sGC/cGMP, HIF1A, Notch, SNAI/ZEB, EC → mesenchymal markers, perivascular fibroblast.
- `docs/module_specs/M4_IL6_Th2_Bcell.md` — IL-6/JAK/STAT3, IL-4/IL-13/STAT6, BCR/CD20, plasma cell (BLIMP1/XBP1/IRF4), autoAb output, BAFF/APRIL.

### 12:50 — Annotation tables and bib seeded

- `curation/annotations/species_annotations.tsv` — header only (columns: `species_id, hgnc_symbol, uniprot, ensembl, chebi, compartment, module, taxonomy, notes`).
- `curation/annotations/reaction_evidence.tsv` — header only (columns: `reaction_id, type, participants, mechanism, pmid, evidence_code, context_biotype, context_assay, module, crosstalk_modules, notes`). Columns match the MI2CAST checklist.
- `curation/pubmed_corpus.bib` — seeded with the methodology references (Mazein 2018, Mazein 2023, Aghakhani 2020 / CaSQ) + RA-map (Singh 2020) + two SSc seed entries (Tabib 2021, Van Bon 2014 / CXCL4). Entries with unverified PMIDs are tagged `pmid = {TODO}` for week 2 cleanup.

### 13:00 — Misc reproducibility scaffold

- `environment.yml` — conda env `sscmim`: Python 3.11, NumPy / pandas / scipy / scikit-learn, NetworkX, AnnData / scanpy / leidenalg / igraph / UMAP, `python-libsbml==5.20.4`, JupyterLab, plus pip-installed `casq` and `pybiopax`.
- `minerva/deployment_notes.md` — pre-flight + 10-step deployment checklist with the four-module colour palette (Set1/Set2 colour-blind-friendly: M1 blue, M2 red, M3 green, M4 orange, crosstalk grey), Zenodo mirror plan, known gotchas (dedupe before upload, palette accessibility).

### 13:10 — Phase 0 complete; next step is the first commit

Phase 0 of the ROADMAP (week 0 — pre-flight, repo bootstrap) is now functionally complete:

- ✅ Repo skeleton + LICENSE + CITATION.cff + .gitignore + CONTRIBUTING.md
- ✅ Issue templates + SBML validation workflow + validator script
- ✅ All Phase 1 documentation seeded (not just placeholders — Tier-1 entity tables, MI2CAST checklist, risks, import pilot procedure)
- ✅ Annotation tables and BibTeX corpus initialised
- ✅ MINERVA deployment plan + conda env definition

**Still pending (Phase 0 items requiring user / external action):**

- ⏸ Installing CellDesigner / MINERVA / Cytoscape locally — requires GUI environment.
- ⏸ Requesting MINERVA Luxembourg curator role.
- ⏸ Kickoff meeting + co-authorship lock-in with SSc rheumatologist.
- ⏸ Bibliography sprint to add ~50 reviews + ~100 primary papers — needs a PubMed-facing environment and biology calls.
- ⏸ Reactome pilot import — needs CellDesigner + MINERVA conversion API.

**Asking the user before committing.** Phase 0 produces ~17 new files; the first commit is meaningful but it is a discrete checkpoint that I will not push without confirmation.

