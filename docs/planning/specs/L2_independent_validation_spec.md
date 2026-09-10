# Spec — L2: independent validation pipeline

> Scope: lot **L2** of `docs/planning/npj_submission_plan.md` (tasks L2-01 … L2-06).
> Governed by `docs/planning/external_validation_prespec.md` — that document holds the hypotheses,
> thresholds and decision rules; this spec builds the machinery that applies them.
> Vocabulary: `CONTEXT.md`. "Validation" below always means sense 4 — a pre-specified hypothesis
> tested on evidence that played no part in building the map.

## Problem Statement

The curator has a curated molecular interaction map of dcSSc skin fibrosis, organised into five
modules, and no way to say whether those modules are right.

Everything the project has done with omics so far is **corroboration**: the overlay projects
transcriptomic signal onto the map and reports agreement. Agreement was never at risk, because no
threshold existed whose failure would have been reported. The one genuine external validation —
module M5 against an independent blood cohort — exists as a single bespoke script covering one module
out of five.

Two things make this urgent rather than merely desirable. First, the intended human check will not
happen: the reviewer deck went out and nothing came back, so **no reaction in the map is ratified by
anyone**, and the resource cannot honestly be described as expert-curated. Second, the project has
already been burned by circularity — a module contrast reported as Δ≈+0.27 collapsed to +0.058 once
the score was made sign-blind, a fivefold inflation caused by using the same contrast to select genes
and to sign the score. Without machinery that enforces the decision rules, a well-meaning analysis
drifts back into confirming what it assumed.

Meanwhile a published number is currently wrong: the committed community↔module enrichment predates
the M4→M5 split and still describes a module that no longer exists.

## Solution

A validation pipeline that can fail, and that applies one set of pre-registered rules everywhere.

The curator freezes the module gene sets before seeing any new data, then runs each independent
evidence source — independent bulk cohorts, SSc genetic association, a target knowledge base — through
a **shared validation core**. The core owns the scoring, the multiple-testing family, and the
two-criterion replication rule, so no analysis can quietly apply its own thresholds. Every test is
emitted with its effect size and adjusted p-value whether it succeeds, fails, or contradicts the
registered prediction, and a module that fails to replicate is reported as a result rather than
dropped.

The existing M5 validation is re-expressed on top of the same core, which turns an already-audited
result into a regression test with a known expected value: if the core is wrong, the M5 numbers stop
reproducing.

## User Stories

