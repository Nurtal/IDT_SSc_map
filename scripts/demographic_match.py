#!/usr/bin/env python3
"""Propensity-score matching between SSc and HC donors on age/sex.

Addresses revision item E12 (R2-M7): the manuscript SSc-vs-HC
contrasts mix donors across four cohorts with no explicit
demographic balancing. This script:

1. Loads ``analysis/clinical/donor_metadata.tsv`` (S3.1 output).
2. Identifies donors with age + sex recorded.
3. Fits a logistic propensity model ``P(SSc | age + sex)`` (closed
   form scikit-learn LogisticRegression).
4. Performs 1:1 nearest-neighbour matching on propensity, no
   replacement, with a calliper of 0.2 × σ(propensity logit).
5. Writes ``analysis/clinical/demographics_summary.tsv`` (per-dataset
   counts) and ``analysis/clinical/sensitivity_matched_hc.tsv``
   (donor_id × matched flag).

Safe to run before age/sex are recovered: emits a gap-only banner
in that case (same pattern as clinical_correlation.py).

CLI::

    python3 scripts/demographic_match.py \
        --metadata analysis/clinical/donor_metadata.tsv \
        --out-dir  analysis/clinical/
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

log = logging.getLogger("demomatch")


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open() as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _normalise_sex(v: str) -> int | None:
    v = v.strip().lower()
    if v in ("m", "male", "h", "homme", "1"):
        return 1
    if v in ("f", "female", "w", "femme", "0"):
        return 0
    return None


def _normalise_age(v: str) -> float | None:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _normalise_condition(v: str) -> str | None:
    v = v.strip().lower()
    if "ssc" in v or "ssc_ild" in v:
        return "SSc"
    if "control" in v or "healthy" in v or v == "hc":
        return "HC"
    return None


def gather_eligible(rows: list[dict]) -> list[dict]:
    """Return rows with age+sex+condition recoverable."""
    eligible = []
    for r in rows:
        age = _normalise_age(r.get("canon_age") or "")
        sex = _normalise_sex(r.get("canon_sex") or "")
        cond = _normalise_condition(r.get("canon_condition") or "")
        if age is None or sex is None or cond is None:
            continue
        eligible.append({
            "dataset": r.get("dataset", ""),
            "tissue":  r.get("tissue", ""),
            "donor":   r.get("sample_title", ""),
            "age":     age, "sex": sex, "group": cond,
        })
    return eligible


def propensity_match(eligible: list[dict], *, calliper_sd: float = 0.2,
                     seed: int = 0) -> list[dict]:
    """1:1 nearest-neighbour matching on logistic-propensity logit.

    Returns the original rows annotated with ``matched`` (0/1) and
    ``matched_to`` (donor id of the partner if matched).
    """
    if len(eligible) < 4:
        for r in eligible:
            r["matched"] = 0
            r["matched_to"] = ""
        return eligible

    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        log.warning("scikit-learn absent; falling back to age-only Euclidean match")
        return _euclidean_match(eligible, calliper_sd, seed)

    X = np.array([[r["age"], r["sex"]] for r in eligible], dtype=float)
    y = np.array([1 if r["group"] == "SSc" else 0 for r in eligible], dtype=int)

    if y.sum() == 0 or y.sum() == len(y):
        for r in eligible:
            r["matched"] = 0
            r["matched_to"] = ""
        return eligible

    lr = LogisticRegression(solver="liblinear", random_state=seed).fit(X, y)
    # Logit of propensity (more linear than raw probability)
    p = lr.predict_proba(X)[:, 1].clip(1e-6, 1 - 1e-6)
    logit = np.log(p / (1 - p))

    calliper = calliper_sd * float(logit.std()) if logit.std() > 0 else float("inf")
    ssc_idx = [i for i, r in enumerate(eligible) if r["group"] == "SSc"]
    hc_idx  = [i for i, r in enumerate(eligible) if r["group"] == "HC"]
    used_hc: set[int] = set()
    for r in eligible:
        r["matched"] = 0
        r["matched_to"] = ""

    rng = np.random.default_rng(seed)
    rng.shuffle(ssc_idx)
    for si in ssc_idx:
        best, best_d = None, float("inf")
        for hj in hc_idx:
            if hj in used_hc:
                continue
            d = abs(logit[si] - logit[hj])
            if d < best_d:
                best_d, best = d, hj
        if best is not None and best_d <= calliper:
            used_hc.add(best)
            eligible[si]["matched"] = 1
            eligible[best]["matched"] = 1
            eligible[si]["matched_to"] = eligible[best]["donor"]
            eligible[best]["matched_to"] = eligible[si]["donor"]
    return eligible


def _euclidean_match(eligible: list[dict], calliper_sd: float,
                     seed: int) -> list[dict]:
    ages = np.array([r["age"] for r in eligible], dtype=float)
    sds = float(ages.std()) or 1.0
    calliper = calliper_sd * sds
    ssc_idx = [i for i, r in enumerate(eligible) if r["group"] == "SSc"]
    hc_idx  = [i for i, r in enumerate(eligible) if r["group"] == "HC"]
    used: set[int] = set()
    for r in eligible:
        r["matched"] = 0
        r["matched_to"] = ""
    rng = np.random.default_rng(seed)
    rng.shuffle(ssc_idx)
    for si in ssc_idx:
        # match on same sex first, closest age second
        candidates = [hj for hj in hc_idx
                      if hj not in used and eligible[hj]["sex"] == eligible[si]["sex"]]
        if not candidates:
            continue
        best = min(candidates, key=lambda hj: abs(ages[hj] - ages[si]))
        if abs(ages[best] - ages[si]) <= calliper:
            used.add(best)
            eligible[si]["matched"] = 1
            eligible[best]["matched"] = 1
            eligible[si]["matched_to"] = eligible[best]["donor"]
            eligible[best]["matched_to"] = eligible[si]["donor"]
    return eligible


def write_demographics_summary(rows: list[dict], out: Path) -> None:
    """Per-dataset n_ssc / n_hc / mean age / sex split."""
    out.parent.mkdir(parents=True, exist_ok=True)
    per_ds: dict[str, dict] = defaultdict(lambda: {"ssc_n": 0, "hc_n": 0,
                                                    "ssc_ages": [], "hc_ages": [],
                                                    "ssc_male": 0, "hc_male": 0})
    for r in rows:
        ds = r["dataset"]
        if r["group"] == "SSc":
            per_ds[ds]["ssc_n"] += 1
            per_ds[ds]["ssc_ages"].append(r["age"])
            per_ds[ds]["ssc_male"] += r["sex"]
        else:
            per_ds[ds]["hc_n"] += 1
            per_ds[ds]["hc_ages"].append(r["age"])
            per_ds[ds]["hc_male"] += r["sex"]
    with out.open("w") as fh:
        cols = ["dataset", "ssc_n", "hc_n",
                "ssc_age_mean", "hc_age_mean",
                "ssc_male_pct", "hc_male_pct"]
        fh.write("\t".join(cols) + "\n")
        for ds, s in sorted(per_ds.items()):
            ssc_age = float(np.mean(s["ssc_ages"])) if s["ssc_ages"] else float("nan")
            hc_age  = float(np.mean(s["hc_ages"]))  if s["hc_ages"]  else float("nan")
            ssc_pct = round(100 * s["ssc_male"] / max(s["ssc_n"], 1), 1)
            hc_pct  = round(100 * s["hc_male"]  / max(s["hc_n"], 1), 1)
            fh.write("\t".join([ds, str(s["ssc_n"]), str(s["hc_n"]),
                                 f"{ssc_age:.1f}", f"{hc_age:.1f}",
                                 f"{ssc_pct:.1f}", f"{hc_pct:.1f}"]) + "\n")


def write_sensitivity(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["dataset", "donor", "group", "age", "sex", "matched", "matched_to"]
    with out.open("w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join([r["dataset"], r["donor"], r["group"],
                                 f"{r['age']:.1f}", str(r["sex"]),
                                 str(r["matched"]), r["matched_to"]]) + "\n")


def _write_gap(out_dir: Path, reason: str, **info) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "demographics_summary.tsv"
    with p.open("w") as fh:
        fh.write("dataset\tssc_n\thc_n\tssc_age_mean\thc_age_mean\tssc_male_pct\thc_male_pct\tnote\n")
        info_str = "; ".join(f"{k}={v}" for k, v in info.items())
        fh.write(f"-\t0\t0\tNA\tNA\tNA\tNA\tgap reason: {reason}; {info_str}\n")
    log.warning("demographic match: %s (see %s)", reason, p)
    return {"status": reason, **info, "out_tsv": str(p)}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--metadata", type=Path,
                    default=Path("analysis/clinical/donor_metadata.tsv"))
    ap.add_argument("--out-dir",  type=Path,
                    default=Path("analysis/clinical/"))
    ap.add_argument("--calliper-sd", type=float, default=0.2)
    ap.add_argument("--seed",     type=int, default=0)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s %(message)s")

    if not args.metadata.exists():
        _write_gap(args.out_dir, "metadata_absent", path=args.metadata)
        return 0

    rows = _read_tsv(args.metadata)
    eligible = gather_eligible(rows)
    n_total = len(rows)
    n_elig = len(eligible)
    if n_elig == 0:
        _write_gap(args.out_dir, "no_age_sex_available",
                   n_total_donors=n_total)
        return 0

    matched = propensity_match(eligible, calliper_sd=args.calliper_sd,
                               seed=args.seed)
    summary_path = args.out_dir / "demographics_summary.tsv"
    sensitivity_path = args.out_dir / "sensitivity_matched_hc.tsv"
    write_demographics_summary(matched, summary_path)
    write_sensitivity(matched, sensitivity_path)

    n_matched = sum(1 for r in matched if r["matched"]) // 2
    log.info("%d / %d donors had age + sex; %d 1:1 SSc-HC pairs matched",
             n_elig, n_total, n_matched)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
