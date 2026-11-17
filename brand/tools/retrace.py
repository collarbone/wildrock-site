#!/usr/bin/env python3
"""retrace.py — high-fidelity re-trace of a logo from a raster source, fitted to an existing SVG frame.

  retrace.py SRC.jpg REF.svg OUT.svg [--up 4] [--alphamax 0.85] [--opttol 0.15] [--turd 60]
             [--diffdir DIR]

* Ink mask from colour projection (paper -> ink), so paper texture is ignored and edges stay anti-aliased.
* Supersampled (--up) before thresholding for sub-pixel edge accuracy.
* Traced with potrace; output path is mapped so its bbox equals REF.svg's path bbox (keeps viewBox/placements).
* Reports IoU / XOR vs the source mask for both REF and OUT, and writes red/blue diff overlays.
"""
import argparse
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ---------- SVG path (absolute M/L/H/V/C/Z) parse, flatten, rasterise ----------
def parse_path(d):
    toks = re.findall(r"[MLHVCZmlhvcz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    subs, cur, i, cmd, pos, start = [], [], 0, None, (0, 0), (0, 0)
    num = lambda: float(toks[i])
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in "Zz":
                if cur: subs.append(cur)
                cur, pos = [], start
                continue
        if cmd == "M":
            if cur: subs.append(cur)
            pos = (float(toks[i]), float(toks[i + 1])); i += 2; start = pos; cur = [pos]; cmd = "L"
        elif cmd == "L":
            pos = (float(toks[i]), float(toks[i + 1])); i += 2; cur.append(pos)
        elif cmd == "H":
            pos = (float(toks[i]), pos[1]); i += 1; cur.append(pos)
        elif cmd == "V":
            pos = (pos[0], float(toks[i])); i += 1; cur.append(pos)
        elif cmd == "C":
            p0 = pos
            c1 = (float(toks[i]), float(toks[i + 1])); c2 = (float(toks[i + 2]), float(toks[i + 3])); p3 = (float(toks[i + 4]), float(toks[i + 5])); i += 6
            for k in range(1, 17):
                t_ = k / 16; u = 1 - t_
                cur.append((u**3 * p0[0] + 3 * u * u * t_ * c1[0] + 3 * u * t_ * t_ * c2[0] + t_**3 * p3[0],
                            u**3 * p0[1] + 3 * u * u * t_ * c1[1] + 3 * u * t_ * t_ * c2[1] + t_**3 * p3[1]))
            pos = p3
        else:
            raise ValueError(f"unsupported path command {cmd}")
    if cur: subs.append(cur)
    return subs


def bbox(subs):
    xs = [p[0] for s in subs for p in s]; ys = [p[1] for s in subs for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def rasterise(subs, W, H, tf):
    """even-odd fill via XOR of per-subpath polygons; tf maps path coords -> pixel coords."""
    acc = np.zeros((H, W), bool)
    for s in subs:
        im = Image.new("1", (W, H), 0)
        ImageDraw.Draw(im).polygon([tf(p) for p in s], fill=1)
        acc ^= np.asarray(im, bool)
    return acc


# ---------- source mask ----------
def ink_alpha(src):
    a = np.asarray(Image.open(src).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hard = (b - r) > 80
    ink = a[hard].mean(0); paper = a[~hard].mean(0)
    v = ink - paper
    t = np.einsum("ijk,k->ij", a - paper, v) / float(np.dot(v, v))
    return np.clip(t, 0, 1), hard


def trace(mask, alphamax, opttol, turd):
    import potrace
    plist = potrace.Bitmap(~mask).trace(turdsize=turd, alphamax=alphamax, opticurve=True, opttolerance=opttol)
    return plist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("ref"); ap.add_argument("out")
    ap.add_argument("--up", type=int, default=4)
    ap.add_argument("--alphamax", type=float, default=0.85)
    ap.add_argument("--opttol", type=float, default=0.15)
    ap.add_argument("--turd", type=int, default=60)
    ap.add_argument("--blur", type=float, default=0, help="gaussian blur radius (supersampled px) before threshold")
    ap.add_argument("--diffdir")
    a = ap.parse_args()

    alpha, hard = ink_alpha(a.src)
    ys, xs = np.where(hard)
    m = 12
    x0, y0, x1, y1 = xs.min() - m, ys.min() - m, xs.max() + m + 1, ys.max() + m + 1
    crop = Image.fromarray((alpha[y0:y1, x0:x1] * 255).astype(np.uint8))
    U = a.up
    big = crop.resize((crop.width * U, crop.height * U), Image.LANCZOS).filter(ImageFilter.MedianFilter(3))
    if a.blur:
        big = big.filter(ImageFilter.GaussianBlur(a.blur))
    mask = np.asarray(big) > 127
    MH, MW = mask.shape

    # trace
    plist = trace(mask, a.alphamax, a.opttol, a.turd)
    # mask-space bbox of traced ink
    mys, mxs = np.where(mask)
    mb = (mxs.min(), mys.min(), mxs.max() + 1, mys.max() + 1)

    # reference frame
    refsvg = open(a.ref).read()
    vb = re.search(r'viewBox="([^"]+)"', refsvg).group(1)
    refd = re.search(r' d="([^"]+)"', refsvg).group(1)
    refsubs = parse_path(refd)
    rb = bbox(refsubs)
    sx = (rb[2] - rb[0]) / (mb[2] - mb[0]); sy = (rb[3] - rb[1]) / (mb[3] - mb[1])
    to_ref = lambda x, y: (rb[0] + (x - mb[0]) * sx, rb[1] + (y - mb[1]) * sy)
    fmt = lambda x, y: "%s %s" % tuple(f"{v:.2f}".rstrip("0").rstrip(".") for v in to_ref(x, y))

    parts = []
    for c in plist:
        parts.append("M" + fmt(c.start_point.x, c.start_point.y))
        for s in c.segments:
            if s.is_corner:
                parts.append("L" + fmt(s.c.x, s.c.y) + "L" + fmt(s.end_point.x, s.end_point.y))
            else:
                parts.append("C" + fmt(s.c1.x, s.c1.y) + " " + fmt(s.c2.x, s.c2.y) + " " + fmt(s.end_point.x, s.end_point.y))
        parts.append("Z")
    newd = "".join(parts)
    w, h = vb.split()[2:]
    open(a.out, "w").write(f'<svg width="{w}" height="{h}" viewBox="{vb}" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
                           f'<path fill-rule="evenodd" d="{newd}" fill="black"/>\n</svg>\n')

    # fidelity: rasterise both into mask space
    from_ref = lambda p: (mb[0] + (p[0] - rb[0]) / sx, mb[1] + (p[1] - rb[1]) / sy)
    old = rasterise(refsubs, MW, MH, from_ref)
    new = rasterise(parse_path(newd), MW, MH, from_ref)

    def score(r):
        inter = (r & mask).sum(); union = (r | mask).sum()
        return inter / union, int((r ^ mask).sum())
    io, xo = score(old); inn, xn = score(new)
    print(f"old  IoU {io:.4f}  xor {xo}px (at {U}x)")
    print(f"new  IoU {inn:.4f}  xor {xn}px (at {U}x)")
    print(f"wrote {a.out}  ({len(newd)} chars, {len(plist)} subpaths)")

    if a.diffdir:
        os.makedirs(a.diffdir, exist_ok=True)
        for name, r in (("old", old), ("new", new)):
            img = np.full((MH, MW, 3), 255, np.uint8)
            img[mask & r] = (40, 40, 40)
            img[mask & ~r] = (230, 30, 30)   # missing ink (red)
            img[~mask & r] = (30, 90, 230)   # extra ink (blue)
            Image.fromarray(img).resize((MW // 2, MH // 2), Image.LANCZOS).save(os.path.join(a.diffdir, f"{name}-full.png"))
            # zoom crops: w, d, r, k regions (fractions of width)
            for tag, f0, f1 in (("w", 0.0, 0.2), ("d", 0.33, 0.52), ("r", 0.47, 0.6), ("k", 0.85, 1.0)):
                Image.fromarray(img[:, int(MW * f0):int(MW * f1)]).save(os.path.join(a.diffdir, f"{name}-{tag}.png"))


if __name__ == "__main__":
    main()
