# SSc-MIM

<p class="subtitle">A curated molecular interaction map of diffuse cutaneous systemic sclerosis — construction, patient-data validation, and endotypes</p>

<div class="meta">
Literature-curated topology · MI2CAST-annotated · SBML L2V4 · validated against four single-cell cohorts<br>
<strong>568 species · 308 reactions · 5 modules · 133 SSc-specific curated reactions</strong><br>
Source deck: <code>docs/presentation.md</code> → <code>make presentation</code> · figures auto-embedded · updated 2026-06-26
</div>

---

## Why SSc-MIM

- Systemic sclerosis (SSc) is an autoimmune fibro-inflammatory disease — skin/organ fibrosis, vasculopathy, immune dysregulation — with **no approved disease-modifying therapy**.
- The field lacks a **mechanistic map** tying together the core molecular circuits, which has hampered rational target prioritisation.
- **SSc-MIM** is the first curated, SBGN-compliant Molecular Interaction Map for **diffuse cutaneous SSc**, built in CellDesigner and annotated to MI2CAST.

| Quantity | Value |
|---|---|
| Molecular species / reactions / compartments | **568 · 308 · 20** |
| Biological modules (+ crosstalk) | **5** (M1–M5) |
| Hand-curated SSc-specific reactions | **133** (126 with a primary PMID) |
| Patient single-cell datasets overlaid | **4** — 197 donors (121 SSc / 76 HC) |
| Map species measurable in patient data | **82.6 %** |
| Interactions queued for expert review | **143** |

---

## Map architecture — five modules + crosstalk

<div class="cols" markdown="1">
<div markdown="1">

- **M1 — Type-I IFN & cGAS–STING.** The innate-immune ignition circuit (ISGs, IRF3/7, STING).
- **M2 — TGF-β / fibroblast→myofibroblast.** The fibrotic core (SMAD2/3/4, collagens, POSTN, COMP).
- **M3 — EndoMT & vasculopathy.** Notch/endothelin, pericyte–endothelial transition.
- **M4 — IL-6 / IL-4 / IL-13 cytokines.** The Th2/JAK-STAT cytokine axis.
- **M5 — B-cell & autoreactivity.** BCR, BAFF/APRIL-BCMA, autoantigens (TOP1, CENPB).
- **Crosstalk layer** wires the modules; **6 phenotype endpoints** (sinks) close the map.

*Topology is literature-derived; patient omics are layered on top — they do not define the structure.*

</div>
<div markdown="1">

![Five-module map](figures/F1_global_MIM_quadrant.png)

</div>
</div>

---

## Standards, provenance & honesty

- **Format & tooling:** CellDesigner v4.4, SBGN Process Description, **SBML Level 2 Version 4**; SBML validity enforced by **CI on every push**.
- **Annotation standard:** **MI2CAST** (identifiers, evidence ECO codes, taxonomy, provenance).
- **Two provenance layers — the honest denominator:**
  - *Reactome backbone* (imported, harmonised) vs *SSc-specific curated layer* (the novel content, **133 reactions**).
- **Tiered citation policy (GO-style ECO codes):** 126/133 carry a primary PMID — 73 at direct-assay codes, the rest at expression / physical-interaction / review-traceable codes.
- **Citation integrity:** an AI verdict pass flagged **28 reactions citing an off-topic PMID** (canonical biology, wrong reference); each was replaced with a PMID **verified against live PubMed** — *no citation is ever fabricated*.

---

## The novel content — 133 SSc-specific curated reactions

<div class="cols" markdown="1">
<div markdown="1">

**By module**

| Module | Reactions |
|---|---|
| M2 — TGF-β / fibroblast | 58 |
| M3 — EndoMT / vasculopathy | 27 |
| M1 — Type-I IFN | 19 |
| M4 — IL-6/IL-4/IL-13 | 11 |
| M5 — B-cell / autoreactivity | 10 |
| Crosstalk | 8 |

</div>
<div markdown="1">

**How an interaction is added (gated, never speculative)**

- Authoritative PMIDs → fetch OA full text → extract a **verbatim deciding sentence**.
- Candidate edge passes **five anti-nonsense gates G0–G4** (`validate_edge_candidates.py`): identity, grounding, polarity, module-fit, duplication.
- A **negative-control fixture** (fabricated edge) must be rejected by the grounding gate — proving the gate works.
- **Contradiction detection** routes conflicting literature; an **AI verdict pass** gives an advisory validate / revise / caution call.
- **Human ratification is binding** — the curator/co-author decides.

</div>
</div>

---

## Patient data — four single-cell cohorts

| GEO | Reference | Tissue | Donors (SSc/HC) |
|---|---|---|---|
| **GSE195452** | Gur *et al.* **Cell** 2022 (PMID 35381199) | Skin (multiome) | 154 (97 / 57) |
| **GSE138669** | Tabib *et al.* **Nat Commun** 2021 (PMID 34282151) | Skin | 22 (12 / 10) |
| **GSE128169** | Morse *et al.* **Eur Respir J** 2019 (PMID 31221805) | Lung (ILD) | 13 (8 / 5) |
| **GSE210395** | GEO (no linked publication) | PBMC | 8 (4 / 4) |

- **Total: 197 donors (121 SSc / 76 HC), 266,884 cells.** Raw archives are **SHA-256-pinned** (`data/MIRROR.md`) for a reproducible input envelope.
- The omics **ground, validate and read out** the map — they **do not define its topology**.

