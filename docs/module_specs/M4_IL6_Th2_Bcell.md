# Module M4 — Cytokines (IL-6 / IL-4 / IL-13)

> Status: **scoped + curated**. [[ROADMAP]] § Phase 2, weeks 10–11.
> The B-cell / autoreactivity content was split out into **[[M5_Bcell_autoreactivity]]** on
> 2026-06-25; this module now covers the cytokine→fibroblast axis only.
> Lead imports: Reactome `R-HSA-1059683` *Interleukin-6 signaling*; RA-map IL-6 module; SYSCID NF-κB.

## 1. Biological scope

The cytokine arm of SSc skin disease: pro-fibrotic and Th2 cytokines that signal to fibroblasts.
Anchored on validated therapeutic targets (tocilizumab; the IL-13/IL-4 biologics romilkimab and
dupilumab). Captures:

- IL-6 / IL-6R / gp130 / JAK / STAT3.
- IL-4 / IL-4Rα / JAK / STAT6; IL-13 / IL-13Rα1 / JAK / STAT6.
- Th cell skewing (GATA3 / Th2; TBX21 / Th1; FOXP3 / Treg; RORC / Th17 — relevant but tier-2 here).
- Cytokine → fibroblast / ECM transcription (the M4→M2 crosstalk rationale).

B-cell receptor signalling, plasma-cell differentiation, BAFF–BCMA and autoantibody output now live in
**M5 (B-cell & autoreactivity)**.

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
| NF-κB family (RELA, RELB, NFKB1, NFKB2, REL, NFKBIA, IKBKB) | macromolecule | cytosol / nucleus | TF | Reactome + SYSCID |

> B-cell / plasma-cell / autoantibody entities (CD19/CD20/CD22/CD40, BCR kinases, BAFF–BCMA,
> PRDM1/XBP1/IRF4, autoantigens) moved to the **M5** Tier-1 table on the split.

### Shared with other modules (resolves to home module on integration)

- **JAK1, TYK2:** home = M1 (canonical IFN-I pathway). Both are recruited downstream of gp130 / IL-6R and IL-4Rα/IL-13Rα1 in this module.

## 3. Sink anchors

- Crosstalk edge into `phenotype_myofibroblast_activation` and ECM deposition (IL-6/STAT3 and
  IL-13/STAT6 → fibroblast). (The autoantibody endpoint is now anchored in **M5**.)

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Tocilizumab | IL-6R | focuSSced (positive on FVC, negative on mRSS) |
| Sarilumab | IL-6R | exploratory |
| Romilkimab | IL-13 | trial (SSc) |
| Dupilumab | IL-4Rα | repurposing rationale |

(B-cell-directed agents — rituximab, belimumab, inebilizumab — are in **M5**.)

## 5. Crosstalk edges

- **In:** M1 — IFN-I priming of the cytokine milieu.
- **Out:** M2 — IL-6 / STAT3 → fibroblast pro-fibrotic transcription; IL-4 / IL-13 / STAT6 → ECM transcription.
- **Out:** M5 — IL-6 supports plasmablast survival / germinal-centre output (cytokine → B-cell).

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
