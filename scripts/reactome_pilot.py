#!/usr/bin/env python3
"""Reactome → CellDesigner import pilot.

Downloads a Reactome pathway in SBGN-ML and BioPAX formats, then attempts a
conversion to CellDesigner SBML via the MINERVA conversion API.

Default target: R-HSA-2173789 (TGF-beta receptor signaling activates SMADs),
which anchors module M2 of the SSc-MIM.

Outputs are written under:
  curation/imports/{module}/pilot_{pathway_id}/
    └─ {pathway_id}.sbgn       (SBGN-ML, from Reactome)
    └─ {pathway_id}.owl        (BioPAX L3, from Reactome)
    └─ {pathway_id}.celldesigner.xml  (converted via MINERVA, if successful)
    └─ conversion_log.txt

Network access is required. Use --dry-run to print the URLs and target
paths without performing any HTTP calls.

Environment variables (override defaults):
  REACTOME_BASE      default: https://reactome.org/ContentService
  MINERVA_CONVERT    default: https://minerva-service.lcsb.uni.lu/minerva/api/convert/

Usage:
  scripts/reactome_pilot.py --pathway R-HSA-2173789 --module M2
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


REACTOME_BASE = os.environ.get("REACTOME_BASE", "https://reactome.org/ContentService")
MINERVA_CONVERT = os.environ.get(
    "MINERVA_CONVERT",
    "https://minerva-service.lcsb.uni.lu/minerva/api/convert/",
)

USER_AGENT = "SSc-MIM-pilot/0.1 (+https://github.com/REPLACE_ME/ssc-mim)"


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_post(
    url: str,
    body: bytes,
    content_type: str,
    timeout: int = 120,
) -> bytes:
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"User-Agent": USER_AGENT, "Content-Type": content_type},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_sbgn(pathway: str) -> bytes:
    url = f"{REACTOME_BASE}/exporter/event/{pathway}.sbgn"
    return http_get(url)


def fetch_biopax(pathway: str, level: int = 3) -> bytes:
    url = f"{REACTOME_BASE}/exporter/event/{pathway}.sbgn?ehld=true"  # SBGN
    # BioPAX endpoint is separate:
    biopax_url = f"{REACTOME_BASE}/exporter/sbml/{pathway}.xml"
    # NOTE: Reactome's BioPAX export endpoint historically lives at
    # /exporter/biopax/{level}/{pathway}.owl ; SBML at /exporter/sbml/{pathway}.xml.
    # Try BioPAX first; if 404 fall back to SBML.
    try:
        return http_get(f"{REACTOME_BASE}/exporter/biopax/{level}/{pathway}.owl")
    except urllib.error.HTTPError:
        # Fallback to SBML so downstream conversion still has *something*.
        return http_get(biopax_url)


def convert_to_celldesigner(sbgn: bytes) -> bytes:
    """POST SBGN-ML to MINERVA's converter and request CellDesigner SBML.

    The exact endpoint signature can change between MINERVA versions. Adjust
    if the pilot reveals the expected payload format differs.
    """
    return http_post(
        MINERVA_CONVERT + "SBGN-ML:CellDesigner_SBML",
        sbgn,
        "application/xml",
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pathway", required=True, help="Reactome stable ID, e.g. R-HSA-2173789")
    ap.add_argument("--module", required=True, choices=["M1", "M2", "M3", "M4"])
    ap.add_argument(
        "--out-root",
        default="curation/imports",
        help="root directory under which the pilot outputs are placed",
    )
    ap.add_argument("--dry-run", action="store_true", help="print planned actions and exit")
    args = ap.parse_args(argv[1:])

    out_dir = Path(args.out_root) / args.module / f"pilot_{args.pathway}"
    sbgn_path = out_dir / f"{args.pathway}.sbgn"
    biopax_path = out_dir / f"{args.pathway}.owl"
    cd_path = out_dir / f"{args.pathway}.celldesigner.xml"
    log_path = out_dir / "conversion_log.txt"

    print(f"Reactome base:    {REACTOME_BASE}")
    print(f"MINERVA convert:  {MINERVA_CONVERT}")
    print(f"Target pathway:   {args.pathway} (module {args.module})")
    print(f"Output directory: {out_dir}")

    if args.dry_run:
        print("[dry-run] would create the directory and fetch:")
        print(f"  GET  {REACTOME_BASE}/exporter/event/{args.pathway}.sbgn  → {sbgn_path}")
        print(f"  GET  {REACTOME_BASE}/exporter/biopax/3/{args.pathway}.owl → {biopax_path}")
        print(f"  POST {MINERVA_CONVERT}SBGN-ML:CellDesigner_SBML           → {cd_path}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []

    # ---- 1. SBGN-ML ----------------------------------------------------
    if sbgn_path.exists() and sbgn_path.stat().st_size > 0:
        print(f"[skip] SBGN exists at {sbgn_path}")
    else:
        try:
            print(f"[fetch] SBGN-ML for {args.pathway} ...")
            sbgn = fetch_sbgn(args.pathway)
            sbgn_path.write_bytes(sbgn)
            print(f"[ok]   wrote {sbgn_path} ({len(sbgn)} bytes)")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"SBGN fetch failed: {exc!r}")
            print(f"[err]  SBGN fetch failed: {exc!r}")

    # ---- 2. BioPAX (with SBML fallback) -------------------------------
    if biopax_path.exists() and biopax_path.stat().st_size > 0:
        print(f"[skip] BioPAX exists at {biopax_path}")
    else:
        try:
            print(f"[fetch] BioPAX (or SBML fallback) for {args.pathway} ...")
            owl = fetch_biopax(args.pathway)
            biopax_path.write_bytes(owl)
            print(f"[ok]   wrote {biopax_path} ({len(owl)} bytes)")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"BioPAX/SBML fetch failed: {exc!r}")
            print(f"[err]  BioPAX/SBML fetch failed: {exc!r}")

    # ---- 3. SBGN → CellDesigner conversion ----------------------------
    if not sbgn_path.exists() or sbgn_path.stat().st_size == 0:
        notes.append("Skipping MINERVA conversion (no SBGN input).")
    elif cd_path.exists() and cd_path.stat().st_size > 0:
        print(f"[skip] CellDesigner conversion already at {cd_path}")
    else:
        try:
            print(f"[convert] SBGN-ML → CellDesigner SBML via {MINERVA_CONVERT} ...")
            cd = convert_to_celldesigner(sbgn_path.read_bytes())
            cd_path.write_bytes(cd)
            print(f"[ok]   wrote {cd_path} ({len(cd)} bytes)")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"MINERVA conversion failed: {exc!r}")
            print(f"[err]  MINERVA conversion failed: {exc!r}")

    if notes:
        log_path.write_text(
            "Reactome pilot for {pw} (module {m})\n\n".format(pw=args.pathway, m=args.module)
            + "\n".join(notes)
            + "\n",
            encoding="utf-8",
        )
        print(f"[log]  wrote {log_path}")
        print("\nReview docs/import_pilot.md for the expected outcomes.")
        return 1
    print("\n[done] pilot succeeded — review the output before treating this as the canonical import.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
