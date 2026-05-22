#!/usr/bin/env python3
"""Pull and parse GEO series_matrix.txt.gz files for the four scRNA-seq
datasets used in SSc-MIM, and emit a unified donor metadata TSV.

Addresses revision item E7 (clinical correlation): the manuscript
§4.4 makes patient-stratification claims that need to be anchored in
real clinical variables (mRSS, disease duration, age, sex, ANA).
This script extracts every ``!Sample_characteristics_ch1`` field
from each dataset's GEO deposit and writes a wide TSV with one row
per donor.

Datasets and matrix URLs:

- Tabib 2021       GSE138669   (skin, 22 donors)
- Gur 2022         GSE195452   (skin multiome, 2 GPL platforms)
- pDC PBMC 2022    GSE210395   (PBMC, 8 donors)
- Morse 2019       GSE128169   (SSc-ILD lung, 13 donors)

Behaviour:

- Downloads each series_matrix.txt.gz on demand (HTTPS to
  ftp.ncbi.nlm.nih.gov) and caches under ``data/raw/<dataset>/``.
- Parses the ``!Sample_title`` line and every
  ``!Sample_characteristics_ch1`` field; coalesces values like
  ``"mRSS: 18"`` into a tidy ``mRSS = 18`` column.
- Tries to recognise the canonical clinical variables (mRSS,
  disease_duration_months, age, sex, ana_specificity,
  subtype_dcssc_lcssc); reports which are present and which are
  absent per dataset.
- Writes ``analysis/clinical/donor_metadata.tsv`` (donor × var) and
  a JSON summary in ``analysis/clinical/metadata_gap.json``.

Library usage::

    from fetch_clinical_metadata import parse_series_matrix, fetch
    rows = parse_series_matrix(local_path)

CLI::

    python3 scripts/fetch_clinical_metadata.py --out-dir analysis/clinical/
"""
from __future__ import annotations

import argparse
import gzip
import json
import logging
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

log = logging.getLogger("clinmeta")


# ── Dataset registry ───────────────────────────────────────────────────────────

DATASETS: dict[str, dict] = {
    "tabib2021_GSE138669": {
        "tissue": "skin",
        "urls": [
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE138nnn/GSE138669/matrix/GSE138669_series_matrix.txt.gz",
        ],
    },
    "gur2022_GSE195452": {
        "tissue": "skin_gur",
        "urls": [
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE195nnn/GSE195452/matrix/GSE195452-GPL18573_series_matrix.txt.gz",
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE195nnn/GSE195452/matrix/GSE195452-GPL24676_series_matrix.txt.gz",
        ],
    },
    "gse210395": {
        "tissue": "pbmc",
        "urls": [
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE210nnn/GSE210395/matrix/GSE210395_series_matrix.txt.gz",
        ],
    },
    "morse2019_GSE128169": {
        "tissue": "lung",
        "urls": [
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE128nnn/GSE128169/matrix/GSE128169_series_matrix.txt.gz",
        ],
    },
}

# Canonical clinical fields we want surfaced as separate columns
CANONICAL_FIELDS = [
    "mrss", "modified_rodnan_skin_score",
    "disease_duration_months", "disease_duration", "duration_months",
    "age", "sex", "gender",
    "ana_specificity", "autoantibody", "scl70", "centromere", "anti_rna_pol_iii",
    "subtype", "dcssc_lcssc", "subgroup",
]


# ── Fetcher ────────────────────────────────────────────────────────────────────

def fetch(url: str, dest: Path, *, force: bool = False, timeout: int = 30) -> Path:
    """Download `url` to `dest`, returning the path.

    Skips download if `dest` exists and `force` is False.
    """
    if dest.exists() and not force:
        log.debug("cache hit: %s", dest)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.info("downloading %s", url)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp, dest.open("wb") as fh:
            while chunk := resp.read(1 << 16):
                fh.write(chunk)
    except urllib.error.URLError as e:
        raise RuntimeError(f"could not fetch {url}: {e}") from e
    return dest


# ── Parser ─────────────────────────────────────────────────────────────────────

_QUOTE = re.compile(r'^"(.*)"$')
_KV = re.compile(r"^([^:]+?)\s*:\s*(.*)$")


