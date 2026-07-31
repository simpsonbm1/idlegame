"""Cottage -- M15_ASSET_SPECS.md entry 47.

  "a humble one-room peasant cottage: rough fieldstone base, wattle-and-daub
   walls, thatched roof, plank door, one warm lit window"

The pilot building, rebuilt on the shared kit. It was originally rendered at
`6.1 / 96`, which put its pixels 1.6 times larger than a character's; it now
matches every other sprite's density and is sized against the same
`BUILDING_HEIGHT` as its neighbours.
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

W, D = 1.45, 1.05
PLINTH, WALL_T = 0.42, 2.25

parts += B.walls(scn, M, W, D, WALL_T, plinth=PLINTH)
parts += B.framing(scn, M, W, D, PLINTH, WALL_T, rails=((WALL_T - 0.10, 0.20), (1.28, 0.14)))
parts += B.gable_roof(scn, M, W, D, WALL_T - 0.08, 1.05, M["thatch"])
parts += B.gable_ends(scn, M, W, D, WALL_T - 0.10, 1.05, M["plaster"])
parts += B.door(scn, M, -0.30, -D, PLINTH)
f, pane = B.window(scn, M, "right", -0.22, W, 1.58)
parts.append(f)
noline.append(pane)
parts += B.chimney(scn, M, 0.55, 0.62, WALL_T)

B.finish(scn, px, "cottage", parts, noline, detail, kind="cottage")
