# Reviewer 1 — Systems Biology / Disease Maps

**Manuscript**: SSc-MIM: A Curated, SBGN-Compliant Molecular Interaction
Map of Skin Fibrosis in Diffuse Cutaneous Systemic Sclerosis
**Author**: N. Foulquier
**Target journal**: npj Systems Biology and Applications
**Reviewer expertise**: SBGN / CellDesigner curation, Disease Maps
Project conventions, MI2CAST, network biology, Boolean modelling.

---

## Overall recommendation

**Major revision.** The map fills a genuine gap — no comprehensive
SBGN-curated MIM exists for systemic sclerosis — and the construction
methodology is largely faithful to Mazein 2018/2023 and MI2CAST 2021.
However, several methodological details required by the npj-SBA
readership (community detection significance testing, dangling fraction
disclosure, sink connectivity, Boolean readiness) are either missing or
under-specified. The crosstalk claims, which are the most original
contribution after the curation itself, are not formally quantified.
With these issues addressed, the manuscript should be a valuable
community resource.

---

## Significance and novelty

The Disease Maps Project ecosystem now covers RA, COVID-19, Parkinson,
Sjögren and several IBD-related maps, but SSc has remained
conspicuously absent despite high unmet medical need and dense
mechanistic literature. The submitted map addresses this gap with a
defensible module decomposition (M1 IFN-I / M2 TGF-β / M3 EndoMT /
M4 IL-6–Th2–B-cell) and an explicit cross-module layer (8 crosstalk
reactions). The scope (526 species, 260 reactions, 85 SSc-curated
reactions backed by 355 PMIDs) is comparable to early RA-map versions
and exceeds the recent SjD map for fibroblast/EndoMT depth.

The novelty is therefore real but should be framed more sharply.
Specifically:

1. **Quantitative comparison vs Reactome/KEGG** — the manuscript
   states qualitatively that disease-specific maps add value over
   canonical databases, but does not show the figures. Please report
   (i) the proportion of SSc-MIM reactions that are *not* recoverable
   by union of the seed Reactome pathways, (ii) the proportion of
   PMIDs that come from SSc-specific primary literature vs review
   articles, and (iii) the species / reactions added by the SSc Tier-1
   curation that were absent from any imported source.
2. **Novelty vs published SSc transcriptomic networks** — the
   Mahoney/Taroni consensus networks and the Tabib (2021) connectivity
   analysis are cited as related work, but no overlap is quantified.
   A side-by-side enrichment of the SSc-MIM hub list against the
   Mahoney 2015 modules (or, more powerfully, the Taroni consortium
   consensus) would substantiate the claim that the curated map
   captures biology not visible in expression-only networks.

---

## Major points

### M1. Sink-node connectivity and dangling species

`make preflight` carries one advisory: a 17.9% dangling fraction
(STATUS.md, 2026-05-19). This is acceptable per Mazein 2023, but the
manuscript does not disclose it. Please add to Methods §2.5 the
final dangling fraction, the count of species with degree 0 or 1
after Tier-1 wiring, and the four "sink phenotype" anchor nodes
(myofibroblast activation, ECM deposition, vascular remodeling,
ISG signature) that close the map at the disease-phenotype level.
Figure 1 already shows them as diamond glyphs — the legend should
mark them as such.

### M2. Statistical support for the cross-module crosstalk claim

The Discussion §4.2 builds a strong narrative around an IFN–TGF-β
positive-feedback loop, but only 8 crosstalk reactions are listed in
Table 1 (no breakdown, no per-edge evidence). For an npj-SBA
audience the following are required:

- **Hypergeometric test of community–module alignment** with the
  exact p-value reported. The community–module contingency table
  shows that community 0 contains 25 M1 + 21 M2 + 15 M4 species,
  which is consistent with a single "inflammatory–fibrotic"
  super-community rather than the cleanly separated modules
  implied by Table 1. Please report the hypergeometric p-value per
  community, after Bonferroni or BH correction across 38
  communities, and re-state the claim "the six largest communities
  were significantly enriched for single biological modules"
  accordingly.
- **Per-crosstalk-reaction PMID, mechanism and ECO code**, ideally as
  a supplementary table. The integrated TSV
  (`curation/ssc_curated_reactions.tsv`) only labels the M2/M3/M4
  module of origin; please add a `crosstalk_target_module` field
  and explicitly list the 8 inter-module reactions.

