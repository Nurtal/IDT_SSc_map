# Scoping notes — SSc-MIM v0.1

> Living document. Every scope decision lands here with a date, who decided it, and the reason.
> Reference: [[ROADMAP]] § Phase 1, week 1.

## 1. Disease and periphery

- **Disease:** Systemic sclerosis (SSc), subtype **diffuse cutaneous SSc (dcSSc)**.
- **Periphery of v0.1:** skin fibrosis. Lung (ILD), vascular (PAH), GI, kidney are out of scope for v0.1 and explicitly scheduled as v0.x future modules.
- **Rationale:** skin is the most-studied compartment, mRSS is a tractable clinical readout, scRNAseq cohorts are available (Tabib 2021).

## 2. Modules

| ID | Module | Status | Notes |
|----|--------|--------|-------|
| M1 | IFN-I signaling (IFNAR / JAK-STAT / ISG) | scoped | Reactome import + SSc add-ons |
| M2 | TGF-β / SMAD / fibroblast → myofibroblast | scoped | Reactome + RA-map import + SSc add-ons |
| M3 | EndoMT and vasculopathy | scoped | Mostly manual (WikiPathways scaffold) |
| M4 | IL-6 / IL-4 / IL-13 / B-cell crosstalk | scoped | RA-map import + SSc adaptation |

## 3. Sink (output) phenotypes

Analogous to the eight phenotype anchors of RA-map. Each Tier-1 species must reach at least one sink via a path of length ≤ 6.

1. **Myofibroblast activation** — αSMA⁺ (ACTA2⁺), proliferative, contractile fibroblast.
2. **ECM deposition** — collagens (COL1A1, COL3A1, COL5A1), fibronectin-EDA (FN1), POSTN, COMP.
3. **Vascular remodelling** — capillary loss, intimal thickening, endothelin axis activation.
4. **ISG signature** — induction of canonical interferon-stimulated genes (IFI44, IFI44L, IFIT1, IFIT3, ISG15, MX1, OAS1/2/3, RSAD2).

## 4. SSc-specific entity priorities (Tier-1 across modules)

- **Chemokines and damage signals:** CCL2, CCL18, CXCL4 / PF4, CXCL10.
- **Matricellular / ECM:** POSTN, COMP, CTGF / CCN2, TNC.
- **Transcription factors:** FRA-2 (FOSL2), TBX2, SNAI1, SNAI2, ZEB1/2, RUNX1/2.
- **Autoantigen-linked pathways:** Topoisomerase-I (TOP1, anti-Scl-70), RNA-polymerase-III (POLR3A), centromere proteins (CENP-A/B for limited disease — included for completeness but not core to dcSSc skin).
- **Autocrine loops:** TGF-β1 → CTGF → fibroblast; IL-6 → STAT3 → IL-6.

## 5. Volumetric target

| Quantity | Target | Source |
|---------|--------|--------|
| Species | 200–300 | RA-map per-module average |
| Reactions | 300–450 | RA-map per-module average |
| References (PMIDs) | 150–250 | proportional to reactions |
| Import / manual split | 60–70 % / 30–40 % | reuse-strategy table in README |

## 6. Decisions log

| Date | Decision | Decided by | Rationale | Reversible? |
|------|----------|------------|-----------|-------------|
| 2026-05-15 | Periphery = skin fibrosis only for v0.1 | lead curator, pending clinical co-author | mRSS readout, scRNAseq availability | yes (extend in v0.x) |
| 2026-05-15 | Four modules M1–M4 as in README | lead curator, pending clinical co-author | Match RA-map structure for re-use | yes |
| 2026-05-15 | Output phenotypes fixed (4 sinks) | lead curator | Anchors for sink-node connectivity check | yes |

## 7. Open items / waiting on

- [ ] Kickoff meeting with SSc rheumatologist (Phase 1 / week 1).
- [ ] Co-authorship confirmation email (file under `docs/`).
- [ ] Reactome pilot import outcome (see `docs/import_pilot.md`).
- [ ] Omics dataset decision (see `docs/omics_decision.md` — created in week 3).
