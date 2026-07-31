"""Apothecary -- M15_ASSET_SPECS.md entry 53.

  "a crooked herbalist's shop: moss-green shingled roof, drying herb bundles
   hung under the eaves, round window, hanging sign with a potion bottle"

CROOKED is the entry, and it is the only thing in the town that is not square.
The walls lean, the roof sits askew and the chimney tilts the other way. In a
row of upright buildings one that is visibly off-plumb is identified instantly.

It is also the only ROUND window in the town, against everyone else's
rectangles and the library's arch.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import building_kit as B
import pixelrig as P
importlib.reload(P)
importlib.reload(B)

scn = P.get_scene()
px = B.start(scn, res=192)
M = B.palette()

parts, noline, detail = [], [], []

W, D = 1.35, 1.05
WALL_T = 2.35

parts += B.walls(scn, M, W, D, WALL_T, plinth=0.32)
parts += B.framing(scn, M, W, D, 0.32, WALL_T, rails=((WALL_T - 0.10, 0.18), (1.30, 0.14)))
# the lean: the whole upper structure is tipped, which is the entry's read
for ob in parts:
    ob.rotation_euler = (0, math.radians(-3.5), 0)
parts += B.gable_roof(scn, M, W, D, WALL_T - 0.06, 1.00, M["mossroof"], overhang=0.40)
parts += B.gable_ends(scn, M, W, D, WALL_T - 0.10, 1.00, M["plaster"])
for ob in parts[-3:]:
    ob.rotation_euler = (0, math.radians(-6.0), 0)
parts += B.door(scn, M, -0.42, -D, 0.32, wide=0.54, tall=1.46)
# the round window
parts.append(P.add_cyl(scn, "roundframe", (W + 0.02, -0.16, 1.62), 0.42, 0.14, M["timber"],
                       verts=10, rot=(0, math.radians(90), 0)))
noline.append(P.add_cyl(scn, "roundpane", (W + 0.09, -0.16, 1.62), 0.31, 0.10, M["green"],
                        verts=10, rot=(0, math.radians(90), 0)))
# herb bundles under the eaves: cones hanging point-down, staggered
for i, a in enumerate((-0.72, -0.24, 0.28, 0.76)):
    detail.append(P.add_cone(scn, "herbs", (a, -D - 0.18, WALL_T - 0.42 - (i % 2) * 0.14),
                             0.14, 0.03, 0.44, M["mossroof"], rot=(math.radians(180), 0, 0), verts=6))
parts += B.hanging_sign(scn, M, -W - 0.10, -D - 0.06, 1.96, M["door"])
detail.append(P.add_cyl(scn, "signbottle", (-W - 0.10, -D - 0.57, 1.82), 0.11, 0.10, M["green"],
                        verts=8, rot=(math.radians(90), 0, 0)))
parts += B.chimney(scn, M, 0.48, 0.56, WALL_T, h=1.5)
for ob in parts[-2:]:
    ob.rotation_euler = (0, math.radians(7.0), 0)

B.finish(scn, px, "apothecary", parts, noline, detail, kind="apothecary")