### M3. Hub-score definition is non-standard

Methods §2.7 defines hub score as the geometric mean of betweenness
centrality and degree, normalised to the 99th percentile. This
combines two metrics on very different scales and the normalisation
choice (99th percentile rather than z-score or min-max) is
arbitrary. The downstream Figure 3 and Table 2 priorities depend
critically on this definition. Please either:

- justify the geometric-mean / 99th-percentile choice empirically
  (e.g. show that rankings are stable across choice of metric
  weighting), or
- supplement the analysis with at least one classical centrality
  ranking (eigenvector or PageRank) and confirm that the top-20
  drug-target list overlaps substantially (e.g. ≥15/20).

The current top-3 (SMAD3–SMAD4, fibroblast pro-fibrotic state, NICD1)
are biologically convincing and would survive most reasonable hub
definitions; the test is whether ranks 12–20 (where brontictuzumab
and dupilumab repurposing arguments live) are robust.

### M4. Boolean-readiness claim should be substantiated

§4.5 mentions "future Boolean or ODE modelling" as a roadmap item,
and the README references CaSQ (Aghakhani 2020) as the inference
target. For a methodological paper in npj-SBA this is the natural
next step and reviewers will expect at least a preliminary
demonstration. Please run CaSQ on the integrated XML and report:

- Number of nodes/edges in the inferred Boolean network.
- A perturbation matrix on the top-5 hubs (single-node KO/KI)
  with steady-state changes in the four sink phenotypes.
- Any species that CaSQ could not infer (and why — multi-mer
  complexes, ambiguous reaction logic, etc.).

If CaSQ inference is not feasible by revision deadline, the
"future Boolean" language should be softened to acknowledge it as
a v2.0 deliverable rather than an in-principle capability.

### M5. MINERVA / BioModels deposit

The Discussion §4.1 frames the map as a "community resource", and the
abstract claims compatibility with MINERVA deployment. However, the
v1.0 release plan (ROADMAP.md, post-2026-05-16 pivot) moves MINERVA
deployment to "post-publication stretch". For an npj-SBA reader the
two questions are:

- Will the resource be browseable via MINERVA at publication, or only
  downloadable from GitHub / Zenodo? A read-only MINERVA instance
  hosted at the consortium or by a partner lab is the community
  norm.
- Will the SBML be deposited in **BioModels** with a curated MIRIAM
  identifier? BioModels deposit is the de facto standard for npj-SBA
  systems biology resources.

If neither is possible by acceptance, the manuscript should be
honest that only GitHub + Zenodo are available, and a follow-up
deposition is planned with a target date.

---

## Minor points

### m1. SBML validation reporting

§2.5 reports "0 errors" after fixing 391 L2v4 issues. This is
laudable. Please add the libSBML 5.20 version in the methods
(currently in scripts only), the validator command, and a
sentence on the CI workflow (the `.github/workflows/validate_sbml.yml`
that runs on every push). This will reassure reviewers about
forward-compatibility.

### m2. MI2CAST coverage completeness

`reaction_evidence.tsv` has 244 rows with 198 PMIDs (81%). Methods
§2.4 should disclose this fraction explicitly and explain the
remaining 19% (presumably curator-inference / ECO:0000305 entries).
A table like

| Module | Reactions | With PMID | With ECO≠305 | Tier-1 (curator-inferred) |
|--------|-----------|-----------|---------------|----------------------------|
| M1 |  |  |  |  |
| ...

would make the curation completeness auditable.

### m3. Compartment vocabulary

Table 1 reports 17 compartments; STATUS.md reports 20 compartments.
This discrepancy should be reconciled. A compartment glossary
(perhaps a supplementary table) would also help readers parse the
SBML `__compartment` suffixes (`__cyto`, `__nuc`, `__ext`, `__pm`,
`__er`, `__endo`, `__mito`, `__ecm`, etc.).

### m4. Tabib 2021 cell-type labels vs Gur 2022

Methods §2.6 mentions that GSE195452 used published cell-type labels
directly. For reproducibility please specify whether (a) the
Gur cluster labels were taken from the original supplementary
table or (b) re-derived from the GEO metadata. The downstream Gur
cluster naming (`Fibro_POSTN`, `Peri_RGS5`, etc.) should reference
the table in the Gur publication.

