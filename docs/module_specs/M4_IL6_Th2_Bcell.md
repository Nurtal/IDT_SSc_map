# Module M4 — IL-6 / IL-4 / IL-13 Th2 axis and B-cell crosstalk

> Status: **scoped, not curated**. [[ROADMAP]] § Phase 2, weeks 10–11.
> Targets: ~50 species, ~80 reactions.
> Lead imports: Reactome `R-HSA-1059683` *Interleukin-6 signaling*; RA-map IL-6 and B-cell modules; SYSCID NF-κB.

## 1. Biological scope

Adaptive-immune and Th2-cytokine arm of SSc skin disease. Anchored on validated therapeutic targets (tocilizumab, rituximab) and the Th2 cytokines that drive fibroblast activation (IL-4, IL-13). Captures:

- IL-6 / IL-6R / gp130 / JAK / STAT3.
- IL-4 / IL-4Rα / JAK / STAT6; IL-13 / IL-13Rα1 / JAK / STAT6.
- B-cell receptor signalling (BCR, CD19, BLK, SYK, BTK), CD20 (MS4A1) target.
- Plasma cell differentiation (BLIMP1 / PRDM1, XBP1, IRF4) and autoantibody output (anti-Topo-I, anti-RNA-polymerase-III, anti-centromere).
- Th cell skewing (GATA3 / Th2; TBX21 / Th1; FOXP3 / Treg; RORC / Th17 — relevant but tier-2 here).
- B-cell ↔ fibroblast crosstalk (CD40-CD40L, IL-6, lymphotoxin).

## 2. Tier-1 entities (must include)

| Symbol | Type | Compartment | Role | Source |
|--------|------|-------------|------|--------|
| IL6, IL6R, IL6ST (gp130) | macromolecule | extracellular / plasma_membrane | ligand / receptor | Reactome |
| JAK2, JAK3 | macromolecule | cytosol | kinase | Reactome |
| STAT3 | macromolecule | cytosol / nucleus | TF | Reactome |
| SOCS3, PIAS3 | macromolecule | cytosol / nucleus | negative regulator | Reactome |
| IL4, IL4R, IL13, IL13RA1 | macromolecule | extracellular / plasma_membrane | ligand / receptor | manual + RA-map |
| STAT6 | macromolecule | cytosol / nucleus | TF | Reactome |
| GATA3, TBX21, FOXP3, RORC | macromolecule | nucleus | T-cell lineage TF | manual |
| CD20 (MS4A1) | macromolecule | plasma_membrane | B-cell surface marker | manual |
| CD19, CD22, CD79A, CD79B | macromolecule | plasma_membrane | BCR complex | manual |
| BLK, SYK, BTK, LYN | macromolecule | cytosol | BCR kinases | manual |
| CD40, CD40LG (CD154) | macromolecule | plasma_membrane | costim | manual |
| PRDM1 (BLIMP1), XBP1, IRF4 | macromolecule | nucleus | plasma cell TF | manual |
| TNFRSF17 (BCMA), BAFF (TNFSF13B), APRIL (TNFSF13) | macromolecule | extracellular / plasma_membrane | survival signals | manual |
| autoAb: anti-TOP1, anti-POLR3A, anti-CENP-A/B | macromolecule | extracellular | output | manual |
| NF-κB family (RELA, RELB, NFKB1, NFKB2, REL, NFKBIA, IKBKB) | macromolecule | cytosol / nucleus | TF | Reactome + SYSCID |

### Shared with other modules (resolves to home module on integration)

- **JAK1, TYK2:** home = M1 (canonical IFN-I pathway). Both are recruited downstream of gp130 / IL-6R and IL-4Rα/IL-13Rα1 in this module.

## 3. Sink anchors

- `phenotype_autoantibody_production` (Topo-I / RNA-pol-III / ACA).
- Crosstalk edge into `phenotype_myofibroblast_activation` (IL-13 / STAT6 / fibroblast).

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Tocilizumab | IL-6R | focuSSced (positive on FVC, negative on mRSS) |
| Sarilumab | IL-6R | exploratory |
| Rituximab | CD20 / MS4A1 | RECITAL trial; SSc-ILD use |
| Belimumab | BAFF | exploratory |
| Romilkimab | IL-13 | trial (SSc) |
| Dupilumab | IL-4Rα | repurposing rationale |
| Inebilizumab | CD19 | exploratory |

## 5. Crosstalk edges

- **In:** M1 — IFN-I → pDC / B-cell class switching.
- **Out:** M2 — IL-6 / STAT3 → fibroblast pro-fibrotic transcription; IL-4 / IL-13 / STAT6 → ECM transcription.
- **Out:** M3 — endothelial chemokines (covered in M3); B-cell-driven endothelial inflammation.

## 6. Tier-2 / Tier-3 candidates

- Tfh / IL-21 axis (Tfh cells → germinal centre B-cell help).
- IL-17 / Th17 axis (RORC, IL17A/F, IL17RA).
- IL-23 / IL-23R.
- Complement axis (C1q-C9) in SSc vasculopathy / autoAb effector.
- TLR2/4 on fibroblasts (DAMPs → fibroblast).

## 7. Open questions / for expert review

- [ ] Whether to model plasma cells as a separate compartment from B cells.
- [ ] Granularity of T-cell subsets: do we draw Th2/Th17/Treg explicitly or collapse to "T-helper" with state variables for lineage TFs?
- [ ] Inclusion of CXCL13 / germinal-centre niche signals.
