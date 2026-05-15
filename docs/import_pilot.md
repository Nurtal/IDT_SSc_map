# Reactome → CellDesigner import pilot

> Phase 1 / week 1 de-risking exercise.
> Target pathway: `R-HSA-2173789` — *TGF-beta receptor signaling activates SMADs*.
> Status: **not yet executed** (requires CellDesigner GUI + MINERVA conversion API access).

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

- [ ] Schedule a 2-hour block in week 1 for the pilot.
- [ ] Test the same flow on RA-map (Singh 2020) for module M2 / M4 imports.
