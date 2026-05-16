# ROADMAP — SSc-MIM (Skin Fibrosis Molecular Interaction Map)

> **Revised on 2026-05-16.** Phase 0 + Phase 1 + the *import* half of Phase 2 are complete, weeks ahead of the original calendar. This rewrite reorganises the remaining work into **three execution lanes** so as much as possible runs without human intervention.

- **Window:** 15 May 2026 → 22 September 2026 (18 weeks).
- **Primary target:** ACR Convergence 2026 late-breaking abstract (deadline 22 Sep 2026, 12:00 ET).
- **Backup:** methodological paper for *Frontiers in Bioinformatics* / *npj Systems Biology and Applications*.
- **Authoritative status:** [STATUS.md](STATUS.md) (snapshot) and the git log (history). This file describes intent and remaining work.

## Execution lanes

Every remaining task is tagged one of:

- 🟢 **AUTO** — fully scripted. Runs in CI or via `make`, produces a reproducible artifact, no human in the loop.
- 🟡 **ASSIST** — script generates a scaffold (XML stub, TSV with TODO rows, markdown checklist). A human fills the biology; the script keeps the scaffold honest.
- 🔴 **HUMAN** — cannot be replaced by code: kickoff meetings, biological sign-off, CellDesigner GUI work, MINERVA account, ACR portal submission.

The point of this revision: keep the project moving on the 🟢 lane while the 🔴 lane is unblocked.

---

## Completed (with commit references)

| Phase | Item | Commit | Lane |
|-------|------|--------|------|
| 0 | Repo bootstrap, LICENSE (CC-BY + MIT), CITATION.cff, .gitignore, CONTRIBUTING, issue templates, SBML CI + libSBML validator | `4dcf004` | 🟢 |
| 1.w1 | Curation guidelines (Mazein 2023-adapted), MI2CAST checklist, scoping notes, risks, four module specs with Tier-1 entity tables | `4dcf004` | 🟢 |
| 1.w1 | Reactome → CellDesigner conversion pilot (live, R-HSA-2173789 TGF-β) | `bfdaea7` | 🟢 |
| 1.w1 | Linters (`check_module_specs`, `check_bib`); caught and fixed 3 real Tier-1 spec bugs | `a23c8bd` | 🟢 |
| 1.w3 | Omics dataset decision (Tabib scRNAseq primary, Whitfield bulk reserve) | `f2354f9` | 🟡 |
| 2.w4-5 | M1 IFN-α/β import + post-process + harmonise — 83 species, 25 reactions | `dd5da1d`, `392bb15` | 🟢 |
| 2.w6-7 | M2 TGF-β SMADs + PDGF — 175 species, 77 reactions | `dd5da1d`, `392bb15` | 🟢 |
| 2.w8-9 | M3 Notch1 (EndMT scaffold; rest manual per design) — 77 species, 39 reactions | `392bb15` | 🟢 |
| 2.w10-11 | M4 IL-6 — 64 species, 34 reactions | `dd5da1d`, `392bb15` | 🟢 |
| Tooling | Reactome post-processor, harmoniser (decode + classify + rename), species seeder, Makefile, scripts-smoke CI | `cf92a46`, `876deaa`, `1304100`, `b7226eb` | 🟢 |

**Volumetric checkpoint (post-import, pre-curation):** 399 raw species, 175 reactions across 5 pathways → 385 unique after cross-import dedupe. Comfortable headroom for the 200–300 / 300–450 target range.

---

## What's left

### Phase 2 (curation) — remaining work

The per-module workflow runs days 1–14. Days 1–5 (import / harmonisation) are done for every module. Days 6–14 split as follows:

| Day | Step | Lane |
|-----|------|------|
| 6–8 | **SSc-specific Tier-1 augmentation** — add CXCL4/PF4, POSTN, COMP, CTGF/CCN2, FRA-2, TBX2, endothelin axis, etc. | 🟡 ASSIST |
| 9–10 | **MI2CAST annotation** — PMID + ECO code per reaction | 🟡 ASSIST |
| 11–12 | **Quality pass** — libSBML, sink connectivity, dangling species, citation completeness | 🟢 AUTO |
| 13–14 | **Buffer / write-up** of the as-built module | 🟡 ASSIST |

#### 🟢 AUTO automation queue (Phase 2 polish)

These ship in this batch and the next; no human input required:

