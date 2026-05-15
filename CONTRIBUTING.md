# Contributing to SSc-MIM

Thank you for considering a contribution to the Skin Fibrosis Molecular Interaction Map for diffuse cutaneous systemic sclerosis. The repository follows the conventions of the [Disease Maps Project](https://disease-maps.io/) and the recommendations of Mazein et al. 2023.

This document explains:

1. [How to propose a curation change](#1-how-to-propose-a-curation-change)
2. [How to review (clinical or methodological)](#2-how-to-review-clinical-or-methodological)
3. [Pull-request rules](#3-pull-request-rules)
4. [Coding and documentation style](#4-coding-and-documentation-style)
5. [Co-authorship policy](#5-co-authorship-policy)
6. [Code of conduct](#6-code-of-conduct)

---

## 1. How to propose a curation change

Open an issue using the **curation_request** template (`.github/ISSUE_TEMPLATE/curation_request.md`). Required fields:

- **PMID** (or DOI) of the supporting paper.
- **Claimed interaction** — entity A → entity B, sign (activation / inhibition / binding / state change), mechanism if known.
- **Evidence excerpt** — quoted text or figure caption.
- **Proposed module** — M1 / M2 / M3 / M4 / cross-module.
- **MI2CAST fields you can pre-fill** (see `docs/mi2cast_checklist.md`).

Curation requests are triaged weekly. Accepted requests become commits with one of:

- `curate(M1): add IFNAR1 → JAK1 phosphorylation`
- `curate(M2): refine TGFBR2 → SMAD2 (citation update)`
- `curate(crosstalk): IFN-α primes fibroblast pro-fibrotic state`

Always cite the PMID in the commit message.

## 2. How to review (clinical or methodological)

Open an issue using the **expert_review** template (`.github/ISSUE_TEMPLATE/expert_review.md`). Reviews can be scoped:

- Whole map (overview pass).
- One module (deep dive).
- A specific mechanism or claim.

Reviewers should attach a short PDF or markdown summary of comments, classified `must-fix` / `nice-to-have` / `discussion`. All comments are tracked publicly and resolved in `docs/review_log.md`.

## 3. Pull-request rules

Every PR that touches `curation/celldesigner/**` **must**:

1. Update `curation/annotations/species_annotations.tsv` for every new or modified species (HGNC symbol, UniProt ID, Ensembl ID, compartment, module).
2. Update `curation/annotations/reaction_evidence.tsv` for every new or modified reaction (participants, mechanism, PMID, evidence code, module).
3. Pass the `validate_sbml` GitHub Actions workflow (libSBML errors block merge).
4. Reference the originating issue (`Closes #NN` or `Refs #NN`).
5. Include at least one PMID per new reaction in the commit body.

PRs that touch only `analysis/**` (scripts, notebooks) must additionally:

1. Pin every new dependency in `environment.yml`.
2. Set random seeds for any stochastic step (UMAP, Leiden, sampling).
3. Be re-runnable from a clean conda env (`mamba env create -f environment.yml`).

## 4. Coding and documentation style

- **Naming.** HGNC primary symbol for genes/proteins; UniProt accession for proteoforms or non-human entities. SBO terms for reaction types where applicable.
- **Compartments.** Vocabulary fixed in `docs/curation_guidelines.md` (`extracellular`, `plasma_membrane`, `cytosol`, `nucleus`, `ECM`, `endosome`, `ER`, `mitochondrion`).
- **Citations.** Cite PMIDs in `reaction_evidence.tsv`; the corresponding BibTeX entry must exist in `curation/pubmed_corpus.bib`.
- **Markdown.** GitHub-flavoured. No tabs; LF line endings.
- **Python.** Format with `ruff format`; lint with `ruff check`. Type hints encouraged.
- **R.** Tidyverse style; one file per analysis step.

## 5. Co-authorship policy

Co-authorship on the ACR 2026 abstract and the methodological paper is offered to contributors meeting at least one of the following thresholds (adapted from CRediT and ICMJE):

- **Curation:** ≥10 substantive curation commits (with PMIDs) or curation of at least one full sub-module.
- **Expert review:** completion of a documented review of ≥1 module with `must-fix` comments resolved.
- **Translational analysis:** non-trivial contribution to the omics overlay, network analysis, or figure pipeline.
- **Tooling:** non-trivial contribution to deployment / CI / reproducibility.

In all cases the contributor must have approved the final manuscript before submission. Acknowledgements (without authorship) are offered for smaller contributions; ask if uncertain.

## 6. Code of conduct

Be kind, be precise, cite your sources. Disagreements about biology are resolved by reference to the primary literature; disagreements about scope or priorities are resolved by the maintainers in consultation with the clinical referent. Personal attacks, harassment, or sustained off-topic behaviour are grounds for removal from the project.
