# Curation decisions — answers to the brief's three questions

> Written by the lead curator on **2026-05-16** as stand-in for the co-author's biological calls, per user direction *"essaie de répondre seul aux questions de curations"*. **Every decision below is reversible**. The co-author overrides at review; each row is a normal git diff on `curation/ssc_curated_reactions.tsv` and a re-run of `scripts/wire_ssc_tier1.py`.

## Q1 — Does the 4-module scope hold ?

**Decision: YES, tel quel.**

Rationale:

- **M1 IFN-I** — independently supported by the IFN signature literature in SSc skin (Tabib 2021, van Bon 2014 PMID 24382179). Defines the inflammatory subset of the Whitfield intrinsic classification. Necessary.
- **M2 TGF-β / fibroblast → myofibroblast** — the central fibrotic axis. Pirfenidone, fresolimumab, romilkimab (via M4 crosstalk), nintedanib (via PDGFR) all converge here. Volumetrically the largest module by design.
- **M3 EndoMT / vasculopathy** — SSc-specific bridge that distinguishes this MIM from PR/SLE maps. SSc vasculopathy (digital ulcers, telangiectasia, PAH precursors) is clinically defining. EndoMT (loss of CDH5 / gain of CDH2 + ACTA2 + FAP) feeds the perivascular fibroblast pool — direct M3→M2 crosstalk.
- **M4 IL-6 / Th2 / B-cell** — anchors the validated SSc trials (focuSSced / tocilizumab, RECITAL / rituximab, SSc trial / romilkimab). Without it the abstract has no "tractable target" handle.

**No reshape needed.** The two refinements I considered and rejected:

- *Add a 5th module: complement / innate ?* Complement is real in SSc vasculopathy (C4d deposits in nailfold capillaroscopy) but the mechanistic literature isn't dense enough yet to warrant a fifth Tier-1 module. Move to v1.1 / v2.0. **Rejected for v1.0.**
- *Merge M3 into M2?* They are biologically continuous (TGF-β drives EndMT) but clinically distinct (Raynaud, digital ulcers, PAH precursors are vascular and have their own drug class — endothelin antagonists, sGC stimulators, prostacyclin analogues). Merging would lose the vascular drug story. **Rejected.**

