#!/usr/bin/env python3
"""shapes.py — draw custom letterforms / marks from a JSON spec and trace them to clean SVG.

Not limited to fonts: build letters from brush strokes (tapered or calligraphic-nib),
polygons, rectangles, ellipses/arcs, and negative-space cuts. Fonts (any TTF/OTF on disk)
can be used as a starting layer and then cut/extended. Output is a single-colour,
outlined SVG (cubic Béziers via potrace), plus an optional PNG preview to inspect.

Commands
  shapes.py render SPEC.json OUT.svg [--png PREVIEW.png] [--scale 4] [--fill #1F1E1B]
  shapes.py trace  IMAGE.png OUT.svg [--threshold 128] [--invert] [--fill #1F1E1B]

Spec format (coordinates in a design grid; y down; units arbitrary, e.g. 1000-wide):
{
  "width": 1000, "height": 300, "pad": 20,
  "elements": [
    {"type": "stroke", "points": [[x,y],...], "width": 40,
     "smooth": true,              # Catmull-Rom through points (default true)
     "taper": [0.2, 1.0],         # width multiplier at start / end (optional; signature feel)
     "nib": {"angle": 30, "ratio": 0.25},  # calligraphic flat pen (optional; overrides round brush)
     "cap": "round" | "flat"},
    {"type": "poly", "points": [[x,y],...]},                 # filled polygon
    {"type": "rect", "x":0, "y":0, "w":10, "h":10, "r": 0},  # r = corner radius
    {"type": "ellipse", "cx":0, "cy":0, "rx":10, "ry":10},
    {"type": "arc", "cx":0, "cy":0, "r":50, "start":180, "end":360, "width":20},  # stroked arc, degrees
    {"type": "text", "font": "path/to/font.ttf", "text": "WILD", "x":0, "y":250,   # y = baseline
     "size": 200, "axes": {"wght": 700}, "tracking": 0},
    ... any element may add  "erase": true  to cut it out (negative space)
  ]
}
Elements are painted in order, so an erase only cuts what was drawn before it.

Requires: Pillow, numpy, potracer (pip install pillow numpy potracer).
"""
import argparse
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---------- geometry helpers ----------
def catmull_rom(pts, samples=24):
    if len(pts) < 3:
        return [tuple(p) for p in pts]
    P = [pts[0]] + [tuple(p) for p in pts] + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                       + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def densify(path, step):
    out = [path[0]]
    for a, b in zip(path, path[1:]):
        d = math.dist(a, b)
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


# ---------- painting ----------
def paint(draw, el, S, ox, oy):
    col = 0 if el.get("erase") else 255
    X = lambda x: (x + ox) * S
    Y = lambda y: (y + oy) * S
    t = el["type"]
    if t == "poly":
        draw.polygon([(X(x), Y(y)) for x, y in el["points"]], fill=col)
    elif t == "rect":
        box = [X(el["x"]), Y(el["y"]), X(el["x"] + el["w"]), Y(el["y"] + el["h"])]
        draw.rounded_rectangle(box, radius=el.get("r", 0) * S, fill=col)
    elif t == "ellipse":
        draw.ellipse([X(el["cx"] - el["rx"]), Y(el["cy"] - el["ry"]),
                      X(el["cx"] + el["rx"]), Y(el["cy"] + el["ry"])], fill=col)
    elif t == "arc":
        r, w = el["r"], el["width"]
        pts = [(el["cx"] + r * math.cos(math.radians(a)), el["cy"] + r * math.sin(math.radians(a)))
               for a in np.linspace(el["start"], el["end"], 90)]
        paint(draw, {"type": "stroke", "points": pts, "width": w, "smooth": False,
                     "cap": el.get("cap", "flat"), "erase": el.get("erase")}, S, ox, oy)
    elif t == "stroke":
        pts = [tuple(p) for p in el["points"]]
        path = catmull_rom(pts) if el.get("smooth", True) else pts
        path = densify(path, step=max(0.5, el["width"] / 12))
        n = len(path)
        t0, t1 = el.get("taper", [1, 1])
        nib = el.get("nib")
        for i, (x, y) in enumerate(path):
            f = t0 + (t1 - t0) * (i / max(1, n - 1))
            w = el["width"] * f
            if nib:
                ang = math.radians(nib["angle"])
                hw, hh = w / 2, max(0.6, w * nib.get("ratio", 0.25) / 2)
                ca, sa = math.cos(ang), math.sin(ang)
                corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
                draw.polygon([(X(x + cx * ca - cy * sa), Y(y + cx * sa + cy * ca)) for cx, cy in corners], fill=col)
            else:
                r = w / 2
                draw.ellipse([X(x - r), Y(y - r), X(x + r), Y(y + r)], fill=col)
        if el.get("cap") == "flat" and not nib:
            pass  # round dabs approximate caps; use poly/rect for hard flat terminals
    elif t == "text":
        font = ImageFont.truetype(el["font"], int(el["size"] * S))
        if el.get("axes"):
            try:
                font.set_variation_by_axes([el["axes"].get(a["name"] if isinstance(a, dict) else a, None)
                                            for a in font.get_variation_axes()])
            except Exception:
                axes = font.get_variation_axes()
                vals = []
                for a in axes:
                    tag = a.get("name", b"").decode() if isinstance(a.get("name"), bytes) else a.get("name", "")
                    key = {"Weight": "wght", "Width": "wdth", "Optical size": "opsz"}.get(tag, tag)
                    vals.append(el["axes"].get(key, a.get("default", a["minimum"])))
                font.set_variation_by_axes(vals)
        x = X(el["x"])
        tr = el.get("tracking", 0) * el["size"] / 1000 * S
        for ch in el["text"]:
            draw.text((x, Y(el["y"])), ch, font=font, fill=col, anchor="ls")
            x += font.getlength(ch) + tr
    else:
        raise ValueError(f"unknown element type {t}")


