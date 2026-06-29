#!/usr/bin/env python3
"""External validation of module M5 (B-cell / autoreactivity) on GSE45536
("The Plasma Cell Signature in Autoimmune Disease II", Streicher et al.),
99 scleroderma + 24 healthy-donor PAXgene whole-blood samples, GPL570.

Builds a per-sample M5 signature score (mean of z-scored M5 probe expression)
and tests scleroderma vs healthy donor (Mann-Whitney). An IFN (M1) control
signature is scored the same way to show specificity.

Inputs (under data/raw/gse45536/ — fetch with `make fetch-gse45536`):
  GSE45536_series_matrix.txt.gz   expression matrix + phenotypes
  GPL570_table.txt                probe -> gene symbol (plain platform table)
  curation/annotations/species_annotations.tsv  module gene sets

Both raw files are pinned (size + SHA-256) in data/MIRROR.sha256.
"""
from __future__ import annotations
import csv, gzip, sys
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
MAT = ROOT / "data/raw/gse45536/GSE45536_series_matrix.txt.gz"
SOFT = ROOT / "data/raw/gse45536/GPL570_table.txt"   # plain platform table from acc.cgi
ANN = ROOT / "curation/annotations/species_annotations.tsv"


def module_genes(mod: str) -> set[str]:
    out = set()
    for r in csv.DictReader(ANN.open(), delimiter="\t"):
        if mod in (r["module"] or "").split(",") and r["hgnc_symbol"].strip():
            out.add(r["hgnc_symbol"].strip())
    return out


def probe_to_symbol(symbols: set[str]) -> dict[str, str]:
    """Return {probe_id: symbol} for probes whose Gene Symbol is in `symbols`,
    parsing the plain GPL570 platform table (header line starts with 'ID\\t')."""
    p2s: dict[str, str] = {}
    id_col = gene_col = None
    with SOFT.open(errors="replace") as f:
        for line in f:
            if id_col is None:
                if line.startswith("ID\t") and "Gene Symbol" in line:
                    header = line.rstrip("\n").split("\t")
                    id_col = header.index("ID")
                    gene_col = header.index("Gene Symbol")
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) <= gene_col:
                continue
            for s in p[gene_col].split("///"):
                if s.strip() in symbols:
                    p2s[p[id_col]] = s.strip()
                    break
    return p2s


def load_matrix():
    phen = None
    with gzip.open(MAT, "rt", errors="replace") as f:
        rows = []
        in_tbl = False
        samples = None
        for line in f:
            if line.startswith("!Sample_characteristics_ch1") and "phenotype:" in line:
                phen = [c.strip('"').replace("phenotype:", "").strip()
                        for c in line.rstrip("\n").split("\t")[1:]]
            if line.startswith("!series_matrix_table_begin"):
                in_tbl = True
                samples = next(f).rstrip("\n").split("\t")[1:]
                samples = [s.strip('"') for s in samples]
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if in_tbl:
                p = line.rstrip("\n").split("\t")
                pid = p[0].strip('"')
                try:
                    vals = [float(x) if x not in ("", '"NA"', "NA") else np.nan for x in p[1:]]
                except ValueError:
                    continue
                rows.append((pid, vals))
    return samples, phen, rows


def sig_score(rows, p2s, samples):
    """mean of per-probe z-scores across the signature, per sample."""
    mat = np.array([v for pid, v in rows if pid in p2s], dtype=float)  # probes x samples
    if mat.size == 0:
        return None
    # z-score each probe across samples, then average probes per sample
    mu = np.nanmean(mat, axis=1, keepdims=True)
    sd = np.nanstd(mat, axis=1, keepdims=True)
    sd[sd == 0] = 1
    z = (mat - mu) / sd
    return np.nanmean(z, axis=0), mat.shape[0]


def main():
    samples, phen, rows = load_matrix()
    grp = np.array(["SSc" if "scleroderma" in (p or "").lower() else
                    ("HC" if "healthy" in (p or "").lower() else "other") for p in phen])
    print(f"GSE45536: {len(samples)} samples | SSc={np.sum(grp=='SSc')} HC={np.sum(grp=='HC')} other={np.sum(grp=='other')}")
    for mod in ("M5", "M1"):
        genes = module_genes(mod)
        p2s = probe_to_symbol(genes)
        mapped = sorted(set(p2s.values()))
        sc = sig_score(rows, p2s, samples)
        if sc is None:
            print(f"{mod}: no probes mapped"); continue
        score, nprobe = sc
        s = score[grp == "SSc"]; h = score[grp == "HC"]
        s = s[~np.isnan(s)]; h = h[~np.isnan(h)]
        p = mannwhitneyu(s, h, alternative="two-sided").pvalue
        print(f"\n=== {mod} signature ({len(mapped)}/{len(genes)} genes, {nprobe} probes) ===")
        print(f"  genes mapped: {mapped}")
        print(f"  SSc mean z={np.mean(s):+.3f} (n={len(s)})  vs  HC mean z={np.mean(h):+.3f} (n={len(h)})"
              f"  Δ={np.mean(s)-np.mean(h):+.3f}  p={p:.3g}{' *' if p<0.05 else ''}")


if __name__ == "__main__":
    main()
