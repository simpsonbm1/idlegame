"""Keep -- M15_ASSET_SPECS.md entry 52.

  "a square stone keep tower: crenellated top, arrow slits, heavy ironbound
   door, a small pennant flying from one corner"

Crenellations are the entry, and they are the only notched top edge in the town.
A row of blocks with gaps between them is unmistakable at any size, which is why
real castles are drawn that way in every medium.

Arrow slits are cut as DARK BARS rather than as recesses. At this density a
recess is a couple of pixels of shading and disappears; a hard black slot on a
pale wall survives.
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
px = B.start(scn, res=224)
M = B.palette()

parts, noline, detail = [], [], []

W, D = 1.30, 1.30
WALL_T = 4.30
MERLON = 0.46

parts += B.walls(scn, M, W, D, WALL_T, plinth=0.50, mat=M["stone"], plinth_mat=M["darkstone"])
# a slight batter: the base is wider than the top, which every real keep has
parts.append(P.add_box(scn, "batter", (0, 0, 0.90), (W * 2.16, D * 2.16, 0.90), M["stone"]))
# the crenellated parapet
parts.append(P.add_box(scn, "parapet", (0, 0, WALL_T + 0.14), (W * 2.20, D * 2.20, 0.28), M["stone"]))
n = 5
for i in range(n):
    t = -1.0 + 2.0 * i / (n - 1.0)
    for sy in (-1, 1):
        parts.append(P.add_box(scn, "merlon", (t * W * 0.92, sy * D * 1.05, WALL_T + 0.28 + MERLON / 2),
                               (W * 2 / n * 0.62, 0.24, MERLON), M["stone"]))
    for sx in (-1, 1):
        parts.append(P.add_box(scn, "merlon", (sx * W * 1.05, t * D * 0.92, WALL_T + 0.28 + MERLON / 2),
                               (0.24, D * 2 / n * 0.62, MERLON), M["stone"]))
parts += B.door(scn, M, -0.10, -D, 0.50, wide=0.56, tall=1.56, arch=True)
for i, s in enumerate((-1, 1)):
    detail.append(P.add_box(scn, "ironband", (-0.10, -D - 0.14, 0.90 + i * 0.60), (1.10, 0.05, 0.13), M["iron"]))
# arrow slits: hard dark bars, since a recess is a couple of pixels and vanishes
for z in (2.10, 3.10):
    detail.append(P.add_box(scn, "slit", (-0.30, -D - 0.03, z), (0.13, 0.06, 0.62), M["dark"]))
    detail.append(P.add_box(scn, "slit", (W + 0.03, 0.30, z), (0.06, 0.13, 0.62), M["dark"]))
# the pennant on one corner
parts.append(P.add_cyl(scn, "flagpole", (-W * 1.05, -D * 1.05, WALL_T + 1.30), 0.06, 2.00, M["timber"], verts=5))
parts.append(P.add_prism(scn, "pennant", [(0.0, 0.0), (0.86, -0.18), (0.0, -0.40)], 0.05, M["cloth"],
                         loc=(-W * 1.05, -D * 1.05, WALL_T + 2.20)))

B.finish(scn, px, "keep", parts, noline, detail, kind="keep")
