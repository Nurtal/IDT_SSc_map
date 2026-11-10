#!/usr/bin/env python3
"""Analysis C — OpenTargets coverage of the map (descriptive; issue #12).

CORROBORATION, NOT VALIDATION (`CONTEXT.md` sense 3; pre-spec §5). OpenTargets
aggregates literature the curation may itself have drawn on. This script
describes how many SSc-associated targets the map covers, by evidence type,
for comparability with the sibling disease map. It emits no threshold, no
test and no verdict.

Disease: systemic sclerosis, MONDO_0005100 (the same id resolved for Analysis B).
Targets: every target OpenTargets associates with it, any score; a target
"has" an evidence type when its datatype score for that type is present.
Map symbols are resolved to current approved HGNC symbols (screen_cohorts.Hgnc,
TAZ -> WWTR1 override) and matched on OpenTargets' approved symbol.

Outputs:
  analysis/validation/opentargets_coverage.json
  figures/F_opentargets_upset.svg / .png

Run:
    python3 scripts/opentargets_coverage.py --fetch   # snapshot into data/raw/opentargets/
    python3 scripts/opentargets_coverage.py           # analyse the snapshot, draw the figure
    python3 scripts/opentargets_coverage.py --check   # exit 1 if the JSON would change
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import screen_cohorts as sc  # noqa: E402

API = "https://api.platform.opentargets.org/api/v4/graphql"
DISEASE = "MONDO_0005100"
SNAPSHOT = ROOT / "data/raw/opentargets/ssc_associated_targets.json"
OUT = ROOT / "analysis/validation/opentargets_coverage.json"
FIG = ROOT / "figures/F_opentargets_upset"
MODULES = ("M1", "M2", "M3", "M4", "M5")
ROLE = ("Corroboration, not validation: a description of how far OpenTargets' SSc-associated targets "
        "are covered by the map. OpenTargets aggregates literature the curation may have drawn on.")

QUERY = """query($id:String!,$i:Int!,$n:Int!,$o:String){
  meta { dataVersion { year month iteration } apiVersion { x y z } }
  disease(efoId:$id){ id name associatedTargets(orderByScore:$o, page:{index:$i,size:$n}){ count
    rows { score target { id approvedSymbol } datatypeScores { id score } } } } }"""


def _post(variables: dict) -> dict:
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json",
                                                           "User-Agent": "ssc-mim-opentargets"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["data"]
        except Exception:  # noqa: BLE001 - transient API errors; retried
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch() -> None:
    # Paging is not stable over score-tied rows (overlaps and gaps observed), and
    # 3000 is the page ceiling. The two orderings' first pages together cover a
    # disease with up to 6000 targets; completeness is checked, not assumed.
    by_id = {}
    for order in ("score desc", "score asc"):
        d = _post({"id": DISEASE, "i": 0, "n": 3000, "o": order})
        at = d["disease"]["associatedTargets"]
        for r in at["rows"]:
            by_id[r["target"]["id"]] = r
    count = at["count"]
    if len(by_id) != count:
        raise RuntimeError(f"incomplete snapshot: {len(by_id)} ids for {count}")
    rows = list(by_id.values())
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps({
        "api": API, "downloaded": time.strftime("%Y-%m-%d"), "meta": d["meta"],
        "disease": {"id": d["disease"]["id"], "name": d["disease"]["name"], "count": at["count"]},
        "rows": sorted(rows, key=lambda r: r["target"]["id"]),
    }, indent=1, sort_keys=True))


def analyse() -> dict:
    snap = json.loads(SNAPSHOT.read_text())
    hgnc = sc.Hgnc(sc.HGNC)
    sets = {m: {hgnc.map_symbol(s) for s in v} for m, v in sc.frozen_genesets().items()}
    map_symbols = set().union(*sets.values())

    ev: dict[str, set[str]] = {}
    for r in snap["rows"]:  # a few symbols carry several Ensembl ids: union their evidence
        ev.setdefault(r["target"]["approvedSymbol"], set()).update(d["id"] for d in r["datatypeScores"])
    evidence = {s: sorted(v) for s, v in ev.items()}
    targets = set(evidence)
    covered = targets & map_symbols
    types = sorted({t for v in evidence.values() for t in v})

    per_type = {}
    for t in types:
        with_t = {s for s, v in evidence.items() if t in v}
        per_type[t] = {"n_targets": len(with_t), "n_covered": len(with_t & map_symbols),
                       "fraction_covered": round(len(with_t & map_symbols) / len(with_t), 4)}
    intersections = Counter(tuple(evidence[s]) for s in covered)
    v = snap["meta"]["dataVersion"]
    return {
        "analysis": "C — OpenTargets coverage (descriptive)",
        "role": ROLE,
        "source": {"api": snap["api"], "downloaded": snap["downloaded"],
                   "data_version": f"{v['year']}.{v['month']}" + (f".{v['iteration']}" if v.get("iteration") else ""),
                   "disease": snap["disease"]},
        "n_targets": len(targets),
        "n_map_symbols": len(map_symbols),
        "n_covered": len(covered),
        "fraction_of_targets_covered": round(len(covered) / len(targets), 4),
        "fraction_of_map_in_opentargets": round(len(covered) / len(map_symbols), 4),
        "per_evidence_type": per_type,
        "per_module": {m: {"n_symbols": len(sets[m]), "n_in_opentargets": len(sets[m] & targets)}
                       for m in MODULES},
        "covered_intersections": [{"evidence_types": list(k), "n": n}
                                  for k, n in sorted(intersections.items(), key=lambda kv: (-kv[1], kv[0]))],
        "covered_targets": sorted(covered),
    }


def draw(result: dict) -> None:
    """UpSet of the covered targets by OpenTargets evidence type (static figure)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, ink2, muted, surface, blue = "#0b0b0b", "#52514e", "#d9d8d4", "#fcfcfb", "#2a78d6"
    inter = result["covered_intersections"][:15]
    types = sorted(result["per_evidence_type"], key=lambda t: -result["per_evidence_type"][t]["n_covered"])
    types = [t for t in types if result["per_evidence_type"][t]["n_covered"]]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "ssc-mim",
                         "svg.fonttype": "none"})
    fig = plt.figure(figsize=(7.2, 4.6), facecolor=surface)
    gs = fig.add_gridspec(2, 1, height_ratios=[2.2, 1.4], hspace=0.05)
    ax, mx = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    for a in (ax, mx):
        a.set_facecolor(surface)
        for s in a.spines.values():
            s.set_visible(False)
    xs = range(len(inter))
    top = max(i["n"] for i in inter)
    ax.bar(list(xs), [i["n"] for i in inter], width=0.6, color=blue, edgecolor="none")
    for x, i in zip(xs, inter):
        ax.text(x, i["n"] + top * 0.02, str(i["n"]), ha="center", va="bottom", color=ink2, fontsize=8)
    ax.set_xlim(-0.6, len(inter) - 0.4)
    ax.set_ylim(0, top * 1.15)
    ax.set_xticks([])
    ax.tick_params(axis="y", colors=ink2, length=0)
    ax.yaxis.grid(True, color=muted, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_ylabel("Map targets", color=ink2)
    fig.text(0.01, 0.975, f"{result['n_covered']} of {result['n_targets']} OpenTargets SSc targets are in the map",
             color=ink, fontsize=10, va="top")
    fig.text(0.01, 0.935, f"OpenTargets {result['source']['data_version']}, MONDO_0005100, "
             f"downloaded {result['source']['downloaded']}", color=ink2, fontsize=8, va="top")
    for y, t in enumerate(types):
        pt = result["per_evidence_type"][t]
        mx.text(-0.8, y, f"{t.replace('_', ' ')}  {pt['n_covered']}/{pt['n_targets']}",
                ha="right", va="center", color=ink2, fontsize=8)
        for x, i in zip(xs, inter):
            on = t in i["evidence_types"]
            mx.scatter(x, y, s=46, color=ink if on else muted, zorder=3)
    for x, i in zip(xs, inter):
        ys = [types.index(t) for t in i["evidence_types"] if t in types]
        if len(ys) > 1:
            mx.plot([x, x], [min(ys), max(ys)], color=ink, linewidth=2, zorder=2)
    mx.set_xlim(-0.6, len(inter) - 0.4)
    mx.set_ylim(len(types) - 0.5, -0.5)
    mx.set_xticks([]); mx.set_yticks([])
    fig.text(0.01, 0.01, "Corroboration, not validation. Bars: map targets carrying exactly that set of evidence "
             "types.\nRows: map targets / all OpenTargets SSc targets with that evidence type.",
             color=ink2, fontsize=7, va="bottom")
    fig.subplots_adjust(left=0.27, right=0.98, top=0.86, bottom=0.1)
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG.with_suffix(".svg"), facecolor=surface, metadata={"Date": None})
    fig.savefig(FIG.with_suffix(".png"), dpi=300, facecolor=surface, metadata={"Software": None})
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="snapshot OpenTargets first (network)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the JSON would change")
    args = ap.parse_args(argv)
    if args.fetch:
        fetch()
    if not SNAPSHOT.exists():
        print("[FAIL] no OpenTargets snapshot; run with --fetch", file=sys.stderr)
        return 1
    result = analyse()
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        ok = OUT.exists() and OUT.read_text() == text
        print(("[OK] " if ok else "[FAIL] ") + str(OUT.relative_to(ROOT)))
        return 0 if ok else 1
    OUT.write_text(text)
    draw(result)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} and {FIG.relative_to(ROOT)}.svg/.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