### m5. SSc-specific Tier-1 wiring — automation vs manual

The journal entry of 2026-05-16 notes that `wire_ssc_tier1.py`
applies SSc reactions from a TSV programmatically rather than via
the CellDesigner GUI. For curation provenance please add a
sentence clarifying which reactions in the integrated XML were
hand-drawn in CellDesigner vs auto-wired from the TSV, and how
graphical correctness (layout, glyph orientation) is then verified.

### m6. ECO code distribution

A pie chart or histogram of ECO code distribution across the 244
reactions in `reaction_evidence.tsv` would visually anchor the
evidence-grade claim. The house rule "every reaction must have an
ECO code stricter than 0000305" (from `docs/mi2cast_checklist.md`)
should be tested and reported.

### m7. Reference to CaSQ paper

Aghakhani 2020 is in the bibliography but not cited in the body.
Either cite it (Methods §2.7 or §4.5 when discussing Boolean
modelling) or remove from the corpus.

### m8. Reference 4 (Hinchcliff et al. 2023)

Listed as "in press". Please update with PMID and DOI if available
by revision (likely now indexed). If the reference cannot be
confirmed, replace with another reference.

### m9. Module M3 "21% coverage" framing

The Discussion §4.5 frankly admits the M3 transcriptomic-coverage
gap, which is good. However, the abstract still implies 50% coverage
without flagging the module asymmetry. A one-sentence caveat in the
abstract ("with coverage heterogeneous across modules, M1 65% to
M3 21%") would prevent misreading.

### m10. Patient stratification language

§4.4 proposes that M1/M2 activation scores "could serve as
computational biomarkers". This is testable but currently
unvalidated. Please soften to "hypothesis-generating" pending
external cohort confirmation, and explicitly recommend a
validation cohort (PRESS, ESCISIT, EUSTAR — names matter here).

---

## Specific suggestions for the figures

- **Figure 1.** The global view is rendered with a force-directed
  layout that loses the metro-map readability that Disease Maps
  reviewers expect. Consider a second variant with modules laid out
  in fixed quadrants (M1 top-left, M2 top-right, M3 bottom-left,
  M4 bottom-right), sinks in the centre, crosstalk arcs across
  quadrants. The current rendering reads as a hairball.

- **Figure 2.** The 4-panel heatmap is the strongest evidence in
  the manuscript. Two improvements: (a) annotate each donor row
  with mRSS or disease duration where available; (b) add a
  significance bar (asterisks for Wilcoxon p<0.05/0.01/0.001) to
  the panel headers for the SSc vs HC contrast.

- **Figure 3.** The drug–target subnetwork is informative but
  cluttered. Please separate "approved in SSc" (rituximab,
  tocilizumab, nintedanib) from "investigational"
  (fresolimumab, brontictuzumab, anifrolumab) using glyph shape
  or border colour. Add the DGIdb hit score next to each drug.

---

## Reproducibility check (rapid)

I cloned the repo (commit `dba9e3d`) and ran `make help` to enumerate
the targets. The `Makefile` is well-organised and the
`environment.yml` is pinned. I did not execute `make auto` (this
review was time-limited), but the CI workflow and the `scripts-smoke`
target indicate that an end-to-end run is plausible. I recommend the
authors add a `make figures` smoke artifact (a tiny test PNG) to the
CI so that future contributors cannot silently break the figure
pipeline.

---

## Summary of essential revisions (R1)

1. Quantify novelty against Reactome/KEGG and against Mahoney /
   Taroni consensus networks (M1, M2).
2. Disclose dangling fraction, sink-node connectivity, ECO
   distribution; reconcile 17 vs 20 compartments (m2, m3, m6).
3. Report hypergeometric tests for community–module enrichment;
   add per-crosstalk-reaction PMID table (M2).
4. Robust-rank check of hub score with alternative centrality (M3).
5. Either run CaSQ and report a perturbation matrix, or soften the
   Boolean-readiness language (M4).
6. State the MINERVA / BioModels deposition plan and target date (M5).
7. Soften "patient stratification" language and propose a named
   validation cohort (m10).

These revisions are achievable from the existing artefact set and
would substantially strengthen the manuscript for npj-SBA.

---

*Confidential to the editor: I would be willing to re-review.*
