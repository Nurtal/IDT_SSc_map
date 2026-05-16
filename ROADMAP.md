# ROADMAP — SSc-MIM (Skin Fibrosis Molecular Interaction Map)

> **Revised on 2026-05-16 (pivot).** Primary delivery is **a functional, robust map hosted on GitHub + Zenodo (citable DOI)**, before ACR submission. MINERVA Luxembourg deployment is moved to a **post-publication stretch goal**. Co-author is locked (médecine interne, ARD-published SSc collaboration).

- **Window:** 15 May 2026 → 22 September 2026 (18 weeks).
- **Primary target:** ACR Convergence 2026 late-breaking abstract (deadline 22 Sep 2026, 12:00 ET) supported by a citable Zenodo DOI for the v1.0 map.
- **Backup:** methodological paper for *Frontiers in Bioinformatics* / *npj Systems Biology and Applications*.
- **Authoritative status:** [STATUS.md](STATUS.md) (snapshot) and the git log (history). This file describes intent and remaining work.

## Execution lanes

- 🟢 **AUTO** — fully scripted. Runs via `make`, no human in the loop.
- 🟡 **ASSIST** — script generates a scaffold; the curator + co-author fill the biology.
- 🔴 **HUMAN** — irreducible: scope sign-off, CellDesigner GUI, ACR submission, git-tag push.

---

## Pivot — what changed on 2026-05-16

| Before | After |
|--------|-------|
| MINERVA deployment in Phase 3 (week 14) on critical path | MINERVA = stretch goal, Phase 6 (post-publication) |
| "Need rheumatologist co-author" was the principal blocker | Co-author **locked** — médecine interne, prior ARD-SSc publication |
| Public URL via MINERVA was the abstract's anchor | Zenodo DOI is the abstract's anchor; MINERVA optional |
| 7 external blockers on the handover queue | 3 (CellDesigner GUI, CITATION.cff fill, GitHub→Zenodo webhook toggle) |

**Why this works:**
- The map content (SBML + annotations + figures + scripts) is the scientific deliverable. Hosting is a rendering of it. GitHub + a Zenodo DOI gives a stable, citable URL with no curator-role gatekeeping.
- The dual licence (CC-BY 4.0 for content, MIT for code) is already configured.
- ACR reviewers care about the resource + the translational story, not the hosting platform. "Available on GitHub (link) / archived on Zenodo (DOI)" is unambiguous.
- MINERVA stays a strong "v2.0 follow-up" line for the methodological paper.

---

## Completed (with commit references)

| Phase | Item | Commit | Lane |
|-------|------|--------|------|
| 0 | Repo bootstrap (LICENSE dual, CITATION.cff, .gitignore, CONTRIBUTING, issue templates, SBML CI + libSBML validator) | `4dcf004` | 🟢 |
| 1.w1 | Curation guidelines (Mazein 2023), MI2CAST checklist, scoping notes, risks, four module specs with Tier-1 tables | `4dcf004` | 🟢 |
| 1.w1 | Reactome → CellDesigner conversion pilot (live, R-HSA-2173789 TGF-β) | `bfdaea7` | 🟢 |
| 1.w1 | Linters; caught and fixed 3 real Tier-1 spec bugs | `a23c8bd` | 🟢 |
| 1.w3 | Omics dataset decision (Tabib scRNAseq primary, Whitfield bulk reserve) | `f2354f9` | 🟡 |
| 2.w4-11 | Reactome imports + post-process + harmonise for M1, M2 (×2), M3 (Notch1), M4 — **399 raw species, 175 reactions** | `dd5da1d`, `392bb15` | 🟢 |
| 3.w12 | Integration of 5 harmonised XMLs → **`SSc_MIM_integrated.xml`** (385 species, 175 reactions, 14 cross-module dedupes) | `f49d930` | 🟢 |
| 3.w12 | Auto-generated crosstalk matrix from module specs (14 edges) | `88345fb` | 🟢 |
| 3.w14 | Network analysis — centrality + top-20 hubs + 31 communities | `739c2fa` | 🟢 |
| 3.w14 | Sink-node connectivity audit (0 violate the >6 rule; 126 dangling → curator backlog) | `f420cb4` | 🟢 |
| 2.w9-10 | **355 PMIDs mined** from Reactome SBML; 159 reaction_evidence rows seeded (158 with citation) | `2490917` | 🟢 |
| 2.w9-10 | **350/350 PMIDs filled** via NCBI E-utils (title, authors, journal, year, DOI) | `bb6fc36` | 🟢 |
| Tooling | MINERVA preflight checklist (repurposed as v1.0 readiness check) | `26e0854` | 🟢 |
| 2.w6-8 | SSc Tier-1 species stubs auto-generated per module (88 stubs) | `b1d2352` | 🟡 |
| 4.w17 | F2 + F3 preview figures rendered | `7cbea7a` | 🟢 |
| 4 | Whitfield bulk overlay notebook stubs | `13e337a` | 🟢 |
| 5 | ACR abstract scaffold from analyses | `13e337a` | 🟢 |
| ROADMAP pivot | This rewrite + co-author lock + Zenodo target | (this batch) | 🟢 |
| Bundle | `.zenodo.json` + `scripts/release_prep.py` + `make release` | (this batch) | 🟢 |

