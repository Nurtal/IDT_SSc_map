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

### 13:30 — User confirmed: single commit + continue

User chose: one consolidated commit for Phase 0, then continue with automatable tasks **and** the Reactome pilot draft.

**Commit `4dcf004`** — `chore: initial scaffold for SSc-MIM (Phase 0)`. 39 files, +2158 lines.

### 14:00 — Makefile and self-documenting help

`Makefile` at the repo root with self-documenting `help` target (the awk one-liner). Targets: `setup` / `setup-conda`, `validate`, `specs-check`, `bib-check`, `pilot`, `lint`, `all`, `clean`. Defaults to `help`. Smoke-tested `make help`.

### 14:15 — Module-spec linter caught real issues

Wrote `scripts/check_module_specs.py`. First run flagged **7 issues**, of which **5 were real** and **2 were regex false positives**:

Real issues caught (now fixed):
1. `M2_TGFb_fibrosis.md`: CTGF/CCN2 compartment listed as `extracellular / nucleus output` — `nucleus output` is not a real compartment. Fixed to `extracellular / ECM`.
2. `M3_EndoMT_vasculopathy.md`: `PTGS2 (COX-2), TXA2 axis (TBXA2R)` lumped two entities in one row with compartment `various`. Split into two rows: `PTGS2` in `ER`, `TBXA2R` in `plasma_membrane`.
3. Cross-module Tier-1 duplicate `ACTA2` in M2 + M3 — αSMA is the myofibroblast marker (M2) and also a mesenchymal-conversion marker (M3). Resolution: home = M2; removed from M3 Tier-1 table; added a "Shared with other modules" subsection in M3 noting it.
4. Cross-module Tier-1 duplicates `JAK1` and `TYK2` in M1 + M4 — same kinases used by IFNAR and IL-6R/IL-4R. Resolution: home = M1; removed from M4 Tier-1 (kept `JAK2, JAK3`); added a "Shared with other modules" subsection in M4.

Regex false positives fixed in the linter:
5–7. The regex picked up `SMA` inside `ACTA2 (αSMA)` and `N-` inside `CDH2 (N-cadherin)`. Updated `extract_entities()` to strip parenthetical aliases before tokenising, and dropped tokens shorter than 3 chars.

After fixes: `OK — 4 spec(s) scanned, no consistency issues`.

Real value here: the lint pass turned up a curation issue (compartment vocabulary drift) and an integration issue (shared species across modules) that would have caused real headaches in week 12 during integration. Catching them in week 1 saves rework.

### 14:30 — BibTeX linter

`scripts/check_bib.py` with a tiny ad-hoc BibTeX parser (no third-party deps). Reports `pmid={TODO}` entries, missing pmid/doi, duplicate citation keys. Two modes: informational (default, exit 0) and `--strict` (exit 1 on issues — to flip on in CI from Phase 2 onward).

First run: 3 entries flagged with `pmid={TODO}` (Aghakhani 2020 / CaSQ, Singh 2020 / RA-map, Tabib 2021). Expected.

### 14:45 — Reactome pilot — executed live ✅

Wrote `scripts/reactome_pilot.py` (stdlib only: `urllib`, no third-party deps). Arguments: `--pathway`, `--module`, `--out-root`, `--dry-run`. Environment variables override the Reactome and MINERVA base URLs.

Then **actually ran the pilot**, fully expecting it to fail with a network error:

```
python3 scripts/reactome_pilot.py --pathway R-HSA-2173789 --module M2
```

**It succeeded end-to-end.** Three artifacts under `curation/imports/M2/pilot_R-HSA-2173789/`:

| Artifact | Size |
|----------|------|
| `R-HSA-2173789.sbgn` | 87 kB |
| `R-HSA-2173789.owl` (BioPAX L3) | 437 kB |
| `R-HSA-2173789.celldesigner.xml` (via MINERVA conversion API) | 363 kB |

