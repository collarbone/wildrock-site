#!/usr/bin/env python3
"""Round-3 type studies, inspired by owner's moodboard loves: 17, 19, 35, 46, 51, 55, 73.
Run: brand/tools/.venv/bin/python brand/04-directions/studies/build.py
Writes per-study spec/svg/png into this folder and a self-contained studies.html.
"""
import json, os, re, subprocess, sys
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "../../tools"))
FONTS = os.path.join(TOOLS, "fonts")
INST = os.path.join(FONTS, "_instances")
PY = sys.executable
os.makedirs(INST, exist_ok=True)


def inst(rel, **axes):
    """Static instance of a (variable) font, cached."""
    src = os.path.join(FONTS, rel)
    if not axes:
        return src
    tag = "_".join(f"{k}{int(v)}" for k, v in sorted(axes.items()))
    out = os.path.join(INST, os.path.basename(src).split("[")[0].replace(".ttf", "") + f"-{tag}.ttf")
    if not os.path.exists(out):
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        f = TTFont(src)
        full = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        full.update(axes)
        instantiateVariableFont(f, full, inplace=True)
        f.save(out)
    return out


def width(font, text, size, tracking=0):
    f = ImageFont.truetype(font, 1000)
    w = sum(f.getlength(c) for c in text) * size / 1000
    return w + tracking * size / 1000 * (len(text) - 1)


def T(font, text, x, y, size, tracking=0):
    return {"type": "text", "font": font, "text": text, "x": x, "y": y, "size": size, "tracking": tracking}


# ---------- fonts ----------
FR_I = inst("fraunces/Fraunces-Italic[SOFT,WONK,opsz,wght].ttf", opsz=72, wght=480, SOFT=30, WONK=0)
FR_R = inst("fraunces/Fraunces[SOFT,WONK,opsz,wght].ttf", opsz=72, wght=480, SOFT=30, WONK=0)
FR_I6 = inst("fraunces/Fraunces-Italic[SOFT,WONK,opsz,wght].ttf", opsz=72, wght=600, SOFT=0, WONK=0)
HK6 = inst("hankengrotesk/HankenGrotesk[wght].ttf", wght=620)
HK7 = inst("hankengrotesk/HankenGrotesk[wght].ttf", wght=720)
MAN4 = inst("manrope/Manrope[wght].ttf", wght=430)
MAN5 = inst("manrope/Manrope[wght].ttf", wght=560)
MARC = inst("marcellus/Marcellus-Regular.ttf")
BOD = inst("bodonimoda/BodoniModa[opsz,wght].ttf", opsz=28, wght=640)

S = 200  # base type size (design units)
studies = []


def study(key, name, ref, note, elements, w, h, ink, bg, fav, pad=24):
    studies.append(dict(key=key, name=name, ref=ref, note=note, ink=ink, bg=bg,
                        spec={"width": w, "height": h, "pad": pad, "elements": elements}, fav=fav))


# S1 — onesalt: italic "wild" fused with roman "rock", lowercase, same family
x = 0; el = []
el.append(T(FR_I, "wild", x, 200, S)); x += width(FR_I, "wild", S) - 2
el.append(T(FR_R, "rock", x, 200, S)); x += width(FR_R, "rock", S)
study("s1", "Fused Serif", "51 onesalt · 46 unearth",
      "One serif family, two voices: *wild* in italic, rock upright. Lowercase, no gap — reads as one word, says two things.",
      el, x, 250, "#1E2A6B", "#EEE8DE", [T(FR_I, "w", 6, 150, 200)])

# S2 — unearth: italic serif "wild" + grotesk "rock"
x = 0; el = []
el.append(T(FR_I6, "wild", x, 200, S)); x += width(FR_I6, "wild", S) + 2
el.append(T(HK6, "rock", x, 200, S, -15)); x += width(HK6, "rock", S, -15)
study("s2", "Serif + Grotesk", "46 unearth",
      "Human italic serif meets a precise grotesk. The switch happens at the seam between wild and rock.",
      el, x, 250, "#1F1E1B", "#F4F1EB", [T(FR_I6, "w", 4, 150, 200)])

