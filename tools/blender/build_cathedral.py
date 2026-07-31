"""Cathedral -- M15_ASSET_SPECS.md entry 55.

  "a grand stone cathedral: pointed arched entrance, large round rose window
   glowing gold, twin spires, the tallest and most ornate building of the set"

The showpiece of the town, and the only building with TWIN anything. Two spires
flanking a gable is a shape no other building in the set has, and it reads from
as far away as the wizard's tower does while saying something completely
different.

The rose window is the largest single light source in the town. It is built as a
glowing disc with spokes over it rather than as tracery, because tracery at this
density is a grey smudge and spokes are four hard lines.
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
px = B.start(scn, res=256)
M = B.palette()

parts, noline, detail = [], [], []

W, D = 1.75, 1.45
NAVE = 3.60

parts += B.walls(scn, M, W, D, NAVE, plinth=0.46, mat=M["stone"], plinth_mat=M["darkstone"])
parts += B.gable_roof(scn, M, W, D, NAVE - 0.08, 1.70, M["slate"], overhang=0.24)
parts += B.gable_ends(scn, M, W, D, NAVE - 0.10, 1.70, M["stone"])
# buttresses down the long wall, which is what makes it read as ecclesiastical
for a in (-0.86, 0.0, 0.86):
    parts.append(P.add_box(scn, "buttress", (a, -D - 0.16, 1.30), (0.34, 0.42, 2.60), M["stone"]))
    parts.append(P.add_cone(scn, "buttresscap", (a, -D - 0.16, 2.78), 0.24, 0.06, 0.42, M["stone"], verts=4,
                            rot=(0, 0, math.radians(45))))
# the pointed arched entrance
parts.append(P.add_box(scn, "portal", (-0.02, -D - 0.10, 1.10), (1.06, 0.24, 1.60), M["darkstone"]))
parts.append(P.add_cone(scn, "portalarch", (-0.02, -D - 0.10, 2.12), 0.62, 0.0, 0.90, M["darkstone"],
                        verts=4, rot=(math.radians(90), 0, math.radians(45))))
parts.append(P.add_box(scn, "cathdoor", (-0.02, -D - 0.20, 1.02), (0.80, 0.10, 1.42), M["door"]))
detail.append(P.add_box(scn, "doorsplit", (-0.02, -D - 0.26, 1.02), (0.07, 0.05, 1.42), M["iron"]))
# the rose window: a glowing disc with hard spokes, not tracery
parts.append(P.add_cyl(scn, "roseframe", (-0.02, -D - 0.06, 3.30), 0.76, 0.16, M["stone"],
                       verts=12, rot=(math.radians(90), 0, 0)))
noline.append(P.add_cyl(scn, "rosepane", (-0.02, -D - 0.14, 3.30), 0.62, 0.10, M["glow"],
                        verts=12, rot=(math.radians(90), 0, 0)))
for i in range(4):
    a = math.radians(i * 45)
    detail.append(P.add_box(scn, "rosespoke", (-0.02, -D - 0.19, 3.30), (1.20, 0.05, 0.09), M["stone"],
                            rot=(0, -a, 0)))
# twin spires flanking the gable
for sx in (-1, 1):
    x = sx * (W + 0.42)
    parts.append(P.add_box(scn, "spirebase", (x, -D * 0.30, 2.40), (0.78, 0.78, 4.80), M["stone"]))
    parts.append(P.add_box(scn, "spirecorbel", (x, -D * 0.30, 4.92), (0.94, 0.94, 0.26), M["stone"]))
    parts.append(P.add_cone(scn, "spireroof", (x, -D * 0.30, 6.10), 0.62, 0.0, 2.10, M["slate"], verts=8))
    parts.append(P.add_sphere(scn, "spirefinial", (x, -D * 0.30, 7.24), 0.11, M["gold"], segs=8, rings=6))
    detail.append(P.add_box(scn, "spireslit", (x, -D * 0.30 - 0.40, 3.90), (0.14, 0.06, 0.72), M["dark"]))

B.finish(scn, px, "cathedral", parts, noline, detail, kind="cathedral")
