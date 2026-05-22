# SSc-MIM input-data mirror manifest (E15 / R3-M2)

> Zenodo mirror of the four GEO source datasets used in the
> revision-v1.1 multi-tissue scRNA-seq overlay. Frozen on
> 2026-05-21 against the analysis run that produced
> `analysis/overlay/cluster_deg_multi_v11.tsv` and
> `analysis/overlay/coverage_v1.1.json`.

This document lists every raw archive consumed by `make overlay-multi`
together with its SHA-256 digest and the GEO accession of origin. The
companion Zenodo deposit (DOI to be minted at v1.1 tag push; deposit
ID **REPLACE_ME** once the upload completes) re-publishes these files
under a single dataset DOI so that the manuscript reproducibility
envelope does not depend on the GEO FTP server remaining reachable.

The upload is a manual step performed by the lead author when minting
the v1.1 Zenodo release; the file list and digests below are
authoritative for that upload. Verification:

```bash
cd data/raw
sha256sum --check ../MIRROR.sha256
```

(see `data/MIRROR.sha256` for the machine-readable companion).

## Inventory

| GEO accession | File | Size | SHA-256 |
|---|---|---|---|
| GSE138669 (Tabib 2021) | `tabib2021/GSE138669_RAW.tar` | 594 155 520 B (594 MB) | `17e7162aae7f007900c0ac98b3f348aceafb60d5087c489171c6993b80b59a02` |
| GSE128169 (Morse 2019) | `gse128169/GSE128169_RAW.tar` | 1 177 282 560 B (1.18 GB) | `a187f509fdb94035a65ff7536bd2a4c703df353962799b218cd33db6b056250e` |
| GSE195452 (Gur 2022) — raw | `gse195452/GSE195452_RAW.tar` | 920 788 169 B (921 MB) | `c06d474f6f16325b469bff73c41cc731509ac60bbd13f1537049435115e1a63d` |
| GSE195452 (Gur 2022) — annotations | `gse195452/GSE195452_Cell_metadata_v26_anno.txt.gz` | 3 267 287 B (3.27 MB) | `8e1d53a8c68eb521c26db444e220094d8574577486f5aebdbdf943c3487af1e9` |
| GSE210395 | `gse210395/GSE210395_scRNA_countMatrix.tsv.gz` | 397 343 213 B (397 MB) | `51c7498517a99ee94695be6000d40391eaa4825b723baa314bf4e7656d41592f` |

Total payload: **3.09 GB** — within the 50 GB Zenodo per-record quota.

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
sha256sum -c data/MIRROR.sha256
# Expected: 5 OK lines, no failures.

# Then re-run the pipeline:
make overlay-multi --deg-backend mixed-v11 --fdr-q 0.05
make aucell
# coverage_v1.1.json should report mim_coverage_pct = 81.3
```

## Status

- 2026-05-21: digests computed and pinned in this manifest. Zenodo
  upload **pending** — manual step at v1.1 tag push (E15 / S6 of the
  revision roadmap). The Docker image (`.github/workflows/docker.yml`)
  does not bundle these raw files; mounting `data/raw/` from this
  Zenodo deposit is the recommended path for end-to-end reproduction.
