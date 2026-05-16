# Crosstalk matrix — SSc-MIM

> Auto-generated from `docs/module_specs/M*.md` "Crosstalk edges" sections by
> `scripts/generate_crosstalk_scaffold.py`. Hand-edit only the **status** and
> **notes** columns — anything else will be overwritten on re-run.

## Conventions

- Source / target are the four sub-modules: M1 (IFN-I), M2 (TGF-β / fibrosis),
  M3 (EndoMT / vasculopathy), M4 (IL-6 / Th2 / B-cell).
- *Mechanism* is the spec's prose verbatim.
- *Status*: `declared` (in a spec, not yet built) → `scaffolded` (placeholder
  exists in CellDesigner) → `curated` (full SBGN reaction + MI2CAST).
- Use the GitHub issue `curation_request` template to track work on any row.

## Edges


| # | source | target | mechanism | status | notes |
|---|--------|--------|-----------|--------|-------|
| 1 | M1 | M2 | IFN-I priming of fibroblast pro-fibrotic state. | declared |  |
| 2 | M1 | M2 | CXCL4 / PF4-mediated fibroblast activation (autocrine on IFN-stimulated DCs). | declared |  |
| 3 | M1 | M4 | IFN-I → plasmacytoid DC → B-cell class-switch. | declared |  |
| 4 | M1 | M2 | IFN-I primes fibroblast pro-fibrotic transcriptional state. | declared |  |
| 5 | M3 | M2 | EndoMT-derived perivascular fibroblasts increase the myofibroblast pool. | declared |  |
| 6 | M4 | M2 | IL-6 / STAT3 and IL-4 / IL-13 / STAT6 augment ECM transcription. | declared |  |
| 7 | M2 | M3 | TGF-β drives endothelial-to-mesenchymal transition. | declared |  |
| 8 | M2 | M3 | TGF-β drives EndMT (TGFBR1 → SMAD3 + non-canonical → SNAI1/SNAI2). | declared |  |
| 9 | M1 | M3 | IFN-I → endothelial activation and microvascular damage (cite SSc-specific evidence). | declared |  |
| 10 | M3 | M2 | perivascular fibroblast emergence feeds the myofibroblast pool. | declared |  |
| 11 | M3 | M4 | endothelial chemokines (CXCL10, CXCL11) recruit Th1/Th2. | declared |  |
| 12 | M1 | M4 | IFN-I → pDC / B-cell class switching. | declared |  |
| 13 | M4 | M2 | IL-6 / STAT3 → fibroblast pro-fibrotic transcription; IL-4 / IL-13 / STAT6 → ECM transcription. | declared |  |
| 14 | M4 | M3 | endothelial chemokines (covered in M3); B-cell-driven endothelial inflammation. | declared |  |

_14 edge(s) auto-extracted from 4 module spec(s)._
