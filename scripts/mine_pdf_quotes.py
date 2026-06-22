#!/usr/bin/env python3
"""Extract the verbatim supporting sentence for each SSc interaction from its source article.

For every curated reaction with a PMID this picks the single sentence that best supports the
interaction — the one mentioning the most of its participants (gene symbols + the protein/molecule
synonyms used in papers), preferably with a relationship verb (binds / induces / inhibits …). The
text is taken from, in order of preference:
  1. a local full-text PDF  (``/home/drfox/data/IDT_SSc_map/article/<pmid>.pdf``)  -> source "pdf"
  2. the PubMed Central open-access full text, fetched via NCBI E-utils                -> source "pmc"
  3. the PubMed abstract, fetched via NCBI E-utils                                     -> source "abstract"

The pick is a heuristic *proposal*: it is stored with a ``quote_status`` (``verbatim
(PDF-extracted)`` / ``verbatim (PMC full-text)`` / ``verbatim (abstract)``) so the reviewer can
confirm or correct it. It only ever *fills* a quote — it never silently overrides a human-curated
verbatim sentence (that arbitration lives in ``build_interaction_db.py``).

Outputs:
    curation/pdf_quotes.tsv   reaction_id, pmid, source, pdf_page, match_score,
                              supporting_quote, hl_terms, alt_page, alt_quote
Cache (outside the repo, regenerable):
    <article_dir>/../article_text/<pmid>.json            cleaned per-page PDF text
    <article_dir>/../article_text/<pmid>.{pmc,abstract}.json   fetched online text

Run: python3 scripts/mine_pdf_quotes.py            # uses cache, fetches missing online text
     python3 scripts/mine_pdf_quotes.py --offline  # cache/PDF only, no network
Network: NCBI E-utils (efetch/elink). Honours NCBI_API_KEY for a higher rate limit.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
SSC = ROOT / "curation/ssc_curated_reactions.tsv"
ART = Path("/home/drfox/data/IDT_SSc_map/article")
CACHE = ART.parent / "article_text"
OUT = ROOT / "curation/pdf_quotes.tsv"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "SSc-MIM-quotes/0.1 (mailto:nathan.foulquier.pro@gmail.com)"
SLEEP = 0.12 if os.environ.get("NCBI_API_KEY") else 0.34

# tokens that look gene-like but are not, so they don't become anchors
STOP = {"THE", "AND", "FOR", "WITH", "FROM", "THAT", "THIS", "WERE", "WAS", "ARE", "HAS",
        "SSC", "DNA", "RNA", "CELL", "CELLS", "FIG", "ECO", "PMID", "ELISA", "PCR", "MRNA",
        "WESTERN", "BLOT", "VITRO", "VIVO", "HUMAN", "MOUSE", "PATIENTS", "CONTROL", "ROLE"}
VERB = re.compile(r"\b(induc|activat|inhibit|bind|phosphoryl|promot|suppress|increas|decreas|"
                  r"express|secret|stimulat|regulat|mediat|driv|trigger|releas|recruit|degrad|"
                  r"up-?regulat|down-?regulat|signal|produc|sens|enhanc|block|repress)", re.I)
CITE = re.compile(r"\bet al\b|doi:|\bFig(?:ure|\.)|\bTable\b|©|http|Received:|Revised:|"
                  r"Accepted:|Published online|Springer|Elsevier|Correspondence|\bemail\b", re.I)
DATEY = re.compile(r"\b\d{1,2}\s+\w+\s+20\d\d\b|\b20\d\d\s*[/)]")
# reference-list entries (author initials, year;volume, journal abbreviations) are not assertions
REFLIKE = re.compile(r"\b\d{4};\s?\d+|\b\d{4}:\s?\d+\b|\b(?:Immunol|Biochem|Biol|Oncol|Rheum|"
                     r"Dermatol|Physiol|Pathol|Cardiol|Pharmacol|Hematol|Proc Natl|Clin Invest|"
                     r"Biol Chem|Nat Rev|Nat Med|Nat Genet|Sci Transl|Circ Res|EMBO|FASEB|PLoS|"
                     r"J Exp Med|Cell Biol|Mol Cell)\b\.?", re.I)
PANEL = re.compile(r"^\(?[A-Za-z]\)|^\(?[ivx]+\)", re.I)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])")


def clean(t: str) -> str:
    t = unicodedata.normalize("NFKC", t).replace("­", "")
    t = re.sub(r"-\n([a-z])", r"\1", t)          # de-hyphenate across line breaks
    t = re.sub(r"\s*\n\s*", " ", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def pages_text(pmid: str) -> list[str]:
    """Cleaned text per page of the local PDF, cached as JSON next to the PDFs."""
    cf = CACHE / f"{pmid}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    doc = fitz.open(ART / f"{pmid}.pdf")
    pages = [clean(p.get_text("text")) for p in doc]
    doc.close()
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(pages, ensure_ascii=False))
    return pages


def _eutils(endpoint: str, **params) -> bytes:
    params.setdefault("retmode", "xml")
    if os.environ.get("NCBI_API_KEY"):
        params["api_key"] = os.environ["NCBI_API_KEY"]
    url = f"{EUTILS}/{endpoint}.fcgi?" + urllib.parse.urlencode(params)
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def fetch_abstract(pmid: str) -> list[str]:
    """Title + abstract paragraphs from PubMed (one cleaned block each)."""
    root = ET.fromstring(_eutils("efetch", db="pubmed", id=pmid, rettype="abstract"))
    blocks = []
    for el in root.iter("ArticleTitle"):
        blocks.append("".join(el.itertext()))
    for el in root.iter("AbstractText"):
        label = el.get("Label")
        blocks.append((f"{label}: " if label else "") + "".join(el.itertext()))
    return [clean(b) for b in blocks if b and b.strip()]


def fetch_pmc(pmid: str) -> list[str]:
    """Open-access PMC full-text paragraphs (empty if the article is not in PMC OA)."""
    raw = _eutils("elink", dbfrom="pubmed", db="pmc", id=pmid, retmode="json").decode("utf-8", "replace")
    link = json.loads(raw, strict=False)  # NCBI sometimes emits unescaped control chars
    pmcid = None
    for ls in link.get("linksets", []):
        for db in ls.get("linksetdbs", []):
            if db.get("dbto") == "pmc" and db.get("links"):
                pmcid = db["links"][0]
    if not pmcid:
        return []
    root = ET.fromstring(_eutils("efetch", db="pmc", id=pmcid))
    paras = []
    for el in root.iter("p"):
        t = "".join(el.itertext())
        if t and len(t) > 40:
            paras.append(clean(t))
    return paras


def get_sources(pmid: str, offline: bool) -> list[tuple[str, list[str]]]:
    """Available text sources for a PMID, in order of preference: local PDF, else PMC, else abstract.
    The caller tries them in turn so a PMC full text that yields no match can fall back to the abstract."""
    if (ART / f"{pmid}.pdf").exists():
        return [("pdf", pages_text(pmid))]
    srcs = []
    for src, fetch in (("pmc", fetch_pmc), ("abstract", fetch_abstract)):
        cf = CACHE / f"{pmid}.{src}.json"
        if cf.exists():
            pages = json.loads(cf.read_text())
        elif offline:
            continue
        else:
            try:
                pages = fetch(pmid)
            except Exception as exc:  # noqa: BLE001
                print(f"  [net] {pmid} {src}: {exc!r}")
                pages = []
            CACHE.mkdir(parents=True, exist_ok=True)
            cf.write_text(json.dumps(pages, ensure_ascii=False))
            time.sleep(SLEEP)
        if pages:
            srcs.append((src, pages))
    return srcs


def symbols(field: str) -> list[str]:
    out = []
    for chunk in re.split(r";", field or ""):
        base = chunk.split("__", 1)[0].strip()
        for tok in re.split(r"[_:/]", base):
            tok = tok.strip()
            if len(tok) >= 2 and tok.upper() not in STOP:
                out.append(tok)
    return out


def genelike(text: str) -> list[str]:
    """Gene/protein-looking tokens from free text (captures synonyms the curator wrote)."""
    out = []
    for tok in re.findall(r"[A-Za-zαβγκ][A-Za-z0-9αβγκ\-]{2,}", text or ""):
        if tok.upper() in STOP:
            continue
        if any(c.isdigit() for c in tok) or tok[0].isupper() or tok != tok.lower():
            out.append(tok)
    return out


# HGNC symbol -> regex alternatives for the common name(s) used in the articles. Articles rarely
# spell the official symbol; without this, exact-symbol matching misses (TGFB1 vs "TGF-β" etc.).
SYN: dict[str, list[str]] = {
    "TGFB1": [r"TGF-?\s?(?:β|beta)\s?1?", r"TGFβ1?", r"transforming growth factor[- ]?\s?(?:β|beta)"],
    "TGFB2": [r"TGF-?\s?(?:β|beta)\s?2"],
    "LGALS3": [r"galectin[- ]?3", r"Gal-?3"],
    "EDN1": [r"endothelin[- ]?1", r"ET-?1", r"\bET1\b"],
    "EDNRA": [r"endothelin (?:type )?A receptor", r"ET-?A receptor", r"ETA\b", r"ETAR"],
    "ARNT": [r"HIF-?\s?1\s?(?:β|beta)", r"HIF1B"],
    "HIF1A": [r"HIF-?\s?1\s?(?:α|alpha)", r"HIF1α"],
    "FLI1": [r"Fli-?1"],
    "COL1A1": [r"type[- ]?I collagen", r"collagen (?:type )?I\b", r"(?:α|alpha)1\(I\) collagen", r"COL1\b"],
    "COL1A2": [r"(?:α|alpha)2\(I\) collagen", r"type[- ]?I collagen"],
    "COL3A1": [r"type[- ]?III collagen", r"collagen (?:type )?III"],
    "JAK1": [r"Janus kinase 1", r"JAK-?1"],
    "SOCS1": [r"SOCS-?1", r"suppressor of cytokine signal\w* 1"],
    "PTPN2": [r"TC-?PTP", r"TCPTP"],
    "SNAI1": [r"Snail-?1?", r"SNAI1"],
    "SNAI2": [r"Slug", r"Snail-?2"],
    "CDH5": [r"VE-?cadherin", r"CD144", r"cadherin-?5"],
    "CDH2": [r"N-?cadherin"],
    "FSP1": [r"S100A4", r"FSP-?1", r"fibroblast[- ]specific protein"],
    "FAP": [r"fibroblast activation protein"],
    "ANGPT1": [r"angiopoietin-?1", r"Ang-?1", r"\bANG1\b"],
    "ANGPT2": [r"angiopoietin-?2", r"Ang-?2", r"\bANG2\b"],
    "TEK": [r"Tie-?2", r"\bTIE2\b"],
    "MMP12": [r"MMP-?12", r"macrophage (?:metallo)?elastase"],
    "PLAUR": [r"uPAR", r"CD87"],
    "ITGAV": [r"integrin\s?(?:α|alpha)\s?v", r"(?:α|alpha)v(?:β|beta)?"],
    "STAT6": [r"STAT-?6"],
    "MS4A1": [r"CD20"],
    "TNFSF13B": [r"BAFF", r"BLyS"],
    "MB21D1": [r"cGAS"],
    "TMEM173": [r"STING"],
    "IFNB1": [r"IFN-?\s?(?:β|beta)", r"interferon[- ]?(?:β|beta)", r"type\s?[I1]\s?(?:IFN|interferons?)",
              r"type\s?[I1]\s?interferon"],
    "IFNA1": [r"IFN-?\s?(?:α|alpha)", r"interferon[- ]?(?:α|alpha)", r"type\s?[I1]\s?(?:IFN|interferons?)"],
    "IFNG": [r"IFN-?\s?(?:γ|gamma)", r"interferon[- ]?(?:γ|gamma)"],
    "CCN2": [r"CTGF", r"connective tissue growth factor"],
}
# generic words that should not become standalone matching concepts
GENERIC = {"complex", "active", "repressed", "inhibited", "dimer", "phenotype", "vascular",
           "remodelling", "remodeling", "activation", "committed", "lineage", "bound", "stiffened",
           "myofibroblast", "signalling", "signaling"}


def concept_res(row: dict) -> tuple[list, list]:
    """Return (concepts, primaries). Each concept = (regex, surface_forms) matching one participant
    (its symbol + known synonyms); primaries are the reactant/product/modifier concepts."""
    def mk(sym: str):
        forms = [re.escape(sym)] + SYN.get(sym.upper(), [])
        rx = re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(forms) + r")(?![A-Za-z0-9])", re.I)
        return (rx, sym)

    prim_syms = [s for s in symbols(row["reactants"]) + symbols(row["products"])
                 + symbols(row.get("modifiers", "")) if s.lower() not in GENERIC]
    concepts, primaries, seen = [], [], set()
    for s in prim_syms:
        if s.lower() in seen:
            continue
        seen.add(s.lower())
        c = mk(s)
        concepts.append(c)
        primaries.append(c)
    for t in genelike(row.get("mechanism", "")) + genelike(row.get("ssc_relevance", "")):
        if t.lower() in seen or t.lower() in GENERIC:
            continue
        seen.add(t.lower())
        concepts.append(mk(t))
    return concepts, primaries


def forms_in(sent: str, concepts: list) -> list[str]:
    """Distinct surface strings (for highlighting) that the concepts match in the sentence."""
    found: list[str] = []
    for rx, _ in concepts:
        for m in rx.finditer(sent):
            found.append(m.group(0))
    return list(dict.fromkeys(found))


def best_quote(row: dict, pages: list[str]):
    """-> (quote, page, score, hl_terms, alt_quote, alt_page); empties if no confident match."""
    concepts, primaries = concept_res(row)
    if not concepts:
        return ("", 0, 0.0, [], "", 0)
    # single-participant reactions (e.g. STAT6 -> STAT6 dimer) can only ever match one concept:
    # accept 1 primary concept *plus a relationship verb* there; else require 2 concepts.
    need = 2 if len(primaries) >= 2 else 1
    ranked = []
    for pno, txt in enumerate(pages, 1):
        for sent in SENT.split(txt):
            sent = sent.strip(" •-–\t")
            if not (40 <= len(sent) <= 360):
                continue
            hitp = [s for rx, s in primaries if rx.search(sent)]
            hitc = sum(1 for rx, _ in concepts if rx.search(sent))
            if not hitp or hitc < need:
                continue
            if need == 1 and not VERB.search(sent):
                continue
            score = float(hitc)
            tgt = any(rx.search(sent) for rx, s in primaries if s in symbols(row["products"]))
            if tgt and len(hitp) >= 2:
                score += 1.0
            if VERB.search(sent):
                score += 0.7
            if CITE.search(sent):
                score -= 1.5
            if DATEY.search(sent):
                score -= 1.5
            if REFLIKE.search(sent):
                score -= 2.0
            if PANEL.match(sent):
                score -= 0.8
            score -= len(sent) / 2000.0
            ranked.append((score, pno, sent))
    if not ranked:
        return ("", 0, 0.0, [], "", 0)
    ranked.sort(key=lambda x: -x[0])
    s0, p0, q0 = ranked[0]
    alt_q, alt_p = "", 0
    for s, p, q in ranked[1:]:
        if q != q0:
            alt_q, alt_p = q, p
            break
    return (q0, p0, s0, forms_in(q0, concepts), alt_q, alt_p)


def has_pmid(v: str) -> bool:
    v = (v or "").strip()
    return bool(v) and v not in ("", "-") and bool(re.search(r"\d", v))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", help="restrict to these reaction_ids")
    ap.add_argument("--show", action="store_true", help="print each extracted quote")
    ap.add_argument("--offline", action="store_true", help="use local PDFs + cache only (no NCBI fetch)")
    args = ap.parse_args()

    rows = list(csv.DictReader(SSC.open(), delimiter="\t"))
    out = {"pdf": 0, "pmc": 0, "abstract": 0}
    miss = nopmid = 0
    records = []
    for r in rows:
        if args.only and r["reaction_id"] not in args.only:
            continue
        pmid = (r.get("pmid") or "").strip()
        if not has_pmid(pmid):
            nopmid += 1
            continue
        chosen = None
        for source, pages in get_sources(pmid, args.offline):
            res = best_quote(r, pages)
            if res[0]:
                chosen = (source, res)
                break
        if not chosen:
            miss += 1
            continue
        source, (quote, page, score, hl, alt_q, alt_p) = chosen
        out[source] += 1
        records.append({"reaction_id": r["reaction_id"], "pmid": pmid, "source": source,
                        "pdf_page": page if source == "pdf" else "",
                        "match_score": f"{score:.2f}", "supporting_quote": quote,
                        "hl_terms": "|".join(hl),
                        "alt_page": (alt_p if source == "pdf" else "") or "", "alt_quote": alt_q})
        if args.show:
            loc = f"p.{page}" if source == "pdf" else source
            print(f"\n[{r['reaction_id']}] {r['reactants']}->{r['products']}  ({source} {loc}, s={score:.2f})\n"
                  f"  “{quote}”\n  hl: {hl}" + (f"\n  alt: “{alt_q}”" if alt_q else ""))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["reaction_id", "pmid", "source", "pdf_page", "match_score",
                                          "supporting_quote", "hl_terms", "alt_page", "alt_quote"],
                           delimiter="\t")
        w.writeheader()
        w.writerows(records)
    total = sum(out.values())
    print(f"[quotes] {total} sentences -> {OUT}  "
          f"(pdf={out['pdf']} pmc={out['pmc']} abstract={out['abstract']}; "
          f"{miss} no confident match, {nopmid} reactions without a PMID)")


if __name__ == "__main__":
    main()
