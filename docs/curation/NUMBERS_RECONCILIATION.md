# Numbers reconciliation — SSc-MIM headline figures

> Created in the **v1.1 hardening sprint (2026-06-05)** in response to an independent
> critical read that flagged divergent headline numbers across files and a
> method-sensitive coverage metric. This is the single canonical mapping from every
> published figure to its definition and source artefact. When two files disagree,
> **this table is authoritative**; the disagreements below are definitional, not errors.

## 1. Species, reactions, compartments

| Figure | Value | Definition | Source artefact |
|--------|-------|------------|-----------------|
| Species (integrated, final) | **526** | All `<species>` in the integrated map after SSc-Tier-1 wiring | `curation/celldesigner/SSc_MIM_integrated.xml`; `STATUS.md` |
| Species (Reactome backbone only) | **385** | Integrated map *before* the 85 SSc-curated reactions + stubs were wired | `curation/celldesigner/SSc_MIM_integrated.report.json` (`totals.species`) |
| Reactions (integrated, final) | **260** | 175 Reactome-derived + 85 SSc-curated | `SSc_MIM_integrated.xml`; `STATUS.md` |
| Reactions (Reactome backbone) | **175** | Reactome import merge total | `SSc_MIM_integrated.report.json` (`totals.reactions`) |
| Reactions (SSc-Tier-1 layer) | **85** | Hand-curated SSc-specific reactions (incl. 8 crosstalk) | `curation/ssc_curated_reactions.tsv` |
| Compartments (biological) | **17** | Biologically meaningful compartments | manuscript §2.5 |
| Compartments (raw `<compartment>`) | **20** | 17 biological + 3 layout-only (CellDesigner round-trip) | `SSc_MIM_integrated.xml`; preflight |

**The point a reviewer must not miss:** the headline 526/260 is the *integrated* map;
the 175→260 reaction delta (i.e. **85 reactions**) is the entire original SSc-specific
contribution. See §3 for how strongly that 85-reaction layer is evidenced.

## 2. Reaction-annotation tables (note the two different denominators)

| Figure | Value | Definition | Source |
|--------|-------|------------|--------|
| `reaction_evidence.tsv` rows | **244** | all annotated reactions = **159 pure-Reactome + 85 SSc** (the 85 SSc rows live in *both* this file and `ssc_curated_reactions.tsv`; do **not** add 244 + 85) | `curation/annotations/reaction_evidence.tsv` |
| ... with a primary PMID | **232 (95.1%)** | non-empty numeric `pmid` (was 198 before the 2026-06-05 depth pass) | preflight |
| ... `type=TODO` before H1 | **159** | un-classified reaction type | (pre-sprint) |
| ... `type=TODO` after H1 | **0** | classified by `evidence_audit.py` (153 by rule, 6 fallback) | `analysis/curation/evidence_stratification.json` |
| `ssc_curated_reactions.tsv` rows | **85** | SSc-Tier-1 layer | `curation/ssc_curated_reactions.tsv` |
| ... with a primary PMID | **75 (88.2%)** | up from 40 (47.1%); of these **67 are full-text- or originally-verified** (`confirmed`), 8 abstract-only (`proposed`) | `analysis/curation/evidence_stratification.json` |
| ... curator-inference debt (untriaged) | **0** | was 45; now 67 confirmed, 8 proposed, 10 reclassified, 0 untested | `curation/curator_inference_register.tsv`, `curation/fulltext_verification_log.md` |

## 3. Evidence quality by provenance layer (H1)

Conflating the two layers inflates the apparent depth of SSc-specific curation.
Stated honestly:

| Layer | Reactions | With PMID | Experimental/review ECO (314/270/353/033) |
|-------|-----------|-----------|--------------------------------|
| Reactome backbone (pure-Reactome) | 159 | 158 (99.4%) | 0 (0.0%) |
| **SSc-Tier-1 (the original contribution)** | **85** | **74 (87.1%)** | **50 (58.8%)** |

After the 2026-06-05 curation-depth pass (`docs/curation/curation_depth_pass.md`), the SSc-specific
layer carries both more citations (87.1%, up from 47.1%) and a *much higher* fraction of
experimental/review-grade ECO codes (58.8%) than the Reactome backbone. The residual
backlog is **1 declared `untested` row** (down from 45), with a candidate-PMID pool,
itemised in `curation/curator_inference_register.tsv`; a further 10 rows were honestly
reclassified as conceptual bridges / phenotype aggregations rather than force-cited. The
`make evidence-lint` CI guard now fails on any *undeclared* inference debt.

Note: the Reactome backbone's 99.4% PMID / 0% experimental-ECO reflects that Reactome
import rows carry a PMID but propagate `ECO:0000305` by default — citation present,
evidence-grade weak. The SSc layer is the inverse and now stronger on both axes.

## 4. Single-cell coverage — report with effect-size context (H2)

The bare "81.3% coverage" headline is the *permissive-cutoff upper bound*. Held at a
fixed method (NB-GLM) and swept over effect-size thresholds:

| `\|log2FC\|` ↓ / `padj_dataset` → | ≤ 0.05 | ≤ 0.01 | ≤ 0.001 |
|---|---|---|---|
| ≥ 0.2 (headline) | **81.3%** | 68.7% | 55.6% |
| ≥ 0.5 | 74.7% | 62.1% | 50.0% |
| ≥ 1.0 (2-fold, **robust**) | 58.6% | **49.5%** | 39.4% |
| ≥ 2.0 (4-fold) | 33.8% | 26.8% | 24.2% |

Source: `analysis/overlay/coverage_sensitivity.{tsv,json}`.

**Interpretation.** At the effect-size-gated operating point (≥2-fold, `padj ≤ 0.01`)
coverage is **49.5% (98/198)** — essentially identical to the v1.0 Wilcoxon baseline
(98/196 = 50.0%). The +31-point jump from 50% to 81.3% is therefore **largely a
stringency/power effect**, not a biological gain: the pooled-donor NB-GLM detects many
small-effect signals the per-cluster Wilcoxon could not. **Recommendation:** lead with
the effect-size-gated **≈50%** figure and present **81.3%** explicitly as the permissive
upper bound, with the grid above as Supplementary evidence.

## 5. How to regenerate

```bash
make harden            # H1 + H2 + H3, fully offline from repo artefacts
# or individually:
make evidence-audit coverage-sensitivity inference-register
```
