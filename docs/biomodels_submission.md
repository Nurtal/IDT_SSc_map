# BioModels submission package — SSc-MIM v1.1 (E11 / R1-M5 / R3-M4)

> Draft submission package, ready for the lead author to upload at
> https://www.ebi.ac.uk/biomodels/submit. Generated 2026-05-21 against
> the v1.1 revision branch.

## Quick start (for the submitter)

1. Open https://www.ebi.ac.uk/biomodels/submit
2. Sign in with the EBI/Elixir account holding the lead-author affiliation.
3. Choose **New submission** → **Non-curated model** → **SBML**.
4. Upload `curation/celldesigner/SSc_MIM_integrated.biomodels.xml`
   (the MIRIAM-annotated variant; see "MIRIAM coverage" below).
5. Paste the cover letter below into the submission notes.
6. Set licence to **CC-BY-4.0** to match `LICENSE` and `.zenodo.json`.
7. Tag the submission ID in `STATUS.md` under "Open external items" once
   received.

## Cover letter (paste into BioModels submission notes)

> **Title:** SSc-MIM — Molecular Interaction Map of skin fibrosis in
> diffuse cutaneous systemic sclerosis (v1.1)
>
> **Type:** Disease map (curated, SBGN-Process-Description-compliant
> molecular interaction map).
>
> **Authors:** Nathan Foulquier (LBAI, UMR 1227 Inserm, CHU Brest;
> ORCID 0000-0003-4620-2794), co-author REPLACE_ME (rheumatology
> co-author to confirm at v1.1 submission).
>
> **Companion manuscript:** *npj Systems Biology and Applications*, in
> revision (cycle v1.1, simulated peer-review run 2026-05-20). The
> manuscript references this BioModels entry in the Data Availability
> Statement.
>
> **Scope:** First curated MIM of systemic sclerosis. 526 species, 260
> reactions, 17 biologically meaningful compartments. Four modules
> (M1 type-I IFN / cGAS-STING; M2 TGF-β / fibroblast-to-myofibroblast;
> M3 EndoMT / vasculopathy; M4 IL-6 / IL-4 / IL-13 / B-cell) plus an
> SSc-Tier-1 layer of 85 hand-curated SSc-specific reactions supported
> by 355 unique PubMed identifiers and annotated with ECO evidence
> codes.
>
> **Validation:** SBML L2V4, 0 errors under libSBML 5.21 (`make
> validate`). `make preflight` reports 1 advisory (17.9% of species
> dangling from a sink phenotype; flagged as remaining curation
> backlog).
>
> **MIRIAM annotation:** Each species carries a `bqbiol:isVersionOf`
> CVTerm referring to identifiers.org/hgnc.symbol/SYMBOL where an HGNC
> mapping is known (206/526 species = 39 %; the remainder are
> compartment-tagged complexes, sinks, or non-protein entities and
> have only the `bqbiol:hasTaxon → identifiers.org/taxonomy/9606`
> term). Reaction-level CVTerms are populated indirectly via the
> SSc-curated reaction PubMed identifiers in
> `curation/annotations/reaction_evidence.tsv`. Programmatic injection
> via `scripts/inject_miriam.py`; round-trip-verified at write time.
>
> **Code & data:** GitHub repository
> https://github.com/Nurtal/IDT_SSc_map under MIT (code) + CC-BY-4.0
> (map content); pinned at git tag `v1.1`. RO-Crate manifest at the
> repo root. Zenodo DOI for the v1.1 release: REPLACE_ME (to be minted
> on tag push). Input scRNA-seq datasets mirrored at Zenodo DOI
> REPLACE_ME (SHA-256 manifest in `data/MIRROR.md`).
>
> **Companion network analysis:** Reproducible via `make network` +
> `make overlay-multi` from a fresh clone. Headline output:
> 38 functional communities (greedy modularity), top-20 hub species
> ranked by `hub_score = z(degree) + z(betweenness)` (see Supplementary
> Figure S1 for the robustness analysis against eigenvector and
> PageRank centralities).
>
> **Suggested curator review focus:** (a) cross-references on the 85
> SSc-curated reactions (`curation/ssc_curated_reactions.tsv`),
> (b) the four phenotype-sink species
> (`phenotype_myofibroblast_activation__cell`,
> `phenotype_ECM_deposition__cell`,
> `phenotype_vascular_remodelling__cell`,
> `phenotype_ISG_signature__nuc`), and (c) the inter-module crosstalk
> reactions enumerated in Supplementary Table S1
> (`manuscript/supplementary/S1_crosstalk_reactions.tsv`).

