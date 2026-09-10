# Plan — first submission to npj Systems Biology and Applications

> **Written 2026-09-10.** Supersedes `ROADMAP.md` (ACR calendar, dead), `presubmission_review/PROGRESS.md`
> and `presubmission_review/REVISION_ROADMAP.md` (sprint dashboards describing a simulated revision
> cycle, stale since 2026-06-30). Those three documents described three mutually contradictory
> calendars; they are retired by lot L1.
>
> Vocabulary: `CONTEXT.md`. Validation methodology: `docs/planning/external_validation_prespec.md`.

---

## 1. Framing

**Nothing has ever been submitted to any journal.** The npj-SBA "major revision" in
`presubmission_review/` is an internally generated exercise, honestly labelled inside that folder and
misleadingly summarised outside it. This is a **first submission**.

**Clinicians are off the critical path for this cycle.** The reviewer deck went out on 2026-06-29 and
nothing came back; the co-author brief of 2026-05-16 was never answered. That is not recoverable by
planning, so the plan assumes it does not happen. Every validation below is one the curator can
execute alone.

**No external deadline exists.** The ACR track is abandoned. The 2026-09-30 date was self-imposed.
The risk is therefore not lateness but indefinite strengthening — four months already went that way.
Hence a ceiling with a pre-agreed degradable scope (§4).

**This machine plans; another machine executes.** Every task below states the command or procedure
explicitly, so it can be run without this session's context.

---

## 2. Lots

Five parents. One parent = one epic; one child task = one issue. IDs are stable and are the issue
keys.

| Lot | Name | Depends on | Gate |
|---|---|---|---|
| **L1** | Sanitisation and honest framing | — | G1 |
| **L2** | Independent validation | L1-05 (plan authority), pre-spec frozen | G2 |
| **L3** | Curation debt | — (parallel) | — |
| **L4** | Manuscript | L2 results | G3 |
| **L5** | Deposition and submission | L4 | G4 |

L1 and L3 start immediately and depend on no result. L2 must not start before its baseline is frozen
(L2-01). L4 restructuring waits for L2 so the manuscript is restructured **once**.

---

## 3. Tasks

Lane: 🟢 AUTO (scripted, no judgement) · 🟡 ASSIST (script proposes, curator decides) · 🔴 HUMAN.
Effort in curator-days.

### L1 — Sanitisation and honest framing

| ID | Task | Dep | Lane | Procedure | Acceptance criterion | Effort |
|---|---|---|---|---|---|---|
| **L1-01** | Rename `revision/` → `presubmission_review/`; add a standing banner to every file in it: *"Internally generated pre-submission critique. Not a journal review. The manuscript has never been submitted."* | — | 🟢 | `git mv revision presubmission_review`; update the 7 non-journal references found earlier | `grep -rl "revision/" --include=*.md . ` returns nothing outside `journal.md`; every file in the folder carries the banner in its first 5 lines | 0.5 |
| **L1-02** | Purge simulated-review vocabulary from the 6 project documents (26 occurrences): `README.md` (5), `STATUS.md` (7), `ROADMAP.md` (5), `CHANGELOG.md` (1), `docs/presentation.md` (1), `docs/SSc_MIM_construction_and_validation.md` (7). Kill in particular "npj-SBA revision v1.1 MERGED", "23/25 reviewer E-items closed", "reframed per editor" | L1-01 | 🟡 | rewrite each occurrence as an internal-audit statement; never delete the underlying fact (the work was really done) | `scripts/check_claims.py` (L1-06) exits 0 on these 6 files | 0.5 |
| **L1-03** | Purge the manuscript (24 occurrences: 13 × "v1.1", 10 × "revision", 1 × "reviewer"). Remove version numbering from the text — only the repository is versioned | L1-01 | 🟡 | `manuscript/SSc_MIM_manuscript_draft.md`, occurrence by occurrence | 0 occurrences of `reviewer|revised version|per the editor|v1\.1` in the manuscript | 0.5 |
| **L1-04** | Requalify the curation claims. Remove or correct "community/expert-curated" and "Scoping with domain experts (SSc clinicians)" wherever the described step did not occur. Draft the single Limitations paragraph: no expert ratification to date, 5 modules are an expert-defined reading frame, curation by one curator | L1-02 | 🔴 | README §Methodology, manuscript Methods + Limitations | no document asserts expert validation; exactly **one** Limitations paragraph carries the statement, and it appears nowhere else | 0.5 |
| **L1-05** | Retire the three stale dashboards. **Partly done 2026-09-10**: historical banners applied to `ROADMAP.md`, `revision/PROGRESS.md`, `revision/REVISION_ROADMAP.md`. **Remaining**: neutralise the forward-looking tables *inside* them (ROADMAP milestone calendar M6–M12, go/no-go gates G2–G5, handover queue; the ⏳-pending sprint rows S4–WR) so no reader mistakes them for open work | L1-01 | 🟡 | | no document other than this plan states a forward calendar; no table row reads as pending work | 0.3 |
| **L1-06** | **CI guard** `scripts/check_claims.py`: fails the build if a forbidden claim appears outside `presubmission_review/` and `journal.md` — *peer review(ed)*, *expert-validated*, *expert-curated*, *as requested by the reviewer/editor*, *major revision*. Wire into `make lint` and the `lint.yml` workflow | L1-02..05 | 🟢 | mirror `scripts/check_data_manifest.py`, which does the same job for data provenance | verified to **fail** on a seeded violation and **pass** on the cleaned tree; job green in CI | 0.5 |