**Volumetric checkpoint:** 385 unique species, 175 reactions, 17 compartments, 355 PMIDs across 5 imports + integrated map. Comfortable headroom relative to the 200–300 / 300–450 target band.

---

## v1.0 release definition

A clean GitHub release tagged `v1.0` (auto-DOI'd via the Zenodo↔GitHub webhook), containing:

1. **`curation/celldesigner/SSc_MIM_integrated.xml`** — the integrated map. SBML L2v4, CellDesigner-openable, MI2CAST-annotated, passes `validate_sbml` and `minerva_preflight` (no blocking failures).
2. **`curation/celldesigner/ssc_additions_template/*.xml`** — 88 SSc Tier-1 species stubs (whether or not they've been wired into the integrated map by `v1.0`).
3. **`curation/annotations/`** — species_annotations.tsv (385 rows), reaction_evidence.tsv (≥159 rows with PMIDs), pubmed_corpus.bib (361 entries; 358 fully filled).
4. **`analysis/network/`** — centrality.tsv, hubs.tsv, communities.tsv, sink_connectivity.tsv, summary.json.
5. **`figures/`** — F2 + F3 (final or preview), F1 placeholder until a render exists.
6. **`docs/`** — scoping notes, curation guidelines, MI2CAST checklist, module specs, crosstalk matrix, omics decision, risk register, import pilot notes.
7. **`scripts/`** — all 13 automation scripts and the `Makefile` so a fresh clone reproduces everything via `make auto`.
8. **`STATUS.md`** + **`ROADMAP.md`** + **`README.md`** + **`CITATION.cff`** (with REPLACE_ME placeholders filled) + **`.zenodo.json`** for the metadata Zenodo reads on tag.

**Release acceptance criteria:**

- `make auto` runs end-to-end clean on a fresh clone.
- `make preflight` returns 0 (no blocking failures); advisories acceptable.
- `git status` clean.
- `CITATION.cff` and `.zenodo.json` have no `REPLACE_ME` strings.
- Sink connectivity dangling fraction has dropped from 33 % (today) — target ≤ 15 % after the SSc Tier-1 wiring round.

---

## What's left

### Phase 2 (curation) — remaining

| Day | Step | Lane | Status |
|-----|------|------|--------|
| 6–8 | **SSc-specific Tier-1 wiring in CellDesigner** | 🟡 + 🔴 | 88 stubs auto-generated; co-author wires the reactions |
| 9–10 | **MI2CAST annotation review** | 🟡 | 159 rows pre-filled; co-author validates ECO codes + PMID relevance |
| 11–12 | **Quality pass** | 🟢 | `make preflight`, `make sink-check`; one-shot, runs in seconds |
| 13–14 | **Buffer / write-up** of the as-built module | 🟡 | |

### Phase 3 (integration + Zenodo release) — replaces MINERVA-centric Phase 3

| Step | Lane | Status |
|------|------|--------|
| Integrate the 5 harmonised XMLs | 🟢 | ✅ done |
| Cross-module species dedupe | 🟢 | ✅ done (14 dedupes) |
| Crosstalk inventory | 🟡 | scaffolded (14 edges); co-author validates each |
| One round of co-author review | 🔴 | kickoff meeting + 2 follow-ups |
| Network analysis + sink connectivity | 🟢 | ✅ done |
| **Zenodo release prep** | 🟢 | this batch (`scripts/release_prep.py`) |
| **`v1.0` git tag** | 🔴 | one command; user-driven |
| Zenodo DOI propagation | 🟢 | webhook-driven, 1–2 days |

### Phase 4 (translational use case + figures) — unchanged

| Step | Lane | Status |
|------|------|--------|
| Download + QC + cluster Tabib scRNAseq | 🟢 | notebook stubs in place |
| Per-cluster DEG (SSc vs HC) | 🟢 | stub `03_deg.ipynb` |
| Project DEGs onto MIM | 🟢 | stub `04_projection.ipynb` |
| Per-donor module scores | 🟢 | stub `05_scoring.ipynb` |
| Druggable hub prioritisation (DGIdb + Open Targets) | 🟢 | stub `06_drug_targets.ipynb` |
| Whitfield bulk overlay (complementary) | 🟢 | stub `01–03_*.ipynb` |
| Figure F2 — overlay heatmap | 🟢 | placeholder rendered; real data lands here |
| Figure F3 — druggable subnetwork | 🟢 | preview rendered |
| Figure F1 — composite global view | 🟡 | render from integrated SBML (no MINERVA needed) |

### Phase 5 (writing + ACR submission)

| Step | Lane | Status |
|------|------|--------|
| ACR abstract scaffold | 🟢 | ✅ generated with real numerics; co-author + lead curator polish |
| Co-author iteration | 🔴 | |
| ACR portal submission | 🔴 | by 22 Sep 12:00 ET |
| Full manuscript draft for Frontiers in Bioinformatics / npj Sys Biol Appl | 🟡 | abstract → outline → expansion |

### Phase 6 — post-publication / stretch (no longer blocking)

| Step | Lane | Status |
|------|------|--------|
| MINERVA Luxembourg curator role request | 🔴 | optional |
| MINERVA deployment with semantic zoom + overlays | 🔴 | optional |
| WikiPathways EndMT correct ID lookup | 🔴 | optional |
| BioModels deposit | 🟢 | optional, auto-bundled by Zenodo |
| v1.x corrections / extensions (lung, GI, vascular peripheries) | 🟡 + 🔴 | optional |

---

## Revised milestone calendar

| # | Milestone | Original date | Revised | Lane | Status |
|---|-----------|---------------|---------|------|--------|
| M0 | Stack + repo skeleton | 14 May | 15 May | 🟢 | ✅ |
| M1 | Scope locked, **co-author signed on** | 5 Jun | **16 May** | 🔴 | ✅ **locked** |
| M2–M5 | Module imports | 19 Jun – 31 Jul | **15 May** | 🟢 | ✅ |
| M5.5 | Integrated MIM (auto-merged) | n/a | **16 May** | 🟢 | ✅ |
| M5.6 | Network analysis + sink connectivity | week 14 | **16 May** | 🟢 | ✅ |
| M6 | Integrated MIM with SSc-specific crosstalk (88 stubs wired) | 14 Aug | **15 Jul** (target) | 🟡 + 🔴 | scaffolded |
| M7 | Co-author review round | 21 Aug | **31 Jul** (target) | 🔴 | scheduled |
| **M8 (new)** | **v1.0 release on GitHub + Zenodo DOI** | n/a | **31 Aug** (target) | 🟢 + 🔴 | ready when M6/M7 land |
| ~~M8old~~ | ~~MINERVA deployment~~ | ~~21 Aug~~ | **moved to Phase 6 (post-pub)** | 🔴 | optional |
| M9 | Omics overlay computed, figures drafted | 11 Sep | **7 Sep** | 🟢 | partial |
| M10 | Abstract submitted to ACR | ≤22 Sep 12:00 ET | unchanged | 🔴 | scheduled |
| M11 | Full manuscript draft circulated | 30 Nov | unchanged | 🟡 + 🔴 | scheduled |
| M12 (new) | MINERVA deployment (optional) | n/a | post-Nov 2026 | 🔴 | stretch |

**Take-away:** the calendar's binding constraint has shifted from "rheumatologist availability" (resolved) to "co-author bandwidth in July–August for the Tier-1 wiring + review". That is now the principal scheduling watch-point.

---

## Go / no-go gates — updated

| Gate | Date | Question | If yes | If no |
|------|------|----------|--------|-------|
| ~~G1~~ | ~~24 Jul~~ | (auto-skipped — imports done in week 1) | | |
| G1.5 | **already passed** | Co-author signed on the scope? | (proceed) | (n/a — done) |
| G2 | 31 Jul 2026 | Co-author review of integrated map (with SSc Tier-1 wired) complete? | proceed to v1.0 tag | tag v0.9; review can iterate post-tag |
| **G3 (new)** | **24 Aug 2026** | `make preflight` clean + working tree green? | `git tag v1.0 && git push --tags` — Zenodo mints DOI | fix and retry |
| G4 | 11 Sep 2026 | Omics overlay produces a clinically-readable F2? | proceed to abstract polish | submit with figure caveat |
| G5 | 18 Sep 2026 | Abstract co-author sign-off? | submit ≤ 21 Sep | push to EULAR 2027 |

---

## Risk register — updated

| Risk | Original level | New level | Why |
|------|----------------|-----------|-----|
| R1 — Curation slower than planned | high | **medium-low** | Imports + harmonisation done; only SSc Tier-1 wiring remains |
| R2 — Reactome → CellDesigner incompatibilities | medium | **low** | Verified on 5 pathways |
| R3 — Late expert validation | medium | **low** | Co-author locked; calendar booking is the only thing left |
| R4 — "Wow factor" for ACR clinician reviewer | medium | unchanged | Mitigated by F2 + F3 + Zenodo DOI |
| R5 — Still "preliminary" at submission | low–medium | **low** | Late-breaking track tolerates it; overlay auto-runs |
| R6 — Reproducibility regression | medium | **low** | environment.yml pinned, CI green, `make auto` end-to-end |
| R7 — Data licensing / GEO availability | low | unchanged | |
| ~~R8 — Tooling drift on MINERVA~~ | ~~low~~ | **closed for v1.0** | MINERVA off the critical path |
| R9 — Automation drift from biology | medium | unchanged | JSON reports + co-author review catch this |
| **R10 (new) — Zenodo DOI propagation delay** | n/a | **low** | Webhook-driven, 1–2 days after tag; mitigation: tag ≥ 1 week before ACR deadline (target 24 Aug for a 22 Sep submission) |
| **R11 (new) — Co-author bandwidth in July–August** | n/a | **medium (binding constraint)** | Book the kickoff + 2 review sessions on the calendar now; share STATUS.md as the brief |

---

## Open external items (handover queue, after pivot)

These are the **only** things between the project and the v1.0 release:

1. **Co-author kickoff** — 1 h walkthrough of STATUS + F2/F3 preview + the 88 SSc Tier-1 stubs. Book ASAP.
2. **CellDesigner GUI work** — open `SSc_MIM_integrated.xml` + the 4 `ssc_additions_template/*.xml`; visual round-trip; wire the stubs into the integrated map; save as `SSc_MIM_integrated.xml` (or v0.9 file then promote). Estimated 2–3 days of curator time.
3. **CITATION.cff** + **`.zenodo.json`** REPLACE_ME placeholders — user has the metadata (name, ORCID, repo URL, co-author entry).
4. **GitHub → Zenodo webhook** — one-time toggle on `zenodo.org` (link account, enable the repo). Free, no curator role needed.
5. **Three seed BibTeX TODOs** — Aghakhani 2020 (CaSQ), Singh 2020 (RA-map), Tabib 2021 (skin scRNAseq) — manual PMID lookup. 5 minutes per entry on PubMed.
6. **`git tag v1.0 && git push --tags`** — one command, user-driven, when the co-author signs off.

Items removed from this queue by the pivot:
- ~~MINERVA Luxembourg curator role~~ — post-publication
- ~~WikiPathways EndMT correct ID~~ — nice-to-have, not blocking
- ~~ACR portal account~~ — Phase 5 only, not on the curation path

---

## How to drive the project from here

```bash
# Everything autonomous, fresh-clone friendly
make auto                              # full AUTO lane in one go
make preflight                         # v1.0 readiness gate
make release                           # CHANGELOG + tag command preview

# Per-step targets (see `make help` for the full list)
make integrate pmids crosstalk network sink-check abstract figures
```

`make auto` is idempotent: re-running it reproduces a deterministic state from `curation/imports/*/*/*.harmonised.xml` onwards.

The v1.0 release is one `git tag` away once the co-author signs off — every other step is automated.

---

*Last revised: 2026-05-16, post-pivot (GitHub + Zenodo as primary delivery; MINERVA moved post-publication).*
