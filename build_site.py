"""Build internships.html from data/listings.json, styled like the portfolio.

Run:   python build_site.py      then open internships.html in your browser.
Fonts are read from assets/fonts and embedded, so the page is one self-contained file.
"""

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "data" / "listings.json"
OUT = ROOT / "internships.html"
FONT_DIR = ROOT / "assets" / "fonts"

FONTS = [
    ("Instrument Serif", "normal", 400, "instrument-serif-latin-400-normal.woff2"),
    ("Instrument Serif", "italic", 400, "instrument-serif-latin-400-italic.woff2"),
    ("Space Grotesk", "normal", 400, "space-grotesk-latin-400-normal.woff2"),
    ("Space Grotesk", "normal", 500, "space-grotesk-latin-500-normal.woff2"),
    ("Space Grotesk", "normal", 700, "space-grotesk-latin-700-normal.woff2"),
    ("JetBrains Mono", "normal", 400, "jetbrains-mono-latin-400-normal.woff2"),
    ("JetBrains Mono", "normal", 500, "jetbrains-mono-latin-500-normal.woff2"),
]


def font_css() -> str:
    out = []
    for family, style, weight, name in FONTS:
        path = FONT_DIR / name
        if not path.exists():
            print(f"warning: missing font {path}; falling back to system fonts")
            continue
        b64 = base64.b64encode(path.read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "\n".join(out)


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Internship Tracker</title>
<meta name="description" content="Tech internships in India, collected from official company career pages.">
<meta name="theme-color" content="#050506">
<style>
__FONTS__
:root{
  --bg:#050506; --fg:#f4f2ee; --muted:rgba(244,242,238,.58); --faint:rgba(244,242,238,.34); --line:rgba(244,242,238,.13);
  --blue:#3d5afe; --orange:#ff7a2f;
  --serif:'Instrument Serif','Times New Roman',serif; --sans:'Space Grotesk',system-ui,sans-serif; --mono:'JetBrains Mono',ui-monospace,monospace;
  --pad:clamp(20px,4.2vw,72px); --ease:cubic-bezier(.2,.8,.2,1);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);color-scheme:dark;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--fg);font:400 16px/1.6 var(--sans);overflow-x:clip;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none} ul{list-style:none} button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
::selection{background:var(--orange);color:#000}
:focus-visible{outline:2px solid var(--orange);outline-offset:4px;border-radius:4px}
.mono{font:400 11px/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase}
.display{font-family:var(--serif);font-weight:400;line-height:.98;letter-spacing:-.015em}
.display em,.name em{font-style:italic;color:var(--orange)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

.spot{position:fixed;inset:0;z-index:1;pointer-events:none;background:radial-gradient(520px circle at var(--mx,50%) var(--my,50%),rgba(61,90,254,.11),transparent 62%)}
.progress{position:fixed;top:0;left:0;right:0;height:2px;z-index:60;pointer-events:none}
.progress i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--orange));transform:scaleX(0);transform-origin:left}

.cursor{position:fixed;left:0;top:0;z-index:90;pointer-events:none;display:none}
@media (hover:hover) and (pointer:fine){.cursor{display:block}body.has-cursor,body.has-cursor a,body.has-cursor button,body.has-cursor input,body.has-cursor select{cursor:none}}
.c-dot{position:absolute;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;background:var(--fg);mix-blend-mode:difference}
.c-ring{position:absolute;width:38px;height:38px;margin:-19px 0 0 -19px;border-radius:50%;border:1px solid rgba(244,242,238,.45);display:grid;place-items:center;transition:width .35s var(--ease),height .35s var(--ease),margin .35s var(--ease),background .3s,border-color .3s}
.c-label{font:500 10px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--fg);opacity:0;transition:opacity .2s}
.cursor.hot .c-ring{width:76px;height:76px;margin:-38px 0 0 -38px;background:rgba(244,242,238,.1);border-color:rgba(244,242,238,.55);backdrop-filter:blur(3px)}
.cursor.hot .c-label{opacity:1}.cursor.hot .c-dot{opacity:0}
.cursor.link .c-ring{width:56px;height:56px;margin:-28px 0 0 -28px;border-color:var(--orange)}

