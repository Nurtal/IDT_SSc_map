# Purge simulated-review vocabulary from the project documents

## What to build

The six documents a newcomer actually reads — the README, the status snapshot, the roadmap, the
changelog, the deck and the construction reference — currently assert that the manuscript went through
review at a journal. It did not.

The facts underneath are kept: the methodological work described really happened. Only the framing
changes, from journal revision to internal audit.

Four dated records carry the same vocabulary and are cleaned here too: the 2026-05-20 standup, the
archived BioModels submission draft, the historical roadmap and the v1.0 baseline README. They keep
their history; only the forbidden phrasings give way to the glossary's term, *simulated
pre-submission review*.

## Acceptance criteria

- [ ] The 26 occurrences across the six documents are rewritten as internal-audit statements
- [ ] The four dated records name the exercise as the simulated pre-submission review, their history otherwise untouched
- [ ] The specific assertions 'revision v1.1 merged', 'reviewer E-items closed' and 'reframed per editor' no longer appear in any form — the guard now enforces this <!-- claims-guard: mention -->
- [ ] No underlying fact is deleted: work that was really done is still described, with honest provenance
- [ ] No document states or implies that the manuscript was submitted to, or reviewed by, a journal
- [ ] Every allowlist entry naming this ticket is removed and the guard still passes

## Blocked by

- {{L1-T1}}