1. ✅ **Extract PMIDs from BioPAX.** `scripts/extract_pmids_from_biopax.py` walks the four `*.owl` files, mines `bp:xref` / `bp:PublicationXref`, seeds `pubmed_corpus.bib` and pre-fills `reaction_evidence.tsv` with one row per Reactome reaction.
2. ✅ **Sink-node connectivity check.** `scripts/sink_connectivity.py` enforces the "every Tier-1 species → sink in ≤ 6 steps" rule from scoping notes.
3. ✅ **Cross-module dedupe report.** Already part of the seeder + integrator.
4. **Cofactor cleanup at integration.** Re-run cofactor collapse across modules (ATP-cyto from M1 = ATP-cyto from M2 once integrated).
5. **Validate-on-CI for all harmonised XMLs.** Already wired; just needs the harmonised paths added.

#### 🟡 ASSIST automation queue (Phase 2 — curator-driven)

1. **`scripts/ssc_additions_template.py`** — read `docs/module_specs/M*.md` Tier-1 tables, emit a starter CellDesigner XML fragment per module with each SSc-specific Tier-1 species as a placeholder node (id, name, compartment from the table; empty reactions). Curator wires the biology in CellDesigner; script does the bookkeeping.
2. **`scripts/mi2cast_starter_rows.py`** — for each reaction in each harmonised XML, emit a draft row in `reaction_evidence.tsv` (reaction_id, type from SBO if present, participants list from the SBML reactants/products, empty mechanism / pmid / evidence_code / module / notes). Reduces the curator's MI2CAST fill from "write 175 rows" to "fill in PMID + mechanism + ECO".
3. **`scripts/bib_lookup.py`** — given a PMID, fetch the canonical citation via NCBI E-utilities and append a `pubmed_corpus.bib` entry. Idempotent. The curator pastes PMIDs into a queue file; the script does the BibTeX bookkeeping.

#### 🔴 HUMAN blockers (Phase 2)

- SSc-specific reaction biology — the curator decides "in SSc skin, CXCL4 drives Th2 chemotaxis with PMID X showing this in dermal biopsies".
- ECO code assignment for each reaction.
- Final Tier-1 sign-off by the rheumatologist.

### Phase 3 (integration + deployment) — weeks 12–14

| Step | Lane | Status |
|------|------|--------|
| Inter-module crosstalk inventory | 🟡 ASSIST | Scaffolded from module specs (this batch); curator confirms |
| Integrate 5 harmonised XMLs → `SSc_MIM_integrated.xml` | 🟢 AUTO | This batch (`scripts/integrate_modules.py`) |
| Cross-module species dedupe + cofactor collapse | 🟢 AUTO | Bundled with integration |
| One round of expert review | 🔴 HUMAN | Locked into rheumatologist's calendar |
| MINERVA upload + colour palette + semantic zoom | 🔴 HUMAN | Needs curator account; we hand off a deployment-ready file |
| Cytoscape-style network analysis | 🟢 AUTO | This batch (`scripts/network_analysis.py`) — pure networkx, no GUI |
| Sink-node connectivity & dangling species | 🟢 AUTO | This batch (`scripts/sink_connectivity.py`) |
| CaSQ Boolean inference (optional) | 🟢 AUTO | Already in `environment.yml`; wire to `make boolean` next batch |

#### 🟢 AUTO automation queue (Phase 3)

1. ✅ **Integration.** `scripts/integrate_modules.py` (this batch) — merge the five harmonised XMLs into `curation/celldesigner/SSc_MIM_integrated.xml`. Deduplicate species by id with explicit dedupe report. Resolve shared-species "homes" from the Tier-1 spec annotations (ACTA2→M2, JAK1/TYK2→M1).
2. ✅ **Network analysis.** `scripts/network_analysis.py` (this batch) — networkx-based: degree, betweenness, closeness, PageRank on species nodes; Louvain communities vs hand-defined modules; top-20 hubs.
3. ✅ **Sink connectivity.** `scripts/sink_connectivity.py` (this batch) — shortest path from every species to the four sinks; flag length > 6.
4. **CaSQ + GINsim sanity simulation.** Next batch. `make boolean` runs `casq` on the integrated map → SBML-qual; run one perturbation (TGF-β ON → ECM_deposition reachable).
5. **MINERVA-readiness check.** Next batch. `scripts/minerva_preflight.py` — verify unique IDs, every species annotated, every reaction PMID-tagged; emit a green/red checklist.

