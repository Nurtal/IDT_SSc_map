# Tickets — npj submission plan

26 tickets across the five lots of `docs/planning/npj_submission_plan.md`, staged here for
publication to GitHub Issues. One directory per lot, one file per ticket. A ticket's key is its lot
plus its file index (`L2/05-…md` is `L2-T5`); blocking edges are `{{L2-T5}}` placeholders in the body,
resolved to real issue numbers at publication time.

## Publish

```bash
python3 docs/planning/specs/tickets/publish.py --dry-run   # check the order first
python3 docs/planning/specs/tickets/publish.py             # create all 26
```

Needs `gh` installed and authenticated — it is absent from the planning machine, which is why these
are files rather than issues. Issues are created in topological order, so every placeholder resolves.
`--lot L1 L3` restricts the run; `--parent <n>` links the tickets to a published spec issue.

## Dependency graph

```
L1-T1 guard: untrue claims ─┬─ L1-T2 rename + banners
                            ├─ L1-T3 purge project docs ─┐
                            └─ L1-T4 purge manuscript ───┴─ L1-T5 requalify + Limitations ─┐
                                                                            │              │
L2-T1 freeze gene sets ─┬─ L2-T2 validation core (M5 golden master) ─┬─ L2-T5 bulk replication ─┐
                        │                                            └─ L2-T6 genetic support ──┤
                        ├─ L2-T3 community concordance re-run ───────────────────────────┐      │
                        ├─ L2-T4 cohort screening ── (blocks L2-T5)                      │      │
                        └─ L2-T7 OpenTargets coverage ───────────────────────────────────┤      │
                                                                                         │      │
L3-T1 unsourced reactions ─┬─ L3-T3 rebuild db + deck ─────────────────────────────┐     │      │
L3-T2 deciding sentences ──┘                                                       │     │      │
                                                                                   │     │      │
L4-T1 guard: stale numbers ─┬─ L4-T2 provenance + QC method ──┐                    │     │      │
                            ├─ L4-T3 M5 section ──────────────┤                    │     │      │
                            └─ L4-T4 independent validations ←─────────────────────┴─────┘      │
                                              │                                                 │
                            L1-T5 → L4-T5 Limitations                    L2-T5,T6 → L4-T7 figures
                                              │                                                 │
                      L4-T2,T3,T4 → L4-T6 abstract ─────────────────────────────────────────────┤
                                                                                                 │
                                              L5-T1 clean-checkout pass ←───────────────────────┘
                                              └─ L5-T2 metadata ─ L5-T3 tag + DOI ─ L5-T4 package
```

**Frontier at the start** — five tickets with no blockers, workable in parallel:
`L1-T1`, `L2-T1`, `L3-T1`, `L3-T2`, `L4-T1`.

**Critical path**: `L2-T1 → L2-T2 → L2-T5 → L4-T4 → L4-T6 → L5-T1 → L5-T2 → L5-T3 → L5-T4`.

## Conventions

- Both guards (`L1-T1`, `L4-T1`) ship **before** the work they check, carrying an allowlist of what is
  dirty today. Each cleanup ticket shrinks it; `L1-T5` is not done until it is empty.
- Second-tier analyses are deliberately absent: they are sacrificeable at the ceiling and have no
  tickets.
- Evidential rules live in `docs/planning/external_validation_prespec.md`. Where a ticket appears to
  disagree with it about a threshold, a direction or a decision rule, the pre-specification wins.
