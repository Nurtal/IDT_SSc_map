# Screen and freeze the independent cohorts

## What to build

The curator has a verified, frozen list of independent cohorts before any of them is analysed, so that
cohort choice cannot be influenced by the answer a cohort gives.

Screening is a separate step with its own committed output, including the candidates that were
rejected and why. If too few cohorts survive, that is a supported outcome: the pipeline records a gap
and succeeds, rather than substituting a weaker analysis to fill the space.

## Acceptance criteria

- [ ] Candidates are screened against the pre-specification's written criteria, applied in the stated order
- [ ] The screening log is committed and includes rejected candidates with the criterion each failed
- [ ] Verified cohort accession, tissue, platform and per-arm sample counts are confirmed against the live source record, not assumed
- [ ] No verified cohort shares donors with the datasets already used for corroboration
- [ ] The verified list is frozen: a cohort cannot be dropped after its result is known
- [ ] Each verified cohort is registered in the data manifest with its checksum, so the existing provenance guard passes rather than failing the build
- [ ] The multiple-testing family is declared: which (module x cohort) pairs are testable, and which are excluded by the size floor
- [ ] If fewer than two cohorts survive screening, a gap record is emitted, the pipeline succeeds, and no substitute analysis is promoted into the validation claim

## Blocked by

- {{T1}}
