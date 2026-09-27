#!/usr/bin/env python3
"""Write a repo's light and dark SVG logos: an icon tile beside a wordmark.

The wordmark is the text set in a font file and converted to SVG paths, so the
logo renders the same everywhere without the font installed. The icon is drawn
by hand as SVG elements in the tile's 96x96 coordinate space.

Needs fontTools. Run it with uv, which fetches it on the fly:

    uv run --with fonttools python make_logo.py --text corral \\
        --font ~/Library/Fonts/IBMPlexMono-SemiBold.otf \\
        --icon icon.svg --out docs/

Writes logo-light.svg and logo-dark.svg into --out. The icon file holds the
elements to place inside the tile (a full <svg> wrapper is also accepted; only
its contents are used). Keep the drawing inside roughly x 9..87, y 9..87 so it
clears the tile's rounded corners, and use colors that read on the dark tile in
both variants: the tile is dark in both, only its border and the wordmark
change.
"""

import argparse
import math
import re
import sys
from pathlib import Path

try:
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
except ImportError:
    sys.exit("make_logo.py needs fontTools: run it with `uv run --with fonttools python make_logo.py ...`")

TILE = 96
GAP = 22  # between the tile's right edge and the wordmark's origin
MARGIN = 8  # right of the wordmark's ink


def number(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def wordmark(font_path, text, size, x0, baseline):
    font = TTFont(font_path)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs, ntos=number)
    bounds = BoundsPen(glyphs)
    advance = 0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            sys.exit("make_logo.py: the font has no glyph for %r" % ch)
        glyph = glyphs[name]
        transform = (scale, 0, 0, -scale, x0 + advance * scale, baseline)
        glyph.draw(TransformPen(pen, transform))
        glyph.draw(TransformPen(bounds, transform))
        advance += glyph.width
    return pen.getCommands(), bounds.bounds


def icon_elements(path):
    body = Path(path).read_text()
    match = re.search(r"<svg\b[^>]*>(.*)</svg>", body, re.S)
    if match:
        body = match.group(1)
    lines = [line.rstrip() for line in body.strip("\n").splitlines()]
    indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join("  " + l[indent:] if l.strip() else "" for l in lines)


def svg(text, width, tile_fill, border, icon, text_fill, path):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{TILE}" viewBox="0 0 {width} {TILE}" role="img" aria-label="{text}">
  <title>{text}</title>
  <rect x="1" y="1" width="94" height="94" rx="22" fill="{tile_fill}" stroke="{border}" stroke-width="2"/>
{icon}
  <path fill="{text_fill}" d="{path}"/>
</svg>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--text", required=True, help="the wordmark, usually the repo name")
    p.add_argument("--font", required=True, help="path to an .otf or .ttf font file")
    p.add_argument("--icon", required=True, help="file of SVG elements drawn in the 96x96 tile")
    p.add_argument("--out", required=True, help="directory for logo-light.svg and logo-dark.svg")
    p.add_argument("--size", type=float, default=64, help="font size in px (default 64)")
    p.add_argument("--baseline", type=float, default=65, help="wordmark baseline y (default 65)")
    p.add_argument("--tile-fill", default="#161b22")
    p.add_argument("--light-border", default="#d0d7de")
    p.add_argument("--dark-border", default="#30363d")
    p.add_argument("--light-text", default="#1f2328")
    p.add_argument("--dark-text", default="#e6edf3")
    a = p.parse_args()

    x0 = TILE + GAP
    path, bounds = wordmark(Path(a.font).expanduser(), a.text, a.size, x0, a.baseline)
    width = math.ceil(bounds[2] + MARGIN)
    icon = icon_elements(Path(a.icon).expanduser())
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "logo-light.svg").write_text(
        svg(a.text, width, a.tile_fill, a.light_border, icon, a.light_text, path))
    (out / "logo-dark.svg").write_text(
        svg(a.text, width, a.tile_fill, a.dark_border, icon, a.dark_text, path))
    print("wrote %s and %s (%dx%d)" % (out / "logo-light.svg", out / "logo-dark.svg", width, TILE))


if __name__ == "__main__":
    main()
