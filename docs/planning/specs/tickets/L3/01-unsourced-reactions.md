# Resolve the eight reactions carrying no primary citation

## What to build

Eight of the curated reactions carry no primary PMID. Each one ends this ticket either properly cited
or honestly declared as curator inference — and never in between.

The precedent is binding: when a targeted search found no paper in existence for one edge, its
identifier was removed rather than replaced with something approximate. Inventing a citation is worse
than declaring an inference.

## Acceptance criteria

- [ ] Each of the eight ends with either a verified primary PMID or an explicitly declared curator inference
- [ ] Verification is against the retrieved title and abstract, not merely that the identifier resolves
- [ ] No citation is invented, and no review is substituted for a primary source without saying so
- [ ] A claim with no source in existence keeps its inference status and loses its identifier
- [ ] The curator inference register reflects the outcome for all eight
- [ ] The evidence-depth lint passes

## Blocked by

None (can start immediately)
