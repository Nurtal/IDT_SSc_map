# Historical roadmap — SSc-MIM (pre-2026-05-20)

> Archived from the README at the start of the npj-SBA revision-v1.1
> sprint cycle (2026-05-21). Preserved for provenance: this is what
> the project plan looked like when scoping started in May 2026,
> before the GitHub-+-Zenodo-first delivery pivot of 2026-05-16 and
> the npj-Systems-Biology-and-Applications submission decision.

## Original target deliverable

- **Late-breaking abstract** — ACR Convergence 2026 (Orlando, 6–11 Nov 2026).
- **Submission deadline:** 22 September 2026, 12:00 ET.
- **Backup deliverable:** methodological paper for *Frontiers in Bioinformatics* or *npj Systems Biology and Applications*.

## Original timeline (18-week plan, 15 May → 22 Sep 2026)

### Phase 1 — Scoping and groundwork (weeks 1–3 · 15 May → 5 Jun)

- Validate scope with 1–2 SSc clinical experts (co-authorship locked).
- Build the core bibliography (~50 key reviews + ~100 primary papers).
- Install stack (CellDesigner, local MINERVA, CaSQ).
- Final decision on the omics dataset (Tabib scRNAseq, Whitfield bulk, or both).

### Phase 2 — Module curation (weeks 4–11 · 6 Jun → 31 Jul)

| Weeks | Module | Target species | Strategy |
|-------|--------|----------------|----------|
| 4–5 | M1 IFN-I | ~60 | Reactome import + SSc-specific curation |
| 6–7 | M2 TGF-β / fibrosis | ~80 | Reactome + RA-map import + SSc-specific curation |
| 8–9 | M3 EndoMT / vasculopathy | ~60 | Mostly manual (no strong upstream source) |
| 10–11 | M4 IL-6 / Th2 / B cells | ~50 | RA-map import + SSc adaptation |

### Phase 3 — Integration and deployment (weeks 12–14 · 1 Aug → 21 Aug)

- Inter-module SSc-specific crosstalk (critical step).
- One round of expert review (~1 week of expert time, planned in advance).
- MINERVA deployment, semantic-zoom check.
- Cytoscape network analyses (hubs, communities vs manually defined modules).

### Phase 4 — Use case and figures (weeks 15–17 · 22 Aug → 11 Sep)

- scRNAseq (or bulk) overlay on the MIM.
- Perturbed hubs, per-patient / per-subset scoring.
- DGIdb / Open Targets prioritisation.
- Three abstract figures: global MIM, overlay, target table.

### Phase 5 — Writing and submission (weeks 18+ · 12 Sep → 22 Sep)

- ACR late-breaking abstract (300 words + 1–2 figures), 5–7 days of co-author iteration.
- Submission on or before 22 September 2026, 12:00 ET.

## Original go / no-go decision points

- **End of week 7 (24 Jul).** If M1 + M2 are not finished, downgrade the scope to three modules or push the target to EULAR 2027 plus the methodological paper alone.
- **End of week 14 (21 Aug).** If expert validation has not happened, submit anyway with a "preliminary" framing in the abstract.

## Original roles and resources estimate

- **One lead curator at 0.8–1.0 FTE over four months** — typically a bioinformatics post-doc or third-year PhD student. Without this, the timeline did not hold.
- **One referent SSc rheumatologist** (~10% of time, for validation and co-authorship) — ideally a member of an established SSc study group (EULAR, SCTC, …).
- **One bioinformatician** for the omics overlay (~0.3 FTE during the last two months).
- **MINERVA access** (free) and modest compute (a laptop is enough unless re-running scRNAseq from raw counts).

## Original risk register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Curation slower than planned | high | Weekly quotas, progressive scope downgrade, curator / expert rotation |
| Import incompatibilities (Reactome → CellDesigner) | medium | Test the Reactome import on one pathway in week 1 |
| Late expert validation | medium | Lock the rheumatologist at project start; book three 1-hour meetings in advance |
| Lack of "wow factor" for an ACR clinician reviewer | medium | Invest heavily in the overlay figure and drug-target table |
| Still "preliminary" at submission | low–medium | The late-breaking track accepts ongoing work, but the overlay figure must be complete |

## Original fallback plan

- **Missed late-breaking ACR.** Aim for **EULAR 2027** (deadline typically end-January 2027) and publish the full version in *Frontiers in Bioinformatics* in the meantime.
- **Missed all of 2026.** Publish a principal paper in *npj Systems Biology and Applications* in mid-2027, then submit to ACR 2027 with an in-press paper as backing — substantially higher acceptance odds.

## What actually happened (2026-05-16 pivot)

The "rheumatologist co-author" and "MINERVA Luxembourg curator role" blockers were dissolved by a single decision on 2026-05-16: deliver v1.0 as a **GitHub + Zenodo DOI** release first (with the locked-in collaborator as co-author), and treat MINERVA deployment as a post-publication stretch goal. This freed the manuscript track to run on its own clock and brought the *Frontiers Bioinformatics* / *npj SBA* paper to the front of the queue. Phase 4 (Tabib + 3 multi-tissue overlays) and Phase 4c (Gur 2022 skin multiome) completed on the AUTO lane between 2026-05-17 and 2026-05-19, and the simulated peer-review run on 2026-05-20 framed the work as a **npj-SBA major-revision** task to be closed by 2026-09-30. See `reviewing/REVISION_ROADMAP.md` and `reviewing/PROGRESS.md` for the current cycle.
