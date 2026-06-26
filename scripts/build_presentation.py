#!/usr/bin/env python3
"""Build the single unified SSc-MIM slide deck as a PDF.

This replaces the three ad-hoc python-pptx decks (overview / construction /
validation-endotypes) and their combined PDF with ONE reproducible, data-current
presentation. No PowerPoint round-trip: the deck is authored in Markdown
(`docs/presentation.md`), one slide per `---` separator, and rendered straight to
PDF with WeasyPrint (the same engine `build_manuscript_pdf.py` uses for the
manuscript). Figures are referenced by repo-relative path and resolved via
``base_url``.

Run:
    python3 scripts/build_presentation.py        # or: make presentation
"""
from __future__ import annotations

from pathlib import Path

import markdown as md
from weasyprint import HTML, CSS

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs/presentation.md"
OUT = ROOT / "docs/SSc_MIM_presentation.pdf"

CSS_TEXT = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Helvetica Neue", Arial, sans-serif; color: #1a2230; }

section.slide {
    page-break-after: always;
    width: 297mm; height: 209mm;          /* A4 landscape, minus a hair to avoid overflow */
    padding: 14mm 18mm;
    position: relative;
    overflow: hidden;
    border-top: 7mm solid #1f4e79;
}
section.slide:last-child { page-break-after: auto; }

h1 { font-size: 30pt; color: #1f4e79; margin: 6mm 0 4mm; line-height: 1.1; }
h2 { font-size: 21pt; color: #1f4e79; margin: 0 0 5mm; line-height: 1.15;
     border-bottom: 1.5pt solid #c7d7e8; padding-bottom: 2mm; }
h3 { font-size: 14pt; color: #2e6ca4; margin: 4mm 0 2mm; }
p, li { font-size: 13pt; line-height: 1.4; }
ul { margin: 2mm 0 2mm 0; padding-left: 7mm; }
li { margin-bottom: 1.5mm; }
strong { color: #14304a; }
em { color: #555; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 10.5pt;
       background: #eef3f8; padding: 0.5mm 1mm; border-radius: 2px; }
a { color: #1f4e79; text-decoration: none; }

table { border-collapse: collapse; margin: 3mm 0; font-size: 11.5pt; width: 100%; }
th { background: #1f4e79; color: #fff; text-align: left; padding: 2mm 3mm; }
td { border-bottom: 0.5pt solid #c7d7e8; padding: 1.6mm 3mm; }
tr:nth-child(even) td { background: #f3f7fb; }

img { max-width: 100%; max-height: 132mm; display: block; margin: 3mm auto; }

.subtitle { font-size: 15pt; color: #2e6ca4; margin-top: 2mm; }
.footer { position: absolute; bottom: 7mm; left: 18mm; right: 18mm;
          font-size: 9pt; color: #8a98a8; border-top: 0.5pt solid #d8e2ee;
          padding-top: 1.5mm; display: flex; justify-content: space-between; }
.cols { display: flex; gap: 9mm; }
.cols > div { flex: 1; }
.big { font-size: 17pt; }
.lead { font-size: 14pt; color: #2e6ca4; margin-bottom: 3mm; }

/* Title slide */
section.title { border-top: 7mm solid #1f4e79; }
section.title h1 { font-size: 34pt; margin-top: 38mm; }
section.title .meta { position: absolute; bottom: 18mm; left: 18mm; right: 18mm;
                      font-size: 12pt; color: #43596f; }
"""

FOOTER = (
    '<div class="footer"><span>SSc-MIM — molecular interaction map of diffuse '
    'cutaneous systemic sclerosis</span><span>{n}</span></div>'
)


def main() -> int:
    raw = SRC.read_text(encoding="utf-8")
    # Slides are separated by a line containing only "---".
    chunks = [c.strip() for c in raw.split("\n---\n")]
    chunks = [c for c in chunks if c]

    slides_html = []
    for i, chunk in enumerate(chunks):
        cls = "slide title" if i == 0 else "slide"
        body = md.markdown(
            chunk,
            extensions=["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"],
            output_format="html5",
        )
        foot = "" if i == 0 else FOOTER.format(n=f"{i+1} / {len(chunks)}")
        slides_html.append(f'<section class="{cls}">{body}{foot}</section>')

    html_doc = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>SSc-MIM presentation</title></head><body>"
        + "\n".join(slides_html)
        + "</body></html>"
    )

    HTML(string=html_doc, base_url=str(ROOT)).write_pdf(
        OUT, stylesheets=[CSS(string=CSS_TEXT)]
    )
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB, {len(chunks)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
