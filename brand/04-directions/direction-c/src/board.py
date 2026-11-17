import re, sys, os
D = sys.argv[1]
INK = "#1C1B19"


def load(name):
    s = open(os.path.join(D, name)).read().strip()
    s = s.replace(f'fill="{INK}"', 'fill="currentColor"')
    s = re.sub(r"<title>.*?</title>", "", s)
    return s


def vb(name):
    return re.search(r'viewBox="([^"]+)"', open(os.path.join(D, name)).read()).group(1)


def inner(name):
    s = load(name)
    return re.search(r"<g .*</g>", s, re.S).group(0)


def nest(name, x, y, w, h, fill):
    """nested <svg> for use inside a larger SVG scene"""
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb(name)}">'
            + inner(name).replace('fill="currentColor"', f'fill="{fill}"') + "</svg>")


def img(name, cls="", label="Wildrock"):
    s = load(name)
    return s.replace("<svg ", f'<svg class="{cls}" aria-label="{label}" ', 1).replace(
        'role="img" aria-label="Wildrock mark"', 'role="img"').replace(
        'role="img" aria-label="Wildrock"', 'role="img"')


WM = img("wordmark.svg", "wm")
MARK = lambda c="": img("mark.svg", c, "Wildrock mark")
FAV = img("favicon.svg", "fav", "Wildrock favicon")
LH = lambda c="": img("lockup-horizontal.svg", c)
LS = lambda c="": img("lockup-stacked.svg", c)

BONE, CLAY, SAGE, SAND = "#EEE9E0", "#A65A3A", "#7E8B74", "#CDBFA8"

# ---------- yard sign scene ----------
sign = f'''<svg class="scene" viewBox="0 0 960 560" role="img" aria-label="Jobsite yard sign in a high-desert landscape">
<rect width="960" height="560" fill="#E7E1D6"/>
<circle cx="760" cy="250" r="54" fill="{CLAY}" opacity=".85"/>
<polygon points="0,300 120,240 210,270 330,190 450,260 560,215 700,275 820,230 960,265 960,560 0,560" fill="{SAND}"/>
<polygon points="0,360 140,320 260,345 400,300 540,350 680,320 820,355 960,330 960,560 0,560" fill="{SAGE}"/>
<rect y="420" width="960" height="140" fill="#B7A98F"/>
<rect y="420" width="960" height="6" fill="#A39579"/>
<rect x="318" y="300" width="14" height="190" fill="{INK}"/>
<rect x="628" y="300" width="14" height="190" fill="{INK}"/>
<rect x="300" y="150" width="360" height="230" fill="{INK}"/>
{nest("lockup-stacked.svg", 340, 186, 280, 130.4, BONE)}
<rect x="340" y="338" width="280" height="2" fill="{BONE}" opacity=".35"/>
<text x="340" y="362" fill="{BONE}" font-family="Instrument Sans, system-ui, sans-serif" font-size="13" letter-spacing="3">CUSTOM HOMES</text>
<text x="620" y="362" fill="{BONE}" text-anchor="end" font-family="Instrument Sans, system-ui, sans-serif" font-size="13" letter-spacing="1.5">wildrock.build</text>
<rect x="0" y="490" width="960" height="70" fill="#AD9F84"/>
</svg>'''

# ---------- watermark scene ----------
water = f'''<svg class="scene" viewBox="0 0 640 400" role="img" aria-label="Single-colour watermark over a landscape photograph">
<rect width="640" height="400" fill="#5F6656"/>
<polygon points="0,210 90,160 170,190 260,120 360,185 450,150 540,195 640,170 640,400 0,400" fill="#4C5446"/>
<polygon points="0,280 120,250 240,272 360,236 500,276 640,250 640,400 0,400" fill="#3D4438"/>
<rect y="330" width="640" height="70" fill="#353A30"/>
<g opacity=".22">{nest("mark.svg", 410, 60, 180, 180, "#FFFFFF")}</g>
<g opacity=".9">{nest("wordmark.svg", 32, 356, 150, 16.95, "#FFFFFF")}</g>
</svg>'''

html = open(os.path.join(os.path.dirname(__file__), "board.tpl.html")).read()
for k, v in {
    "{{WM}}": WM, "{{MARK_L}}": MARK("m-lg"), "{{M64}}": MARK("m64"), "{{M32}}": MARK("m32"),
    "{{M16}}": FAV.replace('class="fav"', 'class="m16"'), "{{LH}}": LH("lh"), "{{LS}}": LS("ls"),
    "{{LH_D}}": LH("lh"), "{{LS_D}}": LS("ls"), "{{SIGN}}": sign, "{{WATER}}": water,
    "{{FAV}}": FAV, "{{MARK_AV}}": MARK("av"), "{{MARK_HDR}}": MARK("hdr-m"),
    "{{WM_HDR}}": WM.replace('class="wm"', 'class="hdr-wm"'),
    "{{WM_SPEC}}": WM.replace('class="wm"', 'class="spec-wm"'),
    "{{MARK_SPEC}}": MARK("spec-m"),
}.items():
    html = html.replace(k, v)
open(os.path.join(D, "board.html"), "w").write(html)
print("ok", len(html))
