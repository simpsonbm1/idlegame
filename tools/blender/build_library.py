"""Library -- M15_ASSET_SPECS.md entry 51.

  "a tall scholarly library: stone lower floor, timbered upper floor, steep
   slate roof, one large arched window glowing warmly"

Two materials stacked, stone under timber, which is the only building in the
town that changes material halfway up. That horizontal seam is its read.

Its roof is STEEP where the tavern's is shallow, and slate-blue where the
tavern's is brown. Two two-storey buildings side by side need to differ at the
roofline, because that is the part of a building a player sees over a crowd.
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

W, D = 1.55, 1.20
GROUND, UPPER = 2.30, 2.00

parts += B.walls(scn, M, W, D, GROUND, plinth=0.36, mat=M["stone"], plinth_mat=M["darkstone"])
parts += B.walls(scn, M, W, D, UPPER, base=GROUND)
parts += B.framing(scn, M, W, D, GROUND, GROUND + UPPER,
                   rails=((GROUND + 0.10, 0.20), (GROUND + UPPER - 0.10, 0.20)))
parts += B.gable_roof(scn, M, W, D, GROUND + UPPER - 0.08, 2.10, M["slate"], overhang=0.28)
parts += B.gable_ends(scn, M, W, D, GROUND + UPPER - 0.10, 2.10, M["plaster"])
parts += B.door(scn, M, -0.34, -D, 0.36, wide=0.56, tall=1.50, arch=True)
# the one large arched window, which is the building's face
parts.append(P.add_box(scn, "archframe", (0.62, -D - 0.02, GROUND + 1.00), (0.94, 0.14, 1.40), M["timber"]))
parts.append(P.add_cyl(scn, "archtop", (0.62, -D - 0.02, GROUND + 1.70), 0.47, 0.14, M["timber"],
                       verts=10, rot=(math.radians(90), 0, 0)))
noline.append(P.add_box(scn, "archpane", (0.62, -D - 0.09, GROUND + 1.00), (0.72, 0.10, 1.24), M["glow"]))
noline.append(P.add_cyl(scn, "archpanetop", (0.62, -D - 0.09, GROUND + 1.70), 0.36, 0.10, M["glow"],
                        verts=10, rot=(math.radians(90), 0, 0)))
detail.append(P.add_box(scn, "archmullion", (0.62, -D - 0.13, GROUND + 1.20), (0.08, 0.05, 1.70), M["timber"]))
f, pane = B.window(scn, M, "right", 0.10, W, 1.50, w=0.36, h=0.50)
parts.append(f)
noline.append(pane)
parts += B.chimney(scn, M, 0.72, 0.78, GROUND + UPPER + 1.10, h=1.2, mat=M["darkstone"])

B.finish(scn, px, "library", parts, noline, detail, kind="library")
