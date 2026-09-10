# Report target-knowledge-base coverage of the map

## What to build

Coverage of SSc-associated targets by the map, with an UpSet view, giving the comparator resource an
exact counterpart.

This is a coverage description, not a hypothesis test. It has no threshold, no pass or fail, and no
verdict, and it must be labelled corroboration in its own output so that a later reader cannot promote
it into an evidence claim. It is the one analysis in the lot that does not pass through the validation
core, because it has no decision to make.

## Acceptance criteria

- [ ] Coverage of SSc targets by map species is computed and reported
- [ ] An UpSet view is produced
- [ ] The output and its caption label the analysis corroboration, never validation
- [ ] The source version and download date are recorded in the output
- [ ] No verdict and no threshold is emitted
- [ ] The analysis runs through a named, idempotent build target

## Blocked by

- {{T1}}
