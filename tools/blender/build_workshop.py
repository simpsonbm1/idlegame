"""Workshop -- M15_ASSET_SPECS.md entry 50.

  "a practical carpenter's workshop: plank walls, wide barn-style door,
   stacked lumber against one wall, sawhorse out front against the wall"

The barn door is nearly the whole screen-left wall, which makes this the only
building whose front is mostly opening. Where the smithy's opening is dark and
glowing, this one is closed and planked, so the two never read as each other.

The stacked lumber is a run of separated bars rather than a solid block. Timber
in a pile is legible as timber because of the gaps between the pieces, the same
reason a ribcage has to be built as bars.
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

W, D = 1.70, 1.15
WALL_T = 2.15

parts += B.walls(scn, M, W, D, WALL_T, plinth=0.30, mat=M["timber"], plinth_mat=M["stone"])
for i in range(9):
    x = -W + 0.02 + (i + 0.5) * (W * 2 - 0.04) / 9.0
    parts.append(P.add_box(scn, "plank", (x, -D - 0.05, (0.30 + WALL_T) / 2),
                           ((W * 2) / 9.0 * 0.80, 0.10, WALL_T - 0.30), M["door"]))
parts += B.framing(scn, M, W, D, 0.30, WALL_T, rails=((WALL_T - 0.10, 0.20),))
# Slate, not shingle, and a real pitch. Brown planks under a brown roof at a
# shallow angle gave one flat brown mass with no building inside it.
parts += B.gable_roof(scn, M, W, D, WALL_T - 0.08, 1.65, M["slate"], overhang=0.36)
parts += B.gable_ends(scn, M, W, D, WALL_T - 0.10, 1.65, M["plaster"])
parts.append(P.add_box(scn, "barnframe", (-0.10, -D - 0.10, 1.10), (1.72, 0.14, 1.70), M["timber"]))
for s in (-1, 1):
    parts.append(P.add_box(scn, "barnleaf", (-0.10 + s * 0.40, -D - 0.16, 1.06),
                           (0.74, 0.10, 1.54), M["door"]))
    detail.append(P.add_box(scn, "barnbrace", (-0.10 + s * 0.40, -D - 0.23, 1.06),
                            (0.84, 0.05, 0.13), M["timber"], rot=(math.radians(s * 34), 0, 0)))
for row in range(3):
    for col in range(3):
        parts.append(P.add_box(scn, "lumber", (W + 0.26, -0.30 + col * 0.30, 0.32 + row * 0.26),
                               (0.62, 0.24, 0.20), M["door"]))
parts.append(P.add_box(scn, "sawtop", (0.90, -D - 0.62, 0.72), (0.16, 0.86, 0.13), M["timber"]))
for sy in (-1, 1):
    for sx in (-1, 1):
        parts.append(P.add_cyl(scn, "sawleg", (0.90 + sx * 0.16, -D - 0.62 + sy * 0.30, 0.36),
                               0.055, 0.72, M["timber"], verts=5,
                               rot=(math.radians(sy * 14), 0, math.radians(-sx * 14))))

B.finish(scn, px, "workshop", parts, noline, detail, kind="workshop")