/* nav */
.nav{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;justify-content:center;padding:12px var(--pad);pointer-events:none;transition:transform .6s var(--ease)}
.nav.hide{transform:translateY(-120%)}
.pill-nav{pointer-events:auto;display:flex;align-items:center;gap:clamp(12px,2vw,32px);width:min(980px,100%);padding:8px 10px 8px 22px;border:1px solid var(--line);border-radius:99px;background:rgba(10,11,16,.62);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}
.nav-logo{font-family:var(--serif);font-size:24px;line-height:1;margin-right:auto;white-space:nowrap}
.nav-logo span{font-style:italic;color:var(--orange)}
.nav-logo .nm{font:500 13px var(--sans);font-style:normal;color:var(--muted);margin-left:8px}
.nav-links{display:flex;gap:clamp(18px,2.6vw,38px);font-size:14px}
.nav-links a{color:var(--muted);transition:color .3s;padding:4px 0}.nav-links a:hover{color:var(--fg)}
.nav-pill{padding:10px 18px;border-radius:99px;background:var(--fg);color:#000;font:500 13px var(--sans);white-space:nowrap;transition:background .3s}
.nav-pill:hover{background:var(--orange)}
@media (max-width:700px){.nav-logo .nm{display:none}.nav-links{display:none}}

/* hero */
.hero{position:relative;z-index:2;min-height:100vh;min-height:100svh;display:grid;grid-template-columns:minmax(0,6fr) minmax(0,5fr);gap:clamp(16px,3vw,48px);align-items:center;padding:110px var(--pad) 90px}
.hello{color:var(--orange);margin-bottom:18px}
.name{font-family:var(--serif);font-weight:400;text-transform:uppercase;font-size:clamp(46px,min(8.6vw,15vh),150px);line-height:.86;letter-spacing:-.025em}
.mask{display:block;overflow:hidden;padding:.04em 0 .1em;margin-bottom:-.06em}
.line{display:inline-block;transform:translateY(105%);animation:up 1.1s var(--ease) forwards}
.mask:nth-child(2) .line{animation-delay:.12s}
@keyframes up{to{transform:none}}
.role{font-family:var(--serif);font-style:italic;font-size:clamp(24px,3vw,48px);line-height:1.08;margin-top:clamp(18px,3vh,32px)}
.tagline{margin-top:14px;color:var(--muted);font-size:clamp(14px,1.15vw,17px);max-width:44ch}
.intro{margin-top:24px;max-width:46ch;color:var(--faint);font-size:13.5px;line-height:1.7;border-left:1px solid var(--line);padding-left:16px}
.stage{position:relative;height:min(64vh,560px);min-height:260px}
.stage canvas{position:absolute;inset:0;width:100%;height:100%}
.hero-meta{position:absolute;bottom:34px;left:var(--pad);display:flex;gap:14px;color:var(--faint)}
.hero-cue{position:absolute;right:var(--pad);bottom:34px;display:flex;align-items:center;gap:12px;color:var(--faint)}
.hero-cue i{width:1px;height:44px;background:linear-gradient(var(--fg),transparent);transform-origin:top;animation:drip 2s var(--ease) infinite}
@keyframes drip{0%{transform:scaleY(0)}50%{transform:scaleY(1)}100%{transform:scaleY(1);opacity:0}}
@media (max-width:900px){.hero{grid-template-columns:1fr;padding-top:96px;align-content:start}.stage{order:-1;height:34vh;min-height:200px}.hero-meta,.hero-cue{display:none}}

/* sections */
.sec{position:relative;z-index:2;padding:clamp(70px,11vh,150px) var(--pad) clamp(40px,8vh,90px)}
.sec-head{display:flex;align-items:center;gap:18px;margin-bottom:clamp(24px,4vh,48px);color:var(--muted)}
.sec-head .rule{flex:1;height:1px;background:var(--line);transform-origin:left;transform:scaleX(0);transition:transform 1.4s var(--ease)}
.sec-head.in .rule{transform:scaleX(1)}
.display.lg{font-size:clamp(38px,5.4vw,88px);max-width:18ch}

/* filters */
.filters{position:relative;z-index:20;margin-top:clamp(28px,5vh,56px);padding:14px 0 12px;display:grid;gap:12px}
@media (min-width:901px){.filters{position:sticky;top:70px;background:linear-gradient(var(--bg) 78%,transparent)}}
.search input{width:100%;font:400 clamp(24px,3vw,40px)/1.2 var(--serif);color:var(--fg);background:none;border:0;border-bottom:1px solid var(--line);padding:6px 0 12px;border-radius:0;outline:none;transition:border-color .4s}
.search input::placeholder{color:var(--faint)}
.search input:focus{border-color:var(--orange)}
.pills{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;align-items:center;padding-bottom:2px}
.pills::-webkit-scrollbar{display:none}
.pills .sp{flex:none;width:1px;height:20px;background:var(--line);margin:0 6px}
.pills button,.pills select{flex:none;font:400 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:8px 14px;border:1px solid var(--line);border-radius:99px;color:var(--fg);background:none;transition:background .3s,color .3s,border-color .3s}
.pills select{background:var(--bg);appearance:none;padding-right:14px}
.pills button:hover,.pills select:hover{border-color:var(--faint)}
.pills button[aria-pressed=true]{background:var(--orange);border-color:var(--orange);color:#000}
.count{color:var(--faint);margin-top:4px}

/* listings */
.group{margin-top:clamp(28px,5vh,56px)}
.group h2{display:flex;align-items:baseline;gap:14px;font:400 clamp(30px,3.4vw,52px)/1 var(--serif);font-style:italic;padding-bottom:12px}
.group h2 small{font:400 11px var(--mono);font-style:normal;letter-spacing:.08em;color:var(--orange)}
.lks{border-top:1px solid var(--line)}
.lk{position:relative;display:grid;grid-template-columns:2.6em minmax(0,1.7fr) minmax(0,1fr) auto 1.4em;align-items:center;gap:clamp(12px,2.4vw,36px);padding:clamp(16px,2.6vh,26px) 0;border-bottom:1px solid var(--line);overflow:hidden}
.lk::before{content:"";position:absolute;inset:0;background:rgba(244,242,238,.07);box-shadow:inset 0 0 0 1px rgba(244,242,238,.12);transform:translateY(101%);transition:transform .6s var(--ease);z-index:0}
.lk>*{position:relative;z-index:1;transition:color .4s,border-color .4s,background .4s}
.lk:hover::before,.lk:focus-visible::before{transform:none}
.lk:hover .co,.lk:focus-visible .co{color:var(--orange)}
.lk .k{font:400 11px var(--mono);letter-spacing:.08em;color:var(--faint)}
.lk .co{display:block;font:400 clamp(28px,3.6vw,56px)/1 var(--serif);overflow-wrap:anywhere}
.lk .ti{display:block;margin-top:6px;color:var(--muted);font-size:clamp(14px,1.1vw,16px);overflow-wrap:anywhere}
.lk .meta{display:grid;gap:4px;font:400 11px/1.5 var(--mono);letter-spacing:.04em;color:var(--muted);min-width:0}
.lk .meta b{font-weight:400;color:var(--faint)}
.lk .age{font:500 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:6px 12px;border:1px solid var(--line);border-radius:99px;white-space:nowrap;color:var(--fg)}
.lk .age.fresh{background:var(--orange);border-color:var(--orange);color:#000}
.lk:hover .age:not(.fresh){border-color:var(--faint)}
.lk .a{font-size:clamp(20px,2.2vw,34px);transition:transform .5s var(--ease)}
.lk:hover .a{transform:translate(6px,-6px)}
.lk.closed .co,.lk.closed .ti{color:var(--faint)}
.lk.closed:hover .co{color:var(--orange)}
.empty{padding:60px 0;color:var(--muted)}
.empty b{display:block;font:400 clamp(34px,4vw,60px)/1 var(--serif);color:var(--fg);margin-bottom:14px}
.empty button{margin-top:22px;padding:13px 24px;border:1px solid var(--fg);border-radius:99px;font:500 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;transition:background .4s,color .4s}
.empty button:hover{background:var(--fg);color:#000}
@media (max-width:760px){
  .lk{grid-template-columns:minmax(0,1fr) auto;gap:8px 12px}
  .lk .k{display:none}.lk .who{grid-column:1}.lk .age{grid-column:2;grid-row:1;align-self:start}
  .lk .meta{grid-column:1/-1}.lk .a{display:none}
}

/* notes */
.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));margin-top:clamp(28px,5vh,56px);border-top:1px solid var(--line)}
.facts div{padding:20px 20px 22px 0;border-bottom:1px solid var(--line)}
.facts dt{color:var(--orange);margin-bottom:8px}
.facts dd{font-size:14.5px;line-height:1.55;color:var(--fg)}
@media (max-width:600px){.facts{grid-template-columns:1fr}}
.foot{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px;margin-top:clamp(50px,9vh,110px);color:var(--faint);padding-top:22px;border-top:1px solid var(--line)}
.foot a:hover{color:var(--orange)}
.pad-b{height:40px}
@media (prefers-reduced-motion:reduce){.line{animation:none;transform:none}.hero-cue i{animation:none}.lk::before,.sec-head .rule{transition:none}}
</style>
</head>
<body>
<div class="spot" aria-hidden="true"></div>
<div class="cursor" aria-hidden="true"><i class="c-dot"></i><i class="c-ring"><b class="c-label"></b></i></div>
<div class="progress" aria-hidden="true"><i></i></div>

<header class="nav" id="nav">
  <div class="pill-nav">
    <a class="nav-logo" href="#top" aria-label="Internship tracker, back to top">IT<span>.</span><span class="nm">Internship tracker</span></a>
    <nav class="nav-links" aria-label="Primary"><a href="#list">Listings</a><a href="#notes">Notes</a></nav>
    <a class="nav-pill" href="#list" id="navCount">Browse</a>
  </div>
</header>

<main id="top">
<section class="hero">
  <div class="hero-text">
    <p class="mono hello" id="hello"></p>
    <h1 class="name" aria-label="Internship tracker">
      <span class="mask"><span class="line">Internship</span></span>
      <span class="mask"><span class="line">Tracker<em>.</em></span></span>
    </h1>
    <p class="role" id="role"></p>
    <p class="tagline">Tech internships in India, collected straight from company career pages.</p>
    <p class="intro">Every Apply button opens the company's own site. Nobody here will ever ask you for money.</p>
  </div>
  <div class="stage" id="stage"><canvas id="gl" aria-hidden="true"></canvas><span class="sr" id="srCount"></span></div>
  <div class="hero-meta mono"><span>(01)</span><span>Live tracker</span></div>
  <div class="hero-cue mono"><span>Scroll</span><i></i></div>
</section>

<section class="sec" id="list">
  <div class="sec-head"><span class="mono">(02)</span><span class="mono">Listings</span><i class="rule"></i></div>
  <h2 class="display lg">Find a role <em>worth applying to.</em></h2>

  <div class="filters">
    <div class="search"><input id="q" type="search" placeholder="Search company, role or city" aria-label="Search internships" autocomplete="off"></div>
    <div class="pills" id="pills" role="group" aria-label="Filters"></div>
  </div>
  <p class="mono count" id="count" aria-live="polite"></p>
  <div id="out"></div>
</section>

<section class="sec" id="notes">
  <div class="sec-head"><span class="mono">(03)</span><span class="mono">Notes</span><i class="rule"></i></div>
  <dl class="facts">
    <div><dt class="mono">Source</dt><dd>Official company career pages, checked on a schedule.</dd></div>
    <div><dt class="mono">Last data</dt><dd id="fBuilt"></dd></div>
    <div><dt class="mono">Coverage</dt><dd id="fCover"></dd></div>
    <div><dt class="mono">Staying safe</dt><dd>Apply only on the company's own site. Real internships never ask you to pay.</dd></div>
  </dl>
  <div class="foot mono"><span>Internship Tracker</span><a href="#top">Back to top</a></div>
  <div class="pad-b"></div>
</section>
</main>

<script>
const DATA = __DATA__;
const BUILT = "__BUILT__";
const LABEL = {swe:"Software",data_ml:"Data and ML",product:"Product",core:"Core engineering",hardware:"Hardware",quant:"Quant",other:"Other"};
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl = u => /^https?:\/\//i.test(u) ? u : "#";
const DAY = 864e5, REDUCE = matchMedia("(prefers-reduced-motion:reduce)").matches;
const state = {status:"open", cat:"", sort:"new"};
const parse = iso => new Date(iso.length > 10 ? iso : iso + "T00:00:00");
const daysAgo = iso => iso ? Math.max(0, Math.floor((Date.now() - parse(iso).getTime()) / DAY)) : null;
const fmt = iso => iso ? parse(iso).toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"}) : "";

const open = DATA.filter(d => d.status === "open");
const nCo = new Set(open.map(d => d.company)).size;
const nAll = new Set(DATA.map(d => d.company)).size;
$("hello").textContent = `Updated ${fmt(BUILT)}`;
$("role").textContent = `${open.length} open ${open.length === 1 ? "role" : "roles"} across ${nCo} ${nCo === 1 ? "company" : "companies"}.`;
$("srCount").textContent = `${open.length} open internships`;
$("navCount").textContent = `${open.length} open`;
$("fBuilt").textContent = fmt(BUILT);
$("fCover").textContent = `${nAll} companies seen so far, ${nCo} with open internships. A company that blocked the last check keeps its older listings.`;

/* ---------- filter pills ---------- */
const cats = [...new Set(DATA.map(d => d.category))].sort((a,b) => (a==="other") - (b==="other") || a.localeCompare(b));
function pills(){
  const b = (k, v, t, on) => `<button data-k="${k}" data-v="${esc(v)}" aria-pressed="${on}">${esc(t)}</button>`;
  $("pills").innerHTML =
    [["open","Open"],["closed","Closed"],["","All"]].map(([v,t]) => b("status", v, t, state.status === v)).join("") +
    '<i class="sp"></i>' +
    [["","Everything"], ...cats.map(c => [c, LABEL[c] || c])].map(([v,t]) => b("cat", v, t, state.cat === v)).join("") +
    '<i class="sp"></i>' +
    `<select id="sort" aria-label="Sort"><option value="new">Newest first</option><option value="co">Company A to Z</option></select>`;
  $("sort").value = state.sort;
  $("sort").onchange = e => { state.sort = e.target.value; render(); };
}
$("pills").addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  state[b.dataset.k] = b.dataset.v; pills(); render();
});
$("q").addEventListener("input", render);
pills();

