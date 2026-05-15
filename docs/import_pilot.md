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