## Files to attach

| File | Purpose |
|---|---|
| `curation/celldesigner/SSc_MIM_integrated.biomodels.xml` | The MIRIAM-annotated SBML to submit (1.6 MB). |
| `curation/celldesigner/SSc_MIM_integrated.miriam_report.json` | Coverage report (206 HGNC + 526 taxonomy CVTerm resources). |
| `curation/annotations/species_annotations.tsv` | Source of the HGNC/taxonomy mapping injected. |
| `curation/annotations/reaction_evidence.tsv` | Reaction-level PMID/ECO table (244 rows, 198 with PMID). |
| `manuscript/supplementary/S1_crosstalk_reactions.tsv` | Per-row crosstalk evidence (E5, 8 rows). |
| `README.md` + `LICENSE` | Project description and licensing. |

## MIRIAM coverage

The injection step (`scripts/inject_miriam.py`) writes:

- `bqbiol:isVersionOf identifiers.org/hgnc.symbol/<SYMBOL>` for every
  species with a curated HGNC symbol (206/526 = 39 %).
- `bqbiol:hasTaxon identifiers.org/taxonomy/9606` for every species
  (526/526 = 100 %; the model is human-only).

Reasons for the < 100 % HGNC coverage:

| Species class | Count | Why no HGNC | Plan |
|---|---|---|---|
| Phenotype sinks (e.g. `phenotype_myofibroblast_activation__cell`) | ~4 | Not a gene; conceptual readout | Annotate with GO/Disease Ontology in v1.2 |
| Complexes (e.g. `TGFB1_TGFBR2_TGFBR1__cyto`) | ~80 | Composite entity; constituents have HGNC | Add composite annotations referencing each component HGNC in v1.2 |
| Compartment-tagged forms of the same protein (e.g. `SMAD3__cyto`, `SMAD3p__cyto`, `SMAD3p_SMAD4__nuc`) | ~200 | Already covered via their unmodified counterpart; the duplicates currently carry the canonical HGNC tag too | Already covered by the injection (`hgnc.symbol/SMAD3` appears on every SMAD3-derived species) |
| Cleavage products / RNA / metabolites (e.g. NICD1, dsDNA, cGAMP) | ~30 | Not protein-coding gene-level entities | Map to UniProt isoform / ChEBI in v1.2 (`curation/annotations/species_annotations.tsv` columns `uniprot`/`chebi` are already in the schema, currently empty) |

The companion manuscript (Methods §2.4) notes the BioModels-targeted
MIRIAM injection as the v1.1 deliverable for R1-M5 / R3-M4.

## Status

- 2026-05-21: package draft created; MIRIAM injection script run;
  output verified by `make validate` (libSBML L2V4 0 errors); 206 HGNC
  + 526 taxonomy CVTerm resources confirmed by round-trip read.
- **Pending external step**: lead-author upload at
  https://www.ebi.ac.uk/biomodels/submit + BioModels submission ID
  pasted back into this file and `STATUS.md`.
- Once the BioModels ID is received it must be cited in:
  - manuscript Methods §2.9 (reproducibility envelope)
  - manuscript Data Availability Statement
  - `.zenodo.json` `related_identifiers`
  - `ro-crate-metadata.json` (`hasPart` entry for the MIRIAM SBML)
  - `STATUS.md` (Open external items)
