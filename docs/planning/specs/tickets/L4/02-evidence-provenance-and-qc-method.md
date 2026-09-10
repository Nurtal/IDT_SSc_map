# Report curation provenance and the citation-QC pipeline as method

## What to build

The paper describes how the curated layer was built and how its citations were checked — and treats
the checking as a contribution rather than as housekeeping.

This is the strongest available substitute for the expert validation that will not happen: a
reproducible pipeline that found dozens of citations pointing at unrelated articles inside the
project's own map, and a policy that removed an edge's identifier rather than invent a replacement.
Nobody else in this ecosystem publishes that.

## Acceptance criteria

- [ ] A Results section reports curation and evidence provenance with the current evidence stratification
- [ ] Methods describes the gated candidate pipeline, the verbatim-grounding requirement, the advisory verdict layer and the reaction-to-citation concordance audit
- [ ] The measured yield is stated: the citations corrected across the successive sweeps, and the edge left uncited because no source exists
- [ ] The layer is explicitly described as automated quality control — not as review, and not as ratification
- [ ] Every number in the section passes the stale-number guard

## Blocked by

- {{L4-T1}}