def _read_text(path: Path) -> str:
    """Read gz or plain text file."""
    if path.suffix == ".gz" or path.name.endswith(".txt.gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    return path.read_text(encoding="utf-8", errors="replace")


def parse_series_matrix(path: Path) -> list[dict[str, str]]:
    """Parse one series_matrix.txt.gz; return one row per sample.

    Each row carries:
    - ``sample_title``: e.g. "SC1" or "AB10128"
    - ``sample_geo``  : GSM accession
    - one column per characteristic key (snake_case_normalized)
    """
    text = _read_text(path)
    by_label: dict[str, list[str]] = defaultdict(list)
    raw_chars: list[list[str]] = []

    for line in text.splitlines():
        if not line.startswith("!"):
            continue
        parts = line.rstrip("\n").split("\t")
        head, values = parts[0], parts[1:]
        # strip enclosing quotes
        values = [_QUOTE.sub(r"\1", v) for v in values]
        if head == "!Sample_title":
            by_label["sample_title"] = values
        elif head == "!Sample_geo_accession":
            by_label["sample_geo"] = values
        elif head == "!Sample_source_name_ch1":
            by_label["source_name"] = values
        elif head == "!Sample_characteristics_ch1":
            raw_chars.append(values)

    n = len(by_label.get("sample_title") or by_label.get("sample_geo") or [])
    if n == 0:
        return []

    # Convert each !Sample_characteristics_ch1 line into a (key, value)
    # column. The key is the prefix before ":", normalised to snake_case.
    char_columns: dict[str, list[str]] = {}
    for col in raw_chars:
        # All values typically share the same key; take the first
        # non-empty as the canonical column name
        col_name = None
        for v in col:
            if not v:
                continue
            m = _KV.match(v)
            if m:
                col_name = _to_snake(m.group(1))
                break
        if col_name is None:
            # No "key:value" format; treat as opaque value
            col_name = f"characteristic_{len(char_columns) + 1}"

        col_values = []
        for v in col:
            m = _KV.match(v)
            if m:
                col_values.append(m.group(2).strip())
            else:
                col_values.append(v.strip())
        # If a column name repeats, suffix it
        base = col_name
        i = 2
        while col_name in char_columns:
            col_name = f"{base}_{i}"
            i += 1
        char_columns[col_name] = col_values

    rows = []
    for i in range(n):
        row = {
            "sample_title": (by_label.get("sample_title") or ["?"] * n)[i],
            "sample_geo":   (by_label.get("sample_geo") or [""] * n)[i],
            "source_name":  (by_label.get("source_name") or [""] * n)[i],
        }
        for col, vals in char_columns.items():
            row[col] = vals[i] if i < len(vals) else ""
        rows.append(row)
    return rows


def _to_snake(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "field"


# ── Field coalescer ────────────────────────────────────────────────────────────

def coalesce_canonical(row: dict[str, str]) -> dict[str, str | None]:
    """Return a dict with canonical clinical keys filled where possible.

    A row may carry the value under any of several aliases (e.g.
    "modified_rodnan_skin_score" or "mrss"); this picks the first match.
    Unknown keys are passed through unchanged.
    """
    aliases = {
        "mrss": ["mrss", "modified_rodnan_skin_score", "modified_rodnan",
                 "rodnan_skin_score"],
        "disease_duration_months": ["disease_duration_months",
                                    "disease_duration", "duration_months",
                                    "duration"],
        "age": ["age", "age_years"],
        "sex": ["sex", "gender"],
        "ana_specificity": ["ana_specificity", "autoantibody", "ana",
                            "autoantibody_specificity"],
        "subtype": ["subtype", "dcssc_lcssc", "subgroup", "ssc_subtype"],
        "condition": ["condition", "disease_state", "subject_status",
                      "group", "status"],
    }
    out: dict[str, str | None] = {}
    for canon, alts in aliases.items():
        out[canon] = None
        for a in alts:
            if a in row and (row[a] or "").strip():
                out[canon] = row[a].strip()
                break
    return out


# ── Driver ─────────────────────────────────────────────────────────────────────

def harvest(out_dir: Path, cache_dir: Path, *, force: bool = False) -> dict:
    """Fetch and parse all four datasets; write donor_metadata.tsv +
    metadata_gap.json. Returns the JSON summary as a dict.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    summary: dict = {"datasets": {}, "global_gap": {}}

    for ds, info in DATASETS.items():
        ds_summary = {"tissue": info["tissue"], "n_samples": 0,
                      "characteristic_columns": [],
                      "canonical_present": [], "canonical_absent": [],
                      "raw_files": []}
        for url in info["urls"]:
            fname = url.rsplit("/", 1)[-1]
            local = cache_dir / ds / fname
            try:
                fetch(url, local, force=force)
            except Exception as e:
                log.warning("could not fetch %s: %s", url, e)
                continue
            rows = parse_series_matrix(local)
            ds_summary["raw_files"].append(str(local))
            ds_summary["n_samples"] += len(rows)
            cols_here = set()
            for r in rows:
                cols_here.update(k for k in r if k not in
                                 {"sample_title", "sample_geo", "source_name"})
            ds_summary["characteristic_columns"].extend(sorted(cols_here))
            for r in rows:
                canon = coalesce_canonical(r)
                merged = {"dataset": ds, "tissue": info["tissue"], **r, **{
                    f"canon_{k}": (v if v is not None else "")
                    for k, v in canon.items()
                }}
                all_rows.append(merged)

        # canonical presence per dataset
        ds_rows = [r for r in all_rows if r["dataset"] == ds]
        if ds_rows:
            for canon in ("mrss", "disease_duration_months", "age", "sex",
                          "ana_specificity", "subtype", "condition"):
                has = any((r.get(f"canon_{canon}") or "") for r in ds_rows)
                (ds_summary["canonical_present"] if has
                 else ds_summary["canonical_absent"]).append(canon)
        summary["datasets"][ds] = ds_summary

    # Global gap analysis
    n_total = len(all_rows)
    if n_total:
        for canon in ("mrss", "disease_duration_months", "age", "sex",
                      "ana_specificity", "subtype"):
            n_have = sum(1 for r in all_rows if (r.get(f"canon_{canon}") or ""))
            summary["global_gap"][canon] = {
                "n_with": n_have, "n_total": n_total,
                "fraction": round(n_have / n_total, 3),
            }

    # Wide TSV
    if all_rows:
        all_keys = ["dataset", "tissue", "sample_title", "sample_geo"]
        canon_keys = [f"canon_{c}" for c in ("condition", "subtype", "mrss",
                                             "disease_duration_months", "age",
                                             "sex", "ana_specificity")]
        all_keys += canon_keys
        # Add per-row characteristic columns we encountered (union)
        extra = sorted({
            k for r in all_rows for k in r
            if k not in set(all_keys) and k != "source_name"
        })
        all_keys += extra
        out_tsv = out_dir / "donor_metadata.tsv"
        with out_tsv.open("w", encoding="utf-8") as fh:
            fh.write("\t".join(all_keys) + "\n")
            for r in all_rows:
                fh.write("\t".join(str(r.get(k, "")) for k in all_keys) + "\n")
        log.info("wrote %d rows × %d cols → %s", len(all_rows), len(all_keys), out_tsv)
        summary["donor_metadata_tsv"] = str(out_tsv)

    gap_path = out_dir / "metadata_gap.json"
    gap_path.write_text(json.dumps(summary, indent=2))
    log.info("wrote %s", gap_path)
    return summary


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir",   type=Path, default=Path("analysis/clinical"))
    ap.add_argument("--cache-dir", type=Path, default=Path("data/raw/series_matrix"))
    ap.add_argument("--force",     action="store_true",
                    help="Re-download even if local cache exists")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s %(message)s")

    summary = harvest(args.out_dir, args.cache_dir, force=args.force)
    print()
    print("Clinical metadata gap summary:")
    print(f"  {'field':<28} {'n_with':>8} / {'n_total':>8}  {'fraction':>9}")
    for k, v in summary.get("global_gap", {}).items():
        print(f"  {k:<28} {v['n_with']:>8} / {v['n_total']:>8}  {v['fraction']:>9.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
