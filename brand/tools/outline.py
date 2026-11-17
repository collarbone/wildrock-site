#!/usr/bin/env python3
"""Convert text set in a TTF (static or variable) into outlined SVG path data.

Usage (CLI):
  outline.py FONT.ttf "TEXT" [--size 100] [--axes wght=800,wdth=75]
             [--tracking 50] [--kern "LD=-20,RO=-10"] [--svg out.svg] [--fill #000]

  --size      font size in SVG user units (cap height ~= 0.7 * size for most fonts)
  --tracking  extra letter spacing in 1/1000 em (like CSS letter-spacing in em*1000)
  --kern      manual pair adjustments in 1/1000 em, e.g. "AV=-60,LD=-20"
              (font GPOS kerning is also applied for simple pair kerning when available)
  --axes      variable-font axis values

Library use:
  from outline import outline
  d, bbox, advance = outline(font, text, size=100, axes={"wght": 800}, tracking=0, kern={})
  # d is SVG path data positioned with baseline at y=0 (text extends into negative y);
  # bbox = (xmin, ymin, xmax, ymax) in the same coordinates; advance = total advance width.

Requires fontTools (venv: <scratchpad>/venv/bin/python).
"""
import argparse
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

_cache = {}


def load(path, axes=None):
    key = (path, tuple(sorted((axes or {}).items())))
    if key in _cache:
        return _cache[key]
    f = TTFont(path)
    if "fvar" in f:
        from fontTools.varLib.instancer import instantiateVariableFont
        defaults = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        loc = {**defaults, **(axes or {})}
        f = instantiateVariableFont(f, loc, inplace=False)
    _cache[key] = f
    return f


def _gpos_pairs(font):
    """Collect simple PairPos format-1/2 kerning (x advance) into a dict."""
    pairs = {}
    if "GPOS" not in font:
        return pairs
    gpos = font["GPOS"].table
    if not gpos.LookupList:
        return pairs
    for lookup in gpos.LookupList.Lookup:
        subtables = lookup.SubTable
        if lookup.LookupType == 9:
            subtables = [s.ExtSubTable for s in subtables]
        elif lookup.LookupType != 2:
            continue
        for st in subtables:
            if getattr(st, "LookupType", 2) != 2 and lookup.LookupType != 9:
                continue
            if not hasattr(st, "Format"):
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for i, first in enumerate(cov):
                    ps = st.PairSet[i]
                    for pvr in ps.PairValueRecord:
                        v = pvr.Value1
                        xa = getattr(v, "XAdvance", 0) if v else 0
                        if xa:
                            pairs.setdefault((first, pvr.SecondGlyph), xa)
            elif st.Format == 2:
                cd1 = st.ClassDef1.classDefs
                cd2 = st.ClassDef2.classDefs
                second_by_class = {}
                for g, c in cd2.items():
                    second_by_class.setdefault(c, []).append(g)
                for first in cov:
                    c1 = cd1.get(first, 0)
                    rec = st.Class1Record[c1]
                    for c2, r2 in enumerate(rec.Class2Record):
                        v = r2.Value1
                        xa = getattr(v, "XAdvance", 0) if v else 0
                        if not xa:
                            continue
                        for second in second_by_class.get(c2, []):
                            pairs.setdefault((first, second), xa)
    return pairs


def outline(font_path, text, size=100, axes=None, tracking=0, kern=None, use_gpos=True):
    font = load(font_path, axes)
    upm = font["head"].unitsPerEm
    scale = size / upm
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    gpos = _gpos_pairs(font) if use_gpos else {}
    kern = kern or {}

    pen = SVGPathPen(gs)
    bpen = BoundsPen(gs)
    x = 0.0
    prev_char = prev_glyph = None
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            raise ValueError(f"glyph for {ch!r} not in font {font_path}")
        if prev_glyph is not None:
            x += gpos.get((prev_glyph, gname), 0)
            x += kern.get(prev_char + ch, 0) * upm / 1000
        # flip y: font units are y-up, SVG is y-down
        t = (1, 0, 0, -1, x, 0)
        gs[gname].draw(TransformPen(pen, t))
        gs[gname].draw(TransformPen(bpen, t))
        x += hmtx[gname][0] + tracking * upm / 1000
        prev_char, prev_glyph = ch, gname
    x -= tracking * upm / 1000  # no trailing tracking

    # scale path commands: re-render with scaling transform instead of string math
    pen2 = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    x2 = 0.0
    prev_char = prev_glyph = None
    for ch in text:
        gname = cmap.get(ord(ch))
        if prev_glyph is not None:
            x2 += gpos.get((prev_glyph, gname), 0)
            x2 += kern.get(prev_char + ch, 0) * upm / 1000
        t = (scale, 0, 0, -scale, x2 * scale, 0)
        gs[gname].draw(TransformPen(pen2, t))
        x2 += hmtx[gname][0] + tracking * upm / 1000
        prev_char, prev_glyph = ch, gname

    b = bpen.bounds or (0, 0, 0, 0)
    bbox = tuple(round(v * scale, 2) for v in b)
    return pen2.getCommands(), bbox, round(x * scale, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("text")
    ap.add_argument("--size", type=float, default=100)
    ap.add_argument("--axes", default="")
    ap.add_argument("--tracking", type=float, default=0)
    ap.add_argument("--kern", default="")
    ap.add_argument("--svg")
    ap.add_argument("--fill", default="#1F1E1B")
    ap.add_argument("--pad", type=float, default=0)
    a = ap.parse_args()
    axes = {k: float(v) for k, v in (p.split("=") for p in a.axes.split(",") if p)}
    kern = {k: float(v) for k, v in (p.split("=") for p in a.kern.split(",") if p)}
    d, (x0, y0, x1, y1), adv = outline(a.font, a.text, a.size, axes, a.tracking, kern)
    if a.svg:
        p = a.pad
        vb = f"{x0 - p:.2f} {y0 - p:.2f} {x1 - x0 + 2 * p:.2f} {y1 - y0 + 2 * p:.2f}"
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
               f'<path fill="{a.fill}" d="{d}"/></svg>\n')
        open(a.svg, "w").write(svg)
        print(f"wrote {a.svg} bbox={(x0, y0, x1, y1)} advance={adv}")
    else:
        print(d)
        print(f"bbox={(x0, y0, x1, y1)} advance={adv}", file=sys.stderr)


if __name__ == "__main__":
    main()
