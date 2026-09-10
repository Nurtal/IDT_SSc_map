# Validation core, delivered through the M5 golden master

## What to build

Every validation analysis reaches its verdict through one shared core, so the rules registered in the
pre-specification are applied uniformly rather than re-implemented per analysis.

The core is delivered *through a real consumer*, not as a standalone library: the existing M5
blood-cohort validation is migrated onto it and must reproduce its published values. That migration is
what makes the core trustworthy — an already-audited result becomes a regression test with a known
expected answer.

The core owns sign-blind scoring, the multiple-testing family, and the replication decision. It knows
nothing about GEO, GWAS Catalog or OpenTargets; source-specific parsing stays in the adapters.

## Acceptance criteria

- [ ] The core provides: sign-blind scoring (rank-based primary, z-score sensitivity), a contrast test returning an effect size, family-wise adjustment over a declared family, and a replication decision returning one of four verdicts — replicated, partial, not replicated, contradicted
- [ ] The core performs no file I/O and contains no source-specific knowledge
- [ ] The result record carries module, source, direction, effect size, n per arm, raw p, adjusted p, testability flag, verdict, and the registered prediction it is compared against
- [ ] The M5 blood-cohort analysis runs on the core, retaining only its cohort parsing and its sub-signature decomposition
- [ ] Re-running the migrated M5 analysis reproduces its published module contrast and sub-signature values
- [ ] Unit tests plant a known effect and assert on the verdict reached, not on intermediate scores or output formatting
- [ ] A module carrying a planted effect in the direction opposite to its reference is reported as **contradicted** — not as replicated, and not merged into not-replicated
- [ ] A module with no planted signal is not called replicated
- [ ] A module below the size floor is excluded from the multiple-testing family
- [ ] The family composition is recorded in the output alongside the adjusted values
- [ ] Tests follow the repository's existing convention (import the script module, plant synthetic data, assert on public functions plus a CLI round-trip) and require neither network access nor the raw single-cell archives
- [ ] The golden-master test skips with a clear message when its cohort files are absent, rather than failing

## Blocked by

- {{L2-T1}}