### Phase 4 (translational use case + figures) — weeks 15–17

| Step | Lane | Status |
|------|------|--------|
| Download + QC + cluster Tabib scRNAseq (GSE138669) | 🟢 AUTO | Notebook stubs in place; needs data download | 
| Per-cluster DEG (SSc vs HC) | 🟢 AUTO | Stub `03_deg.ipynb` |
| Project DEGs onto MIM species | 🟢 AUTO | Stub `04_projection.ipynb` |
| Per-donor module activation scores | 🟢 AUTO | Stub `05_scoring.ipynb` |
| Druggable hub prioritisation (DGIdb + Open Targets) | 🟢 AUTO | Stub `06_drug_targets.ipynb` |
| Whitfield bulk overlay (complementary) | 🟢 AUTO | Stub notebook to be added |
| Figure F2 — overlay heatmap | 🟢 AUTO | Generated from `05_scoring.ipynb` |
| Figure F3 — druggable targets sub-network + table | 🟢 AUTO | Generated from network + drug-target join |
| Figure F1 — global MIM screenshot from MINERVA | 🔴 HUMAN | Requires the deployed MINERVA URL |
| Composite clinical-readable layout | 🟡 ASSIST | Script renders panels; human places labels |

#### 🟢 AUTO automation queue (Phase 4)

1. **`scripts/fetch_tabib.py`** — pull GSE138669 from GEO (large; may need user-side compute). Writes a manifest and a checksum.
2. **`scripts/build_overlay.py`** — load AnnData → DEG per cluster → MIM projection → MINERVA-format TSV. Pure batch.
3. **`scripts/druggable_hubs.py`** — query DGIdb + Open Targets for the top-20 hubs from the network analysis; produce `analysis/overlay/druggable_hubs.tsv`.
4. **`scripts/render_figures.py`** — matplotlib + networkx — produces F2 (heatmap of per-donor module scores) and F3 (hub subnetwork + drug-target table). F1 stays human (MINERVA screenshot).

### Phase 5 (writing + submission) — week 18+

| Step | Lane | Status |
|------|------|--------|
| ACR abstract draft (300 words + figs) | 🟡 ASSIST | Script outline from STATUS + module specs |
| Co-author iteration | 🔴 HUMAN | |
| ACR portal submission | 🔴 HUMAN | |
| Manuscript draft for *Frontiers in Bioinformatics* / *npj Sys Biol* | 🟡 ASSIST | Outline scaffolded; sections written by lead curator |

#### 🟡 ASSIST automation queue (Phase 5)

1. **`scripts/draft_abstract.py`** — from `STATUS.md` + module spec headers + analysis hub table, emit an ACR-style 300-word abstract scaffold (Background / Methods / Results / Conclusion) with placeholders for numerical results. Lead curator edits for voice and final framing.

---

## Revised milestone calendar

The original calendar treated weeks 4–11 as "module curation". With imports done, the curator's focus shifts entirely to **biology-side work** while the 🟢 lane keeps producing artifacts. Dates below reflect what's now realistic:

| # | Milestone | Original date | Revised | Lane | Status |
|---|-----------|---------------|---------|------|--------|
| M0 | Stack + repo skeleton | 14 May | 15 May | 🟢 | ✅ |
| M1 | Scope locked, clinical co-author signed on | 5 Jun | unchanged | 🔴 | ⏸ |
| M2 | Module M1 (IFN-I) imported | 19 Jun | **15 May** | 🟢 | ✅ |
| M3 | Module M2 (TGF-β) imported | 3 Jul | **15 May** | 🟢 | ✅ |
| M4 | **Go/no-go #1** — M1+M2 done? | 24 Jul | n/a — imports completed in week 1 | 🟢 | ✅ skipped |
| M5 | Modules M3 + M4 imported | 31 Jul | **15 May** | 🟢 | ✅ |
| M5.5 | Integrated MIM (auto-merged) | n/a | **16 May** | 🟢 | this batch |
| M5.6 | Network analysis + sink connectivity | week 14 | **16 May** | 🟢 | this batch |
| M6 | Integrated MIM with SSc-specific crosstalk | 14 Aug | unchanged (needs curator + expert) | 🟡 + 🔴 | scaffolded |
| M7 | **Go/no-go #2** — Expert validation? | 21 Aug | unchanged | 🔴 | ⏸ |
| M8 | MINERVA deployment | 21 Aug | unchanged | 🔴 | ⏸ |
| M9 | Omics overlay computed, figures drafted | 11 Sep | unchanged for figures; **AUTO can run as soon as the integrated map is signed off** | 🟢 + 🔴 | partial |
| M10 | Abstract submitted to ACR 2026 | ≤22 Sep 2026, 12:00 ET | unchanged | 🔴 | ⏸ |
| M11 | Full manuscript draft circulated | 30 Nov | unchanged | 🟡 + 🔴 | ⏸ |

