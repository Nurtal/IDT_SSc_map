# SSc-MIM input-data mirror manifest (E15 / R3-M2)

> Zenodo mirror of **every** GEO source dataset that feeds a published
> SSc-MIM result:
> 1. the **four scRNA-seq datasets** of the revision-v1.1 multi-tissue
>    overlay (Tabib / Gur / PBMC / lung), and
> 2. the **bulk whole-blood cohort GSE45536** (Streicher *et al.*) used
>    for the **external validation of module M5**.
> Frozen against the analysis runs that produce
> `analysis/overlay/cluster_deg_multi_v11.tsv`,
> `analysis/overlay/coverage_v1.1.json` (overlay) and
> `analysis/overlay/M5_validation.md` (M5 external validation).

This document lists every raw archive consumed by `make overlay-multi`
**or `make validate-m5`** together with its SHA-256 digest and the GEO
accession of origin. **Any new dataset that contributes to a published
number MUST be added here** — this is enforced in CI by
`scripts/check_data_manifest.py` (`make check-manifest`), which fails the
build if a script references a `GSE`/`GPL` accession absent from this
manifest. The
companion Zenodo deposit (DOI to be minted at v1.1 tag push; deposit
ID **REPLACE_ME** once the upload completes) re-publishes these files
under a single dataset DOI so that the manuscript reproducibility
envelope does not depend on the GEO FTP server remaining reachable.

The upload is a manual step performed by the lead author when minting
the v1.1 Zenodo release; the file list and digests below are
authoritative for that upload. Verification:

```bash
cd data
sha256sum --check MIRROR.sha256   # paths in the manifest are relative to data/
```

(see `data/MIRROR.sha256` for the machine-readable companion).

## Inventory

### A. scRNA-seq overlay datasets (feed `make overlay-multi` → coverage)

| GEO accession | File | Size | SHA-256 |
|---|---|---|---|
| GSE138669 (Tabib 2021) | `tabib2021/GSE138669_RAW.tar` | 594 155 520 B (594 MB) | `17e7162aae7f007900c0ac98b3f348aceafb60d5087c489171c6993b80b59a02` |
| GSE128169 (Morse 2019) | `gse128169/GSE128169_RAW.tar` | 1 177 282 560 B (1.18 GB) | `a187f509fdb94035a65ff7536bd2a4c703df353962799b218cd33db6b056250e` |
| GSE195452 (Gur 2022) — raw | `gse195452/GSE195452_RAW.tar` | 920 788 169 B (921 MB) | `c06d474f6f16325b469bff73c41cc731509ac60bbd13f1537049435115e1a63d` |
| GSE195452 (Gur 2022) — annotations | `gse195452/GSE195452_Cell_metadata_v26_anno.txt.gz` | 3 267 287 B (3.27 MB) | `8e1d53a8c68eb521c26db444e220094d8574577486f5aebdbdf943c3487af1e9` |
| GSE210395 | `gse210395/GSE210395_scRNA_countMatrix.tsv.gz` | 397 343 213 B (397 MB) | `51c7498517a99ee94695be6000d40391eaa4825b723baa314bf4e7656d41592f` |

### B. M5 external-validation cohort (feeds `make validate-m5` → `M5_validation.md`)

| GEO accession | File | Size | SHA-256 |
|---|---|---|---|
| GSE45536 (Streicher) — expression + phenotypes | `gse45536/GSE45536_series_matrix.txt.gz` | 14 420 384 B (14.4 MB) | `af6624e157a32ba589dfe6bf8f8d5c926ca9bce3db719793dade655c7c00df0c` |
| GPL570 (Affymetrix) — probe → gene table | `gse45536/GPL570_table.txt` | 79 501 528 B (79.5 MB) | `ebb6df22d8e0b00a5029151329e5ba37f4dbad54a1866c7469b22b2c9dd3394b` |

Total payload: **3.18 GB** — within the 50 GB Zenodo per-record quota.

## Provenance of each file

- **GSE138669** (Tabib T, *et al.* *Nat Commun* 2021;12:4384): 22 per-sample
  10× `.h5` files archived in a single RAW.tar. Downloaded from
  `ftp.ncbi.nlm.nih.gov/geo/series/GSE138nnn/GSE138669/suppl/GSE138669_RAW.tar`
  via `make tabib-fetch` (`scripts/fetch_tabib.py`).
