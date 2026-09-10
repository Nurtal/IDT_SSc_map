# Purge simulated-review vocabulary from the manuscript

## What to build

The manuscript reads in places as a revised version responding to reviewers. It is a first draft that
has never been submitted, and any reviewer receiving it would be misled by its own text.

Version numbering also leaves the prose: the repository is versioned, the manuscript is not.

## Acceptance criteria

- [ ] The 24 occurrences are addressed: no reviewer, revised-version, or per-the-editor phrasing survives
- [ ] Version numbering is removed from the manuscript text; version identity lives in the repository alone
- [ ] Sentences that described a genuine methodological improvement keep the improvement and lose the revision framing
- [ ] The allowlist entry for the manuscript is removed and the guard still passes

## Blocked by

- {{L1-T1}}
