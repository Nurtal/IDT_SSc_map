# Freeze the module gene sets and tag the baseline

## What to build

The curator can see, in one committed artefact, exactly which HGNC symbols constitute each of the five
modules at the moment validation begins: which of them are RNA-seq-detectable, how far the modules
overlap one another, and which modules are too small to test at all. From this point on, nothing
downstream re-derives module membership — every later analysis reads this artefact.

This exists so that gene membership cannot be adjusted after a result is seen. It is the prefactor for
the whole lot.

## Acceptance criteria

- [ ] Module membership is read from the curated layer's `module` column, never from a reaction's ID prefix — a reaction whose ID still carries a pre-split prefix is counted in the module its column names
- [ ] The artefact lists, per module, each HGNC symbol with its RNA-seq-detectability flag
- [ ] Inter-module overlap is reported: pairwise overlap counts and the symbols belonging to more than one module
- [ ] Modules below the minimum-size floor are flagged not-testable, and the floor itself is recorded in the artefact rather than left implicit
- [ ] Per-module symbol counts reconcile with the curated layer; a mismatch fails the build rather than being merely reported
- [ ] A baseline tag marks the map state the artefact was built from
- [ ] The build target is idempotent: re-running against an unchanged map reproduces identical output
- [ ] The artefact is committed

## Blocked by

None (can start immediately)
