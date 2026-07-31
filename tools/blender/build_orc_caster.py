"""Orc Warband caster -- M15_ASSET_SPECS.md entry 24.

  "an orc warcaster in dark furs and black iron pauldrons, skull-topped staff,
   hurling crackling red-orange battle magic from a clawed hand"

The hurled magic is the entry, and it is the first thing in the roster that has
to read as ENERGY rather than as an object. The undead casters' flames rise and
shrink, which reads as fire; this one throws, so its blobs run outward along a
line and grow rather than shrink, and the largest is furthest from the hand.
Direction is the whole difference.

Red-orange against the family's black iron and olive hide is the strongest colour
contrast in the faction, so the throwing hand is where the eye lands.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import orc_kit as O
import pixelrig as P
importlib.reload(P)
importlib.reload(O)

scn = P.get_scene()
px = O.start(scn, res=112)
M = O.palette()

figure, detail, noline = [], [], []

HIP = 1.36
figure += O.heavy_legs(scn, M, HIP, spread=0.48)
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.14, 0.68, 0.40), M["fur"], bevel=0.06))
# a long fur skirt, which is what separates his lower half from the brute's plate
figure.append(P.add_cone(scn, "ofurskirt", (0, 0, 1.02), 0.84, 0.60, 1.10, M["fur"], verts=12))

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.16, chest_r=0.68, lean=10)
tors.append(P.add_cone(scn, "ofurmantle", (0, 0.02, 0.78), 0.86, 0.44, 0.66, M["fur"], verts=12))
tors.append(P.add_box(scn, "obelt", (0, -0.04, 0.16), (1.18, 0.72, 0.18), M["leath"]))

hd_fig, hd_det = O.head(scn, M, (0, -0.04, 1.22), r=0.46)
tors += hd_fig
tors.append(P.add_cyl(scn, "ohood", (0, 0.10, 1.34), 0.50, 0.34, M["fur"], verts=10))

# black iron pauldrons over the furs
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 0.90, -0.10, 0.90), 0.38, M["hide"],
                             scale=(1, .95, .88)))
    tors.append(P.add_sphere(scn, "opauldron", (s * 0.96, -0.10, 1.02), 0.40, M["iron"],
                             scale=(1, 1, .62)))

# staff arm down and forward, throwing arm up and out
tors.append(P.add_cyl(scn, "oupperL", (-0.94, -0.24, 0.52), 0.25, 0.66, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeL", (-0.86, -0.56, 0.06), 0.22, 0.60, M["hide"], verts=8,
                      rot=(math.radians(26), 0, 0)))
tors.append(P.add_sphere(scn, "ofistL", (-0.82, -0.70, -0.22), 0.23, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (0.98, -0.24, 1.04), 0.25, 0.62, M["hide"], verts=8,
                      rot=(0, math.radians(34), 0)))
tors.append(P.add_cyl(scn, "oforeR", (1.20, -0.44, 1.36), 0.22, 0.58, M["hide"], verts=8,
                      rot=(math.radians(-18), math.radians(26), 0)))
tors.append(P.add_sphere(scn, "oclaw", (1.32, -0.58, 1.62), 0.23, M["hide"]))
# three splayed claw fingers, which is what makes the hand read as casting
for i, s in enumerate((-1, 0, 1)):
    tors.append(P.add_cone(scn, "ofinger", (1.40 + i * 0.02, -0.72, 1.68 + s * 0.14),
                           0.055, 0.02, 0.26, M["hide"],
                           rot=(0, math.radians(74), math.radians(s * 16)), verts=5))

P.parent_all(tors_root, tors + hd_det)

# ---- the hurled magic: blobs running OUTWARD and GROWING, which is what makes
# it read as thrown rather than as a flame held in the hand.
for i, (d, r) in enumerate(((0.30, 0.10), (0.56, 0.145), (0.86, 0.19), (1.20, 0.13))):
    noline.append(P.add_sphere(scn, "obolt", (1.62 + d * 0.72, -0.86 - d * 0.16, 2.86 + d * 0.30),
                               r, M["ember"] if i < 3 else M["ember_d"], segs=8, rings=5))
# crackle: two small blobs off the line, so it does not read as a string of beads
for dx, dy, dz, r in ((2.30, -1.06, 3.42, 0.075), (2.62, -1.10, 3.02, 0.06)):
    noline.append(P.add_sphere(scn, "ospark", (dx, dy, dz), r, M["ember_d"], segs=8, rings=5))

# ---- skull-topped staff ----
st_root = P.make_root(scn, "staff_root", rot=(0, -10, 0), loc=(-0.92, -0.76, 1.24))
staff = [P.add_cyl(scn, "oshaft", (0, 0, 0), 0.07, 3.00, M["wood"], verts=6)]
for z in (-1.10, -0.30, 0.52):
    staff.append(P.add_cyl(scn, "olash", (0, 0, z), 0.10, 0.10, M["leath"], verts=6))
staff.append(P.add_sphere(scn, "ostaffskull", (0, -0.04, 1.62), 0.22, M["bone"],
                          scale=(1, 1.02, 1.08), segs=10, rings=7))
staff.append(P.add_box(scn, "ostaffjaw", (0, -0.12, 1.46), (0.20, 0.16, 0.11), M["bone"]))
for s in (-1, 1):
    staff.append(P.add_cone(scn, "ostaffhorn", (s * 0.18, -0.02, 1.76), 0.055, 0.0, 0.30, M["tusk"],
                            rot=(0, math.radians(s * 40), 0), verts=6))
eyes = [P.add_box(scn, "ostaffeye", (s * 0.085, -0.22, 1.66), (0.08, 0.05, 0.07), M["ember"])
        for s in (-1, 1)]
P.parent_all(st_root, staff + eyes)

O.finish(scn, px, "orc_caster", figure, detail, noline, roots=[tors_root, st_root],
         skip_extra=tuple(o.name for o in hd_det + eyes), role="caster", body_roots=[tors_root])
