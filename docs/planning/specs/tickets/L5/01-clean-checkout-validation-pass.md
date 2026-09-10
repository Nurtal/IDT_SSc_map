# Pass every check on a clean checkout

## What to build

The gate. Everything the project asserts about itself is verified mechanically, from a fresh clone,
before anything is deposited or sent.

## Acceptance criteria

- [ ] SBML validation reports zero errors
- [ ] Every guard passes: data manifest, evidence depth, untrue-claims, stale-numbers
- [ ] The test suite passes
- [ ] The readiness check passes
- [ ] All of the above from a clean checkout, with no manual fix-ups

## Blocked by

- {{L1-T5}}
- {{L3-T3}}
- {{L4-T6}}
- {{L4-T7}}
