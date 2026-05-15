# Module M2 — TGF-β / SMAD / fibroblast → myofibroblast transition

> Status: **scoped, not curated**. [[ROADMAP]] § Phase 2, weeks 6–7.
> Targets: ~80 species, ~120 reactions.
> Lead imports: Reactome `R-HSA-2173789` *TGF-beta receptor signaling activates SMADs*, `R-HSA-186797` *Signaling by PDGF*; RA-map fibroblast block.

## 1. Biological scope

The central fibrotic axis. Captures canonical TGF-β / SMAD signalling, non-canonical TGF-β branches (MAPK, PI3K, Rho), and the autocrine / paracrine loops that drive fibroblast → myofibroblast transition and ECM deposition.

Includes:

- TGF-β activation from latent complex (LAP, LTBP, integrins αvβ3/αvβ6, thrombospondin-1).
- TGF-β receptor signalling (TGFBR1, TGFBR2 → SMAD2/3/4).
- SMAD-dependent transcription (COL1A1, COL3A1, FN1-EDA, ACTA2, CTGF/CCN2).
- Non-canonical signalling: MAPK p38, JNK, ERK; PI3K/AKT; RhoA/ROCK; mechano-transduction via YAP/TAZ.
- Myofibroblast markers (ACTA2, TAGLN, MYH11, CNN1).
- ECM (collagens, fibronectin-EDA, POSTN, COMP, TNC, LOX).
- PDGFR-α/β signalling (autocrine fibroblast loop).

## 2. Tier-1 entities (must include)

| Symbol | Type | Compartment | Role | Source |
|--------|------|-------------|------|--------|
| TGFB1, TGFB2, TGFB3 | macromolecule | extracellular / ECM | ligand | Reactome |
| LAP (TGFB1 N-terminal fragment) | macromolecule | ECM | latent form | manual |
| LTBP1 | macromolecule | ECM | sequestrator | manual |
| ITGAV:ITGB6, ITGAV:ITGB3 | complex | plasma_membrane | TGF-β activator (mechanical) | manual |
| THBS1 | macromolecule | ECM | TGF-β activator | manual |
| TGFBR1, TGFBR2 | macromolecule | plasma_membrane | receptor | Reactome |
| SMAD2, SMAD3 | macromolecule | cytosol → nucleus | R-SMAD | Reactome |
| SMAD4 | macromolecule | cytosol → nucleus | co-SMAD | Reactome |
| SMAD6, SMAD7 | macromolecule | cytosol | I-SMAD | Reactome |
| SMURF1, SMURF2 | macromolecule | cytosol | E3 ligase | Reactome |
| PDGFRA, PDGFRB | macromolecule | plasma_membrane | receptor | Reactome |
| PDGFA, PDGFB, PDGFC, PDGFD | macromolecule | extracellular | ligand | Reactome |
| MAPK14 (p38), MAPK8 (JNK), MAPK1/3 (ERK) | macromolecule | cytosol / nucleus | kinase | Reactome |
| PIK3CA / AKT1 | macromolecule | cytosol | kinase | Reactome |
| RHOA, ROCK1, ROCK2 | macromolecule | cytosol | small GTPase / kinase | manual |
| YAP1, WWTR1 (TAZ) | macromolecule | cytosol / nucleus | mechano-TF | manual |
| ACTA2 (αSMA) | macromolecule | cytosol | myofibroblast marker | manual |
| COL1A1, COL1A2, COL3A1, COL5A1, COL5A2 | macromolecule | extracellular / ECM | ECM | manual |
| FN1 (EDA isoform) | macromolecule | ECM | ECM | manual |
| POSTN, COMP, TNC | macromolecule | ECM | matricellular | manual (POSTN: PMID 22186371; COMP: PMID 22197582) |
| CTGF / CCN2 | macromolecule | extracellular / ECM | matricellular + signalling | manual (PMID 16007098 SSc skin) |
| LOX, LOXL2 | macromolecule | ECM | cross-linker | manual |
| FRA-2 (FOSL2) | macromolecule | nucleus | SSc-relevant TF | manual (Tsk1, Fra2-Tg models; PMID 19638503) |
| TBX2 | macromolecule | nucleus | SSc-relevant TF | manual |

## 3. Sink anchors

- `phenotype_myofibroblast_activation` — ACTA2⁺, contractile, proliferative state.
- `phenotype_ECM_deposition` — increased collagen + FN1-EDA + matricellular load.

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Pirfenidone | TGF-β / fibroblast (multifactorial) | trials (LOTUSS, focuSSced add-on) |
| Nintedanib | PDGFR, FGFR, VEGFR | SENSCIS positive, approved for SSc-ILD |
| Fresolimumab | TGF-β | exploratory trial in SSc skin |
| Romilkimab | IL-13 (M4 crosstalk into fibroblast) | trial, see also M4 |
| Tipifarnib, BMS-986020, etc. | LPA / autotaxin axis | exploratory |

## 5. Crosstalk edges into / out of M2

- **In:** M1 → IFN-I primes fibroblast pro-fibrotic transcriptional state.
- **In:** M3 → EndoMT-derived perivascular fibroblasts increase the myofibroblast pool.
- **In:** M4 → IL-6 / STAT3 and IL-4 / IL-13 / STAT6 augment ECM transcription.
- **Out:** M3 → TGF-β drives endothelial-to-mesenchymal transition.
- **Internal autocrine loops:** TGF-β → CTGF → fibroblast; TGF-β → PDGF → PDGFR autocrine.

## 6. Tier-2 / Tier-3 candidates

- BMP / Activin branch: BMPR1A/1B, BMPR2, ACVR1, NOG, GDF15.
- Wnt / β-catenin axis (CTNNB1, AXIN2) in SSc fibroblast persistence.
- TGFBI (βig-h3), DCN, BGN (proteoglycans), MMP1/2/9/13, TIMP1/2/3 (ECM remodelling).
- IGF-1R / IRS axis.

## 7. Open questions / for expert review

- [ ] Granularity of the latent TGF-β activation step (one reaction vs three).
- [ ] Whether to include the FoxF1 / FoxF2 axis (controversial in SSc fibroblasts).
- [ ] Confirm POSTN / COMP / TNC are best placed in M2 (versus a generic ECM compartment).
