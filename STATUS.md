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

## What's left

See [ROADMAP.md](ROADMAP.md) for the new automation-first plan. Summary:

- 🟢 **Fully automatable** (next batch): integration, network analysis, sink-node connectivity, PMID extraction from BioPAX, crosstalk scaffold.
- 🟡 **Automation-assisted** (script generates scaffold; curator fills): SSc-specific Tier-1 additions, MI2CAST reaction annotation, manuscript outline.
- 🔴 **Human-only** (script cannot replace): rheumatologist kickoff & expert review, CellDesigner GUI visual round-trip, MINERVA account provisioning, ACR portal submission, biological sign-off on every Phase 2 day-6+ reaction.

## Open external blockers (need user action)

1. **Kickoff meeting** with SSc rheumatologist — needed for co-authorship lock + scope sign-off (Phase 1 / week 1).
2. **MINERVA Luxembourg curator role** — request access; needed for Phase 3 week 14.
3. **Bibliography sprint** — ~50 reviews + ~100 primary papers; requires expert filtering.
4. **CellDesigner GUI** — open `*.harmonised.xml` to verify visual round-trip.
5. **WikiPathways EndMT pathway ID** — the WP_3942 cited in the original ROADMAP is "PPAR signaling"; the real EndMT WP ID needs a manual browse on `wikipathways.org`.
6. **`CITATION.cff` `REPLACE_ME` placeholders** — author / ORCID / repository URL.

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
