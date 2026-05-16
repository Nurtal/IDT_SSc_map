# SSc-MIM — Brief co-auteur

**Date :** 16 mai 2026
**Pour :** [nom co-auteure]
**De :** Nathan Foulquier
**Format demandé :** revue de scope, **30–45 min**, async ou en visio selon ta préférence.
**Avant la discussion :** les 3 questions en fin de doc, et idéalement un coup d'œil aux figures F2 / F3 jointes.

---

## 1. Contexte en deux lignes

Pas de Molecular Interaction Map (MIM) curé et SBGN-compliant pour la SSc à ce jour, alors qu'il en existe pour la PR (RA-map), Sjögren (SjD map), COVID, Parkinson, etc. Je propose de combler ce trou avec un **premier module ciblé sur la fibrose cutanée en dcSSc**, hébergé sur GitHub + Zenodo (DOI citable), avec couche d'overlay single-cell Tabib 2021. **Cible :** abstract late-breaking ACR Convergence 2026 (deadline 22 sept).

## 2. Où on en est concrètement (état au 16 mai)

Le scaffolding est posé et l'automatisable est fait :

| Quoi | Volume | État |
|------|--------|------|
| Imports Reactome harmonisés (M1 IFN-α/β, M2 TGF-β SMADs + PDGF, M3 NOTCH1, M4 IL-6) | 399 species → 385 uniques après dedupe cross-module | ✅ |
| Carte intégrée `SSc_MIM_integrated.xml` | 385 species, 175 reactions, 17 compartments | ✅ |
| Réactions annotées MI2CAST avec PMIDs | 158 / 159 avec citation, 355 PMIDs uniques mineés et bib auto-rempli (titre, auteurs, journal) via E-utils | ✅ |
| Analyse réseau (centralité, top hubs, communautés) | top hubs cohérents biologiquement (ISGF3, TGFB1:TGFBR2, PDGFR dimer, ISG signature…) | ✅ |
| 4 modules avec Tier-1 SSc-spécifiques scaffoldés en stubs CellDesigner | 88 species placeholder prêts à câbler | 🟡 à faire |
| Pipeline reproductible | `make auto` end-to-end depuis les imports bruts | ✅ |

**Sinks de phénotype** (sortie biologique de la carte) : myofibroblast activation, ECM deposition, vascular remodeling, ISG signature. Règle modélisation : tout species Tier-1 doit atteindre un sink en ≤ 6 steps. Vérifié sur la carte actuelle : **0 violation** ; 126 species "dangling" qui correspondent exactement au backlog Tier-1 à câbler (essentiellement les sinks M2 ECM/myofibroblast et M4 STAT3-outputs).

**Figures :**
- `figures/F3_druggable_targets.png` — sous-réseau des top-20 hubs coloré par module (preview, données réelles)
- `figures/F2_overlay_by_subtype.png` — placeholder de heatmap per-donor × per-module pour montrer le format final (sera rempli avec Tabib en phase 4)

## 3. Ce que je te demande, concrètement

**Bloc 1 — Revue de scope (30 min)**
Valider que le 4-module + sinks tient pour la fibrose cutanée dcSSc, et identifier ce qu'il manque/dépasse côté Tier-1 SSc-spécifique.

**Bloc 2 — Deux créneaux d'1h sur juillet-août**
Le premier (fin juillet) pour review du Tier-1 câblé en CellDesigner. Le second (mi-août) pour validation pré-tag v1.0 sur Zenodo.

**Bloc 3 — Co-author entry** sur la publication ACR + le papier méthodo associé (Frontiers in Bioinformatics ou npj Systems Biology and Applications selon ton avis, cf. Q3 ci-dessous).

## 4. Les 3 questions à trancher

### Q1 — Scope : le 4-module tient-il ?

