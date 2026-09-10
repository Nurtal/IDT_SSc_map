# Complete the missing deciding sentences

## What to build

Thirty-two reviewer cards carry no verbatim deciding sentence, so a reviewer adjudicating them has the
curated mechanism text and nothing from the source article.

The mining path has a history: a defect once made most full-text quotes come from articles *citing*
the reference rather than the reference itself, and a cached copy of that output survived the first
fix. Both are repaired, but the property must be re-checked here rather than assumed.

## Acceptance criteria

- [ ] Deciding sentences are mined for as many of the thirty-two as have a usable source
- [ ] Every mined sentence is verified present in the **cited** article, not in an article citing it
- [ ] No cached text from a previous run can reintroduce a sentence from the wrong article
- [ ] The residue is listed with the reason each card could not be completed
- [ ] Card counts are updated wherever they are quoted

## Blocked by

None (can start immediately)
