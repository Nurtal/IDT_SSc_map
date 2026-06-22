# Audit — `claude-reclassify` edges without a PMID (2026-06-19)

Triggered by a reviewer question ("FOXP3→COL1A1 negative control had a fabricated citation;
ssc_crosstalk_001 IFN-I→fibroblast has *no* source — where does it come from?"). All 10 edges with
`provenance = claude-reclassify` and no PMID were audited against the **real** literature (PubMed
E-utils esearch + abstracts read manually — no fabricated citations).

## Verdict
The reclassified edges are **not fabricated**: each maps to genuine SSc literature. The missing PMID
reflected their nature as **modelling nodes** (conceptual bridges / phenotype sinks), not invention.

## Conceptual bridges (4) — real citations attached
Evidence codes updated and `pmid` / `candidate_pmids` / `notes` filled in
`curation/ssc_curated_reactions.tsv`. `curation_status` kept `conceptual_bridge` (the app still flags
"KEEP — conceptual (verify reclassification)").

| reaction | claim | verdict | PMID attached | other support |
|---|---|---|---|---|
| `ssc_crosstalk_001` | IFN-I → pro-fibrotic fibroblast (M1→M2) | **supported, contested** — kept ECO:0000305 + caveat | **35686918** (Rheumatology 2023, macrophage DNA→POLR3A/STING/type-I-IFN→SSc fibroblast activation) | 40374521 (cGAS→myofibroblast, Eur Respir J 2025); **CAVEAT 31436583** (Curr Opin Rheumatol 2019 — IFN-I role in skin fibrosis debated, protective vs pathogenic) |
| `ssc_crosstalk_003` | IFN-I → pDC / B-cell (M1→M4) | **supported** → ECO:0000270 | **40341181** (RMD Open 2025, type-I-IFN amplifies autoreactive B-cell differentiation) | 38553621 (Immunol Rev 2024, pDC = major IFN-I producers via NA/TLR) |
| `ssc_M3_013` | EndMT cell → myofibroblast pool | **strongly supported** → ECO:0000270 | **28062404** (Ann Rheum Dis 2017, EndoMT→α-SMA myofibroblast in SSc dermis; already cited in M3_011/012) | 33772754 (Clin Exp Immunol 2021 review) |
| `ssc_crosstalk_007` | EndMT perivascular fibroblast → myofibroblast pool (M3→M2) | **strongly supported** → ECO:0000270 | **28062404** (as above) | 33772754 |

Verbatim sentences for `crosstalk_001` and `crosstalk_003` were extracted (PMC full-text) by the
quote miner; the two EndMT edges keep the PMID/title (no confident auto-sentence — reviewer reads
the source).

## Phenotype aggregations (6) — left as definitional sinks (no single source expected)
`ssc_M1_012` (ISG signature), `ssc_M2_021` (myofibroblast activation), `ssc_M2_022` (ECM
deposition), `ssc_M3_014` (vascular remodelling), `ssc_M4_011` & `ssc_M4_015` (autoAb production).
These are not mechanistic interactions but **phenotype/sink nodes** that aggregate marker sets into a
clinical readout (mRSS, IFN signature, capillaroscopy…), per Disease-Map convention. No PMID is
expected; a review citation can be attached later if desired.

## Method
`esearch` (db=pubmed, relevance) + `efetch` abstracts via NCBI E-utils; abstracts read to judge
support. PMIDs above were verified to exist and to concern the claimed biology. See
[[never-fabricate-citations]].