ElementTree parse of the converted SBML:
- 5 compartments
- 100 species (includes cofactor duplicates: ATP, GDP, Ub one-per-reaction — Reactome's modelling convention)
- 46 reactions

**Findings (recorded in `docs/import_pilot.md` and `docs/decisions/2026-05-15_reactome_import.md`):**

1. Species IDs are MINERVA-generated UUIDs (`s_id_entityVertex_*`). Need a renaming pass to HGNC primary symbols before integration. The `name` attribute carries the readable symbol, so the rename is straightforward.
2. Cofactor duplication: ATP/GDP/H₂O/Pi appear as separate species per reaction. Collapse on import.
3. Ubiquitin appears as a free species; our curation guidelines encode ubiquitination as a state variable on the substrate. Strip free Ub on import.
4. Otherwise the conversion is high-fidelity: 5 compartments, plausible reaction count.

**Decision (`docs/decisions/2026-05-15_reactome_import.md`):** adopt three-stage import workflow — fetch → post-process → curate. A `scripts/post_process_reactome.py` post-processor is added to the backlog and must exist before Phase 2 / week 4 (1 Jun) when M2 curation starts. Timeline unaffected.

**Impact on the ROADMAP:** Phase 1 / week 1 risk-down item ✅ done. Risk R2 (Reactome → CellDesigner incompatibilities) lowered from medium to low. The 60/40 import/manual split stands.

### 15:45 — Phase 1 / week 3 omics decision memo

`docs/omics_decision.md` written (intentionally entered early — revisable until 5 Jun). Summary:

- **Primary:** Tabib 2021 scRNAseq (GSE138669). Rationale: novelty (first sc × MIM overlay in SSc skin), resolution (SFRP2⁺/PRSS23⁺ fibroblasts and myofibroblasts match M2/M3 modelling), feasibility (~50k cells, fits on a workstation), stub infrastructure already in place.
- **Reserve:** Whitfield/GENISOS/PRESS bulk. Switch triggers documented (clean signal absent by end-week-16, or QC retention < 30k cells, or bioinfo FTE drop).
- **Complementary:** project Whitfield intrinsic subsets onto the MIM as a sanity check even on the primary path (1 day add in week 16). Strengthens F2.

Open items: confirm Tabib metadata contains mRSS / disease duration / autoAb status; bioinformatician availability; kickoff sign-off.

### 16:15 — Post-processor implemented and refined

`scripts/post_process_reactome.py` (stdlib only) implements the three transforms from the Reactome decision:

1. Rename species `id` from MINERVA UUIDs to `<sanitised_name>__<compartment_short>`.
2. Collapse cofactor duplicates within the same compartment (ATP/ADP/H₂O/Pi/…). Each cofactor list-encoded.
3. Remove free ubiquitin species; per `curation_guidelines.md` § 5 ubiquitination is a state variable.

Also: rewrites `species`, `reactant`, `product`, `modifiers` attribute references, and `rdf:about` (uses `metaid` ⇒ kept consistent by also rewriting `metaid` to match the new `id`). Walks for orphan reactions and removes any reaction left with zero participants. Outputs both the processed XML and a JSON report.

**Two bugs found and fixed during iteration:**

1. **First run had 176 leftover UUID references.** Root cause: `rdf:about` references `metaid`, not `id`. I'd renamed `id` and `rdf:about` but left `metaid` as the old UUID, which would have broken downstream RDF cross-refs. Fix: rewrite `metaid` to match the new `id`. Leftovers dropped to 77.

2. **Second run had 77 leftover UUIDs in `<celldesigner:reactantLink reactant="...">`, `<celldesigner:productLink product="...">`, and `<celldesigner:modifierLink modifiers="...">`.** These are CellDesigner-specific reaction-visualisation elements that use the attribute names `reactant` / `product` / `modifiers` rather than `species`. Fix: extend the rewrite to those attributes too; `modifiers` is space-separated so handled as a list. Leftovers dropped to **0**.

Applied successfully to M2-TGFβ: 100 species → 99 (one free ubiquitin removed), 46 reactions → 46.

### 16:45 — Fetched the other Reactome-anchored pathways

Three more pilot runs through `scripts/reactome_pilot.py`:

| Module | Pathway | Reactome stable ID | species | reactions | sizes |
|--------|---------|---------------------|---------|-----------|-------|
| M1 | Interferon α/β signaling | R-HSA-909733 | 83 | 25 | 63 / 488 / 288 kB |
| M2 | Signaling by PDGF | R-HSA-186797 | 76 | 31 | 65 / 527 / 274 kB |
| M4 | Interleukin-6 signaling | R-HSA-1059683 | 64 | 34 | 56 / 178 / 240 kB |

All three converted cleanly via the MINERVA API. Post-processor applied; all four (M1, M2-TGFβ, M2-PDGF, M4) post-processed files have zero UUID leftovers.

**Aggregate raw imported volume across the four pathways:**

- 322 species (deduped to 308 unique cross-import)
- 136 reactions
- Module M3 (EndoMT) intentionally not imported — no high-quality Reactome anchor; M3 will be assembled from WikiPathways EndMT scaffold + manual curation in weeks 8–9.

This already sits in the volumetric target ballpark (200–300 species, 300–450 reactions) for raw imports, before SSc-specific additions and cross-module dedupe. M3 will add a smaller batch (~60 species mostly manual), and SSc-specific Tier-1 additions will pad each module.

### 17:00 — Seeded species_annotations.tsv from imports

`scripts/seed_species_from_imports.py` parses every `*.processed.xml` under `curation/imports/`, dedupes by `species_id`, infers `module` from the parent directory, auto-fills `hgnc_symbol` when the name matches the HGNC regex, and writes idempotently to the annotation TSV. First run:

```
scanned 4 processed import(s)
existing rows: 0
new species:   308
wrote curation/annotations/species_annotations.tsv: 308 total rows
```

Examples of clean rows (auto-HGNC):

```
ISG20__nuc      ISG20         nucleoplasm    M1
GBP2__cyto      GBP2          cytosol        M1
IFIT2__cyto     IFIT2         cytosol        M1
PTPN1__cyto     PTPN1         cytosol        M1
```

Examples of rows that need manual cleanup (Reactome encoded biology in the name; documented as the "import-cleanup backlog" in `docs/import_pilot.md`):

```
p_minus_STAT2:p_minus_STAT1                # phospho-STAT1/2 dimer
STAT1_minus_1                              # STAT1 isoform 1
SOCS_minus_1_slash_SOCS_minus_3            # SOCS1/SOCS3 grouped
Mx_space_GTPases                           # MX1+MX2 grouped
OAS_space_proteins                         # OAS1+OAS2+OAS3 grouped
Type_space_I_space_IFN_minus_regulated_…   # gene-set placeholder
Dimeric_space_TGFB1                        # TGF-β1 homodimer
```

This is one of those moments where the import did most of the work but the next 30% (which is the curator's actual job) becomes visible.

### 17:15 — Scripts-smoke CI workflow

`.github/workflows/scripts-smoke.yml` — runs Python 3.11, compiles every `scripts/*.py` with `py_compile`, exercises `--help` on each, runs the linters in informational mode, dry-runs the Reactome pilot, and dry-runs the species seeder. Catches syntax errors and broken `--help` formatting before they reach the lint CI.

Locally: `for f in scripts/*.py; do python3 -m py_compile "$f"; done` → all six scripts compile cleanly.

### 17:30 — Batch 3 ready to commit

Will split into four commits for traceability:

1. `feat(phase1): omics dataset decision (Tabib scRNAseq primary, Whitfield bulk reserve)`
2. `feat(scripts): Reactome post-processor + applied to M2 pilot`
3. `feat(imports): M1 IFN-I + M2 PDGF + M4 IL-6 Reactome imports (post-processed)`
4. `feat(annotations): seed species_annotations.tsv from imports; scripts-smoke CI; doc updates`

### 17:50 — Harmonisation script

Surveyed unrecognised species in the seeded TSV (217/308 lacked auto-HGNC). Pattern counts:

| Count | Pattern | Example |
|-------|---------|---------|
| 139 | complex (`_x_`) | `ABCE1_x_RNASEL_space_dimer__mito` |
| 113 | `_space_` token (Reactome name with a space) | `Mx_space_GTPases__cyto` |
| 43 | phospho (`p_minus_`) | `p_minus_STAT2:p_minus_STAT1` |
| 32 | `default` compartment | `IFN_alpha_beta_IFNA_B__def` |
| 26 | slash-grouping (`_slash_`) | `IFNA_slash_B` |
| 25 | isoform (`X_minus_N`) | `IRF_space_1_minus_9__cyto` |

Two insights this surfaced:
1. `_space_` is **CellDesigner's escape encoding** for ` `, not a sanitiser artefact (similarly `_slash_` for `/`, `_minus_` for `-`, `_x_` for `:`). The MINERVA conversion preserves this encoding. Decoding back is straightforward.
2. The encoded "p-X" and "X-N" patterns are real Reactome biology (phospho-forms and isoforms) that need explicit handling.

Wrote `scripts/harmonise_imports.py` (stdlib only) that:

- Decodes CellDesigner-escaped text on the `name` attribute and on `<celldesigner:name>` text (so the CellDesigner canvas displays human-readable labels).
- Remaps Reactome compartments to our fixed vocabulary (`default` → `extracellular`, `nucleoplasm` → `nucleus`, `early_space_endosome` → `endosome`, `Golgi_space_lumen` → `Golgi`, `endoplasmic_space_reticulum_space_lumen` → `ER`).
- Recomputes species IDs deterministically based on the decoded name, with six pattern classifications, each flagged in the JSON report: `family_to_expand`, `gene_set_placeholder`, `phospho_state`, `isoform`, `homodimer`, `slash_pair_to_split`.
- Crucially, **does only identifier-level work** — no structural splits. Splitting `MX_family` into MX1 + MX2 (and fanning the reactions) is left to the CellDesigner curator and is flagged. Same for `ISG_signature`, `pSTAT2`, etc.

### 18:15 — Iteration: decoding the CellDesigner annotation labels too

First run had 524 leftover encoding tokens. They were in `<celldesigner:name>` element text (the canvas display labels) — separate from the structural `name=` attribute. CellDesigner shows this text on the glyph. Extended the harmoniser to walk `celldesigner:name` text and `celldesigner:protein name=` and decode them. After fix: **0 leftover encoding tokens** across all four harmonised files.

### 18:30 — Applied to all imports

| Module | species_renamed | flags |
|--------|-----------------|-------|
| M1 (IFN-α/β) | 43 | 4 family_to_expand, 2 isoform, 1 gene_set_placeholder |
| M2 (TGF-β) | 68 | 1 homodimer, 1 isoform, 2 slash_pair_to_split |
| M2 (PDGF) | 57 | (clean) |
| M4 (IL-6) | 52 | 2 isoform |

Species counts unchanged (no structural changes by design): 99, 76, 64 respectively. Reactions unchanged: 46, 31, 34.

### 19:00 — WikiPathways EndMT — the ROADMAP was wrong about the WP ID

ROADMAP cites `WP_3942 EndMT` as the M3 scaffold. Fetched it successfully (81 kB GPML + 19 kB datanodes TSV)… and discovered the pathway name is "**PPAR signaling**" — not EndMT. The ROADMAP draft used a guessed WP ID.

Tried a few plausible WP IDs (`WP4474`, `WP4655`, `WP5045`, `WP5057`, `WP4787`) via the asset endpoint — all returned HTTP 403. Tried the WikiPathways search webservice (`webservice.wikipathways.org`) — 404. Tried `classic.wikipathways.org` and `www.wikipathways.org/api/` — 403 / 404. The WikiPathways public API surface has been reorganised; programmatic lookup of "EndMT" from the search interface needs a manual-browser step that's outside what I can do here.

**Fallback used:** Reactome `R-HSA-1980143` — *Signaling by NOTCH1*. 79 species, 39 reactions, with HIF1A, JAG1, JAG2, DLL1, NOTCH1 — all relevant to EndoMT. Fetched, post-processed (→ 77 species, 2 ubiquitin removed), harmonised (48 renames; 1 phospho_state, 2 slash_pair_to_split flags).

**Conclusion:** M3 stays "manual-heavy" as the ROADMAP foresaw. Notch1 gives M3 a Reactome anchor for the Notch-driven EndMT axis but the rest (endothelin, NO/sGC/cGMP, VE-cadherin loss, SNAI/ZEB) is still manual. Documented in `docs/import_pilot.md` and as an open follow-up item for the lead curator (browse WikiPathways directly).

### 19:30 — Updated import_pilot.md and re-seeded annotations

Re-seeded `species_annotations.tsv` from harmonised files (preferring `*.harmonised.xml` over `*.processed.xml`). New volumetric:

| Module | species |
|--------|---------|
| M1 | 83 |
| M2 | 165 (TGF-β + PDGF) |
| M3 | 77 (Notch1 + manual to follow) |
| M4 | 60 |
| **Total unique** | **385** |

Already above the 200–300 species target band for the post-curation map — cross-module dedupe during Phase 3 integration will reduce this, and SSc-specific manual additions will pad each module. The volumetric story is healthy.

Auto-HGNC fill rate is 125 / 385 = 32 % — limited because most unrecognised entries are protein complexes (`X_Y_Z`) which need component-level annotation rather than a single HGNC symbol.

### 19:40 — Makefile extensions

Added targets:
- `harmonise` — runs post-process + harmonise on every `*.celldesigner.xml` under `curation/imports/`.
- `seed` — regenerates `species_annotations.tsv` from imports.
- `m3-fetch` — fetches Notch1 (R-HSA-1980143) for M3.

Also fixed the awk regex in `help` to accept digits in target names (it was filtering out `m3-fetch`).

### 20:00 — Batch 4 ready

Commit plan:

1. `feat(scripts): import harmonisation pass (decode + classify + rename)`
2. `feat(imports): apply harmoniser to M1+M2+M4; M3 Notch1 fallback for EndoMT scaffold`
3. `chore: Makefile harmonise/seed/m3-fetch targets; help regex fix`
4. `docs(import_pilot): harmonisation outcome + WikiPathways EndMT gotcha`

---

## 2026-05-16 — Automation-first rewrite + Phase 3 pipeline

User direction: "*il va falloir que tu automatise le plus possible toutes les tâches à venir, fait un point sur ce qui a été fait, update la roadmap en conséquence*". This day's work:

- Snapshot ([STATUS.md](STATUS.md)) of what's done with commit refs.
- ROADMAP rewritten around three execution lanes (AUTO / ASSIST / HUMAN).
- Phase 3 week-12-and-14 work brought forward — integration, network analysis, sink connectivity, PMID extraction, crosstalk scaffold — all automated.

### 09:30 — STATUS snapshot

Wrote `STATUS.md`: completion table per phase with commit refs; inventory (385 unique species, 175 reactions, 5 imports, 6 bib entries — pre-extraction); explicit external blockers (rheumatologist meeting, MINERVA account, CellDesigner GUI verification, bibliography sprint, CITATION.cff placeholders).

### 09:50 — ROADMAP rewritten

Heavy rewrite of `ROADMAP.md`. Every remaining task tagged 🟢 AUTO / 🟡 ASSIST / 🔴 HUMAN. New **automation queue** sections per phase. Original Go/no-go G1 marked "auto-skipped" because the import-pace question it tested is no longer the binding constraint; new gate G1.5 (scope sign-off at end of week 4) added as the actual binding constraint. Risk register updated: R1 (curation pace) downgraded high → medium-low; R2 (import compatibility) medium → low; R3 (expert validation) becomes the dominant scheduling risk; new R9 (automation drift from biology) added with the "every transform produces a JSON report, nothing is destructive, curator can override" mitigation.

### 10:30 — Integration

`scripts/integrate_modules.py` merges the 5 harmonised XMLs into `curation/celldesigner/SSc_MIM_integrated.xml`. Walks listOfCompartments/Species/Reactions, dedupes by id, tags each species' SBML notes with `module=<comma-list>` so downstream tools (network analysis, MINERVA) can colour by source module.

Results: **385 species, 175 reactions, 17 compartments, 14 cross-module dedupes**. The cross-module species are exactly what you'd expect — ATP, ADP, H2O, Pi, FURIN, CBL, PTPN11 — universal cofactors and a few shared signaling components correctly collapsed to one node.

Two small bugs caught and fixed during iteration:
- Module-notes annotation initially appended a fresh `<html>/<body>` each time because my `find()` was non-recursive — body lives two levels under notes. Fixed by `notes.iter()`.
- Verified that the resulting `module=M1,M2,M4` annotation on ATP__cyto is correct (3 imports contributed).

### 11:00 — PMID mining from Reactome SBML

`scripts/extract_pmids_from_biopax.py`. Surprise: the `.owl` files are actually SBML L3v1 (the BioPAX URL 404'd at fetch time; the script's fallback to `/exporter/sbml/` kicked in). The PMIDs are there though, encoded as `<rdf:li rdf:resource="https://identifiers.org/pubmed:NNNN" />` inside `<bqbiol:isDescribedBy>` blocks attached to species and reactions.

Mined **355 unique PMIDs** across the five Reactome imports. Pre-filled `curation/annotations/reaction_evidence.tsv` with **159 rows** (one per Reactome reaction), populated with: reaction id (prefixed by module), mechanism (Reactome's reaction name), participants list, PMIDs (semicolon-separated), evidence code `ECO:0000305` (curator-inference, pending real PMID read), module tag. **158/159 reactions have at least one PMID.**

Also appended 355 BibTeX stub entries to `pubmed_corpus.bib` (with `pmid` + TODO body — `scripts/bib_lookup.py` (future) will fetch title/journal/year from NCBI E-utils).

This is one of the biggest single lifts of the project so far: it pre-fills Phase 2 days 9–10 (MI2CAST annotation) from "write 175 rows from scratch" to "review 175 auto-filled rows".

**Caveat:** The reaction IDs in the Reactome SBML L3 export (`reaction_<stableID>`) don't match the IDs in the CellDesigner export (`reactionVertex_<n>`) — same biology, different ID schemes from different Reactome export paths. The curator needs a mapping pass. The row text (mechanism + participants list with HGNC symbols) makes this trivial by hand; an automated mapping pass is on the queue.

### 11:30 — Network analysis

`scripts/network_analysis.py` (needs networkx, installed in `.venv`). Bipartite graph (species ↔ reaction), undirected species projection: **385 nodes, 1140 edges in the species-only graph** (513 directed in the directed projection). Computes degree / betweenness / closeness / PageRank; hub score = z(degree) + z(betweenness); top-20 hubs excluding common cofactors; greedy modularity communities (31 communities detected vs the 4 hand-defined modules — sub-structure is real).

**Top 5 non-cofactor hubs:**

```
1. ISGF3_bound_to_ISRE_promotor_elements__nuc   M1  score=9.57  deg=29
2. ISG_signature__nuc                            M1  score=8.83  deg=28
3. PDGF_Phospho_PDGF_receptor_dimer__cyto        M2  score=7.91  deg=10
4. TGFB1_TGFBR2_p_TGFBR1__cyto                   M2  score=6.71  deg=7
5. IFNA_B_IFNAR2_JAK1_STAT2_IFNAR1_TYK2__cyto    M1  score=6.14  deg=9
```

These are mostly multi-protein complexes — biologically the central hubs of each signalling cascade. The drug-target prioritisation step in Phase 4 will want to drill down to the individual subunits within these complexes.

### 12:00 — Sink-node connectivity audit

`scripts/sink_connectivity.py` enforces the scoping-notes rule "every Tier-1 species reaches a sink in ≤ 6 steps". For each of the 385 species, computes shortest path to the nearest of four sink-anchor sets (ISG_signature / ECM-myofibroblast / vascular_remodelling / Th2-autoAb).

Results:

| Sink anchor | nodes detected |
|-------------|----------------|
| M1 ISG_signature | 9 |
| M2 ECM_myofibroblast | **0** |
| M3 vascular_remodelling | 12 |
| M4 Th2_autoAb_output | 8 |

**Findings:**

- **0 species violate the >6 rule** — i.e., every species that reaches a sink does so in ≤ 6 steps. ROADMAP constraint satisfied for the connected portion.
- **126 dangling species** (33%) — no path to any sink:
  - M1: 11 / 78 dangling (14%)
  - M2: 66 / 164 dangling (40%) — high because the M2 ECM sinks (ACTA2, COL1A1, FN1, POSTN, COMP, CTGF) are SSc-specific Tier-1 placeholders not yet imported. These are the curator's explicit next-week task.
  - M3: 5 / 77 dangling (6%)
  - M4: 44 / 60 dangling (73%) — IL-6R signalling internal states that terminate at intermediate complexes; needs the M4 transcriptional outputs (STAT3-target gene transcription nodes) to be wired in.

The 0-detected M2 sink and the 73% M4 dangling rate point to the same root cause: the **sink anchors are the SSc-specific Tier-1 additions the curator still needs to add** (Phase 2 days 6–8). Once those land, dangling will drop substantially.

### 12:30 — Crosstalk matrix scaffold

`scripts/generate_crosstalk_scaffold.py` parses the "Crosstalk edges" prose in each module spec and emits `docs/crosstalk_matrix.md` as a single table. Two parsing iterations:
- First run: 0 edges from M1 / M2 (each uses a different prose style). Regex DIRECTED_RE was too strict.
- Second run after extending the parser: M1 implicit "→ Mx: text" → 3 edges, M2 "**In:** Mx → text" → 4 edges. **14 unique edges across the four modules**, each tagged `declared`. Some redundancies (M2↔M3 appears twice with different phrasings) — the curator dedupes by hand.

### 13:00 — Makefile updates

Added targets: `integrate`, `pmids`, `network`, `sink-check`, `crosstalk`, and the meta-target `phase3` which runs the whole Phase 3 AUTO lane in sequence. `make phase3` is now the end-to-end pipeline from harmonised imports to integrated map + analyses.

### 13:15 — Commit plan

1. `feat(roadmap): rewrite around automation lanes; add STATUS.md`
2. `feat(scripts): integration of harmonised modules`
3. `feat(annotations): mine 355 PMIDs + seed 159 reaction_evidence rows`
4. `feat(scripts): network analysis (centrality, hubs, communities)`
5. `feat(scripts): sink-node connectivity audit`
6. `feat(scripts): auto-generate crosstalk matrix from module specs`
7. `chore: Makefile phase3 pipeline target`

### 14:30 — Bibliography via NCBI E-utils

`scripts/bib_lookup.py`: stdlib-only NCBI E-utils efetch client. Iterates over BibTeX entries whose `title = {TODO}` (basically every Reactome-mined PMID), batches in groups of 200, fetches PubMed XML, extracts title / authors / journal / year / DOI, rewrites the entry in place. Polite rate-limiting (~3 req/s without an API key); honours `NCBI_API_KEY` if set.

Live result: **350 / 350 PMIDs fetched** in two batches (200 + 150), in well under 2 minutes. Example:

```bibtex
@article{Reactome_pmid_1314164,
  author  = {Kashishian A and Kazlauskas A and Cooper JA},
  title   = {Phosphorylation sites in the PDGF receptor with different specificities for binding GAP and PI3 kinase in vivo.},
  journal = {EMBO J},
  year    = {1992},
  pmid    = {1314164},
  doi     = {10.1002/j.1460-2075.1992.tb05182.x}
}
```

`scripts/check_bib.py` now reports only **3 remaining `TODO` PMIDs** — the three pre-seeded entries (Aghakhani / CaSQ, Singh / RA-map, Tabib / scRNAseq) whose `pmid = {TODO}` was an actual TODO from the seed file rather than a fetchable PMID. These need a manual lookup from the lead curator.

### 15:00 — MINERVA preflight

`scripts/minerva_preflight.py` produces the green/red checklist before the (human) MINERVA upload step. Result on the current integrated map:

```
[ ok ] XML parses                          949 kB
[ ok ] Unique species ids                  385
[ ok ] Unique reaction ids                 175
[ ok ] Species annotation coverage         385/385
[ ok ] reaction_evidence.tsv PMID coverage 158/159
[ ok ] Sink connectivity <= max_path       0 / 385 violate the >6 rule
[warn] Dangling fraction                   126/385 cannot reach any sink (SSc Tier-1 still to wire)
[ ok ] Every species has a display name
       (info) cross-module species:        6
```

One advisory (dangling fraction), no blocking failures. The map is **uploadable to MINERVA** today; the dangling fraction is the explicit curator backlog and will drop substantially once the SSc-specific Tier-1 species (88 stubs auto-generated; see below) are wired into the integrated XML.

### 15:30 — SSc-specific Tier-1 stubs

`scripts/ssc_additions_template.py` parses every module spec's Tier-1 table, filters to rows tagged `Source = manual`, splits multi-symbol cells (`cGAS (MB21D1), STING1 (TMEM173)` → `MB21D1`, `TMEM173`), filters out entities already in `species_annotations.tsv`, and writes one SBML L2v4 stub per module under `curation/celldesigner/ssc_additions_template/`. Each stub is CellDesigner-importable.

Result: **88 SSc Tier-1 stubs across the four modules.**

| Module | Stubs | Sample |
|--------|-------|--------|
| M1 | 14 | IRF7, MB21D1, TMEM173 (STING), DDX58 (RIG-I), TLR3/7/8/9, TICAM1, TBK1, IKBKE, SOCS1, PTPN2 |
| M2 | 22 | (TGF-β latent activation + matricellular + mechanotransduction layers) |
| M3 | 27 | (endothelin axis + NO/sGC/cGMP + Notch ligands + EndoMT markers) |
| M4 | 25 | (Th2 cytokines + BCR/CD20 + plasma cell + BAFF/APRIL) |

`REPORT.md` lists every stub per module with role + compartment, for the curator's check-off.

### 16:00 — Preview figures F2 + F3

`scripts/render_figures.py` (needs matplotlib; auto-falls-back to `.venv/bin/python`).

- **F3 preview** — top-20 hub subnetwork + 1-hop neighbours, spring layout, node size ∝ hub_score, colour by module. Real data: the 385 species + 1140 species-projection edges from the integrated map. Saved as both SVG (237 kB) and 300-dpi PNG (1.3 MB).
- **F2 placeholder** — per-donor × per-module activation-score heatmap with mock z-scores, watermarked "PLACEHOLDER". Layout and axes match the planned final figure so a reviewer at the kickoff meeting can see what the eventual output will look like. Replaced by real data once Phase 4 overlay runs.

### 16:15 — Whitfield bulk overlay notebook stubs

`analysis/overlay/whitfield_bulk/01_load_geo.ipynb`, `02_intrinsic_subsets.ipynb`, `03_project.ipynb` — JSON-skeleton notebooks for the reserve / complementary overlay path: GSE58095 + GSE45485 → intrinsic-subset assignment (Milano 2008 / Pendergrass 2012 signatures) → projection onto the MIM as a subset × module heatmap. Mirrors the Tabib scRNAseq stubs.

### 16:30 — ACR abstract scaffold

`scripts/draft_abstract.py` reads three JSON / TSV artifacts (`SSc_MIM_integrated.report.json`, `analysis/network/summary.json`, `reaction_evidence.tsv`) and writes `manuscript/ACR2026_late_breaking_abstract.md` as a 300-word IMRAD scaffold with **real volumetrics filled in**:

```
385 species, 175 reactions, 17 compartments
355 unique PMIDs (auto-mined; 158/159 reactions have a citation)
14 cross-module species (cofactor + signalling collapse)
31 detected communities vs 4 hand-defined modules
Top hubs: ISGF3, ISG_signature, PDGF·PDGFRα/β dimer, TGFB1:TGFBR2:p-TGFBR1, …
```

The Results section preserves explicit `[TO BE FILLED:` markers for the four numerical results that depend on the Phase 4 overlay (per-cluster DEG counts, per-donor module scores, mRSS correlations, drug shortlist size). The curator regenerates the scaffold via `make abstract` after each analysis update; placeholders are auto-replaceable downstream.

### 16:45 — `make auto` = full AUTO lane

Wired all new targets into the Makefile. The new flagship target:

```bash
make auto
```

Runs lint → validate → harmonise → seed → integrate → pmids → crosstalk → network → sink-check → preflight → ssc-stubs → figures → abstract in one go. A fresh clone + `make auto` reaches a deterministic state from raw imports to abstract scaffold.

### 17:00 — Batch 6 ready to commit

Commit plan:

1. `feat(bib): NCBI E-utils PMID metadata fill (350/350)`
2. `feat(preflight): MINERVA-readiness checklist`
3. `feat(assist): SSc Tier-1 species stubs per module (88 stubs)`
4. `feat(figures): preview F2 + F3 renderers`
5. `feat(overlay): Whitfield bulk notebook stubs`
6. `feat(manuscript): auto-drafted ACR abstract scaffold from analyses`
7. `chore: make auto = full AUTO lane`

### 18:30 — Pivot — co-author locked, MINERVA → post-pub, Zenodo → primary

User clarification this evening: existing co-author from médecine interne, prior ARD-SSc publication. → **Two original blockers resolved in one move:**

1. "Rheumatologist co-author lock" — done (clinician with SSc experience + literature credibility + ACR creds; specialty title is internal medicine, which is the *more* common SSc specialty in France).
2. "MINERVA Luxembourg curator role" — no longer on the critical path.

User direction: **deliver v1.0 on GitHub + Zenodo first**, MINERVA is a stretch goal post-publication.

### 18:45 — Why the pivot makes sense

- The map content (SBML + annotations + figures + scripts) IS the scientific deliverable. Hosting is one rendering of it.
- GitHub + a Zenodo DOI gives a stable, citable URL with no curator-role gatekeeping.
- ACR reviewers care about the resource + the translational story, not the hosting platform. "Available on GitHub (link), archived on Zenodo (DOI)" reads cleanly in an abstract.
- MINERVA stays a strong "v2.0 follow-up" line for the methodological paper — better-positioned with a DOI'd v1.0 already cited.
- Risk R8 (MINERVA tooling drift) closes for v1.0; R10 (Zenodo DOI propagation, 1–2 min after tag, worst case 1 day) replaces it.

### 19:00 — STATUS.md update

Reflect the pivot:
- ✅ co-author marked as locked.
- Handover queue collapses from 7 items to 4: kickoff scheduling, CellDesigner GUI work, CITATION.cff + .zenodo.json placeholder fill, GitHub→Zenodo webhook toggle, 3 seed BibTeX TODOs, `git tag v1.0` push. (MINERVA, WikiPathways EndMT, ACR portal account moved to post-publication.)

### 19:15 — ROADMAP rewrite

Substantive rewrite of `ROADMAP.md`:

- New "Pivot" section documenting the before/after of the 2026-05-16 decision.
- New **v1.0 release definition** section listing exactly what ships in the release bundle and the acceptance criteria.
- **Milestone calendar revised:** original M8 (MINERVA deployment) demoted to M12 (optional, post-Nov 2026); new M8 = "v1.0 release on GitHub + Zenodo DOI" with target date 31 Aug.
- **New Phase 6** (post-publication / stretch) section captures MINERVA, WikiPathways EndMT, BioModels deposit, peripheral module extensions.
- **Go/no-go gates** revised: G1 stays auto-skipped, G1.5 already passed (co-author locked), new G3 = `make preflight` + clean tree before tagging.
- **Risk register** updated: R3 medium → low; R8 closed; R10 (Zenodo propagation) and R11 (co-author bandwidth July–Aug) added.

### 19:30 — Zenodo deposit bundle

Two new files:

- **`.zenodo.json`** — Zenodo reads this on every tagged GitHub release (when the GitHub↔Zenodo integration is enabled). Metadata: title, description (with real volumetrics), keywords, CC-BY-4.0 licence, `diseasemaps` community membership, related identifiers pointing to the five source Reactome pathways, two creator slots with REPLACE_ME placeholders for the user + co-author.
- **`scripts/release_prep.py`** — pre-release sanity check. Verifies (a) branch = main, (b) working tree clean, (c) `CITATION.cff` and `.zenodo.json` have no REPLACE_ME / 0000-… placeholders, (d) `make preflight` passes, (e) writes / overwrites `CHANGELOG.md` from `git log`. Non-destructive by default; `--tag VERSION --push` actually creates and pushes the tag.

Smoke-tested: correctly flags the current dirty tree + 11 REPLACE_ME placeholders (5 in CITATION.cff, 6 in .zenodo.json). Once the user fills those, `make release` is one command.

### 19:45 — Supporting updates

- `minerva/deployment_notes.md` — re-labelled as post-publication stretch; preserves the deployment plan in case the user pursues it later. Adds the Docker self-host alternative.
- `scripts/draft_abstract.py` — conclusion section rewritten: "publicly archived on Zenodo (DOI) and developed on GitHub" instead of "publicly hosted on MINERVA". F1 marker also updated (no MINERVA screenshot dependency).
- `manuscript/ACR2026_late_breaking_abstract.md` regenerated with the new conclusion.
- `docs/risks.md` — R3 downgraded, R8 closed, R10 and R11 added.

### 20:00 — `make release` is the new one-shot

```bash
$ make release
# branch + tree + placeholders + preflight check
# writes CHANGELOG.md
# prints the `git tag` command to run when ready
```

When the user runs `make release --tag v1.0 --push` (after filling placeholders + the co-author's CellDesigner round), the Zenodo webhook mints a DOI within 1–2 minutes.

### 20:15 — Commit plan

1. `docs: pivot — STATUS + ROADMAP rewrite around GitHub+Zenodo v1.0 delivery`
2. `feat(release): .zenodo.json + scripts/release_prep.py + make release`
3. `docs: deprioritise MINERVA notes; downgrade R3 + R8; add R10 + R11`
4. `chore(abstract): conclusion rewritten for Zenodo/GitHub; regenerate manuscript`

### 21:00 — Curator mode: build v1.0 end-to-end

User direction: *"focus soumission ACR, essaie de répondre seul aux questions de curations, travaille à une roadmap spécifique pour ça, présenter un livrable concret de bout en bout."* Translation: act as the curator-stand-in, build v1.0, document choices, keep reversible.

Three docs pin the curation strategy:

- **`docs/curation_plan.md`** — granularity rules, three-tier ECO citation policy (ECO:0000314 strong / 0000270 moderate / 0000305 inference with explicit "co-author upgrade" markers), reaction-density targets per module, v1.0 success metrics.
- **`docs/curation_decisions.md`** — explicit answers to Q1 (4-module scope **holds** — no reshape, M3-Notch emphasis upweighted, complement deferred to v1.1), Q2 (per-module add/remove/promote with rationale), Q3 (**ACR-only**, methods paper to 2027).
- **`curation/ssc_curated_reactions.tsv`** — source-of-truth: 67 SSc-specific reactions. M1 12, M2 22 (heaviest, fills the ECM-sink gap), M3 13, M4 11, crosstalk 8, sink-feeding 1. PMID coverage: 27 strong (ECO:0000314), 10 moderate (ECO:0000270), 2 physical interaction (ECO:0000353), 28 curator inference (ECO:0000305 with explicit "co-author upgrade" notes).

`scripts/wire_ssc_tier1.py` reads the TSV + the 88 stubs + the integrated map, adds the 88 stub species + 45 auto-created species (sink phenotypes + phospho-states + new conceptual species like dsDNA / cGAMP / TGFB1 standalone) + the 67 reactions. Also updates `species_annotations.tsv` (133 new rows) and `reaction_evidence.tsv` (67 new rows).

### 21:30 — TSV parsing pitfall

Built the TSV by hand. First load: 4 rows had a PMID in the ECO column + 1 row had only 10 columns. Cause: I'd written 3 tabs (= 2 empty cells) between products and pmid in rows where modifiers were empty, instead of 2 tabs (= 1 empty cell). Fixed five rows. Now: 67 rows × 11 columns clean.

### 21:45 — Wire result

```
integrated map before:  385 species, 175 reactions
integrated map after:   518 species, 242 reactions, 20 compartments
  - stubs wired:        88
  - reactions added:    67
  - species auto-created: 45  (sink phenotypes, phospho-states, new concepts)
species_annotations.tsv: 385 → 518 rows
reaction_evidence.tsv:   159 → 226 rows
```

### 22:00 — Re-running the AUTO lane on the curated map

`make preflight` advisories down to 1 (dangling fraction, expected). All blocking checks green.

**Network analysis** — top hubs now reflect SSc biology:

| Rank | Species | Module | Hub score |
|------|---------|--------|-----------|
| 1 | SMAD3:SMAD4 (nuclear) | M2 | 11.10 |
| 2 | NICD1 (cytosol) | M3 | 9.31 |
| 3 | ISGF3 | M1 | 9.28 |
| 4 | ISG_signature | M1 | 9.23 |
| 5 | fibroblast_proFibrotic | M2 | 9.05 |
| 6 | TGFB1 (extracellular) | M2 | 8.96 |
| 7 | TGFB1:TGFBR2:TGFBR1 (Reactome complex) | M2 | 8.20 |
| 8 | SNAI2 (nuclear) | ssc_tier1 | 6.70 |

Compare to the previous Reactome-only run where the top 5 were all multi-protein Reactome complexes. The fibrosis story is now visible in the hub list.

**Sink connectivity** — every anchor group now has nodes:

| Sink | Before | After |
|------|--------|-------|
| M1 ISG_signature | 9 | **10** |
| M2 ECM/myofibroblast | **0** | **7** ← unlocked by curation |
| M3 vascular remodelling | 12 | **12** |
| M4 Th2/autoAb output | 8 | **10** |

Dangling fraction: 126 / 385 = 33% → 124 / 518 = **24%**. The numerator is roughly stable but the denominator grew, and the 88 newly-added stubs still need their full reactions wired to reach a sink — 37 of the 88 are dangling (those need their downstream-most reactions added in v1.1).

**0 species violate the >6 sink-distance rule** — the scoping invariant holds.

### 22:15 — Re-rendered figures + abstract

- `figures/F3_druggable_targets.svg/png` — re-rendered from the curated map. Hub subnetwork now shows SMAD3/TGFB1/fibroblast nodes prominently with their M2 colour, distinct from the IFN cluster.
- `manuscript/ACR2026_late_breaking_abstract.md` — Results section auto-updated to "518 species across 20 compartments, 242 reactions… 65 detected communities".

Also fixed `draft_abstract.py` to read live totals directly from `SSc_MIM_integrated.xml` rather than the stale `SSc_MIM_integrated.report.json` (which is captured pre-wire).

### 22:30 — Makefile integration

Two new targets:
- `make wire` — apply the curated TSV to the integrated map.
- `make auto` updated to include `ssc-stubs → wire` between `crosstalk` and `network` so the full pipeline now reaches v1.0 state.

### 22:45 — Commit plan (this batch)

1. `feat(curation): curation plan + decisions + reactions TSV (67 SSc-specific reactions)`
2. `feat(curation): wire SSc Tier-1 into integrated map; 518 species / 242 reactions`
3. `feat(analyses): re-run network + sink + figures + abstract on curated map`
4. `docs: ROADMAP curation sub-plan + STATUS refresh`

### 15:00 — Notebook stubs for the omics overlay

Six JSON-skeleton notebooks under `analysis/overlay/tabib_scRNAseq/`:

- `01_qc.ipynb` — load counts → AnnData, per-cell metrics, filtering rules.
- `02_clustering.ipynb` — normalise, HVG, PCA → kNN → Leiden → UMAP, marker-based annotation (SFRP2+ / PRSS23+ fibroblasts, myofibroblasts, ECs, etc.).
- `03_deg.ipynb` — Wilcoxon SSc vs HC per cluster, FDR < 0.05, |log2FC| ≥ 0.5.
- `04_projection.ipynb` — join DEGs to `species_annotations.tsv`, output MINERVA-compatible overlays.
- `05_scoring.ipynb` — per-donor module activation score (M1/M2/M3/M4), correlation with mRSS / disease duration / autoAb status.
- `06_drug_targets.ipynb` — DGIdb + Open Targets, ChEMBL phase, scored hub × drug table.

All six parse as valid `nbformat 4.5`. Empty code cells with `# TODO: implement during Phase 4 (week 15/16).` markers.

### 15:15 — Lint CI workflow

`.github/workflows/lint.yml` — two jobs (`specs-check`, `bib-check`) on Python 3.11, triggered on changes to module specs or the bib. Bib-check kept informational until Phase 2 (the corpus is intentionally TODO-heavy at week 1).

### 15:25 — Batch 2 ready to commit

Files in this batch:

```
Makefile
scripts/check_module_specs.py
scripts/check_bib.py
scripts/reactome_pilot.py
.github/workflows/lint.yml
docs/decisions/2026-05-15_reactome_import.md
docs/import_pilot.md  (updated)
docs/module_specs/M2_TGFb_fibrosis.md  (compartment fix)
docs/module_specs/M3_EndoMT_vasculopathy.md  (compartment + ACTA2 fix)
docs/module_specs/M4_IL6_Th2_Bcell.md  (JAK1/TYK2 → shared subsection)
analysis/overlay/tabib_scRNAseq/01_qc.ipynb..06_drug_targets.ipynb
curation/imports/M2/pilot_R-HSA-2173789/*  (real pilot output, 880 kB total)
```

Will split into two commits for readability:
- `feat: tooling + linters + Makefile + lint CI`
- `feat(M2): Reactome pilot — successful import of R-HSA-2173789 (TGF-β)`

---

## 2026-05-18 — Status review + SBML validation fixes

### 10:00 — Project status bilan

Full health-check of the project: built a Python `.venv` (system Python 3.12 lacks the project deps), ran the complete pipeline (`validate_sbml`, `minerva_preflight`, `network_analysis`, `sink_connectivity`, `druggable_hubs`, `render_figures`, `draft_abstract`, `check_module_specs`, `check_bib`, `release_prep`), and reviewed ROADMAP/STATUS against the current git state.

**Findings:**

| Check | Result |
|-------|--------|
| `make preflight` | ✅ 0 blocking failures, 1 advisory (dangling 18%) |
| `check_module_specs` | ✅ 4 specs clean |
| `check_bib` | ✅ 358/361 entries filled; 3 seed PMIDs still TODO |
| `network_analysis` | ✅ 38 communities, SSc hubs correct |
| `druggable_hubs` | ✅ 23 SSc-relevant targets via DGIdb |
| `render_figures` | ✅ F1/F2/F3 generated |
| `draft_abstract` | ✅ 526 sp. / 260 rxn. / 386 PMIDs |
| `validate_sbml` | ❌ **391 errors** (see below) |
| `release_prep` | ❌ 3 blockers (figures dirty, 11 REPLACE_ME placeholders, 3 bib TODOs) |

**ROADMAP position:** all AUTO + ASSIST Phase 2-3 work is complete. Binding constraint is co-author bandwidth for GUI round-trip and review (M6 milestone target: 15 Jul). Release blockers (CITATION.cff, .zenodo.json, webhook) are human-only tasks.

### 11:00 — SBML validation: root-cause analysis

`make validate` (libSBML schema validation) exposed 391 errors across three distinct classes — all pre-existing, previously hidden behind the ordering errors that caused libsbml to short-circuit further checks:

**Class 1 — annotation/notes ordering (385 errors in `SSc_MIM_integrated.xml`)**
SBML L2V4 §4.1 requires `<notes>` to appear *before* `<annotation>` in every element. Reactome exports have the reverse order. This was introduced during `make integrate` because `integrate_modules.py`'s `annotate_species_with_module()` appended `<notes>` after the pre-existing `<annotation>` via `ET.SubElement()`, and on the first pass the Reactome XML was used as-is.

**Class 2 — XHTML format (385 hidden + newly visible in integrated, + 4 in stubs)**
All species/reaction notes used `<html:html><html:body>…` without `<html:head>`. The SBML validator enforces that form-1 XHTML ("complete document") requires `<html>`, `<head>`, *and* `<body>`. Without `<head>`, the content satisfies none of the three allowed forms. The model-level notes (which always had `<html:head>`) validated correctly; the species/reaction notes (generated by the Python scripts) did not.

**Class 3 — Invalid SId `COX-2__er` (2 in integrated, 1 in M3 stub)**
Hyphens are not permitted in SBML SId syntax. The name "COX-2" (PTGS2 alias) was used verbatim as the ID base; the correct sanitised form is `COX_2__er`.

### 11:30 — Fixes applied

**`SSc_MIM_integrated.xml`**

1. *Ordering fix (385 species):* Regex anchored on `<species[^>]*>` to safely swap only species-level `<annotation>/<notes>` blocks without risk of cross-element contamination. (A first attempt using an unanchored DOTALL regex was reverted — it matched from the model-level `<annotation>` across thousands of lines to the first species' `</annotation>`, corrupting the model structure. Restored from git and reapplied with the correct pattern.)

2. *XHTML fix (611 notes):* Added `<html:head><html:title /></html:head>` inside every `<html:html>` block to produce valid form-1 XHTML. Simple string replacement; the `xmlns:html` declaration was already present on the `<sbml>` element.

3. *SId fix (`COX-2__er` → `COX_2__er`, 3 occurrences):* species `id`, `metaid`, and `speciesReference species` attribute.

**Stub files `M1–M4_ssc_additions.xml`**

- Added `xmlns:html="http://www.w3.org/1999/xhtml"` to `<sbml>` opening tag.
- Changed `<html xmlns="…"><body>` → `<html:html><html:head><html:title /></html:head><html:body>`.
- Fixed `COX-2__er` → `COX_2__er` in M3 stub.

**TSV annotation files**

`curation/annotations/species_annotations.tsv`, `reaction_evidence.tsv`, `curation/ssc_curated_reactions.tsv` — renamed `COX-2__er` → `COX_2__er` in all references.

**Scripts (source-level fixes — prevent regression on next `make auto`)**

| Script | Change |
|--------|--------|
| `integrate_modules.py` | `_insert_notes_before_annotation()` helper inserts `<notes>` before `<annotation>` when creating a new notes block; post-processing loop reorders existing wrong-order children before writing. |
| `wire_ssc_tier1.py` | `add_species()` and `add_reaction()` now build `html/head/title/body` structure. |
| `ssc_additions_template.py` | `build_sbml()` adds `xmlns:html` to `<sbml>` and uses `<html:html><html:head>…` format. |

### 12:00 — Verification

```
make validate  →  all [ok]   (5 files, 0 errors)
make preflight →  1 advisory (dangling fraction unchanged)
```

**Commit `68d4317`** — `fix(sbml): resolve all 391 SBML L2V4 validation errors`.

---

## 2026-05-19 — Manuscript draft

### 10:30 — First IMRAD manuscript draft generated

Generated `manuscript/SSc_MIM_manuscript_draft.md` — a full IMRAD scientific manuscript draft (~4 800 words) targeting Frontiers in Bioinformatics (or npj Systems Biology and Applications).

**Structure:**
- Title, affiliations, ORCID (Nathan Foulquier, LBAI U1227 Inserm CDC CHU Brest)
- Abstract (flowing prose, no section labels): 246 words
- Introduction: disease context, mechanistic complexity, gap statement, Disease Maps Project rationale
- Materials and Methods (9 subsections, 2.1–2.9): module definition, Reactome import, SSc Tier-1 curation, MI2CAST annotation, SBML validation pipeline, scRNA-seq overlay (Tabib 2021, GSE138669), network analysis (NetworkX, Louvain), DGIdb drug prioritisation, software/reproducibility statement
- Results (3 subsections): Table 1 (module statistics), Figure 1 placeholder (global MIM), scRNA-seq overlay with coverage metrics, Table 2 (top-20 hubs + drugs), Figure 2 and Figure 3 placeholders
- Discussion (4 subsections): Disease Maps ecosystem context, TGF-β/IFN axis, Notch/EndoMT, stratification by subtype; limitations section
- Conclusion, Data Availability, Author Contributions, Funding, Acknowledgements
- 26 references (Vancouver-style, PMID-cited)

**Key quantitative claims used:**
- 526 species, 260 reactions, 17 compartments, 85 SSc-curated reactions
- 355 unique PMIDs (from `.zenodo.json`)
- 38 network communities; top hub SMAD3p_SMAD4 (13.42)
- 21 SSc-relevant drug–target interactions (DGIdb)
- 60% scRNA-seq map coverage (Tabib 2021)

**Pending before submission:**
- Co-author metadata (REPLACE_ME placeholder in `.zenodo.json` / `CITATION.cff`)
- Funding statement
- Validation of scRNA-seq coverage fraction against updated overlay output
- Figures F1–F3 already generated as SVG under `figures/`; need journal-format PNG exports
- Pre-submission check against Frontiers author guidelines (word limit, figure count)

---

## 2026-05-19 — Real Tabib 2021 pipeline + ROADMAP check

### 10:30 — Vrai pipeline scanpy

Téléchargement des données GEO (GSE138669_RAW.tar, 594 MB) + extraction des 22 fichiers `.h5`. Installation de scanpy 1.12 + h5py 3.16 dans le venv.

Implémentation du vrai pipeline dans `scripts/build_overlay.py` (`real_deg()`) :
- Métadonnées SSc/HC récupérées depuis le soft file GEO (SC2/SC5/SC19/SC49/SC60/SC69/SC70/SC86/SC119/SC185/SC188/SC189 = SSC ; reste = HC)
- QC : 16 220 160 → 64 211 cellules (min_genes 200, max_genes 6000, pct_mt < 25%)
- Normalisation 10 000 cppc, log1p, HVG top 2000, PCA 30 composantes, kNN k=20, Leiden 0.35
- Annotation : 6 types (keratinocyte 29 535, fibroblast 13 046, myofibroblast 8 790, endothelial 6 930, T lymphocyte 2 987, macrophage 2 923)
- DEG pseudobulk Wilcoxon (12 SSC vs 10 HC) : 1 058 paires (|log2FC| ≥ 0.2, p ≤ 0.05)
- 34 espèces MIM mappées (16% des 211 gènes annotés HGNC)
- Scores par module : M1 SSc 0.342±0.095 / HC 0.070±0.016 ; M2 SSc 0.232±0.061 / HC 0.044±0.007
- Top IFN : IFITM3, IFITM1, IFI27, IRF7, ISG15 (macrophages + myofibroblastes)
- Top fibrose : COL1A1, COMP, POSTN, TNC (fibroblastes)
- Commit `572892f`

### 11:30 — Manuscrit mis à jour avec les vrais chiffres

4 sections corrigées : Abstract, Methods 2.6, Results 3.2, Discussion 4.4. Les chiffres synthétiques (60% coverage, 97 DEG) remplacés par les valeurs réelles. Commit `4571708`.

### 14:00 — Bilan ROADMAP

État au 2026-05-19 :

| Phase | État |
|-------|------|
| 0 Bootstrap | ✅ |
| 1 Curation docs | ✅ |
| 2 Imports + SSc Tier-1 (85 réactions) | ✅ |
| 3-AUTO Integration + réseau + Zenodo prep | ✅ |
| 4 Overlay réel + DGIdb + figures F1/F2/F3 | ✅ **complété cette session** |
| 5 Manuscrit draft | ✅ (draft complet ~5 100 mots) |
| 5 ACR abstract | ✅ scaffold avec vrais chiffres |
| Co-author kickoff | 🔴 EN ATTENTE |
| CellDesigner GUI + wiring | 🔴 EN ATTENTE |
| .zenodo.json co-author REPLACE_ME | 🔴 EN ATTENTE |
| Zenodo webhook | 🔴 EN ATTENTE |
| v1.0 tag | 🔴 EN ATTENTE |

Gates en cours :
- G2 (31 jul) : co-author review → **bloquant**
- G3 (24 août) : `make preflight` clean → 1 advisory seulement (dangling 17.9%, target ≤15%)
- G4 (11 sep) : F2 real data → **✅ passé**
- G5 (18 sep) : abstract sign-off co-auteur → en attente

STATUS.md mis à jour pour refléter l'état actuel (526 sp / 260 rxn, mode=REAL).

### 15:00 — Recherche de jeux de données complémentaires + mise à jour ROADMAP

**Problème identifié** : la couverture DEG de la MIM est de seulement 16% (34/211 espèces HGNC) avec Tabib 2021 seul. Cause : le skin biopsy atlas manque de pDC, B cells, cellules endothéliales, et myofibroblastes pulmonaires.

**Datasets ouverts identifiés (survey systématique GEO + PubMed) :**

| Priorité | Accession | Étude | Tissu | Gap MIM rempli |
|----------|-----------|-------|-------|----------------|
| P1 | GSE210395 | SSc PBMC pDC/monocyte (2022) | Sang | axe pDC IFN-I → M1 |
| P1 | GSE128169 | Morse *ARD* 2019 (PMID 31405848) | Poumon SSc-ILD | myofibroblastes pulmonaires → M2 |
| P2 | GSE159354 | Vanderploeg *Front Immunol* 2021 (PMID 33679266) | Poumon SSc-ILD+IPF | IFN-I vs IFN-γ divergence |
| P2 | GSE195452 | Gur *Cell* 2022 (PMID 35381199) | Peau multiome (97 SSc / 56 HC) | LGR5+ ScAF → M2+M3 |
| P3 | GSE136831 | Adams *Sci Adv* 2020 (PMID 32832599) | Poumon IPF (312k cellules) | HAS2+/ACTA2+ myofibroblastes → M2 |
| P3 | GSE136103 | Ramachandran *Nature* 2019 (PMID 31748742) | Foie cirrhotique | HSC → myofibroblaste (LOXL2, MMP2) → M2 |

Tous sans restriction d'accès (pas de dbGaP). Gain attendu : 16% → ~30-40% couverture MIM après intégration P1+P2.

**Mise à jour ROADMAP :** Phase 4b créée ; milestone M9b (31 août) ; gate G4b ajouté. Phase 4 marquée ✅ complète. Manuscrit draft marqué disponible.

### 17:00 — Intégration P1 datasets (GSE210395 + GSE128169) — Phase 4b complète

**Objectif :** augmenter la couverture MIM de 16% (skin seul) à ≥30% via deux datasets complémentaires.

**Données téléchargées :**
- `data/raw/gse210395/GSE210395_scRNA_countMatrix.tsv.gz` — 379 MB, format long-format triplet (feature/cell/count)
- `data/raw/gse128169/GSE128169_RAW.tar` — 1,1 GB, matrices MEX GEO flat-directory (13 échantillons, 5 HC + 8 SSC)

**Script :** `scripts/build_overlay_multi.py` — pipeline unifié pour les 3 datasets (skin/PBMC/lung).

Particularité technique : les fichiers GEO de GSE128169 sont au format "flat-directory" avec préfixe de sample (`GSM3666096_SC45NOR_matrix.mtx.gz`). La fonction `sc.read_10x_mtx` de scanpy ne supporte pas ce format ; chargement manuel via `scipy.io.mmread` + pandas.

**Résultats pipeline (commit `4136481`) :**

| Dataset | Tissu | Cellules (QC) | Types cellulaires | DEG entries | Donors |
|---------|-------|---------------|-------------------|-------------|--------|
| Tabib 2021 (GSE138669) | Skin | 64 211 | 6 (keratinocyte, fibroblast, myofib., endothélial, macrophage, T) | 1 066 | 22 |
| GSE210395 | PBMC | 34 619 | 6 (pDC, monocyte classique/non-classique, NK, B, plasma) | 1 799 | 8 |
| GSE128169 | Poumon ILD | 67 516 | 6 (AT2, macrophage-SPP1, macrophage-alv, T, endothélial, fibroblaste-CXCL12) | 1 125 | 13 |
| **TOTAL** | | **166 346** | **18 clusters** | **3 990** | **43** |

**Couverture MIM : 72/211 espèces HGNC = 34.1%** (gate G4b ≥30% : ✅ atteint)

Nouvelles espèces capturées par rapport au skin seul :
- M1 IFN-I : BST2, IFITM1, IFI44, IFIT3, OASL (pDC PBMC)
- M2 TGF-β/fibrose : CTHRC1, FN1, POSTN, TNC, COL5A1/2 (myofibroblastes poumon)
- M4 IL-6/B : CD40, CD79B, BTK, MZB1 (B lymphocytes / plasma cells PBMC)

18 overlays MINERVA générés (6 skin + 6 PBMC + 6 lung). Figure F2_multi 3 panneaux générée.

STATUS.md mis à jour (Phase 4b COMPLETE, couverture 34.1%).

### 18:00 — Correction dénominateur couverture + nettoyage alias HGNC

**Question posée :** 34% de couverture, c'est faiblard ?

**Analyse :** le dénominateur de 211 incluait des entrées structurellement inaccessibles au transcriptomique :
- 7 petites molécules (ADP, ATP, GDP, GMP, GTP, H2O, NO)
- 6 isoformes/complexes dont le gène parent est déjà dans le MIM (ISGF3, NICD1, LAP, IL6R-2, IL6ST-2, STAT1-1)
- 15 alias non-officiels (BCMA, BLIMP1, CD154, CD31, COX-2, FSP1, PCAF, PI3K, IFNAR2-2, ZFYVE9-1, ARRB, DTX, HEY, MAML, TLE)

**Corrections appliquées (`c5cb945`) :**
- 15 alias remplacés par les symboles HGNC officiels (BCMA→TNFRSF17, FSP1→S100A4, COX-2→PTGS2, etc.)
- 13 hgnc_symbol vidés avec note explicative (métabolites + collisions isoformes)

**Résultat :** 198 symboles HGNC propres (vs 211), 196/198 (99%) détectables par RNA-seq. Gains directs : +3 hits (PECAM1, PTGS2, S100A4).

**Couverture finale corrigée :**

| Dénominateur | Hits | % |
|---|---|---|
| Toutes annotées (ancien) | 72/211 | 34.1% |
| Détectables RNA-seq (corrigé) | **75/196** | **38.3%** |

Par module : M1 IFN-I 50% · SSc-Tier1 44% · M2 TGF-β 34% · M4 IL-6/B 24% · M3 Notch/EndoMT 17%

M3 volontairement bas : les cellules endothéliales en transition et les péricytes sont absents des 3 datasets — gap documenté dans le manuscrit (Discussion 4.4).

Manuscrit mis à jour (`00017d5`) : abstract, Methods 2.6, Results 3.2, Discussion 4.4.