/* ---------- list ---------- */
const BUCKETS = ["Posted today","This week","This month","Earlier"];
const bucket = d => d === null ? 3 : d === 0 ? 0 : d <= 7 ? 1 : d <= 30 ? 2 : 3;
const two = n => String(n).padStart(2, "0");

function rowHtml(d, i){
  const e = d.enrichment || {}, isOpen = d.status === "open";
  const age = daysAgo(d.date_posted || d.first_seen);
  const chip = isOpen ? `<span class="age ${age === 0 ? "fresh" : ""}">${age === null ? "n/a" : age === 0 ? "New" : age + " d"}</span>`
                      : `<span class="age">Closed</span>`;
  const meta = [
    `<span>${esc((d.locations || []).join("; ") || "Location not listed")}</span>`,
    `<span><b>${esc(LABEL[d.category] || d.category)}</b>${d.is_remote ? " / Remote" : ""}${e.duration_months ? " / " + e.duration_months + " months" : ""}${e.eligible_batches && e.eligible_batches.length ? " / Batch " + esc(e.eligible_batches.join(", ")) : ""}${e.stipend ? " / " + esc(e.stipend) : ""}</span>`,
    !isOpen && d.closed_at ? `<span><b>Closed ${esc(fmt(d.closed_at))}</b></span>` : ""
  ].join("");
  return `<a class="lk ${isOpen ? "" : "closed"}" href="${esc(safeUrl(d.url))}" target="_blank" rel="noopener noreferrer" data-cursor="Apply" aria-label="${esc(d.title)} at ${esc(d.company)}. Opens the company's careers page.">
    <span class="k">${two(i + 1)}</span>
    <span class="who"><span class="co">${esc(d.company)}</span><span class="ti">${esc(d.title)}</span></span>
    <span class="meta">${meta}</span>${chip}<span class="a" aria-hidden="true">↗</span></a>`;
}

