#!/usr/bin/env python3
"""Fetch the Tabib 2021 SSc skin scRNAseq raw counts from GEO.

Dataset: GSE138669 (Tabib et al, Nat Commun 2021, PMID 34042322).
12 SSc + 10 HC skin biopsies, 10x Chromium, ~50k cells.

Files: 22 per-sample .h5 count matrices, total ~594 MB.

Default behaviour: download the GEO supplementary tar to
data/raw/tabib2021/, untar, and write a manifest. Resumable via the
HTTP Range header.

Usage:
  scripts/fetch_tabib.py                     # full download
  scripts/fetch_tabib.py --probe             # just print sizes / status

The `data/` directory is gitignored — the raw counts never enter the repo.
The downstream overlay pipeline in scripts/build_overlay.py uses this
directory if present, otherwise falls back to the synthetic-grounded
projection.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tarfile
import time
import urllib.request
from pathlib import Path


GEO_TAR_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE138nnn/GSE138669/suppl/GSE138669_RAW.tar"
)
GEO_FILELIST_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE138nnn/GSE138669/suppl/filelist.txt"
)


def probe() -> None:
    req = urllib.request.Request(GEO_TAR_URL, method="HEAD")
    with urllib.request.urlopen(req, timeout=20) as r:
        size = int(r.headers.get("Content-Length", 0))
    print(f"GSE138669_RAW.tar: {size:,} bytes ({size / 1e9:.2f} GB)")
    print(f"URL: {GEO_TAR_URL}")
    print(f"Filelist: {GEO_FILELIST_URL}")


def download(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".partial")
    start = tmp.stat().st_size if tmp.exists() else 0
    req = urllib.request.Request(GEO_TAR_URL)
    if start:
        req.add_header("Range", f"bytes={start}-")
        print(f"resuming from byte {start:,}")

    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("ab") as fh:
        total = int(resp.headers.get("Content-Length", 0)) + start
        downloaded = start
        chunk = 1024 * 1024  # 1 MB
        while True:
            buf = resp.read(chunk)
            if not buf:
                break
            fh.write(buf)
            downloaded += len(buf)
            if total:
                pct = 100 * downloaded / total
                speed = (downloaded - start) / max(1, time.time() - t0) / 1e6
                print(f"\r  {downloaded:,}/{total:,} bytes ({pct:5.1f}%) — {speed:5.1f} MB/s", end="")
        print()
    tmp.rename(target)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", type=Path, default=Path("data/raw/tabib2021/GSE138669_RAW.tar"))
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--untar", action="store_true", help="untar after download")
    args = ap.parse_args(argv[1:])

    if args.probe:
        probe()
        return 0

    if args.target.exists():
        print(f"[ok] already exists: {args.target} ({args.target.stat().st_size:,} bytes)")
    else:
        print(f"downloading {GEO_TAR_URL} → {args.target}")
        download(args.target)
        print(f"[ok] {args.target}")

    if args.untar:
        out_dir = args.target.parent
        with tarfile.open(args.target) as tar:
            tar.extractall(out_dir, filter="data")
        print(f"[ok] untarred to {out_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
