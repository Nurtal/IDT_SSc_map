#!/usr/bin/env python3
"""Screen and freeze the independent skin cohorts for Analysis A (L2-04, issue #11).

Applies `docs/planning/external_validation_prespec.md` §3.2 BEFORE any cohort is
analysed: every candidate is checked against the four criteria in their stated
order, the first failed criterion is recorded, survivors are frozen with their
arm assignment, and the (module × cohort) multiple-testing family is declared
from each platform's coverage of the frozen gene sets. Nothing here scores a
module or compares arms.

Criteria, in order (pre-spec §3.2):
  1. SSc skin biopsies, SSc vs healthy control, n >= 20 per arm (one sample per subject);
  2. public, with per-sample condition labels in the GEO series matrix;
  3. no donor overlap with the four single-cell datasets already used;
  4. not used at any point in curation.

Criterion 3 cannot be computed from expression data; it is assessed from the
public records and the evidence is written into DONOR_OVERLAP below, verbatim,
with the curator's decision. Criterion 4 is checked by searching the curated
layer, the curation docs and the manuscript for the accession and its PMIDs.

Arm assignment rules are written per cohort below, before any scoring, and the
resulting per-sample table is committed so L2 analyses read it rather than
re-deriving it.

Outputs (deterministic):
  analysis/validation/cohort_screening.json   log incl. rejections, frozen list, family, gap
  analysis/validation/cohort_samples.tsv      per-sample arm assignment of frozen cohorts

Run:
    python3 scripts/screen_cohorts.py --fetch   # download missing inputs into data/raw/
    python3 scripts/screen_cohorts.py           # screen, write outputs
    python3 scripts/screen_cohorts.py --check   # exit 1 if outputs would change
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
GENESETS = ROOT / "analysis/validation/module_genesets.tsv"
OUT_JSON = ROOT / "analysis/validation/cohort_screening.json"
OUT_SAMPLES = ROOT / "analysis/validation/cohort_samples.tsv"
HGNC = RAW / "hgnc/hgnc_complete_set.txt"
GPL10558_ANNOT = RAW / "gpl10558/GPL10558.annot.gz"

MIN_PER_ARM = 20          # pre-spec §3.2 criterion 1
MIN_DETECTABLE = 10       # pre-spec §2 size floor
MODULES = ("M1", "M2", "M3", "M4", "M5")
GEO = "https://ftp.ncbi.nlm.nih.gov/geo"

FETCH = {
    RAW / "gse130955/GSE130955_series_matrix.txt.gz": f"{GEO}/series/GSE130nnn/GSE130955/matrix/GSE130955_series_matrix.txt.gz",
    RAW / "gse130955/GSE130955_RAW.tar": f"{GEO}/series/GSE130nnn/GSE130955/suppl/GSE130955_RAW.tar",
    RAW / "gse58095/GSE58095_series_matrix.txt.gz": f"{GEO}/series/GSE58nnn/GSE58095/matrix/GSE58095_series_matrix.txt.gz",
    RAW / "gse95065/GSE95065_series_matrix.txt.gz": f"{GEO}/series/GSE95nnn/GSE95065/matrix/GSE95065_series_matrix.txt.gz",
    GPL10558_ANNOT: f"{GEO}/platforms/GPL10nnn/GPL10558/annot/GPL10558.annot.gz",
    HGNC: "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt",
}

# Candidates in the pre-spec's order. GSE45536 is held out as the M5 positive
# control only (pre-spec §3.2) and is not screened as a new cohort.
CANDIDATES = ("GSE130955", "GSE58095", "GSE95065")
HELD_OUT = {"GSE45536": "M5 positive control (whole blood); not counted as a new cohort (pre-spec §3.2)"}

# Single-cell datasets already used (corroboration layer) and their donor origin,
# from their GEO records and papers (checked 2026-11-09).
SINGLE_CELL = {
    "GSE138669": "Tabib 2021 skin, 12 SSc / 10 HC; University of Pittsburgh (UPMC) IRB; PRESS not mentioned (PMID 34282151)",
    "GSE195452": "Gur 2022 skin+blood, 97 SSc / 56 HC; two medical centres in Israel (GEO overall design)",
    "GSE128169": "Morse 2019 lung explants, SSc-ILD; University of Pittsburgh",
    "GSE210395": "PBMC, 4 SSc / 4 HC; Hospital for Special Surgery, New York",
}

# Criterion 3 evidence and decision, per candidate (written before any scoring).
DONOR_OVERLAP = {
    "GSE130955": {
        "passes": True,
        "status": "not contradicted (residual risk declared)",
        "evidence": [
            "PRESS registry, multicentre; the PMID 31767698 author list includes the University of "
            "Pittsburgh (affiliation 19), the centre of Tabib 2021 (GSE138669).",
            "Tabib 2021 (PMID 34282151) recruited 12 SSc / 10 HC under the UPMC IRB and does not mention PRESS.",
            "No public record links any GSE130955 donor to a single-cell dataset; overlap is neither shown "
            "nor excludable. At most the 12 Tabib SSc donors could be shared with the 48 PRESS SSc donors.",
        ],
        "decision": "retained with the residual risk declared (curator decision 2026-11-09); "
                    "carried into the Analysis A limitations",
    },
    "GSE58095": {
        "passes": True,
        "status": "no overlap",
        "evidence": [
            "GENISOS cohort and an open-label imatinib study; contributors from UTHealth Houston, UCLA and "
            "the University of Michigan; no Pittsburgh or Israeli site.",
        ],
        "decision": "passes",
    },
    "GSE95065": {"passes": None, "status": "not assessed (failed criterion 1)", "evidence": [], "decision": "—"},
}

# Expression source per cohort, and the normalisation fixed before scoring (pre-spec §3.3).
EXPRESSION = {
    "GSE130955": {"platform": "GPL16791", "kind": "RNA-seq FPKM per sample (Ensembl gene IDs) in GSE130955_RAW.tar",
                  "normalisation": "log2(FPKM + 1); raw counts are not deposited, so TMM/vst is not available "
                                   "(singscore is rank-based and unaffected; the z-score sensitivity sees log2 FPKM)"},
    "GSE58095": {"platform": "GPL10558", "kind": "Illumina HT-12 v4 series matrix",
                 "normalisation": "as deposited (log2 scale, normalised by the submitters)"},
    "GSE95065": {"platform": "GPL23080", "kind": "series matrix", "normalisation": "—"},
}


# ── series-matrix parsing ──────────────────────────────────────────────────────

def read_series_header(path: Path) -> dict:
    """Return {'series': {key: [values]}, 'samples': {key: [[values per sample], ...]}}."""
    series: dict[str, list[str]] = {}
    samples: dict[str, list[list[str]]] = {}
    with gzip.open(path, "rt", errors="replace") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                break
            key, *vals = line.rstrip("\n").split("\t")
            vals = [v.strip('"') for v in vals]
            if key.startswith("!Series_"):
                series.setdefault(key[8:], []).extend(vals)
            elif key.startswith("!Sample_"):
                samples.setdefault(key[8:], []).append(vals)
    return {"series": series, "samples": samples}


def sample_fields(header: dict) -> list[dict]:
    """One dict per sample: gsm, title, source, characteristics as {key: value}."""
    s = header["samples"]
    n = len(s["geo_accession"][0])
    out = []
    for i in range(n):
        chars = {}
        for row in s.get("characteristics_ch1", []):
            v = row[i]
            if ":" in v:
                k, val = v.split(":", 1)
                chars[k.strip().lower()] = val.strip()
        out.append({
            "gsm": s["geo_accession"][0][i],
            "title": s["title"][0][i],
            "source": s.get("source_name_ch1", [[""] * n])[0][i],
            "chars": chars,
        })
    return out


# ── arm assignment rules (one sample per subject; fixed before scoring) ────────

def arms_gse130955(samples: list[dict]) -> list[tuple[str, str]]:
    """diagnosis: SSc patient | healthy control; keep each subject's first biopsy only."""
    out = []
    for s in samples:
        dx, bn = s["chars"].get("diagnosis", ""), s["chars"].get("biopsy number for this subject", "")
        if bn != "1":
            out.append(("excluded", f"repeat biopsy (number {bn}) of an already-included subject"))
        elif dx == "SSc patient":
            out.append(("SSc", "diagnosis: SSc patient, first biopsy"))
        elif dx == "healthy control":
            out.append(("HC", "diagnosis: healthy control"))
        else:
            out.append(("excluded", f"unrecognised diagnosis {dx!r}"))
    return out


