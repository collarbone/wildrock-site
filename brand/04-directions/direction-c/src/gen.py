"""Wildrock direction C - Horizon Wordmark. Generates all SVG geometry.
Units: cap height H = 100, stroke S = 16. Horizon band in the O: y 60..70.
"""
import math, os, sys

OUT = sys.argv[1]
INK = "#1C1B19"
H = 100.0
S = 18.0
BAND_TOP, BAND_BOT = 60.0, 70.0   # the horizon cut (shared by O and mark)


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def poly(pts):
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z"


def rect(x, y, w, h):
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def stroke_w(dx, dy):
    """horizontal width of a diagonal stroke with perpendicular thickness S"""
    return S / math.cos(math.atan2(dx, dy))


# ---------------- letters: each returns (list_of_paths, width) ----------
# every path string is filled with fill-rule evenodd; separate paths union.

def W():
    d = 30.0
    th = stroke_w(d, H)
    m = 2 * d + th / 2
    p = [
        poly([(0, 0), (th, 0), (d + th, H), (d, H)]),
        poly([(d, H), (d + th, H), (m + th / 2, 0), (m - th / 2, 0)]),
        poly([(2 * m - d - th, H), (2 * m - d, H), (m + th / 2, 0), (m - th / 2, 0)]),
        poly([(2 * m - th, 0), (2 * m, 0), (2 * m - d, H), (2 * m - d - th, H)]),
    ]
    return p, 2 * m


def I():
    return [rect(0, 0, S, H)], S


def L():
    w = 64.0
    return [poly([(0, 0), (S, 0), (S, H - S), (w, H - S), (w, H), (0, H)])], w


def D():
    st = 40.0  # straight part before the round
    r, ri = H / 2, H / 2 - S
    p = (f"M0 0 H{f(st)} A{f(r)} {f(r)} 0 0 1 {f(st)} {f(H)} H0 Z "
         f"M{f(S)} {f(S)} H{f(st)} A{f(ri)} {f(ri)} 0 0 1 {f(st)} {f(H - S)} H{f(S)} Z")
    return [p], st + r


def R():
    bb = BAND_TOP          # bowl bottom sits on the horizon line
    r = bb / 2
    ri = r - S
    xb = 44.0
    bowl = (f"M0 0 H{f(xb)} A{f(r)} {f(r)} 0 0 1 {f(xb)} {f(bb)} H0 Z "
            f"M{f(S)} {f(S)} H{f(xb)} A{f(ri)} {f(ri)} 0 0 1 {f(xb)} {f(bb - S)} H{f(S)} Z")
    stem = rect(0, 0, S, H)
    w = 80.0
    a = 34.0               # leg top-left x at y = bb - S
    y0 = bb - S
    th = 18.0
    for _ in range(20):
        th = stroke_w(w - th - a, H - y0)
    leg = poly([(a, y0), (a + th, y0), (w, H), (w - th, H)])
    return [stem, bowl, leg], w


def O():
    r = H / 2
    c = r
    def hw(y):
        return math.sqrt(r * r - (y - c) ** 2)
    up = (f"M{f(c - hw(BAND_TOP))} {f(BAND_TOP)} A{f(r)} {f(r)} 0 1 1 "
          f"{f(c + hw(BAND_TOP))} {f(BAND_TOP)} Z")
    lo = (f"M{f(c - hw(BAND_BOT))} {f(BAND_BOT)} A{f(r)} {f(r)} 0 0 0 "
          f"{f(c + hw(BAND_BOT))} {f(BAND_BOT)} Z")
    return [up, lo], H


def C():
    r, ri = H / 2, H / 2 - S
    cut = 78.0
    do = math.sqrt(r * r - (cut - r) ** 2)
    di = math.sqrt(ri * ri - (cut - r) ** 2)
    p = (f"M{f(cut)} {f(r - do)} A{f(r)} {f(r)} 0 1 0 {f(cut)} {f(r + do)} "
         f"L{f(cut)} {f(r + di)} A{f(ri)} {f(ri)} 0 1 1 {f(cut)} {f(r - di)} Z")
    return [p], cut


def K():
    w = 78.0
    yj = BAND_TOP          # upper arm centre meets the stem on the horizon
    stem = rect(0, 0, S, H)
    # upper arm: centreline from (w - th/2, 0) to (S, yj)
    th = 20.0
    for _ in range(20):
        th = stroke_w(w - th / 2 - S, yj)
    top_c = w - th / 2
    slope = (top_c - S) / yj          # dx per dy (going down-left)
    # edges: left edge passes (w-th,0), right edge passes (w,0); both x = x0 - slope*y
    def y_at(x0, x):
        return (x0 - x) / slope
    # extend past stem edge into stem by 6 units so the union is clean
    xin = S - 6
    arm = poly([(w - th, 0), (w, 0), (xin, y_at(w, xin)), (xin, y_at(w - th, xin))])
    # leg: from bottom-right up to the arm centreline at x = xa
    xa = 38.0
    ya = (top_c - xa) / slope
    tl = 18.0
    for _ in range(20):
        tl = stroke_w(w - tl / 2 - xa, H - ya)
    bc = w - tl / 2
    ls = (bc - xa) / (H - ya)          # dx per dy going down-right
    # leg edges: left edge through (w - tl, H), right edge through (w, H); x = xb - ls*(H - y)
    # clip the leg's upper end on the arm centreline: x = top_c - slope*y
    def meet(xb):
        # xb - ls*(H-y) = top_c - slope*y  -> y*(ls+slope) = top_c - xb + ls*H
        y = (top_c - xb + ls * H) / (ls + slope)
        return (top_c - slope * y, y)
    leg = poly([meet(w - tl), meet(w), (w, H), (w - tl, H)])
    return [stem, arm, leg], w


