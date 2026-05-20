#!/usr/bin/env python3
"""Spearman correlation with bootstrap CI between module activation
scores (AUCell / Z-score) and clinical variables.

Addresses revision item E7. Built to consume:

- ``analysis/overlay/patient_module_scores_aucell.tsv`` (S2.1 output;
  may be empty until make overlay-multi has produced real pseudobulks).
- ``analysis/clinical/donor_metadata.tsv`` (S3.1 output).

Output:

- ``analysis/clinical/module_clinical_correlation.tsv`` — one row per
  (module, clinical_var) with Spearman ρ, bootstrap 95% CI, and n.
- ``figures/F_supp_module_clinical_scatter.svg/png`` — scatter
  matrix when at least one numeric clinical variable is present.
- If no numeric clinical variable is present, writes a banner row
  documenting the gap rather than failing silently.

The script is **safe to run before mRSS is recovered**. The result
is then a transparent "no numeric clinical variable available; gap
documented" report.

CLI::

    python3 scripts/clinical_correlation.py \
        --scores analysis/overlay/patient_module_scores_aucell.tsv \
        --metadata analysis/clinical/donor_metadata.tsv \
        --out-tsv analysis/clinical/module_clinical_correlation.tsv \
        --out-fig figures/F_supp_module_clinical_scatter.svg
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

import numpy as np

log = logging.getLogger("clincorr")

MODULES = ["M1", "M2", "M3", "M4", "ssc_tier1"]


# ── I/O ────────────────────────────────────────────────────────────────────────

def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open() as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _join_scores_to_metadata(scores: list[dict], meta: list[dict]
                              ) -> list[dict]:
    """Inner-join on (dataset, donor_id ↔ sample_title)."""
    by_key: dict[tuple[str, str], dict] = {}
    for r in meta:
        key = (r.get("dataset", ""), r.get("sample_title", ""))
        by_key[key] = r
    joined = []
    for s in scores:
        ds, donor = s.get("dataset", ""), s.get("donor_id", "")
        m = by_key.get((ds, donor))
        if m is None:
            continue
        merged = {**s, **{f"meta_{k}": v for k, v in m.items()}}
        joined.append(merged)
    return joined


# ── Stats ──────────────────────────────────────────────────────────────────────

def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman ρ as Pearson on ranks."""
    if x.size < 3:
        return float("nan")
    from scipy.stats import rankdata
    rx, ry = rankdata(x), rankdata(y)
    mx, my = rx.mean(), ry.mean()
    num = ((rx - mx) * (ry - my)).sum()
    den = (((rx - mx) ** 2).sum() * ((ry - my) ** 2).sum()) ** 0.5
    return float(num / den) if den else float("nan")


