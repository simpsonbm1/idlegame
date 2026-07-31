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

# Palette of the backdrop as rendered. Unit shadows darken the ground and then
# snap back onto this, so a shadow never introduces a colour the scene does not
# already contain -- which is what keeps it reading as pixel art rather than as a
# translucent overlay laid on top.
_flat = bg[:, :, :3].reshape(-1, 3)
_u, _c = np.unique((_flat * 255).astype(np.uint8), axis=0, return_counts=True)
PALETTE = (_u[np.argsort(-_c)[:96]].astype(np.float32)) / 255.0

PX_PER_UNIT = ZOOM / (BG_ORTHO / BG_W)     # screen pixels per world unit across
DARKEN = 0.56


def ground_shadow(dst, wx, wy, rx_w=0.78, ry_w=0.30, dx_w=0.55, dy_w=-0.10):
    """Contact shadow under a unit standing at world (wx, wy).

    Offset toward where the sun throws it, which on this backdrop is right and
    slightly down. A geometrically full-length shadow would run about 94 screen
    pixels from a 40-pixel-wide figure and turn a formation into a thicket, so
    this is a contact ellipse rather than a true projection.
    """
    cx = (wx + dx_w + BG_ORTHO / 2) * PX_PER_UNIT
    cy = (BG_H / 2 + (wy + dy_w) * UPY / (BG_ORTHO / BG_W)) * ZOOM
    ax, ay = rx_w * PX_PER_UNIT, ry_w * PX_PER_UNIT * UPY
    x0, x1 = int(cx - ax) - 1, int(cx + ax) + 2
    y0, y1 = int(cy - ay) - 1, int(cy + ay) + 2
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(dst.shape[1], x1), min(dst.shape[0], y1)
    if x1 <= x0 or y1 <= y0:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    inside = (((xs + 0.5 - cx) / ax) ** 2 + ((ys + 0.5 - cy) / ay) ** 2) <= 1.0
    if not inside.any():
        return
    patch = dst[y0:y1, x0:x1, :3]
    dark = patch[inside] * DARKEN
    d = ((dark[:, None, :] - PALETTE[None, :, :]) ** 2).sum(axis=2)
    patch[inside] = PALETTE[np.argmin(d, axis=1)]


# The wall throws its shadow to the RIGHT, so the band from x = -1.8 to about
# x = 1.9 is in shade. A brightly lit sprite standing in it reads as pasted on,
# so the battle line forms up clear of it.
KNIGHTS = ((3.2, -5.0), (5.3, -6.4), (4.0, -8.0))
GOBLINS = ((11.8, -5.0), (13.9, -6.4), (12.5, -8.0))
# Goblins are broader than knights, so their shadow is too.
for wx, wy in KNIGHTS:
    ground_shadow(bg, wx, wy)
for wx, wy in GOBLINS:
    ground_shadow(bg, wx, wy, rx_w=0.95, ry_w=0.36)
for wx, wy in KNIGHTS:
    seat(bg, knight, wx, wy)
for wx, wy in GOBLINS:
    seat(bg, goblin, wx, wy)

out = bpy.data.images.new("vista", bg.shape[1], bg.shape[0], alpha=True)
out.pixels.foreach_set(bg.ravel())
out.file_format = 'PNG'
out.filepath_raw = os.path.join(OUT, "out_vista.png")
out.save()
bpy.data.images.remove(out)
print("vista %dx%d, six figures seated by world coordinate" % (bg.shape[1], bg.shape[0]))
