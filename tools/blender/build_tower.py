"""Wizard's tower -- M15_ASSET_SPECS.md entry 54.

  "a slender wizard's tower: pale stone spiraling slightly as it rises, conical
   deep-blue roof, a single glowing arcane window near the top"

The tallest and thinnest thing in the town, and the only CONICAL roof. Height
and a point are its whole silhouette, so nothing else on it needs to be busy.

The spiral is built as a stack of drums each turned a few degrees further than
the last, which at this size shows up as the courses shifting rather than as a
visible twist. That is the correct amount: a tower that visibly corkscrews reads
as broken rather than as magical.
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

R_BASE, R_TOP = 0.92, 0.68
DRUMS, DRUM_H = 9, 0.62

for i in range(DRUMS):
    t = i / (DRUMS - 1.0)
    r = R_BASE + (R_TOP - R_BASE) * t
    parts.append(P.add_cyl(scn, "drum", (0, 0, 0.34 + i * DRUM_H + DRUM_H / 2), r, DRUM_H,
                           M["stone"], verts=10, rot=(0, 0, math.radians(i * 7.5))))
    if i % 2 == 0:
        parts.append(P.add_cyl(scn, "course", (0, 0, 0.34 + i * DRUM_H), r * 1.06, 0.11,
                               M["darkstone"], verts=10, rot=(0, 0, math.radians(i * 7.5))))
parts.append(P.add_cyl(scn, "towerbase", (0, 0, 0.17), R_BASE * 1.22, 0.34, M["darkstone"], verts=10))
TOP = 0.34 + DRUMS * DRUM_H
parts.append(P.add_cyl(scn, "corbel", (0, 0, TOP + 0.10), R_TOP * 1.26, 0.24, M["stone"], verts=10))
parts.append(P.add_cone(scn, "conicalroof", (0, 0, TOP + 1.32), R_TOP * 1.34, 0.0, 2.20,
                        M["bluetile"], verts=10))
parts.append(P.add_sphere(scn, "finial", (0, 0, TOP + 2.52), 0.14, M["gold"], segs=8, rings=6))
parts += B.door(scn, M, 0.0, -R_BASE * 1.02, 0.34, wide=0.48, tall=1.34, arch=True)
# the single arcane window, near the top so the eye is led up the shaft
parts.append(P.add_box(scn, "arcframe", (0.0, -R_TOP - 0.02, TOP - 1.00), (0.62, 0.14, 0.86), M["timber"]))
noline.append(P.add_box(scn, "arcpane", (0.0, -R_TOP - 0.09, TOP - 1.00), (0.44, 0.10, 0.68), M["arcane"]))
for i, dz in enumerate((0.44, 0.72, 0.96)):
    noline.append(P.add_sphere(scn, "arcwisp", (0.10 * (i % 2), -R_TOP - 0.14, TOP - 1.00 + dz),
                               0.09 - i * 0.02, M["arcane"], segs=8, rings=5))
# two small slit windows lower down, so the shaft is not blank
for z in (2.20, 3.80):
    detail.append(P.add_box(scn, "towerslit", (0.0, -R_BASE - 0.02, z), (0.13, 0.06, 0.52), M["dark"]))

B.finish(scn, px, "tower", parts, noline, detail, kind="tower")
