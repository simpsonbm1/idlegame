"""Orc Warband shaman -- M15_ASSET_SPECS.md entry 25.

  "an orc witch doctor in a horned wooden mask and bone jewelry, feathered fetish
   staff with a glowing charm"

The mask is the entry, and it does something no other head in the roster does: it
REPLACES the face. Every other figure is identified by what its face is doing, so
a blank painted board with two slots and a pair of horns is instantly the odd one
out, which is exactly what a witch doctor should be.

He and the goblin shaman both carry feathers and a charm, which is deliberate --
the two families are meant to share a shamanic idea. They are separated by scale
and by palette, not by concept: this one is a head taller, olive rather than
mossy, and his charm burns ember-orange where the goblin's is green.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import orc_kit as O
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(O)

scn = P.get_scene()
px = O.start(scn, res=112)
M = O.palette()

figure, detail, noline = [], [], []

HIP = 1.34
figure += O.heavy_legs(scn, M, HIP, spread=0.48)
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.12, 0.66, 0.40), M["hide"], bevel=0.06))
figure.append(P.add_cone(scn, "ograsskirt", (0, 0, 1.06), 0.80, 0.58, 0.98, M["fur"], verts=12))
detail += S.tatters(scn, (0, -0.44, 0.62), 1.10, M["cloth"], count=7, drop=0.30, seed=9)

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.16, chest_r=0.66, lean=12)
tors.append(P.add_box(scn, "obelt", (0, -0.04, 0.16), (1.16, 0.72, 0.18), M["leath"]))

# ---- bone jewellery: a collar of tusks, staggered so it is not a printed row ----
tors.append(P.add_cyl(scn, "ocollar", (0, -0.24, 0.94), 0.46, 0.11, M["leath"], verts=10))
for i, dx in enumerate((-0.34, -0.12, 0.10, 0.32)):
    tors.append(P.add_cone(scn, "otoothcharm", (dx, -0.44, 0.74 - (i % 2) * 0.09),
                           0.055, 0.015, 0.30, M["bone"],
                           rot=(math.radians(178), 0, 0), verts=5))

# ---- the horned wooden mask, which replaces the face entirely ----
tors.append(P.add_cyl(scn, "oneck", (0, 0, 1.06), 0.20, 0.22, M["hide"], verts=8))
tors.append(P.add_sphere(scn, "oheadback", (0, 0.06, 1.28), 0.40, M["hide"],
                         scale=(1.0, 0.96, 1.0), segs=10, rings=7))
tors.append(P.add_prism(scn, "omask",
                        [(-0.36, -0.44), (0.36, -0.44), (0.42, 0.10), (0.30, 0.44),
                         (-0.30, 0.44), (-0.42, 0.10)], 0.14, M["wood"],
                        loc=(0, -0.36, 1.30)))
tors_det = []
tors_det.append(P.add_box(scn, "omaskband", (0, -0.46, 1.34), (0.74, 0.06, 0.13), M["paint"]))
for s in (-1, 1):
    tors_det.append(P.add_box(scn, "omaskeye", (s * 0.17, -0.46, 1.42), (0.15, 0.05, 0.11), M["dark"]))
    tors.append(P.add_cone(scn, "omaskhorn", (s * 0.34, -0.24, 1.68), 0.09, 0.02, 0.52, M["tusk"],
                           rot=(0, math.radians(s * 40), 0), verts=6))
tors_det.append(P.add_box(scn, "omaskmouth", (0, -0.46, 1.10), (0.34, 0.05, 0.09), M["dark"]))

# ---- arms ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 0.88, -0.10, 0.86), 0.37, M["hide"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "oupperL", (-0.92, -0.24, 0.50), 0.24, 0.64, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeL", (-0.84, -0.56, 0.06), 0.215, 0.58, M["hide"], verts=8,
                      rot=(math.radians(26), 0, 0)))
tors.append(P.add_sphere(scn, "ofistL", (-0.80, -0.70, -0.20), 0.22, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (0.92, -0.22, 0.82), 0.24, 0.60, M["hide"], verts=8,
                      rot=(0, math.radians(28), 0)))
tors.append(P.add_cyl(scn, "oforeR", (1.08, -0.42, 1.14), 0.215, 0.56, M["hide"], verts=8,
                      rot=(math.radians(-22), math.radians(20), 0)))
tors.append(P.add_sphere(scn, "ofistR", (1.16, -0.54, 1.40), 0.22, M["hide"]))

P.parent_all(tors_root, tors + tors_det)

# ---- feathered fetish staff ----
st_root = P.make_root(scn, "staff_root", rot=(0, -12, 0), loc=(-0.90, -0.76, 1.22))
staff = [P.add_cyl(scn, "oshaft", (0, 0, 0), 0.068, 2.90, M["wood"], verts=6)]
for z in (-1.06, -0.24, 0.56):
    staff.append(P.add_cyl(scn, "olash", (0, 0, z), 0.10, 0.10, M["leath"], verts=6))
# a fan of feathers below the charm: the irregular top edge is the read
for i, s in enumerate((-2, -1, 0, 1, 2)):
    staff.append(P.add_cone(scn, "ofeather", (s * 0.11, 0.06, 1.28 + (2 - abs(s)) * 0.08),
                            0.05, 0.012, 0.46 + (2 - abs(s)) * 0.10,
                            M["cloth"] if i % 2 else M["tusk"],
                            rot=(math.radians(18), 0, math.radians(s * 15)), verts=5))
staff.append(P.add_cyl(scn, "ocradle", (0, 0, 1.44), 0.15, 0.12, M["iron"], verts=8))
glow = [P.add_sphere(scn, "ocharm", (0, -0.04, 1.64), 0.135, M["ember"], segs=8, rings=5),
        P.add_sphere(scn, "ocharmhalo", (0, -0.06, 1.82), 0.075, M["ember_d"], segs=8, rings=5)]
P.parent_all(st_root, staff + glow)

O.finish(scn, px, "orc_shaman", figure, detail, noline, roots=[tors_root, st_root],
         skip_extra=tuple(o.name for o in glow + tors_det), role="shaman", body_roots=[tors_root])
