# Rename the critique folder and banner every file in it

## What to build

A reader landing anywhere in the internally generated critique can tell, within the first lines, that
it is not a journal review. Today only that folder's own README says so, and its name — `revision` —
actively suggests otherwise, colliding with the separate reviewer app.

The folder is renamed to say what it is, every file carries a standing banner, and the references
elsewhere follow.

## Acceptance criteria

- [ ] The folder name states that this is a pre-submission internal critique, and no longer collides with the reviewer app's name
- [ ] Every file in it carries, within its first lines: internally generated, not a journal review, and the manuscript has never been submitted
- [ ] Non-journal references to the old location are updated; the historical journal is left untouched as a record
- [ ] No internal link is broken by the move
- [ ] The allowlist entries for these files are removed and the guard still passes

## Blocked by

- {{L1-T1}}
