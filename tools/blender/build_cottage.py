"""Cottage sprite. Palette sampled off assets/raw/raw_bldg_cottage.png.

Screen orientation at this camera azimuth: the -Y wall lands on screen LEFT,
the +X wall on screen RIGHT. Door goes left, window right, matching the reference.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

scn = P.get_scene()
P.ensure_rig(scn)          # no window in background Blender; ensure_rig activates safely
P.setup_render(scn, res=96)
P.clear_scene(scn)

P.place_cam(scn, target=(0, 0, 1.55), rx_deg=59, rz_deg=38, dist=20, ortho=6.1)
px = P.pixel_size(scn)

# Key light from screen-upper-left but biased toward the camera, so BOTH visible
# faces stay lit and separate by tilt rather than one half going black.
scn.collection.objects["KeySun"].rotation_euler = (math.radians(46), 0, math.radians(-39))

THATCH = P.toon_mat("THATCH", "#a8863c", "#d4b563", "#ecd591")
PLASTER = P.toon_mat("PLASTER", "#8e8474", "#b9ae9c", "#dcd3c4")
TIMBER = P.toon_mat("TIMBER", "#472d18", "#6b4526", "#8f6539")
STONE = P.toon_mat("STONE", "#55554f", "#77776f", "#9c9c94")
GLOW = P.flat_mat("WINDOWGLOW", "#ffcf5c")

W, D = 1.45, 1.05
PLINTH, WALL_T = 0.42, 2.25

o = []
o.append(P.add_box(scn, "plinth", (0, 0, PLINTH / 2), (W * 2.09, D * 2.09, PLINTH), STONE))
o.append(P.add_box(scn, "walls", (0, 0, (PLINTH + WALL_T) / 2),
                   (W * 2, D * 2, WALL_T - PLINTH), PLASTER))

# timber framing: corner posts, one mid post per long wall, top plate, waist rail
for sx in (-1, 1):
    for sy in (-1, 1):
        o.append(P.add_box(scn, "post", (sx * W, sy * D, (PLINTH + WALL_T) / 2),
                           (0.21, 0.21, WALL_T - PLINTH), TIMBER))
    o.append(P.add_box(scn, "midpostX", (sx * W, 0, (PLINTH + WALL_T) / 2),
                       (0.18, 0.18, WALL_T - PLINTH), TIMBER))
    o.append(P.add_box(scn, "midpostY", (0, sx * D, (PLINTH + WALL_T) / 2),
                       (0.18, 0.18, WALL_T - PLINTH), TIMBER))
for z, t in ((WALL_T - 0.10, 0.20), (1.28, 0.14)):
    o.append(P.add_box(scn, "rail", (0, 0, z), (W * 2.04, D * 2.04, t), TIMBER))

# thatched gable roof, ridge running along Y so both slopes read on screen
OH, RIDGE, EAVE = 0.30, 1.05, 0.28
roof_pts = [(-W - OH, WALL_T - 0.08), (0, WALL_T + RIDGE), (W + OH, WALL_T - 0.08),
            (W + OH, WALL_T - 0.08 - EAVE), (0, WALL_T + RIDGE - EAVE),
            (-W - OH, WALL_T - 0.08 - EAVE)]
o.append(P.add_prism(scn, "roof", roof_pts, depth=D * 2 + 0.48, mat=THATCH))
for sy in (-1, 1):
    o.append(P.add_prism(scn, "gable",
                         [(-W, WALL_T - 0.10), (0, WALL_T + RIDGE - 0.26), (W, WALL_T - 0.10)],
                         depth=0.16, mat=PLASTER, loc=(0, sy * D, 0)))

# door -> screen left (-Y wall)
o.append(P.add_box(scn, "doorframe", (-0.30, -D - 0.02, (PLINTH + 1.62) / 2),
                   (0.86, 0.14, 1.62 - PLINTH + 0.12), TIMBER))
o.append(P.add_box(scn, "door", (-0.30, -D - 0.08, (PLINTH + 1.52) / 2),
                   (0.62, 0.10, 1.52 - PLINTH), P.toon_mat("DOORWOOD", "#3a2413", "#5a3a1f", "#7a5230")))
# window -> screen right (+X wall)
o.append(P.add_box(scn, "winframe", (W + 0.02, -0.22, 1.58), (0.14, 0.72, 0.66), TIMBER))
o.append(P.add_box(scn, "winpane", (W + 0.08, -0.22, 1.58), (0.10, 0.50, 0.46), GLOW))

o.append(P.add_box(scn, "chimney", (0.55, 0.62, WALL_T + 0.78), (0.36, 0.36, 1.6), STONE))

P.outline_all(scn, px, width_px=1.6)
P.render_to(scn, os.path.join(OUT, "out_cottage.png"))
P.upscale_nearest(os.path.join(OUT, "out_cottage.png"), os.path.join(OUT, "out_cottage_big.png"), 8, bg="#ff00ff")
print("cottage done, parts:", len(o))