function render(){
  const q = $("q").value.trim().toLowerCase();
  const rows = DATA.filter(d =>
    (!state.status || d.status === state.status) && (!state.cat || d.category === state.cat) &&
    (!q || (d.company + " " + d.title + " " + (d.locations || []).join(" ")).toLowerCase().includes(q)));
  const byCo = state.sort === "co";
  rows.sort(byCo ? (a,b) => a.company.localeCompare(b.company) || a.title.localeCompare(b.title)
                 : (a,b) => (b.date_posted || b.first_seen || "").localeCompare(a.date_posted || a.first_seen || ""));
  $("count").textContent = `${rows.length} ${rows.length === 1 ? "listing" : "listings"}`;
  if (!rows.length){
    $("out").innerHTML = `<div class="empty"><b>Nothing matches.</b>Try a shorter search, or show every category.<br><button id="reset">Clear filters</button></div>`;
    $("reset").onclick = () => { $("q").value = ""; state.cat = ""; state.status = "open"; pills(); render(); };
    return;
  }
  if (byCo || state.status !== "open"){
    $("out").innerHTML = `<div class="group"><div class="lks">${rows.map(rowHtml).join("")}</div></div>`; return;
  }
  const g = [[],[],[],[]];
  rows.forEach(d => g[bucket(daysAgo(d.date_posted || d.first_seen))].push(d));
  let n = 0;
  $("out").innerHTML = g.map((list, i) => list.length
    ? `<section class="group"><h2>${BUCKETS[i]} <small>${list.length}</small></h2><div class="lks">${list.map(d => rowHtml(d, n++)).join("")}</div></section>` : "").join("");
}
render();

