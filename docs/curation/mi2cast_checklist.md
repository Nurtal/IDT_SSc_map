# MI2CAST checklist — SSc-MIM

> [MI2CAST](https://mi2cast.org/) is the minimum information standard for the annotation of causal statements. It is used in the Disease Maps Project and is the contract we use here.
> Reference: Vinaixa & Touré et al. *Bioinformatics* 2021.

## What MI2CAST requires per causal statement (= per reaction in our map)

| # | Field | Description | Where it lives in this repo |
|---|-------|-------------|-----------------------------|
| 1 | Source entity (regulator) | identifier + biological role | `species_annotations.tsv` + `reaction_evidence.tsv:participants` |
| 2 | Target entity (regulated) | identifier + biological role | as above |
| 3 | Effect | activation / inhibition / state change / binding / translocation / catalysis / transcription | `reaction_evidence.tsv:type` |
| 4 | Mechanism | how does the regulation occur (e.g. phosphorylation, complex formation) | `reaction_evidence.tsv:mechanism` |
| 5 | Evidence | reference (PMID / DOI) + evidence code (ECO) | `reaction_evidence.tsv:pmid`, `:evidence_code` |
| 6 | Context — biological type | cell type, tissue, organism, condition | `reaction_evidence.tsv:context_biotype` (free text) |
| 7 | Context — experimental | assay, technology, perturbation | `reaction_evidence.tsv:context_assay` |
| 8 | Taxonomy | NCBI taxon | `species_annotations.tsv:taxonomy` (default `9606`) |

## Evidence Code Ontology (ECO) — frequently used codes

| Code | Meaning | When to use |
|------|---------|-------------|
| `ECO:0000314` | direct assay evidence | biochemistry, kinase assay, IP-MS, ChIP-seq |
| `ECO:0000353` | physical interaction evidence | Y2H, co-IP, AP-MS, BioID |
| `ECO:0000270` | expression pattern evidence | RNA-seq, scRNAseq, qPCR |
| `ECO:0000315` | mutant phenotype evidence | KO, KD, CRISPR, dominant-negative |
| `ECO:0000316` | genetic interaction evidence | epistasis, synthetic lethality |
| `ECO:0007053` | high-throughput evidence | omics-scale screen |
| `ECO:0000305` | curator inference | only when no direct primary evidence exists; flag for follow-up |
| `ECO:0000033` | author statement supported by traceable reference | review-cited mechanism, with the review's primary citation captured separately |

## Evidence policy (tiered) — aligned with GO/GOA, not "primary-only"

The gold standard in pathway/interaction curation is the **Gene Ontology Annotation (GO/GOA)**
model, which MI2CAST inherits: **honest, ECO-coded provenance** — *not* "cite a primary paper
for everything". A review that states an established mechanism and traces it to its source is
a **first-class, accepted** evidence category — the Traceable-Author-Statement (TAS) tier,
encoded here as `ECO:0000033`. There is a quality hierarchy (experimental > review-traceable >
curator inference), but a review citation is a legitimate annotation, not a placeholder. The
COVID-19 Disease Map and RA-map both rely heavily on reviews.

The useful distinction is therefore **canonical vs. study-novel**, not review vs. primary:

| Claim type | Minimum acceptable evidence |
|---|---|
| Canonical / textbook mechanism (known receptor, enzyme, TF) | a citation at **`ECO:0000033`** (review, traceable) or stronger — **do not** burn effort upgrading these to primary |
| **SSc-specific novelty — especially inter-module crosstalk** (`module = crosstalk`) | a **primary** citation with an experimental ECO (`0000314` / `0000270` / `0000353` / `0000315`), ideally in an SSc context (see `curation_guidelines.md` §7); **or** an explicit `conceptual_bridge` tag when it encodes a cell-state assertion rather than a molecular interaction |
| Contested / non-consensus claim | primary experimental |

**House rule (replaces the old "stricter-than-0000305 everywhere" rule):** every reaction must
either (a) carry a citation at `ECO:0000033` or stronger, or (b) be **declared** — `untested`
backlog or honest reclassification (`conceptual_bridge` / `phenotype_aggregation`). Pure
curator inference (`ECO:0000305`, no citation) is tolerated **only as declared backlog**.
Crosstalk rows are held to the higher (primary/experimental, or reclassified) bar. The
`make evidence-lint` guard (`scripts/check_evidence_depth.py`) enforces exactly this — it does
**not** demand that canonical review-cited edges be upgraded to primary.

## Recommended SSc-specific context vocabularies

To keep `context_biotype` and `context_assay` clean:

- **Cell types:** `dermal fibroblast`, `myofibroblast`, `keratinocyte`, `vascular endothelial cell`, `pericyte`, `Th2 cell`, `Th17 cell`, `B cell`, `plasma cell`, `pDC`, `mDC`, `macrophage`, `monocyte`.
- **Tissues / source:** `SSc skin biopsy`, `healthy skin biopsy`, `SSc PBMC`, `bleomycin mouse skin`, `Tsk1 mouse skin`, `Fra2 transgenic mouse skin`, `cultured cells`, `iPSC-derived`.
- **Assays:** `scRNAseq`, `bulk RNAseq`, `RT-qPCR`, `WB`, `IHC`, `IF`, `ChIP-seq`, `ATAC-seq`, `ELISA`, `proteomic MS`, `kinase assay`, `reporter assay`, `KO`, `KD`, `CRISPR`, `pharmacological inhibitor`, `pharmacological agonist`, `neutralising antibody`.

## Minimal example

```tsv
reaction_id	type	participants	mechanism	pmid	evidence_code	context_biotype	context_assay	module
R_M2_001	state_change	TGFB1(catalyst);TGFBR1(substrate)>TGFBR1@P_active(product)	Ligand-induced TGFBR1 transphosphorylation by TGFBR2 within the heterotetrameric receptor.	7774572	ECO:0000314	mink lung epithelial cells; SSc dermal fibroblasts	kinase assay; WB	M2
```

## Open items

- [ ] Decide whether to use ECO directly or the simpler `mi-evidence` codes from PSI-MI. **Tentative:** ECO, because it integrates with Disease Maps Project conventions.
- [ ] Add a CI lint that rejects rows missing required fields. **Schedule:** Phase 2 / week 4.
