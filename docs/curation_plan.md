# Curation plan — v1.0 of the SSc-MIM

> Sub-plan inside [ROADMAP.md](../ROADMAP.md). Written 2026-05-16 by the lead curator acting as stand-in for the co-author's biological decisions, on the explicit instruction that **everything is reversible**. Co-author overrides at the post-hoc review.

## Why this document exists

The user direction: *"essaie de répondre seul aux questions de curations […] présenter un livrable concret de bout en bout même si on doit revenir sur certains points a posteriori."* Translation: act as the curator, build a v1.0 the co-author can override, don't get blocked on every biology call.

This plan defines the rules I use to make those calls.

## Position statement

The Reactome imports give the integrated map the **canonical signalling backbone**. They are well-curated, PMID-cited, MI2CAST-annotatable. They are also **not SSc-specific** — they describe IFN / TGF-β / Notch / IL-6 / PDGF in the general human cell context. The remaining work is to wire the SSc layer **on top of** that backbone:

1. SSc-specific entities (CXCL4, POSTN, COMP, CTGF, FRA-2, …) that the Reactome imports don't carry.
2. SSc-specific reactions that connect generic signalling to SSc disease phenotype (e.g., SMAD3 → COL1A1 transcription is canonical biochemistry; *"in SSc dermal fibroblasts, SMAD3 → COL1A1 is elevated and pirfenidone reduces this"* is the SSc-specific claim).
3. Sink phenotype nodes (myofibroblast activation, ECM deposition, vascular remodeling, autoAb output) so every Tier-1 species terminates somewhere disease-meaningful.
4. Inter-module crosstalk reactions that the canonical imports omit by construction (CXCL4 → fibroblast; TGF-β → EndMT; IL-13/STAT6 → ECM).

## Scope rules

- **Periphery:** skin fibrosis in dcSSc. Lung / kidney / GI / vascular peripheries are out of scope for v1.0.
- **Granularity:** per `docs/curation_guidelines.md` § 6 — one reaction per ligand-receptor binding, one per kinase-substrate pair, one per TF-target transcription. No multi-step collapsing unless intermediates are absent.
- **Compartments:** fixed vocabulary (`docs/curation_guidelines.md` § 3).
- **Naming:** HGNC primary symbol for genes/proteins; phosphoforms encoded as state variables (`@P`) on the substrate, not as separate species. Reactome's `p-X` species in the imports remain as legacy (already documented in `docs/import_pilot.md`); new reactions use the state-variable convention.

## Citation strategy

Three tiers of confidence, all explicit in `reaction_evidence.tsv`:

| Tier | ECO code | When to use | Marker for co-author |
|------|----------|-------------|----------------------|
| Strong | `ECO:0000314` (direct assay) or `ECO:0000353` (physical interaction) | I'm confident the cited PMID directly assays this exact mechanism, in a SSc-relevant context where possible | none — confident |
| Moderate | `ECO:0000270` (expression pattern) or `ECO:0000315` (mutant phenotype) | The PMID supports the existence + direction but not the exact mechanism | `notes` column: "supports direction, mechanism inferred" |
| Inference | `ECO:0000305` (curator inference) | I know the canonical biology; the cited PMID is a review or a related-mechanism paper; an SSc-specific direct-assay PMID likely exists but I haven't verified it | `notes` column: "co-author to upgrade PMID" |

The co-author re-grades each reaction at the review session. The `notes` column makes the upgrade queue obvious.

## Reaction-density targets per module

The Reactome imports already contribute 175 reactions. SSc-specific additions target ~50-70 reactions to get to a credible v1.0 density (~225-245 reactions total, comfortably inside the 300-450 target band from `docs/scoping_notes.md`).

| Module | Reactome contribution | SSc-specific target | Rationale |
|--------|----------------------|---------------------|-----------|
| M1 IFN-I | 25 | 10-12 | cGAS-STING-IRF3 axis + CXCL4 modulation + TLR/MyD88 inputs |
| M2 TGF-β / fibrosis | 77 | 20-25 | latent TGF-β activation + SMAD3 → ECM transcription battery + FRA-2 + autocrine loops + ECM cross-linking |
| M3 EndoMT / vasculopathy | 39 | 12-15 | endothelin axis + NO/sGC/cGMP + TGF-β → SNAI → CDH5 loss + HIF1A/VEGF inputs |
| M4 IL-6 / Th2 / B-cell | 34 | 10-12 | IL-4/IL-13 → STAT6 → ECM; plasma cell differentiation; autoAb output |
| Crosstalk (inter-module) | 0 | 5-8 | the 14 declared edges from `docs/crosstalk_matrix.md`, distilled |