# S3 — Architexture: bold grotesk "Wild" + italic serif "rock"
x = 0; el = []
el.append(T(HK7, "Wild", x, 200, S, -20)); x += width(HK7, "Wild", S, -20) + 4
el.append(T(FR_I, "rock", x, 200, S)); x += width(FR_I, "rock", S)
study("s3", "Grotesk + Italic Swap", "55 Architexture",
      "Solid grotesk carries the name; the italic serif 'rock' is the moment of craft. Title case for warmth.",
      el, x, 250, "#1F1E1B", "#EFEFF0", [T(HK7, "W", 2, 160, 200, 0)])

# S4 — PINES: calm flared capitals, wide tracking
tr = 260; el = [T(MARC, "WILDROCK", 0, 170, 170, tr)]
study("s4", "Quiet Capitals", "17 Pines",
      "Flared, chiselled capitals with generous air. Stone-carved calm; the most timeless and the strongest from the street.",
      el, width(MARC, "WILDROCK", 170, tr), 200, "#E9E2CF", "#253229", [T(MARC, "W", 6, 160, 190)])

# S5 — MORADA: geometric spaced caps + stacked descriptor
tr = 120; wm = width(MAN4, "WILDROCK", 150, tr)
el = [T(MAN4, "WILDROCK", 0, 160, 150, tr),
      T(MAN5, "CUSTOM", wm + 34, 86, 30, 220), T(MAN5, "HOMES", wm + 34, 128, 30, 220)]
study("s5", "Studio Caps + Descriptor", "19 Morada",
      "Clean geometric caps with a tiny stacked descriptor — reads like an architecture practice. Descriptor is swappable.",
      el, wm + 34 + width(MAN5, "CUSTOM", 30, 220), 190, "#FFFFFF", "#9C7A5B", [T(MAN4, "W", 10, 150, 170)])

# S6 — Allan Visses: drawn signature monogram + tracked caps (original strokes)
nib = {"angle": 40, "ratio": 0.16}
sig = [
    {"type": "stroke", "points": [[150, 58], [162, 130], [178, 196], [200, 128], [214, 100], [230, 160], [244, 194], [262, 120], [290, 40]], "width": 24, "nib": nib, "taper": [0.5, 1]},
    {"type": "stroke", "points": [[312, 122], [309, 160], [306, 196]], "width": 20, "nib": nib},
    {"type": "stroke", "points": [[308, 156], [324, 128], [348, 118], [368, 124]], "width": 20, "nib": nib, "taper": [1, 0.45]},
    {"type": "stroke", "points": [[96, 236], [220, 220], [360, 212], [478, 198]], "width": 11, "taper": [0.2, 1]},
    {"type": "ellipse", "cx": 498, "cy": 194, "rx": 8, "ry": 8},
]
tr = 520; cw = width(MAN4, "WILDROCK", 40, tr)
el = sig + [T(MAN4, "WILDROCK", (600 - cw) / 2, 330, 40, tr)]
study("s6", "Signature Monogram", "35 Allan Visses",
      "A hand-drawn W r signature (original strokes, flat-pen angle) with a quick ridgeline flourish, over precise tracked caps.",
      el, 600, 350, "#1F1E1B", "#FFFFFF",
      [{"type": "stroke", "points": [[20, 40], [50, 175], [85, 95], [118, 178], [168, 25]], "width": 34, "nib": nib, "taper": [0.6, 1]}])

# S7 — Vella: high-contrast didone, title case, closing period (gesture to develop if chosen)
el = [T(BOD, "Wildrock.", 0, 200, S, -10)]
study("s7", "Didone, Assured", "73 Vella",
      "Exclusive high-contrast serif in title case with a closing period — confident and fashion-adjacent. A custom ligature/gesture would be developed if chosen.",
      el, width(BOD, "Wildrock.", S, -10), 250, "#FFFFFF", "#1C1C1C", [T(BOD, "W", 4, 165, 190)])

# S8 — hybrid stack: big italic 'wild' over spaced caps ROCK, same width (sign lockup)
ww = width(FR_I, "wild", 230)
tr = 0
for _ in range(30):  # solve tracking so ROCK matches width of 'wild'
    rw = width(MARC, "ROCK", 110, tr)
    tr += (ww - rw) / (110 / 1000 * 3) * 0.5
