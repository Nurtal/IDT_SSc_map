# Pre-specification — independent validation of SSc-MIM

> **Written 2026-09-10, before any of the analyses below were run.** Frozen at commit time.
> Its purpose is to make the analyses falsifiable: the hypotheses, thresholds and decision rules are
> fixed here so that a negative result is a finding rather than a discard.
>
> **Amendment rule.** Any change after execution begins is appended to §8 with a date and a reason,
> and the original text is left standing. Silent edits defeat the point of the document.
>
> Vocabulary follows `CONTEXT.md`. In particular: *validation* here means sense 4 — a pre-specified
> hypothesis tested on data that played no part in building the map.

---

## 1. Why this document exists

Everything the project has done with omics so far is **corroboration** (`CONTEXT.md` sense 3): the
overlay projects transcriptomic signal onto the map and reports agreement. Agreement was never at
risk, because nothing about the analysis could have produced disagreement — there is no threshold
whose failure would have been reported.

Two of the analyses below can fail, and are designed to. The other two are descriptive and are
labelled as such, so they are not mistaken for evidence.

A second, specific reason: this project has already been burned once by circularity. The v1.0
sign-weighted module score reported Δ≈+0.27; recomputed sign-blind with AUCell the same contrast gave
Δ=+0.058. The inflation was a factor of ~5 and came entirely from using the SSc-vs-HC contrast both
to select genes and to sign the score. Every scoring rule below is therefore fixed *before* the data
are seen.

**Independence claimed here is independence of the evidence source, not of the analyst.** The same
curator runs these analyses. What makes them independent is that the cohorts and knowledge bases were
produced without reference to this map.

---

## 2. Frozen inputs

These definitions are fixed now and must not be re-derived during analysis.

| Input | Definition | Frozen artefact |
|---|---|---|
| Module membership | the `module` column of the curated layer, joined to HGNC symbols via species annotations | `curation/ssc_curated_reactions.tsv`, `curation/annotations/species_annotations.tsv` at the commit tagged `prespec-baseline` |
| Module gene sets | the distinct HGNC symbols reachable in each module; a symbol appearing in two modules is kept in both and the overlap is reported | derived, must be written to `analysis/validation/module_genesets.tsv` **before** any cohort is downloaded |
| Detectability filter | symbols flagged RNA-seq-detectable, as already used for the coverage denominator (236 symbols) | `species_annotations.tsv` |
| Reference directions | the per-module SSc-vs-HC direction observed in the single-cell overlay of 2026-06-26 | `analysis/overlay/module_score_contrasts_v1.1.json` |

**Minimum module size:** a module with fewer than 10 detectable symbols in a given cohort's platform
is reported as *not testable in that cohort* and excluded from the multiple-testing family. This rule
is fixed now so it cannot be applied selectively later.

---

## 3. Analysis A — replication of module activation in independent bulk cohorts

### 3.1 Claim under test

*Each module's SSc-vs-healthy activation, observed in the single-cell overlay used to build the
corroboration layer, reproduces in a bulk transcriptomic cohort that contributed nothing to the map.*

The template is the M5 validation already performed on GSE45536 (99 SSc / 24 HC whole blood,
p=1.3×10⁻⁴), generalised from one module to five.

### 3.2 Cohort selection

Cohorts are chosen **before** any is analysed, on these criteria, in this order:

