# Reactions without a primary PMID — resolution log (L3-01, issue #3)

Date: 2026-11-10. Rule: each row ends with a **verified** primary PMID or is kept as **declared**
curator inference (`ECO:0000305`). No PMID is invented (`CONTEXT.md`, "Curator inference").

| Reaction | Module | Claim | Outcome | Basis |
|---|---|---|---|---|
| `ssc_M2_012` | M2 | SMAD3:SMAD4 induces POSTN transcription | declared inference, **untested** backlog (was `to_complete` / `ECO:0000270`, an undeclared status) | PubMed, 3 queries (periostin/POSTN × SMAD3 × TGF-β, fibroblast, promoter/transcription), 31 abstracts read. None shows SMAD3-dependent POSTN transcription (no SMAD3 loss-of-function, no promoter binding). Closest: PMID 24004653 and 29916554, TGFBR1-dependent periostin induction correlated with p-SMAD3. Kept as candidates with 16815144 (IL-4/IL-13 route), not cited. The mechanism question in the row's notes stays open. |
| `ssc_M2_019` | M2 | FRA-2 binds TBX2 cooperatively | declared inference, **untested** (was `confirmed` without PMID, a contradiction the evidence-depth guard rejects) | Three searches on 2026-06-29 found no source; the mis-cited PMID was removed then. Keeping or removing the reaction is a curation decision left to the curator. |
| `ssc_M1_012` | M1 | ISG response converges on the ISG-signature phenotype | kept, `phenotype_aggregation` | Definitional sink: names a phenotype from its components, so no single experiment can be its source. |
| `ssc_M2_021` | M2 | ACTA2+ activated fibroblast → myofibroblast phenotype | kept, `phenotype_aggregation` | idem |
| `ssc_M2_022` | M2 | ECM gene deposition → ECM-deposition phenotype | kept, `phenotype_aggregation` | idem |
| `ssc_M3_014` | M3 | NO loss + EDN1 + capillary loss → vascular remodelling phenotype | kept, `phenotype_aggregation` | idem |
| `ssc_M4_011` | M5 | plasma-cell autoantibody secretion → autoantibody phenotype | kept, `phenotype_aggregation` | idem; module M5 by its `module` column (ID predates the split) |
| `ssc_M4_015` | M4 | T-helper balance shapes autoantibody output | kept, `phenotype_aggregation` | idem |

Result: **0 PMIDs assigned, 8 rows declared.** The evidence-depth guard (`make evidence-lint`, CI job
`evidence-depth`), which had been failing on main since the 2026-06-29 citation fixes, passes again:
133 rows triaged, 125 cited, 2 untested backlog.
