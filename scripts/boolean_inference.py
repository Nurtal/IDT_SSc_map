#!/usr/bin/env python3
"""Boolean inference of the SSc-MIM via CaSQ.

Converts SSc_MIM_integrated.xml (CellDesigner SBML L2v4) to SBML-qual
using `casq` (Soliman group / Inria; in environment.yml).

Output:
  analysis/boolean/ssc_mim.sbml-qual
  analysis/boolean/boolean_inference.report.json

The SBML-qual is loadable by GINsim, BioLQM, MaBoSS, and bonesis for
perturbation simulation (e.g. TGF-β ON → ECM_deposition reachable?).
This v1.0 ships the file; simulation harness is queued for v1.1.

Usage:
  scripts/boolean_inference.py
  scripts/boolean_inference.py --casq /path/to/casq      # override binary
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--integrated",
        type=Path,
        default=Path("curation/celldesigner/SSc_MIM_integrated.xml"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("analysis/boolean/ssc_mim.sbml-qual"),
    )
    ap.add_argument("--casq", default="casq", help="path to the casq CLI")
    args = ap.parse_args(argv[1:])

    casq = shutil.which(args.casq) or shutil.which(".venv/bin/casq")
    if casq is None:
        print(
            "casq not found in PATH. Install: pip install casq (already in environment.yml)\n"
            "Or activate the sscmim conda env / .venv.",
            file=sys.stderr,
        )
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    print(f"running: {casq} {args.integrated} {args.out}")
    r = subprocess.run([casq, str(args.integrated), str(args.out)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        print(f"casq exited {r.returncode}", file=sys.stderr)
        return r.returncode
    print(r.stdout.strip() or "[ok] casq run completed")

    # Count qual species + transitions
    try:
        from xml.etree import ElementTree as ET
        t = ET.parse(args.out)
        QUAL = "http://www.sbml.org/sbml/level3/version1/qual/version1"
        n_qs = len(t.findall(f".//{{{QUAL}}}qualitativeSpecies"))
        n_tr = len(t.findall(f".//{{{QUAL}}}transition"))
    except Exception:
        n_qs = n_tr = -1

    report = {
        "input": str(args.integrated),
        "output": str(args.out),
        "qualitative_species": n_qs,
        "transitions": n_tr,
        "note": "Load in GINsim / BioLQM / MaBoSS / bonesis for perturbation simulation.",
    }
    report_path = args.out.with_suffix(args.out.suffix + ".report.json")
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[ok] {args.out}: {n_qs} qual species, {n_tr} transitions")
    print(f"[ok] {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
