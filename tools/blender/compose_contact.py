"""Contact sheets: every rendered sprite in a group on one image.

    blender --background --factory-startup --python compose_contact.py

Its only job is to make style drift visible. Because every figure comes off the
same rig, outline weight, tone bands, sun angle and pixel scale are identical by
construction rather than by inspection -- so anything that DOES look out of place
on a sheet is a modelling decision, which is the thing worth a human's attention.

**Canonical sheets are composed FROM `assets/rendered/sprites/`, and written back
to `assets/rendered/sheets/`.** They used to be composed from the gitignored
scratch directory, and that is the exact mechanism of the 2026-08-02 drift: `out/`
does not travel between machines, so a builder edited on one machine left the
other holding an older render under the right filename, and a sheet composed
there showed four banneret sprites the repository did not have. A sheet is a
claim about the repository, so it is built from the repository; a stale scratch
directory now cannot poison one, because nothing canonical reads scratch.

Each canonical sheet records the pixel hash of every sprite it consumed into
`assets/rendered/manifest.json` (see `manifest.py`), and is only rewritten when
its own pixels actually change, so a no-op recompose leaves `git status` clean.

`--line <hero>` is the one scratch mode: an ad-hoc four-tier sheet for judging a
rework BEFORE it is published, composed from `out/` and written to `out/`. It is
review scratch by definition and never travels.

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
import hash_pngs as HP
importlib.reload(P)
importlib.reload(F)
importlib.reload(roster)
importlib.reload(M)
importlib.reload(HP)
OUT = P.out_dir()
SPRITES = os.path.join(M.RENDERED, "sprites")
SHEETS = os.path.join(M.RENDERED, "sheets")

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

    Returns (canvas, inputs) where inputs maps each consumed path to the pixel
    hash of what was actually loaded -- the provenance a canonical sheet records.
    Missing files are skipped, not blanked, so a half-finished family still
    produces a judgeable sheet.

    Labels are stamped into the 1x canvas rather than onto an upscale, so label
    pixels come out the same size as sprite pixels. Without a name under every
    figure the sheet shows that two sprites differ but gives no way to SAY which
    one needs the edit, and near-identical rarity variants are exactly where that
    bites (user, 2026-08-01)."""
    tiles, inputs = [], {}
    for label, path in entries:
        if not os.path.exists(path):
            continue
        t = load_rgba(path)
        inputs[path] = HP.hash_pixels(t, t.shape[1], t.shape[0])
        tiles.append((label, t))
    if not tiles:
        return None, {}

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

    return canvas, inputs


def publish_sheet(man, canvas, inputs, dest, upscale=4):
    """Write a canonical sheet only if its pixels changed; record provenance.

    Written through a scratch temp file so the hash compared is the hash of what
    is actually on disk after Blender's own PNG quantization -- one definition of
    "same" everywhere (see `hash_pngs`). An unchanged sheet is not rewritten, so
    a no-op recompose does not churn `git status` with byte-different files.
    """
    tmp = os.path.join(OUT, "_tmp_" + os.path.basename(dest))
    save_rgba(canvas, tmp)
    px = HP.hash_image(tmp)
    key = M.rel(dest)
    entry = man.get(key)
    rec = {"px": px, "wh": [canvas.shape[1], canvas.shape[0]],
           "inputs": {M.rel(p): h for p, h in inputs.items()}}
    changed = (entry or {}).get("px") != px
    if changed:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest):
            os.remove(dest)
        os.replace(tmp, dest)
    else:
        os.remove(tmp)
    man[key] = rec
    # a zoomable copy stays in scratch for local review; it is derivative, so it
    # is never published
    big = os.path.join(OUT, "sheet_%s_big.png" % os.path.basename(dest)[:-4])
    if changed or not os.path.exists(big):
        P.upscale_nearest(dest, big, upscale, bg=BG)
    return changed


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
    canvas, _ = compose(entries, cols=len(roster.TIER_ORDER))
    if canvas is None:
        raise SystemExit("no scratch renders for %s -- render the line first" % argv[1])
    path = os.path.join(OUT, "sheet_line_%s.png" % argv[1])
    save_rgba(canvas, path)
    P.upscale_nearest(path, path.replace(".png", "_big.png"), 4, bg=BG)
    print("scratch line sheet written to %s" % path)
    raise SystemExit(0)

man = M.load()
made, unchanged = [], []
for g in roster.GROUPS + ["all_characters"]:
    entries, cols = canonical_entries(g)
    canvas, inputs = compose(entries, cols=cols)
    if canvas is None:
        continue
    dest = os.path.join(SHEETS, g + ".png")
    upscale = 3 if g == "all_characters" else 4
    if publish_sheet(man, canvas, inputs, dest, upscale=upscale):
        made.append("%s (%d sprites)" % (g, len(inputs)))
    else:
        unchanged.append(g)
M.save(man)

print("canonical sheets -> %s" % SHEETS)
for line in made:
    print("  rewrote " + line)
print("  unchanged: %s" % (", ".join(unchanged) or "none"))