- **GSE128169** (Morse C, *et al.* *Eur Respir J* 2019;54:1802441): per-sample
  10× MEX sparse matrices archived in RAW.tar.
- **GSE195452** (Gur C, *et al.* *Cell* 2022;185:1373-1388): 727 per-batch
  dense gene×cell matrices archived in RAW.tar; cell-level annotations
  in a separate `Cell_metadata_v26_anno.txt.gz` file. A hand-curated
  `data/raw/gse195452/sample_map.json` (not part of this mirror — re-derive
  from sample titles via `scripts/build_overlay_multi.py`) maps batch
  titles to (patient_id, condition).
- **GSE210395**: long-format triplet TSV; 8 donors enriched for pDC and
  monocyte populations.
- **GSE45536** (Streicher K, *et al.*, *"The Plasma Cell Signature in
  Autoimmune Disease (II)"*): 99 scleroderma + 24 healthy-donor PAXgene
  **whole-blood** samples on Affymetrix GPL570. Used **only** for the
  external validation of module M5 (B-cell / autoreactivity) — it does
  **not** contribute to the MIM coverage figure. Two files:
  the GEO series matrix (expression + phenotypes) from
  `ftp.ncbi.nlm.nih.gov/geo/series/GSE45nnn/GSE45536/matrix/` and the
  GPL570 platform table (probe → Gene Symbol) from
  `www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL570&targ=self&form=text&view=data`.
  Both are fetched reproducibly by `make fetch-gse45536`
  (`scripts/fetch_gse45536.py`); the validation re-run
  (`make validate-m5` → `scripts/validate_m5_gse45536.py`) on these exact
  files reproduces M5 SSc-vs-HC **p = 1.3×10⁻⁴** (Δ z = −0.291) and the
  autoantigen-core (TOP1/CENPB) **p = 1.7×10⁻¹⁰**, with the M1/IFN
  positive control at **p = 3.8×10⁻⁵**.

## Reproducibility envelope

`make overlay-multi --deg-backend mixed-v11 --fdr-q 0.05` on these
exact files produces (modulo non-deterministic AnnData warnings):

| Output | Rows | SHA-256 dependency |
|---|---|---|
| `analysis/overlay/cluster_deg_multi_v11.tsv` | 257 748 | all 5 mirror files |
| `analysis/overlay/pseudobulk_multi.tsv` | 4 722 × 196 | all 5 mirror files |
| `analysis/overlay/patient_module_scores_aucell.tsv` | 197 | pseudobulk_multi.tsv |
| `analysis/overlay/coverage_v1.1.json` | — | cluster_deg_multi_v11.tsv |

## How to verify a Zenodo download

```bash
# After downloading the Zenodo record, place each file under data/raw/<dataset>/
cd data && sha256sum -c MIRROR.sha256 && cd ..
# Expected: 7 OK lines, no failures.

# Then re-run the pipelines:
make overlay-multi --deg-backend mixed-v11 --fdr-q 0.05
make aucell
# coverage_v1.1.json should report mim_coverage_pct = 82.6
make validate-m5
# should report M5 SSc-vs-HC p = 0.000127 (1.3e-4) and M1/IFN p = 3.8e-5
```

## Status

- 2026-05-21: digests computed and pinned in this manifest. Zenodo
  upload **pending** — manual step at v1.1 tag push (E15 / S6 of the
  revision roadmap). The Docker image (`.github/workflows/docker.yml`)
  does not bundle these raw files; mounting `data/raw/` from this
  Zenodo deposit is the recommended path for end-to-end reproduction.
- 2026-06-29: **added GSE45536 + GPL570** (M5 external-validation cohort)
  to the manifest with verified SHA-256 digests — both files were
  downloaded from GEO and `scripts/validate_m5_gse45536.py` reproduced the
  published M5 p-values against them before pinning. Added
  `scripts/check_data_manifest.py` (CI guard: every GSE/GPL accession used
  by a script must be listed here) and `scripts/fetch_gse45536.py`
  (reproducible fetch). Fixed the (previously wrong) verification command
  in this file. This closes the gap where the dataset carrying the M5
  validation numbers was off-manifest and absent from disk.
