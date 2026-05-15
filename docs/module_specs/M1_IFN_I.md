# Module M1 — Type-I interferon signaling

> Status: **scoped, not curated**. [[ROADMAP]] § Phase 2, weeks 4–5.
> Targets: ~60 species, ~80 reactions.
> Lead import: Reactome `R-HSA-909733` *Interferon alpha/beta signaling*.

## 1. Biological scope

Captures the canonical type-I interferon (IFN-α and IFN-β) signalling cascade and its downstream interferon-stimulated gene (ISG) response, as observed in SSc skin and blood. Includes:

- Nucleic-acid sensing upstream (cGAS-STING, RIG-I/MAVS, TLR3/7/8/9) — entry points relevant to SSc autoantigen-driven IFN induction.
- IFNAR1/2 ligation and JAK1/TYK2 activation.
- STAT1 / STAT2 / IRF9 (ISGF3) assembly and nuclear translocation.
- ISG transcription.
- Negative regulators (USP18, SOCS1, PTPN1/2).
- Crosstalk inputs from CXCL4 / PF4 (van Bon 2014).

## 2. Tier-1 entities (must include)

| Symbol | Type | Compartment | Role | Source |
|--------|------|-------------|------|--------|
| IFNA1, IFNA2 | macromolecule | extracellular | ligand | Reactome |
| IFNB1 | macromolecule | extracellular | ligand | Reactome |
| IFNAR1, IFNAR2 | macromolecule | plasma_membrane | receptor | Reactome |
| JAK1 | macromolecule | plasma_membrane → cytosol | kinase | Reactome |
| TYK2 | macromolecule | plasma_membrane → cytosol | kinase | Reactome |
| STAT1, STAT2 | macromolecule | cytosol / nucleus | TF | Reactome |
| IRF9 | macromolecule | cytosol / nucleus | TF cofactor | Reactome |
| ISGF3 (STAT1:STAT2:IRF9) | complex | nucleus | TF complex | Reactome |
| IRF7 | macromolecule | cytosol / nucleus | TF | manual |
| cGAS (MB21D1), STING1 (TMEM173) | macromolecule | cytosol / ER | sensor | manual |
| RIG-I (DDX58), MAVS | macromolecule | cytosol / mitochondrion | sensor | manual |
| TLR3, TLR7, TLR8, TLR9 | macromolecule | endosome | sensor | manual |
| TRIF (TICAM1), MyD88 | macromolecule | cytosol | adaptor | manual |
| TBK1, IKBKE | macromolecule | cytosol | kinase | manual |
| USP18, SOCS1, PTPN1, PTPN2 | macromolecule | cytosol | negative regulator | manual |
| CXCL4 / PF4 | macromolecule | extracellular | SSc-specific IFN modulator | manual (Van Bon 2014, PMID 24382179) |

## 3. ISG output anchors (sink contributors)

At least **5** of: IFI44, IFI44L, IFIT1, IFIT3, ISG15, MX1, MX2, OAS1, OAS2, OAS3, RSAD2, IRF7, IFI27.

Connected to: `phenotype_ISG_signature`.

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Anifrolumab | IFNAR1 | trials in SLE; rationale extension to SSc |
| Tofacitinib, baricitinib, ruxolitinib | JAK1/2/3 | repurposing rationale |
| Cerdulatinib, fostamatinib | SYK / SSc-relevant kinases | exploratory |

## 5. Crosstalk edges out of M1

- → M2 (TGF-β / fibrosis): IFN-I priming of fibroblast pro-fibrotic state.
- → M2: CXCL4 / PF4-mediated fibroblast activation (autocrine on IFN-stimulated DCs).
- → M4 (IL-6 / Th2 / B cell): IFN-I → plasmacytoid DC → B-cell class-switch.

## 6. Tier-2 / Tier-3 candidates (include if time allows)

- IRF1, IRF3, IRF5 (gene-specific IFN responses).
- DDX21, DDX60, ZBP1 (additional nucleic-acid sensors).
- ADAR, OAS-RNAseL pathway (translational repression).
- IFNL1/2/3 (type-III IFN crosstalk).

## 7. Open questions / for expert review

- [ ] Is the cGAS-STING entry point relevant in SSc skin specifically (vs blood)? Cite primary evidence.
- [ ] Confirm CXCL4 / PF4 placement (IFN modulator vs separate node feeding M2).
- [ ] Decide if pDC is modelled explicitly or kept as a black-box upstream "IFN production" process.
