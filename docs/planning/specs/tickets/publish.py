#!/usr/bin/env python3
"""Publish the submission-plan tickets to GitHub Issues, in dependency order.

Run this on the machine that has `gh` installed and authenticated:

    python3 docs/planning/specs/tickets/publish.py --dry-run    # print, create nothing
    python3 docs/planning/specs/tickets/publish.py              # create all lots
    python3 docs/planning/specs/tickets/publish.py --lot L1 L3  # only these lots
    python3 docs/planning/specs/tickets/publish.py --parent 42  # link to a parent spec issue

Layout: one directory per lot (L1 … L5), one markdown file per ticket. A ticket's
key is its lot plus its file index — `L2/05-…md` is `L2-T5` — and blocking edges
are written in the body as `{{L2-T5}}` placeholders.

Issues are created in topological order, so a blocker always exists by the time
the ticket referencing it is created and every placeholder resolves to a real
number. Blocking edges are recorded twice: in the body's "Blocked by" section
(always) and as GitHub native issue dependencies (best effort, with a clear note
when the API is unavailable on the repo).
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
PLACEHOLDER = re.compile(r"\{\{(L\d+-T\d+)\}\}")


def gh(*args: str) -> str:
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{out.stderr.strip()}")
    return out.stdout.strip()


def load(lots: list[str] | None) -> dict[str, dict]:
    tickets: dict[str, dict] = {}
    for lot_dir in sorted(p for p in HERE.iterdir() if p.is_dir() and re.fullmatch(r"L\d+", p.name)):
        if lots and lot_dir.name not in lots:
            continue
        for i, path in enumerate(sorted(lot_dir.glob("[0-9][0-9]-*.md")), start=1):
            raw = path.read_text(encoding="utf-8")
            title, _, body = raw.partition("\n")
            tickets[f"{lot_dir.name}-T{i}"] = {
                "title": title.lstrip("# ").strip(),
                "body": body.strip(),
                "deps": PLACEHOLDER.findall(body),
                "path": path,
            }
    return tickets


def topo(tickets: dict[str, dict]) -> list[str]:
    """Blockers first. Ties broken by key so the order is stable and readable."""
    done: list[str] = []
    seen = set(done)
    remaining = dict(tickets)
    while remaining:
        ready = sorted(k for k, t in remaining.items()
                       if all(d in seen or d not in tickets for d in t["deps"]))
        if not ready:
            raise RuntimeError("dependency cycle among: " + ", ".join(sorted(remaining)))
        for k in ready:
            done.append(k)
            seen.add(k)
            del remaining[k]
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", help="issue number of the parent spec, if published")
    ap.add_argument("--lot", nargs="*", help="restrict to these lots, e.g. L1 L3")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tickets = load(args.lot)
    if not tickets:
        print("no ticket files found", file=sys.stderr)
        return 1
    order = topo(tickets)

    repo = ""
    if not args.dry_run:
        repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
        subprocess.run(["gh", "label", "create", LABEL, "--force"], capture_output=True, text=True)
        print(f"repo: {repo}\ncreating {len(order)} issues\n")

    numbers: dict[str, str] = {}
    for key in order:
        t = tickets[key]
        body = t["body"]
        for dep in t["deps"]:
            if dep in numbers:
                body = body.replace("{{%s}}" % dep, f"#{numbers[dep]}")
            elif dep in tickets:
                raise RuntimeError(f"{key} references {dep}, not yet created — topological order is wrong")
            else:
                # a blocker in a lot excluded by --lot: keep it legible
                body = body.replace("{{%s}}" % dep, f"`{dep}` (not published in this run)")
        if args.parent:
            body = f"## Parent\n\n- #{args.parent}\n\n{body}"

        if args.dry_run:
            numbers[key] = key
            print(f"--- {key}: {t['title']}")
            print(f"    blocked by: {', '.join(t['deps']) or 'nothing'}")
            continue

        url = gh("issue", "create", "--title", t["title"], "--body", body, "--label", LABEL)
        numbers[key] = url.rsplit("/", 1)[-1]
        print(f"{key} -> #{numbers[key]}  {t['title']}")

    if args.dry_run:
        frontier = [k for k in order if not tickets[k]["deps"]]
        print(f"\n{len(order)} tickets, frontier: {', '.join(frontier)}")
        return 0

    print("\nadding native blocked-by edges…")
    for key in order:
        for dep in tickets[key]["deps"]:
            if dep not in numbers or numbers[dep] == dep:
                continue
            child, blocker = numbers[key], numbers[dep]
            try:
                blocker_id = json.loads(gh("api", f"repos/{repo}/issues/{blocker}"))["id"]
                gh("api", "--method", "POST",
                   f"repos/{repo}/issues/{child}/dependencies/blocked_by",
                   "-F", f"issue_id={blocker_id}")
                print(f"  #{child} blocked by #{blocker}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [skip] #{child} blocked by #{blocker}: {exc}")
                print("         the body's 'Blocked by' section still records it")

    frontier = [f"#{numbers[k]}" for k in order if not tickets[k]["deps"]]
    print(f"\ndone. Frontier (no blockers): {', '.join(frontier)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