## Phenotype sink anchors

Every Tier-1 species in the map must reach one of these in ≤6 graph steps. The names are normative — used as IDs and rendered on figures.

| ID | Compartment | Anchors |
|----|-------------|---------|
| `phenotype_myofibroblast_activation` | cell | ACTA2 transcription induced, contractile phenotype |
| `phenotype_ECM_deposition` | ecm | net new collagen/fibronectin-EDA/matricellular load |
| `phenotype_vascular_remodelling` | cell | capillary loss, intimal proliferation, altered vasomotor tone |
| `phenotype_autoAb_production` | extracellular | plasma cell secretion of anti-Topo-I / anti-RNApol-III / ACA |
| `phenotype_ISG_signature` | nucleus | already exists in the M1 import as `ISG_signature__nuc` |

Five sinks total. The four new ones (myofibroblast, ECM, vascular, autoAb) need to be added as Phenotype-class species in the integrated map and wired as products of the most downstream reactions.

## Reaction format

Reactions live in `curation/ssc_curated_reactions.tsv` as the source of truth. Columns:

| Column | Meaning |
|--------|---------|
| `reaction_id` | unique id, format `ssc_<module>_<NNN>` |
| `module` | M1 / M2 / M3 / M4 / crosstalk |
| `type` | SBGN-PD process type (transcription / phosphorylation / binding / state_change / translocation / catalysis / degradation) |
| `mechanism` | one-line biological description |
| `reactants` | semicolon-separated species ids |
| `products` | semicolon-separated species ids |
| `modifiers` | catalysts / regulators (TFs, kinases acting on the reaction without being consumed) |
| `pmid` | one or more PMIDs, semicolon-separated |
| `evidence_code` | ECO code |
| `ssc_relevance` | what makes this an SSc-specific claim |
| `notes` | freeform — typically "co-author to upgrade PMID" or a caveat |

`scripts/wire_ssc_tier1.py` reads this TSV and applies it to `SSc_MIM_integrated.xml`. The TSV is the curator's working surface; the XML is the consequence.

## Species creation policy

When a TSV reaction references a species id:

1. If the id is already in the integrated map → use as is.
2. If the id matches one of the 88 stubs in `curation/celldesigner/ssc_additions_template/` → add the stub to the integrated map and use it.
3. If the id is none of the above → create it as a new species, deriving compartment from the id suffix (`__cyto`, `__nuc`, `__ext`, `__ecm`, etc.) and type from the id form (uppercase HGNC-like → macromolecule; lowercase → small molecule; `phenotype_*` → Phenotype).

This way the curator can introduce new SSc-specific entities (e.g., the four sink phenotypes) directly from the TSV without editing the XML by hand.

## Success metrics for v1.0

| Metric | Today | v1.0 target |
|--------|-------|-------------|
| Total species | 385 | 470-500 |
| Total reactions | 175 | 230-250 |
| Reactions PMID-cited | 158 (90%) | ≥95% |
| Sink-node dangling fraction | 126 / 385 = 33% | ≤15% |
| Hubs reflecting SSc biology | top hubs are canonical complexes only | top hubs include ACTA2 / COL1A1 / SMAD3 / CTGF |
| `make preflight` blocking failures | 0 | 0 |
| `make preflight` advisories | 1 (dangling) | 0 or 1 (allowed if dangling < 15%) |

## Out of scope for v1.0 (queued for v1.1 or co-author review)

- ECO upgrades for the `ECO:0000305` reactions (co-author handles in review).
- BMP / Activin axis (M2 tier-2).
- Wnt / β-catenin in fibroblasts (M2 tier-2).
- Complement cascade in vasculopathy (M3 tier-3).
- Th17 / IL-17 axis (M4 tier-2).
- Tfh / IL-21 axis (M4 tier-3).
- Cellular-scale features beyond skin (lung, GI, kidney, PAH).

These remain on `docs/module_specs/M*.md` as Tier-2/3 entries; v1.1 picks them up.

## Process

1. Curator (acting stand-in) tranches Q1/Q2/Q3 → `docs/curation_decisions.md`.
2. Curator builds `curation/ssc_curated_reactions.tsv` per the strategy above.
3. `scripts/wire_ssc_tier1.py` applies the TSV to the integrated map.
4. `make preflight + network + sink-check + figures + abstract` re-runs the AUTO lane on the curated map.
5. v1.0 commit + tag (after the user fills `CITATION.cff` / `.zenodo.json` placeholders).
6. Co-author review post-hoc; every change is a normal git diff on the TSV → re-run wiring → re-run AUTO → re-tag if needed.
