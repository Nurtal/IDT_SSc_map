# Co-author kickoff — npj-SBA revision

**Date proposed**: week of 2026-05-25 (Sprint S0, before S1 starts
on 2026-05-28).
**Duration**: 60 min.
**Format**: video call + shared screen on the revision artefacts.
**Attendees**: lead curator (N. Foulquier), co-author (TBC).

---

## Why this meeting

The npj-SBA peer-review run returned a **Major Revision** with
non-trivial methodological work (statistical re-analysis +
clinical validation + FAIR deposition). Before committing nine
weeks of curator effort to the revision plan, we need explicit
co-author sign-off on (i) the scope, (ii) the descoping decisions,
and (iii) the dates that need their bandwidth.

---

## Agenda (60 min)

### 1. Context (5 min)

- Where we are: v1.0 submission package frozen at git tag
  `v1.0-pre-review` (commit `e638a4d`, 2026-05-20). Three
  simulated reviewers (R1 systems biology / R2 scRNA-seq+clinical
  / R3 reproducibility) all converge on **Major Revision**.
- Editor synthesis: 5 themes, 25 essential revision items
  (E1–E25), 18-week window. See
  `reviewing/editor_decision.md`.

### 2. The five revision themes (15 min)

Walk through one slide / paragraph per theme:

- **Theme A — Statistical formalisation** (E1–E4, E13)
  - DEG re-run with mixed-effects + FDR (will likely drop MIM
    coverage from 50 % to ~35–42 %).
  - AUCell scoring replaces sign-weighted score (removes the
    double-dipping concern).
  - Hub-score robustness check via eigenvector / PageRank.
  - Hypergeometric tests for community–module enrichment.

- **Theme B — External validation** (E5, E6, E7, E12)
  - mRSS correlation with M1/M2 scores in Tabib donors
    (highest-leverage clinical item).
  - Table 2 recalibration vs actual SSc trial outcomes
    (focuSSced negative, fresolimumab discontinued, RECITAL
    ambiguous, brontictuzumab GI tox).

- **Theme C — FAIR deposition** (E11, E14–E17)
  - MINERVA *or* BioModels deposit before submission.
  - Docker image, Zenodo input-data mirror, CI for figures,
    RO-Crate manifest.

- **Theme D — Module-specific deepening** (E8, E9)
  - M3 / EndoMT — within-vascular-subset scoring on Gur 2022
    pericyte / vascular clusters.
  - CellTypist / Azimuth harmonisation across the four datasets.

- **Theme E — Boolean / mechanistic modelling** (E10)
  - Either run CaSQ + MaBoSS perturbation matrix, or soften
    §4.5 to a v2.0 deliverable. **Descope candidate.**

### 3. Descoping decisions — explicit sign-off needed (10 min)

These are the two items I propose to **descope** to a v2.0
follow-up if we are behind schedule, in order to protect the
critical-path items. Need co-author agreement:

| ID | Item | Proposed action | Co-author OK? |
|----|------|------------------|---------------|
| E10 | CaSQ Boolean inference + perturbation matrix | Descope to v2.0; rewrite §4.5 as "future direction" | ☐ |
| E18 (partial) | Mahoney 2015 / Taroni edge-file novelty comparison | Restrict to Reactome/KEGG only if edges not retrievable in 2 days | ☐ |

If both are descoped, the manuscript narrative needs to be
softened in three places (abstract, §4.3, §4.5). I will send a
red-line diff before S7.

### 4. Sprint plan (10 min)

Walk through `reviewing/REVISION_ROADMAP.md`:

- 7 sprints × 2 weeks + 3-week write-up = 17 weeks of work.
- Target submission: 2026-09-30.
- Critical gates at end of each sprint.

### 5. Co-author bandwidth — slots to lock now (15 min)

I need to put these on your calendar **today**:

| When | What | Duration | Why |
|------|------|----------|-----|
| **S5 (week of 2026-07-27)** | Table 2 drug-target sign-off | 2 h | Co-author owns the clinical-trial accuracy of the drug table |
| **WR session 1 (week of 2026-09-07)** | Read v1.1 draft + comment | 4 h reading + 1 h call | First polish round |
| **WR session 2 (week of 2026-09-21)** | Sign off final draft + point-by-point | 1 h | Submission readiness |

Optional but useful:
- **S3 (week of 2026-06-29)** — 30 min to discuss any mRSS
  metadata complications, and decide whether to reach out to
  the Tabib lab.

### 6. Risk register (5 min)

Top 3 risks I want you to be aware of:

- **RR1** — FDR re-analysis could drop M3/M4 coverage to ~15 %.
  Plan: pre-emptively soften the narrative; M1 and M2 are the
  load-bearing modules anyway.
- **RR2** — mRSS may not be in any GEO metadata file. Plan:
  email Tabib lab on first day of S3; fallback to disease
  duration as a continuous covariate.
- **RR3** — MINERVA curator-role grant could slip. Plan: pursue
  BioModels in parallel from S6 day 1.

---

## Decisions to record from the call

- [ ] D1 — Revision scope: accept the E1–E13 critical-path items?
  *(Yes / No / Modify)*
- [ ] D2 — Descope E10 (CaSQ) to v2.0? *(Yes / No / Decide at S5)*
- [ ] D3 — Descope E18 partial (Mahoney/Taroni) to v2.0?
  *(Yes / No / Decide at S7)*
- [ ] D4 — Co-author bandwidth — slots locked?
  *(Yes / Reschedule)*
- [ ] D5 — Authorship / contribution allocation for v1.1?
- [ ] D6 — Should we contact the Tabib lab for mRSS metadata?
  *(Yes / Use disease duration as proxy)*
- [ ] D7 — Are we OK with the 2026-09-30 submission target?

---

## Pre-read for the co-author (in priority order)

1. `reviewing/editor_decision.md` — 15 min read. The single most
   important file.
2. `reviewing/REVISION_ROADMAP.md` — 20 min skim. Sprint plan.
3. `reviewing/R1_systems_biology.md` and
   `reviewing/R2_scRNAseq_clinical.md` — 30 min total.
   R3 is software-flavoured and can be skipped.
4. `reviewing/PROGRESS.md` — 5 min. The dashboard we will track
   together.

---

## Outcome — to record after the call

(empty until the call happens)

- Decisions D1–D7 recorded above.
- Action items assigned with dates.
- Next sync: end of S1 (2026-06-10).

---

*Brief prepared 2026-05-20 by N. Foulquier.*
