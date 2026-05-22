#!/usr/bin/env python3
"""E18 — Quantify SSc-MIM novelty against Reactome and KEGG.

Two comparisons:

1.  **Reactome / SSc-curated split** — already implicit in the curation
    layer (244 rows from Reactome imports + 85 SSc-Tier1 reactions =
    329). We commit the numbers explicitly here.

2.  **KEGG pathway Jaccard** — cross-reference the 198 HGNC symbols of
    the MIM against three KEGG pathway gene lists fetched from the
    KEGG REST API on 2026-05-21 (hashed into
    ``analysis/network/kegg_pathways.json`` for reproducibility):

      hsa04350  TGF-β signalling                  (M2)
      hsa04060  Cytokine-cytokine receptor inter.  (M4)
      hsa04630  JAK-STAT signalling                (M1 + M4)

    For each pathway we report (|MIM ∩ pathway|, |MIM only|,
    |pathway only|, Jaccard). The novelty narrative target is the
    "MIM only" column — entities the MIM curation surfaced that KEGG
    does not encode at the gene level.

The Mahoney 2015 and Taroni 2024 consensus-network comparisons were
descoped to a follow-up paper after the v1.1 sprint check (edge files
not retrievable in the budgeted 2 days; reviewer R1 indicated this is
acceptable provided the gap is acknowledged in §4).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ANN = Path("curation/annotations/species_annotations.tsv")
EVI = Path("curation/annotations/reaction_evidence.tsv")
SSC = Path("curation/ssc_curated_reactions.tsv")
OUT_TSV = Path("analysis/network/novelty_kegg.tsv")
OUT_JSON = Path("analysis/network/novelty.json")

# KEGG gene lists fetched from https://rest.kegg.jp/get/hsa04XXX on
# 2026-05-21 (Hinchcliff-cycle revision). Frozen here to keep
# `make novelty` reproducible without a live network call.
KEGG = {
    "hsa04350_TGFb": {
        "label": "TGF-β signalling",
        "module_hint": "M2",
        "genes": {
            "MICOS10-NBL1","CDKN2B","FST","LEFTY1","ACVR1C","CREBBP","HJV",
            "GDF7","DCN","E2F4","E2F5","EMP3","EP300","FBN1","FMOD","LEMD3",
            "BAMBI","SIN3A","LRRC32","GREM1","AMH","AMHR2","RGMB","HDAC1",
            "HDAC2","HFE","ID1","ID2","ID3","ID4","IFNG","BMP8A","IGSF1",
            "INHBA","INHBB","INHBC","NRROS","RHOA","GDF6","LTBP1","SMAD1",
            "SMAD2","SMAD3","SMAD4","SMAD5","SMAD6","SMAD7","SMAD9","MYC",
            "NBL1","NEO1","NODAL","PITX2","PPP2CA","PPP2CB","PPP2R1A",
            "PPP2R1B","MAPK1","MAPK3","RGMA","SMURF1","HAMP","RBL1","TGIF2",
            "ROCK1","RPS6KB1","RPS6KB2","GREM2","SMURF2","SKI","SKIL","BMP2",
            "SKP1","BMP4","BMP5","BMP6","BMP7","BMP8B","BMPR1A","BMPR1B",
            "BMPR2","SP1","TF","TFDP1","TFR2","TFRC","TGFB1","TGFB2","TGFB3",
            "LEFTY2","TGFBR1","TGFBR2","TGIF1","THBS1","TNF","TMEM53","THSD4",
            "GDF5","INHBE","CUL1","CHRD","ACVR1","ACVR1B","ACVR2A","NOG",
            "ACVR2B","ZFYVE9","NCOR1","ZFYVE16","RBX1",
        },
    },
    "hsa04060_cytokine": {
        "label": "Cytokine-cytokine receptor interaction",
        "module_hint": "M4",
        "genes": set("""