**Sub-module M3 emphasis:** the original spec gave equal weight to endothelin / NO-sGC / EndMT / Notch. After the analysis (NOTCH1 Reactome import contributes 77 species, hub analysis shows NOTCH1 coactivator complex at #6 hub) I re-weight slightly: **Notch + EndMT are the dominant axes**; endothelin and NO/sGC are real but lighter in the v1.0 wiring. They keep all Tier-1 entities but fewer SSc-specific reactions.

## Q2 — Tier-1 SSc additions, removals, promotions

### M1 — IFN-I

**Add (new SSc-specific reactions, beyond Reactome IFNAR import):**

| Mechanism | Why |
|-----------|-----|
| cGAS (MB21D1) senses cytosolic dsDNA → cGAMP | Drives type-I IFN in SSc skin; rationale for new STING-axis SSc trials |
| STING (TMEM173) activated by cGAMP → TBK1 → IRF3-P → IFN-β | Same |
| TLR3 / TLR7 / TLR9 endosomal sensing → MyD88/TRIF → IRF7-P → IFN production | TLR involvement in SSc (autoimmunity / nucleic acid release) |
| RIG-I (DDX58) → MAVS → IRF3/7 phosphorylation | Cytosolic RNA sensing, third sensor branch |
| **CXCL4 / PF4 → IFN modulation of pDC + direct fibroblast activation** | Van Bon 2014 NEJM PMID 24382179 — flagship SSc-specific finding |
| IRF7 nuclear translocation → IFN-α positive feedback | Closes the IFN amplification loop |
| USP18 / SOCS1 → JAK1 degradation (already-imported negative regulators get explicit reactions) | Negative feedback completeness |

**Keep all Tier-1 from spec.**

**Demote / drop:**
- *Type-III IFN (IFNL1/2/3 crosstalk)* — was Tier-2 already; stays Tier-2.
- *DDX21 / DDX60 / ZBP1* — alternative sensors; weak SSc evidence. Stays Tier-3.

### M2 — TGF-β / fibroblast → myofibroblast

**Add (the heaviest module — biggest gap because Reactome's import has no ECM output sinks):**

| Mechanism | Why |
|-----------|-----|
| Latent TGF-β (LAP-LTBP1 complex) released from ECM via ITGAV:ITGB6 / ITGAV:ITGB3 integrin pulling | TGF-β activation is the rate-limiting step; mechanotransduction is SSc-specific |
| Thrombospondin-1 (THBS1) as auxiliary TGF-β activator | Alternative activation route |
| SMAD3-P:SMAD4 complex → COL1A1 transcription | Canonical biochem; direct ECM output |
| SMAD3-P:SMAD4 → COL3A1 transcription | Same |
| SMAD3-P:SMAD4 → FN1 (fibronectin-EDA) transcription | Same |
| SMAD3-P:SMAD4 → ACTA2 transcription | Myofibroblast marker output |
| SMAD3-P:SMAD4 → CTGF/CCN2 transcription | Matricellular amplifier |
| CTGF → autocrine fibroblast activation (feedback) | Autocrine loop |
| SMAD3-P:SMAD4 → POSTN transcription | Matricellular |
| FRA-2 (FOSL2) → COL1A1 transcription | Trojanowska work; FRA-2 transgenic mouse phenocopies SSc |
| FRA-2 → TBX2 cooperativity | Documented in SSc fibroblasts |
| TGF-β → ROS → mechanotransduction loop into YAP1/WWTR1 (TAZ) | Mechanical-feedback model in SSc |
| YAP1 → ACTA2 / CTGF transcription | Mechano-output |
| LOX / LOXL2 → collagen cross-linking → stiffened ECM → mechano-feedback | Fibrosis maturation |
| ACTA2 → contractile myofibroblast phenotype | Phenotype output |
| Aggregated COL1A1+COL3A1+FN1+POSTN+COMP+CTGF+LOX/LOXL2 → ECM deposition sink | Sink convergence |

**Keep all Tier-1 from spec.**

**Demote / drop for v1.0:**
- *BMP / Activin branch* — biologically relevant (BMP7 anti-fibrotic) but Tier-2 in spec, stays Tier-2.
- *Wnt / β-catenin* — Tier-2.
- *IGF-1R / IRS* — Tier-2.

### M3 — EndoMT / vasculopathy

**Add:**

| Mechanism | Why |
|-----------|-----|
| EDN1 secreted → EDNRA / EDNRB binding → Gq/PLC → vasoconstriction | Endothelin axis; bosentan/macitentan target |
| eNOS (NOS3) → NO → sGC (GUCY1A1/B1) → cGMP → PKG → vasodilation | NO/sGC axis; riociguat target |
| PDE5A → cGMP degradation | Sildenafil target (Raynaud) |
| TGF-β → SMAD3 (M2 crosstalk into M3) → SNAI1, SNAI2 transcription in endothelial cells | EndMT trigger |
| SNAI1/2 → CDH5 (VE-cadherin) gene repression | Loss of endothelial junction |
| SNAI1/2 + TGF-β → CDH2 (N-cadherin) + ACTA2 + FAP induction | Mesenchymal conversion |
| HIF1A (under hypoxia) → EDN1 transcription + VEGFA | Hypoxia → endothelin + angiogenesis input |
| VEGFA → KDR (VEGFR2) → endothelial proliferation signal | Vascular maintenance |
| Notch1 ligand binding (JAG1/2, DLL1/4) → NICD release → CSL/RBPJ → HES/HEY transcription | Already in Reactome NOTCH1 import; add the SSc-specific note |
| EndMT-converted EC → perivascular fibroblast → joins myofibroblast pool | Bridge to M2 |
| Aggregated capillary loss + intimal proliferation + EDN1 elevation → vascular remodelling sink | Sink convergence |

**Demote for v1.0:**
- *BMP9 / ALK1 / ENG* (HHT axis) — Tier-2.
- *Pericyte transition* — clinically real but mechanistically split between M2 and M3; defer.
- *Inflammasome (NLRP3 / GSDMD) in EC* — Tier-3.

### M4 — IL-6 / Th2 / B-cell

**Add:**

| Mechanism | Why |
|-----------|-----|
| IL-4 → IL-4Rα/γc complex → JAK1/JAK3 → STAT6-P | Canonical Th2 |
| IL-13 → IL-13Rα1/IL-4Rα → JAK2/TYK2 → STAT6-P | Canonical Th2 |
| STAT6 nuclear translocation → fibroblast ECM gene transcription | Direct M4→M2 crosstalk (romilkimab rationale) |
| IL-6 (Reactome import) → STAT3 → fibroblast pro-fibrotic transcription | M4→M2 crosstalk (tocilizumab rationale) |
| GATA3 → Th2 lineage commitment | TF anchor |
| TBX21 → Th1 lineage; FOXP3 → Treg; RORC → Th17 (anchors only, not deeply wired in v1.0) | Lineage anchors |
| BCR engagement → CD79A/CD79B → BLK/SYK/BTK → PLCγ2 → NFAT/NF-κB | B-cell activation skeleton |
| Sustained BCR + CD40-CD40L → PRDM1 (BLIMP1) / XBP1 / IRF4 → plasma cell differentiation | Plasma cell lineage |
| BAFF / APRIL → TNFRSF13B (BCMA) → plasma cell survival | Survival signal |
| Plasma cell → secretion of anti-Topo-I / anti-RNApol-III / anti-CENP-A/B autoantibodies → autoAb output sink | Sink convergence |
| Tocilizumab → IL-6R (annotation), Rituximab → CD20 (annotation), Dupilumab → IL-4Rα (annotation) | Drug binding nodes |

**Demote for v1.0:**
- *Tfh / IL-21 axis* — Tier-3.
- *IL-17 / Th17* — Tier-2.
- *Complement axis* — overlaps M3 (vascular) and M4 (effector); defer to v1.1.

### Crosstalk (inter-module) — final 8 edges

From the auto-extracted `docs/crosstalk_matrix.md` (14 edges, redundancy across specs), I retain 8 distinct ones to wire as explicit reactions:

| # | Edge | Mechanism | PMID strategy |
|---|------|-----------|---------------|
| 1 | M1 → M2 | IFN-α/β primes fibroblast pro-fibrotic transcription (priming, not direct induction) | Curator inference; co-author upgrades |
| 2 | M1 → M2 | CXCL4 → direct fibroblast activation | 24382179 (van Bon 2014) |
| 3 | M1 → M4 | IFN-α/β → pDC / B-cell class switching | Curator inference |
| 4 | M2 → M3 | TGF-β → SMAD3 → SNAI1/2 → EndMT | Strong canonical evidence |
| 5 | M3 → M2 | EndMT-derived EC → perivascular fibroblast → joins myofibroblast pool | Curator inference; conceptual bridge |
| 6 | M4 → M2 | IL-13 / STAT6 → ECM transcription in fibroblasts | Strong (Aliprantis 2007 if applicable) |
| 7 | M4 → M2 | IL-6 / STAT3 → fibroblast pro-fibrotic transcription | Strong (Khanna 2016 focuSSced trial supports) |
| 8 | M2 → M2 (intra) | TGF-β → CTGF → fibroblast (autocrine amplifier) | Strong canonical evidence |

Edges I dropped as redundant:
- The second "M2 → M3" wording (TGF-β drives EndMT) — same biology as #4, merged.
- "M3 → M4" endothelial chemokines (CXCL10/11 recruiting Th1/Th2) — biologically real but lower yield for v1.0 (CXCL10/11 not yet in map); defer to v1.1.
- "M4 → M3" B-cell-driven endothelial inflammation — weak mechanistic evidence; defer.

## Q3 — Ambition: ACR alone, ACR + methods paper, or methods first

**Decision: Option A — ACR abstract only, methods paper deferred to 2027.**

Per user direction: *"on focus soumission ACR"*. Reasoning:

- The bandwidth question is the binding constraint (R11). Splitting effort between ACR and a methods paper in parallel risks both.
- A late-breaking ACR abstract supported by a citable Zenodo DOI is a strong outcome on its own.
- The methods paper in 2027 lands stronger if v1.0 + an ACR poster have happened first — "demonstrated at ACR Convergence 2026" is a real introduction line.
- Option C (methods first, ACR 2027) is the explicit fallback in ROADMAP § Phase 6 if the calendar slips.

**Implication:** the abstract is the primary deliverable. Manuscript work is queued for early 2027.

## Reversibility

Every decision here is a row (or block of rows) in `curation/ssc_curated_reactions.tsv`. To override:

1. Edit the TSV.
2. Run `make wire` (added in this batch).
3. Re-run `make preflight network sink-check figures abstract`.
4. Commit with a meaningful message.
5. (Optional) re-tag if past v1.0.

The TSV is the curator-readable surface; the XML and the analyses are derived state.