**G1 clears when L1-06 is green.**

### L2 — Independent validation

Governed by `docs/planning/external_validation_prespec.md`. Read it before starting; do not amend it
silently.

| ID | Task | Dep | Lane | Procedure | Acceptance criterion | Effort |
|---|---|---|---|---|---|---|
| **L2-01** | **Freeze the baseline.** Tag `prespec-baseline`. Emit `analysis/validation/module_genesets.tsv` (module × HGNC symbol, detectability flag, inter-module overlap reported) **before any cohort is downloaded** | pre-spec committed | 🟢 | new `scripts/build_module_genesets.py` | tag exists; TSV committed; per-module counts match the curated layer; any module < 10 detectable symbols flagged not-testable | 0.5 |
| **L2-02** | **Analysis D — community↔module concordance, re-run.** The committed `community_enrichment.tsv` is dated 2026-06-09, **pre-M5-split**, and still reports a module M4 of 78 species that no longer exists. Every number drawn from it is currently wrong | L2-01 | 🟢 | `make network` (networkx only, no raw data) | new `analysis/network/community_enrichment.tsv` contains M5; the 5 modules' enrichment status reported as found, not as expected; every downstream figure and sentence updated | 0.5 |
| **L2-03** | **Analysis A — cohort verification.** Verify the candidate accessions against the live GEO record (accession, tissue, platform, per-arm n, donor overlap with the 4 single-cell datasets). Commit the screening log, including rejections | L2-01 | 🟡 | pre-spec §3.2; fallback GEO query documented there | ≥2 skin cohorts verified and frozen, **or** a committed log showing why not and Analysis A declared not executable; every verified cohort added to `data/MIRROR.sha256` (the `check-manifest` guard will otherwise fail the build) | 1 |
| **L2-04** | **Analysis A — execution.** Singscore + Z sensitivity, Mann-Whitney, BH over the frozen (module × cohort) family; replication decided by the two-criterion rule; contradictions reported separately | L2-03 | 🟢 | new `scripts/validate_external_cohorts.py`, modelled on `validate_m5_gse45536.py` | every testable (module × cohort) pair reported with effect size and padj, including failures; predictions of pre-spec §3.6 reproduced alongside outcomes; results JSON written for figure use, no hard-coded numbers | 1.5 |
| **L2-05** | **Analysis B — genetic support.** GWAS Catalog SSc (p ≤ 5×10⁻⁸) and DisGeNET; hypergeometric enrichment per module against the protein-coding universe, plus the Reactome-backbone within-map control | L2-01 | 🟢 | new `scripts/validate_genetic_support.py`; record the resolved EFO term and the download date | per-module enrichment with BH; overlap gene lists committed so a reader can judge them; declared non-independence (pre-spec §4.4) carried into the output | 1 |
| **L2-06** | **Analysis C — OpenTargets coverage** (descriptive, comparator parity). Coverage of SSc OpenTargets targets by map species + UpSet | L2-01 | 🟢 | new `scripts/opentargets_coverage.py` | figure + table; output labelled corroboration, not validation, in caption and text | 1 |
| **L2-07** | *Second tier — sacrificeable.* CaSQ Activity-Flow view for comparator parity | L2-02 | 🟢 | `make casq` (already produces 83 Boolean nodes) → Cytoscape export | figure produced or task dropped at the ceiling | 0.5 |
| **L2-08** | *Second tier — sacrificeable.* Systematic ClinicalTrials.gov confrontation of the 28 DGIdb targets (6 already done by hand) | — | 🟡 | | table refreshed or task dropped | 1 |
| **L2-09** | *Second tier — sacrificeable.* Cross-map overlap: SSc-MIM × SjD Map × RA-map | — | 🟢 | | table produced or task dropped | 1 |

