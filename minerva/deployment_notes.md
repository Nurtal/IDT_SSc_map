# MINERVA deployment notes

> [[ROADMAP]] § Phase 3, week 14.
> Target instance: MINERVA at the University of Luxembourg (LCSB).
> Status: **not yet deployed**.

## Pre-flight (one-time)

1. Request curator access on the Luxembourg MINERVA instance (`https://minerva.uni.lu/`).
2. Confirm the integrated XML (`curation/celldesigner/SSc_MIM_integrated.xml`) passes the local `validate_sbml` script and the CI workflow.
3. Verify that all species in the integrated map have HGNC + UniProt annotations, and that PMIDs are correctly listed in `reaction_evidence.tsv` (post-Phase-2 QA).

## Deployment steps (target: week 14)

```text
[ ] 1. Login to MINERVA admin panel.
[ ] 2. Create project "SSc-MIM v0.x" with description copied from README.
[ ] 3. Upload the integrated CellDesigner XML.
[ ] 4. Configure submap colouring:
       - M1 (IFN-I):     blue   #2c7fb8
       - M2 (TGF-β):     red    #d7191c
       - M3 (EndoMT):    green  #1a9641
       - M4 (IL-6/Th2):  orange #fdae61
       - crosstalk:      grey   #636363
[ ] 5. Configure semantic zoom levels (overview → module → reaction).
[ ] 6. Enable search by HGNC symbol, UniProt accession, PMID.
[ ] 7. Add overlays from `minerva/overlays/`:
       - tabib_sfrp2_vs_healthy.tsv
       - tabib_myofibroblast_vs_healthy.tsv
       - per-patient module scores
[ ] 8. Configure permissions: public read; curator write.
[ ] 9. Verify in a clean browser session.
[ ] 10. Capture the public URL and add it to README.md, CITATION.cff, and the ACR abstract.
```

## Backup / mirror

- Before ACR submission, mirror the integrated XML on Zenodo for a citable DOI.
- Tag the repo `acr2026-submission` and link the Zenodo record from CITATION.cff.

## Known gotchas

- MINERVA strict mode rejects SBML files with duplicate species IDs after submap merge — run a dedupe check in week 12 before uploading.
- Submap colour palette must be colour-blind-friendly; the four colours above are from ColorBrewer Set1 / Set2 and have been chosen for distinguishability.
