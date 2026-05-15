# Reactome → CellDesigner import pilot

> Phase 1 / week 1 de-risking exercise.
> Target pathway: `R-HSA-2173789` — *TGF-beta receptor signaling activates SMADs*.
> Status: **SBGN-ML download + MINERVA conversion successful (2026-05-15)**, GUI / round-trip checks still pending.

## Why this pathway

- Anchors module M2 (TGF-β / fibrosis), the largest module and the highest-impact for SSc.
- Reactome representation is dense (~30 entities) — large enough to surface real conversion issues, small enough to fix in a day.
- Reactome maintains an active SBGN-PD export for this pathway, the closest format to CellDesigner.

## Pre-flight (to execute locally)

1. Confirm CellDesigner v4.4 launches and can save an empty document.
2. Confirm the MINERVA conversion API is reachable (`https://minerva-service.lcsb.uni.lu/api/`).
3. Confirm one of:
   - Direct CellDesigner XML export from Reactome ContentService, or
   - SBGN-ML export → CellDesigner via MINERVA conversion.

## Steps

```text
[ ] 1. Retrieve `R-HSA-2173789` as SBGN-ML from Reactome ContentService.
[ ] 2. Convert SBGN-ML → CellDesigner SBML via MINERVA conversion API.
[ ] 3. Open the result in CellDesigner.
[ ] 4. Record visual fidelity (compartments, glyph types, arc types).
[ ] 5. Manually re-save and reopen to test round-trip stability.
[ ] 6. Run `python scripts/validate_sbml.py curation/imports/pilot_TGFb/` on the result.
[ ] 7. Note any HGNC mismatches, missing UniProt IDs, dropped annotations.
```

## Expected outcomes

- **Best case:** clean round-trip, all glyphs and arcs preserved, HGNC + UniProt annotations carried over. Adopt direct import for M1, M2, M4.
- **Acceptable case:** glyph layout lost, but biology preserved. Adopt import-then-relayout workflow.
- **Worst case:** identifiers dropped or arc signs flipped. Fall back to manual recreation using Reactome's online SBGN-PD as visual reference.

## Decision

- After this pilot, the lead curator commits a decision to `docs/decisions/2026-05-XX_reactome_import.md`:
  - Path forward for Reactome imports (direct / hybrid / manual).
  - Per-module estimated overhead.
  - Whether to update the 60/40 import/manual split.

## Open

- [ ] Open the converted `R-HSA-2173789.celldesigner.xml` in CellDesigner GUI for the visual round-trip check.
- [ ] Run CI / `validate_sbml.py` on the converted file (skipped locally — libsbml not in the host env; CI will pick it up).
- [ ] Test the same flow on RA-map (Singh 2020) for module M2 / M4 imports.

## Outcome (2026-05-15)

Automated pilot run via `scripts/reactome_pilot.py --pathway R-HSA-2173789 --module M2`.

| Artifact | Size | Path |
|----------|------|------|
| SBGN-ML  | 87 kB  | `curation/imports/M2/pilot_R-HSA-2173789/R-HSA-2173789.sbgn` |
| BioPAX (L3) | 437 kB | `curation/imports/M2/pilot_R-HSA-2173789/R-HSA-2173789.owl` |
| CellDesigner SBML | 363 kB | `curation/imports/M2/pilot_R-HSA-2173789/R-HSA-2173789.celldesigner.xml` |

Quick parse of the CellDesigner output (lxml):

