"""Battle band: the same 3D scene, zoomed so 1 world unit renders at exactly the
same pixel scale as the character sprites, with both figures composited on it.

Matching the scale is arithmetic, not eyeballing:
    sprite pixel size = ortho / res = 3.75 / 96   = 0.0390625 world units
    band  pixel size  = ortho / res = 11.25 / 288 = 0.0390625  -- identical
So a sprite dropped on the band is automatically the right size. That is the
thing the AI pipeline cannot give you: relative scale for free.

Run AFTER build_scene.py, which leaves the vista in place.
"""

import bpy, math, os, sys, importlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

scn = P.get_scene()
bpy.context.window.scene = scn
scn.render.resolution_x, scn.render.resolution_y = 288, 96
P.place_cam(scn, target=(7.0, 0.0, 1.50), rx_deg=83, rz_deg=-14, dist=90, ortho=11.25)
P.render_to(scn, os.path.join(OUT, "out_band.png"))
print("band px:", scn.camera.data.ortho_scale / scn.render.resolution_x)


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return buf.reshape(h, w, 4)          # row 0 is the BOTTOM row in Blender


def paste(dst, src, x, y):
    """Alpha-composite src onto dst with its lower-left corner at (x, y),
    clipped to dst. Coordinates are bottom-up, matching Blender's buffer."""
    sh, sw = src.shape[:2]
    dh, dw = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dw, x + sw), min(dh, y + sh)
    if x1 <= x0 or y1 <= y0:
        return dst
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[:, :, 3:4]
    d = dst[y0:y1, x0:x1]
    d[:, :, :3] = s[:, :, :3] * a + d[:, :, :3] * (1 - a)
    d[:, :, 3:4] = np.clip(a + d[:, :, 3:4] * (1 - a), 0, 1)
    return dst


band = load_rgba(os.path.join(OUT, "out_band.png")).copy()
knight = load_rgba(os.path.join(OUT, "out_knight.png"))
goblin = load_rgba(os.path.join(OUT, "out_goblin.png"))

# Both sprite renders put ground level on the same row, so a single y offset
# seats every character on the same line.
GROUND_Y = -1
paste(band, knight, 40, GROUND_Y)
paste(band, knight, 78, GROUND_Y - 1)
paste(band, goblin, 150, GROUND_Y)
paste(band, goblin, 192, GROUND_Y - 1)

out = bpy.data.images.new("battleband", band.shape[1], band.shape[0], alpha=True)
out.pixels.foreach_set(band.ravel())
out.file_format = 'PNG'
out.filepath_raw = os.path.join(OUT, "out_battle.png")
out.save()
bpy.data.images.remove(out)
P.upscale_nearest(os.path.join(OUT, "out_battle.png"), os.path.join(OUT, "out_battle_big.png"), 4)
print("battle band composed")