1. As the lead curator, I want the module gene sets frozen and committed before any new cohort is downloaded, so that gene membership cannot be adjusted after seeing a result.
2. As the lead curator, I want the frozen baseline marked by a tag, so that anyone can reconstruct exactly which map state the validation was run against.
3. As the lead curator, I want each module's gene set derived from the curated layer's module column rather than from reaction ID prefixes, so that the M5 reactions still carrying an `ssc_M4_` prefix are counted in M5.
4. As the lead curator, I want inter-module gene overlap reported when the gene sets are built, so that I know how far the five modules are statistically independent of one another before I test them.
5. As the lead curator, I want a module with too few detectable symbols in a cohort's platform declared not testable up front, so that the exclusion is a rule rather than a judgement made after seeing the result.
6. As the lead curator, I want the set of not-testable module–cohort pairs excluded from the multiple-testing family, so that the correction is applied over the tests actually performed.
7. As the lead curator, I want candidate cohorts screened against written criteria before any is analysed, so that cohort choice cannot be influenced by the answer it gives.
8. As the lead curator, I want the screening log committed including the rejections and their reasons, so that a reader can see which cohorts were considered and why they were dropped.
9. As the lead curator, I want the verified cohort list frozen once screening is complete, so that a cohort cannot be removed after its result is known.
10. As the lead curator, I want every newly downloaded cohort registered in the data manifest with its checksum, so that the existing provenance guard keeps the build honest instead of failing it.
11. As the lead curator, I want module scores computed sign-blind from module membership alone, so that the circularity that inflated the v1.0 contrast fivefold cannot recur.
12. As the lead curator, I want a rank-based score as primary and a z-score as a pre-declared sensitivity analysis, so that the headline does not depend on one scoring choice.
13. As the lead curator, I want the SSc-versus-healthy contrast tested with the same non-parametric test used for the M5 precedent, so that results across cohorts are comparable.
14. As the lead curator, I want an effect size reported for every test, significant or not, so that a null result can be distinguished from an underpowered one.
15. As the lead curator, I want the replication decision to require both an adjusted significance threshold and agreement with the reference direction, so that a significant result in the wrong direction is never counted as success.
16. As the lead curator, I want a significant result in the opposite direction reported as a contradiction in its own category, so that it is visible rather than absorbed into "not replicated".
17. As the lead curator, I want the reference direction for the fibrosis module taken from the fibroblast-restricted comparison rather than the whole-tissue one, so that the known dilution artefact does not decide the outcome.
18. As the lead curator, I want a module that meets the criteria in some but not all cohorts labelled partial, so that inconsistent replication is not rounded up to replication.
19. As the lead curator, I want the existing M5 blood-cohort validation re-expressed on the shared core, so that one module is not validated by different machinery from the other four.
20. As the lead curator, I want the M5 result to reproduce its published values when re-run on the shared core, so that a defect in the core is caught by an already-audited answer.
21. As the lead curator, I want SSc genetic association tested for enrichment per module, so that the modular structure is examined by evidence that cannot be a consequence of disease state.
22. As the lead curator, I want the genetic test run against a second, within-map universe as a control, so that enrichment cannot be explained purely by the map being built of well-studied immune genes.
23. As the lead curator, I want the overlapping genes listed per module, so that a reader can judge the enrichment directly rather than trusting a p-value.
24. As the lead curator, I want the partial non-independence of literature-derived gene–disease sources stated in the output itself, so that the caveat travels with the number.
25. As the lead curator, I want the resolved trait identifier and the download date recorded with every knowledge-base query, so that the analysis can be repeated against the same snapshot.
26. As the lead curator, I want the target-knowledge-base coverage analysis labelled corroboration rather than validation in its own output, so that it cannot be promoted into an evidence claim by a later reader.
27. As the lead curator, I want community detection and community↔module enrichment re-run on the current five-module map, so that the committed file stops describing a module that no longer exists.
28. As the lead curator, I want the community analysis labelled an internal consistency check wherever it is emitted, so that it is not mistaken for independent evidence.
29. As a journal reviewer, I want the registered predictions reproduced next to the outcomes, so that I can see what was expected before it was known.
30. As a journal reviewer, I want every pre-specified test present in the reported results, so that I can tell that nothing was quietly dropped.
31. As a journal reviewer, I want analyses added after seeing results labelled post-hoc, so that I can weigh them differently.
32. As a reader of the resource, I want a module that fails to replicate to keep its place in the map with the failure stated, so that I can see the map's mechanistic claims and its evidential support separately.
33. As the lead curator, I want every figure built from the validation results to read them from committed result files, so that the hard-coded-values incident that decoupled a published figure from its script cannot recur.
34. As the lead curator, I want the validation results written as structured files rather than printed, so that figures, the manuscript and the numeric-coherence guard all draw from one source.
35. As a future maintainer, I want the decision rules implemented once in a shared module rather than repeated per analysis, so that changing a threshold cannot leave analyses disagreeing with each other.
36. As a future maintainer, I want the decision rules covered by tests with planted ground truth, so that "we applied the registered rule" is verified rather than asserted.
37. As a future maintainer, I want each analysis runnable through a named build target, so that the pipeline can be re-run without reconstructing the commands.
38. As the lead curator, I want the pipeline to run without the single-cell raw archives, so that validation does not depend on restoring gigabytes of data whose results are already frozen.
39. As the lead curator, I want an analysis that cannot be executed reported as a gap rather than substituted, so that the absence is recorded the way the clinical-metadata gap already is.
40. As the lead curator, I want any change to the registered rules appended to the amendment log with a date and reason, so that a silent post-hoc edit is distinguishable from a declared one.

## Implementation Decisions

**A shared validation core is introduced, and it is the only place decision rules live.**
`validation_core` exposes: loading of frozen module gene sets; sign-blind per-sample scoring (rank-based
primary, z-score sensitivity); a contrast test returning a result record with effect size and raw
p-value; family-wise adjustment over a declared family; and the replication decision, returning one of
four verdicts — *replicated*, *partial*, *not replicated*, *contradicted*. It performs no file I/O and
knows nothing about GEO, GWAS Catalog or OpenTargets.

**Analysis scripts are thin adapters over that core.** Each source-specific script owns only its
parsing and fetching — series-matrix and platform-table parsing for bulk cohorts, association
retrieval for genetic support, target retrieval for the knowledge base — and then hands normalised
tables to the core. No script re-implements scoring, adjustment or the decision rule.

**The existing M5 validation is migrated onto the core rather than left alongside it.** Its helpers
(module gene set loading, probe-to-symbol mapping, matrix loading, signature scoring) are the origin
of the core's interface; after migration the M5 script keeps only its cohort-specific parsing and its
sub-signature decomposition. This is the decision that makes the core trustworthy: it must reproduce
an already-audited result.

**The result record is a single shape across every analysis**: module, source, direction, effect size,
n per arm, raw p, adjusted p, testability flag, verdict, and the registered prediction it is being
compared against. Figures, the manuscript and the numeric-coherence guard consume this shape; nothing
downstream re-derives a number.

**The multiple-testing family is declared before adjustment and recorded in the output.** Adjustment
happens over module × cohort pairs marked testable; the family composition travels with the results so
a reader can see what was corrected over.

**Gene sets are built once, committed, and read thereafter.** The builder emits module membership with
a detectability flag and the inter-module overlap; downstream analyses read that artefact and never
re-derive membership from the curated layer.

