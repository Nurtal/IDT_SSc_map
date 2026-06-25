# Module M5 — B-cell & autoreactivity

> Status: **scoped + curated** (10 SSc-specific reactions). Split from the old M4 ("IL-6/Th2/B")
> on 2026-06-25 to separate the B-cell / autoreactivity arm from the cytokine arm (now M4).
> **Independently validated** — see [[M5_validation]] (`analysis/overlay/M5_validation.md`).
> Lead imports: RA-map / SYSCID B-cell modules; manual SSc curation.

## 1. Biological scope

The adaptive-humoral, autoreactive arm of SSc. SSc is defined clinically by near-universal
autoantibodies (anti-topoisomerase-I / Scl-70, anti-RNA-polymerase-III, anti-centromere), and B-cell
depletion (rituximab) is an active therapeutic strategy — so autoreactivity is a first-class output of
the map, not a side branch. Captures:

- B-cell receptor (BCR) signalling: CD79A/CD79B → SYK / BLK / LYN → BTK → downstream activation.
- B-cell surface / co-stimulation: CD19, CD20 (MS4A1), CD22, CD40 / CD40LG.
- Plasma-cell differentiation: PRDM1 (BLIMP1), XBP1, IRF4.
- Survival / niche signals: BAFF (TNFSF13B), APRIL (TNFSF13) → BCMA (TNFRSF17).
- Autoantibody output against SSc autoantigens (TOP1, POLR3A, CENP-A/B).

## 2. Tier-1 entities (must include)

| Symbol | Type | Compartment | Role | Source |
|--------|------|-------------|------|--------|
| CD19, CD22, CD79A, CD79B | macromolecule | plasma_membrane | BCR complex / co-receptor | manual |
| MS4A1 | macromolecule | plasma_membrane | CD20 B-cell surface marker | manual |
| BLK, SYK, BTK, LYN | macromolecule | cytosol | BCR kinases | manual |
| CD40, CD40LG | macromolecule | plasma_membrane | costimulation | manual |
| PRDM1, XBP1, IRF4 | macromolecule | nucleus | plasma-cell differentiation TF | manual |
| TNFRSF17 | macromolecule | plasma_membrane | BCMA survival receptor | manual |
| TNFSF13B, TNFSF13 | macromolecule | extracellular | BAFF / APRIL survival ligands | manual |
| TOP1, POLR3A, CENPB | macromolecule | extracellular | autoantigen targets (anti-Scl-70 / RNApol-III / ACA) | manual |

## 3. Sink anchors

- `phenotype_autoantibody_production` (anti-Topo-I / anti-RNA-pol-III / anti-centromere) — the
  primary M5 output endpoint.

## 4. Druggable handles

| Drug | Target | Status in SSc |
|------|--------|---------------|
| Rituximab | CD20 / MS4A1 | RECITAL/DESIRES trials; SSc-ILD use |
| Inebilizumab | CD19 | exploratory |
| Belimumab | BAFF / TNFSF13B | exploratory (anti-BAFF) |
| Telitacicept | BAFF + APRIL (TACI-Fc) | emerging |
| CD19 CAR-T | CD19 | early-phase, refractory SSc |

## 5. Crosstalk edges

- **In:** M1 — IFN-I → pDC priming and B-cell class switching (M1→M5).
- **In:** M4 — IL-6 supports plasmablast survival / germinal-centre output (cytokine→B-cell).
- **Out:** autoantibody-mediated effects feed the autoreactivity endpoint and, via immune-complex
  signalling, can prime fibroblasts (candidate M5→M2 edge, for expert review).

## 6. Tier-2 / Tier-3 candidates

- Tfh / IL-21 axis (germinal-centre B-cell help).
- CXCL13 / germinal-centre niche signals.
- Complement axis (C1q–C9) as autoantibody effector in SSc vasculopathy.
- FcγR-bearing effector engagement of immune complexes.

## 7. Validation (B-cell compartment, not whole tissue)

B/plasma cells are too rare in whole-tissue pseudobulk to surface in an AUCell ranking, so M5 is
scored on a **B/plasma-restricted pseudobulk** (`scripts/build_bplasma_pseudobulk.py`):

- **Internal** (skin scRNA-seq, Gur cohort): M5 higher in SSc (0.085 vs 0.047, p=0.046) and the only
  significant module in that compartment → specific to autoreactivity.
- **External** ([GSE45536](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE45536), 99 SSc / 24 HC
  whole blood): M5 separates SSc from HC (p=1.3×10⁻⁴); the autoantigen core TOP1/CENPB is strongly
  elevated (p=1.7×10⁻¹⁰), while circulating B/plasma abundance is reduced (peripheral lymphopenia).
- IFN (M1) positive control is elevated in SSc in both datasets, validating the method.

## 8. Open questions / for expert review

- [ ] Model plasma cells as a separate compartment / cell state from B cells?
- [ ] Is the M5→M2 immune-complex→fibroblast edge supportable, or should it stay a candidate?
- [ ] Stratify M5 readout by autoantibody serotype (anti-Scl-70 vs ACA vs ARA) when metadata allows.
