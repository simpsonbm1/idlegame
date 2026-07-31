"""Characters standing on the backdrop, at true relative scale.

The backdrop renders at 2x SPRITE_PX, so displaying it at 2x makes one screen
pixel equal one character pixel and the sprites drop on at 1:1 with no fitting.
Figures are seated by WORLD coordinate, projected through the backdrop camera,
so a unit asked to stand at (x, y) lands exactly there on the ground.

Run after build_backdrop.py, build_knight.py and build_goblin.py.
"""

import bpy, math, os, sys, importlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

ZOOM = 2                                   # backdrop px -> character px
BG_ORTHO, BG_W, BG_H = 60.0, 768, 406
RX = 28.0
UPY = math.cos(math.radians(RX))           # screen rise per world unit of Y
FEET_UP = 10                               # rows above a sprite cell's bottom edge


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return buf.reshape(h, w, 4)            # row 0 is the BOTTOM row


def paste(dst, src, x, y):
    sh, sw = src.shape[:2]
    dh, dw = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dw, x + sw), min(dh, y + sh)
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[:, :, 3:4]
    d = dst[y0:y1, x0:x1]
    d[:, :, :3] = s[:, :, :3] * a + d[:, :, :3] * (1 - a)
    d[:, :, 3:4] = np.clip(a + d[:, :, 3:4] * (1 - a), 0, 1)


def seat(dst, sprite, wx, wy):
    """Place a sprite so its feet stand on world point (wx, wy) of the ground."""
    cell = sprite.shape[0]
    px_x = (wx + BG_ORTHO / 2) / (BG_ORTHO / BG_W) * ZOOM
    row_from_bottom = (BG_H / 2 + wy * UPY / (BG_ORTHO / BG_W)) * ZOOM
    paste(dst, sprite, int(px_x - cell / 2), int(row_from_bottom - FEET_UP))


bg = load_rgba(os.path.join(OUT, "out_backdrop.png"))
bg = np.repeat(np.repeat(bg, ZOOM, axis=0), ZOOM, axis=1).copy()
knight = load_rgba(os.path.join(OUT, "out_knight.png"))
goblin = load_rgba(os.path.join(OUT, "out_goblin.png"))

for wx, wy in ((0.6, -5.0), (2.6, -6.4), (1.4, -8.0)):
    seat(bg, knight, wx, wy)
for wx, wy in ((9.5, -5.0), (11.6, -6.4), (10.2, -8.0)):
    seat(bg, goblin, wx, wy)

out = bpy.data.images.new("vista", bg.shape[1], bg.shape[0], alpha=True)
out.pixels.foreach_set(bg.ravel())
out.file_format = 'PNG'
out.filepath_raw = os.path.join(OUT, "out_vista.png")
out.save()
bpy.data.images.remove(out)
print("vista %dx%d, six figures seated by world coordinate" % (bg.shape[1], bg.shape[0]))