**Module membership comes from the module column, never from the reaction ID.** Reaction IDs predate
the M4→M5 split and were not renumbered.

**The reference direction per module is read from the frozen single-cell contrasts**, with the
fibrosis module pinned to the fibroblast-restricted comparison as fixed in the pre-specification.

**Cohort verification precedes cohort analysis and is a separate step with its own committed output.**
Verified cohorts enter the data manifest so the existing provenance guard covers them.

**Not-executable is a supported outcome.** If cohort screening yields too few usable cohorts, the
analysis emits a gap record and the pipeline succeeds; it does not substitute a weaker analysis.

**Outputs are structured files under the analysis tree**, one per analysis, plus the screening and
amendment logs. Every build target is named and idempotent, following the existing convention.

**No task in this lot requires the single-cell raw archives.** The overlay stays frozen at its audited
run; only bulk series matrices and web APIs are fetched.

## Testing Decisions

**What a good test looks like here.** A test plants data with a known ground truth and asserts on the
verdict the pipeline reaches — not on how it got there. Tests assert that a planted effect is
recovered in the right direction, that a planted reverse effect is reported as a contradiction rather
than a success, that a module with no planted signal is not called replicated, and that a module below
the size floor is excluded from the family. Tests do not assert on intermediate scores, iteration
order, or output formatting.

**Prior art, followed rather than reinvented.** The repository already tests scripts by importing the
script module directly, planting synthetic data with a known answer, and asserting on the public
functions plus a CLI round-trip. The existing AUCell smoke test is the closest model: it plants an
elevated signal in one module and a *reversed* signal in another specifically to prove the score is
sign-blind, and includes a third module with nothing planted as a negative control. The mixed-effects
and clinical-correlation tests follow the same shape. New tests live beside them and use the same
discovery convention and temporary-directory fixture.

**Modules under test.** The validation core carries the real coverage, because it holds every rule
that matters: scoring sign-blindness, family adjustment, and the four-verdict decision. The adapters
get smoke coverage only — that a well-formed source parses into the expected normalised table, and
that a malformed one fails loudly rather than silently yielding an empty table, which would otherwise
present as a null result.

**The golden-master test.** Re-running the migrated M5 analysis against its cohort must reproduce the
published values for the module contrast and its sub-signature decomposition. This is the one test
whose expected values come from an independently audited run rather than from planted synthetic data,
and it is the strongest evidence that the core is correct.

**A directional negative control is mandatory.** At least one synthetic module carries a planted
effect in the direction *opposite* to its reference, and the test asserts the pipeline reports it as a
contradiction. Without this, a pipeline that always returns "replicated" would pass.

**Tests must not require network access or the raw archives.** Adapter tests use small committed or
synthesised fixtures; the golden-master test is skipped with a clear message when its cohort files are
absent, rather than failing.

## Out of Scope

- **The second-tier parity analyses** — activity-flow view, systematic clinical-trial confrontation,
  cross-map overlap. They are in the plan as sacrificeable and are not part of this spec.
- **Re-deriving the single-cell overlay.** Its numbers are audited and propagated; re-running them can
  only reintroduce divergence.
- **Cell-type deconvolution of bulk cohorts.** The inability to separate composition shift from module
  activation in bulk is declared as a limitation, not engineered around.
- **Clinical stratification.** No public deposit used carries the necessary clinical variables; that
  gap is already documented and is not reopened here.
- **Expert ratification and anything requiring clinician availability.** Out of reach for this cycle by
  decision, not by oversight. If decisions do arrive, they merge as a separate human verdict layer;
  nothing here depends on them.
- **Manuscript prose.** Writing the results section consumes these outputs and is a separate lot.
- **Changing the map.** This lot tests the curated layer; it does not add, remove or re-annotate
  reactions. Curation debt is a parallel lot.

## Further Notes

**The pre-specification outranks this spec on anything evidential.** Where they appear to disagree
about a threshold, a direction or a decision rule, the pre-specification wins and this spec is wrong.

**The registered predictions are expected to be partly falsified, and that is the point.** The
vasculopathy module is predicted null in skin bulk, and genetic enrichment is predicted for the
immune modules and absent for the effector ones. A run in which everything replicates in the predicted
direction should prompt suspicion that the test lacked discriminating power, and the pipeline should
make that easy to see by always reporting effect sizes and arm sizes.

**One number in the repository is wrong today.** The committed community↔module enrichment predates the
module split and describes a module of a size that no longer exists. That task is a correction, not an
enhancement, and it is the cheapest item in the lot — it needs no new data and no network.

**Why the shared core is worth the indirection.** The alternative — one self-contained script per
analysis, matching how the M5 validation was written — is simpler to write and is how the project got
here. It fails for a specific reason: the pre-specification's value rests entirely on the rules being
applied uniformly, and rules copied into four scripts diverge on the first thing that seems like a
special case. Putting them in one place makes uniformity a property of the code rather than a matter
of discipline.
