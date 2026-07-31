"""Smithy -- M15_ASSET_SPECS.md entry 49.

  "a sturdy stone smithy: open working front with a glowing forge inside,
   stout chimney trailing smoke, anvil silhouette visible in the doorway"

The open front is the entry, and it is the only building in the town with a hole
in it. That hole is where the forge glow comes from, and an orange rectangle low
in a grey stone wall identifies it faster than any sign could.

The anvil stands INSIDE the opening rather than beside the building, so it reads
as a silhouette against the glow instead of as a separate small object that
would be lost at this size.
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

W, D = 1.60, 1.20
WALL_T = 2.30

parts += B.walls(scn, M, W, D, WALL_T, plinth=0.40, mat=M["stone"], plinth_mat=M["darkstone"])
parts.append(P.add_box(scn, "forgerecess", (-0.10, -D - 0.02, 1.14), (1.28, 0.22, 1.44), M["darkstone"]))
noline.append(P.add_box(scn, "forgeglow", (-0.10, -D - 0.10, 0.98), (1.06, 0.10, 1.02), M["forge"]))
detail.append(P.add_box(scn, "anvilbody", (-0.10, -D - 0.18, 0.78), (0.46, 0.14, 0.22), M["iron"]))
detail.append(P.add_box(scn, "anvilstem", (-0.10, -D - 0.18, 0.58), (0.18, 0.12, 0.22), M["iron"]))
detail.append(P.add_box(scn, "anvilfoot", (-0.10, -D - 0.18, 0.44), (0.34, 0.13, 0.10), M["iron"]))
parts += B.gable_roof(scn, M, W, D, WALL_T - 0.08, 0.86, M["shingle"], overhang=0.34)
parts += B.gable_ends(scn, M, W, D, WALL_T - 0.10, 0.86, M["stone"])
f, pane = B.window(scn, M, "right", -0.30, W, 1.62, w=0.40, h=0.40)
parts.append(f)
noline.append(pane)
parts += B.chimney(scn, M, 0.70, 0.70, WALL_T - 0.30, h=2.30, w=0.46, mat=M["darkstone"])
for i, (dz, r) in enumerate(((0.30, 0.24), (0.66, 0.30), (1.02, 0.24))):
    detail.append(P.add_sphere(scn, "smoke", (0.70 + i * 0.10, 0.70, WALL_T + 2.06 + dz), r,
                               M["stone"], segs=8, rings=6))

B.finish(scn, px, "smithy", parts, noline, detail, kind="smithy")
