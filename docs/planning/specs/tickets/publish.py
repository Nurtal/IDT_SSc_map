#!/usr/bin/env python3
"""Publish the L2 tickets to GitHub Issues, in dependency order.

Run this on the machine that has `gh` installed and authenticated:

    python3 docs/planning/specs/tickets/publish.py            # tickets only
    python3 docs/planning/specs/tickets/publish.py --parent 42 # link them to spec issue #42
    python3 docs/planning/specs/tickets/publish.py --dry-run   # print, create nothing

Each ticket file's first line is its title; the rest is the issue body. Files are
created in filename order, so a ticket's blockers always exist by the time it is
created, and the {{Tn}} placeholders can be resolved to real issue numbers.

Blocking edges are recorded two ways: in the body's "Blocked by" section (always),
and as GitHub native issue dependencies (best effort — skipped with a note if the
API is unavailable on this repo).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = "ready-for-agent"


def gh(*args: str) -> str:
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{out.stderr.strip()}")
    return out.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", help="issue number of the parent spec, if published")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(p for p in HERE.glob("[0-9][0-9]-*.md"))
    if not files:
        print("no ticket files found", file=sys.stderr)
        return 1

    if not args.dry_run:
        repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
        subprocess.run(["gh", "label", "create", LABEL, "--force"],
                       capture_output=True, text=True)  # already exists is fine
        print(f"repo: {repo}\n")

    numbers: dict[str, str] = {}   # "T1" -> "17"
    blockers: dict[str, list[str]] = {}  # "T3" -> ["T1"]

    for idx, path in enumerate(files, start=1):
        key = f"T{idx}"
        raw = path.read_text(encoding="utf-8")
        title = raw.split("\n", 1)[0].lstrip("# ").strip()
        body = raw.split("\n", 1)[1].strip()

        blockers[key] = re.findall(r"\{\{(T\d+)\}\}", body)
        for dep in blockers[key]:
            if dep not in numbers and not args.dry_run:
                raise RuntimeError(f"{key} references {dep}, which has not been created yet")
            body = body.replace("{{%s}}" % dep, f"#{numbers.get(dep, dep)}")

        if args.parent:
            body = f"## Parent\n\n- #{args.parent}\n\n{body}"

        if args.dry_run:
            print(f"--- {key}: {title}\n{body}\n")
            numbers[key] = key
            continue

        url = gh("issue", "create", "--title", title, "--body", body, "--label", LABEL)
        numbers[key] = url.rsplit("/", 1)[-1]
        print(f"{key} -> #{numbers[key]}  {title}")

    if args.dry_run:
        return 0

    # Native dependency edges, best effort.
    print("\nadding native blocked-by edges…")
    for key, deps in blockers.items():
        for dep in deps:
            child, blocker = numbers[key], numbers[dep]
            try:
                blocker_id = json.loads(gh("api", f"repos/{repo}/issues/{blocker}"))["id"]
                gh("api", "--method", "POST",
                   f"repos/{repo}/issues/{child}/dependencies/blocked_by",
                   "-F", f"issue_id={blocker_id}")
                print(f"  #{child} blocked by #{blocker}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [skip] #{child} blocked by #{blocker}: {exc}\n"
                      f"         the body's 'Blocked by' section still records it")

    print("\ndone. Frontier (no open blockers): #%s" % numbers["T1"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