**Take-away:** the calendar's bottleneck shifted from "can the curator finish in time?" to "when does the rheumatologist sign off?" The 🟢 lane keeps producing artifacts and the curator can attack biology-only work without waiting.

---

## Go / no-go gates — updated

| Gate | Original date | Revised | Question | If yes | If no |
|------|---------------|---------|----------|--------|-------|
| G1 | 24 Jul 2026 | **n/a — auto-completed** | M1 + M2 imports + harmonised? | (gate skipped; imports done in week 1) | (not reachable) |
| G2 | 21 Aug 2026 | unchanged | Expert review completed and integrated? | Submit with full-confidence framing | Submit with "validation in progress" caveat |
| G3 | 18 Sep 2026 | unchanged | Abstract co-author sign-off achieved? | Submit on/before 21 Sep | Push to EULAR 2027 |
| **G1.5 (new)** | **End of week 4 — 12 Jun 2026** | new gate | Has the rheumatologist signed off on the four-module scope and the Tier-1 lists? | Curator launches Phase 2 day-6+ biology work | Re-scope; consider dropping M3 or merging M3 into M2 |

The new G1.5 gate replaces G1 since the original G1 (about curator pace) is no longer the binding constraint.

---

## Risk register — updated

| Risk | Original level | New level | Why |
|------|----------------|-----------|-----|
| R1 — Curation slower than planned | high | **medium-low** | Imports + harmonisation done in week 1; biology-only work remaining |
| R2 — Reactome → CellDesigner incompatibilities | medium | **low** | Conversion verified live on 5 pathways |
| R3 — Late expert validation | medium | **medium (binding constraint)** | Now the principal scheduling risk |
| R4 — "Wow factor" for ACR clinician reviewer | medium | unchanged | Mitigated by automation of F2 + F3 figures |
| R5 — Still "preliminary" at submission | low–medium | **low** | Late-breaking track tolerates it; overlay AUTO-runs |
| R6 — Reproducibility regression | medium | **low** | `environment.yml` pinned, CI green |
| R7 — Data licensing / GEO availability | low | unchanged | |
| R8 — Tooling drift on MINERVA | low | unchanged | Mirror to Zenodo planned |
| **R9 (new) — Automation drift from biology** | n/a | **medium** | Script-generated scaffolds can ossify wrong choices. Mitigation: every transform produces a JSON report; nothing is destructive; curator can override. |

---

## Open external blockers (handover queue)

These are the **only** items that prevent further automated progress. They live with the user:

1. **Rheumatologist kickoff + co-authorship lock** (single most important).
2. **MINERVA Luxembourg curator role** request.
3. **Bibliography sprint** (~150 PMIDs to feed `pubmed_corpus.bib`).
4. **CellDesigner GUI** open of each `*.harmonised.xml` for visual round-trip and SSc-specific augmentation.
5. **WikiPathways EndMT pathway ID** lookup (the original WP_3942 is PPAR signalling).
6. **`CITATION.cff` `REPLACE_ME` placeholders** — author / ORCID / repo URL.
7. **ACR portal account** + figure-format check (limits change annually).

The 🟢 + 🟡 lanes proceed independently of these.

---

## How to drive the project from here

```bash
# Run everything that doesn't need a human
make lint                              # specs + bib linters
make validate                          # libSBML on every harmonised XML
make harmonise                         # re-runs the post-process + harmonise pipeline
make seed                              # regenerates species_annotations.tsv
make integrate     # this batch        # builds SSc_MIM_integrated.xml + dedupe report
make network       # this batch        # centrality + communities + hubs
make sink-check    # this batch        # sink-node connectivity report
make pmids         # this batch        # mines BioPAX -> bib + reaction_evidence.tsv
```

The intent is that a fresh clone + `make all` reaches the same state without manual steps.

---

*Last revised: 2026-05-16, after the import + harmonisation phase landed.*
