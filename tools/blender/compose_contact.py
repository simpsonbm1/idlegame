"""Contact sheets: every rendered sprite in a group on one image.

    blender --background --factory-startup --python compose_contact.py

Its only job is to make style drift visible. Because every figure comes off the
same rig, outline weight, tone bands, sun angle and pixel scale are identical by
construction rather than by inspection -- so anything that DOES look out of place
on a sheet is a modelling decision, which is the thing worth a human's attention.

Sprites are bottom-aligned, which is what puts them all on one ground line. The
sprite cells already share a ground row by construction (see the scale-matching
section of README.md), so a taller cell simply has more headroom above the same
feet.

Supersedes `compose_lineup.py`, which carried a hardcoded three-sprite list.
"""

import bpy
import os
import sys
import importlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import roster
importlib.reload(P)
importlib.reload(roster)
OUT = P.out_dir()

PAD = 4                 # blank pixels between cells, so outlines never touch
BG = "#2a2320"          # the dark board the sheets are judged against
COLS = 6                # a family is six, so a family is one row


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return buf.reshape(h, w, 4)


def save_rgba(arr, path):
    out = bpy.data.images.new("sheet", arr.shape[1], arr.shape[0], alpha=True)
    out.pixels.foreach_set(arr.ravel())
    out.file_format = 'PNG'
    out.filepath_raw = path
    out.save()
    bpy.data.images.remove(out)
    return path


def sheet(assets, path, cols=COLS, upscale=4):
    """Tile `assets` into a grid. Missing renders are skipped, not blanked, so a
    half-finished family still produces a judgeable sheet."""
    tiles = []
    for a in assets:
        p = os.path.join(OUT, a.out)
        if os.path.exists(p):
            tiles.append((a, load_rgba(p)))
    if not tiles:
        return None

    cell = max(max(t.shape[0], t.shape[1]) for _, t in tiles)
    cols = min(cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (cell + PAD) + PAD
    H = rows * (cell + PAD) + PAD
    canvas = np.zeros((H, W, 4), dtype=np.float32)

    for i, (a, t) in enumerate(tiles):
        r, c = i // cols, i % cols
        h, w = t.shape[:2]
        # numpy row 0 is the BOTTOM row in Blender's pixel buffer, so counting
        # rows from the bottom of the canvas is what lands every figure on one
        # ground line.
        y = (rows - 1 - r) * (cell + PAD) + PAD
        x = c * (cell + PAD) + PAD + (cell - w) // 2
        canvas[y:y + h, x:x + w] = t

    save_rgba(canvas, path)
    P.upscale_nearest(path, path.replace(".png", "_big.png"), upscale, bg=BG)
    return [a.key for a, _ in tiles]


made = []
for g in roster.GROUPS:
    assets = roster.by_group(g)
    keys = sheet(assets, os.path.join(OUT, "sheet_%s.png" % g))
    if keys:
        made.append("%s (%d): %s" % (g, len(keys), ", ".join(keys)))

# one sheet with everything on it, which is where cross-family drift shows up
everything = [a for a in roster.ROSTER if a.group != "buildings"]
sheet(everything, os.path.join(OUT, "sheet_all_characters.png"), cols=8, upscale=3)

print("contact sheets written to", OUT)
for line in made:
    print("  " + line)
