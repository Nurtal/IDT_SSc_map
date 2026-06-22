#!/usr/bin/env python3
"""Build a per-interaction literature dossier so the human reviewer has maximum context to decide.

For every curated interaction this queries PubMed (NCBI E-utils) for articles that co-mention the
interaction's participants, fetches their abstracts, and splits the hits into two lists:
  - support  : articles co-mentioning >=2 participants with no contrary cue (candidate support)
  - contrary : articles co-mentioning the participants AND carrying a contrary cue (a null result,
               "no effect / not associated / did not", or an opposite-direction signal such as
               "anti-fibrotic / protective") — surfaced separately so the reviewer can weigh them

These are *candidate* references retrieved by query + flagged by lexical cue — NOT adjudicated
verdicts and NOT fabricated. Every PMID is real (returned by esearch). The reviewer reads and judges.

Outputs:
    curation/evidence_dossier.json     {reaction_id: {support:[...], contrary:[...]}}
Cache (resumable): the JSON itself is the cache — a reaction already present is skipped unless
--refresh. Use --offline to only emit from what is already cached.

Run: python3 scripts/mine_evidence_dossier.py            # all reactions, resumable
     python3 scripts/mine_evidence_dossier.py --only ssc_M2_031 --refresh
Network: NCBI E-utils. Honours NCBI_API_KEY for a higher rate limit.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from mine_pdf_quotes import SYN, clean  # reuse the symbol->synonym regexes + text cleaner

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
OUT = ROOT / "curation/evidence_dossier.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "SSc-MIM-dossier/0.1 (mailto:nathan.foulquier.pro@gmail.com)"
SLEEP = 0.12 if os.environ.get("NCBI_API_KEY") else 0.34

# plain-text names (for the PubMed *query*) where the symbol differs a lot from the spoken name
PLAINQ = {
    "IFNB1": ["interferon beta", "type I interferon"], "IFNA1": ["interferon alpha", "type I interferon"],
    "IFNG": ["interferon gamma"], "MB21D1": ["cGAS"], "TMEM173": ["STING"],
    "CCN2": ["CTGF", "connective tissue growth factor"], "LGALS3": ["galectin-3"], "EDN1": ["endothelin-1"],
    "EDNRA": ["endothelin receptor A"], "PF4": ["CXCL4"], "ACTA2": ["alpha-smooth muscle actin"],
    "FAP": ["fibroblast activation protein"], "CDH2": ["N-cadherin"], "CDH5": ["VE-cadherin"],
    "TEK": ["Tie2"], "ANGPT1": ["angiopoietin-1"], "ANGPT2": ["angiopoietin-2"], "MS4A1": ["CD20"],
    "TNFSF13B": ["BAFF"], "FLI1": ["Fli-1"], "HTR2B": ["5-HT2B receptor"], "LPAR1": ["LPA receptor 1"],
    "SNAI1": ["Snail"], "SNAI2": ["Slug"], "NICD1": ["Notch"], "GREM1": ["gremlin"], "JUNB": ["JunB"],
}
GENERIC = {"complex", "active", "activated", "repressed", "inhibited", "dimer", "phenotype", "committed",
           "lineage", "bound", "stiffened", "myofibroblast", "signalling", "signaling", "cell", "ext",
           "ecm", "cyto", "nuc", "pm", "er", "endo", "p", "proFibrotic", "fibroblast", "macrophage",
           "ISG", "signature", "vascular", "remodelling", "Th", "lineage", "autoAb", "production"}
CONTRARY = re.compile(r"\b(no effect|not associated|did not|does not|do not|failed to|no significant|"
                      r"no change|unaffected|independent of|no correlation|not required|not necessary|"
                      r"in contrast|contrary to|anti-?fibrotic|protective|suppress(?:es|ed)? fibrosis|"
                      r"attenuat\w+ fibrosis|reduce[sd]? fibrosis|negative result|paradoxical)", re.I)
# an article only counts if it actually touches SSc / fibrosis / the relevant tissue biology
CONTEXT = re.compile(r"\b(systemic sclerosis|scleroderma|SSc|fibros\w+|fibroblast|myofibroblast|collagen|"
                     r"dermal|skin|pulmonary|lung|vascul\w+|sclerot\w+|extracellular matrix|ECM|"
                     r"endotheli\w+|autoimmun\w+)\b", re.I)


def eutils(ep: str, **p) -> bytes:
    p.setdefault("retmode", "xml")
    if os.environ.get("NCBI_API_KEY"):
        p["api_key"] = os.environ["NCBI_API_KEY"]
    url = f"{EUTILS}/{ep}.fcgi?" + urllib.parse.urlencode(p)
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def participants(row: dict) -> list[tuple[str, re.Pattern]]:
    """Searchable participants: (symbol, abstract-matching regex incl. synonyms). Drops phenotypes."""
    out, seen = [], set()
    for field in ("reactants", "products", "modifiers"):
        for chunk in (row.get(field, "") or "").split(";"):
            base = chunk.split("__", 1)[0].strip()
            for tok in re.split(r"[_:/]", base):
                tok = tok.strip()
                if len(tok) < 2 or tok in GENERIC or tok.lower() in seen:
                    continue
                if not (any(c.isdigit() for c in tok) or tok[0].isupper()):
                    continue
                seen.add(tok.lower())
                forms = [re.escape(tok)] + SYN.get(tok.upper(), []) + [re.escape(x) for x in PLAINQ.get(tok.upper(), [])]
                out.append((tok, re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(forms) + r")(?![A-Za-z0-9])", re.I)))
    return out


def query_term(sym: str) -> str:
    names = [sym] + PLAINQ.get(sym.upper(), [])
    return "(" + " OR ".join(f'"{n}"[tiab]' for n in dict.fromkeys(names)) + ")"


def esearch(term: str, n: int = 12) -> list[str]:
    d = json.loads(eutils("esearch", db="pubmed", term=term, retmax=n, sort="relevance", retmode="json"))
    return d.get("esearchresult", {}).get("idlist", [])


def fetch(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    root = ET.fromstring(eutils("efetch", db="pubmed", id=",".join(ids), rettype="abstract"))
    out = {}
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        te = art.find(".//ArticleTitle")
        title = "".join(te.itertext()) if te is not None else ""
        year = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
        jr = art.findtext(".//Journal/ISOAbbreviation") or ""
        ab = clean(" ".join("".join(a.itertext()) for a in art.iter("AbstractText")))
        out[pmid] = {"pmid": pmid, "title": clean(title), "year": year, "journal": jr, "abstract": ab}
    return out


def snippet(ab: str, m: re.Match) -> str:
    i, j = max(0, m.start() - 90), min(len(ab), m.end() + 90)
    return ("…" if i else "") + ab[i:j].strip() + ("…" if j < len(ab) else "")


def dossier(row: dict) -> dict:
    parts = participants(row)
    if not parts:
        return {"support": [], "contrary": [], "note": "no searchable gene participant"}
    syms = [s for s, _ in parts][:3]
    term = " AND ".join(query_term(s) for s in syms)
    ctx = '("systemic sclerosis" OR scleroderma OR fibrosis OR fibroblast)'
    ids = esearch(f"{term} AND {ctx}")
    time.sleep(SLEEP)
    if len(ids) < 4:                                   # widen if the SSc-context query is too narrow
        ids = list(dict.fromkeys(ids + esearch(term)))
        time.sleep(SLEEP)
    own = {(row.get("pmid") or "").strip(), *(row.get("secondary_pmids", "") or "").split(";")}
    arts = fetch([i for i in ids if i not in own][:14])
    time.sleep(SLEEP)
    need = 2 if len(parts) >= 2 else 1                 # single-gene reactions (gene->phenotype) need 1
    support, contrary = [], []
    for pid in ids:
        a = arts.get(pid)
        if not a:
            continue
        hay = a["title"] + " " + a["abstract"]
        hit = sum(1 for _, rx in parts if rx.search(hay))
        if hit < need or not CONTEXT.search(hay):      # co-mention + SSc/fibrosis relevance required
            continue
        ref = {"pmid": pid, "title": a["title"], "year": a["year"], "journal": a["journal"]}
        m = CONTRARY.search(a["abstract"])
        if m:
            ref["cue"] = m.group(0)
            ref["snippet"] = snippet(a["abstract"], m)
            contrary.append(ref)
        else:
            support.append(ref)
    return {"support": support[:6], "contrary": contrary[:5]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--refresh", action="store_true", help="re-query even if already cached")
    ap.add_argument("--offline", action="store_true", help="don't hit the network; just report cache")
    args = ap.parse_args()

    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    todo = [r for r in rows if (not args.only or r["reaction_id"] in args.only)]
    done = sup = con = 0
    for i, r in enumerate(todo, 1):
        rid = r["reaction_id"]
        if rid in data and not args.refresh:
            continue
        if args.offline:
            continue
        try:
            data[rid] = dossier(r)
        except Exception as exc:  # noqa: BLE001
            print(f"  [err] {rid}: {exc!r}")
            continue
        done += 1
        sup += len(data[rid]["support"])
        con += len(data[rid]["contrary"])
        if done % 10 == 0:
            OUT.write_text(json.dumps(data, ensure_ascii=False, indent=0))
            print(f"  …{i}/{len(todo)} ({rid}) support={sup} contrary={con}")
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=0))
    tot = {k: data[k] for k in data}
    S = sum(len(v["support"]) for v in tot.values())
    C = sum(len(v["contrary"]) for v in tot.values())
    print(f"[dossier] {len(data)} reactions -> {OUT}  (support refs: {S}, contrary refs: {C}; "
          f"this run: {done} queried)")


if __name__ == "__main__":
    main()
