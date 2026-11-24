"""
gb-my-team: build.py

Reads data/data.json (written by fetch_data.py) and writes index.html.
All page logic lives here. Never edit index.html by hand: change this file
and rebuild. See SPEC.md sections 10 and 11.
"""

import json
import os
import html

DATA_PATH = os.path.join("data", "data.json")
OUT_PATH = "index.html"

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light">
<title>__TITLE__</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏀</text></svg>">
<style>
:root{
  --maple:#efd9b4; --maple2:#e4c492; --wood-text:#4a2c0c; --line:#ffffff;
  --paint:#3d6fb6; --paint-dk:#24508f; --orange:#d9651e;
  --page:#fbf8f2; --card:#ffffff; --grid:#e3ddd2; --head:#f6f1e7;
  --text:#2b2620; --muted:#7a7166; --mine:#e8f0fb; --warn:#c0392b;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--page);color:var(--text);
  font:13px/1.4 "Segoe UI",Calibri,Arial,sans-serif}
.bar{background:var(--maple);border-bottom:3px solid var(--orange);
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:10px 16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;color:var(--wood-text)}
.brand h1{margin:0;font-size:20px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase}
.brand .sub{font-size:12px;color:#7a5326}
.pages{display:flex;gap:6px}
.pages button{border:1.5px solid var(--wood-text);background:transparent;color:var(--wood-text);
  border-radius:6px;padding:5px 14px;font:600 13px "Segoe UI",sans-serif;cursor:pointer}
.pages button.on{background:var(--wood-text);color:var(--maple)}
.court{display:block;width:100%;height:30px}
.warnbar{background:#fdecea;border-left:5px solid var(--warn);color:#7d1f15;
  margin:10px 16px 0;padding:8px 12px;border-radius:0}
.warnbar b{display:block;margin-bottom:2px}
.warnbar ul{margin:0;padding-left:18px}
.wrap{padding:10px 16px 24px}
.panel{background:var(--card);border:1px solid var(--grid);border-radius:8px;
  padding:8px 10px;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center}
.cg{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.cg .lab{color:var(--muted);font-size:12px;margin-right:2px}
.chip{border:1px solid #cfc6b6;background:#fff;color:var(--text);border-radius:5px;
  padding:2px 9px;font:12px "Segoe UI",sans-serif;cursor:pointer}
.chip.on{background:var(--paint);border-color:var(--paint-dk);color:#fff}
.chip.clear{border-style:dashed;color:var(--muted)}
details.lines{background:var(--card);border:1px solid var(--grid);border-radius:8px;
  margin-bottom:10px;padding:6px 10px}
details.lines summary{cursor:pointer;font-weight:600;color:var(--wood-text)}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--grid);border-radius:8px}
table{border-collapse:separate;border-spacing:0;width:100%;white-space:nowrap}
th,td{border-right:1px solid var(--grid);border-bottom:1px solid var(--grid);
  padding:4px 7px;text-align:right}
th{background:var(--head);font-weight:600;position:sticky;top:0;z-index:2;cursor:pointer;user-select:none}
th.gh{cursor:default;text-align:center;color:var(--wood-text);border-bottom:2px solid var(--maple2)}
th .ar{color:var(--muted);font-size:10px}
td.l,th.l{text-align:left}
td.sticky,th.sticky{position:sticky;left:0;background:var(--card);z-index:1}
th.sticky{z-index:3;background:var(--head)}
tr.mine td{background:var(--mine)}
tr.mine td.sticky{background:var(--mine)}
td.dim{color:#b3aba0}
.tag{display:inline-block;font-size:10.5px;font-weight:700;border-radius:3px;padding:0 4px;margin-left:5px;vertical-align:1px}
.tag.inj{background:#fbe1dd;color:#9b2a1c}
.tag.gtd{background:#fdf0d5;color:#8a5a00}
.tag.cut{background:#ece8e1;color:#6b6358}
.tag.mine{background:var(--paint);color:#fff}
.tag.wv{background:#ece8e1;color:#6b6358}
.why{color:var(--muted);font-size:11px;margin-left:6px}
.star{color:var(--orange)}
.note{color:var(--muted)}
.note.bad{color:var(--warn);font-weight:600}
.up{color:#2f7d47}.dn{color:var(--warn)}
.foot{color:var(--muted);font-size:12px;margin-top:10px}
.lt td,.lt th{padding:3px 8px}
.lt{width:auto}
.sline{margin:0 0 6px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;margin:0 0 8px;color:var(--text)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:50%}
.legend i.ln{width:20px;height:0;border-radius:0;border-top:2px dashed var(--orange)}
.legend i.ln.wk{border-top:2px dotted var(--paint)}
.chartwrap{position:relative;background:var(--card);border:1px solid var(--grid);border-radius:8px;padding:6px}
.chartwrap svg{display:block;width:100%;height:auto}
.dot{cursor:pointer}
.dot.hot{stroke:#2b2620 !important;stroke-width:2.5px !important}
.tip{position:absolute;z-index:5;background:#fff;border:1px solid #cfc6b6;border-radius:6px;
  padding:7px 9px;font-size:12px;line-height:1.5;box-shadow:0 4px 14px rgba(60,40,10,.15);max-width:260px;pointer-events:none}
.tip .k{color:var(--muted)}
.empty{color:var(--muted);padding:20px}
@media (max-width:640px){.brand h1{font-size:16px}.wrap{padding:8px}}
</style>
</head>
<body>
<div class="bar">
  <div class="brand">
    <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="#d9651e" stroke="#4a2c0c" stroke-width="1.6"/><path d="M2 16h28M16 2v28M6 6c5 5 5 15 0 20M26 6c-5 5-5 15 0 20" fill="none" stroke="#4a2c0c" stroke-width="1.4"/></svg>
    <div><h1 id="mast"></h1><div class="sub" id="sub"></div></div>
  </div>
  <div class="pages"><button id="pg-team" class="on">My Team</button><button id="pg-wire">Waiver Wire</button><button id="pg-scatter">Scatter</button></div>
</div>
<svg class="court" viewBox="0 0 1000 30" preserveAspectRatio="none" aria-hidden="true">
  <rect width="1000" height="30" fill="#e4c492"/>
  <rect x="0" y="5" width="110" height="20" fill="#3d6fb6"/><rect x="890" y="5" width="110" height="20" fill="#3d6fb6"/>
  <path d="M110 0 A120 60 0 0 1 110 30" fill="none" stroke="#fff" stroke-width="2.5"/>
  <path d="M890 0 A120 60 0 0 0 890 30" fill="none" stroke="#fff" stroke-width="2.5"/>
  <line x1="500" y1="0" x2="500" y2="30" stroke="#fff" stroke-width="2.5"/>
  <circle cx="500" cy="15" r="13" fill="none" stroke="#fff" stroke-width="2.5"/>
  <path d="M0 2.5H1000M0 27.5H1000" stroke="#fff" stroke-width="2"/>
</svg>
<div id="warn"></div>
<div class="wrap">
  <div id="controls"></div>
  <div id="linesbox"></div>
  <div class="tw" id="tablearea"><table id="tbl"></table></div>
  <div id="scatarea" hidden>
    <p class="sline" id="scatline"></p>
    <div class="legend" id="scatlegend"></div>
    <div class="chartwrap" id="scatwrap"><div class="tip" id="tip" hidden></div><div id="scatsvg"></div></div>
    <p class="foot">X = total fantasy points in the window. Y = fantasy points per game. Dashed orange line = replacement line for this position and window.
      Dotted blue line = your weakest active player at this position (any free agent above it is an upgrade).
      Labels show your players and the top 5 qualified free agents by PPG. Hover or tap any dot for details.
      Turning off "Show my team" or "Show disqualified" grays those dots out instead of removing them. Position and Window are shared with the Waiver Wire.</p>
  </div>
  <div class="foot" id="foot"></div>
</div>
<script>
const D = __DATA__;
const STATS = ["PTS","REB","AST","ST","BLK","TO"];
const LENSES = ["forme","season","l30","l14"];
const LLAB = {forme:"For me", season:"Season", l30:"L30", l14:"L14"};
const POSORD = {G:0, F:1, C:2};
const S = {
  page:"team",
  team:{view:"rep", mode:"pos", win:"season", as:"raw",
        pos:new Set(["G","F","C"]), status:new Set(["Active","Injured"]), flags:new Set(),
        sort:null, dir:-1},
  wire:{pos:"ALL", win:"l30", show:"pg", as:"raw", mine:true, disq:false, sort:"ppg", dir:-1}
};

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const f1 = v => v == null ? "" : (Math.round(v*10)/10).toFixed(1);
const f0 = v => v == null ? "" : String(Math.round(v));
const sg1 = v => v == null ? "" : (v > 0 ? "+" : "") + f1(v);
const sg0 = v => v == null ? "" : (v > 0 ? "+" : "") + f0(v);
const pct = v => v == null ? "" : f0(v) + "%";

/* ---------- color scales ---------- */
const RED=[248,105,107], WHITE=[255,255,255], GREEN=[99,190,123];
const mix=(a,b,t)=>a.map((x,i)=>Math.round(x+(b[i]-x)*t));
const rgb=c=>`rgb(${c[0]},${c[1]},${c[2]})`;
function seqColor(v, vals, rev){
  if (v==null || vals.length<2) return "";
  const s=[...vals].sort((a,b)=>a-b), lo=s[0], hi=s[s.length-1];
  const mid=s.length%2 ? s[(s.length-1)/2] : (s[s.length/2-1]+s[s.length/2])/2;
  if (hi===lo) return "";
  let c;
  if (v<=mid) c = mix(RED, WHITE, mid===lo ? 1 : (v-lo)/(mid-lo));
  else c = mix(WHITE, GREEN, hi===mid ? 0 : (v-mid)/(hi-mid));
  if (rev) c = v<=mid ? mix(GREEN, WHITE, mid===lo?1:(v-lo)/(mid-lo)) : mix(WHITE, RED, hi===mid?0:(v-mid)/(hi-mid));
  return rgb(c);
}
function divColor(v, vals){
  if (v==null) return "";
  const m=Math.max(...vals.map(Math.abs), 0);
  if (!m) return "";
  return rgb(v<0 ? mix(WHITE, RED, -v/m) : mix(WHITE, GREEN, v/m));
}

/* ---------- generic table ---------- */
function drawTable(cols, rows, st, defaultSort){
  // sort
  const col = cols.find(c=>c.k===st.sort);
  rows = rows.slice();
  if (col){
    rows.sort((a,b)=>{
      const x=col.sv?col.sv(a):col.v(a), y=col.sv?col.sv(b):col.v(b);
      if (x==null && y==null) return 0; if (x==null) return 1; if (y==null) return -1;
      return (typeof x==="string" ? x.localeCompare(y) : x-y) * st.dir;
    });
  } else if (defaultSort) rows.sort(defaultSort);
  // scales
  const scaleVals = {};
  cols.forEach(c=>{ if (c.scale) scaleVals[c.k] = rows.filter(r=>!(c.skip&&c.skip(r))).map(c.v).filter(v=>v!=null); });
  // header (with optional group row)
  let h = "";
  if (cols.some(c=>c.g)){
    h += "<tr>"; let i=0;
    while (i<cols.length){
      const g=cols[i].g||""; let n=1;
      while (i+n<cols.length && (cols[i+n].g||"")===g) n++;
      h += `<th class="gh${i===0?" sticky":""}" colspan="${n}">${esc(g)}</th>`; i+=n;
    }
    h += "</tr>";
  }
  h += "<tr>"+cols.map(c=>{
    const ar = st.sort===c.k ? `<span class="ar">${st.dir<0?" ▼":" ▲"}</span>` : "";
    return `<th data-k="${c.k}" class="${c.l?"l ":""}${c.sticky?"sticky":""}" title="${esc(c.tip||"")}">${esc(c.h)}${ar}</th>`;
  }).join("")+"</tr>";
  let b = rows.map(r=>{
    const tds = cols.map(c=>{
      const v=c.v(r); let bg="";
      if (c.scale && !(c.skip&&c.skip(r))){
        bg = c.scale==="div" ? divColor(v, scaleVals[c.k]) : seqColor(v, scaleVals[c.k], c.rev && c.rev());
      }
      const cls=[c.l?"l":"", c.sticky?"sticky":"", c.dim&&c.dim(r)?"dim":""].join(" ").trim();
      const style = bg && !(c.dim&&c.dim(r)) ? ` style="background:${bg}"` : "";
      return `<td class="${cls}"${style}>${c.f?c.f(v,r):esc(v??"")}</td>`;
    }).join("");
    return `<tr class="${r._mine?"mine":""}">${tds}</tr>`;
  }).join("");
  if (!rows.length) b = `<tr><td class="l" colspan="${cols.length}">No rows match these filters.</td></tr>`;
  $("tbl").innerHTML = `<thead>${h}</thead><tbody>${b}</tbody>`;
  $("tbl").querySelectorAll("th[data-k]").forEach(th=>th.onclick=()=>{
    const k=th.dataset.k;
    if (st.sort===k) st.dir=-st.dir; else { st.sort=k; st.dir = cols.find(c=>c.k===k).l ? 1 : -1; }
    render();
  });
}

/* ---------- shared bits ---------- */
function tagHtml(t){
  if (!t) return "";
  const cls = (t==="O"||t==="INJ"||t==="SUSP") ? "inj" : "gtd";
  return `<span class="tag ${cls}">${esc(t)}</span>`;
}
function statVal(st, s, gp, perGame, asPts){
  if (!st || !gp) return null;
  let v = st[s] * (asPts ? D.meta.weights[s] : 1);
  return perGame ? v/gp : v;
}
function chips(label, opts, isOn, onClick){
  const html = opts.map(([val,lab])=>`<button class="chip${isOn(val)?" on":""}" data-v="${esc(val)}">${esc(lab)}</button>`).join("");
  return {label, html, onClick};
}
function drawControls(groups, extra){
  const box=$("controls");
  box.innerHTML = `<div class="panel">${groups.map((g,i)=>`<div class="cg" data-i="${i}"><span class="lab">${esc(g.label)}</span>${g.html}</div>`).join("")}${extra||""}</div>`;
  box.querySelectorAll(".cg").forEach(el=>{
    const g=groups[+el.dataset.i];
    el.querySelectorAll(".chip").forEach(b=>b.onclick=()=>{ g.onClick(b.dataset.v); render(); });
  });
}

/* ---------- My Team ---------- */
function teamRows(){
  const T=S.team, src = T.mode==="pos" ? D.rows.pos : D.rows.all;
  return src.filter(r=>{
    const p=D.players[r.p];
    const posOk = T.mode==="pos" ? T.pos.has(r.pos) : p.pos.some(x=>T.pos.has(x));
    if (!posOk || !T.status.has(p.status)) return false;
    for (const f of T.flags) if (!r.flags.includes(f)) return false;
    return true;
  });
}
function playerCell(r){
  const p=D.players[r.p];
  let t = esc(p.name) + tagHtml(p.tag);
  if (p.status==="Cut") t += `<span class="tag cut">Cut</span>`;
  return t;
}
function notesCell(r){
  return r.notes.map(n=>`<span class="note${(n==="Replace?"||n==="Poor performer")?" bad":""}">${esc(n)}</span>`).join(", ");
}
function trendCell(v, thr){
  if (v==null) return "";
  const a = v>thr ? `<span class="up">▲</span> ` : v<-thr ? `<span class="dn">▼</span> ` : "";
  return a + sg0(v*100) + "%";
}
function drawTeam(){
  const T=S.team;
  const groups=[
    chips("View",[["rep","vs Replacement"],["stat","Stat line"]],v=>T.view===v,v=>{T.view=v;T.sort=null;}),
    chips("Compare to",[["pos","Position"],["all","All players"]],v=>T.mode===v,v=>T.mode=v),
  ];
  if (T.view==="stat"){
    groups.push(chips("Window",LENSES.map(l=>[l,LLAB[l]]),v=>T.win===v,v=>T.win=v));
    groups.push(chips("Stats as",[["raw","Raw"],["pts","Fantasy pts"]],v=>T.as===v,v=>T.as=v));
  }
  groups.push(chips("Position",[["G","G"],["F","F"],["C","C"]],v=>T.pos.has(v),v=>{T.pos.has(v)?T.pos.delete(v):T.pos.add(v);}));
  groups.push(chips("Status",[["Active","Active"],["Injured","Injured"],["Cut","Cut"]],v=>T.status.has(v),v=>{T.status.has(v)?T.status.delete(v):T.status.add(v);}));
  groups.push(chips("Flags",[["Poor performer","Poor performer"],["Replace?","Replace?"]],v=>T.flags.has(v),v=>{T.flags.has(v)?T.flags.delete(v):T.flags.add(v);}));
  groups.push(chips("",[["x","Clear slicers"]],()=>false,()=>{T.pos=new Set(["G","F","C"]);T.status=new Set(["Active","Injured"]);T.flags=new Set();}));
  drawControls(groups);
  $("controls").querySelectorAll('.chip[data-v="x"]').forEach(b=>b.classList.add("clear"));
  drawLines();

  const base=[
    {k:"name",h:"Player",l:1,sticky:1,v:r=>D.players[r.p].name,f:(v,r)=>playerCell(r)},
    {k:"pos",h:"Pos",l:1,v:r=>r.pos,sv:r=>POSORD[r.pos.split(",")[0]]},
    {k:"notes",h:"Notes",l:1,v:r=>r.notes.join(", "),f:(v,r)=>notesCell(r)},
  ];
  const defSort=(a,b)=>{
    const pa=POSORD[a.pos.split(",")[0]], pb=POSORD[b.pos.split(",")[0]];
    if (pa!==pb) return pa-pb;
    const x=a.c.season?a.c.season.ppg:-1e9, y=b.c.season?b.c.season.ppg:-1e9;
    return y-x;
  };
  let cols;
  if (T.view==="rep"){
    cols=[...base];
    LENSES.forEach(l=>{
      const g=LLAB[l], dim = l==="forme" ? (r=>r.small) : null;
      const get = (r,f)=>r.c[l]?r.c[l][f]:null;
      cols.push({k:l+"gp",g,h:"GP",v:r=>get(r,"gp"),f:f0,dim});
      cols.push({k:l+"ppg",g,h:"PPG",v:r=>get(r,"ppg"),f:f1,scale:"seq",dim});
      cols.push({k:l+"fp",g,h:"Total FP",v:r=>get(r,"fp"),f:f1,dim});
      cols.push({k:l+"gap",g,h:"+/- PPG",v:r=>get(r,"gap"),f:sg1,scale:"div",dim,tip:"PPG minus the replacement line"});
      cols.push({k:l+"pts",g,h:"+/- Pts",v:r=>get(r,"pts"),f:sg0,scale:"div",dim,tip:"+/- PPG x GP"});
    });
    const mp=r=>{const w=D.players[r.p].w.season; return w?w.mpg:null;};
    cols.push({k:"pt",g:"Trend",h:"PPG L30 vs Szn",v:r=>r.pt,f:v=>trendCell(v,D.meta.ppg_trend_pct)});
    cols.push({k:"mpg",g:"Trend",h:"MPG Szn",v:mp,f:f1,scale:"seq"});
    cols.push({k:"mt",g:"Trend",h:"MPG L14 vs Szn",v:r=>r.mt,f:v=>trendCell(v,D.meta.mpg_trend_pct)});
  } else {
    const w=T.win, asPts=T.as==="pts";
    const d=r=>D.players[r.p].w[w];
    cols=[...base,
      {k:"gp",h:"GP",v:r=>d(r)?d(r).gp:null,f:f0},
      {k:"mpg",h:"MPG",v:r=>d(r)?d(r).mpg:null,f:f1,scale:"seq"},
      {k:"ppg",h:"PPG",v:r=>d(r)?d(r).fp/d(r).gp:null,f:f1,scale:"seq"},
      {k:"fp",h:"Total FP",v:r=>d(r)?d(r).fp:null,f:f1},
      ...STATS.map(s=>({k:s,h:s+"/G",v:r=>d(r)?statVal(d(r).st,s,d(r).gp,true,asPts):null,f:f1,scale:"seq",rev:()=>s==="TO"&&!asPts})),
    ];
  }
  drawTable(cols, teamRows(), T, defSort);
}
function drawLines(){
  const L=D.lines, labs={G:"G",F:"F",C:"C",ALL:"All"};
  let h=`<details class="lines"><summary>Replacement lines (top ${D.meta.pool_size} free agents by PPG, GP-weighted)</summary><table class="lt"><tr><th class="l">Window</th><th>Min GP</th>`+
    Object.values(labs).map(x=>`<th>${x}</th>`).join("")+"</tr>";
  ["season","l30","l14"].forEach(w=>{
    const any=L[w].ALL;
    h+=`<tr><td class="l">${LLAB[w]}</td><td>${any.min_gp} <span class="note">(max ${any.max_gp})</span></td>`+
      Object.keys(labs).map(k=>{const x=L[w][k]; const short=x.n<D.meta.pool_size?` <span class="note">(${x.n})</span>`:"";
        return `<td title="${esc(x.members.join(", "))}">${f1(x.ppg)}${short}</td>`;}).join("")+"</tr>";
  });
  h+=`</table><div class="note" style="margin-top:4px">Hover a number to see the players in that line. Min GP = ${Math.round(D.meta.min_gp_pct*100)}% of the most games played by any free agent in that window, rounded up.</div></details>`;
  $("linesbox").innerHTML=h;
}

/* ---------- Waiver Wire ---------- */
function myRows(w, L){
  const out=[];
  D.players.forEach(p=>{
    const d=p.w[w];
    if (p.status==="Cut" || !d || !d.gp) return;
    if (L!=="ALL" && !p.pos.includes(L)) return;
    out.push({name:p.name,team:p.team,pos:p.pos,tag:p.tag,status:p.status,own:d.own,gp:d.gp,fp:d.fp,
              ppg:d.fp/d.gp,mpg:d.mpg,st:d.st,q:true,why:"",pool:[],_mine:true});
  });
  return out;
}
function addGaps(rows, lp, weak){
  rows.forEach(r=>{
    r.gap = (r.ppg!=null && lp!=null) ? r.ppg-lp : null;
    r.upg = (!r._mine && weak && r.ppg!=null && r.ppg>weak.ppg) ? r.ppg-weak.ppg : null;
  });
  return rows;
}
function wireControls(full){
  const Wv=S.wire, g=[
    chips("Position",[["G","G"],["F","F"],["C","C"],["ALL","All"]],v=>Wv.pos===v,v=>Wv.pos=v),
    chips("Window",[["season","Season"],["l30","L30"],["l14","L14"]],v=>Wv.win===v,v=>Wv.win=v),
  ];
  if (full){
    g.push(chips("Show",[["pg","Per game"],["tot","Totals"]],v=>Wv.show===v,v=>Wv.show=v));
    g.push(chips("Stats as",[["raw","Raw"],["pts","Fantasy pts"]],v=>Wv.as===v,v=>Wv.as=v));
  }
  g.push(chips("Show my team",[["1","On"]],()=>Wv.mine,()=>Wv.mine=!Wv.mine));
  g.push(chips("Show disqualified",[["1","On"]],()=>Wv.disq,()=>Wv.disq=!Wv.disq));
  drawControls(g);
}
function drawWire(){
  const Wv=S.wire, w=Wv.win, L=Wv.pos;
  wireControls(true);
  $("linesbox").innerHTML="";
  const line=D.lines[w][L], lp=line.ppg, weak=D.weakest[w][L];
  let rows=D.fa[w].filter(r=>(L==="ALL"||r.pos.includes(L)) && (Wv.disq||r.q)).map(r=>Object.assign({},r));
  if (Wv.mine) rows.push(...myRows(w, L));
  addGaps(rows, lp, weak);
  const per=Wv.show==="pg", asPts=Wv.as==="pts";
  const cols=[
    {k:"star",h:"★",v:r=>r.pool.includes(L)?1:0,f:v=>v?'<span class="star" title="In the replacement pool">★</span>':""},
    {k:"name",h:"Player",l:1,sticky:1,v:r=>r.name,f:(v,r)=>esc(v)+tagHtml(r.tag)+(r._mine?'<span class="tag mine">Mine</span>':"")+(r.wv?'<span class="tag wv">Waivers</span>':"")+(r.q?"":`<span class="why">${esc(r.why)}</span>`)},
    {k:"pos",h:"Pos",l:1,v:r=>r.pos.join(",")},
    {k:"team",h:"Team",l:1,v:r=>r.team},
    {k:"own",h:"Own %",v:r=>r.own,f:pct},
    {k:"gp",h:"GP",v:r=>r.gp,f:f0},
    {k:"mpg",h:"MPG",v:r=>r.mpg,f:f1,scale:"seq"},
    {k:"ppg",h:"PPG",v:r=>r.ppg,f:f1,scale:"seq"},
    {k:"fp",h:"Total FP",v:r=>r.fp,f:f1},
    {k:"gap",h:"+/- Line",v:r=>r.gap,f:sg1,scale:"div",tip:`PPG minus the ${LLAB[w]} ${L==="ALL"?"All":L} line (${f1(lp)})`},
    ...STATS.map(s=>({k:s,h:s+(per?"/G":""),v:r=>statVal(r.st,s,r.gp,per,asPts),f:f1,scale:"seq",rev:()=>s==="TO"&&!asPts})),
    {k:"upg",h:"Upgrade over",l:1,sv:r=>r.upg,v:r=>r.upg,f:v=>v==null?"":`+${f1(v)} vs ${esc(weak.name)}`,tip:"PPG gain over your weakest Active player at this position, same window"},
  ];
  drawTable(cols, rows, Wv, null);
}

/* ---------- Scatter ---------- */
const SC={pts:[], pinned:false};
const lastName = n => { const p=n.split(" "); while (p.length>1 && /^(jr\.?|sr\.?|ii|iii|iv|v)$/i.test(p[p.length-1])) p.pop(); return p[p.length-1]; };
function niceStep(range, target){
  const raw=range/Math.max(1,target), mag=Math.pow(10,Math.floor(Math.log10(raw))), n=raw/mag;
  return (n<1.5?1:n<3?2:n<7?5:10)*mag;
}
function ticks(lo, hi, target){
  const st=niceStep(hi-lo,target), out=[];
  for (let v=Math.ceil(lo/st)*st; v<=hi+1e-9; v+=st) out.push(Math.round(v*1000)/1000);
  return out;
}
function drawScatter(){
  const Wv=S.wire, w=Wv.win, L=Wv.pos, posName = L==="ALL" ? "All positions" : L;
  wireControls(false);
  $("linesbox").innerHTML="";
  const line=D.lines[w][L], lp=line.ppg, weak=D.weakest[w][L];
  const fa=addGaps(D.fa[w].filter(r=>(L==="ALL"||r.pos.includes(L)) && r.ppg!=null && r.gp>0).map(r=>Object.assign({},r)), lp, weak);
  const mine=addGaps(myRows(w, L), lp, weak);
  const top5=new Set(fa.filter(r=>r.q).sort((a,b)=>b.ppg-a.ppg).slice(0,5).map(r=>r.name));
  const pts=[];
  for (const r of fa){
    const dq=!r.q;
    pts.push({r, cat: dq?"dq":(r.pool.includes(L)?"pool":"fa"), gray: dq && !Wv.disq, label: !dq && top5.has(r.name)});
  }
  for (const r of mine) pts.push({r, cat:"mine", gray:!Wv.mine, label:Wv.mine});
  SC.pts=pts; SC.pinned=false;

  const n=k=>pts.filter(p=>p.cat===k).length;
  $("scatline").innerHTML = `<b>${LLAB[w]}, ${posName}:</b> replacement line ${lp==null?"n/a":f1(lp)+" PPG"} from ${line.n} free agent${line.n===1?"":"s"} (min ${line.min_gp} GP).` +
    (weak ? ` Your weakest active player here: <b>${esc(weak.name)}</b>, ${f1(weak.ppg)} PPG.` : "");
  $("scatlegend").innerHTML =
    `<span><i style="background:var(--paint)"></i>My team (${n("mine")})${Wv.mine?"":" grayed"}</span>`+
    `<span><i style="background:var(--orange)"></i>★ Replacement pool (${n("pool")})</span>`+
    `<span><i style="background:#8f877b"></i>Other free agents (${n("fa")})</span>`+
    `<span><i style="background:#fff;border:2px solid #8f877b;width:9px;height:9px"></i>Disqualified (${n("dq")})${Wv.disq?"":" grayed"}</span>`+
    `<span><i class="ln"></i>Replacement line</span>`+
    (weak?`<span><i class="ln wk"></i>Your weakest</span>`:"");

  const host=$("scatsvg");
  if (!pts.length){ host.innerHTML=`<p class="empty">No players to plot for this position and window.</p>`; return; }

  const Wd=Math.max(320, Math.round($("scatwrap").clientWidth-12));
  const H=Math.round(Math.min(620, Math.max(360, Wd<600 ? Wd*1.05 : Wd*0.58)));
  const m={l:52, r:18, t:14, b:44};
  const xs=pts.map(p=>p.r.fp), ys=pts.map(p=>p.r.ppg);
  if (lp!=null) ys.push(lp);
  if (weak) ys.push(weak.ppg);
  const x0=0, x1=Math.max(...xs)*1.06 || 10;
  let y0=Math.min(...ys), y1=Math.max(...ys);
  const pad=(y1-y0)*0.08 || 2; y1+=pad; y0-=pad;
  const yst=niceStep(y1-y0,6); y0=Math.floor(y0/yst)*yst;
  const X=v=>m.l+(v-x0)/(x1-x0)*(Wd-m.l-m.r);
  const Y=v=>H-m.b-(v-y0)/(y1-y0)*(H-m.t-m.b);

  let g=`<svg viewBox="0 0 ${Wd} ${H}" role="img" aria-label="Total fantasy points versus points per game">`;
  for (const t of ticks(y0,y1,6)) g+=`<line x1="${m.l}" x2="${Wd-m.r}" y1="${Y(t)}" y2="${Y(t)}" stroke="#ece6db"/><text x="${m.l-6}" y="${Y(t)+4}" text-anchor="end" font-size="11" fill="#7a7166">${t}</text>`;
  for (const t of ticks(x0,x1,Wd<600?5:8)) g+=`<line y1="${m.t}" y2="${H-m.b}" x1="${X(t)}" x2="${X(t)}" stroke="#f2ede4"/><text x="${X(t)}" y="${H-m.b+16}" text-anchor="middle" font-size="11" fill="#7a7166">${t}</text>`;
  g+=`<line x1="${m.l}" x2="${Wd-m.r}" y1="${H-m.b}" y2="${H-m.b}" stroke="#bfb3a0"/><line x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${H-m.b}" stroke="#bfb3a0"/>`;
  g+=`<text x="${(m.l+Wd-m.r)/2}" y="${H-6}" text-anchor="middle" font-size="12" font-weight="700" fill="#2b2620">Total fantasy points</text>`;
  g+=`<text transform="translate(14 ${(m.t+H-m.b)/2}) rotate(-90)" text-anchor="middle" font-size="12" font-weight="700" fill="#2b2620">Fantasy points per game</text>`;

  // reference lines, labels placed away from dots and from each other
  const placed=[];
  const nearDot=b=>pts.some(p=>{ if (p.gray) return false; const dx=X(p.r.fp), dy=Y(p.r.ppg); return dx>b.x-8 && dx<b.x+b.w+8 && dy>b.y-8 && dy<b.y+b.h+8; });
  const overlaps=b=>placed.some(q=>b.x<q.x+q.w && b.x+b.w>q.x && b.y<q.y+q.h && b.y+b.h>q.y);
  function refLine(val, txt, color, dash){
    const yy=Y(val), tw=txt.length*6.3, th=13;
    const opts=[{x:Wd-m.r-4-tw,y:yy-5-th},{x:m.l+6,y:yy-5-th},{x:Wd-m.r-4-tw,y:yy+4},{x:m.l+6,y:yy+4}].map(o=>Object.assign({w:tw,h:th},o));
    const box=opts.find(o=>!nearDot(o)&&!overlaps(o)) || opts.find(o=>!overlaps(o)) || opts[0];
    placed.push(box);
    g+=`<line x1="${m.l}" x2="${Wd-m.r}" y1="${yy}" y2="${yy}" stroke="${color}" stroke-width="1.6" stroke-dasharray="${dash}"/>`;
    return `<text x="${box.x}" y="${box.y+th-2}" font-size="11.5" font-weight="700" fill="${color}" paint-order="stroke" stroke="#fff" stroke-width="3">${esc(txt)}</text>`;
  }
  let refText="";
  if (lp!=null) refText+=refLine(lp, `Replacement line ${f1(lp)}`, "#d9651e", "6 4");
  if (weak) refText+=refLine(weak.ppg, `Your weakest: ${lastName(weak.name)} ${f1(weak.ppg)}`, "#3d6fb6", "2 3");

  // dots: grayed first, then disqualified, free agents, pool, mine on top
  const order={dq:1, fa:2, pool:3, mine:4};
  const idx=pts.map((p,i)=>i).sort((a,b)=>(pts[a].gray?0:order[pts[a].cat])-(pts[b].gray?0:order[pts[b].cat]));
  for (const i of idx){
    const p=pts[i], cx=X(p.r.fp), cy=Y(p.r.ppg);
    let fill, stroke, sw=1, op=1, rad=5.5;
    if (p.gray){ fill="#d8d2c8"; stroke="#d8d2c8"; op=0.5; rad=4.5; }
    else if (p.cat==="mine"){ fill="#3d6fb6"; stroke="#fff"; sw=1.5; rad=7; }
    else if (p.cat==="pool"){ fill="#d9651e"; stroke="#fff"; sw=1.5; rad=6; }
    else if (p.cat==="dq"){ fill="#fff"; stroke="#8f877b"; sw=2; }
    else { fill="#8f877b"; stroke="#fff"; }
    g+=`<circle class="dot" data-i="${i}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${rad}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" opacity="${op}"/>`;
  }
  g+=refText;

  // labels with collision avoidance; my players always labeled, crowded free agent labels dropped
  const hit=a=>overlaps(a) || pts.some(p=>{ if (p.gray) return false; const dx=X(p.r.fp), dy=Y(p.r.ppg); return dx>a.x-3 && dx<a.x+a.w+3 && dy>a.y-3 && dy<a.y+a.h+3; });
  const lab=idx.filter(i=>pts[i].label && !pts[i].gray).reverse();
  const lnCount={}; lab.forEach(i=>{ const k=lastName(pts[i].r.name); lnCount[k]=(lnCount[k]||0)+1; });
  const area=b=>placed.reduce((s,q)=>s+Math.max(0,Math.min(b.x+b.w,q.x+q.w)-Math.max(b.x,q.x))*Math.max(0,Math.min(b.y+b.h,q.y+q.h)-Math.max(b.y,q.y)),0);
  for (const i of lab){
    const p=pts[i], cx=X(p.r.fp), cy=Y(p.r.ppg), ln=lastName(p.r.name);
    const txt=lnCount[ln]>1 ? p.r.name[0]+". "+ln : ln, tw=txt.length*6.9+4, th=13;
    const cands=[[cx+9,cy-th/2],[cx-9-tw,cy-th/2],[cx-tw/2,cy-9-th],[cx-tw/2,cy+9],[cx+9,cy-th-4],[cx+9,cy+4],[cx-9-tw,cy-th-4],[cx-9-tw,cy+4]];
    let pick=null;
    for (const [x,y] of cands){
      const box={x,y,w:tw,h:th};
      if (x<m.l || x+tw>Wd-m.r || y<m.t || y+th>H-m.b) continue;
      if (!hit(box)){ pick=box; break; }
    }
    if (!pick){
      if (p.cat!=="mine") continue;  // crowded: drop free agent labels (hover still works), always label my players
      // pick the spot that overlaps other labels the least
      let best=null, bestA=Infinity;
      for (const [x0c,yc] of cands){
        const b={x:Math.max(m.l, Math.min(x0c, Wd-m.r-tw)), y:Math.max(m.t, Math.min(yc, H-m.b-th)), w:tw, h:th};
        const a=area(b); if (a<bestA){ bestA=a; best=b; }
      }
      pick=best;
    }
    placed.push(pick);
    const col=p.cat==="mine" ? "#24508f" : "#a9480f";
    g+=`<text x="${pick.x+2}" y="${pick.y+th-3}" font-size="11.5" font-weight="700" fill="${col}" paint-order="stroke" stroke="#fff" stroke-width="3" pointer-events="none">${esc(txt)}</text>`;
  }
  g+=`</svg>`;
  host.innerHTML=g;
  $("tip").hidden=true;
}
function showTip(i, evt){
  const p=SC.pts[i]; if (!p) return;
  const r=p.r, tip=$("tip"), wrap=$("scatwrap");
  const kind = p.cat==="mine" ? "My team" + (r.status==="Injured" ? " (Injured)" : "")
             : p.cat==="pool" ? "★ Replacement pool"
             : p.cat==="dq" ? "Disqualified: " + esc(r.why) : "Free agent";
  tip.innerHTML = `<b>${esc(r.name)}</b>${tagHtml(r.tag)}${r.wv?'<span class="tag wv">Waivers</span>':""}<br>`+
    `<span class="k">${esc(r.team)} · ${esc(r.pos.join(","))} · ${kind}</span><br>`+
    `<span class="k">Own</span> ${pct(r.own)} &nbsp; <span class="k">GP</span> ${f0(r.gp)} &nbsp; <span class="k">MPG</span> ${f1(r.mpg)}<br>`+
    `<span class="k">PPG</span> <b>${f1(r.ppg)}</b> &nbsp; <span class="k">Total FP</span> <b>${f0(r.fp)}</b><br>`+
    `<span class="k">vs line</span> ${sg1(r.gap)} PPG` +
    (r.upg!=null ? `<br><span class="k">Upgrade over</span> ${esc(D.weakest[S.wire.win][S.wire.pos].name)} <b>+${f1(r.upg)}</b>` : "");
  tip.hidden=false;
  const wr=wrap.getBoundingClientRect();
  let x=evt.clientX-wr.left+14, y=evt.clientY-wr.top+14;
  const tw=tip.offsetWidth, th=tip.offsetHeight;
  if (x+tw>wr.width-4) x=evt.clientX-wr.left-tw-14;
  if (y+th>wr.height-4) y=evt.clientY-wr.top-th-14;
  tip.style.left=Math.max(4,x)+"px"; tip.style.top=Math.max(4,y)+"px";
  document.querySelectorAll("svg .dot.hot").forEach(d=>d.classList.remove("hot"));
  const dot=document.querySelector(`svg .dot[data-i="${i}"]`); if (dot) dot.classList.add("hot");
}
function hideTip(){
  const t=$("tip"); if (t) t.hidden=true;
  document.querySelectorAll("svg .dot.hot").forEach(d=>d.classList.remove("hot"));
}
document.addEventListener("mousemove", e=>{
  if (S.page!=="scatter" || SC.pinned) return;
  const d=e.target.closest && e.target.closest("svg .dot");
  if (d) showTip(+d.dataset.i, e); else hideTip();
});
document.addEventListener("click", e=>{
  if (S.page!=="scatter") return;
  const d=e.target.closest && e.target.closest("svg .dot");
  if (d){ SC.pinned=true; showTip(+d.dataset.i, e); }
  else if (!e.target.closest("button")){ SC.pinned=false; hideTip(); }
});
let scatTimer=null;
window.addEventListener("resize", ()=>{ if (S.page!=="scatter") return; clearTimeout(scatTimer); scatTimer=setTimeout(drawScatter,150); });

/* ---------- page ---------- */
function render(){
  $("pg-team").classList.toggle("on", S.page==="team");
  $("pg-wire").classList.toggle("on", S.page==="wire");
  $("pg-scatter").classList.toggle("on", S.page==="scatter");
  $("tablearea").hidden = S.page==="scatter";
  $("scatarea").hidden = S.page!=="scatter";
  if (S.page==="team") drawTeam(); else if (S.page==="wire") drawWire(); else drawScatter();
}
function go(p){ S.page=p; try{ history.replaceState(null,"",p==="team"?location.pathname:"#"+p); }catch(e){} render(); }
$("pg-team").onclick=()=>go("team");
$("pg-wire").onclick=()=>go("wire");
$("pg-scatter").onclick=()=>go("scatter");
if (location.hash==="#scatter") S.page="scatter";
else if (location.hash==="#wire") S.page="wire";
$("mast").textContent=D.meta.masthead;
$("sub").textContent=`${D.meta.team} · ${D.meta.season_label}`;
if (D.warnings.length){
  $("warn").innerHTML=`<div class="warnbar"><b>Data check</b><ul>${D.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul></div>`;
}
$("foot").textContent=`Updated ${D.meta.updated}` + (D.meta.pull_date?` · Sheet pulled ${D.meta.pull_date}`:"") +
  ` · Flags use ${LLAB[D.meta.flag_window]} · Replace? below ${D.meta.replace_threshold} pts`;
render();
</script>
</body>
</html>
"""


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")  # never close the script tag early
    page = (PAGE.replace("__TITLE__", html.escape(data["meta"]["masthead"]))
                .replace("__DATA__", payload))
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {OUT_PATH} ({len(page):,} bytes)")


if __name__ == "__main__":
    main()