**G2 clears when L2-02, L2-04, L2-05 and L2-06 have produced a result — whatever that result is.**
A negative or null outcome clears the gate. An unexecuted analysis does not.

### L3 — Curation debt (parallel, no dependency)

| ID | Task | Dep | Lane | Procedure | Acceptance criterion | Effort |
|---|---|---|---|---|---|---|
| **L3-01** | The **8 reactions carrying no primary PMID**: `ssc_M1_012`, `ssc_M2_012`, `ssc_M2_019`, `ssc_M2_021`, `ssc_M2_022`, `ssc_M3_014`, `ssc_M4_011` (module M5), `ssc_M4_015`. Targeted PubMed search for each | — | 🟡 | `make mine-lit`, then abstract verification | each row ends either with a **verified** primary PMID or explicitly retained as declared `ECO:0000305` curator inference. **No PMID is invented** — `ssc_M2_019` is the precedent: three searches, no such paper, PMID removed rather than fabricated | 1 |
| **L3-02** | The **32 `to_complete` cards** with no verbatim deciding sentence | — | 🟢 | `make pdf-quotes` (needs PyMuPDF for the PDF path; the PMC/abstract path runs without it) | count reduced and the residue listed with its reason; every mined quote verified present in the **cited** article — the `fetch_pmc` self-link trap that once poisoned 8/9 quotes is fixed, but the property must be re-checked, not assumed | 1 |
| **L3-03** | Rebuild the interaction database and the reviewer deck | L3-01, L3-02 | 🟢 | `make review` | deck count reconciles with `ssc_curated_reactions.tsv` (143 = 133 in_map + 10 discarded, or the new figure justified); no local path leaks into the shipped HTML; the negative-control candidate stays absent | 0.5 |

### L4 — Manuscript

| ID | Task | Dep | Lane | Procedure | Acceptance criterion | Effort |
|---|---|---|---|---|---|---|
| **L4-01** | Restructure to comparator parity: new §3.2 curation and evidence provenance; §3.5 M5 external validation as a standalone section | G2 | 🔴 | plan in `docs/planning/sjd_inspired_manuscript_plan.md` §6 | sections exist with the current verified numbers | 1.5 |
| **L4-02** | **New §3.7 — independent validation.** Analyses A, B, C, D with outcomes, including failures. Reproduce the pre-registered predictions next to the results | L4-01 | 🔴 | pre-spec §7 | every pre-specified test present; no post-hoc analysis presented as pre-specified | 1.5 |
| **L4-03** | Limitations, calibrated. **One** paragraph: no expert ratification to date; modules are an expert-defined frame; coverage is corroboration, not validation; bulk cannot separate composition from activation; no clinical stratification (0/773 GEO samples carry mRSS) | L1-04 | 🔴 | | stated once, factually, in Limitations only — not repeated in Results, Discussion or Abstract, and not in an apologetic register | 0.5 |
| **L4-04** | Methods: the **citation-integrity QC pipeline as a contribution**. Gates G0–G4, verbatim grounding, the advisory AI verdict layer, and the reaction↔PMID concordance audit with its real yield: 28 + 6 + 3 corrected citations, 1 edge unpublished for want of any source | L4-01 | 🔴 | | described as a reproducible QC layer with measured yield; explicitly **not** described as review or ratification | 1 |
| **L4-05** | Structured abstract (~200 words) + cite the SjD Map as the sibling resource + position the curation-first inversion | L4-02 | 🔴 | | abstract carries only numbers that exist in committed artefacts | 0.5 |
| **L4-06** | **CI guard `scripts/check_numbers.py`**: extract every headline figure from the manuscript, README, STATUS and the deck, and diff against the committed analysis artefacts | L4-02 | 🟢 | the project has been bitten repeatedly by stale numbers (81.3 vs 82.6 %, 58 vs 62 overlays, 143 vs 145 cards) | exits non-zero on any divergence; wired into `make lint` | 1 |
| **L4-07** | Figures: F3 gains the module↔community concordance panel (post-M5); one new figure for Analysis A + B | L2-04, L2-05 | 🟢 | `make figures f1-quadrant`; new render script for the validation figure, reading the JSON from L2-04/L2-05 — **no hard-coded values** (the F7 hard-coding incident is the precedent) | figures regenerate from committed artefacts on a clean checkout | 1 |

