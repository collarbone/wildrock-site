---
name: svg-lettering
description: Draw custom letterforms, wordmarks, signatures and marks as clean single-colour SVG without being limited to available fonts — build shapes from brush strokes (tapered or calligraphic nib), polygons, arcs and negative-space cuts, optionally starting from any font, then trace to Bézier outlines. Use for Wildrock logo/wordmark exploration, hand-lettering, signature logos, custom ligatures, or tracing a sketch/raster into vector.
---

# SVG lettering & shape tracing

Tools live in `brand/tools/` (run with `brand/tools/.venv/bin/python`; if the venv is missing:
`python3 -m venv brand/tools/.venv && brand/tools/.venv/bin/pip install -r brand/tools/requirements.txt`).

| Tool | Use it for |
|---|---|
| `shapes.py render SPEC.json OUT.svg --png PREVIEW.png` | Custom drawing → traced SVG. Strokes, nib calligraphy, tapers, polys, rects, ellipses, arcs, font text, `erase` cuts. Full spec in the file's docstring. |
| `shapes.py trace IMAGE.png OUT.svg` | Trace any raster (a sketch photo, a rendered study) to vector. |
| `outline.py FONT "TEXT" --svg OUT.svg` | Exact font outlines (variable axes, tracking, kerning) when a font is the right base. |
| `contact_sheet.py DIR OUT.png` | Review many renders in one image. |
| `fonts/` | 21 OFL Google Fonts (safe for commercial logos). Any other font file on disk also works in `shapes.py` text elements. |

## Workflow (keep it cheap)
1. Write a small JSON spec on a ~1000-unit grid. Build letters from strokes/polys; use `erase` for counters, cuts and notches. Fonts are optional scaffolding.
2. `render ... --png preview.png`, then **Read the PNG** and fix proportions, spacing and weight. Iterate by editing the JSON, not by hand-editing the path.
3. When several variants exist, put the PNGs in one folder and make a `contact_sheet.py` image; review that single image instead of many.
4. Check the final SVG: `xmllint --noout`. Test legibility at 16 px and on a dark background (`--fill #fff`).
5. For HTML review pages, **inline** the SVG; the browser on this Mac cannot load linked local files.

## Design guardrails (Wildrock brief)
- Traits: Human / Wild / Precise. Tone: timeless, quiet, exclusive, steady.
- Bold enough for a yard sign and a favicon. No hairlines; minimum stroke ≈ 6% of cap height.
- Avoid house icons, rustic/Western clichés, intricate detail, and cold corporate looks.
- Use references from `brand/03-inspiration/` for **inspiration only**. Don't trace another company's logo or a commercial font's glyphs into a Wildrock mark. Draw original shapes that borrow the idea (spacing, contrast, gesture), not the artwork.

## Spec cheat-sheet
```json
{"width":1000,"height":300,"pad":20,"elements":[
 {"type":"stroke","points":[[20,90],[60,240],[110,120]],"width":26,"nib":{"angle":35,"ratio":0.22},"taper":[0.6,1]},
 {"type":"poly","points":[[0,0],[40,0],[20,60]]},
 {"type":"rect","x":350,"y":150,"w":520,"h":10,"r":0,"erase":true},
 {"type":"arc","cx":500,"cy":150,"r":60,"start":180,"end":360,"width":18},
 {"type":"text","font":"brand/tools/fonts/archivo/Archivo[wdth,wght].ttf","text":"ROCK","x":360,"y":240,"size":190,"axes":{"wght":800},"tracking":30}
]}
```
Elements paint in order; `erase` cuts only what is beneath it.
