"""Contact sheets for the ATTACK sheets: one row per combatant, captioned.

    blender -b --factory-startup --python compose_attack_contact.py            # canonical
    blender -b --factory-startup --python compose_attack_contact.py -- hero_   # ad-hoc, scratch

**The canonical groups are composed FROM `assets/rendered/attack/` and written
as CANDIDATES into `out/`**, where `publish.py` hashes them, copies the changed
ones, and records provenance -- same reasoning as `compose_contact.py`: a sheet
is a claim about the repository, so it is built from the repository, and all
bookkeeping lives in one system-Python tool (see `pixhash.py`).

A FILTERED run is the ad-hoc review tool for judging renders BEFORE they are
published: it reads `out/` and writes to `out/`, and never touches the manifest.
A filter matches as a substring, so `hero_mender` pulls in all four rarity tiers;
prefix `=` for an exact key, which is one row per hero LINE.

**One row per character, all eight frames, in order.** A row is the animation,
so the eye reads the arc along it, and the rows stack so arcs compare down the
column. Rows are bottom-aligned, because that is the edge every cell shares --
the ground row sits 10% up from the bottom of a cell whatever its size, so the
128 and 192 cells cannot both be aligned on it and the bottom is the honest
common edge.

Labels are stamped into the 1x canvas before the upscale, so label pixels are the
same size as sprite pixels. Every row is captioned with its roster key, because a
sheet that shows two attacks differ but gives no way to SAY which one needs the
edit is what cost a review round on the mender's rarity variants (user,
2026-08-01).
"""

import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelfont as F  # noqa: E402
import manifest as M   # noqa: E402

LABEL_RGBA = (0.72, 0.68, 0.60, 1.0)
GAP = 4          # blank rows between characters, in 1x pixels
UPSCALE = 3
ATTACK = os.path.join(M.RENDERED, "attack")
OUT = os.path.join(HERE, "out")


# Deliberately NOT imported from `compose_contact`, which does all its work at
# module level: importing it re-composes every canonical sheet as a side effect.
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


def rows(src_dir, keys_filter=None):
    """(key, strip path) for every attack sheet present in `src_dir`."""
    import attack_roster as R

    def wanted(key):
        if not keys_filter:
            return True
        return any(f[1:] == key if f.startswith("=") else f in key
                   for f in keys_filter)

    out = []
    for a in R.ATTACKS:
        if not wanted(a.key):
            continue
        name = ("atk_%s.png" if src_dir == OUT else "%s.png") % a.key
        p = os.path.join(src_dir, name)
        if os.path.exists(p):
            out.append((a.key, p))
    return out


def compose(entries):
    """Stack one strip per entry, captioned underneath, and upscale the result.

    Everything here is in Blender's BOTTOM-UP pixel convention, which is what
    `load_rgba` hands back and what `save_rgba` and `pixelfont.draw_block` both
    expect. Building the canvas from y=0 upward therefore lays entries out from
    the bottom, so the list is walked in reverse to put the first entry on top.
    """
    strips = [(k, load_rgba(p)) for k, p in entries]
    if not strips:
        return None
    width = max(s.shape[1] for _, s in strips)
    cap = F.block_height(1)
    height = sum(s.shape[0] + cap + GAP for _, s in strips)

    canvas = np.zeros((height, width, 4), dtype=np.float32)
    y = 0
    for key, s in reversed(strips):
        # Through `text_lines`, never the raw key: `pixelfont` carries uppercase
        # glyphs only and falls back to a BLANK for anything else, so a
        # lower-case key with underscores draws nothing at all and does it
        # silently. `text_lines` is what upper-cases and unpicks the underscores.
        F.draw_block(canvas, F.text_lines(key, width), width // 2, y, LABEL_RGBA)
        y += cap
        canvas[y:y + s.shape[0], 0:s.shape[1]] = s
        y += s.shape[0] + GAP

    big = np.repeat(np.repeat(canvas, UPSCALE, axis=0), UPSCALE, axis=1)
    bg = np.array([0.10, 0.09, 0.08, 1.0], dtype=np.float32)
    al = big[:, :, 3:4]
    big = big * al + bg * (1.0 - al)
    big[:, :, 3] = 1.0
    return big


def main():
    # Blender puts its OWN arguments in sys.argv, so only what follows `--`
    # belongs to this script.
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    filters = [a for a in argv if not a.startswith("-")]

    import attack_roster as R
    if not filters:
        os.makedirs(OUT, exist_ok=True)
        made = []
        for name, f in R.SHEET_GROUPS:
            canvas = compose(rows(ATTACK, f))
            if canvas is None:
                continue
            save_rgba(canvas, os.path.join(OUT, "sheet_attacks_%s.png" % name))
            made.append(name)
        print("attack sheet candidates -> %s: %s" % (OUT, ", ".join(made)))
        print("next: python tools/blender/publish.py")
        return 0

    # ad-hoc scratch sheet, for judging renders before they are published
    tag = "_".join(f.lstrip("=") for f in filters)
    if len(tag) > 40:
        tag = tag[:40].rstrip("_") + "_etc"
    canvas = compose(rows(OUT, filters))
    if canvas is None:
        raise SystemExit("no scratch attack renders match %s" % filters)
    path = save_rgba(canvas, os.path.join(OUT, "sheet_attacks_%s.png" % tag))
    print("%s -> scratch review sheet" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