el = [T(FR_I, "wild", 0, 190, 230), T(MARC, "ROCK", 6, 330, 110, tr)]
study("s8", "Stacked: wild / ROCK", "51 + 17",
      "The italic voice on top, chiselled capitals beneath — a compact block built for the yard sign and the avatar.",
      el, ww + 10, 350, "#2B3A2F", "#ECE6D8", [T(FR_I, "w", 6, 150, 200)])


# ---------- render ----------
def run_render(spec, svg, png=None):
    sp = svg.replace(".svg", ".json")
    json.dump(spec, open(sp, "w"), indent=1)
    cmd = [PY, os.path.join(TOOLS, "shapes.py"), "render", sp, svg, "--scale", "3"]
    if png:
        cmd += ["--png", png]
    subprocess.run(cmd, check=True, capture_output=True)
    s = open(svg).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    d = re.search(r' d="([^"]+)"', s).group(1)
    return vb, d


for st in studies:
    k = st["key"]
    st["vb"], st["d"] = run_render(st["spec"], os.path.join(HERE, f"{k}.svg"), os.path.join(HERE, f"{k}.png"))
    fav = {"width": 200, "height": 200, "pad": 0, "elements": st["fav"]}
    st["fvb"], st["fd"] = run_render(fav, os.path.join(HERE, f"{k}-favicon.svg"))
    print("rendered", k)


def svg(vb, d, fill, style=""):
    return f'<svg viewBox="{vb}" style="{style}" xmlns="http://www.w3.org/2000/svg"><path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>'


