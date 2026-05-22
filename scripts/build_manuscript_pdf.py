#!/usr/bin/env python3
"""Compile manuscript/SSc_MIM_manuscript_draft.md to PDF with figures.

Pipeline:
  1. Read the source markdown.
  2. Replace every ``**[Figure N: ...]**`` placeholder with a real
     ``<figure>`` block referencing the matching PNG under figures/.
     The placeholder's existing caption is preserved verbatim.
  3. Convert markdown to HTML via python-markdown (tables, fenced
     code, attr_list extensions enabled).
  4. Wrap in a journal-style HTML shell with embedded CSS.
  5. Render to PDF via WeasyPrint (full CSS + image support).

Output:
  manuscript/SSc_MIM_manuscript_v1.1.pdf
"""
from __future__ import annotations

import re
from pathlib import Path

import markdown as md
from weasyprint import HTML, CSS

SRC = Path("manuscript/SSc_MIM_manuscript_draft.md")
OUT = Path("manuscript/SSc_MIM_manuscript_v1.1.pdf")

FIG_RE = re.compile(
    r"\*\*\[((?:Supplementary\s+)?Figure[^:\]]*?:\s*[^]]*?)\]\*\*",
    flags=re.DOTALL,
)
SVG_NAME_RE = re.compile(r"`figures/([^`]+?)\.svg`")


def expand_figure_placeholders(md_text: str) -> tuple[str, int]:
    n = 0

    def _sub(m: re.Match) -> str:
        nonlocal n
        block = m.group(1)
        svg_match = SVG_NAME_RE.search(block)
        if not svg_match:
            return m.group(0)
        stem = svg_match.group(1)
        png = Path("figures") / f"{stem}.png"
        if not png.exists():
            return m.group(0)
        n += 1
        caption = block.replace("\\*", "*").strip()
        return (
            f'\n\n<figure>\n'
            f'<img src="{png.resolve().as_uri()}" alt="{stem}" />\n'
            f'<figcaption><b>{caption}</b></figcaption>\n'
            f'</figure>\n\n'
        )

    return FIG_RE.sub(_sub, md_text), n


HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""

CSS_TEXT = """
@page {
  size: A4;
  margin: 22mm 18mm 22mm 18mm;
  @bottom-center {
    content: "SSc-MIM v1.1 — page " counter(page) " / " counter(pages);
    font-family: 'Liberation Serif', 'Times New Roman', serif;
    font-size: 8.5pt;
    color: #666;
  }
}
body {
  font-family: 'Liberation Serif', 'Times New Roman', serif;
  font-size: 10.5pt;
  line-height: 1.42;
  color: #111;
}
h1 { font-size: 16pt; margin: 1.4em 0 0.4em; }
h2 {
  font-size: 13pt;
  margin: 1.2em 0 0.5em;
  border-bottom: 1px solid #999;
  padding-bottom: 2px;
}
h3 { font-size: 11.5pt; margin: 1.0em 0 0.4em; }
h4 { font-size: 11pt; margin: 0.9em 0 0.3em; }
p  { text-align: justify; margin: 0.45em 0; }
hr { border: none; border-top: 1px solid #aaa; margin: 1.0em 0; }
ul, ol { margin: 0.4em 0 0.4em 1.2em; }
li { margin: 0.15em 0; }
table {
  border-collapse: collapse;
  margin: 0.6em 0;
  font-size: 9.5pt;
  width: 100%;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #999;
  padding: 3px 6px;
  vertical-align: top;
}
th { background: #efefef; }
code {
  font-family: 'Liberation Mono', 'Courier New', monospace;
  font-size: 9pt;
  background: #f3f3f3;
  padding: 0 3px;
  border-radius: 2px;
}
pre {
  font-family: 'Liberation Mono', 'Courier New', monospace;
  font-size: 8.5pt;
  background: #f6f6f6;
  border-left: 3px solid #ccc;
  padding: 6px 10px;
  white-space: pre-wrap;
  page-break-inside: avoid;
}
blockquote {
  margin: 0.6em 0;
  padding: 0.2em 0.8em;
  border-left: 3px solid #888;
  color: #444;
  font-style: italic;
}
figure {
  margin: 1.2em 0;
  page-break-inside: avoid;
  text-align: center;
}
figure img {
  max-width: 95%;
  max-height: 17cm;
  border: 1px solid #ddd;
  padding: 2px;
  background: white;
}
figcaption {
  font-size: 9pt;
  margin-top: 6px;
  text-align: justify;
  color: #222;
  padding: 0 1em;
}
"""


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    new_md, n_figs = expand_figure_placeholders(src)
    print(f"expanded {n_figs} figure placeholders")

    html_body = md.markdown(
        new_md,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"],
        output_format="html5",
    )
    title = ("SSc-MIM v1.1 — A Curated, SBGN-Compliant Molecular "
             "Interaction Map of Skin Fibrosis in Diffuse Cutaneous "
             "Systemic Sclerosis")
    html_doc = HTML_SHELL.format(title=title, body=html_body)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc, base_url=str(Path.cwd())).write_pdf(
        OUT,
        stylesheets=[CSS(string=CSS_TEXT)],
    )
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
