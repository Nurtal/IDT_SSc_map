#!/usr/bin/env python3
"""Evidence stratification + TODO reaction-type classification (H1).

Part of the v1.1 hardening sprint (see ROADMAP "v1.1 hardening sprint").

Two jobs, both deterministic and offline:

1. **Classify the `type=TODO` rows** of
   ``curation/annotations/reaction_evidence.tsv`` (Reactome-derived backbone)
   by keyword rules on the human-readable ``mechanism`` field, mapping each onto
   the controlled vocabulary already used by the SSc-curated layer. The original
   curated *content* of the map is untouched; only the annotation-completeness
   field ``type`` is filled, and the inference is traced transparently in the
   ``notes`` column (suffix ``[type auto-inferred: evidence_audit.py]``) so the
   change is never silent and is fully reversible.

2. **Stratify the whole evidence base by provenance** — Reactome-backbone
   (``reaction_evidence.tsv``) vs SSc-Tier-1 (``ssc_curated_reactions.tsv``) —
   and cross-tabulate ECO evidence code × PMID presence within each layer. This
   is the quantified answer to the "headline numbers are stronger than the
   SSc-specific curation" critique: it makes the split explicit.

Outputs:
    analysis/curation/evidence_stratification.tsv   provenance × ECO × PMID matrix
    analysis/curation/evidence_stratification.json   machine-readable summary
    analysis/curation/evidence_stratification.md      human-readable report
    curation/annotations/reaction_evidence.tsv        updated in place (type filled)

Run:
    python3 scripts/evidence_audit.py
or  make evidence-audit
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REACTION_EVIDENCE = ROOT / "curation/annotations/reaction_evidence.tsv"
SSC_CURATED = ROOT / "curation/ssc_curated_reactions.tsv"
OUT_DIR = ROOT / "analysis/curation"

INFERRED_TAG = "[type auto-inferred: evidence_audit.py]"

# Ordered keyword rules: first match wins. Patterns are matched case-insensitively
# against the `mechanism` free-text. Mapped onto the controlled vocabulary already
# present in the SSc-curated layer (catalysis, state_change, phosphorylation,
# transcription, binding, activation, contributes, degradation) plus transport /
# inhibition / dissociation which the Reactome backbone genuinely needs.
RULES: list[tuple[str, str]] = [
    (r"\bdephosphorylat", "state_change"),        # before 'phosphorylat'
    (r"\bautophosphorylat|\bphosphorylat", "phosphorylation"),
    (r"\bubiquitin|\bproteasom|\bdegradation\b|\bdegrad", "degradation"),
    (r"\bcleav|\bclevage|\bproteolyt|\bprocessing of|\bfurin", "catalysis"),
    (r"\bexpression of|\btranscription|\binduces .*transcription", "transcription"),
    (r"\btranslocat|\bimport\b|\bexport|\bshuttl|\btraffick|\btraffic", "transport"),
    (r"\brelease of|\bdissociat", "dissociation"),
    (r"\binhibit|\bprevents\b|\bblocks\b|\bnegative regulat", "inhibition"),
    (r"\bactivation\b|\bactivates\b|\bactive receptor\b", "activation"),
    (r"\bbinds|\bbinding|\brecruit|\binteraction of|\bformation of|\bassembl|\bbind ", "binding"),
]
# Anything not matched falls back to state_change (the most generic conformational
# / status transition), and is flagged low-confidence in the audit.
FALLBACK = "state_change"


def classify(mechanism: str) -> tuple[str, str]:
    """Return (inferred_type, confidence) for a mechanism string."""
    text = (mechanism or "").lower()
    for pattern, rxn_type in RULES:
        if re.search(pattern, text):
            return rxn_type, "rule"
    return FALLBACK, "fallback"


def has_pmid(value: str) -> bool:
    v = (value or "").strip()
    return bool(v) and v != "-" and bool(re.search(r"\d", v))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    re_df = pd.read_csv(REACTION_EVIDENCE, sep="\t", dtype=str, keep_default_na=False)
    ssc_df = pd.read_csv(SSC_CURATED, sep="\t", dtype=str, keep_default_na=False)

    # ---- Job 1: classify TODO reaction types -------------------------------
    todo_mask = re_df["type"].str.strip() == "TODO"
    n_todo_before = int(todo_mask.sum())
    inferences: list[dict] = []
    for idx in re_df.index[todo_mask]:
        mech = re_df.at[idx, "mechanism"]
        rxn_type, confidence = classify(mech)
        re_df.at[idx, "type"] = rxn_type
        # trace the inference in notes, idempotently
        note = re_df.at[idx, "notes"]
        if INFERRED_TAG not in note:
            re_df.at[idx, "notes"] = (note + " " + INFERRED_TAG).strip()
        inferences.append(
            {
                "reaction_id": re_df.at[idx, "reaction_id"],
                "mechanism": mech,
                "inferred_type": rxn_type,
                "confidence": confidence,
            }
        )

    n_fallback = sum(1 for i in inferences if i["confidence"] == "fallback")
    re_df.to_csv(REACTION_EVIDENCE, sep="\t", index=False)

    # ---- Job 2: provenance × ECO × PMID stratification ---------------------
    def layer_stats(df: pd.DataFrame, eco_col: str, pmid_col: str, layer: str) -> list[dict]:
        rows = []
        for eco, sub in df.groupby(df[eco_col].str.strip()):
            n = len(sub)
            n_pmid = int(sub[pmid_col].apply(has_pmid).sum())
            rows.append(
                {
                    "layer": layer,
                    "evidence_code": eco or "(none)",
                    "n_reactions": n,
                    "n_with_pmid": n_pmid,
                    "n_without_pmid": n - n_pmid,
                }
            )
        return rows

    # The 85 SSc rows are present in BOTH reaction_evidence.tsv and
    # ssc_curated_reactions.tsv. To avoid double-counting, "backbone" is the
    # pure-Reactome remainder (reaction_id not starting with "ssc_").
    backbone_df = re_df[~re_df["reaction_id"].str.startswith("ssc_")].copy()
    backbone_rows = layer_stats(backbone_df, "evidence_code", "pmid", "reactome_backbone")
    ssc_rows = layer_stats(ssc_df, "evidence_code", "pmid", "ssc_tier1")
    strat = pd.DataFrame(backbone_rows + ssc_rows)
    strat = strat.sort_values(["layer", "evidence_code"]).reset_index(drop=True)
    strat.to_csv(OUT_DIR / "evidence_stratification.tsv", sep="\t", index=False)

    def layer_summary(df: pd.DataFrame, pmid_col: str) -> dict:
        n = len(df)
        n_pmid = int(df[pmid_col].apply(has_pmid).sum())
        # "experimental" = direct assay / expression / physical-interaction codes
        exp_codes = {"ECO:0000314", "ECO:0000270", "ECO:0000353"}
        n_exp = int(df["evidence_code"].str.strip().isin(exp_codes).sum())
        return {
            "n_reactions": n,
            "n_with_pmid": n_pmid,
            "pct_with_pmid": round(100 * n_pmid / n, 1) if n else 0.0,
            "n_experimental_eco": n_exp,
            "pct_experimental_eco": round(100 * n_exp / n, 1) if n else 0.0,
        }

    summary = {
        "todo_classification": {
            "n_todo_before": n_todo_before,
            "n_todo_after": int((re_df["type"].str.strip() == "TODO").sum()),
            "n_classified": len(inferences),
            "n_by_rule": len(inferences) - n_fallback,
            "n_by_fallback": n_fallback,
            "type_distribution_after": re_df["type"].str.strip().value_counts().to_dict(),
        },
        "provenance": {
            "reactome_backbone": layer_summary(backbone_df, "pmid"),
            "ssc_tier1": layer_summary(ssc_df, "pmid"),
        },
        "ssc_curation_status": (
            ssc_df["curation_status"].str.strip().replace("", "(unset)").value_counts().to_dict()
            if "curation_status" in ssc_df.columns else {}
        ),
        "inferences": inferences,
    }
    (OUT_DIR / "evidence_stratification.json").write_text(json.dumps(summary, indent=2))

    # ---- Markdown report ---------------------------------------------------
    bb = summary["provenance"]["reactome_backbone"]
    sc = summary["provenance"]["ssc_tier1"]
    md = []
    md.append("# Evidence stratification — provenance × evidence quality\n")
    md.append("_Auto-generated by `scripts/evidence_audit.py` (v1.1 hardening sprint, H1)._\n")
    md.append("## 1. Two provenance layers\n")
    md.append(
        "The integrated map's reaction annotations come from two distinct layers. "
        "Conflating them inflates the apparent depth of the SSc-specific curation.\n"
    )
    md.append("| Layer | Reactions | With PMID | Experimental ECO (314/270/353) |")
    md.append("|---|---|---|---|")
    md.append(
        f"| **Reactome backbone** (pure-Reactome rows of `reaction_evidence.tsv`) | {bb['n_reactions']} | "
        f"{bb['n_with_pmid']} ({bb['pct_with_pmid']}%) | {bb['n_experimental_eco']} ({bb['pct_experimental_eco']}%) |"
    )
    md.append(
        f"| **SSc-Tier-1** (`ssc_curated_reactions.tsv`) | {sc['n_reactions']} | "
        f"{sc['n_with_pmid']} ({sc['pct_with_pmid']}%) | {sc['n_experimental_eco']} ({sc['pct_experimental_eco']}%) |"
    )
    md.append("")
    md.append(
        "**Read this as:** the headline reaction count is dominated by the imported "
        "Reactome backbone, which propagates `ECO:0000305` (curator inference) by default. "
        f"The genuinely SSc-specific layer is {sc['n_reactions']} reactions, of which "
        f"{sc['n_with_pmid']} carry a primary PMID and {sc['n_experimental_eco']} carry an "
        "experimental ECO code. This is the honest denominator for 'how much new SSc "
        "curation does this resource contribute'.\n"
    )
    status = summary.get("ssc_curation_status", {})
    if status:
        md.append("## 1b. SSc-Tier-1 curation status (depth pass)\n")
        md.append(
            "Each SSc reaction carries a `curation_status`. `proposed` rows received a "
            "literature-mined, abstract-verified citation pending co-author ratification; "
            "`conceptual_bridge`/`phenotype_aggregation` are honest reclassifications of "
            "cell-state assertions that are not single molecular interactions (not citation "
            "debt); `untested` rows still need a primary citation and carry a candidate pool.\n"
        )
        md.append("| status | n |")
        md.append("|---|---|")
        for s, c in sorted(status.items(), key=lambda kv: -kv[1]):
            md.append(f"| {s} | {c} |")
        md.append("")
    md.append("## 2. TODO reaction-type classification\n")
    tc = summary["todo_classification"]
    md.append(
        f"- `type=TODO` rows before: **{tc['n_todo_before']}** → after: **{tc['n_todo_after']}**\n"
        f"- Classified by keyword rule: **{tc['n_by_rule']}**; by generic fallback "
        f"(`{FALLBACK}`, low confidence): **{tc['n_by_fallback']}**\n"
        f"- Each inference is traced in the `notes` column (`{INFERRED_TAG}`) and is reversible.\n"
    )
    md.append("Type distribution after classification:\n")
    md.append("| type | n |")
    md.append("|---|---|")
    for t, c in sorted(tc["type_distribution_after"].items(), key=lambda kv: -kv[1]):
        md.append(f"| {t} | {c} |")
    md.append("")
    md.append("## 3. Full provenance × ECO × PMID matrix\n")
    md.append("See `evidence_stratification.tsv`. Per (layer, ECO):\n")
    md.append("| layer | ECO | n | with PMID | without PMID |")
    md.append("|---|---|---|---|---|")
    for _, r in strat.iterrows():
        md.append(
            f"| {r['layer']} | {r['evidence_code']} | {r['n_reactions']} | "
            f"{r['n_with_pmid']} | {r['n_without_pmid']} |"
        )
    md.append("")
    (OUT_DIR / "evidence_stratification.md").write_text("\n".join(md))

    # ---- console ------------------------------------------------------------
    print(f"[evidence_audit] TODO types: {tc['n_todo_before']} -> {tc['n_todo_after']} "
          f"({tc['n_by_rule']} by rule, {tc['n_by_fallback']} fallback)")
    print(f"[evidence_audit] backbone: {bb['n_reactions']} rxn, {bb['pct_with_pmid']}% PMID, "
          f"{bb['pct_experimental_eco']}% experimental ECO")
    print(f"[evidence_audit] SSc-Tier1: {sc['n_reactions']} rxn, {sc['pct_with_pmid']}% PMID, "
          f"{sc['pct_experimental_eco']}% experimental ECO")
    print(f"[evidence_audit] wrote {OUT_DIR}/evidence_stratification.{{tsv,json,md}}")


if __name__ == "__main__":
    main()
