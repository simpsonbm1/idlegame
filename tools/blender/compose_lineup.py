"""Family lineup: every finished character sprite on one strip.

Its only job is to make style drift visible if there ever is any. Because all of
them come off the same rig, the outline weight, tone-band positions, sun angle
and pixel scale are identical by construction rather than by inspection.
"""

import bpy, os, sys, importlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

SPRITES = ["out_knight.png", "out_goblin.png", "out_undead_caster.png"]
CELL = 112      # widest sprite cell in the set; narrower sprites are centred


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return buf.reshape(h, w, 4)


strip = np.zeros((CELL, CELL * len(SPRITES), 4), dtype=np.float32)
for i, name in enumerate(SPRITES):
    s = load_rgba(os.path.join(OUT, name))
    h, w = s.shape[:2]
    x = i * CELL + (CELL - w) // 2
    strip[0:h, x:x + w] = s

out = bpy.data.images.new("lineup", strip.shape[1], strip.shape[0], alpha=True)
out.pixels.foreach_set(strip.ravel())
out.file_format = 'PNG'
out.filepath_raw = os.path.join(OUT, "out_lineup.png")
out.save()
bpy.data.images.remove(out)
P.upscale_nearest(os.path.join(OUT, "out_lineup.png"),
                  os.path.join(OUT, "out_lineup_big.png"), 5, bg="#2a2320")
print("lineup written:", len(SPRITES), "sprites")
