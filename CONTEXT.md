# CONTEXT — SSc-MIM glossary

> The project's shared vocabulary. Glossary only: no status, no plan, no implementation detail.
> Status lives in `STATUS.md`, the plan in `docs/planning/npj_submission_plan.md`.
>
> Several terms below exist *because* the same word was previously used for different things and
> produced an overstated claim. Where that happened, the entry says so.

## The resource

**SSc-MIM** — the resource as a whole: the curated map, its annotations, the analyses derived from
it, and the code that reproduces them. Not a synonym for the SBML file.

**The map** — `curation/celldesigner/SSc_MIM_integrated.xml`. The SBGN-PD, CellDesigner-authored,
libSBML-validated model. One file, one source of truth for structure.

**Species** — a node of the map: a gene product, complex, small molecule, or phenotype. Distinct
from **HGNC symbol**: several species can share a symbol (isoforms, phospho-forms, complexes), and
some species have no symbol at all. Counts of species and counts of symbols are never
interchangeable.

**Reaction** — an edge of the map, as stored in SBML.

**Interaction** — a row of the reviewer-facing database (`analysis/curation/interaction_database.csv`).
Broader than *reaction*: it includes rows that are **not** in the map (see `discarded`). A count of
interactions is therefore never a count of reactions.

## Provenance layers

**Reactome backbone** — reactions imported from Reactome and harmonised. Not the project's original
contribution; it exists to give the curated layer somewhere to attach.

**SSc-curated layer** — the reactions hand-curated for this project (`curation/ssc_curated_reactions.tsv`).
**This is the original scientific contribution.** Whenever a reaction count is quoted, it must say
which of the two layers it refers to; conflating them was the source of an earlier overstatement.

**Tier-1** — an entity or reaction judged essential to SSc pathophysiology at scoping time, as
opposed to Tier-2 context. A curation priority, not an evidence level.

## Modules

**Module** — one of five expert-defined pathophysiological axes: M1 IFN-I, M2 TGF-β/fibrosis,
M3 EndoMT/vasculopathy, M4 cytokines, M5 B-cell/autoreactivity. A module is an **expert-defined
reading frame** — the Disease Maps convention — **not** a data-derived partition. It is the
operational unit of the project: overlay, scoring, external validation and drug mapping all happen
per module.

**Crosstalk** — a reaction whose reactant and product sit in different modules. Kept as an explicit
category because module boundaries are a curatorial choice, so the edges crossing them are the ones
most exposed to that choice.

**Community** — a group found by unsupervised community detection on the curated graph. A community
is *not* a module: it is computed, it carries no label, and because it runs on the curated graph it
partly reflects curation density. Community↔module agreement is an **internal consistency check**,
never independent proof.

**Reaction ID prefix ≠ module.** Reaction IDs were minted before the 2026-06-25 M4→M4+M5 split and
were not renumbered: `ssc_M4_011` belongs to module M5. The `module` column is authoritative; the ID
is an opaque stable key.

**Phenotype endpoint (sink)** — a terminal node standing for a biological or clinical outcome
(myofibroblast activation, ECM deposition, vascular remodelling, ISG signature, autoantibody
production, skin severity). Sinks are definitional, not mechanistic: they aggregate, they do not
react.

## Evidence

**ECO code** — the evidence class behind a reaction. The distinction that matters:
`ECO:0000305` is **curator inference** (a reasoned assertion, no direct experiment); `ECO:0000270`
and `ECO:0000314` denote reported or direct assay. A reaction with a PMID is not thereby
experimentally supported — the ECO code says what the PMID actually shows.

**Curator inference** — a reaction asserted on reasoning rather than a specific experiment. Legitimate
and declared, never disguised. A reaction with no source in existence keeps its inference status
rather than acquiring an invented citation.

**Deciding sentence** — the single verbatim sentence from the cited article that supports the
reaction, mined from PDF, PMC full text, or abstract. It is a *proposal for a human to confirm*, not
an adjudication.

