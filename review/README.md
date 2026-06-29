# SSc-MIM interaction review app

A self-contained, offline static app to adjudicate every curated SSc interaction one by one,
in a swipe-based ("Tinder-like") deck.

## Use
Just open **`review/index.html`** in a browser (double-click — no server needed).

The page is split in two: the **card deck on the left**, and a **module-map preview on the right**.
The preview is a force-directed graph (computed in-browser, no library) of the **whole module** the
interaction belongs to, **initially zoomed on the reaction being evaluated**. **Scroll to zoom, drag
to pan**, or use the buttons — ◎ re-zoom on the reaction, **+ / –**, and **⤢ fit the whole module**.
The current interaction's edges are highlighted in blue and its participants keep their card colours;
**click any edge** to jump to that interaction in the deck. The layout is computed once per module
(so it stays stable as you move between its cards). On narrow screens the preview hides.

You get **one card at a time**. Each card lays out everything backing the interaction:
regulator → target with the interaction type, the mechanism, **SSc relevance**, the **verbatim
deciding sentence**, the **source article** (title + journal/year + **PubMed/DOI links**, incl.
secondary sources for multi-source interactions), the **evidence level** / ECO code / provenance,
the **AI recommendation** + rationale, and a **Literature dossier**.

The **Literature dossier** gives the reviewer maximum context before deciding: a PubMed pass
(`scripts/mine_evidence_dossier.py`) lists, per interaction, **candidate supporting** articles
(co-mentioning the participants in an SSc/fibrosis context) and, in a **separate “Possibly
contrary”** column, articles carrying a contrary cue (a null result — “no effect / not associated /
did not” — or an opposite-direction signal such as “anti-fibrotic / protective”), each with the
matched cue. These are **candidate references retrieved by query, not adjudicated verdicts** (every
PMID is real, none fabricated) — read and judge.

**AI reviewer call.** Above the dossier, each card shows an advisory verdict the assistant reached
**after actually reading** the deciding quote + every support/contrary abstract for that interaction
(`scripts/build_reading_packets.py` assembles the abstracts; the calls are in
`curation/ai_review_verdicts.json`): **✓ validate** (would confirm), **✎ revise citation** (biology
sound but the cited PMID looks wrong — replace it), **⚠ caution** (supported but genuinely
contested), or **✗ reject**. Each carries a one-line rationale and the PMIDs it relied on. It is
**advisory only** — the human reviewer decides. Filter the deck by AI call to triage (e.g. jump
straight to the *revise* citations). Notably this pass flagged ~28 interactions whose cited
reference points to an unrelated paper (the underlying biology is sound; only the citation needs
fixing).

**Citations extracted from the source article.** `scripts/mine_pdf_quotes.py` pulls the single
sentence that best supports each interaction, taking the text from — in order — a **local full-text
PDF** (`/home/drfox/data/IDT_SSc_map/article/<pmid>.pdf`), the **PubMed Central open-access full
text**, or the **PubMed abstract** (the last two fetched via NCBI E-utils and cached). It is shown
as the deciding sentence, badged *“📄 extracted from … — verify”* (PDF / PMC full-text / PubMed
abstract); PDF picks add the page number and an *“↗ PDF p.N”* deep-link. Each reaction participant
gets **its own colour** — the same colour in the regulator→target headline and on its mentions
(incl. synonyms) in the sentence — so you can map sentence to reaction at a glance. When the pick is
ambiguous a collapsible **“alternative sentence”** offers the runner-up. These are heuristic
proposals — confirm or correct them.

The top progress bar tracks your **position in the deck** (card *X* / *N*) and resets to the first
card each time you open the app; stored decisions are shown separately as *“K/143 decided”*.

The matcher knows the common name↔symbol synonyms used in papers (e.g. `TGFB1`→“TGF-β”,
`LGALS3`→“galectin-3”, `EDN1`→“endothelin-1”, `ARNT`→“HIF-1β”), so it still finds the sentence
when the article never spells the HGNC symbol. Reactions with **no confident match** keep their
existing backing — the curated mechanism text, the evidence note, the ECO code, and the PMID/DOI.

**Swipe the card** right to accept, left to reject — or use the action buttons / keyboard:

| Action | Swipe | Keys | Meaning |
|--------|-------|------|---------|
| Accept | →     | `→` / `A` | keep an `in_map` interaction (**confirm**), or **re-include** a discarded one |
| Reject | ←     | `←` / `R` | mark as not belonging in the map |
| Skip   |       | `↑` | move on without deciding |
| Undo   |       | `Z` | revert the last decision and step back |
| Note   |       | `N` | open the reviewer-note field |

A green **Keep** / red **Drop** stamp tracks the drag; decided cards carry a KEPT/REJECTED ribbon.
The top bar shows live progress and lets you **Filter** (status / module / AI-reco / decision +
search), **export** decisions to CSV/JSON, and **Reset** (clears every stored decision & note, after
confirmation). Everything persists locally (localStorage).

Discarded/excluded interactions are included (with the reason) so you have full control — you can
re-include any. Contradictions and to-complete quotes are flagged.

## Refresh after curation changes
```
make review        # rebuilds analysis/curation/interaction_database.csv + this app
```
The app embeds a snapshot of the database; re-run to pick up new interactions.
