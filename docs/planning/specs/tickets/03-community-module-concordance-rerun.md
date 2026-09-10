# Re-run the community-module concordance on the five-module map

## What to build

A number currently committed to the repository is wrong: the community-module enrichment predates the
M4-to-M5 split and still describes a module of a size that no longer exists. Any figure or sentence
drawn from it is wrong today.

This ticket is a correction, not an enhancement. It is the cheapest item in the lot — no new data, no
network — and its output must not be presented as independent evidence: community detection runs on
the curated graph, so it partly measures curation density.

## Acceptance criteria

- [ ] Community detection and hypergeometric community-module enrichment are re-run on the current five-module map
- [ ] The output contains M5 and no longer reports a module of a size that no longer exists
- [ ] Every emitted file, figure caption and referring sentence labels this an internal consistency check, not independent evidence
- [ ] Module membership agrees with the frozen gene-set artefact
- [ ] Documents and figures quoting the superseded enrichment numbers are updated, or flagged for the manuscript lot if they belong to it
- [ ] Runs without network access and without the raw single-cell archives

## Blocked by

- {{T1}}