def arms_gse58095(samples: list[dict]) -> list[tuple[str, str]]:
    """Labels are spread over shifted characteristic columns. PATIENTnn = SSc baseline;
    `group: Control` = HC; `group: SSc` = SSc unless marked unaffected skin; any
    `time point` sample is a longitudinal re-sample (5 patients) and is excluded."""
    out = []
    for s in samples:
        c = s["chars"]
        if "time point" in c:
            out.append(("excluded", f"longitudinal re-sample (time point: {c['time point']})"))
        elif c.get("group") == "Control":
            out.append(("HC", "group: Control"))
        elif c.get("group") == "SSc" and c.get("affected (1=yes)") == "0":
            out.append(("excluded", "group: SSc but affected (1=yes): 0 (unaffected skin)"))
        elif c.get("group") == "SSc" or s["title"].startswith("PATIENT"):
            out.append(("SSc", "group: SSc" if c.get("group") == "SSc" else "PATIENT series (SSc baseline)"))
        else:
            out.append(("excluded", "no condition label"))
    return out


def arms_gse95065(samples: list[dict]) -> list[tuple[str, str]]:
    out = []
    for s in samples:
        dx = s["chars"].get("dx", "")
        if dx == "diffuse cutaneous systemic sclerosis":
            out.append(("SSc", f"dx: {dx}"))
        elif dx == "healthy":
            out.append(("HC", "dx: healthy"))
        else:
            out.append(("excluded", f"unrecognised dx {dx!r}"))
    return out