LETTERS = {"W": W, "I": I, "L": L, "D": D, "R": R, "O": O, "C": C, "K": K}
# optical gaps between letter boxes (units of cap height 100)
GAPS = {"WI": 30, "IL": 40, "LD": 30, "DR": 38, "RO": 30, "OC": 32, "CK": 38}


def wordmark_paths(x0=0.0, y0=0.0, scale=1.0):
    word = "WILDROCK"
    out, x = [], 0.0
    for i, ch in enumerate(word):
        paths, w = LETTERS[ch]()
        for p in paths:
            out.append((x, p))
        x += w
        if i < len(word) - 1:
            x += GAPS[word[i] + word[i + 1]]
    total = x
    g = "".join(
        f'<path transform="translate({f(x0 + dx * scale)} {f(y0)}) scale({f(scale)})" d="{p}"/>'
        if scale != 1 else f'<path transform="translate({f(x0 + dx)} {f(y0)})" d="{p}"/>'
        for dx, p in out)
    return g, total


def mark_path(size=100.0, r_ratio=0.32, band_ratio=None, x0=0.0, y0=0.0):
    """Ink square with the disc knocked out; the horizon band stays ink.
    band positions are expressed relative to the disc radius, mirroring the O."""
    R_ = size * r_ratio
    cx, cy = x0 + size / 2, y0 + size / 2
    bt = cy + (BAND_TOP - 50) / 50 * R_
    bb = cy + (BAND_BOT - 50) / 50 * R_
    if band_ratio is not None:          # thicker band for tiny sizes
        mid = (bt + bb) / 2
        bt, bb = mid - band_ratio * size / 2, mid + band_ratio * size / 2
    hw = lambda y: math.sqrt(R_ * R_ - (y - cy) ** 2)
    sq = f"M{f(x0)} {f(y0)} H{f(x0 + size)} V{f(y0 + size)} H{f(x0)} Z"
    up = f"M{f(cx - hw(bt))} {f(bt)} A{f(R_)} {f(R_)} 0 1 1 {f(cx + hw(bt))} {f(bt)} Z"
    lo = f"M{f(cx - hw(bb))} {f(bb)} A{f(R_)} {f(R_)} 0 0 0 {f(cx + hw(bb))} {f(bb)} Z"
    return sq + " " + up + " " + lo


def svg(vb_w, vb_h, body, title, fill=INK, pad=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(-pad)} {f(-pad)} '
            f'{f(vb_w + 2 * pad)} {f(vb_h + 2 * pad)}" role="img" aria-label="{title}">\n'
            f'<title>{title}</title>\n<g fill="{fill}" fill-rule="evenodd">{body}</g>\n</svg>\n')


def write(name, text):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(text)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    wm, wm_w = wordmark_paths()
    write("wordmark.svg", svg(wm_w, H, wm, "Wildrock"))

    write("mark.svg", svg(100, 100, f'<path d="{mark_path()}"/>', "Wildrock mark"))
    write("mark-mono-white.svg", svg(100, 100, f'<path d="{mark_path()}"/>',
                                     "Wildrock mark, white", fill="#FFFFFF"))
    # favicon: bigger disc, thicker horizon so it survives 16px
    write("favicon.svg", svg(16, 16, f'<path d="{mark_path(16, 0.36, band_ratio=0.125)}"/>',
                             "Wildrock"))

    # horizontal lockup: tile sized so its disc == the O (r 50) -> horizons align
    T = 100 / 0.64          # 156.25
    gap = 56
    ty = 50 - T / 2
    wm2, _ = wordmark_paths(x0=T + gap)
    body = f'<path d="{mark_path(T, 0.32, x0=0, y0=ty)}"/>' + wm2
    write("lockup-horizontal.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {f(ty)} {f(T + gap + wm_w)} {f(T)}" '
          f'role="img" aria-label="Wildrock"><title>Wildrock</title>'
          f'<g fill="{INK}" fill-rule="evenodd">{body}</g></svg>\n')

    # stacked lockup: tile centred over wordmark
    T2 = 240
    gap2 = 72
    wm3, _ = wordmark_paths(y0=T2 + gap2)
    body = f'<path d="{mark_path(T2, 0.32, x0=(wm_w - T2) / 2, y0=0)}"/>' + wm3
    write("lockup-stacked.svg", svg(wm_w, T2 + gap2 + H, body, "Wildrock"))
    print("wordmark width", wm_w)
