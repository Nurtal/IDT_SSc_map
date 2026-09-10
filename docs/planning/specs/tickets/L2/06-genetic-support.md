# Test genetic support for the module structure

## What to build

The module structure is examined by an axis of evidence that cannot be a consequence of disease state:
germline association. This is the sharpest falsifiable claim in the lot — enrichment is predicted for
the immune modules and predicted absent for the effector ones, so a uniform result falsifies it.

Because the curated layer was built from SSc literature and some of that literature is genetic, the
overlap is not fully independent. That caveat is carried in the output itself, not left to the prose.

## Acceptance criteria

- [ ] Per-module enrichment of genome-wide-significant SSc associations is computed, with adjustment across the five modules
- [ ] The test is run against the protein-coding universe and, separately, against the within-map control universe, so enrichment cannot be explained purely by the map being made of well-studied immune genes
- [ ] The overlapping genes are listed per module, so a reader can judge the enrichment directly rather than trusting a p-value
- [ ] The resolved trait identifier and the download date are recorded in the output, so the query can be repeated against the same snapshot
- [ ] The partial non-independence of literature-derived gene-disease sources is stated in the output itself
- [ ] The secondary, broader source is reported separately from the primary one and never merged into it
- [ ] Registered predictions are reproduced alongside the outcomes
- [ ] The result record uses the same shape as every other analysis in the lot
- [ ] The analysis runs through a named, idempotent build target

## Blocked by

- {{L2-T2}}
