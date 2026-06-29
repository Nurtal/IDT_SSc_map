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
import csv, gzip, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
MAT = ROOT / "data/raw/gse45536/GSE45536_series_matrix.txt.gz"
SOFT = ROOT / "data/raw/gse45536/GPL570_table.txt"   # plain platform table from acc.cgi
ANN = ROOT / "curation/annotations/species_annotations.tsv"
OUT = ROOT / "analysis/overlay/m5_gse45536_validation.json"

# Sub-signatures of the M5 gene set, used for the decomposition in Panel B of
# figures/F7_M5_validation.png (see analysis/overlay/M5_validation.md). The
# remaining M5 genes (CD40, CD40LG) belong to none of the three sub-sets.
SUBSIGS = {
    "autoantigens": {"TOP1", "CENPB"},
    "plasma_core":  {"PRDM1", "XBP1", "TNFRSF17", "IRF4", "TNFSF13B", "TNFSF13"},
    "b_surface":    {"CD19", "CD22", "CD79A", "CD79B", "MS4A1", "BLK", "BTK", "LYN", "SYK"},
}


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


def score_signature(rows, samples, grp, genes: set[str]) -> dict | None:
    """Score one signature on the cohort; return summary stats or None."""
    p2s = probe_to_symbol(genes)
    sc = sig_score(rows, p2s, samples)
    if sc is None:
        return None
    score, nprobe = sc
    s = score[grp == "SSc"]; h = score[grp == "HC"]
    s = s[~np.isnan(s)]; h = h[~np.isnan(h)]
    p = float(mannwhitneyu(s, h, alternative="two-sided").pvalue)
    return {
        "genes_mapped": sorted(set(p2s.values())),
        "n_genes": len(genes),
        "n_genes_mapped": len(set(p2s.values())),
        "n_probes": int(nprobe),
        "n_ssc": int(len(s)), "n_hc": int(len(h)),
        "ssc_mean_z": float(np.mean(s)), "hc_mean_z": float(np.mean(h)),
        "delta": float(np.mean(s) - np.mean(h)), "p": p,
    }


def main():
    samples, phen, rows = load_matrix()
    grp = np.array(["SSc" if "scleroderma" in (p or "").lower() else
                    ("HC" if "healthy" in (p or "").lower() else "other") for p in phen])
    n_ssc = int(np.sum(grp == "SSc")); n_hc = int(np.sum(grp == "HC"))
    print(f"GSE45536: {len(samples)} samples | SSc={n_ssc} HC={n_hc} other={np.sum(grp=='other')}")

    # Full M5 + M1 control, then the M5 sub-signature decomposition.
    sigs: dict[str, set[str]] = {"M5": module_genes("M5"), "M1": module_genes("M1")}
    sigs.update(SUBSIGS)

    results: dict[str, dict] = {}
    for name, genes in sigs.items():
        r = score_signature(rows, samples, grp, genes)
        if r is None:
            print(f"{name}: no probes mapped"); continue
        results[name] = r
        star = " *" if r["p"] < 0.05 else ""
        print(f"\n=== {name} signature ({r['n_genes_mapped']}/{r['n_genes']} genes, {r['n_probes']} probes) ===")
        print(f"  genes mapped: {r['genes_mapped']}")
        print(f"  SSc mean z={r['ssc_mean_z']:+.3f} (n={r['n_ssc']})  vs  "
              f"HC mean z={r['hc_mean_z']:+.3f} (n={r['n_hc']})  "
              f"Δ={r['delta']:+.3f}  p={r['p']:.3g}{star}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "dataset": "GSE45536",
        "description": "Streicher et al., whole-blood; external validation of module M5",
        "n_ssc": n_ssc, "n_hc": n_hc,
        "signatures": results,
    }, indent=2))
    print(f"\n[ok] wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
