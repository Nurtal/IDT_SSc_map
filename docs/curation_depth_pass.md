# Curation-depth pass — SSc-Tier-1 evidence sourcing (2026-06-05)

> Companion to the v1.1 hardening sprint. Where the hardening sprint *quantified* the
> weak SSc-specific curation layer (45/85 reactions on curator inference, no PMID), this
> pass *pays it down* — by literature-mining, verifying, and triaging every one of those
> 45 rows. Method and integrity discipline are recorded here so the result is auditable
> and the co-author's ratification step is well-scoped.

## Why

The SSc-Tier-1 layer (85 reactions in `curation/ssc_curated_reactions.tsv`) is what makes
this a *curated SSc map* rather than a Reactome re-export. Of those, only 40 carried a
primary PMID; 45 rested on `ECO:0000305` (curator inference). The house rule
(`docs/mi2cast_checklist.md`) requires every reaction to carry a citation stricter than
`ECO:0000305`. This pass closes most of that gap.

## Method

1. **Schema** — `ssc_curated_reactions.tsv` gained `curation_status`, `candidate_pmids`,
   `provenance` columns (additive; `wire_ssc_tier1.py` reads via `DictReader`, unaffected).
2. **Candidate mining** — `scripts/mine_lit_candidates.py` (NCBI E-utils `esearch`+`esummary`,
   reusing `bib_lookup.py` infra) builds disease-context and canonical-mechanism PubMed
   queries from each reaction's gene participants + mechanism text, caching ranked candidate
   PMIDs to `curation/lit_candidates/<reaction_id>.json`.
3. **Verified assignment** — for each row the candidate abstracts were **read** and a PMID
   attached only if the abstract supports the specific causal statement. Evidence codes
   follow `mi2cast_checklist.md`: `ECO:0000314` (primary assay), `ECO:0000270` (expression),
   `ECO:0000353` (physical interaction), or `ECO:0000033` (author statement in a review that
   accurately states an established mechanism). All such rows are tagged
   `curation_status=proposed` and `provenance=claude-lit-mine/2026-06-05`.
4. **Honest reclassification** — rows that are cell-state assertions or phenotype convergence
   points (not single molecular interactions) were tagged `conceptual_bridge` or
   `phenotype_aggregation` instead of being force-fitted with a weak citation.
5. **Backlog** — rows with no clean primary paper were left `untested` with their candidate
   pool attached (`candidate_pmids`) so the co-author has a head start.
6. **Lock-in** — `scripts/check_evidence_depth.py` (`make evidence-lint`, CI job
   `evidence-depth` in `.github/workflows/lint.yml`) fails on any *undeclared* inference
   debt, enforcing triage completeness without demanding a zero-inference map.

## Integrity discipline

- **No fabricated PMIDs.** Every proposed PMID is a real PubMed record whose abstract was
  read to confirm it supports the claim.
- **Proposed ≠ validated.** Proposed citations are counted separately from confirmed and
  are *not* presented as expert-ratified. Co-author ratification (`proposed`→`confirmed`)
  remains the irreducible human step; this pass converts it from "source 45 rows from
  scratch" into "ratify 23 abstract-checked proposals + confirm 10 reclassifications".
- **Reclassification beats citation laundering.** A review at `ECO:0000033` is honest; a
  tangential primary paper dressed as `ECO:0000314` is not.
- **Map content untouched.** Only evidence fields and the new status columns changed; the
  `SSc_MIM_integrated.xml` species/reactions are unchanged (preflight green, 526/260).
  Regenerating the MIRIAM-annotated SBML to embed the new PMIDs is a release step
  (`scripts/inject_miriam.py`), out of scope here.

## Result

| SSc-Tier-1 (85 reactions) | before | pass 1 | pass 2 | pass 3 (full-text) |
|---|---|---|---|---|
| With a primary PMID | 40 (47%) | 63 (74.1%) | 74 (87.1%) | **72 (84.7%)** |
| Full-text- or originally-verified (`confirmed`) | 40 | 40 | 40 | **67** |
| Undeclared inference debt (`ECO:0000305`, no PMID, untriaged) | 45 | 0 | 0 | **0** |

Pass 2 (2026-06-05, same day) cleared 11 of the 12 `untested` rows with targeted searches +
abstract verification (e.g. PMID 7539918, the canonical Wang & Semenza 1995 HIF-1 bHLH-PAS
heterodimer paper, for `ssc_M3_020`).

**Pass 3 — full-text verification (2026-06-05).** The downloaded PDFs were read (not just
abstracts) to keep/discard each proposed citation against its specific causal claim — logged
in `curation/fulltext_verification_log.md`. Of the 34 proposed: **27 kept** (full-text
confirms the claim → `confirmed`), **2 discarded** (`ssc_M3_017` TWIST1 and `ssc_M3_021` ZEB2
were assigned to PMID 28062404, which documents Snail1-driven EndoMT in SSc but does *not*
cover TWIST1 or ZEB2 → back to `untested`), and **5 left `proposed`** (PDF not available:
`ssc_M3_005/006/007/008/019`).

Final curation-status breakdown: **confirmed 67, proposed 5, conceptual_bridge 4,
phenotype_aggregation 6, untested 3** (`ssc_M1_013` + the two discards). 67/85 SSc reactions
now carry a full-text-or-originally-verified citation; the 5 `proposed` await their PDF.

Notable SSc-specific anchors added: PMID 16319104 (constitutively phosphorylated Smad3 in
scleroderma fibroblasts) and PMID 28062404 (EndoMT in systemic sclerosis), which underpin
the M2 collagen-transcription and M3 EndoMT edges respectively.

## Regenerate

```bash
make mine-lit              # (network) refresh candidate pools
make evidence-audit inference-register evidence-lint   # recompute + guard
```
