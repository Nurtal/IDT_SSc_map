#!/usr/bin/env python3
"""Assemble per-interaction reading packets so the abstracts can actually be READ for adjudication.

The literature dossier (curation/evidence_dossier.json) lists candidate support/contrary PMIDs but
not their abstract text. This script fetches every referenced abstract (the dossier refs + each
reaction's own + secondary PMIDs) once, caches them, and writes one human-/model-readable packet per
reaction: the curated claim + deciding quote, then each support and each possibly-contrary reference
with its abstract. These packets are what a reviewer (or the assistant, acting as one) reads before
calling validate / reject / uncertain.

Outputs:
    curation/_dossier_abstracts.json     {pmid: {title, year, journal, abstract}}  (cache)
    curation/reading_packets.json        {reaction_id: {claim, quote, support:[...], contrary:[...]}}

Run: python3 scripts/build_reading_packets.py            # fetch missing abstracts, rebuild packets
     python3 scripts/build_reading_packets.py --offline  # only use cached abstracts
Network: NCBI E-utils efetch. Honours NCBI_API_KEY.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from mine_pdf_quotes import clean

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
DOSSIER = ROOT / "curation/evidence_dossier.json"
ABS = ROOT / "curation/_dossier_abstracts.json"
OUT = ROOT / "curation/reading_packets.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "SSc-MIM-packets/0.1 (mailto:nathan.foulquier.pro@gmail.com)"
SLEEP = 0.12 if os.environ.get("NCBI_API_KEY") else 0.34


def efetch(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    params = {"db": "pubmed", "id": ",".join(ids), "rettype": "abstract", "retmode": "xml"}
    if os.environ.get("NCBI_API_KEY"):
        params["api_key"] = os.environ["NCBI_API_KEY"]
    url = f"{EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(params)
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=45).read()
    root = ET.fromstring(raw)
    out = {}
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        te = art.find(".//ArticleTitle")
        title = "".join(te.itertext()) if te is not None else ""
        year = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
        jr = art.findtext(".//Journal/ISOAbbreviation") or ""
        ab = clean(" ".join("".join(a.itertext()) for a in art.iter("AbstractText")))
        out[pmid] = {"title": clean(title), "year": year, "journal": jr, "abstract": ab}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    dossier = json.loads(DOSSIER.read_text()) if DOSSIER.exists() else {}
    rows = {r["reaction_id"]: r for r in csv.DictReader(SSC.open(), delimiter="\t")}

    wanted: set[str] = set()
    for rid, e in dossier.items():
        for it in e.get("support", []) + e.get("contrary", []):
            if it.get("pmid"):
                wanted.add(it["pmid"])
    for r in rows.values():
        for p in [r.get("pmid", "")] + (r.get("secondary_pmids", "") or "").split(";"):
            p = (p or "").strip()
            if p and p not in ("", "-"):
                wanted.add(p)

    cache = json.loads(ABS.read_text()) if ABS.exists() else {}
    missing = sorted(wanted - set(cache))
    if missing and not args.offline:
        print(f"[packets] fetching {len(missing)} abstracts…")
        for i in range(0, len(missing), 150):
            batch = missing[i:i + 150]
            try:
                cache.update(efetch(batch))
            except Exception as exc:  # noqa: BLE001
                print(f"  [efetch] batch {i} failed: {exc!r}")
            ABS.write_text(json.dumps(cache, ensure_ascii=False))
            time.sleep(SLEEP)

    def ref(it: dict) -> dict:
        a = cache.get(it["pmid"], {})
        d = {"pmid": it["pmid"], "title": a.get("title", it.get("title", "")),
             "year": a.get("year", it.get("year", "")), "journal": a.get("journal", ""),
             "abstract": a.get("abstract", "")}
        if it.get("cue"):
            d["cue"] = it["cue"]
        return d

    packets = {}
    for rid, r in rows.items():
        e = dossier.get(rid, {})
        own = (r.get("pmid", "") or "").strip()
        packets[rid] = {
            "claim": f'{r["reactants"]} --[{r["type"]}]--> {r["products"]}'
                     + (f'  (mods: {r["modifiers"]})' if r.get("modifiers") else ""),
            "mechanism": r.get("mechanism", ""),
            "ssc_relevance": r.get("ssc_relevance", ""),
            "curation_status": r.get("curation_status", ""),
            "evidence_code": r.get("evidence_code", ""),
            "own_pmid": own,
            "own_abstract": cache.get(own, {}).get("abstract", "") if own and own not in ("", "-") else "",
            "support": [ref(it) for it in e.get("support", [])],
            "contrary": [ref(it) for it in e.get("contrary", [])],
        }
    OUT.write_text(json.dumps(packets, ensure_ascii=False, indent=1))
    refs = sum(len(p["support"]) + len(p["contrary"]) for p in packets.values())
    print(f"[packets] {len(packets)} reactions, {len(cache)} abstracts cached, {refs} refs -> {OUT}")


if __name__ == "__main__":
    main()
