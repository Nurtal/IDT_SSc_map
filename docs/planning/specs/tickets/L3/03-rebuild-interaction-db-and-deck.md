# Rebuild the interaction database and the reviewer deck

## What to build

The reviewer-facing database and the offline deck reflect the curation as it now stands, and the deck
remains safe to send to someone outside the project.

## Acceptance criteria

- [ ] The deck's interaction count reconciles with the curated source table, or the new figure is justified
- [ ] No local filesystem path appears in the shipped file
- [ ] The negative-control candidate remains absent from the deck
- [ ] Deduplication identity excludes the citation, so correcting a PMID cannot resurface a staged duplicate
- [ ] Advisory verdict counts reconcile with the verdict file

## Blocked by

- {{L3-T1}}
- {{L3-T2}}
