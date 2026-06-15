#!/usr/bin/env python3
"""Generate a self-contained static HTML review app from the interaction database.

Reads analysis/curation/interaction_database.csv and emits review/index.html with the data
embedded as JSON (no server, no CDN, no fetch — works by double-clicking the file). The reviewer
processes interactions one by one: regulator->target, evidence level, the deciding sentence, the
AI recommendation, and PubMed/DOI links; then Confirm / Reject / Re-include / annotate. Decisions
persist in localStorage and export to CSV/JSON.

Run: python3 scripts/build_review_app.py   (or make review-app)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "analysis/curation/interaction_database.csv"
OUT = ROOT / "review/index.html"

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SSc-MIM — interaction review</title>
<style>
:root{--bg:#0f1419;--card:#1a2027;--mut:#8a97a8;--fg:#e6edf3;--bd:#2b3440;--accent:#4493f8;
--green:#3fb950;--red:#f85149;--amber:#d29922;--grey:#6e7681}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
background:var(--bg);color:var(--fg)}
a{color:var(--accent)}button{font:inherit;cursor:pointer;border-radius:6px;border:1px solid var(--bd);
background:var(--card);color:var(--fg);padding:7px 12px}button:hover{border-color:var(--accent)}
.wrap{display:grid;grid-template-columns:300px 1fr;height:100vh}
.side{border-right:1px solid var(--bd);overflow:auto;padding:12px;background:#0c1117}
.side h1{font-size:15px;margin:0 0 4px}.side .sub{color:var(--mut);font-size:12px;margin-bottom:10px}
.side input,.side select{width:100%;margin:3px 0;padding:6px;background:var(--card);color:var(--fg);
border:1px solid var(--bd);border-radius:6px}
.li{padding:6px 8px;border-radius:6px;cursor:pointer;font-size:12px;border:1px solid transparent;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.li:hover{background:var(--card)}.li.cur{background:var(--card);border-color:var(--accent)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle}
.main{overflow:auto;padding:24px;display:flex;justify-content:center}
.card{max-width:820px;width:100%}
.bar{display:flex;gap:8px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
.tag{font-size:11px;padding:3px 8px;border-radius:999px;border:1px solid var(--bd);color:var(--mut)}
.tag.mod{color:var(--accent);border-color:var(--accent)}
.tag.inmap{color:var(--green);border-color:var(--green)}
.tag.disc{color:var(--grey);border-color:var(--grey)}
.tag.warn{color:var(--red);border-color:var(--red)}
.inter{font-size:24px;font-weight:600;margin:6px 0;line-height:1.3}
.inter .arrow{color:var(--mut);font-weight:400}.inter .typ{font-size:14px;color:var(--amber);font-weight:500}
.mech{color:var(--fg);margin:6px 0}.rel{color:var(--mut);font-size:13px;margin:0 0 16px}
.box{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;margin:12px 0}
.box h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.quote{border-left:3px solid var(--accent);padding:4px 0 4px 14px;font-size:15px;color:#d6e2ee;font-style:italic}
.reco{font-size:16px;font-weight:600}.reco small{display:block;font-weight:400;color:var(--mut);font-size:12px;margin-top:3px}
.ev{display:inline-block;padding:3px 9px;border-radius:6px;background:#10243a;border:1px solid #1f4068;color:#9cc4f0;font-size:12px}
.refs a{display:inline-block;margin-right:14px}
.disc-reason{color:var(--amber)}
.dec{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap;align-items:center}
.dec button.act{font-weight:600}
.dec .confirm{border-color:var(--green);color:var(--green)}.dec .confirm.on{background:var(--green);color:#001}
.dec .reject{border-color:var(--red);color:var(--red)}.dec .reject.on{background:var(--red);color:#001}
.dec .incl{border-color:var(--accent);color:var(--accent)}.dec .incl.on{background:var(--accent);color:#001}
textarea{width:100%;margin-top:10px;background:var(--card);color:var(--fg);border:1px solid var(--bd);
border-radius:8px;padding:8px;font:inherit;min-height:54px}
.nav{display:flex;justify-content:space-between;margin-top:18px}
.prog{color:var(--mut);font-size:12px}.kbd{font-size:11px;color:var(--grey);margin-top:8px}
.exp{margin-top:14px}.count{font-size:12px;color:var(--mut);margin:8px 0}
</style></head><body>
<div class="wrap">
 <div class="side">
  <h1>SSc-MIM review</h1>
  <div class="sub" id="meta"></div>
  <input id="q" placeholder="Search regulator / target / gene…">
  <select id="fStatus"><option value="">all (in_map + discarded)</option><option>in_map</option><option>discarded</option></select>
  <select id="fMod"></select>
  <select id="fReco"></select>
  <select id="fDec"><option value="">decision: any</option><option value="">— undecided</option><option>confirm</option><option>reject</option><option>include</option></select>
  <div class="count" id="count"></div>
  <button class="exp" onclick="exportCsv()">⤓ Export decisions (CSV)</button>
  <button class="exp" onclick="exportJson()">⤓ JSON</button>
  <div class="count" id="prog2"></div>
  <div id="list"></div>
 </div>
 <div class="main"><div class="card" id="card"></div></div>
</div>
<script>
const DATA = /*__DATA__*/;
const KEY='sscmim_review_v1';
let store=JSON.parse(localStorage.getItem(KEY)||'{}');
let view=[], idx=0;
const $=s=>document.querySelector(s);
const pubmed=p=>`https://pubmed.ncbi.nlm.nih.gov/${p}/`;
function save(){localStorage.setItem(KEY,JSON.stringify(store));}
function dotColor(r){const d=(store[r.reaction_id]||{}).decision;
 if(d==='confirm')return 'var(--green)';if(d==='reject')return 'var(--red)';if(d==='include')return 'var(--accent)';
 return r.inclusion_status==='discarded'?'var(--grey)':'var(--bd)';}
function applyFilters(){
 const q=$('#q').value.toLowerCase(),st=$('#fStatus').value,md=$('#fMod').value,rc=$('#fReco').value,dc=$('#fDec').value;
 view=DATA.filter(r=>{
  if(st&&r.inclusion_status!==st)return false;
  if(md&&r.module!==md)return false;
  if(rc&&r.ai_recommendation!==rc)return false;
  const d=(store[r.reaction_id]||{}).decision||'';
  if($('#fDec').selectedIndex===1&&d)return false; // "undecided"
  if(dc&&$('#fDec').selectedIndex>1&&d!==dc)return false;
  if(q){const h=(r.regulator+r.target+r.mechanism+r.reaction_id).toLowerCase();if(!h.includes(q))return false;}
  return true;});
 if(idx>=view.length)idx=0;
 renderList();render();
}
function renderList(){
 const dec=Object.values(store).filter(x=>x.decision).length;
 $('#count').textContent=`${view.length} shown · ${dec}/${DATA.length} decided`;
 $('#list').innerHTML=view.map((r,i)=>`<div class="li ${i===idx?'cur':''}" onclick="go(${i})">
  <span class="dot" style="background:${dotColor(r)}"></span>${r.reaction_id} · ${r.regulator.split(';')[0].split('__')[0]}→${r.target.split('__')[0]}</div>`).join('');
}
function go(i){idx=i;renderList();render();}
function setDec(d){const r=view[idx];if(!r)return;const cur=store[r.reaction_id]||{};
 cur.decision=cur.decision===d?'':d;store[r.reaction_id]=cur;save();renderList();render();}
function setNote(v){const r=view[idx];if(!r)return;const cur=store[r.reaction_id]||{};cur.notes=v;store[r.reaction_id]=cur;save();}
function render(){
 const r=view[idx];if(!r){$('#card').innerHTML='<p class="prog">No interactions match the filters.</p>';$('#prog2').textContent='';return;}
 const dec=(store[r.reaction_id]||{});
 const secs=(r.secondary_pmids||'').split(';').filter(Boolean);
 const refs=`${r.pmid?`<a href="${pubmed(r.pmid)}" target="_blank">PubMed ${r.pmid}</a>`:''}
  ${r.doi?`<a href="https://doi.org/${r.doi}" target="_blank">DOI</a>`:''}
  ${secs.map(p=>`<a href="${pubmed(p)}" target="_blank">+PubMed ${p}</a>`).join('')}`;
 const statusTag=r.inclusion_status==='in_map'?'<span class="tag inmap">in map</span>':'<span class="tag disc">discarded</span>';
 const warn=r.contradiction_flag?`<span class="tag warn">⚠ contradiction</span>`:'';
 const multi=Number(r.n_sources)>1?`<span class="tag">${r.n_sources} sources</span>`:'';
 $('#card').innerHTML=`
  <div class="bar">${statusTag}<span class="tag mod">${r.module||'—'}</span>
   <span class="tag">${r.reaction_id}</span>${multi}${warn}</div>
  <div class="inter">${esc(r.regulator)} <span class="arrow">—[${r.interaction_type}]→</span> ${esc(r.target)}</div>
  <div class="mech">${esc(r.mechanism)||'<i>(reclassification / no mechanism text)</i>'}</div>
  <div class="rel">${esc(r.ssc_relevance)}</div>
  ${r.inclusion_status==='discarded'?`<div class="box"><h3>Why it was discarded</h3><div class="disc-reason">${esc(r.discard_reason)}</div></div>`:''}
  <div class="box"><h3>AI recommendation</h3>
   <div class="reco">${esc(r.ai_recommendation)}<small>${esc(r.ai_rationale)}</small></div>
   <div style="margin-top:10px"><span class="ev">${esc(r.evidence_level||'—')}</span> <span class="tag">${r.eco_code||''}</span> <span class="tag">${esc(r.provenance)}</span></div>
  </div>
  <div class="box"><h3>Deciding sentence ${r.quote_status==='to_complete'?'<span class="tag warn">to complete</span>':''}</h3>
   ${r.supporting_quote?`<div class="quote">“${esc(r.supporting_quote)}”</div>`:'<p class="prog">No verbatim quote stored — add one from the source.</p>'}
  </div>
  <div class="box"><h3>References</h3>
   <div class="rel">${esc(r.article_title)} <span class="prog">${esc(r.journal_year)}</span></div>
   <div class="refs">${refs||'<span class="prog">no PMID</span>'}</div></div>
  <div class="dec">
   <button class="confirm act ${dec.decision==='confirm'?'on':''}" onclick="setDec('confirm')">✓ Confirm</button>
   <button class="reject act ${dec.decision==='reject'?'on':''}" onclick="setDec('reject')">✗ Reject</button>
   ${r.inclusion_status==='discarded'?`<button class="incl act ${dec.decision==='include'?'on':''}" onclick="setDec('include')">↺ Re-include</button>`:''}
   <span class="prog">${dec.decision?('→ '+dec.decision):'undecided'}</span>
  </div>
  <textarea placeholder="Reviewer note (optional)…" oninput="setNote(this.value)">${esc(dec.notes||'')}</textarea>
  <div class="nav"><button onclick="go((idx-1+view.length)%view.length)">← Prev</button>
   <span class="prog" id="prog">${idx+1} / ${view.length}</span>
   <button onclick="go((idx+1)%view.length)">Next →</button></div>
  <div class="kbd">Keys: ← → navigate · C confirm · R reject · I re-include · N focus note</div>`;
 $('#prog2').textContent=`Interaction ${idx+1} of ${view.length}`;
 renderList();
}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function exportCsv(){
 const rows=[['reaction_id','review_decision','review_notes']];
 DATA.forEach(r=>{const s=store[r.reaction_id]||{};if(s.decision||s.notes)rows.push([r.reaction_id,s.decision||'',(s.notes||'').replace(/"/g,'""')]);});
 const csv=rows.map(r=>r.map(c=>/[",\n]/.test(c)?`"${c}"`:c).join(',')).join('\n');
 dl('ssc_review_decisions.csv',csv,'text/csv');}
function exportJson(){dl('ssc_review_decisions.json',JSON.stringify(store,null,2),'application/json');}
function dl(name,txt,mime){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:mime}));a.download=name;a.click();}
document.addEventListener('keydown',e=>{if(e.target.tagName==='TEXTAREA'||e.target.tagName==='INPUT')return;
 if(e.key==='ArrowRight')go((idx+1)%view.length);else if(e.key==='ArrowLeft')go((idx-1+view.length)%view.length);
 else if(e.key.toLowerCase()==='c')setDec('confirm');else if(e.key.toLowerCase()==='r')setDec('reject');
 else if(e.key.toLowerCase()==='i')setDec('include');else if(e.key.toLowerCase()==='n'){const t=document.querySelector('textarea');if(t){e.preventDefault();t.focus();}}});
(function init(){
 const mods=[...new Set(DATA.map(r=>r.module).filter(Boolean))].sort();
 $('#fMod').innerHTML='<option value="">module: all</option>'+mods.map(m=>`<option>${m}</option>`).join('');
 const recos=[...new Set(DATA.map(r=>r.ai_recommendation))].sort();
 $('#fReco').innerHTML='<option value="">AI reco: all</option>'+recos.map(m=>`<option>${esc(m)}</option>`).join('');
 const inmap=DATA.filter(r=>r.inclusion_status==='in_map').length;
 $('#meta').textContent=`${DATA.length} interactions · ${inmap} in map · ${DATA.length-inmap} discarded`;
 ['#q','#fStatus','#fMod','#fReco','#fDec'].forEach(s=>$(s).addEventListener('input',applyFilters));
 applyFilters();
})();
</script></body></html>
"""


def main() -> None:
    rows = list(csv.DictReader(DB.open()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = HTML.replace("/*__DATA__*/", json.dumps(rows, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    print(f"[review-app] {len(rows)} interactions -> {OUT}  (open it in a browser)")


if __name__ == "__main__":
    main()
