#!/usr/bin/env python3
"""Fetch the GSE45536 whole-blood cohort used for the M5 external validation.

Dataset: GSE45536 (Streicher K et al, "The Plasma Cell Signature in
Autoimmune Disease (II)"). 99 scleroderma + 24 healthy-donor PAXgene
whole-blood samples, Affymetrix GPL570.

This cohort is **not** part of the scRNA-seq overlay — it is the external
validation set for module M5 (B-cell / autoreactivity), consumed by
scripts/validate_m5_gse45536.py (`make validate-m5`).

Two files land under data/raw/gse45536/:
  GSE45536_series_matrix.txt.gz   expression matrix + sample phenotypes
  GPL570_table.txt                probe -> Gene Symbol platform table

Both are pinned (size + SHA-256) in data/MIRROR.sha256; pass --verify to
check the on-disk copies against that manifest.

The `data/` directory is gitignored — the raw files never enter the repo;
the manifest is the provenance record.

Usage:
  scripts/fetch_gse45536.py            # download both files
  scripts/fetch_gse45536.py --probe    # print sizes / status, no download
  scripts/fetch_gse45536.py --verify   # SHA-256 check against data/MIRROR.sha256
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/raw/gse45536"

FILES = {
    "GSE45536_series_matrix.txt.gz": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE45nnn/GSE45536/matrix/"
        "GSE45536_series_matrix.txt.gz"
    ),
    "GPL570_table.txt": (
        "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
        "?acc=GPL570&targ=self&form=text&view=data"
    ),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_digests() -> dict[str, str]:
    """{filename: sha256} for the gse45536 rows of data/MIRROR.sha256."""
    out: dict[str, str] = {}
    man = ROOT / "data/MIRROR.sha256"
    for line in man.read_text().splitlines():
        line = line.strip()
        if not line or "gse45536/" not in line:
            continue
        digest, path = line.split(None, 1)
        out[Path(path.strip()).name] = digest
    return out


def probe() -> None:
    for name, url in FILES.items():
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=20) as r:
                size = int(r.headers.get("Content-Length", 0))
            print(f"{name}: {size:,} bytes  <- {url}")
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: HEAD failed ({exc})  <- {url}")


def download(name: str, url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".partial")
    t0 = time.time()
    with urllib.request.urlopen(url, timeout=300) as resp, tmp.open("wb") as fh:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        while True:
            buf = resp.read(1 << 20)
            if not buf:
                break
            fh.write(buf)
            downloaded += len(buf)
            speed = downloaded / max(1e-6, time.time() - t0) / 1e6
            tail = f"/{total:,}" if total else ""
            print(f"\r  {name}: {downloaded:,}{tail} bytes — {speed:5.1f} MB/s", end="")
        print()
    tmp.rename(target)


def verify() -> int:
    digests = manifest_digests()
    if not digests:
        print("[FAIL] no gse45536 rows in data/MIRROR.sha256")
        return 1
    rc = 0
    for name, want in digests.items():
        path = OUT_DIR / name
        if not path.exists():
            print(f"[MISSING] {name} (run scripts/fetch_gse45536.py)")
            rc = 1
            continue
        got = sha256(path)
        ok = got == want
        print(f"[{'OK' if ok else 'MISMATCH'}] {name}")
        if not ok:
            print(f"   expected {want}\n   got      {got}")
            rc = 1
    return rc


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe", action="store_true", help="print sizes only")
    ap.add_argument("--verify", action="store_true",
                    help="SHA-256 check on-disk copies vs data/MIRROR.sha256")
    args = ap.parse_args(argv[1:])

    if args.probe:
        probe()
        return 0
    if args.verify:
        return verify()

    for name, url in FILES.items():
        target = OUT_DIR / name
        if target.exists():
            print(f"[ok] already exists: {target} ({target.stat().st_size:,} bytes)")
            continue
        print(f"downloading {url} -> {target}")
        download(name, url, target)
        print(f"[ok] {target}")

    print("\nVerify against the manifest with:")
    print("  scripts/fetch_gse45536.py --verify")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
