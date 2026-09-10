# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

**This is a single-context repo.** There is no `CONTEXT-MAP.md` and no per-package context.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root: the project glossary.
- **`docs/decisions/`**: the architecture decision records. Read the ones that touch the area you're
  about to work in.

> **Note on location.** The skills' default convention is `docs/adr/`. This repo used
> `docs/decisions/` before the skills were set up, and keeps it. There is no `docs/adr/`; don't create
> one.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest
creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and
`/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

```
/
├── CONTEXT.md
├── docs/
│   └── decisions/
│       └── 2026-05-15_reactome_import.md
├── curation/          ← the map and its curated layer
├── analysis/          ← derived results
└── scripts/           ← the pipeline
```

## ADR naming

`YYYY-MM-DD_slug.md`, matching the existing `2026-05-15_reactome_import.md` — **not** the
`0001-slug.md` numbering used in the skills' generic templates. New ADRs follow the existing file's
shape: Context · Outcome · Decision · Implications · Open items, with a `Status:` line in the header
block.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test
name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly
avoids.

This repo's glossary exists because several words were used for more than one thing and produced an
overstated claim. Three traps in particular:

- **"validation"** has five distinct senses (SBML / citation QC / corroboration / external / expert).
  Never write it unqualified.
- **"reaction" vs "interaction"** are different counts (133 vs 143). They are not interchangeable.
- **"module" vs "community"** — one is expert-defined, the other computed. A community is not
  evidence for a module.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language
the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts the 2026-05-15 Reactome-import decision, but worth reopening because…_
