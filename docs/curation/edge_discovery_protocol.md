# Edge-discovery protocol — growing the SSc-specific layer without adding nonsense

> See ROADMAP § "SSc-specificity growth plan". This is the operating procedure for adding new
> SSc-specific curated reactions. The governing rule: **the curated map is never written
> speculatively** — every new edge passes five automated gates *and* human ratification.

## Pipeline

```
SSc papers → candidate edges (staging) → G0–G4 gates → ratification → promote → wire/audit/lint
```

1. **Stage** candidate edges in `curation/staging/ssc_edge_candidates.tsv` (never the curated TSV).
   Columns: `candidate_id, module, type, mechanism, reactants, products, modifiers,
   source_pmid, supporting_quote, ssc_relevance, proposed_eco, decision`.
   The `supporting_quote` is a **verbatim sentence from the source paper** that states the edge.
2. **Fetch** source text: `make corpus-fetch` (`scripts/fetch_ssc_corpus.py`) caches OA full
   text (Europe PMC) or the abstract to `curation/staging/corpus/<pmid>.txt`.
3. **Gate**: `make validate-edges` (`scripts/validate_edge_candidates.py`) → `validation_report.tsv`:
   - **G0 schema** — required fields; `type` in the controlled vocabulary.
   - **G1 HGNC** — every gene entity is an official HGNC symbol (HGNC REST, cached).
   - **G2 grounding** — the `supporting_quote` must be a verbatim substring of the cached source
     text. *If the quote is not in the paper, the edge is rejected.* This is the anti-hallucination
     keystone.
   - **G3 novelty** — the (input→product) gene pair is not already an SSc reaction (dedup, hard
     reject) and, advisory, not a forward Reactome-backbone pair (`G3:reactome_overlap` flag).
   - **G4 evidence** — numeric PMID; corpus text present (SSc-context by corpus membership).
   Verdicts: **PASS** (clean) / **FLAG** (soft issue) / **REJECT** (hard fail).
4. **Ratify**: a human sets `decision = promote` on the candidate rows to accept (default empty
   = held). Only PASS + `decision=promote` are eligible.
5. **Promote**: `make promote-edges` (`scripts/promote_edges.py`) appends ratified rows to
   `ssc_curated_reactions.tsv` with `ratification = "AI-proposed (discovery)"` and the quote in
   `notes`; each is one reversible row.
6. **Rebuild**: `make wire network evidence-audit evidence-lint preflight` (+ `reactome-novelty`).

## Rules

- **Quality over volume.** 12 solid grounded edges beat 40 shaky ones. Padding is a failure.
- **Disease-specific only.** Prefer content Reactome structurally cannot hold (autoantibodies,
  GWAS-function, SSc cell states, crosstalk, clinical axes). New edges should be Reactome-novel
  (see `make reactome-novelty`).
- **One quote, one edge.** Every causal statement is backed by a verbatim quote that grounds.
- **Reversible + tagged.** Promoted discovery edges are tagged in `ratification` and removable
  by deleting one TSV row and re-wiring.
- **Human sign-off remains.** AI proposes and self-gates; the corresponding author ratifies the
  biology (`decision=promote`) and the per-row `ratification` tag records provenance.
