# Guard against stale headline numbers

## What to build

Every headline figure quoted in the manuscript, the README, the status snapshot and the deck is
checked against the artefact it came from, and a divergence fails the build.

This repository has been bitten three separate times by numbers that drifted out of sync — a coverage
figure, an overlay count, a card count — each caught by chance during a reading pass. This makes it a
build failure instead.

## Acceptance criteria

- [ ] Headline figures are extracted from the manuscript, README, status snapshot and deck, and compared against the committed analysis artefacts
- [ ] A divergence exits non-zero naming the number, the document that quotes it and the artefact that contradicts it
- [ ] Historical baselines quoted deliberately as history are exempted by explicit rule, not by loose matching
- [ ] Verified to fail on a seeded stale number and pass on the current tree
- [ ] Wired into the lint target and running in CI

## Blocked by

None (can start immediately)