def bootstrap_ci(x: np.ndarray, y: np.ndarray, *, n_boot: int = 1000,
                 seed: int = 0, alpha: float = 0.05
                 ) -> tuple[float, float]:
    if x.size < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = x.size
    rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        rhos[i] = spearman(x[idx], y[idx])
    lo, hi = np.nanquantile(rhos, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


# ── Driver ─────────────────────────────────────────────────────────────────────

def analyse(scores_path: Path, meta_path: Path, out_tsv: Path,
            *, n_boot: int = 1000, fig_path: Path | None = None) -> dict:
    if not scores_path.exists():
        log.warning("scores TSV missing: %s — emitting gap-only report",
                    scores_path)
        return _write_gap(out_tsv, reason="scores_absent",
                          scores_path=scores_path, meta_path=meta_path)

    scores = _read_tsv(scores_path)
    if not scores:
        return _write_gap(out_tsv, reason="scores_empty",
                          scores_path=scores_path, meta_path=meta_path)

    meta = _read_tsv(meta_path) if meta_path.exists() else []
    joined = _join_scores_to_metadata(scores, meta) if meta else scores

    # Find which numeric clinical variables we actually have
    canonical = ["mrss", "disease_duration_months", "age"]
    numeric_cols: list[str] = []
    for c in canonical:
        key = f"meta_canon_{c}"
        vals = [(r.get(key) or "").strip() for r in joined]
        non_empty = [v for v in vals if v]
        if len(non_empty) >= 3:
            try:
                [float(v) for v in non_empty]
                numeric_cols.append(key)
            except ValueError:
                continue

    if not numeric_cols:
        return _write_gap(out_tsv, reason="no_numeric_clinical_var",
                          scores_path=scores_path, meta_path=meta_path,
                          n_donors_scored=len(scores), n_joined=len(joined))

    # Spearman for each (module, numeric_var)
    out_rows = []
    for col in numeric_cols:
        for mod in MODULES:
            xs, ys = [], []
            for r in joined:
                v_y = (r.get(col) or "").strip()
                v_x = (r.get(mod) or "").strip()
                if not v_y or not v_x:
                    continue
                try:
                    ys.append(float(v_y))
                    xs.append(float(v_x))
                except ValueError:
                    continue
            x, y = np.asarray(xs), np.asarray(ys)
            rho = spearman(x, y)
            lo, hi = bootstrap_ci(x, y, n_boot=n_boot)
            out_rows.append({
                "module": mod,
                "clinical_var": col.replace("meta_canon_", ""),
                "n": int(x.size),
                "spearman_rho": round(rho, 4),
                "ci_lo": round(lo, 4),
                "ci_hi": round(hi, 4),
            })

    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with out_tsv.open("w") as fh:
        cols = ["module", "clinical_var", "n", "spearman_rho", "ci_lo", "ci_hi"]
        fh.write("\t".join(cols) + "\n")
        for r in out_rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    log.info("wrote %d (module, clinical_var) tests → %s", len(out_rows), out_tsv)

    # Optional scatter figure
    if fig_path:
        _render_scatter(joined, numeric_cols, fig_path)

    return {"status": "ok", "n_tests": len(out_rows),
            "numeric_clinical_vars": [c.replace("meta_canon_", "") for c in numeric_cols],
            "out_tsv": str(out_tsv)}


def _write_gap(out_tsv: Path, *, reason: str, **info) -> dict:
    """Emit a gap-only TSV with a single banner row + JSON-style note."""
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with out_tsv.open("w") as fh:
        fh.write("module\tclinical_var\tn\tspearman_rho\tci_lo\tci_hi\tnote\n")
        info_str = "; ".join(f"{k}={v}" for k, v in info.items())
        fh.write(f"-\t-\t0\tNA\tNA\tNA\tgap reason: {reason}; {info_str}\n")
    log.warning("clinical correlation: %s (see %s)", reason, out_tsv)
    return {"status": reason, **info, "out_tsv": str(out_tsv)}


def _render_scatter(joined: list[dict], numeric_cols: list[str],
                    fig_path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        log.warning("matplotlib absent; skipping figure")
        return
    n_vars = len(numeric_cols)
    fig, axes = plt.subplots(len(MODULES), n_vars,
                             figsize=(3.5 * n_vars, 2.5 * len(MODULES)),
                             dpi=110, squeeze=False)
    for i, mod in enumerate(MODULES):
        for j, col in enumerate(numeric_cols):
            ax = axes[i][j]
            xs, ys = [], []
            for r in joined:
                vx = (r.get(mod) or "").strip()
                vy = (r.get(col) or "").strip()
                if not vx or not vy:
                    continue
                try:
                    xs.append(float(vx)); ys.append(float(vy))
                except ValueError:
                    continue
            if xs:
                ax.scatter(xs, ys, alpha=0.7, s=18)
                rho = spearman(np.asarray(xs), np.asarray(ys))
                ax.set_title(f"{mod} vs {col.replace('meta_canon_','')}\nρ={rho:+.2f}, n={len(xs)}",
                             fontsize=9)
            ax.set_xlabel(mod)
            ax.set_ylabel(col.replace("meta_canon_", ""))
    plt.tight_layout()
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_path, format="svg")
    fig.savefig(fig_path.with_suffix(".png"), format="png", dpi=300)
    plt.close(fig)
    log.info("wrote %s", fig_path)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scores",   type=Path,
                    default=Path("analysis/overlay/patient_module_scores_aucell.tsv"))
    ap.add_argument("--metadata", type=Path,
                    default=Path("analysis/clinical/donor_metadata.tsv"))
    ap.add_argument("--out-tsv",  type=Path,
                    default=Path("analysis/clinical/module_clinical_correlation.tsv"))
    ap.add_argument("--out-fig",  type=Path,
                    default=Path("figures/F_supp_module_clinical_scatter.svg"))
    ap.add_argument("--n-boot",   type=int, default=1000)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s %(message)s")
    summary = analyse(args.scores, args.metadata, args.out_tsv,
                      n_boot=args.n_boot, fig_path=args.out_fig)
    print("clinical correlation summary:", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