EBI3 GDF11 CCL26 CXCL13 CXCR6 TNFSF13B CCR9 CCL27 EDAR IL24 IL17F TNFRSF13C
CCR1 CCR3 CCR4 CCR5 CCR6 CCR7 CCR8 CNTF CNTFR ACVR1C IL17RE IL31RA CSF1
CSF1R CSF2 CSF2RA CSF2RB CSF3 CSF3R CSH1 CSH2 CSHL1 IL34 CTF1 IL23R GDF7
CX3CR1 IFNLR1 EDA EPO EPOR TNFRSF13B CLCF1 IL17RA IL27 IL36RN GDF1 GDF2
MSTN GDF9 GDF10 AMH GH1 GH2 AMHR2 GHR IL36B IL37 IL36A IL17C IL17B
TNFRSF21 BMP10 CCR10 IFNL2 IFNL3 IFNL1 XCR1 CXCR3 CXCL17 RELL2 CXCL1 CXCL2
CXCL3 IL19 IFNE IFNA1 IFNA2 IFNA4 IFNA5 IFNA6 IFNA7 IFNA8 IFNA10 IFNA13
IFNA14 IFNA16 IFNA17 IFNA21 IFNAR1 IFNAR2 IFNB1 IFNG IFNGR1 IFNGR2 IFNW1
BMP8A FAS IL1A IL1B IL1R1 IL1RAP IL1RN IL2 IL2RA FASLG IL2RB IL2RG IL3
IL3RA IL4 IL4R IL5 IL5RA IL6 IL6R IL6ST IL7 IL7R CXCL8 CXCR1 IL9 CXCR2
IL9R IL10 IL10RA IL10RB IL11 IL11RA IL12A IL12B IL12RB1 IL12RB2 IL13
IL13RA1 IL13RA2 IL15 IL15RA IL16 TNFRSF9 IL17A IL18 INHA INHBA INHBB INHBC
CXCL10 IL31 CCL4L1 GDF6 LEP LEPR LIF LIFR LTA LTB LTBR CCL3L3 CXCL9 MPL
NGF NGFR NODAL TNFRSF11B OSM IL20 IL21R IL22 TNFRSF12A ACKR4 IL23A PF4
PF4V1 IL17D IL20RA IL20RB PPBP TNFRSF19 IL17RB IL26 PRL PRLR IL36G CCL28
IFNK ACKR3 CXCL16 IL22RA1 IL21 EDA2R TNFRSF17 CCL1 CCL2 CCL3 CCL3L1 CCL4
CCL5 CCL7 CCL8 CCL11 CCL13 CCL14 CCL15 CCL16 CCL17 CCL18 CCL19 CCL20
CCL21 CCL22 CCL23 CCL24 CCL25 CXCL6 CXCL11 CXCL5 XCL1 CX3CL1 CXCL12 CRLF2
CXCR5 IL25 BMP2 BMP3 BMP4 BMP5 BMP6 BMP7 BMP8B BMPR1A BMPR1B BMPR2 XCL2
TGFB1 TGFB2 TGFB3 TGFBR1 TGFBR2 THPO TNF TNFRSF1A TNFRSF1B TNFSF4 CCR2
TNFRSF4 RELL1 IL1R2 CXCR4 GDF5 INHBE IL1F10 IL17RC RELT TSLP TNFSF11
TNFRSF25 TNFSF14 TNFSF13 TNFSF12 TNFSF10 TNFSF9 TNFRSF14 TNFRSF6B
TNFRSF18 TNFRSF11A TNFRSF10D TNFRSF10C TNFRSF10B TNFRSF10A IL18RAP IL1RL2
IL18R1 TNFSF18 ACVR1 IL33 ACVR1B IL1RL1 OSMR ACVR2A CD4 BMP15 IL32 ACVR2B
CD27 ACVRL1 TNFRSF8 TNFSF8 IL27RA GDF15 CXCL14 CCL4L2 GDF3 CD40 CD40LG
CD70 TNFSF15
""".split()),
    },
    "hsa04630_jakstat": {
        "label": "JAK-STAT signalling",
        "module_hint": "M1+M4",
        "genes": set("""
