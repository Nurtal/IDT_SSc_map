# STATUS — SSc-MIM

> Snapshot for orientation. Updated on every batch.
> Authoritative source for completion state is the git log; this file gives one-screen context.

## Headline

- **11 commits** on `main`, pushed to GitHub.
- **5 Reactome imports** fetched, post-processed, harmonised. **0 encoding-token leftovers** across all five files.
- **385 unique species, 175 reactions** scaffolded across M1, M2, M3, M4.
- Reactome pilot succeeded live; harmonisation classifier produced JSON reports flagging every transform.
- **All Phase 0 + Phase 1 items + the import phase of Phase 2 are complete or done early.**

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

## Inventory

| Artifact | Count | Notes |
|----------|-------|-------|
| `curation/imports/*/*/*.harmonised.xml` | 5 | M1 + M2×2 + M3 + M4 |
| `curation/annotations/species_annotations.tsv` | 385 rows | Auto-HGNC fill 32% (complexes need component-level annotation) |
| `curation/annotations/reaction_evidence.tsv` | 0 rows | MI2CAST annotation pending |
| `curation/pubmed_corpus.bib` | 6 BibTeX entries | 3 with `pmid={TODO}` |
| `scripts/*.py` | 7 | reactome_pilot, post_process_reactome, harmonise_imports, seed_species_from_imports, check_module_specs, check_bib, wikipathways_fetch, validate_sbml |
| `.github/workflows/` | 3 | validate_sbml, lint, scripts-smoke |

## Delivery target — pivoted 2026-05-16

**Primary v1.0 delivery: GitHub repo + Zenodo DOI release**, *before* ACR submission. MINERVA deployment is now a post-publication stretch goal — the map content is the deliverable, hosting is one rendering of it.

The pivot resolved two original blockers in one move:
- "Rheumatologist co-author" is locked → an existing collaborator (médecine interne, ARD-published on SSc with the lead curator).
- "MINERVA Luxembourg curator role" is no longer on the critical path.

## What's left

See [ROADMAP.md](ROADMAP.md) for the new GitHub+Zenodo-first plan. Summary:

- 🟢 **Fully automatable**: integration, network analysis, sink connectivity, PMID extraction, crosstalk scaffold, bib lookup, preflight, SSc stubs, figures, abstract draft, Zenodo bundle prep — **all shipped**.
- 🟡 **Automation-assisted** (script generates scaffold; curator + co-author fill): SSc Tier-1 wiring in CellDesigner, MI2CAST reaction annotation review, manuscript polish.
- 🔴 **Human-only** (irreducible): co-author scope sign-off & biological validation, CellDesigner GUI work, ACR portal submission, the `v1.0` git-tag push.

## Open external items (handover queue)

1. ✅ ~~Co-author~~ — médecine interne collaborator, ARD-published SSc, **locked**.
2. **Co-author kickoff** — schedule 1-hour kickoff + 2 review sessions; brief is auto-generatable.
3. **CellDesigner GUI** — open `*.harmonised.xml` and `SSc_MIM_integrated.xml` for visual round-trip; wire the 88 SSc Tier-1 stubs (`curation/celldesigner/ssc_additions_template/`).
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
