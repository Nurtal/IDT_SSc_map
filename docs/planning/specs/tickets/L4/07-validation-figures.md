# Render the validation figures from committed results

## What to build

The figures reporting module concordance and the independent validations, generated from result files
rather than from values typed into a script.

A published figure in this project once carried numbers hard-coded into its renderer, decoupled from
the analysis that produced them. Every figure here reads its inputs.

## Acceptance criteria

- [ ] The module-to-community concordance panel is regenerated from the re-run enrichment output
- [ ] A figure reports the independent validation results, reading them from the committed result files
- [ ] No numeric value is hard-coded in any renderer
- [ ] Figures regenerate identically from a clean checkout with no manual step

## Blocked by

- {{L2-T5}}
- {{L2-T6}}
