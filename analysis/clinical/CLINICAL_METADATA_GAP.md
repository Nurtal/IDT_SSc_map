# Clinical metadata gap — recorded 2026-05-20

> Outcome of revision sprint S3 (E7 mRSS correlation + E12
> demographic matching). Documents the *de facto* unavailability of
> clinical metadata in the public GEO deposits used by SSc-MIM.

## TL;DR

Of 773 donor-samples across the four scRNA-seq datasets used in
SSc-MIM, **zero** carry numeric mRSS, disease duration, age, sex, or
autoantibody-specificity fields in their public GEO
`series_matrix.txt.gz` deposits. The patient-stratification analysis
proposed in revision item E7 (Spearman ρ between module activation
scores and mRSS) and the demographic-matching sensitivity analysis
proposed in E12 are therefore **not executable** on public data.

This file documents what was checked, what we found, and the
manuscript-level treatment we adopted for the v1.1 submission to
*npj Systems Biology and Applications*.

## What was checked

`scripts/fetch_clinical_metadata.py` pulled every
`series_matrix.txt.gz` available at NCBI GEO for the four datasets,
parsed every `!Sample_characteristics_ch1` field, normalised
canonical keys (mRSS, age, sex, disease duration, autoantibody,
subtype, condition), and computed presence statistics:

| dataset | samples | available fields |
|---------|---------|------------------|
| Tabib 2021 — GSE138669 | 22 | `tissue` (skin); `chemistry` (10X V1/V2); `condition` (CONTROL/SSC) |
| Gur 2022 — GSE195452  | 727 | `tissue` (Skin); `selection_marker` (CD90+); `patient_id` (Ctrl* / pt*) |
| pDC PBMC — GSE210395  | 8 | `condition`; `tissue` (PBMC); `cell type` (BLOOD) |
| Morse 2019 — GSE128169 | 16 | `subject status`; `tissue` (lung); `chemistry` |

**Global gap (`metadata_gap.json`):**

| canonical field | n_with / n_total | fraction |
|-----------------|------------------|----------|
| mRSS | 0 / 773 | 0.000 |
| disease_duration_months | 0 / 773 | 0.000 |
| age | 0 / 773 | 0.000 |
| sex | 0 / 773 | 0.000 |
| ana_specificity | 0 / 773 | 0.000 |
| subtype (dcSSc/lcSSc) | 0 / 773 | 0.000 |

## What the revision plan said vs reality

The revision roadmap listed three actions for S3:

| Roadmap item | Outcome | Reason |
|--------------|---------|--------|
| E7 — Spearman ρ(M1, mRSS) on Tabib donors | **not executable** | mRSS absent from GEO |
| E12 — Age/sex propensity matching | **not executable** | age + sex absent from GEO |
| Fallback — disease duration as proxy | **not executable** | also absent |

Risk RR2 in the revision risk register was rated *medium*; it has
now been formally confirmed.

## What we built anyway

Three scripts that are *ready to run* as soon as clinical metadata
arrives via a non-GEO route (e.g. a lab supplementary table or a
direct request to the corresponding author):

- **`scripts/fetch_clinical_metadata.py`** — fetches and parses
  series_matrix files for all four datasets; emits
  `donor_metadata.tsv` (773 rows × 20 cols) with one canonical
  column per recognised clinical variable. Already executed; output
  committed.
- **`scripts/clinical_correlation.py`** — generic Spearman ρ with
  1000-iteration bootstrap CI per (module, clinical_var). Honours
  a "gap" mode that emits a banner row when no numeric clinical
  variable is available, so the pipeline never silently produces
  vacuous correlations. Optional supplementary scatter figure.
- **`scripts/demographic_match.py`** — 1:1 propensity-score
  matching on age + sex with a configurable calliper. Falls back to
  age-only Euclidean matching if scikit-learn is absent. Emits a
  per-dataset demographics table and a sensitivity-matched-HC
  donor list.

All three pass the smoke suite
(`scripts/tests/test_clinical_correlation.py`).

## Manuscript-level treatment for v1.1

§4.4 ("Transcriptomic Overlay and Patient Stratification") is
updated to acknowledge this gap explicitly:

> *"The patient-stratification framing in this paragraph is
> hypothesis-generating. Clinical metadata required to test the
> stratification claim directly — modified Rodnan Skin Score (mRSS),
> disease duration, age, sex, and autoantibody specificity — is not
> available in the public GEO deposits of the four datasets we
> integrated (`analysis/clinical/CLINICAL_METADATA_GAP.md`). External
> validation against named SSc cohorts (PRESS, EUSTAR, ESCISIT) is
> a priority for v2.0; the analysis pipeline is in place
> (`scripts/clinical_correlation.py`, `scripts/demographic_match.py`)
> and is ready to execute once cohort metadata is available."*

§4.5 ("Limitations and Future Directions") is updated with a fourth
limitation paragraph covering the metadata gap as a structural
constraint of using public scRNA-seq deposits.

## How to close the gap

1. **Tabib lab (GSE138669)** — email Dr. Tabib (University of
   Pittsburgh) requesting per-sample mRSS and disease duration for
   the 12 SSc donors. Template in
   `docs/standups/tabib_metadata_request_template.md` (to be
   drafted).
2. **Gur 2022 (GSE195452)** — the Gur et al. *Cell* 2022
   supplementary tables include per-patient clinical
   characteristics; supplementary Table S1 should be downloaded and
   parsed into the donor_metadata.tsv schema.
3. **Bhattacharyya / Whitfield bulk cohorts** — these are
   maintained at Dartmouth and Northwestern with rich clinical
   annotation. Adding a bulk-overlay channel to v2.0 would
   sidestep the public-deposit gap entirely.

## File outputs of this sprint

- `analysis/clinical/donor_metadata.tsv` — 773 rows, no numeric
  clinical vars (canonical columns are present but empty).
- `analysis/clinical/metadata_gap.json` — machine-readable summary.
- `analysis/clinical/module_clinical_correlation.tsv` — gap banner.
- `analysis/clinical/demographics_summary.tsv` — gap banner.
- `data/raw/series_matrix/` — cached series_matrix.txt.gz files
  (5 files, ~13 kB total).

---

*Generated 2026-05-20 during revision sprint S3. Update if any
external clinical metadata becomes available.*