/* ---------- section rule reveal ---------- */
const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && (e.target.classList.add("in"), io.unobserve(e.target))), {threshold:.4});
document.querySelectorAll(".sec-head").forEach(el => io.observe(el));

/* ---------- progress, nav hide, spotlight ---------- */
const bar = document.querySelector(".progress i"), nav = $("nav"); let lastY = 0;
addEventListener("scroll", () => {
  const y = scrollY, max = document.documentElement.scrollHeight - innerHeight;
  bar.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
  nav.classList.toggle("hide", y > lastY && y > 160); lastY = y;
}, {passive:true});
const spot = document.querySelector(".spot");
addEventListener("pointermove", e => { spot.style.setProperty("--mx", e.clientX + "px"); spot.style.setProperty("--my", e.clientY + "px"); }, {passive:true});

/* ---------- cursor ---------- */
if (matchMedia("(hover:hover) and (pointer:fine)").matches){
  document.body.classList.add("has-cursor");
  const cur = document.querySelector(".cursor"), label = document.querySelector(".c-label");
  let x = -99, y = -99, cx_ = -99, cy_ = -99;
  addEventListener("pointermove", e => { x = e.clientX; y = e.clientY; });
  (function tick(){ cx_ += (x - cx_) * .2; cy_ += (y - cy_) * .2; cur.style.transform = `translate(${cx_}px,${cy_}px)`; requestAnimationFrame(tick); })();
  document.addEventListener("pointerover", e => {
    const hot = e.target.closest("[data-cursor]"), link = e.target.closest("a,button,select,input");
    cur.classList.toggle("hot", !!hot); cur.classList.toggle("link", !hot && !!link);
    label.textContent = hot ? hot.dataset.cursor : "";
  });
}

