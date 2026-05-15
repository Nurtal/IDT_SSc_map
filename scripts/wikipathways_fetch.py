#!/usr/bin/env python3
"""Fetch a WikiPathways pathway as GPML and (when available) BioPAX / SBGN.

Default target: WP3942 — Mechanisms of EndMT.

Endpoints (as of 2025–2026 WikiPathways REST):
    https://www.wikipathways.org/wikipathways-assets/pathways/<WPID>/<WPID>.gpml
    https://www.wikipathways.org/wikipathways-assets/pathways/<WPID>/<WPID>.owl     (BioPAX L3)
    https://www.wikipathways.org/wikipathways-assets/pathways/<WPID>/<WPID>-datanodes.tsv
The legacy webservice (`webservice.wikipathways.org`) is still mirrored too,
which we fall back to if the asset endpoint fails.

Outputs:
    curation/imports/<module>/<WPID>/<WPID>.gpml
    curation/imports/<module>/<WPID>/<WPID>.owl       (if available)
    curation/imports/<module>/<WPID>/<WPID>.datanodes.tsv (if available)
    curation/imports/<module>/<WPID>/conversion_log.txt
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ASSET_BASE = os.environ.get(
    "WIKIPATHWAYS_ASSET_BASE",
    "https://www.wikipathways.org/wikipathways-assets/pathways",
)
WS_BASE = os.environ.get(
    "WIKIPATHWAYS_WS_BASE",
    "https://webservice.wikipathways.org",
)
USER_AGENT = "SSc-MIM-wikipathways/0.1 (+https://github.com/REPLACE_ME/ssc-mim)"


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def try_endpoints(wpid: str, fmt: str) -> tuple[str, bytes] | None:
    """Try a list of endpoints for the given format, returning the first success."""
    candidates: list[str] = []
    if fmt == "gpml":
        candidates += [
            f"{ASSET_BASE}/{wpid}/{wpid}.gpml",
            f"{WS_BASE}/getPathwayAs?fileType=gpml&pwId={wpid}",
        ]
    elif fmt == "owl":
        candidates += [
            f"{ASSET_BASE}/{wpid}/{wpid}.owl",
            f"{WS_BASE}/getPathwayAs?fileType=owl&pwId={wpid}",
        ]
    elif fmt == "datanodes":
        candidates += [
            f"{ASSET_BASE}/{wpid}/{wpid}-datanodes.tsv",
        ]
    else:
        return None

    for url in candidates:
        try:
            return url, http_get(url)
        except urllib.error.HTTPError as exc:
            print(f"[skip]   {url} -> HTTP {exc.code}")
        except urllib.error.URLError as exc:
            print(f"[skip]   {url} -> {exc.reason}")
        except Exception as exc:  # noqa: BLE001
            print(f"[skip]   {url} -> {exc!r}")
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wpid", default="WP3942", help="WikiPathways pathway ID (default: WP3942 EndMT)")
    ap.add_argument("--module", required=True, choices=["M1", "M2", "M3", "M4"])
    ap.add_argument("--out-root", default="curation/imports", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv[1:])

    out_dir = args.out_root / args.module / args.wpid
    if args.dry_run:
        print(f"[dry-run] would create {out_dir} and try:")
        for fmt in ("gpml", "owl", "datanodes"):
            print(f"  - {fmt}: {ASSET_BASE}/{args.wpid}/{args.wpid}.{'tsv' if fmt=='datanodes' else fmt}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    successes = 0

    for fmt, suffix in (("gpml", ".gpml"), ("owl", ".owl"), ("datanodes", ".datanodes.tsv")):
        print(f"[fetch] {args.wpid} as {fmt}")
        result = try_endpoints(args.wpid, fmt)
        if result is None:
            log.append(f"{fmt}: all endpoints failed")
            print(f"[err]    {fmt}: all endpoints failed")
            continue
        url, data = result
        path = out_dir / f"{args.wpid}{suffix}"
        path.write_bytes(data)
        log.append(f"{fmt}: {url} -> {path} ({len(data)} bytes)")
        print(f"[ok]     {fmt}: {len(data)} bytes from {url}")
        successes += 1

    (out_dir / "conversion_log.txt").write_text(
        f"WikiPathways fetch for {args.wpid} (module {args.module})\n\n"
        + "\n".join(log) + "\n",
        encoding="utf-8",
    )
    print()
    print(f"[done] {successes} format(s) retrieved.")
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
