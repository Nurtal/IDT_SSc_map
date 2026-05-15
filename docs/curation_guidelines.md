# Curation guidelines — SSc-MIM

> Adapted from Mazein et al. *Front Bioinform* 2023 and the Disease Maps Project conventions.
> The goal of this document is to make curation **deterministic**: two curators following these rules should produce the same map.

## 1. Tooling

- **Diagram editor:** CellDesigner v4.4 (SBGN Process Description).
- **Format:** SBML L2v4 with CellDesigner annotations on save.
- **Validation:** every commit triggers `validate_sbml` CI workflow.

## 2. Naming convention

| Entity type | Identifier source | Example |
|-------------|------------------|---------|
| Gene / protein (human) | HGNC primary symbol | `TGFB1`, `SMAD3`, `IFNAR1` |
| Proteoform / modified form | HGNC + state | `SMAD3_phos` (pSer423/425) |
| Complex | participant symbols joined with `:` | `SMAD2:SMAD3:SMAD4` |
| Small molecule | ChEBI ID + short label | `chebi_15377_H2O` |
| Drug | INN, lowercase | `tocilizumab`, `nintedanib` |
| Phenotype (sink) | `phenotype_<slug>` | `phenotype_myofibroblast_activation` |

The CellDesigner `id` attribute must be **unique across the integrated map**. Use the canonical symbol; rely on `name` for human-readable labels including state info.

## 3. Compartments

Fixed vocabulary. Add a new compartment only with a documented decision in `docs/decisions/`.

| Compartment | Label |
|-------------|-------|
| `extracellular` | extracellular space |
| `ECM` | extracellular matrix (subset of extracellular, kept distinct for fibrosis biology) |
| `plasma_membrane` | plasma membrane |
| `cytosol` | cytosol |
| `nucleus` | nucleus |
| `ER` | endoplasmic reticulum |
| `endosome` | endosomal compartment |
| `mitochondrion` | mitochondrion |

Cell-type-specific compartments are encoded as a **prefix** on the compartment label only when needed for clarity in mixed-cell modules (e.g. `EC_cytosol` for endothelial-cell cytosol in M3 where fibroblast and endothelial cytosols co-exist).

## 4. SBGN Process Description usage

Follow standard SBGN-PD glyph mapping:

- **Macromolecule** for proteins.
- **Simple chemical** for small molecules / lipids.
- **Complex** for multi-protein assemblies.
- **Nucleic acid feature** for mRNAs when explicitly modelled.
- **Phenotype** for sink nodes.
- **Process** for reactions; **omitted process** for grouped multistep reactions where intermediates are not modelled.
- **Modulation arcs:** stimulation (open triangle), catalysis (filled circle), inhibition (T-bar), necessary stimulation (double triangle).

## 5. State variables

- Phosphorylation: `P` at the specific residue (e.g. `SMAD3@S423`).
- Ubiquitination: `Ub` (no chain detail unless functionally critical).
- Acetylation: `Ac` at residue.
- Cleaved: separate species with `_cleaved` suffix.
- Bound to ligand: prefer a complex node over a state variable.

## 6. Reaction granularity

Match the granularity of Mazein 2023:

- **Receptor activation:** one reaction per ligand–receptor binding event.
- **Phosphorylation cascades:** one reaction per kinase–substrate pair, **not** one reaction per residue (collapse residues into a single state variable list).
- **Transcription:** one reaction `TF → mRNA(target)` per target, with the TF as catalyst.
- **Translation:** modelled only when functionally important (e.g. for an immediate-early gene).
- **Translocation:** explicit when the localisation change is functionally meaningful.

## 7. Crosstalk and inter-module edges

Inter-module edges are first-class citizens. Each crosstalk reaction must:

1. Be tagged in `reaction_evidence.tsv` with `module = crosstalk` and a `crosstalk_modules` column listing the two modules.
2. Be coloured / annotated in CellDesigner notes to show provenance.
3. Cite at least one SSc-specific PMID demonstrating the edge in human SSc tissue or a high-quality SSc model.

## 8. Annotation contract

Every species must have:

- HGNC symbol (or ChEBI / Drug INN for non-protein).
- UniProt accession (for proteins, human canonical unless otherwise noted).
- Compartment.
- Module assignment.

Every reaction must have:

- Reaction type (per SBGN-PD).
- Participants (with role: substrate / product / catalyst / modulator).
- Mechanism (free text, ≤2 sentences).
- ≥1 PMID with an evidence code (see `docs/mi2cast_checklist.md`).
- Module assignment.

## 9. Common pitfalls (lessons from RA-map / SjD map)

- **Duplicate species** with different `id` but same HGNC symbol after integration. Always check after merge.
- **Floating species** with no inbound or outbound edge after manual additions. Add a `dangling` check before each commit.
- **Sign drift** between Cytoscape export and CellDesigner notation. Always preserve sign during round-trip.
- **Citation rot.** PMIDs from review papers should be replaced by the primary source when known.

## 10. Versioning

- `v0.x` during pre-submission curation; minor bumps per module completion.
- `v1.0` at ACR abstract submission tag (`acr2026-submission`).
- `v1.x` post-submission corrections.
- `v2.0` for additional peripheries (lung, GI, vascular, kidney).
