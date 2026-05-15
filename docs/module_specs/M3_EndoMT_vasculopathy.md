# Module M3 — Endothelial-to-mesenchymal transition (EndoMT) and vasculopathy

> Status: **scoped, not curated**. [[ROADMAP]] § Phase 2, weeks 8–9.
> Targets: ~60 species, ~90 reactions.
> Lead imports: WikiPathways EndMT (WP_3942 *Mechanisms of endothelial-to-mesenchymal transition (EndMT)*); selected Reactome vascular entries.
> **Highest manual fraction** (~70–80 %).

## 1. Biological scope

SSc-specific bridge between vasculopathy and fibrosis. Captures:

- Vascular injury and hypoxia (HIF1A axis) in SSc skin microvasculature.
- Endothelin axis (EDN1 → EDNRA / EDNRB → vasoconstriction + pro-fibrotic).
- NO / sGC / cGMP axis (eNOS → sGC → cGMP → PDE5).
- Notch / Snail / Slug / ZEB transcriptional EndMT programme.
- Loss of endothelial identity (CDH5/VE-cadherin, PECAM1/CD31, VWF) and gain of mesenchymal markers (CDH2/N-cadherin, ACTA2, FAP, FSP1/S100A4).
- Perivascular fibroblast emergence and feeding into the M2 myofibroblast pool.

## 2. Tier-1 entities (must include)

| Symbol | Type | Compartment | Role | Source |
|--------|------|-------------|------|--------|
| EDN1 | macromolecule | extracellular | ligand | manual |
| EDNRA, EDNRB | macromolecule | plasma_membrane | receptor | manual |
| NOS3 (eNOS) | macromolecule | plasma_membrane | enzyme | manual |
| NO (chebi_16480) | small_chemical | extracellular | signal molecule | manual |
| GUCY1A1 / GUCY1B1 (sGC) | macromolecule | cytosol | enzyme | manual |
| cGMP (chebi_16356) | small_chemical | cytosol | second messenger | manual |
| PDE5A | macromolecule | cytosol | enzyme | manual |
| HIF1A, HIF1B (ARNT) | macromolecule | cytosol → nucleus | TF | manual |
| VEGFA, VEGFR2 (KDR) | macromolecule | extracellular / plasma_membrane | ligand / receptor | manual |
| CDH5 (VE-cadherin), PECAM1 (CD31), VWF, TIE2 (TEK) | macromolecule | plasma_membrane | EC identity markers | manual |
| NOTCH1, NOTCH3, JAG1, DLL4, RBPJ | macromolecule | plasma_membrane / nucleus | Notch pathway | manual |
| SNAI1, SNAI2, ZEB1, ZEB2, TWIST1 | macromolecule | nucleus | EMT/EndMT TFs | manual |
| CDH2 (N-cadherin) | macromolecule | plasma_membrane | mesenchymal marker | manual |
| FAP, S100A4 (FSP1) | macromolecule | plasma_membrane / cytosol | mesenchymal markers | manual |
| ANGPT1, ANGPT2 | macromolecule | extracellular | ligand | manual |
| PTGS2 (COX-2) | macromolecule | ER | enzyme (prostanoid synthesis) | manual |
| TBXA2R | macromolecule | plasma_membrane | receptor (vasoconstrictor / platelet) | manual |

### Shared with other modules (resolves to home module on integration)

- **ACTA2 (αSMA):** home = M2 (myofibroblast marker). Referenced here as the convergent output of EndoMT.

## 3. Sink anchors

- `phenotype_vascular_remodelling` — intimal proliferation, capillary loss, altered vasomotor tone.
- Crosstalk edge into `phenotype_myofibroblast_activation` via mesenchymal-converted ECs.

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Bosentan, macitentan, ambrisentan | EDNRA / EDNRB | approved for PAH; SSc digital ulcers (bosentan) |
| Riociguat | sGC | approved for PAH; SSc trials (RISE-SSc) |
| Sildenafil, tadalafil | PDE5 | Raynaud, digital ulcers |
| Iloprost, treprostinil, epoprostenol | prostacyclin | SSc Raynaud / PAH |
| Selexipag | prostacyclin receptor (IP) | PAH |

## 5. Crosstalk edges

- **In:** M2 — TGF-β drives EndMT (TGFBR1 → SMAD3 + non-canonical → SNAI1/SNAI2).
- **In:** M1 — IFN-I → endothelial activation and microvascular damage (cite SSc-specific evidence).
- **Out:** M2 — perivascular fibroblast emergence feeds the myofibroblast pool.
- **Out:** M4 — endothelial chemokines (CXCL10, CXCL11) recruit Th1/Th2.

## 6. Tier-2 / Tier-3 candidates

- BMP9 / ALK1 / ENG (hereditary haemorrhagic telangiectasia axis — relevant in SSc telangiectasias).
- ROBO4, ROCK1/2 vascular permeability.
- THY1, MEOX1, NRP1 (additional mesenchymal markers).
- Inflammasome activation in ECs (NLRP3, GSDMD).

## 7. Open questions / for expert review

- [ ] Are we modelling EndMT as a binary phenotype or a graded set of intermediate states?
- [ ] Inclusion of pericyte transition pathway (PDGFRB⁺ pericytes → myofibroblast) — likely belongs in M2 but trafficks via M3 signals.
- [ ] Whether to model EDA-fibronectin in M3 (vascular pro-fibrotic) or M2 only.
