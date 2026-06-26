#!/usr/bin/env python3
"""Generate a self-contained static HTML review app from the interaction database.

Reads analysis/curation/interaction_database.csv and emits review/index.html with the data
embedded as JSON (no server, no CDN, no fetch — works by double-clicking the file). The reviewer
adjudicates interactions one at a time in a swipe-based "Tinder-like" deck: each card shows
regulator->target, mechanism, SSc relevance, evidence level, the verbatim deciding sentence, the
source article (title + PubMed/DOI), and the AI recommendation. Swipe / arrow-right to accept
(keep in map, or re-include a discarded one), left to reject; skip, undo, and annotate are also
available. Decisions persist in localStorage and export to CSV/JSON.

Run: python3 scripts/build_review_app.py   (or make review-app)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "analysis/curation/interaction_database.csv"
OUT = ROOT / "review/index.html"
# Local directory holding the <pmid>.pdf full texts, so the app can deep-link "open PDF at page N".
ARTICLE_DIR = Path("/home/drfox/data/IDT_SSc_map/article")

try:  # share the symbol->synonym map with the quote miner so colours catch the same names
    from mine_pdf_quotes import SYN
except Exception:  # noqa: BLE001 — keep the generator usable even if PyMuPDF is missing
    SYN = {}

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SSc-MIM — interaction review</title>
<style>
:root{--bg:#0d1117;--bg2:#0f1419;--card:#1a2230;--card2:#212c3d;--mut:#8a97a8;--fg:#e6edf3;
 --bd:#2b3440;--accent:#4493f8;--green:#3fb950;--red:#f85149;--amber:#d29922;--grey:#6e7681;--purple:#a371f7}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;font:14px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);
 background:radial-gradient(1100px 560px at 50% -8%,#16202e 0,var(--bg) 62%);overflow:hidden}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
button{font:inherit;cursor:pointer;border-radius:8px;border:1px solid var(--bd);background:var(--card);color:var(--fg);padding:7px 12px}
button:hover{border-color:var(--accent)}
.app{display:flex;flex-direction:column;height:100vh;max-width:1180px;margin:0 auto;padding:0 16px}
.cols{flex:1;min-height:0;display:grid;grid-template-columns:minmax(400px,1fr) minmax(340px,.92fr);gap:16px}
.left{display:flex;flex-direction:column;min-height:0}
.preview{display:flex;flex-direction:column;min-height:0;background:linear-gradient(180deg,var(--card2),var(--card));
 border:1px solid var(--bd);border-radius:18px;overflow:hidden;margin:4px 0 6px}
.pv-head{display:flex;align-items:center;gap:8px;padding:12px 16px 8px;font-size:12px;text-transform:uppercase;
 letter-spacing:.05em;color:var(--mut)}
.pv-head b{color:var(--fg);text-transform:none;letter-spacing:0;font-size:13px}
.pv-ctl{display:flex;gap:4px;margin-left:8px}
.pv-ctl button{padding:1px 7px;font-size:13px;line-height:1.4;border-radius:6px;min-width:24px}
.pv-canvas{flex:1;min-height:0;position:relative}
.pv-canvas svg{position:absolute;inset:0;width:100%;height:100%;cursor:grab;touch-action:none}
.pv-tip{margin-left:auto;color:var(--grey)}
.pv-empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--grey);font-size:13px;text-align:center;padding:20px}
.pv-edge{stroke:#3a4453;stroke-width:1.4;fill:none}
.pv-edge.cur{stroke:var(--accent);stroke-width:2.6}
.pv-hit{stroke:transparent;stroke-width:12;fill:none;cursor:pointer}
.pv-node circle{stroke:#0d1117;stroke-width:1.5}
.pv-node text{font:600 10.5px system-ui;fill:var(--mut);paint-order:stroke;stroke:#0d1117;stroke-width:3px;stroke-linejoin:round}
.pv-node.cur text{fill:var(--fg);font-size:12px}
.pv-legend{display:flex;flex-wrap:wrap;gap:10px;padding:8px 16px 12px;border-top:1px solid var(--bd);font-size:11.5px}
.pv-legend span{display:inline-flex;align-items:center;gap:5px;color:var(--mut)}
.pv-legend i{width:10px;height:10px;border-radius:50%;display:inline-block}
@media(max-width:860px){.cols{grid-template-columns:1fr}.preview{display:none}}
.top{display:flex;align-items:center;gap:10px;padding:14px 2px 8px}
.top h1{font-size:15px;margin:0;font-weight:700;letter-spacing:.02em}
.top h1 small{color:var(--mut);font-weight:400;margin-left:6px;font-size:12px}
.top .spacer{flex:1}
.iconbtn{padding:6px 10px;font-size:13px}
.iconbtn.danger{color:var(--red);border-color:#5a1f1f}.iconbtn.danger:hover{border-color:var(--red);background:#2a0f0f}
.progwrap{padding:2px 2px 8px}
.progbar{height:6px;border-radius:999px;background:var(--card);overflow:hidden}
.progbar>div{height:100%;width:0;background:linear-gradient(90deg,var(--green),var(--accent));transition:width .3s}
.progmeta{display:flex;justify-content:space-between;font-size:11.5px;color:var(--mut);margin-top:5px}
.progmeta b{color:var(--fg)}
.filters{display:none;gap:8px;flex-wrap:wrap;background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px;margin-bottom:8px}
.filters.open{display:flex}
.filters input,.filters select{flex:1;min-width:130px;padding:7px;background:var(--bg2);color:var(--fg);border:1px solid var(--bd);border-radius:7px}
.deck{position:relative;flex:1;min-height:0;margin:4px 0 6px}
.card{position:absolute;inset:0;background:linear-gradient(180deg,var(--card2),var(--card));border:1px solid var(--bd);
 border-radius:18px;box-shadow:0 18px 50px -22px #000c;display:flex;flex-direction:column;overflow:hidden;
 will-change:transform;touch-action:pan-y;transition:transform .25s ease,opacity .25s ease}
.card.top{cursor:grab}.card.top:active{cursor:grabbing}
.card .body{flex:1;overflow:auto;padding:18px 20px 10px}
.card .body::-webkit-scrollbar{width:8px}.card .body::-webkit-scrollbar-thumb{background:var(--bd);border-radius:8px}
.chips{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.tag{font-size:11px;padding:3px 9px;border-radius:999px;border:1px solid var(--bd);color:var(--mut);white-space:nowrap}
.tag.mod{color:var(--accent);border-color:#27466e;background:#10243a}
.tag.inmap{color:var(--green);border-color:#1f5130;background:#0f2a18}
.tag.disc{color:var(--amber);border-color:#5a4612;background:#2a2009}
.tag.warn{color:var(--red);border-color:#5a1f1f;background:#2a0f0f}
.tag.src{color:var(--purple);border-color:#3a2a5a;background:#1a1330}
.inter{font-size:23px;font-weight:700;line-height:1.25;margin:2px 0;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.node{background:#0f1722;border:1px solid var(--bd);border-radius:9px;padding:3px 11px}
.arrow{display:inline-flex;flex-direction:column;align-items:center;color:var(--mut);font-size:10.5px;font-weight:600;text-transform:lowercase}
.arrow .ln{font-size:22px;line-height:.7;color:var(--accent)}
.arrow.inhib .ln{color:var(--red)}
.subids{font-size:11px;color:var(--grey);margin:3px 0 12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.mech{font-size:15px;margin:8px 0}
.rel{color:var(--mut);font-size:13px;margin:0 0 6px}.rel b{color:#bcd0e6;font-weight:600}
.box{background:#0e151f;border:1px solid var(--bd);border-radius:12px;padding:12px 14px;margin:12px 0}
.box h3{margin:0 0 7px;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);display:flex;align-items:center;gap:8px}
.quote{border-left:3px solid var(--accent);padding:2px 0 2px 14px;font-size:15px;color:#dfeaf6;font-style:italic}
.quote.none{border-color:var(--grey);color:var(--grey);font-style:normal;font-size:13px}
.qb{font-size:10px;padding:2px 8px;border-radius:999px;border:1px solid var(--bd);color:var(--mut);font-weight:600;text-transform:none;letter-spacing:0}
.qb.pdf{color:#9cc4f0;border-color:#1f4068;background:#10243a}
.qb.ok{color:var(--green);border-color:#1f5130;background:#0f2a18}
.qb.note{color:var(--amber);border-color:#5a4612;background:#2a2009}
.qb.warn{color:var(--red);border-color:#5a1f1f;background:#2a0f0f}
.pdflink{font-size:11px;font-weight:600;margin-left:auto;text-transform:none;letter-spacing:0}
.quote .hl{font-weight:600;font-style:normal;border-radius:3px;padding:0 3px}
.inter .plus{color:var(--mut);font-weight:400}
.altq{margin-top:8px}
.altq summary{cursor:pointer;color:var(--mut);font-size:12px;list-style:none}
.altq summary:hover{color:var(--accent)}.altq summary::-webkit-details-marker{display:none}
.altq summary::before{content:"＋ ";color:var(--accent)}
.altq[open] summary::before{content:"－ "}
.altq .quote{margin-top:8px;border-left-color:var(--grey)}
.reco{font-size:15px;font-weight:600}.reco small{display:block;font-weight:400;color:var(--mut);font-size:12px;margin-top:4px;font-style:italic}
.meta-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.ev{display:inline-block;padding:3px 10px;border-radius:7px;background:#10243a;border:1px solid #1f4068;color:#9cc4f0;font-size:12px}
.refs{margin-top:8px}.refs a{display:inline-block;margin:0 14px 4px 0}
.art{font-size:13px;color:#cdd9e6}.art .yr{color:var(--mut)}
.disc-reason{color:var(--amber);font-size:13px}
.lit{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:560px){.lit{grid-template-columns:1fr}}
.lit-col h4{margin:0 0 5px;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.lit-col h4.sup{color:var(--green)}.lit-col h4.con{color:var(--amber)}
.lit ul{margin:0;padding-left:15px}
.lit li{font-size:12px;line-height:1.4;margin:4px 0;color:#cdd9e6}
.lit li .yr{color:var(--mut)}
.lit .cue{color:var(--red);border:1px solid #5a1f1f;background:#2a0f0f;border-radius:5px;padding:0 5px;font-size:10.5px;white-space:nowrap}
.verdict{margin:10px 0 4px;padding:9px 12px;border-radius:10px;border:1px solid var(--bd);border-left-width:4px;background:#0e151f}
.verdict .v-badge{display:block;font-weight:700;font-size:13px;margin-bottom:3px}
.verdict .v-rat{font-size:12.5px;color:#cdd9e6}
.verdict .v-pm a{font-family:ui-monospace,Menlo,monospace;font-size:11.5px}
.verdict.v-ok{border-left-color:var(--green)}.verdict.v-ok .v-badge{color:var(--green)}
.verdict.v-rev{border-left-color:var(--amber)}.verdict.v-rev .v-badge{color:var(--amber)}
.verdict.v-cau{border-left-color:#f0883e}.verdict.v-cau .v-badge{color:#f0883e}
.verdict.v-rej{border-left-color:var(--red)}.verdict.v-rej .v-badge{color:var(--red)}
.stamp{position:absolute;top:24px;font-size:30px;font-weight:800;letter-spacing:.06em;padding:6px 16px;border:4px solid;
 border-radius:12px;opacity:0;pointer-events:none;text-transform:uppercase;z-index:5}
.stamp.keep{left:22px;color:var(--green);border-color:var(--green);transform:rotate(-15deg)}
.stamp.drop{right:22px;color:var(--red);border-color:var(--red);transform:rotate(15deg)}
.ribbon{position:absolute;top:0;right:0;font-size:11px;font-weight:700;padding:4px 12px;border-bottom-left-radius:12px;color:#001;z-index:4}
.ribbon.confirm,.ribbon.include{background:var(--green)}.ribbon.reject{background:var(--red)}
.actions{display:flex;align-items:center;justify-content:center;gap:14px;padding:8px 0 12px}
.fab{width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;
 border-width:2px;background:var(--card);transition:transform .12s,box-shadow .2s;flex:0 0 auto;line-height:1}
.fab:hover{transform:translateY(-3px)}
.fab.sm{width:44px;height:44px;font-size:17px}
.fab.reject{color:var(--red);border-color:var(--red)}.fab.reject:hover{box-shadow:0 8px 22px -8px var(--red)}
.fab.accept{color:var(--green);border-color:var(--green)}.fab.accept:hover{box-shadow:0 8px 22px -8px var(--green)}
.fab.undo{color:var(--amber);border-color:#4a3a12}
.fab.skip{color:var(--mut)}
.fab.note{color:var(--accent);border-color:#27466e}
.fab.on{background:var(--accent);color:#001}
.notepanel{display:none;padding:0 2px 10px}.notepanel.open{display:block}
.notepanel textarea{width:100%;background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:10px;padding:10px;font:inherit;min-height:58px}
.done{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:12px;padding:30px}
.done .big{font-size:46px}.done h2{margin:0;font-size:22px}
.kbd{text-align:center;font-size:11px;color:var(--grey);padding-bottom:10px}
.kbd kbd{background:var(--card);border:1px solid var(--bd);border-radius:5px;padding:1px 6px;font-family:inherit}
@media(max-width:520px){.inter{font-size:20px}.fab{width:52px;height:52px}.kbd{display:none}}
</style></head><body>
<div class="app">
 <div class="top">
   <h1>SSc-MIM review <small id="meta"></small></h1>
   <span class="spacer"></span>
   <button class="iconbtn" onclick="toggleFilters()">⚲ Filter</button>
   <button class="iconbtn" onclick="exportCsv()">⤓ CSV</button>
   <button class="iconbtn" onclick="exportJson()">JSON</button>
   <button class="iconbtn danger" onclick="resetAll()" title="Clear all stored decisions & notes">⟲ Reset</button>
 </div>
 <div class="filters" id="filters">
   <input id="q" placeholder="Search regulator / target / gene / id / title…">
   <select id="fStatus"><option value="">status: all</option><option value="in_map">in map</option><option value="discarded">discarded</option></select>
   <select id="fMod"></select>
   <select id="fReco"></select>
   <select id="fAi"><option value="">AI call: all</option><option value="validate">✓ validate</option><option value="revise">✎ revise citation</option><option value="caution">⚠ caution</option><option value="reject">✗ reject</option></select>
   <select id="fDec"><option value="">decision: any</option><option value="__undec">— undecided only</option><option value="confirm">confirmed</option><option value="reject">rejected</option><option value="include">re-included</option></select>
 </div>
 <div class="progwrap">
   <div class="progbar"><div id="pbar"></div></div>
   <div class="progmeta"><span id="pleft"></span><span id="pright"></span></div>
 </div>
 <div class="cols">
  <div class="left">
   <div class="deck" id="deck"></div>
   <div class="notepanel" id="notepanel"><textarea id="note" placeholder="Reviewer note for this interaction…" oninput="setNote(this.value)"></textarea></div>
   <div class="actions" id="actions">
     <button class="fab undo sm" title="Undo last decision (Z)" onclick="undo()">↩</button>
     <button class="fab reject" title="Reject — not in map (← / R)" onclick="doReject()">✗</button>
     <button class="fab skip sm" title="Skip without deciding (↑)" onclick="skip()">⏭</button>
     <button class="fab note sm" title="Add a note (N)" onclick="toggleNote()">✎</button>
     <button class="fab accept" title="Accept — keep in map (→ / A)" onclick="doAccept()">✓</button>
   </div>
   <div class="kbd"><kbd>→</kbd>/<kbd>A</kbd> accept · <kbd>←</kbd>/<kbd>R</kbd> reject · <kbd>↑</kbd> skip · <kbd>Z</kbd> undo · <kbd>N</kbd> note · or drag the card</div>
  </div>
  <div class="preview" id="preview">
   <div class="pv-head">Module map · <b id="pvmod"></b><span style="flex:1"></span><span id="pvcount"></span>
    <span class="pv-ctl"><button onclick="pvFocus()" title="Zoom to this reaction">◎</button><button onclick="pvZoom(0.8)" title="Zoom in">+</button><button onclick="pvZoom(1.25)" title="Zoom out">–</button><button onclick="pvFit()" title="Fit whole module">⤢</button></span></div>
   <div class="pv-canvas" id="pvcanvas"></div>
   <div class="pv-legend" id="pvlegend"></div>
  </div>
 </div>
</div>
<script>
const DATA = /*__DATA__*/;
const KEY='sscmim_review_v1';
let store=JSON.parse(localStorage.getItem(KEY)||'{}');
let view=[], idx=0, hist=[];
const $=s=>document.querySelector(s);
const pubmed=p=>`https://pubmed.ncbi.nlm.nih.gov/${p}/`;
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cleanNames=s=>(s||'').split(';').filter(Boolean).map(x=>x.split('__')[0]).join(' + ')||'?';
const acceptKind=r=>r.inclusion_status==='discarded'?'include':'confirm';
const ARTBASE=/*__ARTBASE__*/;
const MODTITLE={M1:'Type-I IFN signalling',M2:'TGF-β / fibroblast→myofibroblast',
 M3:'EndoMT & vasculopathy',M4:'IL-6/IL-4/IL-13 cytokine axis',M5:'B-cell & autoreactivity',
 crosstalk:'inter-module crosstalk'};
const modLabel=r=>{const t=MODTITLE[r.module];return r.module?(r.module+(t?' · '+t:'')):(r.inclusion_status==='discarded'?'discarded':'—');};
function quoteBadge(qs){
 const map={'verbatim (PDF-extracted)':['pdf','📄 extracted from article PDF — verify'],
  'verbatim (PMC full-text)':['pdf','📄 extracted from PMC full-text — verify'],
  'verbatim (abstract)':['pdf','📄 extracted from PubMed abstract — verify'],
  'verbatim (discovery)':['ok','verbatim — abstract'],'verbatim (excluded)':['ok','verbatim'],
  'full-text evidence note':['note','evidence note (paraphrase)'],'to_complete':['warn','to complete']};
 const e=map[qs];return e?`<span class="qb ${e[0]}">${e[1]}</span>`:'';
}
function pdfLink(r,page){
 const p=page||r.pdf_page||1;
 return (r.quote_status==='verbatim (PDF-extracted)'&&r.pmid)
  ?`<a class="pdflink" href="${ARTBASE}${r.pmid}.pdf#page=${p}" target="_blank" rel="noopener" title="Open the source PDF at this page">↗ PDF p.${esc(String(page||r.pdf_page||'?'))}</a>`:'';
}
// HGNC symbol -> common-name regex alternatives (mirrors mine_pdf_quotes.py), so a species' colour
// also catches the synonym the article uses ("TGF-β" for TGFB1, "galectin-3" for LGALS3 …).
const SYN=/*__SYN__*/;
const PALETTE=['#4493f8','#3fb950','#d29922','#a371f7','#f0883e','#56d4dd','#f778ba','#e6c07b'];
const GEN_RX=/^(complex|active|activated|repressed|inhibited|dimer|phenotype|committed|lineage|bound|stiffened|myofibroblast|signalling|signaling|cell|ext|ecm|cyto|nuc|pm|er|endo|p|mt)$/i;
const reEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
// escape a symbol but allow an optional hyphen/space at letter<->digit boundaries, so the literal
// "IL6" also matches "IL-6", "STAT3" matches "STAT-3", etc. (gene names are hyphenated in prose).
const flexTok=t=>reEsc(t).replace(/([A-Za-z])(?=\d)/g,'$1[- ]?').replace(/(\d)(?=[A-Za-z])/g,'$1[- ]?');
// One "species" per participant label (before __). Each gets a colour + the regex forms that name it.
function speciesOf(r){
 const labels=[];
 (r.regulator+';'+r.target).split(';').forEach(x=>{const l=(x.split('__')[0]||'').trim();
  if(l&&!labels.some(s=>s.label===l))labels.push({label:l});});
 return labels.map((s,i)=>{
  const color=PALETTE[i%PALETTE.length];
  const toks=s.label.split(/[_:/]/).map(t=>t.replace(/[a-z]+$/,'')).filter(t=>t.length>=2&&!GEN_RX.test(t));
  const forms=new Set();
  if(!/_/.test(s.label)&&!GEN_RX.test(s.label))forms.add(flexTok(s.label));
  toks.forEach(t=>{forms.add(flexTok(t));(SYN[t.toUpperCase()]||[]).forEach(y=>forms.add(y));});
  return {label:s.label,color,forms:[...forms].filter(Boolean)};
 });
}
function hlQuote(text,specs){
 const all=specs.flatMap(s=>s.forms.map(f=>({f,color:s.color}))).filter(x=>x.f);
 if(!all.length)return esc(text);
 const tests=specs.map(s=>({color:s.color,rx:new RegExp('^(?:'+s.forms.join('|')+')$','i')}));
 const big=new RegExp('(?<![\\w>])('+all.map(x=>x.f).sort((a,b)=>b.length-a.length).join('|')+')(?![\\w<])','gi');
 return esc(text).replace(big,m=>{const t=tests.find(x=>x.rx.test(m));const c=t?t.color:'#fff';
  return `<span class="hl" style="color:${c};background:${c}22">${m}</span>`;});
}
function nodeChips(field,specs){
 return field.split(';').filter(Boolean).map(x=>{const l=(x.split('__')[0]||'').trim();
  const sp=specs.find(s=>s.label===l);const c=sp?sp.color:'var(--fg)';
  return `<span style="color:${c}">${esc(l)}</span>`;}).join(' <span class="plus">+</span> ')||'?';
}
function aiVerdict(r){
 if(!r.ai_verdict)return '';
 const meta={validate:['v-ok','✓','Validate','I would confirm this interaction'],
  revise:['v-rev','✎','Revise citation','Biology sound — but the cited reference looks wrong; fix it'],
  caution:['v-cau','⚠','Caution','Supported but contested — weigh the evidence'],
  reject:['v-rej','✗','Reject','I would not include this']}[r.ai_verdict]||['v-cau','?','—',''];
 const pm=(r.ai_verdict_pmids||'').split(';').filter(Boolean);
 const links=pm.length?` <span class="v-pm">${pm.map(p=>`<a href="${pubmed(p)}" target="_blank" rel="noopener">${esc(p)}</a>`).join(' · ')}</span>`:'';
 return `<div class="verdict ${meta[0]}" title="${esc(meta[3])}">
   <span class="v-badge">${meta[1]} AI reviewer call: ${meta[2]}</span>
   <span class="v-rat">${esc(r.ai_verdict_rationale)}${links}</span></div>`;
}
function litRefs(s){try{return JSON.parse(s||'[]');}catch(_){return [];}}
function litItem(x){return `<li><a href="${pubmed(x.p)}" target="_blank" rel="noopener">PMID ${esc(x.p)}</a> ${esc(x.t)} <span class="yr">${esc(x.y)}</span>${x.c?` <span class="cue">${esc(x.c)}</span>`:''}</li>`;}
function litBox(r){
 const sup=litRefs(r.lit_support),con=litRefs(r.lit_contrary);
 if(!sup.length&&!con.length)return '';
 return `<div class="box"><h3>Literature dossier <span class="qb">candidate refs · read &amp; verify</span></h3>
  <div class="lit">
   <div class="lit-col"><h4 class="sup">↑ Supporting (${sup.length})</h4>${sup.length?`<ul>${sup.map(litItem).join('')}</ul>`:'<p class="rel">none surfaced</p>'}</div>
   <div class="lit-col"><h4 class="con">⚠ Possibly contrary (${con.length})</h4>${con.length?`<ul>${con.map(litItem).join('')}</ul>`:'<p class="rel">none surfaced</p>'}</div>
  </div></div>`;
}
function quoteBlock(r,specs){
 const main=r.supporting_quote?`<div class="quote">“${hlQuote(r.supporting_quote,specs)}”</div>`
   :'<div class="quote none">No verbatim quote stored yet — add one from the source.</div>';
 const alt=r.pdf_alt_quote?`<details class="altq"><summary>alternative sentence${r.pdf_alt_page?` (p.${esc(String(r.pdf_alt_page))})`:''}</summary>
   <div class="quote">“${hlQuote(r.pdf_alt_quote,specs)}” ${pdfLink(r,r.pdf_alt_page)}</div></details>`:'';
 return main+alt;
}
function save(){localStorage.setItem(KEY,JSON.stringify(store));}
function toggleFilters(){$('#filters').classList.toggle('open');}
function toggleNote(){const p=$('#notepanel');p.classList.toggle('open');$('.fab.note').classList.toggle('on',p.classList.contains('open'));if(p.classList.contains('open'))$('#note').focus();}

function applyFilters(){
 const q=$('#q').value.toLowerCase(),st=$('#fStatus').value,md=$('#fMod').value,rc=$('#fReco').value,av=$('#fAi').value,dc=$('#fDec').value;
 view=DATA.filter(r=>{
  if(st&&r.inclusion_status!==st)return false;
  if(md&&r.module!==md)return false;
  if(rc&&r.ai_recommendation!==rc)return false;
  if(av&&r.ai_verdict!==av)return false;
  const d=(store[r.reaction_id]||{}).decision||'';
  if(dc==='__undec'&&d)return false;
  if(dc&&dc!=='__undec'&&d!==dc)return false;
  if(q){const h=(r.regulator+r.target+r.mechanism+r.reaction_id+r.article_title).toLowerCase();if(!h.includes(q))return false;}
  return true;});
 if(idx>view.length)idx=view.length;
 renderDeck();
}

function renderProgress(){
 // the bar tracks the current position in the deck (resets each session — idx is not persisted),
 // not the count of stored decisions, so it follows the "card X of N" counter beside it.
 const pos=Math.min(idx,view.length);
 const pct=view.length?Math.round(pos/view.length*100):0;
 $('#pbar').style.width=pct+'%';
 const decided=DATA.filter(r=>(store[r.reaction_id]||{}).decision).length;
 $('#pleft').innerHTML=view.length?`card <b>${Math.min(idx+1,view.length)}</b> / ${view.length}`:'no cards in view';
 $('#pright').innerHTML=`${decided}/${DATA.length} decided`;
}

function cardHTML(r){
 const dec=(store[r.reaction_id]||{});
 const secs=(r.secondary_pmids||'').split(';').filter(Boolean);
 const refs=`${r.pmid?`<a href="${pubmed(r.pmid)}" target="_blank" rel="noopener">PubMed ${r.pmid}</a>`:''}${r.doi?`<a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener">DOI</a>`:''}${secs.map(p=>`<a href="${pubmed(p)}" target="_blank" rel="noopener">+PubMed ${p}</a>`).join('')}`;
 const statusTag=r.inclusion_status==='in_map'?'<span class="tag inmap">● in map</span>':'<span class="tag disc">○ discarded</span>';
 const warn=r.contradiction_flag?'<span class="tag warn">⚠ contradiction</span>':'';
 const multi=Number(r.n_sources)>1?`<span class="tag src">${r.n_sources} sources</span>`:'';
 const inhib=/inhib|repress|degrad|block|negativ|suppress/i.test(r.interaction_type)?'inhib':'';
 const ribbon=dec.decision?`<div class="ribbon ${dec.decision}">${dec.decision==='reject'?'REJECTED':'KEPT'}</div>`:'';
 const specs=speciesOf(r);
 return `${ribbon}<span class="stamp keep">Keep</span><span class="stamp drop">Drop</span>
  <div class="body">
   <div class="chips">${statusTag}<span class="tag mod">${esc(modLabel(r))}</span><span class="tag">${esc(r.reaction_id)}</span>${multi}${warn}</div>
   <div class="inter"><span class="node">${nodeChips(r.regulator,specs)}</span>
    <span class="arrow ${inhib}"><span class="ln">${inhib?'⊣':'→'}</span>${esc(r.interaction_type)}</span>
    <span class="node">${nodeChips(r.target,specs)}</span></div>
   <div class="subids">${esc(r.regulator)} → ${esc(r.target)}</div>
   <div class="mech">${esc(r.mechanism)||'<i>(reclassification / no mechanism text)</i>'}</div>
   ${r.ssc_relevance?`<div class="rel"><b>SSc relevance:</b> ${esc(r.ssc_relevance)}</div>`:''}
   ${aiVerdict(r)}
   <div class="box"><h3>Source article</h3>
    <div class="art">${esc(r.article_title)||'<span class="disc-reason">no title stored</span>'} <span class="yr">${esc(r.journal_year)}</span></div>
    <div class="refs">${refs||'<span class="rel">no PMID</span>'}</div></div>
   <div class="box"><h3>Deciding sentence ${quoteBadge(r.quote_status)}${pdfLink(r)}</h3>
    ${quoteBlock(r,specs)}</div>
   <div class="box"><h3>Evidence &amp; AI recommendation</h3>
    <div class="meta-row"><span class="ev">${esc(r.evidence_level||'—')}</span>${r.eco_code?`<span class="tag">${esc(r.eco_code)}</span>`:''}<span class="tag">${esc(r.provenance)}</span></div>
    <div class="reco" style="margin-top:10px">${esc(r.ai_recommendation)}<small>${esc(r.ai_rationale)}</small></div></div>
   ${litBox(r)}
   ${r.inclusion_status==='discarded'?`<div class="box"><h3>Why it was discarded</h3><div class="disc-reason">${esc(r.discard_reason)}</div></div>`:''}
  </div>`;
}

function renderDeck(){
 const deck=$('#deck');
 if(idx>=view.length){
  const decided=DATA.filter(r=>(store[r.reaction_id]||{}).decision).length;
  deck.innerHTML=`<div class="card"><div class="done"><div class="big">${view.length?'🎉':'🔍'}</div>
   <h2>${view.length?'Deck complete':'No interactions match the filters'}</h2>
   <p class="rel">${decided} / ${DATA.length} interactions decided overall.</p>
   <div style="display:flex;gap:8px">${view.length?'<button onclick="restart()">↺ Review this deck again</button>':''}<button onclick="exportCsv()">⤓ Export CSV</button></div></div></div>`;
  $('#actions').style.visibility='hidden';$('#note').value='';
  renderPreview(null);renderProgress();return;
 }
 $('#actions').style.visibility='visible';
 const stack=[];
 for(let k=Math.min(idx+2,view.length-1);k>=idx;k--)stack.push(k);
 deck.innerHTML=stack.map(k=>{
  const depth=k-idx,isTop=depth===0,scale=(1-depth*0.04).toFixed(3),ty=depth*14;
  return `<div class="card ${isTop?'top':''}" style="transform:translateY(${ty}px) scale(${scale});z-index:${10-depth};${isTop?'':'pointer-events:none;filter:brightness(.82)'}">${cardHTML(view[k])}</div>`;
 }).join('');
 $('#note').value=(store[view[idx].reaction_id]||{}).notes||'';
 attachDrag(deck.querySelector('.card.top'));
 renderPreview(view[idx]);
 renderProgress();
}

// ---- module-map preview (right pane) ----------------------------------------
// Shows the WHOLE module the interaction belongs to, initially zoomed on the reaction; the layout
// is computed once per module (virtual 1000x760 space) and cached, then a pan/zoomable SVG viewBox
// lets the reviewer zoom out to the full module. Scroll = zoom, drag = pan, edge click = jump.
const splitSpecies=f=>[...new Set((f||'').split(';').map(x=>(x.split('__')[0]||'').trim()).filter(Boolean))];
const VW=900,VH=900;
let ALLEDGES=[],pvCache={},pv=null;
function buildEdges(){
 const e=[];
 DATA.forEach(r=>{const ss=splitSpecies(r.regulator),ts=splitSpecies(r.target);
  ss.forEach(s=>ts.forEach(t=>{if(s!==t)e.push({s,t,id:r.reaction_id,module:r.module,
   inhib:/inhib|repress|degrad|block|negativ|suppress/i.test(r.interaction_type)});}));});
 return e;
}
const moduleKey=r=>r.module||('· '+r.inclusion_status);
// Fruchterman-Reingold with deterministic 2D random init + temperature cooling — spreads the graph
// across the plane (a circle init + accumulated velocity collapsed it into a near-1D line).
function layout(nodes,edges,W,H){
 const n=nodes.length,pos={};
 let seed=2166136261>>>0;const rnd=()=>{seed=(seed*1103515245+12345)>>>0;return seed/4294967296;};
 nodes.forEach(id=>{pos[id]={x:W*0.12+rnd()*W*0.76,y:H*0.12+rnd()*H*0.76};});
 const idx={};nodes.forEach((id,i)=>idx[id]=i);
 const pairs=edges.filter(e=>idx[e.s]!==undefined&&idx[e.t]!==undefined);
 const k=Math.sqrt(W*H/Math.max(n,1))*0.9;   // ideal edge length
 let temp=W*0.12;
 for(let it=0;it<320;it++){
  const dsp=nodes.map(()=>({x:0,y:0}));
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const a=pos[nodes[i]],b=pos[nodes[j]];
   let dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy)||0.01,f=k*k/d;
   dsp[i].x+=dx/d*f;dsp[i].y+=dy/d*f;dsp[j].x-=dx/d*f;dsp[j].y-=dy/d*f;}
  pairs.forEach(e=>{const a=pos[e.s],b=pos[e.t],i=idx[e.s],j=idx[e.t];
   let dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy)||0.01,f=d*d/k;
   dsp[i].x-=dx/d*f;dsp[i].y-=dy/d*f;dsp[j].x+=dx/d*f;dsp[j].y+=dy/d*f;});
  nodes.forEach((id,i)=>{const p=pos[id],dl=Math.hypot(dsp[i].x,dsp[i].y)||0.01,mv=Math.min(dl,temp);
   p.x+=dsp[i].x/dl*mv;p.y+=dsp[i].y/dl*mv;
   p.x=Math.max(24,Math.min(W-24,p.x));p.y=Math.max(24,Math.min(H-24,p.y));});
  temp*=0.985;
 }
 return pos;
}
function moduleGraph(r){
 const key=moduleKey(r);
 if(pvCache[key])return pvCache[key];
 let edges=ALLEDGES.filter(e=>e.module===r.module);
 if(!edges.length)edges=ALLEDGES.filter(e=>e.id===r.reaction_id);
 const nodes=[...new Set(edges.flatMap(e=>[e.s,e.t]))];
 const pos=layout(nodes,edges,VW,VH);
 const xs=nodes.map(n=>pos[n].x),ys=nodes.map(n=>pos[n].y);
 const b={x0:Math.min(...xs),x1:Math.max(...xs),y0:Math.min(...ys),y1:Math.max(...ys)};
 return pvCache[key]={edges,nodes,pos,b};
}
// Node sizes/labels are drawn in SCREEN px (viewBox = 0 0 cw ch, 1 unit = 1 px) so they stay a
// constant, legible size at any zoom; pv.view is a window {cx,cy,w} in the virtual layout space.
const cvSize=()=>{const cv=$('#pvcanvas');return [cv.clientWidth||440,cv.clientHeight||400];};
const aspect=()=>{const[w,h]=cvSize();return w/h;};
const fitW=g=>{const a=aspect();let w=(g.b.x1-g.b.x0)+150,h=(g.b.y1-g.b.y0)+150;return Math.max(w,h*a);};
const fullW=g=>fitW(g)*1.15;            // hard zoom-out limit (a bit past the whole module)
function boxOf(nodes,g,pad){const xs=nodes.map(n=>g.pos[n].x),ys=nodes.map(n=>g.pos[n].y),a=aspect();
 let w=(Math.max(...xs)-Math.min(...xs))+pad*2,h=(Math.max(...ys)-Math.min(...ys))+pad*2;
 return {cx:(Math.min(...xs)+Math.max(...xs))/2,cy:(Math.min(...ys)+Math.max(...ys))/2,w:Math.min(Math.max(w,h*a),fullW(g))};}
function boxFit(g){return boxOf(g.nodes,g,75);}
function focusNodes(g,r){const own=new Set([...splitSpecies(r.regulator),...splitSpecies(r.target)].filter(x=>g.pos[x]));
 const out=new Set(own);g.edges.forEach(e=>{if(own.has(e.s))out.add(e.t);if(own.has(e.t))out.add(e.s);});
 return {own,nodes:[...out]};}
function boxFocus(g,r){const f=focusNodes(g,r);return f.nodes.length?boxOf(f.nodes,g,95):boxFit(g);}
function draw(){
 if(!pv)return;
 const svg=pv.svg,[cw,ch]=cvSize(),v=pv.view,s=cw/v.w;
 const sx=x=>(x-v.cx)*s+cw/2,sy=y=>(y-v.cy)*s+ch/2;
 svg.setAttribute('viewBox',`0 0 ${cw} ${ch}`);
 const g=pv.g,r=pv.r,specs=speciesOf(r),colorOf=l=>{const z=specs.find(x=>x.label===l);return z?z.color:null;};
 const own=new Set([...splitSpecies(r.regulator),...splitSpecies(r.target)]);
 const labels=s>=0.5,short=t=>t.length>16?t.slice(0,15)+'…':t;
 let lines='';
 g.edges.forEach(e=>{const ax=sx(g.pos[e.s].x),ay=sy(g.pos[e.s].y),bx=sx(g.pos[e.t].x),by=sy(g.pos[e.t].y),cur=e.id===r.reaction_id;
  lines+=`<path class="pv-edge ${cur?'cur':''}" marker-end="url(#${e.inhib?'mi':'ma'}${cur?'c':''})" d="M${ax.toFixed(1)} ${ay.toFixed(1)} L${bx.toFixed(1)} ${by.toFixed(1)}"/>`
   +`<path class="pv-hit" data-id="${esc(e.id)}" d="M${ax.toFixed(1)} ${ay.toFixed(1)} L${bx.toFixed(1)} ${by.toFixed(1)}"><title>${esc(e.id)} (${esc(e.s)}→${esc(e.t)})</title></path>`;});
 let dots='';
 g.nodes.forEach(id=>{const x=sx(g.pos[id].x),y=sy(g.pos[id].y),c=colorOf(id),inF=own.has(id);
  dots+=`<g class="pv-node ${inF?'cur':''}"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${inF?7:5}" fill="${c||(inF?'#9db2c8':'#5b6675')}"/>`
   +((labels||inF)?`<text x="${x.toFixed(1)}" y="${(y-10).toFixed(1)}" text-anchor="middle">${esc(short(id))}</text>`:'')+'</g>';});
 const mk=(id,col)=>`<marker id="${id}" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="${col}"/></marker>`;
 const mkBar=(id,col)=>`<marker id="${id}" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M6,0 L6,6" stroke="${col}" stroke-width="2"/></marker>`;
 svg.innerHTML=`<defs>${mk('ma','#3a4453')}${mk('mac','#4493f8')}${mkBar('mi','#3a4453')}${mkBar('mic','#4493f8')}</defs>${lines}${dots}`;
}
function zoomAt(clientX,clientY,f){const v=pv.view,svg=pv.svg,rect=svg.getBoundingClientRect(),[cw,ch]=cvSize();
 const s=cw/v.w,vx=v.cx+((clientX-rect.left)-cw/2)/s,vy=v.cy+((clientY-rect.top)-ch/2)/s;
 v.w=Math.max(110,Math.min(v.w*f,fullW(pv.g)));const s2=cw/v.w;
 v.cx=vx-((clientX-rect.left)-cw/2)/s2;v.cy=vy-((clientY-rect.top)-ch/2)/s2;draw();}
function pvZoom(f){if(!pv)return;const r=pv.svg.getBoundingClientRect();zoomAt(r.left+r.width/2,r.top+r.height/2,f);}
function pvFit(){if(pv){pv.view=boxFit(pv.g);draw();}}
function pvFocus(){if(pv){pv.view=boxFocus(pv.g,pv.r);draw();}}
function renderPreview(r){
 const cv=$('#pvcanvas');
 if(!r){$('#pvmod').textContent='—';$('#pvcount').textContent='';$('#pvlegend').innerHTML='';
  cv.innerHTML='<div class="pv-empty">No interaction selected.</div>';pv=null;return;}
 $('#pvmod').textContent=modLabel(r);
 const g=moduleGraph(r);
 cv.innerHTML='<svg></svg>';
 const svg=cv.querySelector('svg');
 pv={svg,g,r,view:boxFocus(g,r)};
 draw();
 attachPan();
 svg.addEventListener('click',ev=>{const h=ev.target.closest('.pv-hit');if(!h)return;
  const i=view.findIndex(v=>v.reaction_id===h.dataset.id);if(i>=0&&i!==idx){idx=i;renderDeck();}});
 const specs=speciesOf(r);
 $('#pvcount').textContent=`${g.nodes.length} nodes · ${g.edges.length} links`;
 $('#pvlegend').innerHTML=specs.map(s=>`<span><i style="background:${s.color}"></i>${esc(s.label)}</span>`).join('')
   +'<span><i style="background:#5b6675"></i>module</span><span class="pv-tip">scroll = zoom · drag = pan</span>';
}
function attachPan(){
 const svg=pv.svg;let panning=false,lx=0,ly=0;
 svg.addEventListener('wheel',e=>{e.preventDefault();zoomAt(e.clientX,e.clientY,e.deltaY<0?0.84:1.19);},{passive:false});
 svg.addEventListener('pointerdown',e=>{if(e.target.classList.contains('pv-hit'))return;
  panning=true;lx=e.clientX;ly=e.clientY;svg.setPointerCapture(e.pointerId);svg.style.cursor='grabbing';});
 svg.addEventListener('pointermove',e=>{if(!panning)return;const[cw]=cvSize(),s=cw/pv.view.w;
  pv.view.cx-=(e.clientX-lx)/s;pv.view.cy-=(e.clientY-ly)/s;lx=e.clientX;ly=e.clientY;draw();});
 const stop=()=>{panning=false;svg.style.cursor='';};
 svg.addEventListener('pointerup',stop);svg.addEventListener('pointercancel',stop);
}

function attachDrag(card){
 if(!card)return;
 let sx=0,sy=0,dx=0,dy=0,drag=false;
 const keep=card.querySelector('.stamp.keep'),drop=card.querySelector('.stamp.drop');
 card.addEventListener('pointerdown',e=>{
  if(e.target.closest('a'))return;
  drag=true;sx=e.clientX;sy=e.clientY;card.style.transition='none';
  try{card.setPointerCapture(e.pointerId);}catch(_){}
 });
 card.addEventListener('pointermove',e=>{
  if(!drag)return;dx=e.clientX-sx;dy=e.clientY-sy;
  card.style.transform=`translate(${dx}px,${dy*0.25}px) rotate(${dx/20}deg)`;
  const t=Math.min(Math.abs(dx)/120,1);
  keep.style.opacity=dx>0?t:0;drop.style.opacity=dx<0?t:0;
 });
 const end=()=>{
  if(!drag)return;drag=false;card.style.transition='transform .3s ease,opacity .3s ease';
  if(dx>110)commitDecision(acceptKind(view[idx]));
  else if(dx<-110)commitDecision('reject');
  else{card.style.transform='';keep.style.opacity=0;drop.style.opacity=0;}
  dx=dy=0;
 };
 card.addEventListener('pointerup',end);
 card.addEventListener('pointercancel',end);
}

function flyOut(card,dir){if(card){card.style.transform=`translate(${dir*720}px,40px) rotate(${dir*28}deg)`;card.style.opacity=0;}}
function commitDecision(kind){
 const r=view[idx];if(!r)return;
 const cur=store[r.reaction_id]||{};cur.decision=kind;store[r.reaction_id]=cur;save();
 hist.push(r.reaction_id);
 const card=$('#deck .card.top');
 if(card){card.style.transition='transform .3s ease,opacity .3s ease';flyOut(card,kind==='reject'?-1:1);}
 setTimeout(()=>{idx++;renderDeck();},230);
}
function doAccept(){if(view[idx])commitDecision(acceptKind(view[idx]));}
function doReject(){if(view[idx])commitDecision('reject');}
function skip(){if(idx<view.length){idx++;renderDeck();}}
function restart(){idx=0;renderDeck();}
function undo(){
 const id=hist.pop();
 if(id){const e=store[id];if(e){delete e.decision;if(!e.notes)delete store[id];save();}}
 view=filteredView();
 const back=id?view.findIndex(v=>v.reaction_id===id):-1;
 idx=back>=0?back:Math.max(0,idx-1);
 renderDeck();
}
function setNote(v){const r=view[idx];if(!r)return;const cur=store[r.reaction_id]||{};cur.notes=v;store[r.reaction_id]=cur;save();}

function filteredView(){
 const q=$('#q').value.toLowerCase(),st=$('#fStatus').value,md=$('#fMod').value,rc=$('#fReco').value,av=$('#fAi').value,dc=$('#fDec').value;
 return DATA.filter(r=>{
  if(st&&r.inclusion_status!==st)return false;
  if(md&&r.module!==md)return false;
  if(rc&&r.ai_recommendation!==rc)return false;
  if(av&&r.ai_verdict!==av)return false;
  const d=(store[r.reaction_id]||{}).decision||'';
  if(dc==='__undec'&&d)return false;
  if(dc&&dc!=='__undec'&&d!==dc)return false;
  if(q){const h=(r.regulator+r.target+r.mechanism+r.reaction_id+r.article_title).toLowerCase();if(!h.includes(q))return false;}
  return true;});
}

function exportCsv(){
 const rows=[['reaction_id','review_decision','review_notes']];
 DATA.forEach(r=>{const s=store[r.reaction_id]||{};if(s.decision||s.notes)rows.push([r.reaction_id,s.decision||'',(s.notes||'').replace(/"/g,'""')]);});
 const csv=rows.map(r=>r.map(c=>/[",\n]/.test(c)?`"${c}"`:c).join(',')).join('\n');
 dl('ssc_review_decisions.csv',csv,'text/csv');
}
function exportJson(){dl('ssc_review_decisions.json',JSON.stringify(store,null,2),'application/json');}
function resetAll(){
 const n=Object.values(store).filter(x=>x.decision||x.notes).length;
 if(!confirm(n?`Clear all ${n} stored decision(s) and note(s)? This cannot be undone.`
   :'Nothing is stored yet — reset anyway?'))return;
 store={};localStorage.removeItem(KEY);hist=[];idx=0;applyFilters();
}
function dl(name,txt,mime){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:mime}));a.download=name;a.click();}

document.addEventListener('keydown',e=>{
 if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;
 const k=e.key.toLowerCase();
 if(e.key==='ArrowRight'||k==='a'){e.preventDefault();doAccept();}
 else if(e.key==='ArrowLeft'||k==='r'){e.preventDefault();doReject();}
 else if(e.key==='ArrowUp'){e.preventDefault();skip();}
 else if(k==='z'){e.preventDefault();undo();}
 else if(k==='n'){e.preventDefault();toggleNote();}
});

(function init(){
 ALLEDGES=buildEdges();
 addEventListener('resize',()=>{if(view[idx])renderPreview(view[idx]);});
 const mods=[...new Set(DATA.map(r=>r.module).filter(Boolean))].sort();
 $('#fMod').innerHTML='<option value="">module: all</option>'+mods.map(m=>`<option value="${esc(m)}">${esc(m)}</option>`).join('');
 const recos=[...new Set(DATA.map(r=>r.ai_recommendation).filter(Boolean))].sort();
 $('#fReco').innerHTML='<option value="">AI reco: all</option>'+recos.map(m=>`<option value="${esc(m)}">${esc(m)}</option>`).join('');
 const inmap=DATA.filter(r=>r.inclusion_status==='in_map').length;
 $('#meta').textContent=`· ${DATA.length} interactions (${inmap} in map, ${DATA.length-inmap} discarded)`;
 ['#q','#fStatus','#fMod','#fReco','#fAi','#fDec'].forEach(s=>$(s).addEventListener('input',()=>{idx=0;applyFilters();}));
 applyFilters();
})();
</script></body></html>
"""


def main() -> None:
    rows = list(csv.DictReader(DB.open()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    artbase = ARTICLE_DIR.resolve().as_uri() + "/"
    html = (HTML.replace("/*__DATA__*/", json.dumps(rows, ensure_ascii=False))
                .replace("/*__ARTBASE__*/", json.dumps(artbase))
                .replace("/*__SYN__*/", json.dumps(SYN, ensure_ascii=False)))
    OUT.write_text(html, encoding="utf-8")
    n_ext = sum(1 for r in rows if r.get("quote_status", "").startswith("verbatim (")
                and r.get("quote_status") != "verbatim (excluded)")
    print(f"[review-app] {len(rows)} interactions -> {OUT}  ({n_ext} with an extracted/verbatim quote shown)")


if __name__ == "__main__":
    main()
