# Reviewing — npj Systems Biology and Applications submission

> Simulated peer-review run for the manuscript draft
> `manuscript/SSc_MIM_manuscript_draft.md` (v0.1, 2026-05-19).
> Generated 2026-05-20, prior to first journal submission.

## Target journal

**npj Systems Biology and Applications** (Nature Portfolio).
Article type: **Research Article** (formerly "Article").
Scope match: SBGN-compliant Molecular Interaction Maps, mechanistic
disease modelling, multi-omics integration, drug repurposing.
Reference precedent in scope: Mazein et al. *npj Syst Biol Appl* 2018
(Disease Maps Project methodology paper).

## Files in this run

| File | Purpose |
|------|---------|
| `R1_systems_biology.md` | Reviewer 1 — disease maps / SBGN / network analysis expertise |
| `R2_scRNAseq_clinical.md` | Reviewer 2 — single-cell transcriptomics / SSc clinical expertise |
| `R3_reproducibility.md` | Reviewer 3 — computational reproducibility / FAIR data / software |
| `editor_decision.md` | Editor synthesis + recommended decision + essential revisions |
| `revision_plan.md` | Author-side mapping of each comment to an actionable revision item |
| `REVISION_ROADMAP.md` | Detailed sprint-structured execution plan (7 sprints, 5 tracks, 9 gates) |

## How this review was generated

- Source artefacts consulted: `manuscript/SSc_MIM_manuscript_draft.md`,
  `STATUS.md`, `ROADMAP.md`, `journal.md`, `curation/ssc_curated_reactions.tsv`,
  `curation/annotations/*.tsv`, `analysis/network/summary.json`,
  `analysis/overlay/druggable_hubs.tsv`,
  `analysis/overlay/patient_module_scores_multi.tsv`, figures F1–F3.
- Reviewers are simulated personae with non-overlapping expertise,
  asked to focus on the npj-SBA criteria: novelty, methodological rigour,
  reproducibility, biological/mechanistic value, computational
  contribution.
- The editor synthesis weighs the three reviews into a single
  recommendation that the lead author can act on.

## Decision summary (preview)

**Recommendation: Major revision.**
The work is original (no curated SBGN MIM exists for SSc) and matches
the journal scope. The main weaknesses to address before acceptance are
(i) statistical formalisation of the cross-module crosstalk claims,
(ii) clearer quantification of novelty relative to existing pathway
resources, (iii) external validation of at least one drug-target
prediction, (iv) MINERVA / BioModels deposit so that the resource is
not GitHub-only, and (v) more explicit treatment of the M3/EndoMT
coverage gap. See `editor_decision.md` for the full list.
