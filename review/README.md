# SSc-MIM interaction review app

A self-contained, offline static app to adjudicate every curated SSc interaction one by one.

## Use
Just open **`review/index.html`** in a browser (double-click — no server needed).

Per interaction you get: regulator → target (+ sign), mechanism, **evidence level**, the
**AI recommendation** + rationale, the **verbatim deciding sentence**, and **PubMed/DOI links**
(incl. secondary sources for multi-source interactions). Decide with **Confirm / Reject /
Re-include**, add a note, and **export** your decisions to CSV/JSON. Decisions persist locally
(localStorage). Filter by status / module / AI-reco / decision, search, and use keyboard shortcuts
(← → C R I N).

Discarded/excluded interactions are included (with the reason) so you have full control — you can
re-include any. Contradictions and to-complete quotes are flagged.

## Refresh after curation changes
```
make review        # rebuilds analysis/curation/interaction_database.csv + this app
```
The app embeds a snapshot of the database; re-run to pick up new interactions.