Modules actuels :
- **M1** IFN-I / IFNAR / JAK-STAT / ISG signature
- **M2** TGF-β / SMAD / fibroblast → myofibroblast / ECM
- **M3** EndoMT et vasculopathie (Notch + endothéline + NO/sGC + HIF)
- **M4** IL-6 + IL-4/IL-13 + B cell + autoAb output

> **Ta réponse :**
> - [ ] OK tel quel
> - [ ] OK mais déplacer X de Mn à Mp
> - [ ] Fusionner deux modules (lesquels ?)
> - [ ] Ajouter un 5e module (lequel ? complément innate / Th17 / complement / autre ?)

### Q2 — Tier-1 SSc : quoi ajouter, quoi retirer ?

Les Tier-1 actuels (= à câbler en CellDesigner par dessus l'import Reactome) listés dans `docs/module_specs/M*.md`. Aperçu rapide :

- **M1 :** CXCL4/PF4, IRF7, cGAS/STING, RIG-I/MAVS, TLR3/7/8/9, USP18, SOCS1, PTPN1/2
- **M2 :** TGF-β latent (LAP, LTBP1, ITGAV:ITGB6/B3, THBS1), POSTN, COMP, CTGF/CCN2, TNC, LOX/LOXL2, FRA-2 (FOSL2), TBX2, YAP/TAZ, PDGFs
- **M3 :** EDN1/EDNRA/EDNRB, eNOS/sGC/cGMP/PDE5, HIF1A, VEGFA/KDR, Notch ligands JAG1/2 DLL1/4, SNAI1/2 ZEB1/2 TWIST1, CDH5 → CDH2 transition, ANGPT1/2
- **M4 :** IL-4, IL-13, IL-4Rα, IL-13Rα1, STAT6, GATA3/TBX21/FOXP3/RORC, CD19/CD20/CD22/BCR kinases, CD40/CD40L, PRDM1/XBP1/IRF4, BAFF/APRIL, autoAb Topo-I / RNApol-III / ACA

> **Ta réponse :** liste des entités/réactions à
> - **ajouter** (avec PMID si tu as) :
> - **retirer** (déjà dans la liste mais peu pertinent à ton avis) :
> - **promouvoir** Tier-2 → Tier-1 :

### Q3 — Ambition : ACR seul, ou ACR + papier méthodo en parallèle ?

Option A : **ACR abstract uniquement** (22 sept). Tape sur la nouveauté du resource + use case Tabib. Papier méthodo plus tard, 2027.
Option B : **ACR + papier méthodo en parallèle** (Frontiers Bioinformatics ou npj Sys Biol App). Plus de travail à 2 mois mais l'abstract devient "in press paper" à présenter au congrès = beaucoup plus de visibilité.
Option C : **Papier méthodo d'abord, ACR 2027 ensuite** (fallback explicite dans la ROADMAP) si l'agenda ne le permet pas.

> **Ta réponse :**
> - [ ] A — ACR only, papier en 2027
> - [ ] B — Les deux en parallèle (rythme tendu)
> - [ ] C — Papier en priorité, ACR pushé à 2027

## 5. Pour aller plus loin (totalement optionnel)

- **Repo GitHub :** `https://github.com/Nurtal/IDT_SSc_map` (public)
- **Snapshot état projet :** `STATUS.md` à la racine
- **Plan détaillé :** `ROADMAP.md` à la racine — section "Pivot" explique pourquoi on cible GitHub+Zenodo au lieu de MINERVA Luxembourg
- **Spécifs par module :** `docs/module_specs/M*.md` (la base à challenger)
- **Crosstalk inter-module :** `docs/crosstalk_matrix.md` (14 edges auto-extraites — à valider)

Je peux te générer un export PDF de tout ça si plus pratique à lire.

---

**Côté pratique :** dis-moi simplement quand t'es dispo (visio 30 min ou réponses async par email, les deux marchent). Je peux travailler sur les commentaires des Tier-1 dès que je les ai.

Merci.
