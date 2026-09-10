# Replicate the modules in the independent bulk cohorts

## What to build

The headline result: each module's SSc-versus-healthy activation is tested in cohorts that contributed
nothing to building the map, and the outcome is reported whatever it is.

Every testable pair is reported with its effect size and arm sizes, so a null result can be told apart
from an underpowered one. Registered predictions appear next to outcomes, so a reader can see what was
expected before it was known. Some of those predictions are expected to be wrong.

## Acceptance criteria

- [ ] Every testable (module x cohort) pair is reported with direction, effect size, n per arm, raw and adjusted p, and verdict — including failures and contradictions
- [ ] Adjustment is applied over the family declared at screening, and the family composition travels with the results
- [ ] Scores are computed from module membership alone; the SSc-versus-healthy contrast plays no part in constructing the score, in this cohort or any other
- [ ] Both the rank-based primary score and the z-score sensitivity analysis are emitted
- [ ] The fibrosis module's reference direction is taken from the fibroblast-restricted comparison, not the whole-tissue one
- [ ] Registered predictions are reproduced alongside the outcomes
- [ ] A module meeting the criteria in some but not all cohorts is labelled partial, not replicated
- [ ] A significant result in the direction opposite the reference is reported as a contradiction in its own category
- [ ] Results are written as a structured file that figures and the numeric-coherence guard can consume; no downstream consumer re-derives a number
- [ ] The analysis runs through a named, idempotent build target and needs no raw single-cell archives

## Blocked by

- {{T2}}
- {{T4}}