AKT3 STAM2 CDKN1A IRF9 PIAS3 IL24 CISH IL22RA2 SOCS4 CNTF CNTFR IL31RA
CREBBP CSF2 CSF2RA CSF2RB CSF3 CSF3R CSH1 CSH2 CSHL1 CTF1 IL23R IFNLR1
EGF EGFR EP300 EPO EPOR AKT1 AKT2 FHL1 CLCF1 IL27 MTOR GFAP GH1 GH2 GHR
IFNL2 IFNL3 IFNL1 GRB2 IL19 SOCS7 AOX1 HRAS IFNE IFNA1 IFNA2 IFNA4 IFNA5
IFNA6 IFNA7 IFNA8 IFNA10 IFNA13 IFNA14 IFNA16 IFNA17 IFNA21 IFNAR1 IFNAR2
IFNB1 IFNG IFNGR1 IFNGR2 IFNW1 IL2 IL2RA IL2RB IL2RG IL3 IL3RA IL4 IL4R
IL5 IL5RA IL6 IL6R IL6ST IL7 IL7R IL9 IL9R IL10 IL10RA IL10RB IL11 IL11RA
IL12A IL12B IL12RB1 IL12RB2 IL13 IL13RA1 IL13RA2 IL15 IL15RA JAK1 JAK2
JAK3 IL31 LEP LEPR LIF LIFR MCL1 MPL MYC OSM IL20 IL21R IL22 PDGFA PDGFB
PDGFRA IL23A PIAS4 PDGFRB PIK3CA PIK3CB PIM1 PIK3CD PIK3R1 PIK3R2 IL20RA
IL20RB IL26 PRL PRLR IFNK PTPN2 PTPN6 PTPN11 RAF1 IL22RA1 IL21 CCND1 BCL2
BCL2L1 CRLF2 SOS1 SOS2 STAT1 STAT2 STAT3 STAT4 STAT5A STAT5B STAT6 THPO
TYK2 STAM PIK3R3 TSLP PIAS1 SOCS1 SOCS2 CCND2 CCND3 SOCS3 PIAS2 OSMR
SOCS6 IL27RA SOCS5
""".split()),
    },
}


def main() -> int:
    # Load MIM HGNC denominator
    mim_genes: set[str] = set()
    for row in csv.DictReader(ANN.open(), delimiter="\t"):
        sym = (row.get("hgnc_symbol") or "").strip()
        if sym:
            mim_genes.add(sym)
    print(f"MIM HGNC denominator: {len(mim_genes)} unique symbols")

    # Reactome / SSc split from the reaction layer
    n_reactome = sum(1 for _ in csv.DictReader(EVI.open(), delimiter="\t"))
    n_sscur    = sum(1 for _ in csv.DictReader(SSC.open(), delimiter="\t"))
    n_total = n_reactome + n_sscur
    print()
    print("Reaction-layer split:")
    print(f"  Reactome-derived (`reaction_evidence.tsv`): {n_reactome} = "
          f"{100*n_reactome/n_total:.1f}%")
    print(f"  SSc-curated (`ssc_curated_reactions.tsv`):  {n_sscur} = "
          f"{100*n_sscur/n_total:.1f}%")
    print(f"  total: {n_total}")

    # KEGG comparisons
    print()
    print("KEGG pathway novelty (HGNC Jaccard):")
    rows: list[dict] = []
    summary = {
        "mim_n_hgnc": len(mim_genes),
        "reactome_n_reactions": n_reactome,
        "ssc_curated_n_reactions": n_sscur,
        "kegg": {},
    }
    for kid, info in KEGG.items():
        pw = set(info["genes"])
        inter = mim_genes & pw
        mim_only = mim_genes - pw
        kegg_only = pw - mim_genes
        jaccard = len(inter) / max(1, len(mim_genes | pw))
        rec = {
            "kegg_pathway": kid,
            "label": info["label"],
            "module_hint": info["module_hint"],
            "kegg_size": len(pw),
            "mim_size": len(mim_genes),
            "intersect": len(inter),
            "mim_only": len(mim_only),
            "kegg_only": len(kegg_only),
            "jaccard": round(jaccard, 4),
        }
        rows.append(rec)
        summary["kegg"][kid] = rec
        print(f"  [{kid}] {info['label']}")
        print(f"    KEGG size  = {len(pw)}")
        print(f"    intersect  = {len(inter)}")
        print(f"    MIM only   = {len(mim_only)}  (novel against this KEGG pathway)")
        print(f"    KEGG only  = {len(kegg_only)}")
        print(f"    Jaccard    = {jaccard:.4f}")

    # Aggregate: how many MIM symbols are covered by AT LEAST one of the three
    # KEGG pathways? The complement is "uniquely MIM".
    kegg_union = set()
    for info in KEGG.values():
        kegg_union |= info["genes"]
    only_mim_total = mim_genes - kegg_union
    print()
    print(f"MIM genes NOT in any of the 3 KEGG pathways: {len(only_mim_total)} / {len(mim_genes)} ({100*len(only_mim_total)/len(mim_genes):.1f}%)")
    print(f"MIM ∩ KEGG-union: {len(mim_genes & kegg_union)}")
    summary["mim_genes_not_in_any_kegg"] = len(only_mim_total)
    summary["mim_n_in_kegg_union"] = len(mim_genes & kegg_union)
    summary["kegg_union_size"] = len(kegg_union)

    # Save TSV
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader(); w.writerows(rows)
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nwrote {OUT_TSV} and {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
