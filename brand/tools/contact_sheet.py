#!/usr/bin/env python3
"""Build a numbered contact-sheet PNG from a folder of images (for fast visual curation).

Usage: contact_sheet.py IN_DIR OUT.png [--cols 10] [--thumb 180] [--only 1,5,9]
Image filenames must start with their number (e.g. 007.jpg). Requires Pillow.
"""
import argparse
import os
import re

from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("indir")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=10)
    ap.add_argument("--thumb", type=int, default=180)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = {int(x) for x in a.only.split(",") if x}
    files = []
    for f in sorted(os.listdir(a.indir)):
        m = re.match(r"(\d+)", f)
        if not m:
            continue
        n = int(m.group(1))
        if only and n not in only:
            continue
        files.append((n, os.path.join(a.indir, f)))
    t, pad, lab = a.thumb, 6, 18
    rows = (len(files) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (a.cols * (t + pad) + pad, rows * (t + pad + lab) + pad), "white")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
    for i, (n, p) in enumerate(files):
        r, c = divmod(i, a.cols)
        x, y = pad + c * (t + pad), pad + r * (t + pad + lab)
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((t, t))
            sheet.paste(im, (x + (t - im.width) // 2, y + lab + (t - im.height) // 2))
        except Exception:
            d.rectangle([x, y + lab, x + t, y + lab + t], outline="red")
        d.text((x, y), str(n), fill="black", font=font)
    sheet.save(a.out)
    print(f"wrote {a.out}: {len(files)} images, {sheet.size}")


if __name__ == "__main__":
    main()
