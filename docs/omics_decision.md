# Decision — Omics dataset for the translational overlay

- **Date:** 2026-05-15 (entered early; revisable until end of Phase 1 / week 3, 5 Jun 2026)
- **Phase:** 1 (week 3)
- **Decider:** lead curator, pending sign-off by bioinformatician + clinical referent at the kickoff meeting
- **Status:** **draft — primary path chosen, reserve path documented**

## Why this decision matters

The overlay (Phase 4) is the abstract's clinical "wow factor" (risk R4). It must be (a) feasible inside Phase 4 (weeks 15–17), (b) cell-type-resolved enough for fibroblast-subset stratification, and (c) generate a clinician-readable figure F2.

## Options compared

| Criterion | **Tabib 2021 scRNAseq (primary)** | **Whitfield / GENISOS / PRESS bulk (reserve)** |
|-----------|-----------------------------------|-----------------------------------------------|
| GEO accession | GSE138669 (and successor scRNAseq datasets) | GSE58095, GSE45485, and equivalents |
| Sample size | 12 SSc + 10 HC skin biopsies (≈ 50k cells) | 200+ SSc + HC bulk biopsies across cohorts |
| Cell-type resolution | yes — fibroblast subsets (SFRP2⁺/PRSS23⁺), myofibroblasts, ECs | no — only intrinsic subset (inflammatory / fibroproliferative / normal-like) |
| Public availability | open on GEO | open on GEO |
| Pre-processed h5ad | available via published companion code | reprocess from CEL files / raw counts |
| Time-to-figure | 2–3 weeks in Phase 4 with stubs already in place | 1–2 weeks (simpler data) |
| Novelty for ACR | high — first MIM overlay at single-cell resolution in SSc skin | moderate — Whitfield subsets are 10+ years old |
| Clinical readability | medium — needs careful figure work (F2 is the lift) | high — patients already mapped to subsets |
| Drug-target story | strong — subset-specific druggable hubs | strong — subset-specific druggable hubs |

## Decision

**Primary path: Tabib 2021 scRNAseq (GSE138669).**

Rationale:
1. **Novelty.** A single-cell × disease-map overlay in SSc skin is a first; aligns with the abstract's competitive framing.
2. **Resolution.** SFRP2⁺ / PRSS23⁺ fibroblast subsets and myofibroblasts are exactly the actors that modules M2 + M3 model — cell-type-specific projections will read more directly on the figure.
3. **Feasibility.** The dataset is small enough to process on a single workstation (~50k cells, no batch-correction nightmares). Pre-processed AnnData is published.
4. **Stub infrastructure ready.** Six notebooks already scaffolded under `analysis/overlay/tabib_scRNAseq/` (commit `a23c8bd`).

**Reserve path: Whitfield / GENISOS / PRESS bulk (GSE58095, GSE45485).**

When to switch to reserve:
- If by end of week 16 (4 Sep) the per-cluster DEG step has not produced clean subset-specific signal, or
- If the QC pass loses too many cells (< 30k post-filter), or
- If the bioinformatician's availability shifts below 0.3 FTE during weeks 15–17.

**Complementary use of both.** Even on the primary path, project the Whitfield intrinsic subsets onto the MIM as a sanity check that the four modules' activation scores recapitulate the known intrinsic subset structure (inflammatory ↔ M1 / M4, fibroproliferative ↔ M2). This is a 1-day addition in week 16 and strengthens the abstract narrative.

## Implications

- Phase 4 scaffolding stays as-is.
- Add a stub notebook for the Whitfield comparison: `analysis/overlay/whitfield_bulk/01_intrinsic_subsets.ipynb` (to be added before Phase 4).
- Risk R4 mitigation strengthened: F2 figure now has two complementary panels (scRNAseq subset overlay + Whitfield intrinsic subset overlay).

## Open

- [ ] Confirm with clinical referent that the Tabib cohort metadata includes mRSS / disease duration / autoAb status. If not, fall back to score-vs-cluster comparisons only.
- [ ] Confirm bioinformatician availability for weeks 15–17.
- [ ] Sign-off at the kickoff meeting (Phase 1 / week 1).