**Reaction↔PMID concordance** — the property that a reaction's cited PMID points to an article that
is actually about that reaction. Distinct from evidence strength: a citation can be perfectly
concordant and still be weak evidence, and a strong claim can carry a citation to an unrelated paper.
Auditing the two separately is what surfaced the wrong-citation problem.

**AI verdict** — an advisory call (`validate` / `revise` / `caution` / `reject`) produced by reading
the deciding quote and the retrieved abstracts. **Advisory only.** It is a documented QC layer; it is
not review, not ratification, and it does not make the map expert-validated.

**Ratification** — a named human expert accepting a reaction into the map. **No reaction is ratified
to date.** "Expert-curated" and "community-curated" must not be used of this resource until that
changes.

## Curation lifecycle

**Candidate edge** — a proposed reaction living in `curation/staging/`. Never in the map.

**Gates G0–G4** — the automated checks a candidate must clear: schema, HGNC resolution, **verbatim
grounding of the supporting quote in the real article text (G2)**, novelty against existing and
Reactome edges, and evidence/citation resolvability. G2 is the anti-fabrication guarantee: an edge
cannot exist unless it carries a quote provably present in the cited article.

**Promotion** — moving a candidate that cleared the gates into the curated layer.

**`in_map` / `discarded` / `excluded`** — a row of the interaction database that is, respectively:
in the curated layer; considered and kept out, with a reason; or filtered before consideration.
`discarded` rows ship to reviewers deliberately, so a reviewer can overturn the exclusion.

**Reviewer deck** — the offline swipe app (`review/index.html`). A **mechanism offered** for
adjudication, not a step performed. Sending it is not the same as receiving decisions.

## Omics

**Overlay** — projection of transcriptomic signal onto map species, per (dataset, cluster).
Descriptive; it colours the map, it does not test it.

**Coverage** — the fraction of RNA-seq-detectable HGNC symbols in the map that are differentially
expressed somewhere in the overlay. Always quote it with its threshold: the **robust** figure is
effect-size-gated, the **permissive** figure is the upper bound. The gap between them is statistical
power, not biology, and neither number is a validation of anything.

**Module score** — a per-donor activation score for a module. Must be computed sign-blind (AUCell or
an independent Z-score): deriving both the gene selection and the score sign from the same SSc-vs-HC
contrast is circular, and an earlier version of this project inflated an effect ~5× that way.

**Donor** — the unit of statistical replication. Cells are not replicates; pseudobulk-per-donor is
what makes a contrast legitimate.

## Validation — five distinct things

The word alone is banned in this project; one of these five is always meant.

1. **SBML validation** — the file is syntactically and structurally valid (libSBML, enforced in CI).
   Says nothing about biology.
2. **Citation-integrity QC** — automated checks that citations resolve and concord with their claims.
   Says nothing about whether the biology is right.
3. **Corroboration** — map content is consistent with transcriptomic signal (coverage, overlay).
   Descriptive and non-inferential: the map was not built from these data, but agreement with them is
   weak evidence. **Never call this validation.**
4. **External validation** — a pre-specified hypothesis about the map is tested on a cohort that
   played no part in building it, with a stated threshold and a possible negative result. This is the
   only sense in which the map is *validated*. Currently true of module M5 only.
5. **Expert validation** — a named domain expert ratifies content. **Has not happened.**

**Independent** qualifies the *evidence source*, not the analyst: a validation is independent when the
data or knowledge base was produced without reference to this map. It does not mean "run by someone
else".

## Pre-submission review

**Simulated pre-submission review** — the internal critical read of 2026-05-20 (`presubmission_review/`):
three reviewer personae and an editor synthesis, all generated internally, **before any journal
submission**. The manuscript has never been submitted to any journal and has never been peer
reviewed. "Reviewer", "editor", "revision" and "E-item" refer to this internal exercise **only**, and
any document using them must say so on the same page.

**E-item** — one action item derived from that internal exercise. Not a journal requirement.
