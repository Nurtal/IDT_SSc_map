# STATUS — SSc-MIM

> Snapshot for orientation. Updated on every batch.
> Authoritative source for completion state is the git log; this file gives one-screen context.

## Headline  *(updated 2026-05-19)*

- **Integrated map:** 526 species, 260 reactions, 20 compartments. **SBML validation: 0 errors (5 files clean). `make preflight`: 1 advisory only (dangling 17.9%), 0 blocking failures.**
- **Phase 4 COMPLETE (real data)** — Tabib 2021 scanpy pipeline: 64 211 cells, 1 058 DEG entries, 34 MIM-mapped genes; REAL per-donor module scores (M1 IFN: SSc 0.342 vs HC 0.070; M2 fibrosis: 0.232 vs 0.044). Figures F1/F2/F3 generated.
- **Phase 5 partial** — Full IMRAD manuscript draft at `manuscript/SSc_MIM_manuscript_draft.md` (~5 100 words, Frontiers Bioinformatics target, real stats throughout).
- **Lead-author metadata filled** — `CITATION.cff` + `.zenodo.json` (Nathan Foulquier, ORCID 0000-0003-4620-2794, LBAI U1227 Inserm CDC CHU Brest). Co-author slot still REPLACE_ME.
- **All Phase 0 + 1 + 2 + 3-AUTO + 4 complete.** Binding constraint = co-author kickoff + CellDesigner GUI work + .zenodo.json co-author fill.

## What's done (with commit refs)

| Phase | Item | Commit |
|-------|------|--------|
| 0 | Repo bootstrap (LICENSE, .gitignore, CITATION.cff, CONTRIBUTING, issue templates, SBML CI) | `4dcf004` |
| 1.w1 | Curation guidelines (Mazein 2023), MI2CAST checklist, risks, scoping notes, four module specs with Tier-1 tables | `4dcf004` |
| 1.w1 | Reactome → CellDesigner conversion pilot (live, R-HSA-2173789 TGF-β) | `bfdaea7` |
| 1.w1 | Linters (`check_module_specs`, `check_bib`); fixed 3 real Tier-1 spec bugs the linter found | `a23c8bd` |
| 1.w3 | Omics dataset decision memo (Tabib scRNAseq primary, Whitfield bulk reserve) | `f2354f9` |
| 2.w4-5 | M1 IFN-α/β import + post-process + harmonise (83 species, 25 reactions) | `dd5da1d`, `392bb15` |
| 2.w6-7 | M2 TGF-β SMADs + PDGF imports + post-process + harmonise (175 species, 77 reactions) | `dd5da1d`, `392bb15` |
| 2.w8-9 | M3 Notch1 import (EndMT scaffold; rest manual per design) — 77 species, 39 reactions | `392bb15` |
| 2.w10-11 | M4 IL-6 import + post-process + harmonise (64 species, 34 reactions) | `dd5da1d`, `392bb15` |
| (tooling) | Post-processor + harmoniser + species seeder + Makefile + scripts-smoke CI | `cf92a46`, `876deaa`, `1304100`, `b7226eb` |
| QC | **391 SBML L2V4 errors resolved** (notes/annotation ordering, XHTML head, SId hyphens); source-level fixes in 3 generator scripts | `68d4317` |
| metadata | Lead-author CITATION.cff + .zenodo.json filled (Foulquier, ORCID, LBAI affiliation) | `40da591` |
| 4 | **Real Tabib 2021 scanpy pipeline** — 64 211 cells QC'd, 6 cell types, 1 058 DEG entries, 34 MIM-mapped species (16% coverage); REAL per-donor module scores; F2 updated (mode=REAL) | `572892f` |
| 4 | **Druggable hub prioritisation** — 21 SSc-relevant drug–target interactions via DGIdb; F3 generated | earlier |
| 4 | **Figures F1/F2/F3** — SVG + 300 dpi PNG for all three main figures | earlier |
| 5 | **IMRAD manuscript draft** — ~5 100 words, Frontiers Bioinformatics target, all sections complete with real pipeline stats | `4571708` |

## Inventory

