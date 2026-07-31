"""Orc Warband sapper -- M15_ASSET_SPECS.md entry 26.

  "an orc saboteur carrying a wooden powder keg under one arm and a lit torch in
   the other hand, bandolier of crude bombs across the chest"

The keg is the read. It is a big pale cylinder held against a dark olive body,
and no other figure in the roster carries a large object OFF TO ONE SIDE -- every
other two-handed thing is centred on the body. That asymmetry identifies him
before any detail does.

Sappers across the five factions all carry a tool or a charge rather than a
weapon, and this is the family's version of the goblin tunneler's pickaxe and the
undead grave digger's shovel.
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
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.14, 0.68, 0.40), M["leath"], bevel=0.06))
figure.append(P.add_prism(scn, "oapron", [(-0.34, 0.28), (0.34, 0.28), (0.26, -0.62), (-0.26, -0.62)],
                          0.11, M["leath"], loc=(0.02, -0.38, 1.30)))

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.16, chest_r=0.68, lean=14)
tors.append(P.add_box(scn, "obelt", (0, -0.04, 0.16), (1.20, 0.74, 0.18), M["leath"]))

# ---- bandolier of crude bombs. The bombs are SPHERES ON A STRAP rather than
# painted marks, so each casts its own edge and the strap reads as loaded.
tors.append(P.add_box(scn, "obandolier", (0, -0.42, 0.62), (1.30, 0.12, 0.17), M["leath"],
                      rot=(0, math.radians(32), 0)))
for i, (dx, dz) in enumerate(((-0.44, 0.36), (-0.18, 0.52), (0.10, 0.68), (0.36, 0.84))):
    tors.append(P.add_sphere(scn, "obomb", (dx, -0.54, dz), 0.135, M["iron"], segs=8, rings=6))
    tors.append(P.add_cyl(scn, "ofuse", (dx + 0.04, -0.58, dz + 0.17), 0.022, 0.16, M["cloth"],
                          verts=4, rot=(0, math.radians(22), 0)))

hd_fig, hd_det = O.head(scn, M, (0, -0.04, 1.20), r=0.46)
tors += hd_fig
tors.append(P.add_sphere(scn, "ocap", (0, -0.04, 1.42), 0.47, M["leath"],
                         scale=(1.05, 1.0, 0.56), segs=10, rings=6))

# ---- arms: one clamped round the keg, one out with the torch ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 0.90, -0.10, 0.86), 0.38, M["hide"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "oupperL", (-0.96, -0.20, 0.52), 0.25, 0.62, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeL", (-1.06, -0.44, 0.16), 0.22, 0.58, M["hide"], verts=8,
                      rot=(math.radians(18), math.radians(-16), 0)))
tors.append(P.add_sphere(scn, "ofistL", (-1.12, -0.60, -0.08), 0.23, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (0.96, -0.24, 0.94), 0.25, 0.60, M["hide"], verts=8,
                      rot=(0, math.radians(30), 0)))
tors.append(P.add_cyl(scn, "oforeR", (1.14, -0.44, 1.26), 0.22, 0.56, M["hide"], verts=8,
                      rot=(math.radians(-20), math.radians(22), 0)))
tors.append(P.add_sphere(scn, "ofistR", (1.22, -0.56, 1.52), 0.23, M["hide"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the powder keg, clamped under the left arm ----
kg_root = P.make_root(scn, "keg_root", rot=(-72, 0, 0), loc=(-1.10, -0.58, 1.52))
keg = [P.add_cyl(scn, "okegbody", (0, 0, 0), 0.40, 0.72, M["wood"], verts=10),
       P.add_cyl(scn, "okeglid", (0, 0, 0.38), 0.34, 0.09, M["wood"], verts=10)]
for z in (-0.24, 0.0, 0.24):
    keg.append(P.add_cyl(scn, "okeghoop", (0, 0, z), 0.42, 0.08, M["iron"], verts=10))
keg.append(P.add_cyl(scn, "okegfuse", (0.10, 0, 0.48), 0.03, 0.28, M["cloth"], verts=4,
                     rot=(math.radians(24), 0, 0)))
P.parent_all(kg_root, keg)

# ---- the lit torch ----
tc_root = P.make_root(scn, "torch_root", rot=(0, 24, 0), loc=(1.26, -0.62, 3.02))
torch = [P.add_cyl(scn, "otorchhaft", (0, 0, 0.10), 0.065, 0.84, M["wood"], verts=6),
         P.add_cyl(scn, "otorchhead", (0, 0, 0.58), 0.13, 0.24, M["cloth"], verts=8),
         P.add_box(scn, "otorchband", (0, 0, 0.42), (0.17, 0.15, 0.08), M["iron"])]
fire = S.flame(scn, (0, -0.02, 0.78), M["ember"], M["ember_d"], scale=1.15)
P.parent_all(tc_root, torch + fire)

O.finish(scn, px, "orc_sapper", figure, detail, noline,
         roots=[tors_root, kg_root, tc_root],
         skip_extra=tuple(o.name for o in hd_det + fire), role="sapper", body_roots=[tors_root])
