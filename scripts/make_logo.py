#!/usr/bin/env python3
"""Draw the vterinka.cz logo and favicons from the Bodoni Moda outlines (run once locally, the outputs are committed).

    python3 scripts/make_logo.py /path/to/BodoniModa[opsz,wght].ttf

Logo = the word "vteřinka" as vector outlines (no <text>, renders the same everywhere) over a minute track: a hairline with
60 ticks, every 5th one longer in brass. One bordeaux accent: the tip of a second hand that crosses the track at the end.
Favicon = a lower-case "v" in ivory on a dial-blue rounded square, ringed by 12 hour ticks (a watch face).
PNG favicons are rendered by headless Chromium (no Cairo on the Pi). Font: Bodoni Moda, SIL Open Font License (static/fonts/OFL-bodoni.txt).
"""
import base64
import io
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

APP = Path(__file__).resolve().parent.parent
ST = APP / "static"
NAVY, INK, BRASS, BORDO, IVORY = "#1F3A5F", "#16181D", "#A87F2A", "#962B2B", "#F4EFE4"


def instance(path):
    f = TTFont(path, lazy=False)
    f = instancer.instantiateVariableFont(f, {"opsz": 48, "wght": 620})
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    return TTFont(buf, lazy=False)


def word_paths(font, text, scale, x0, baseline):
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    x = x0
    parts = []
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[gname].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        parts.append(pen.getCommands())
        x += hmtx[gname][0] * scale
    return " ".join(parts), x


def logo_svg(font, color, tick, accent):
    upm = font["head"].unitsPerEm
    scale = 46 / upm
    baseline = 36
    d, right = word_paths(font, "vteřinka", scale, 2, baseline)
    w = right + 14
    y = baseline + 8
    ticks = []
    n = 60
    span = right - 4
    for i in range(n + 1):
        x = 3 + span * i / n
        big = i % 5 == 0
        ticks.append(f"M{x:.1f} {y}v{5.5 if big else 3}")
    big_ticks = " ".join(t for i, t in enumerate(ticks) if i % 5 == 0)
    small_ticks = " ".join(t for i, t in enumerate(ticks) if i % 5)
    hand = (f'<path d="M{right - 8:.1f} {y + 7:.1f}L{right + 9:.1f} {y - 14:.1f}" stroke="{accent}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<circle cx="{right - 8:.1f}" cy="{y + 7:.1f}" r="2.6" fill="{accent}"/>')
    track = (f'<path d="{small_ticks}" stroke="{color}" stroke-width=".9" fill="none"/>'
             f'<path d="{big_ticks}" stroke="{tick}" stroke-width="1.5" fill="none"/>')
    h = y + 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="vteřinka">'
            f'<path d="{d}" fill="{color}"/>{track}{hand}</svg>'), (round(w), round(h))


def favicon_svg(font, ticks=True):
    upm = font["head"].unitsPerEm
    gs = font.getGlyphSet()
    g = font.getBestCmap()[ord("v")]
    bp = BoundsPen(gs)
    gs[g].draw(bp)
    xmin, ymin, xmax, ymax = bp.bounds
    scale = (30 if ticks else 40) / (ymax - ymin)
    gw, gh = (xmax - xmin) * scale, (ymax - ymin) * scale
    x = (64 - gw) / 2 - xmin * scale
    baseline = (64 - gh) / 2 + ymax * scale
    pen = SVGPathPen(gs)
    gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
    t = ""
    if ticks:
        segs = []
        for i in range(12):
            a = math.radians(i * 30)
            r0, r1 = (22.5 if i % 3 == 0 else 24.5), 27.5
            segs.append(f"M{32 + r0 * math.sin(a):.2f} {32 - r0 * math.cos(a):.2f}L{32 + r1 * math.sin(a):.2f} {32 - r1 * math.cos(a):.2f}")
        t = f'<path d="{" ".join(segs)}" stroke="{IVORY}" stroke-width="2.2" stroke-linecap="round"/><circle cx="32" cy="4.6" r="2.4" fill="#D9A54A"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{NAVY}"/>'
            f'<path d="{pen.getCommands()}" fill="{IVORY}"/>{t}</svg>')


def png(svg, size, out):
    """Render an SVG at `size` px with headless Chromium (screenshot of a page that holds only the image)."""
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "p.html"
        page.write_text(f'<html><body style="margin:0;background:transparent"><img src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}" width="{size}" height="{size}"></body></html>')
        shot = Path(td) / "s.png"
        subprocess.run(["chromium", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                        f"--window-size={size},{size}", f"--screenshot={shot}", f"file://{page}"], check=True, capture_output=True)
        Image.open(shot).convert("RGBA").crop((0, 0, size, size)).save(out, optimize=True)


def main():
    font = instance(sys.argv[1])
    dark, (w, h) = logo_svg(font, INK, BRASS, BORDO)
    light, _ = logo_svg(font, IVORY, "#D9B76A", "#E07A6E")
    (ST / "img/ui").mkdir(parents=True, exist_ok=True)
    (ST / "img/ui/logo.svg").write_text(dark)
    (ST / "img/ui/logo-light.svg").write_text(light)
    big = favicon_svg(font, ticks=True)
    small = favicon_svg(font, ticks=False)
    (ST / "favicon.svg").write_text(big)
    for size, svg in ((32, small), (180, big), (192, big), (512, big)):
        png(svg, size, ST / f"favicon-{size}.png")
    png(small, 48, ST / "f48.png")
    Image.open(ST / "f48.png").save(ST / "favicon.ico", sizes=[(48, 48), (32, 32), (16, 16)])
    os.remove(ST / "f48.png")
    print(f"logo {w}x{h}")


if __name__ == "__main__":
    main()