**G3 clears when L4-06 is green and the manuscript is structurally complete.** G3 ⇒ submit.

### L5 — Deposition and submission

| ID | Task | Dep | Lane | Procedure | Acceptance criterion | Effort |
|---|---|---|---|---|---|---|
| **L5-01** | Full validation pass on a clean checkout | G3 | 🟢 | `make lint validate pytest preflight` | SBML 0 errors; all guards green (`check-manifest`, `evidence-lint`, `check_claims`, `check_numbers`) | 0.5 |
| **L5-02** | Refresh deposition metadata: `CITATION.cff`, `.zenodo.json`, `ro-crate-metadata.json`, `data/MIRROR.md` including the new cohorts | L5-01 | 🟡 | | no `REPLACE_ME` outside a deliberately empty co-author slot; RO-Crate lists the new artefacts | 0.5 |
| **L5-03** | Tag, Zenodo webhook, DOI | L5-02 | 🔴 | `git tag v1.0 && git push --tags` | DOI minted and quoted in the data-availability statement. **10 minutes; not a blocker at any earlier point** | 0.1 |
| **L5-04** | Submission package: cover letter framed as a **first submission** (no mention of revision), data-availability statement, author list as it actually stands | L5-03 | 🔴 | | package coherent with `CONTEXT.md`: nothing claims peer review, expert validation, or a revision cycle | 0.5 |

**Total: ~22 curator-days**, of which ~4 are sacrificeable second tier.

---

## 4. Gates, ceiling, degradation

| Gate | Condition | Consequence |
|---|---|---|
| **G1** | L1 closed, `check_claims` green | the repo no longer asserts anything untrue about its own review status |
| **G2** | L2-02, L2-04, L2-05, L2-06 have **produced a result, whatever it is** | validation section is writable |
| **G3** | manuscript structurally complete, `check_numbers` green | **submit** |
| **G4** | deposited, DOI minted, package coherent | submitted |

**Ceiling: end of November 2026.** If G3 is not cleared by then, submit with a degraded scope,
according to this order, fixed now so it is not renegotiated under pressure:

1. drop L2-09 (cross-map), then L2-08 (trials), then L2-07 (CaSQ);
2. drop L3-02 (deciding-sentence completion) — it improves the reviewer deck, not the manuscript;
3. **never drop** L2-02, L2-04, L2-05, L1, L4-03, L4-06.

L2-02 is not droppable because a committed number is currently wrong. L2-04 and L2-05 are not
droppable because they are the entire point of this cycle.

---

## 5. Execution environment

| Need | Detail |
|---|---|
| Python stack | pandas, numpy, scipy, statsmodels, networkx, python-libsbml, matplotlib, requests. **scanpy is not required** for any task in this plan |
| Raw data | **The 3.18 GB of single-cell archives are not needed.** The single-cell overlay is frozen at the audited 2026-06-26 run. Only the new bulk cohorts are downloaded (series matrices, tens of MB) |
| Optional | PyMuPDF for the PDF path of L3-02; CaSQ + Cytoscape for L2-07; weasyprint for the deck and manuscript PDF |
| Network | required — GEO, GWAS Catalog, OpenTargets, NCBI E-utils |
| Restoring the full stack | if a task ever needs cell-level rescoring: `data/MIRROR.sha256` + the `make fetch-*` targets restore the 3.18 GB and `make overlay-multi aucell` re-derives. Out of scope here |

**Why the overlay stays frozen:** its numbers are audited and consistently propagated across every
document. Re-deriving them can only reintroduce divergence, and no task in this plan depends on
cell-level rescoring.

---

## 6. Standing risks

| Risk | Handling |
|---|---|
| Analysis A finds no usable independent skin cohort | declared not executable and reported as a gap (pre-spec §7.5); the claim is not made by another route |
| M1 or M2 fails to replicate | a serious finding about the map, reported as such; pre-spec §3.5 gives the confounds that would need excluding first |
| Uniform GWAS enrichment across modules | the §4.5 prediction is falsified; reported, and the modular structure loses that support |
| Indefinite strengthening | the ceiling and the fixed degradation order in §4 |
| Clinicians re-engage mid-cycle | pure upside: their decisions merge as a `human_verdict` layer beside the advisory AI verdicts, and the Limitations paragraph is rewritten. Nothing in this plan depends on it |
| Stale numbers reappear | `check_numbers` (L4-06) makes it a build failure rather than a proofreading task |