---

## Overlay pipeline & coverage = 82.6 %

<div class="cols" markdown="1">
<div markdown="1">

- Re-process each dataset from raw counts with **scanpy** (QC, Leiden, cell-type labels — validated vs **CellTypist**, κ = 0.92).
- **Pseudobulk per donor**; SSc-vs-HC DE with a **mixed-effects negative-binomial GLM** + BH-FDR (q = 0.05).
- Map DE genes onto species → **coverage 82.6 %** (195/236):
  M1 82 · M2 87 · M3 79 · M4 72 · **M5 100** · Tier-1 80 %.
- **Per-donor AUCell** turns each patient into a **5-module activation vector**.

</div>
<div markdown="1">

![AUCell module activation across four cohorts](figures/F2_multi_overlay_aucell.png)

</div>
</div>

---

## Biological readout — the map behaves like SSc

- **Type-I IFN (M1) is significantly elevated in SSc skin** under sign-blinded AUCell:
  Gur **p = 6.4×10⁻⁸** (∆ = +0.077), Tabib **p = 5.8×10⁻³** — a known SSc hallmark, recovered de novo.
- **M2 (TGF-β)** is active in the fibroblast/myofibroblast compartment across skin *and* lung (FAP, POSTN, CTHRC1, collagens).
- **M3 vasculopathy** surfaces in pericytes (**EDN1 ↑, ANGPT2 ↑**), not in whole-tissue endothelium — consistent with EndoMT being a diluted minority state.
- Coverage is reported across a **(significance × effect-size) grid** (53 % robust → 82.6 % permissive), framed as *corroboration*, not validation: a signalling map encodes post-translational events that transcriptomics cannot see.

---

## M5 — B-cell & autoreactivity, independently validated

<div class="cols" markdown="1">
<div markdown="1">

- M5 was split out of the old M4 once its **B-cell / autoantibody** content was disentangled from the IL-6 cytokine core.
- Whole-tissue AUCell for M5 ≈ 0 (B/plasma cells are rare) → validated on a **B/plasma-restricted pseudobulk**:
  - **Internal (Gur):** M5 ScS 0.085 vs HC 0.047, **p = 0.046** — the only significant module in that compartment.
  - **External (GSE45536, 99 ScS / 24 HC):** M5 separates ScS/HC **p = 1.3×10⁻⁴**; autoantigen core (TOP1/CENPB) **p = 1.7×10⁻¹⁰**.

</div>
<div markdown="1">

![M5 validation](figures/F7_M5_validation.png)

</div>
</div>

---

## Endotypes — patients as module-activation vectors

<div class="cols" markdown="1">
<div markdown="1">

- Each donor's **5-module AUCell vector** is a quantitative, **map-grounded** readout of which circuits are active.
- This exposes candidate **molecular endotypes** (e.g. IFN-high vs fibrosis-dominant) directly interpretable in terms of the curated biology.
- Patient stratification against clinical outcomes (mRSS, autoantibody class) is **reserved as a follow-up**: the public GEO cohorts carry **no per-donor clinical metadata** (the pipeline is built and tested, awaiting an annotated cohort).

</div>
<div markdown="1">

![Endotype profiles](figures/F6_endotype_profiles.png)

</div>
</div>

---

## Druggable hubs — from topology to targets

<div class="cols" markdown="1">
<div markdown="1">

- Network analysis (centrality + Leiden communities; **1011 edges, 39 communities**) surfaces hubs that match known SSc biology:
  **pro-fibrotic state, TGFB1, TGF-β receptor, SMAD3–SMAD4, ISG core**.
- Hubs are cross-referenced against **DGIdb** for druggability and recalibrated against **SSc clinical-trial reality** (e.g. nintedanib, tocilizumab, JAK inhibitors).
- The map is exported as a **Boolean network** (CaSQ → SBML-qual) — substrate for a future dynamic-perturbation study.

</div>
<div markdown="1">

![Druggable targets](figures/F3_druggable_targets.png)

</div>
</div>

---

## Reproducibility & open release

- **Everything is scripted & re-runnable:** `make auto` rebuilds every TSV in `analysis/` and every figure in `figures/` from a clean clone.
- **Container & provenance:** Dockerfile, `environment.yml`, **RO-Crate** metadata, pytest + CI (SBML validation on every push).
- **Inputs pinned:** the four raw scRNA-seq archives are SHA-256-verified (`data/MIRROR.md`).
- **BioModels-ready** SBML (MIRIAM CVTerms injected); **Zenodo DOI** to be minted at the `v1.0` tag.
- **License:** CC-BY-4.0 (map) / MIT (code).

---

## Status & what's next

<div class="cols" markdown="1">
<div markdown="1">

**Done (automated lanes)**

- Integrated map, SBML QC, 5-module split (M5 validated).
- Real scRNA-seq overlay on 4 cohorts, coverage 82.6 %, AUCell endotypes.
- Network/druggability, all figures, manuscript (npj-SBA revision v1.1), reviewer swipe-deck app (143 interactions).

</div>
<div markdown="1">

**Remaining — human-only**

- Expert / co-author **adjudication of the 143 interactions**.
- CellDesigner GUI visual round-trip.
- Fill the `.zenodo.json` co-author slot.
- `git tag v1.0` + Zenodo webhook (one-time).

</div>
</div>

*Full written companion: `docs/SSc_MIM_construction_and_validation.md`. Live status: `STATUS.md`.*
