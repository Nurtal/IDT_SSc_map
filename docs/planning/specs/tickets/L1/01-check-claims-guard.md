# Guard against untrue claims about the project's review status

## What to build

The build fails when a document claims something untrue about how this work has been reviewed. Until
now the only thing preventing "npj-SBA revision merged" or "expert-curated" from reappearing was
someone noticing.

The guard ships **before** the cleanup it enforces, carrying an explicit allowlist of the files that
are dirty today. CI is therefore green from the first commit, and each cleanup ticket shrinks the
allowlist. Progress becomes mechanically visible rather than a matter of proofreading — and the final
cleanup ticket is not done until the allowlist is empty.

## Acceptance criteria

- [ ] Forbidden phrasings are detected case-insensitively: peer review / peer-reviewed, expert-validated, expert-curated, community-curated, as requested by the reviewer or editor, major revision
- [ ] The guard reports the file, the line and the matched phrase, so a violation is actionable without searching
- [ ] The internally generated critique folder and the historical journal are exempt **by documented rule**, not by silent omission
- [ ] Files that are dirty today are listed in an explicit allowlist, each entry naming the ticket that will remove it
- [ ] Verified to exit non-zero on a seeded violation and zero on the current tree
- [ ] Wired into the lint target and running as its own CI job
- [ ] The allowlist is documented as temporary, with the rule that it must be empty before submission

## Blocked by

None (can start immediately)
