"""Contact sheets: every rendered sprite in a group on one image.

    blender --background --factory-startup --python compose_contact.py

Its only job is to make style drift visible. Because every figure comes off the
same rig, outline weight, tone bands, sun angle and pixel scale are identical by
construction rather than by inspection -- so anything that DOES look out of place
on a sheet is a modelling decision, which is the thing worth a human's attention.

**Canonical sheets are composed FROM `assets/rendered/sprites/` and written as
CANDIDATES into `out/`, where `publish.py` hashes them and copies the ones that
actually changed.** Two decisions live in that sentence. Reading published art is
the drift fix: sheets used to be composed from the gitignored scratch renders,
which do not travel between machines, and on 2026-08-02 sheets committed that way
showed four banneret sprites the repository did not have -- a sheet is a claim
about the repository, so it is built from the repository. Writing candidates
rather than finals keeps ALL bookkeeping in `publish.py`: Blender turns pixels
into pixels, and one system-Python tool owns every hash (see `pixhash.py`).

`--line <hero>` is the one scratch-INPUT mode: an ad-hoc four-tier sheet for
judging a rework BEFORE it is published, composed from `out/` renders. Review
scratch by definition; it never travels.

Sprites are bottom-aligned, which is what puts them all on one ground line. The
sprite cells already share a ground row by construction (see the scale-matching
section of README.md), so a taller cell simply has more headroom above the same
feet.
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
import pixelfont as F
import roster
import manifest as M
importlib.reload(P)
importlib.reload(F)
importlib.reload(roster)
importlib.reload(M)
OUT = P.out_dir()
SPRITES = os.path.join(M.RENDERED, "sprites")

PAD = 4                 # blank pixels between cells, so outlines never touch
BG = "#2a2320"          # the dark board the sheets are judged against
COLS = 6                # a family is six, so a family is one row
INK = "#cfc4b0"         # label colour: legible on BG without competing with art
LABEL_GAP = 3           # blank rows between a figure's feet and its name


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


def compose(entries, cols=COLS):
    """Tile (label, path) entries into a captioned grid.

    Missing files are skipped, not blanked, so a half-finished family still
    produces a judgeable sheet.

    Labels are stamped into the 1x canvas rather than onto an upscale, so label
    pixels come out the same size as sprite pixels. Without a name under every
    figure the sheet shows that two sprites differ but gives no way to SAY which
    one needs the edit, and near-identical rarity variants are exactly where that
    bites (user, 2026-08-01)."""
    tiles = []
    for label, path in entries:
        if os.path.exists(path):
            tiles.append((label, load_rgba(path)))
    if not tiles:
        return None

    cell = max(max(t.shape[0], t.shape[1]) for _, t in tiles)
    cols = min(cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols

    # One label band height for every row, so the grid stays regular and the
    # ground lines stay shared even when one key wraps and its neighbours do not.
    labels = [F.text_lines(k, cell) for k, _ in tiles]
    band = LABEL_GAP + F.block_height(max(len(l) for l in labels))

    step = cell + band + PAD
    W = cols * (cell + PAD) + PAD
    H = rows * step + PAD
    canvas = np.zeros((H, W, 4), dtype=np.float32)
    ink = P.hexcol(INK)

    for i, (_, t) in enumerate(tiles):
        r, c = i // cols, i % cols
        h, w = t.shape[:2]
        # numpy row 0 is the BOTTOM row in Blender's pixel buffer, so counting
        # rows from the bottom of the canvas is what lands every figure on one
        # ground line.
        y = (rows - 1 - r) * step + PAD
        x = c * (cell + PAD) + PAD
        F.draw_block(canvas, labels[i], x + cell / 2, y, ink)
        canvas[y + band:y + band + h, x + (cell - w) // 2:x + (cell - w) // 2 + w] = t

    return canvas


def canonical_entries(g):
    if g == "variants":
        assets, cols = roster.variant_rows(), len(roster.TIER_ORDER)
    elif g == "all_characters":
        assets, cols = [a for a in roster.ROSTER if a.group != "buildings"], 8
    else:
        assets, cols = roster.by_group(g), COLS
    entries = []
    for item in assets:
        a, label = item if isinstance(item, tuple) else (item, item.key)
        entries.append((label, os.path.join(SPRITES, a.key + ".png")))
    return entries, cols


# `blender ... --python compose_contact.py -- --line hero_fighter` builds ONE
# hero's four-tier sheet from the SCRATCH renders and stops: the pre-publish
# review tool. The developer reviews a rework a line at a time (user, 2026-08-01).
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) == 2 and argv[0] == "--line":
    entries = []
    for item in roster.variant_rows(argv[1]):
        a, label = item if isinstance(item, tuple) else (item, item.key)
        entries.append((label, os.path.join(OUT, a.out)))
    canvas = compose(entries, cols=len(roster.TIER_ORDER))
    if canvas is None:
        raise SystemExit("no scratch renders for %s -- render the line first" % argv[1])
    path = os.path.join(OUT, "sheet_line_%s.png" % argv[1])
    save_rgba(canvas, path)
    P.upscale_nearest(path, path.replace(".png", "_big.png"), 4, bg=BG)
    print("scratch line sheet written to %s" % path)
    raise SystemExit(0)

made = []
for g in roster.GROUPS + ["all_characters"]:
    entries, cols = canonical_entries(g)
    canvas = compose(entries, cols=cols)
    if canvas is None:
        continue
    cand = os.path.join(OUT, "sheet_%s.png" % g)
    save_rgba(canvas, cand)
    # a zoomable copy for local review; derivative, never published
    P.upscale_nearest(cand, os.path.join(OUT, "sheet_%s_big.png" % g),
                      3 if g == "all_characters" else 4, bg=BG)
    made.append(g)

print("sheet candidates -> %s: %s" % (OUT, ", ".join(made)))
print("next: python tools/blender/publish.py")