def render(spec, scale=4):
    W, H, pad = spec["width"], spec["height"], spec.get("pad", 0)
    img = Image.new("L", (int((W + 2 * pad) * scale), int((H + 2 * pad) * scale)), 0)
    d = ImageDraw.Draw(img)
    for el in spec["elements"]:
        paint(d, el, scale, pad, pad)
    return img


# ---------- tracing ----------
def trace_bitmap(mask, scale, offset, turdsize=4, alphamax=1.0, opttolerance=0.2):
    import potrace
    bm = potrace.Bitmap(~mask)  # potracer treats False as ink; our mask is True = ink
    plist = bm.trace(turdsize=turdsize, alphamax=alphamax, opticurve=True, opttolerance=opttolerance)
    def f(p):
        x, y = (p.x, p.y) if hasattr(p, "x") else (p[0], p[1])
        return f"{x / scale - offset:.2f} {y / scale - offset:.2f}"
    parts = []
    for curve in plist:
        parts.append(f"M{f(curve.start_point)}")
        for seg in curve.segments:
            if seg.is_corner:
                parts.append(f"L{f(seg.c)}L{f(seg.end_point)}")
            else:
                parts.append(f"C{f(seg.c1)} {f(seg.c2)} {f(seg.end_point)}")
        parts.append("Z")
    return "".join(parts)


def to_svg(d, w, h, fill):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>\n')


def cmd_render(a):
    spec = json.load(open(a.spec))
    img = render(spec, a.scale)
    if a.png:
        prev = Image.eval(img, lambda v: 255 - v)
        prev.thumbnail((1600, 1600))
        prev.save(a.png)
    mask = np.array(img) > 127
    pad = spec.get("pad", 0)
    d = trace_bitmap(mask, a.scale, 0)
    w, h = spec["width"] + 2 * pad, spec["height"] + 2 * pad
    open(a.out, "w").write(to_svg(d, w, h, a.fill))
    print(f"wrote {a.out} ({len(d)} chars path){' + ' + a.png if a.png else ''}")


def cmd_trace(a):
    img = Image.open(a.image).convert("L")
    arr = np.array(img)
    mask = arr < a.threshold
    if a.invert:
        mask = ~mask
    d = trace_bitmap(mask, 1, 0)
    open(a.out, "w").write(to_svg(d, img.width, img.height, a.fill))
    print(f"wrote {a.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("spec"); r.add_argument("out")
    r.add_argument("--png"); r.add_argument("--scale", type=float, default=4)
    r.add_argument("--fill", default="#1F1E1B")
    t = sub.add_parser("trace")
    t.add_argument("image"); t.add_argument("out")
    t.add_argument("--threshold", type=int, default=128); t.add_argument("--invert", action="store_true")
    t.add_argument("--fill", default="#1F1E1B")
    a = ap.parse_args()
    {"render": cmd_render, "trace": cmd_trace}[a.cmd](a)


if __name__ == "__main__":
    main()
