"""Tavern -- M15_ASSET_SPECS.md entry 48.

  "a wide cheerful two-story tavern: timber-framed walls, shingled roof,
   hanging wooden sign with a foaming mug painted on it, several warm lit windows"

WIDE is the entry. Every other building in the town is taller than it is broad,
so the tavern is the one whose footprint spreads, and that alone identifies it
in a row of rooftops.

Its second storey JETTIES: it oversails the ground floor on every side the way a
real timber-framed one does. That cuts a hard shadow line right around the
building at first-floor height, which is worth more than surface detail here.
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

W, D = 2.05, 1.35
GROUND, UPPER = 2.05, 1.90
JW, JD = W + 0.16, D + 0.16

parts += B.walls(scn, M, W, D, GROUND, plinth=0.34)
parts += B.framing(scn, M, W, D, 0.34, GROUND, rails=((GROUND - 0.10, 0.18),))
parts += B.walls(scn, M, JW, JD, UPPER, base=GROUND)
parts += B.framing(scn, M, JW, JD, GROUND, GROUND + UPPER,
                   rails=((GROUND + 0.08, 0.20), (GROUND + UPPER - 0.10, 0.20)))
# The ridge has to clear a QUARTER of the span or the roof reads as a flat slab
# from this camera angle. At 1.20 over a 4.4-wide building it did exactly that.
parts += B.gable_roof(scn, M, JW, JD, GROUND + UPPER - 0.08, 2.10, M["shingle"], overhang=0.34)
parts += B.gable_ends(scn, M, JW, JD, GROUND + UPPER - 0.10, 2.10, M["plaster"])
parts += B.door(scn, M, -0.55, -D, 0.34, wide=0.72, tall=1.62)
for a, z, wall in ((0.85, 1.30, -D), (-0.55, GROUND + 1.00, -JD), (0.85, GROUND + 1.00, -JD)):
    f, pane = B.window(scn, M, "left", a, wall, z, w=0.44, h=0.52)
    parts.append(f)
    noline.append(pane)
for a, z, wall in ((-0.30, 1.34, W), (0.55, GROUND + 1.00, JW)):
    f, pane = B.window(scn, M, "right", a, wall, z, w=0.44, h=0.52)
    parts.append(f)
    noline.append(pane)
parts += B.hanging_sign(scn, M, -W - 0.10, -D - 0.10, GROUND + 0.30, M["door"])
detail.append(P.add_cyl(scn, "signmug", (-W - 0.10, -D - 0.66, GROUND + 0.16), 0.13, 0.10,
                        M["gold"], verts=8, rot=(math.radians(90), 0, 0)))
parts += B.chimney(scn, M, 0.90, 0.80, GROUND + UPPER, h=1.5)

B.finish(scn, px, "tavern", parts, noline, detail, kind="tavern")