ARM_RULES = {"GSE130955": arms_gse130955, "GSE58095": arms_gse58095, "GSE95065": arms_gse95065}


# ── platform coverage of the frozen gene sets ──────────────────────────────────

# Map symbols whose HGNC history would resolve them to the wrong gene. The map's
# TAZ species is the YAP co-activator (YAP1_TAZ complexes in M2), i.e. WWTR1;
# HGNC's previous symbol TAZ belongs to TAFAZZIN, a different gene.
MAP_SYMBOL_OVERRIDES = {"TAZ": "WWTR1"}


class Hgnc:
    """Current approved HGNC symbols, Ensembl IDs, and previous-symbol resolution."""

    def __init__(self, path: Path):
        self.approved: set[str] = set()
        self.ensembl: dict[str, str] = {}
        prev: dict[str, set[str]] = {}
        with path.open(newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("status") != "Approved":
                    continue
                self.approved.add(r["symbol"])
                if r.get("ensembl_gene_id"):
                    self.ensembl[r["ensembl_gene_id"]] = r["symbol"]
                for old in filter(None, (r.get("prev_symbol") or "").split("|")):
                    prev.setdefault(old, set()).add(r["symbol"])
        self.prev = {k: next(iter(v)) for k, v in prev.items() if len(v) == 1}

    def current(self, symbol: str) -> str:
        """Approved symbol for `symbol` (itself if approved, else its unique successor)."""
        if symbol in self.approved:
            return symbol
        return self.prev.get(symbol, symbol)

    def map_symbol(self, symbol: str) -> str:
        """Resolve a map symbol to the measured gene, applying the curated overrides first."""
        return MAP_SYMBOL_OVERRIDES.get(symbol) or self.current(symbol)


def measured_gse130955(tar_path: Path, hgnc: Hgnc) -> set[str]:
    """Symbols of the Ensembl genes present in every sample file (version suffix dropped)."""
    common: set[str] | None = None
    with tarfile.open(tar_path) as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            text = gzip.decompress(t.extractfile(m).read()).decode()
            ids = {ln.split("\t", 1)[0].split(".", 1)[0] for ln in text.splitlines()[1:] if ln}
            common = ids if common is None else common & ids
    return {hgnc.ensembl[e] for e in (common or set()) if e in hgnc.ensembl}


def measured_gse58095(matrix: Path, annot: Path, hgnc: Hgnc) -> set[str]:
    probes = set()
    with gzip.open(matrix, "rt", errors="replace") as fh:
        in_tbl = False
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                in_tbl = True
                next(fh)
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if in_tbl:
                probes.add(line.split("\t", 1)[0].strip('"'))
    symbols = set()
    with gzip.open(annot, "rt", errors="replace") as fh:
        header = None
        for line in fh:
            if header is None:
                if line.startswith("ID\t"):
                    header = line.rstrip("\n").split("\t")
                    i_id, i_sym = header.index("ID"), header.index("Gene symbol")
                continue
            if line.startswith("!"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) > i_sym and p[i_id] in probes and p[i_sym]:
                symbols.update(hgnc.current(s) for s in p[i_sym].split("///") if s)
    return symbols


def frozen_genesets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = {m: set() for m in MODULES}
    with GENESETS.open() as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sets[r["module"]].add(r["hgnc_symbol"])
    return sets


# ── criterion 4: not used in curation ──────────────────────────────────────────

def used_in_curation(accession: str, pmids: list[str]) -> list[str]:
    """git-grep the curation sources (curated layer, curation docs, module specs) for the
    accession or its PMIDs. The manuscript is not a curation source: it cites the frozen
    cohorts as validation data, which is not use during curation."""
    terms = [accession] + pmids
    paths = ["curation", "docs/curation", "docs/module_specs"]
    hits = []
    for term in terms:
        r = subprocess.run(["git", "grep", "-l", "-w", term, "--", *paths],
                           cwd=ROOT, capture_output=True, text=True)
        hits += [f"{term} in {p}" for p in r.stdout.split()]
    return hits


# ── screening ──────────────────────────────────────────────────────────────────

def screen(accession: str) -> tuple[dict, list[dict]]:
    path = RAW / accession.lower() / f"{accession}_series_matrix.txt.gz"
    header = read_series_header(path)
    ser = header["series"]
    samples = sample_fields(header)
    arms = ARM_RULES[accession](samples)
    n_ssc = sum(a == "SSc" for a, _ in arms)
    n_hc = sum(a == "HC" for a, _ in arms)
    tissues = sorted({s["chars"].get("tissue", s["source"]) for s in samples})
    pmids = ser.get("pubmed_id", [])
    rec = {
        "accession": accession,
        "title": ser.get("title", [""])[0],
        "platform": sorted(set(header["samples"]["platform_id"][0])),
        "type": ser.get("type", []),
        "pubmed_ids": pmids,
        "n_samples_total": len(samples),
        "tissue_labels": tissues,
        "n_ssc": n_ssc, "n_hc": n_hc,
        "n_excluded_samples": sum(a == "excluded" for a, _ in arms),
        "criteria": [],
    }

    def crit(n, passed, detail):
        rec["criteria"].append({"criterion": n, "passed": passed, "detail": detail})
        return passed

    skin = all("skin" in t.lower() for t in tissues)
    ok = crit(1, skin and n_ssc >= MIN_PER_ARM and n_hc >= MIN_PER_ARM,
              f"tissue {tissues}; {n_ssc} SSc / {n_hc} HC after one-sample-per-subject (floor {MIN_PER_ARM} per arm)")
    if ok:
        labelled = n_ssc + n_hc + rec["n_excluded_samples"] == len(samples) and \
            not any(r == "no condition label" for _, r in arms)
        ok = crit(2, labelled, "per-sample condition labels present in the series matrix"
                  if labelled else "some samples carry no condition label")
    if ok:
        d = DONOR_OVERLAP[accession]
        ok = crit(3, bool(d["passes"]), f"{d['status']}: " + " ".join(d["evidence"]))
    if ok:
        hits = used_in_curation(accession, pmids)
        ok = crit(4, not hits, "not found in the curated layer, curation docs or module specs"
                  if not hits else f"used: {hits}")
    failed = next((c["criterion"] for c in rec["criteria"] if not c["passed"]), None)
    rec["verdict"] = "verified" if failed is None else f"rejected (criterion {failed})"
    rec["donor_overlap_decision"] = DONOR_OVERLAP[accession]["decision"]
    rows = [{"cohort": accession, "gsm": s["gsm"], "title": s["title"], "arm": a, "reason": r}
            for s, (a, r) in zip(samples, arms)]
    return rec, rows


def build() -> tuple[dict, list[dict]]:
    log, sample_rows = [], []
    for acc in CANDIDATES:
        rec, rows = screen(acc)
        log.append(rec)
        if rec["verdict"] == "verified":
            sample_rows += rows
    frozen = [r["accession"] for r in log if r["verdict"] == "verified"]

    sets = frozen_genesets()
    hgnc = Hgnc(HGNC)
    resolved = {sym: hgnc.map_symbol(sym) for m in MODULES for sym in sets[m]}
    measured = {}
    if "GSE130955" in frozen:
        measured["GSE130955"] = measured_gse130955(RAW / "gse130955/GSE130955_RAW.tar", hgnc)
    if "GSE58095" in frozen:
        measured["GSE58095"] = measured_gse58095(RAW / "gse58095/GSE58095_series_matrix.txt.gz",
                                                 GPL10558_ANNOT, hgnc)

    family, coverage = [], {}
    for acc in frozen:
        coverage[acc] = {}
        for m in MODULES:
            on = {sym for sym in sets[m] if resolved[sym] in measured[acc]}
            n = len(on)
            coverage[acc][m] = {"n_symbols": len(sets[m]), "n_on_platform": n,
                                "missing": sorted(sets[m] - on),
                                "testable": n >= MIN_DETECTABLE}
            family.append({"module": m, "cohort": acc, "testable": n >= MIN_DETECTABLE})
        for r in log:
            if r["accession"] == acc:
                r["expression"] = EXPRESSION[acc]
                r["n_platform_symbols"] = len(measured[acc])

    result = {
        "prespec": "docs/planning/external_validation_prespec.md §3.2 (criteria applied in order)",
        "screened_on": "2026-11-09",
        "candidates": log,
        "held_out": HELD_OUT,
        "single_cell_datasets_used": SINGLE_CELL,
        "frozen_cohorts": frozen,
        "frozen_rule": "the verified list is frozen: a cohort may not be dropped after its result is known",
        "symbol_resolution": {
            "rule": "map symbols and platform symbols are both resolved to current approved HGNC "
                    "symbols (unique previous-symbol successor) before matching; curated overrides first",
            "overrides": MAP_SYMBOL_OVERRIDES,
            "override_reason": {"TAZ": "the map's TAZ is the YAP co-activator (WWTR1); HGNC previous "
                                       "symbol TAZ is TAFAZZIN, an unrelated gene"},
            "renamed": {k: v for k, v in sorted(resolved.items()) if k != v},
        },
        "platform_coverage": coverage,
        "family": {
            "unit": "module x cohort",
            "min_detectable_symbols": MIN_DETECTABLE,
            "testable": [f"{f['module']}|{f['cohort']}" for f in family if f["testable"]],
            "excluded_not_testable": [f"{f['module']}|{f['cohort']}" for f in family if not f["testable"]],
        },
        "gap": None if len(frozen) >= 2 else {
            "analysis": "A",
            "status": "not executable",
            "reason": f"{len(frozen)} cohort(s) survived screening; the pre-spec requires at least two "
                      "(fallback GEO query of §3.2 to be screened before declaring the gap final)",
        },
    }
    return result, sample_rows


def render(result: dict, rows: list[dict]) -> tuple[str, str]:
    cols = ["cohort", "gsm", "title", "arm", "reason"]
    tsv = "\t".join(cols) + "\n" + "".join("\t".join(r[c] for c in cols) + "\n" for r in rows)
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n", tsv


def fetch() -> None:
    for dest, url in FETCH.items():
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  fetching {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "ssc-mim-screen-cohorts"})
        with urllib.request.urlopen(req, timeout=600) as r, dest.open("wb") as fh:
            fh.write(r.read())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="download missing inputs first")
    ap.add_argument("--check", action="store_true", help="exit 1 if the outputs would change")
    args = ap.parse_args(argv)
    if args.fetch:
        fetch()
    missing = [str(p.relative_to(ROOT)) for p in FETCH if not p.exists()]
    if missing:
        print(f"[FAIL] missing inputs (run with --fetch): {missing}", file=sys.stderr)
        return 1
    result, rows = build()
    js, tsv = render(result, rows)
    if args.check:
        stale = [p for p, t in ((OUT_JSON, js), (OUT_SAMPLES, tsv)) if not p.exists() or p.read_text() != t]
        for p in stale:
            print(f"[FAIL] {p.relative_to(ROOT)} differs from a fresh screening", file=sys.stderr)
        return 1 if stale else 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(js)
    OUT_SAMPLES.write_text(tsv)
    for r in result["candidates"]:
        print(f"  {r['accession']}: {r['verdict']} — {r['n_ssc']} SSc / {r['n_hc']} HC")
    print(f"  frozen: {result['frozen_cohorts']}")
    print(f"  family: {len(result['family']['testable'])} testable, "
          f"excluded {result['family']['excluded_not_testable']}")
    if result["gap"]:
        print(f"  GAP: {result['gap']['reason']}")
    print(f"[OK] wrote {OUT_JSON.relative_to(ROOT)} and {OUT_SAMPLES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