| Artifact | Count | Notes |
|----------|-------|-------|
| `curation/celldesigner/SSc_MIM_integrated.xml` | **526 species / 260 reactions / 20 compartments** | SBML validated 0 errors; preflight 1 advisory |
| `curation/imports/*/*/*.harmonised.xml` | 5 | M1 + M2×2 + M3 + M4 |
| `curation/ssc_curated_reactions.tsv` | 85 reactions | source-of-truth for SSc-specific layer |
| `curation/celldesigner/ssc_additions_template/*.xml` | 88 stubs | all wired into integrated map |
| `curation/annotations/species_annotations.tsv` | 526 rows | full coverage of the integrated map |
| `curation/annotations/reaction_evidence.tsv` | 244 rows | 198 with PMID (81%) |
| `curation/pubmed_corpus.bib` | 361 BibTeX entries | 358 fully filled; 3 seed TODOs |
| `analysis/network/` | 5 files | 38 communities, top-20 hubs, SMAD3–SMAD4 #1 (score 13.42) |
| `analysis/overlay/` | cluster_deg.tsv (1 058 entries), patient_module_scores.tsv (22 donors), report (mode=REAL) | real Tabib 2021 data |
| `minerva/overlays/` | 6 cluster TSVs | ready for MINERVA import |
| `figures/` | F1 + F2 + F3 (SVG + 300dpi PNG) | F2 = REAL overlay |
| `manuscript/ACR2026_late_breaking_abstract.md` | 1 file | 300-word scaffold |
| `manuscript/SSc_MIM_manuscript_draft.md` | 1 file | ~5 100-word IMRAD draft (Frontiers Bioinformatics) |
| `scripts/*.py` | 16 | + fetch_tabib.py, build_overlay.py (real pipeline) |
| `.github/workflows/` | 3 | validate_sbml, lint, scripts-smoke |

## Delivery target — pivoted 2026-05-16

**Primary v1.0 delivery: GitHub repo + Zenodo DOI release**, *before* ACR submission. MINERVA deployment is now a post-publication stretch goal — the map content is the deliverable, hosting is one rendering of it.

The pivot resolved two original blockers in one move:
- "Rheumatologist co-author" is locked → an existing collaborator (médecine interne, ARD-published on SSc with the lead curator).
- "MINERVA Luxembourg curator role" is no longer on the critical path.

## What's left

See [ROADMAP.md](ROADMAP.md) for the new GitHub+Zenodo-first plan. Summary:

- ✅ 🟢 **Phase 0–4 AUTO lanes: COMPLETE.** Integration, validation, SBML QC, network analysis, real scRNA-seq overlay (Tabib 2021), DGIdb drug prioritisation, all figures, manuscript draft.
- 🟡 **Automation-assisted, remaining**: manuscript polish + co-author review of curation decisions.
- 🔴 **Human-only blockers (binding)**:
  1. Co-author kickoff + CellDesigner GUI wiring
  2. `.zenodo.json` co-author slot (2× REPLACE_ME)
  3. GitHub → Zenodo webhook toggle (one-time)
  4. `git tag v1.0 && git push --tags`

## Open external items (handover queue — updated 2026-05-19)

1. ✅ ~~Co-author~~ — locked.
2. **Co-author kickoff** — 1 h walkthrough of STATUS + F2/F3 + 85 SSc reactions; share `manuscript/SSc_MIM_manuscript_draft.md` as the brief.
3. **CellDesigner GUI** — visual round-trip + wire 88 stubs into `SSc_MIM_integrated.xml`.
4. **`.zenodo.json` co-author entry** — replace 2× REPLACE_ME (name, affiliation, ORCID).
5. **GitHub → Zenodo webhook** — one-time toggle at zenodo.org.
6. **3 seed BibTeX TODOs** — Aghakhani 2020 (CaSQ), Singh 2020 (RA-map), Tabib 2021.
7. **`git tag v1.0 && git push --tags`** — after G3 gate (24 Aug target).
4. **`CITATION.cff` `REPLACE_ME` placeholders** — author / ORCID / repository URL / co-author entry (the user has the metadata in hand).
5. **GitHub → Zenodo webhook** — one-time toggle in Zenodo to mint a DOI on `git tag v1.0`.
6. **3 seed BibTeX TODOs** — Aghakhani 2020 (CaSQ), Singh 2020 (RA-map), Tabib 2021 (skin scRNAseq) — need manual PMID lookup.
7. **Bibliography sprint** — mostly auto-completed (350/350 mined PMIDs filled by `bib_lookup.py`); remaining is the 3 seeds above.

## Post-publication / stretch (no longer blocking)

- MINERVA Luxembourg curator role + deployment.
- WikiPathways EndMT correct ID (WP_3942 was PPAR; pure nice-to-have).
- ACR portal account + figure-format check.

## Working assumptions for the automated branch

While external blockers resolve, the automation work assumes:
- The four sub-module scope (M1–M4) and the four sink phenotypes are stable.
- Reactome / NOTCH1 imports are acceptable as the structural scaffold pending biology review.
- Tier-1 entity tables in the module specs are the contract for what the curator will eventually add to each module.
- All automated outputs are reversible — they live alongside their JSON reports, and the curator can override any decision.

## How to verify the current state

```bash
git status                           # working tree clean
make lint                            # specs + bib linters pass
make validate                        # libSBML validation (CI also runs this)
python3 scripts/seed_species_from_imports.py --dry-run   # no diffs vs committed
```