cards = ""
for i, st in enumerate(studies, 1):
    cards += f'''<article class="card"><div class="hero" style="background:{st['bg']}">{svg(st['vb'], st['d'], st['ink'])}</div>
<div class="row"><div class="sign"><div class="board">{svg(st['vb'], st['d'], '#F4F1EB')}<small>CUSTOM HOMES · (555) 010-0000</small></div><div class="post"></div></div>
<div class="favs"><div class="tile" style="background:{st['bg']}">{svg(st['fvb'], st['fd'], st['ink'])}</div><div class="tile s32" style="background:{st['bg']}">{svg(st['fvb'], st['fd'], st['ink'])}</div><div class="tile s16" style="background:{st['bg']}">{svg(st['fvb'], st['fd'], st['ink'])}</div>
<div class="small">{svg(st['vb'], st['d'], '#1F1E1B')}</div></div></div>
<div class="meta"><div class="eyebrow">Study {i} · inspired by {st['ref']}</div><h3>{st['name']}</h3><p>{st['note']}</p>
<div class="act"><button class="up" data-id="{i}">👍</button><button class="down" data-id="{i}">👎</button><input class="note" data-id="{i}" placeholder="note"></div></div></article>'''

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wildrock Studies</title>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Newsreader:ital,opsz,wght@1,6..72,300&display=swap" rel="stylesheet">
<style>
:root{{--bg:#F4F1EB;--card:#fff;--ink:#1F1E1B;--muted:#6E6A62;--line:#E2DDD3}}
*{{box-sizing:border-box;margin:0}}body{{background:var(--bg);color:var(--ink);font:400 15px/1.5 "Inter Tight",system-ui,sans-serif;padding:40px 16px 120px}}
.wrap{{max-width:1240px;margin:0 auto}}h1{{font:300 clamp(30px,4.5vw,48px)/1.1 "Newsreader",serif;font-style:italic;margin:8px 0}}
.eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}header p{{color:var(--muted);max-width:720px;margin-bottom:32px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:20px}}
.card{{background:var(--card);border:2px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}}
.card.love{{border-color:#2F6B3F}}.card.no{{opacity:.45}}
.hero{{height:220px;display:flex;align-items:center;justify-content:center;padding:28px}}.hero svg{{max-width:100%;max-height:100%;width:auto;height:auto}}
.row{{display:flex;gap:14px;padding:16px;border-top:1px solid var(--line);align-items:flex-end;background:linear-gradient(#DCE3E3,#C9D1C4 70%,#A9B39C 70%)}}
.sign{{display:flex;flex-direction:column;align-items:center}}.board{{background:#1F1E1B;width:170px;padding:16px 12px 10px;display:flex;flex-direction:column;align-items:center;gap:8px;border-radius:2px}}
.board svg{{width:100%;max-height:56px}}.board small{{color:#F4F1EB;font-size:7px;letter-spacing:.14em}}.post{{width:6px;height:34px;background:#5c5a55}}
.favs{{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;flex:1;justify-content:flex-end}}
.tile{{width:64px;height:64px;border-radius:12px;display:flex;align-items:center;justify-content:center;padding:10px}}.tile svg{{width:100%;height:100%}}
.tile.s32{{width:32px;height:32px;border-radius:7px;padding:5px}}.tile.s16{{width:16px;height:16px;border-radius:3px;padding:2px}}
.small{{width:100%;display:flex;justify-content:flex-end}}.small svg{{width:110px;height:auto;max-height:30px;background:#fff;padding:4px}}
.meta{{padding:14px 18px 18px;display:flex;flex-direction:column;gap:6px}}.meta h3{{font-size:18px;font-weight:600}}.meta p{{color:var(--muted);font-size:14px}}
.act{{display:flex;gap:8px;margin-top:6px}}.act button{{border:1px solid var(--line);background:transparent;border-radius:8px;padding:4px 10px;font-size:16px;cursor:pointer}}
.card.love .up{{background:#2F6B3F}}.card.no .down{{background:#A23B2A}}.note{{flex:1;border:1px solid var(--line);border-radius:6px;padding:5px 8px;font:inherit;font-size:13px}}
.bar{{position:fixed;left:0;right:0;bottom:0;background:var(--ink);color:var(--bg);padding:12px 16px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap}}
.bar button{{background:var(--bg);color:var(--ink);border:0;border-radius:8px;padding:8px 16px;font:600 14px "Inter Tight";cursor:pointer}}.bar textarea{{width:min(560px,100%);height:40px;font:12px monospace;border-radius:6px;padding:6px}}
</style></head><body><div class="wrap"><header><div class="eyebrow">Wildrock · Round 3 · Type studies from your moodboard picks (17, 19, 35, 46, 51, 55, 73)</div>
<h1>Eight quick studies. Pick the voice, then we refine.</h1>
<p>Each study shows the wordmark in its own palette, on a jobsite sign, as a favicon (64 / 32 / 16 px) and at small size. All letterforms are outlined SVG (fonts used as scaffolding are open-licence; the signature is drawn). These are directions, not finished logos — spacing and details get tuned after you choose.</p></header>
<div class="grid">{cards}</div></div>
<div class="bar"><span id="count"></span><button id="copy">Copy my picks</button><textarea id="out" readonly placeholder="your picks appear here"></textarea></div>
<script>
const K='wildrock-studies-r3';let st={{}};try{{st=JSON.parse(localStorage.getItem(K)||'{{}}')}}catch(e){{}}
const cards=[...document.querySelectorAll('.card')];
function save(){{try{{localStorage.setItem(K,JSON.stringify(st))}}catch(e){{}}render()}}
function render(){{let l=0;cards.forEach((c,i)=>{{const s=st[i+1]||{{}};c.classList.toggle('love',s.v==='love');c.classList.toggle('no',s.v==='no');const n=c.querySelector('.note');if(document.activeElement!==n)n.value=s.note||'';if(s.v==='love')l++}});document.getElementById('count').textContent=l+' loved'}}
cards.forEach((c,i)=>{{const id=i+1,g=()=>st[id]=st[id]||{{}};c.querySelector('.up').onclick=()=>{{g().v=st[id].v==='love'?'':'love';save()}};c.querySelector('.down').onclick=()=>{{g().v=st[id].v==='no'?'':'no';save()}};c.querySelector('.note').oninput=e=>{{g().note=e.target.value;save()}}}});
document.getElementById('copy').onclick=()=>{{const ids=Object.keys(st).sort((a,b)=>a-b);const love=ids.filter(i=>st[i].v==='love'),no=ids.filter(i=>st[i].v==='no'),notes=ids.filter(i=>st[i].note).map(i=>'S'+i+': '+st[i].note);
const t='Studies love: '+(love.join(', ')||'-')+' · No: '+(no.join(', ')||'-')+(notes.length?' · Notes: '+notes.join('; '):'');const o=document.getElementById('out');o.value=t;o.select();try{{navigator.clipboard.writeText(t)}}catch(e){{document.execCommand('copy')}}}};
render();
</script></body></html>'''
open(os.path.join(HERE, "studies.html"), "w").write(html)
print("wrote studies.html")
