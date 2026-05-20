# baseline_v1.0/

> Frozen pre-review artefacts. Used by Sprints S1–S2 as the
> comparison baseline when the DEG / scoring / network analyses are
> re-run with the corrections from the simulated peer review.

**Pinned commit**: tag `v1.0-pre-review` (= `e638a4d` on `main`).
**Frozen on**: 2026-05-20.
**Do not edit** — these files exist to support
diff-vs-baseline reporting.

## Contents

| File | Source path | Purpose |
|------|-------------|---------|
| `cluster_deg_multi.tsv` | `analysis/overlay/cluster_deg_multi.tsv` | 4338 DEG entries (Wilcoxon, raw p-value) — baseline for E1 mixed-effects + FDR re-run |
| `patient_module_scores_multi.tsv` | `analysis/overlay/patient_module_scores_multi.tsv` | per-donor sign-weighted module scores — baseline for E2 AUCell |
| `network_summary.json` | `analysis/network/summary.json` | 38 communities, top-20 hubs by hub_score — baseline for E3/E4 |
| `hubs.tsv` | `analysis/network/hubs.tsv` | top-20 hub ranking, current hub_score formulation |
| `druggable_hubs.tsv` | `analysis/overlay/druggable_hubs.tsv` | DGIdb cross-reference baseline for E6 drug-table recalibration |
| `SHA256SUMS` | computed at freeze time | integrity check |

## Headline numbers frozen here

- Total significant DEG entries (raw Wilcoxon, p ≤ 0.05): **4 338**.
- MIM coverage from these: **98 / 196 = 50.0 %**.
  - M1 (IFN-I): 65 % (24/37)
  - SSc Tier-1: 51 % (44/86)
  - M2 (TGF-β): 53 % (17/32)
  - M4 (IL-6/Th2/B-cell): 35 % (6/17)
  - M3 (Notch/EndoMT): 21 % (5/24)
- Top hub: SMAD3p_SMAD4 (hub_score 13.42).
- Per-donor module scores (skin, mean ± SD): M1 SSc 0.342 ± 0.095
  vs HC 0.070 ± 0.016; M2 SSc 0.232 ± 0.061 vs HC 0.044 ± 0.007.
- 38 communities; "six largest enriched for single modules"
  claim — *no hypergeometric p-values reported yet* (E4).

## How to verify

```bash
cd analysis/baseline_v1.0
sha256sum -c SHA256SUMS
```

## When this directory becomes stale

After Sprint S2 closes, the v1.1 outputs will live in their
canonical locations (`analysis/overlay/`, `analysis/network/`).
The diff lives in `analysis/baseline_v1.1_vs_v1.0.md` (created at
the S2 gate).