/* ---------- hero: particles assemble into the open count ---------- */
(function hero(){
  const stage = $("stage"), cv = $("gl"), ctx = cv.getContext("2d"), num = String(open.length);
  let W = 0, H = 0, dpr = 1, parts = [], t0 = 0, mouse = {x:-9999, y:-9999}, raf = 0;
  function build(){
    const r = stage.getBoundingClientRect(); dpr = Math.min(2, devicePixelRatio || 1);
    W = Math.max(50, Math.round(r.width)); H = Math.max(50, Math.round(r.height));
    cv.width = W * dpr; cv.height = H * dpr;
    const off = document.createElement("canvas"); off.width = W; off.height = H;
    const o = off.getContext("2d"); let fs = H * 1.1;
    o.font = `${fs}px "Instrument Serif", serif`;
    const w = o.measureText(num).width; if (w > W * .96) fs *= W * .96 / w;
    o.font = `${fs}px "Instrument Serif", serif`; o.textAlign = "center"; o.fillStyle = "#fff";
    const m = o.measureText(num); o.fillText(num, W / 2, (H + m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2);
    const px = o.getImageData(0, 0, W, H).data, step = Math.max(4, Math.round(W / 105)); parts = [];
    for (let y = 0; y < H; y += step) for (let x = 0; x < W; x += step) if (px[(y * W + x) * 4 + 3] > 128){
      const c = Math.random();
      parts.push({tx:x, ty:y, x:0, y:0, sx:Math.random() * W, sy:H * (.9 + Math.random() * .6), vx:0, vy:0,
        d:Math.random() * .5, r:step * (.34 + Math.random() * .22),
        c: c < .72 ? "rgba(244,242,238,.92)" : c < .92 ? "#ff7a2f" : "#3d5afe"});
    }
  }
  function frame(now){
    const t = (now - t0) / 1000; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    for (const p of parts){
      const k = REDUCE ? 1 : Math.min(1, Math.max(0, (t - p.d) / 1.9));
      if (k < 1){ const e = 1 - Math.pow(1 - k, 4); p.x = p.sx + (p.tx - p.sx) * e; p.y = p.sy + (p.ty - p.sy) * e; p.vx = p.vy = 0; }
      else {
        const dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < 12100){ const d = Math.sqrt(d2) || 1, f = (110 - d) / 110; p.vx += dx / d * f * 2.4; p.vy += dy / d * f * 2.4; }
        p.vx += (p.tx - p.x) * .06; p.vy += (p.ty - p.y) * .06; p.vx *= .84; p.vy *= .84; p.x += p.vx; p.y += p.vy;
      }
      ctx.fillStyle = p.c; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
    }
    if (!REDUCE || t < 0.1) raf = requestAnimationFrame(frame);
  }
  function start(replay){ cancelAnimationFrame(raf); build(); t0 = performance.now() - (replay ? 0 : 4000); raf = requestAnimationFrame(frame); }
  stage.addEventListener("pointermove", e => { const r = stage.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
  stage.addEventListener("pointerleave", () => { mouse.x = mouse.y = -9999; });
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => start(false), 200); });
  const go = () => start(true);
  (document.fonts && document.fonts.load ? document.fonts.load('100px "Instrument Serif"').then(go, go) : Promise.resolve().then(go));
})();
</script>
</body>
</html>
"""


def main() -> int:
    if not SRC.exists():
        print(f"Missing {SRC}. Run the tracker first.")
        return 1
    data = json.loads(SRC.read_text(encoding="utf-8"))
    keep = (
        "company",
        "title",
        "url",
        "category",
        "status",
        "locations",
        "date_posted",
        "first_seen",
        "closed_at",
        "is_remote",
        "enrichment",
    )
    slim = [{k: d.get(k) for k in keep} for d in data]
    payload = json.dumps(slim, ensure_ascii=False).replace("</", "<\\/")
    built = max((d.get("last_seen") or "" for d in data), default="unknown")
    html = (
        TEMPLATE.replace("__FONTS__", font_css())
        .replace("__DATA__", payload)
        .replace("__BUILT__", built)
    )
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(slim)} listings. Open it in your browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())