- 5 compartments
- 100 species (includes Reactome's cofactor duplicates — ATP, Ub, GDP, …)
- 46 reactions

Observations:

- Species `id`s are MINERVA-generated UUIDs (`s_id_entityVertex_<n>`). Renaming to HGNC primary symbols is required before integration — needs a post-processing step.
- Cofactors like `ATP` and `Ub` are duplicated across reactions (one species per reaction it touches). House rule: collapse ATP / GTP / ubiquitin to one species per compartment after import.
- Ubiquitin appears as a free species. In SBGN-PD per our `curation_guidelines.md`, ubiquitination is encoded as a state variable on the substrate, not a free species. Strip on import.
- HGNC-friendly names are present on `<species>` `name=` attributes (CBL, FURIN, SMAD2, …), so the rename pass is a `name → id` transform plus a deduplication.

**Decision (logged in `docs/decisions/2026-05-15_reactome_import.md`):** adopt the import → post-process → curate workflow.

## Post-processor results (2026-05-15)

`scripts/post_process_reactome.py` applied to the four pathway imports. All four post-processed XMLs have zero UUID leftovers; reactions reference renamed HGNC-based species IDs.

| Module | Pathway | species (in→out) | reactions (in→out) | Ub removed |
|--------|---------|------------------|--------------------|------------|
| M1 | R-HSA-909733 (IFN α/β signaling) | 83 → 83 | 25 → 25 | 0 |
| M2 | R-HSA-2173789 (TGF-β / SMADs) | 100 → 99 | 46 → 46 | 1 |
| M2 | R-HSA-186797 (PDGF signaling) | 76 → 76 | 31 → 31 | 0 |
| M4 | R-HSA-1059683 (IL-6 signaling) | 64 → 64 | 34 → 34 | 0 |
| **Total** | | **323 → 322** | **136 → 136** | **1** |

No cofactor collapses occurred — each cofactor (ATP, ADP, H₂O, Pi) appears exactly once per compartment in the Reactome convention, which is already what we want.

## Known gotchas surfaced by the four imports

Reactome encodes several biological details inside the `name` attribute that survive the post-process step and need to be normalised in the curation phase (Phase 2):

| Pattern in name | Biological meaning | Curation action |
|-----------------|---------------------|-----------------|
| `p_minus_STAT2`, `p_minus_Y701_minus_STAT1` | phosphorylation (`p-` prefix; sometimes residue-specific) | Encode as a CellDesigner state variable (`@P` or `@P:S<residue>`) on the parent species; collapse multiple phospho-states |
| `STAT1_minus_1` | isoform 1 of STAT1 | Encode as a state variable or rename to `STAT1_iso1`; check UniProt for canonical isoform |
| `SOCS_minus_1_slash_SOCS_minus_3` | grouped entity `SOCS1/SOCS3` | Split into two distinct species |
| `Mx_space_GTPases` | the Mx family (MX1, MX2) | Split into MX1 and MX2 |
| `IRF_space_1_minus_9` | "IRF 1-9" (IRF family) | Split into IRF1…IRF9 individually |
| `OAS_space_proteins` | OAS family | Split into OAS1, OAS2, OAS3 |
| `Type_space_I_space_IFN_minus_regulated_space_genes_…` | a gene-set placeholder | Replace with explicit species (IFI44, IFI44L, ISG15, IFIT1…) or model as a "gene-set" black box with documented members |
| `Dimeric_space_TGFB1` | TGF-β1 homodimer | Encode as a complex of two TGFB1 |
| `default` compartment | unmapped compartment | Map to `extracellular` or `cytosol` depending on the species role |

These cases are tracked as the **import-cleanup backlog** for Phase 2 week 4 (M1, M2). The lead curator drives the cleanup before Tier-1 SSc-specific additions.

## Seeded species_annotations.tsv (2026-05-15)

`scripts/seed_species_from_imports.py` populated `curation/annotations/species_annotations.tsv` with **308 unique species** (dedup of 322 across modules → 14 cross-module collisions). `hgnc_symbol` is auto-filled when the species name matches the HGNC regex `^[A-Z][A-Z0-9\-]*$`; complex/phospho-form species are left for manual annotation.

## Harmonisation pass (2026-05-15)

`scripts/harmonise_imports.py` extends the post-processor with **identifier-level normalisation**. It:

- Decodes CellDesigner-escaped names (`_space_` → ` `, `_slash_` → `/`, `_minus_` → `-`, `_x_` → `:`) into human-readable display labels.
- Maps Reactome compartment names to our fixed vocabulary (`default` → `extracellular`, `nucleoplasm` → `nucleus`, `early_space_endosome` → `endosome`, etc.).
- Rewrites species `id` / `metaid` and every `species` / `reactant` / `product` / `modifiers` reference; also rewrites `<celldesigner:name>` and `<celldesigner:protein name=>` so the CellDesigner canvas shows the decoded label.
- Applies six classifications with flagged transformations:
  - **family_to_expand:** known family placeholders (`Mx GTPases` → `MX_family` + members `MX1, MX2`; `OAS proteins` → `OAS_family` + `OAS1, OAS2, OAS3`; `SOCS-1 and SOCS-3` → `SOCS_family`; `IRF 1-9` → `IRF_family`).
  - **gene_set_placeholder:** "Type I IFN-regulated genes…" → `ISG_signature`. To be expanded by the curator with explicit ISGs (IFI44, ISG15, MX1, OAS1…).
  - **phospho_state:** `p-X` → `pX`. Curator promotes to a CellDesigner state variable on the parent.
  - **isoform:** `X-N` → `X_isoN` (STAT1-1 → STAT1_iso1; IFNAR2-2 → IFNAR2_iso2).
  - **homodimer:** `Dimeric X` → `X_dimer`.
  - **slash_pair_to_split:** `X/Y` short pair → `XY` with a split flag.

After harmonisation, four imports refreshed (no structural changes; species and reaction counts unchanged):

| Module | species_renamed | flags (notable) |
|--------|-----------------|-----------------|
| M1 | 43 | 4 family_to_expand, 2 isoform, 1 gene_set_placeholder |
| M2 (TGF-β) | 68 | 1 homodimer, 1 isoform, 2 slash_pair_to_split |
| M2 (PDGF) | 57 | 0 (mostly clean names) |
| M3 (Notch1) | 48 | 1 phospho_state, 2 slash_pair_to_split |
| M4 (IL-6) | 52 | 2 isoform |

Encoding tokens (`_space_`, `_slash_`, `_minus_`) remaining in the four harmonised XMLs: **0** (verified by regex grep).

## M3 EndoMT — source-pathway story (2026-05-15)

The ROADMAP cited "WP_3942 EndMT" as the WikiPathways scaffold for module M3. **WP3942 turns out to be PPAR signalling**, not EndMT — a guessed ID from the original ROADMAP draft.

I probed several plausible IDs (`WP4474`, `WP4655`, `WP5045`, `WP5057`, `WP4787`) via the WikiPathways asset endpoint; all returned HTTP 403. The legacy webservice search APIs returned 404 / 403 too. WikiPathways' public REST surface appears to have been reorganised; a curator-driven lookup on the WikiPathways website itself is needed to identify the correct EndMT pathway ID.

**Fallback used:** Reactome `R-HSA-1980143` (*Signaling by NOTCH1*) was fetched and post-processed for M3. It contains 79 raw species, 39 reactions, with HIF1A, JAG1, JAG2, DLL1, NOTCH1 — all directly relevant to EndoMT signalling. Post-processed → 77 species, 39 reactions (2 ubiquitin species removed). Harmonised: 48 species renamed, including a phospho-state flag and two slash-pair flags.

This **does not** make M3 "import-anchored" like M1/M2/M4 — Notch1 is one piece. EndoMT-specific entities (endothelin axis, NO/sGC/cGMP, VE-cadherin loss, SNAI/ZEB induction) remain manual per the M3 spec. The ROADMAP's "~70-80% manual" estimate for M3 is unchanged.

**Open follow-up:** the lead curator should browse `https://www.wikipathways.org/` directly (or query Pathway Commons) for an EndMT-specific scaffold once the search APIs stabilise.

## Post-harmonisation volumetric (2026-05-15)

| Module | pathways | raw species | post-processed | harmonised flags | imported reactions |
|--------|----------|-------------|----------------|------------------|--------------------|
| M1 | R-HSA-909733 | 83 | 83 | 7 flagged | 25 |
| M2 | R-HSA-2173789 + R-HSA-186797 | 176 | 175 | 4 flagged | 77 |
| M3 | R-HSA-1980143 | 79 | 77 | 3 flagged | 39 |
| M4 | R-HSA-1059683 | 64 | 64 | 2 flagged | 34 |
| **Total** | 5 pathways | **402** | **399** | **16 flagged** | **175** |

After cross-import dedupe: **385 unique species** in `curation/annotations/species_annotations.tsv` — comfortably above the 200–300 species target band for the entire MIM (the target was *post-curation*; we still need to dedupe across modules during integration in Phase 3, then add SSc-specific Tier-1 manual entities).
