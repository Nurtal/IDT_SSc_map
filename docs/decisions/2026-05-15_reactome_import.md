# Decision — Reactome import workflow

- **Date:** 2026-05-15
- **Phase:** 1 (week 1)
- **Decider:** lead curator
- **Status:** accepted

## Context

The ROADMAP foresees a Reactome → CellDesigner pilot as the principal risk-down step in Phase 1. The pilot was executed end-to-end on `R-HSA-2173789` (TGF-β receptor signaling activates SMADs).

## Outcome

- SBGN-ML and BioPAX-L3 downloaded successfully from Reactome ContentService.
- SBGN-ML converted to CellDesigner SBML L2v4 via the MINERVA conversion API.
- Output: 100 species, 46 reactions, 5 compartments. Parseable by ElementTree; expected to pass libSBML validation in CI.

## Decision

Adopt a three-stage import workflow for every Reactome-derived module:

1. **Fetch.** `scripts/reactome_pilot.py --pathway R-HSA-XXXX --module Mx` (idempotent; skips existing files).
2. **Post-process.** Apply two transforms before manual curation:
   - **Rename species:** replace MINERVA UUIDs (`s_id_entityVertex_*`) with HGNC primary symbols using the existing `name` attribute. Collisions are resolved by appending a compartment or state-variable suffix.
   - **Collapse cofactors:** ATP / ADP / GTP / GDP / ubiquitin / H₂O / Pi appear in many copies (one per reaction); collapse to one species per compartment, or — for ubiquitin — convert to a state variable on the substrate per `docs/curation_guidelines.md` § 5.
   - A dedicated post-processor will be implemented in week 4 (start of Phase 2) before M2 curation kicks off: `scripts/post_process_reactome.py`.
3. **Curate.** Open the post-processed file in CellDesigner; add SSc-specific entities and reactions per the module spec; annotate per the MI2CAST checklist.

## Implications for the timeline

- Phase 2 weeks 4–7 (M1 + M2) remain on schedule. Estimated overhead per module for post-processing: 0.5–1 day, included in the existing day-1–2 "import" allocation.
- The 60/40 import/manual split is realistic; no change needed.

## Open items

- [ ] Implement `scripts/post_process_reactome.py` before week 4 (1 Jun).
- [ ] Open the converted file in CellDesigner GUI for a visual round-trip check (lead curator's workstation).
- [ ] Run a parallel pilot on RA-map (`R-HSA-1059683` IL-6 signaling) to confirm the same workflow holds for non-Reactome upstream sources.
