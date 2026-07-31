"""Bandit Horde skirmisher -- M15_ASSET_SPECS.md entry 29.

  "a lean masked cutthroat in worn brown leathers and a muted red sash, a knife
   in each hand"

The third twin-blade skirmisher in the roster, after the undead shadow reaver and
the goblin skulker, so the pose is the whole risk. The reaver holds his blades
out WIDE, the skulker holds his LOW and forward, and this one holds one high in a
reverse grip and one low. Same weapons, three silhouettes.

His sash is the family's one saturated element and it sits at the waist, which
splits his brown column in half. Without it a lean figure in worn brown reads as
a single vertical smear.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import bandit_kit as B
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(B)

scn = P.get_scene()
px = B.start(scn, res=112)
M = B.palette()

figure, detail, noline = [], [], []

HIP = 1.14
figure += B.lean_legs(scn, M, HIP, spread=0.32)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.72, 0.48, 0.28), M["leath"], bevel=0.05))

tors_root, tors = B.torso(scn, M, HIP + 0.14, chest_r=0.40, lean=16)
tors.append(P.add_box(scn, "bjerkin", (0, -0.12, 0.48), (0.82, 0.40, 0.64), M["leath"], bevel=0.05))
tors += B.patches(scn, M, (0.0, -0.34, 0.52), count=2, seed=5)
# the sash: the family's one saturated element, splitting the brown column
tors.append(P.add_box(scn, "bsash", (0, -0.06, 0.14), (0.86, 0.50, 0.19), M["red"]))
tors.append(P.add_box(scn, "bsashtail", (0.34, -0.30, -0.06), (0.15, 0.08, 0.34), M["red"]))

hd_fig, hd_det = B.head(scn, M, (0, -0.04, 1.02), r=0.29, cover="mask", hood=True)
tors += hd_fig

# ---- one knife high in a reverse grip, one low: the pose that separates him
# from the two other twin-blade skirmishers in the roster.
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.50, -0.08, 0.66), 0.21, M["leath"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "bupperL", (-0.56, -0.18, 0.78), 0.145, 0.46, M["coat"], verts=8,
                      rot=(0, math.radians(-28), 0)))
tors.append(P.add_cyl(scn, "bforeL", (-0.70, -0.34, 1.06), 0.13, 0.44, M["skin"], verts=8,
                      rot=(math.radians(-12), math.radians(-18), 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.76, -0.44, 1.28), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "bupperR", (0.56, -0.22, 0.40), 0.145, 0.46, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeR", (0.60, -0.48, 0.06), 0.13, 0.44, M["skin"], verts=8,
                      rot=(math.radians(34), math.radians(12), 0)))
tors.append(P.add_sphere(scn, "bfistR", (0.62, -0.60, -0.16), 0.15, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- two knives. Short and straight, and pale steel so they separate from the
# browns by value rather than relying on the outline alone.
knife = [(-0.045, 0.0), (0.045, 0.0), (0.055, 0.30), (0.0, 0.40), (-0.055, 0.30)]
knife_roots = []
for name, rot, loc in (("knifeL_root", (0, 196, 0), (-0.80, -0.48, 2.58)),   # reverse grip, blade down
                       ("knifeR_root", (0, 58, 0), (0.64, -0.64, 1.14))):
    kr = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(kr, [P.add_prism(scn, "bknife", knife, 0.05, M["steel"]),
                      P.add_box(scn, "bknifegrip", (0, 0, -0.11), (0.065, 0.065, 0.20), M["rag"]),
                      P.add_box(scn, "bknifeguard", (0, 0, 0.02), (0.16, 0.075, 0.05), M["iron"])])
    knife_roots.append(kr)

B.finish(scn, px, "bandit_skirmisher", figure, detail, noline,
         roots=[tors_root] + knife_roots, skip_extra=tuple(o.name for o in hd_det),
         role="skirmisher", body_roots=[tors_root])