1. SSc **skin** biopsies (the map's periphery), SSc vs healthy control, n ≥ 20 per arm;
2. public, with per-sample condition labels retrievable from the GEO series matrix;
3. no overlap of donors with the four single-cell datasets already used;
4. not used at any point in curation.

**Candidate accessions, all to be verified before use** — accession, tissue, platform, and per-arm n
must be confirmed against the live GEO record, and the candidate dropped if it fails any criterion
above. These are leads, not established facts:

| Candidate | Expected content | Verification required |
|---|---|---|
| GSE130955 | dcSSc skin, bulk RNA-seq, SSc vs HC | accession, arm sizes, platform, donor overlap |
| GSE58095 | SSc skin, microarray, large SSc vs HC series | idem |
| GSE95065 | SSc skin, RNA-seq | idem |
| GSE45536 | whole blood, already used for M5 | **held out as the M5 positive control only** — not counted as a new cohort |

If fewer than two skin cohorts survive verification, the fallback is a documented GEO query
(`systemic sclerosis[All Fields] AND skin AND (expression profiling by array OR by high throughput
sequencing)`), screened against the same four criteria, with the screening log committed. If no
cohort survives, Analysis A is reported as **not executable**, exactly as the clinical-metadata gap
was, and the claim it would have supported is not made by other means.

**Cohorts are frozen once verified.** A cohort may not be dropped after its result is known.

### 3.3 Scoring

- Per sample, per module: **singscore** (rank-based, sign-blind) over the module gene set, with mean
  Z-score across module genes as a pre-declared sensitivity analysis. Both are computed; the
  singscore is primary.
- The score uses **module membership only**. No gene weighting, no gene selection, and no use of the
  SSc-vs-HC contrast in this cohort or any other, at any point in constructing the score.
- Sample-level normalisation follows the platform default (log2 for microarray as deposited; TMM or
  vst for count data), fixed per cohort before scoring.

### 3.4 Test and thresholds

- **Contrast:** SSc vs HC, two-sided **Mann-Whitney U** (matching the GSE45536 precedent; no
  distributional assumption).
- **Effect size:** rank-biserial correlation, reported for every test whether significant or not.
- **Multiple testing:** Benjamini-Hochberg across the family of (module × cohort) tests that are
  *testable* per §2. The family is fixed once cohorts are verified and is stated in the results.
- **Replication of a module** requires **both**:
  1. `padj ≤ 0.05`, **and**
  2. the same direction as the single-cell reference in §2.
  A significant result in the **opposite** direction is reported as a **contradiction**, not as a
  replication, and gets its own line in the results.
- **Per-cohort consistency:** with ≥2 cohorts, a module is *replicated* only if it meets both
  criteria in at least half of the cohorts where it is testable; meeting them in some but not all is
  reported as *partial*.

### 3.5 Known confounds, declared now

- **Whole-tissue dilution.** M2 was paradoxically *down* in whole-tissue single-cell scoring
  (Δ=−0.041, p=7.3×10⁻⁴) because myofibroblasts are diluted by bulk composition. Bulk skin is subject
  to the same effect, in the opposite direction (fibrotic skin has more fibroblast mass). The M2
  reference direction in §2 must therefore be taken from the **fibroblast-restricted** comparison, not
  the whole-tissue one, and this choice is made here rather than after seeing the result.
- **Cell-composition shift is not module activation.** A module can move purely because its cell type
  changed in abundance. This is not separable in bulk. It is stated as a limitation of Analysis A in
  the manuscript; no deconvolution is claimed unless it is actually run.
- **Rare-population modules.** M5 in skin is carried by B and plasma cells, which are rare there. A
  null M5 in skin bulk is **expected** and is not evidence against M5, which was validated in blood.

### 3.6 Pre-registered predictions

Stated before execution. Their value is that some of them should turn out wrong.

| Module | Predicted direction (SSc vs HC, skin bulk) | Confidence | Rationale |
|---|---|---|---|
| M1 IFN-I | **up** | high | IFN signature is among the most reproduced findings in SSc skin and blood; AUCell Δ=+0.077, p=6.4×10⁻⁸ in Gur |
| M2 TGF-β / fibrosis | **up** | high | fibrotic skin; the dominant axis of the disease and of the map |
| M3 EndoMT / vasculopathy | **null or weak** | low | the project's own vascular-subset analysis found **no** endothelial EndoMT signal; the three hits were pericyte-restricted (EDN1↑, ANGPT2↑, S100A4↓) |
| M4 cytokines | **up, modest** | medium | IL-6/IL-13 axis documented but not a dominant bulk signal |
| M5 B-cell / autoreactivity | **null in skin** | medium | rare populations in skin; already validated in blood (GSE45536) |

**A failure of M1 or M2 to replicate would be a serious finding about the map** and must be reported
as such. A null M3 confirms an internal observation and is a legitimate result. If every module
replicates in the predicted direction, the concordance is reported plainly, and the possibility that
the test lacked discriminating power is stated.

---

## 4. Analysis B — genetic support for the module structure

### 4.1 Claim under test

*Genes carrying SSc genetic association are enriched in the map, and unevenly across modules.*

This axis is **orthogonal** to transcriptomics: germline association cannot be a consequence of the
disease state, so it is not vulnerable to the reverse-causation and composition problems of §3.

### 4.2 Sources

- **GWAS Catalog**, SSc trait (EFO term to be resolved and recorded), genome-wide significant
  associations only (p ≤ 5×10⁻⁸); reported and mapped genes as deposited.
- **DisGeNET** SSc gene-disease associations as a secondary, broader source, reported separately —
  it aggregates literature and is therefore **partly non-independent** of the map's own curation.

### 4.3 Test

- **Universe:** protein-coding genes, primary. A second test against the Reactome-backbone symbols is
  run as a within-map control, to check that any enrichment is not merely an artefact of the map being
  made of well-studied immune genes.
- **Test:** hypergeometric enrichment of SSc GWAS genes among map symbols, then per module.
- **Multiple testing:** BH across the 5 modules.
- **Reported regardless of outcome:** the overlap gene list per module, so a reader can judge it
  directly.

### 4.4 Declared non-independence

The curated layer was built from SSc literature, and some of that literature is genetic. So the
overlap is **not fully independent** — a locus can be in the map *because* it was a GWAS hit. This is
stated in the manuscript, and mitigated, not hidden, by two devices: (i) the within-map Reactome
control above, and (ii) reporting the per-module *pattern* rather than the global overlap, since
uniform curation bias predicts uniform enrichment.

### 4.5 Pre-registered prediction

| Module | Predicted GWAS enrichment | Rationale |
|---|---|---|
| M1 IFN-I | **strong** | IRF5, STAT4, TNFAIP3, IRF7/IRF8, TYK2 are among the best-replicated SSc loci |
| M5 B-cell / autoreactivity | **strong** | BANK1, BLK, CSK, DNASE1L3 |
| M4 cytokines | **weak to moderate** | few canonical SSc loci in this axis |
| M2 TGF-β / fibrosis | **absent or weak** | the fibrotic axis is effector biology, largely without germline association |
| M3 EndoMT / vasculopathy | **absent or weak** | idem |

**This prediction is the sharpest falsifiable statement in the document.** It says the map's immune
modules are genetically supported and its effector modules are not — which is a claim about SSc
biology, testable in one query, and wrong if enrichment turns out to be uniform. If the predicted
split holds, it is a substantive result: the modular structure is recovered by an axis of evidence
that played no part in creating it.

---

## 5. Analysis C — OpenTargets coverage (descriptive)

Coverage of SSc-associated targets from OpenTargets by map species, with an UpSet view, mirroring the
comparator resource. **This is a coverage description, not a hypothesis test:** no threshold, no
pass/fail, and it is reported under corroboration (`CONTEXT.md` sense 3), never as validation. Its
purpose is comparability with the sibling disease map, and it is honest about the fact that
OpenTargets aggregates literature the curation may itself have drawn on.

## 6. Analysis D — community↔module concordance (internal consistency)

Re-run of unsupervised community detection and hypergeometric community↔module enrichment on the
current five-module map. **This is an internal consistency check, not validation** (`CONTEXT.md`,
*Community*): the graph it runs on is the curated graph, so it partly measures curation density.

It is nonetheless mandatory, for a reason unrelated to validation: the committed
`analysis/network/community_enrichment.tsv` dates from 2026-06-09, **before the M4→M5 split**, and
still reports a module M4 of 78 species that no longer exists. Any figure or sentence drawn from it
is currently wrong. Re-running is a correction, not an enhancement.

---

## 7. Reporting commitments

1. **Every pre-registered test in §3 and §4 is reported**, with its effect size and p-value, whether
   it succeeds, fails, or contradicts the prediction. No test that appears here may be absent from
   the manuscript.
2. **Predictions in §3.6 and §4.5 are reproduced verbatim in the manuscript or its supplement**, next
   to the outcomes, so a reader can see what was expected before it was known.
3. **Modules that fail to replicate keep their place in the map**, with the failure stated. The map is
   a mechanistic knowledge structure; a module can be mechanistically sound and transcriptionally
   invisible in bulk tissue, and §3.5 gives the reasons that would apply.
4. **No analysis added after seeing results is presented as pre-specified.** Post-hoc analyses are
   permitted, labelled post-hoc, and reported after the pre-specified ones.
5. **If Analysis A proves not executable**, that is reported as a gap, and no substitute analysis is
   promoted into the validation claim.

## 8. Amendment log

| Date | Change | Reason |
|---|---|---|
| 2026-09-10 | Document created, before execution | — |
