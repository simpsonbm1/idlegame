"""Bandit Horde brute -- M15_ASSET_SPECS.md entry 28.

  "a burly bandit enforcer in patched brigandine, scarf over the lower face,
   gripping a heavy spiked club"

The family's heavy, and the one who has to establish that these are PEOPLE. He
is built on the same human frame as the player's knight and separated from him
by three things: the scarf across his face, a palette of worn browns with one
muted red, and gear that is patched rather than fitted.

His club is close kin to the goblin brute's, which is deliberate. Both factions
scavenge, and a bandit enforcer carrying a proper sword would read as a soldier.
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

HIP = 1.16
figure += B.lean_legs(scn, M, HIP, spread=0.38)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.86, 0.54, 0.32), M["leath"], bevel=0.05))

tors_root, tors = B.torso(scn, M, HIP + 0.14, chest_r=0.50, lean=10)
# brigandine: a slab of leather studded with plates, so the studs are what read
tors.append(P.add_box(scn, "bbrig", (0, -0.14, 0.50), (1.02, 0.44, 0.72), M["leath"], bevel=0.05))
for i in range(3):
    for s in (-1, 1):
        tors.append(P.add_box(scn, "bstud", (s * 0.22, -0.36, 0.28 + i * 0.22),
                              (0.13, 0.06, 0.11), M["steel"]))
tors += B.patches(scn, M, (0.0, -0.38, 0.56), count=3, seed=2)
tors.append(P.add_box(scn, "bbelt", (0, -0.04, 0.14), (1.00, 0.58, 0.15), M["rag"]))
tors.append(P.add_box(scn, "bsash", (0, -0.34, 0.34), (1.06, 0.10, 0.16), M["red"],
                      rot=(0, math.radians(26), 0)))

hd_fig, hd_det = B.head(scn, M, (0, -0.04, 1.06), r=0.31, cover="scarf", hood=False)
tors += hd_fig
# a wrapped headband instead of a hood, so the family's heavy is not another hood
tors.append(P.add_box(scn, "bband", (0, -0.10, 1.30), (0.66, 0.60, 0.13), M["red"]))

# ---- heavy shoulders and both fists forward on the club ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.62, -0.08, 0.68), 0.26, M["leath"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "bupperL", (-0.66, -0.22, 0.36), 0.18, 0.52, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeL", (-0.60, -0.50, 0.02), 0.16, 0.46, M["skin"], verts=8,
                      rot=(math.radians(26), 0, 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.56, -0.62, -0.20), 0.17, M["skin"]))
tors.append(P.add_cyl(scn, "bupperR", (0.66, -0.22, 0.38), 0.18, 0.50, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeR", (0.48, -0.54, 0.10), 0.16, 0.50, M["skin"], verts=8,
                      rot=(math.radians(34), 0, math.radians(20))))
tors.append(P.add_sphere(scn, "bfistR", (0.30, -0.66, -0.06), 0.17, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- heavy spiked club, hafted low across the body ----
club = [(-0.09, -0.18), (0.09, -0.18), (0.09, 0.62), (0.17, 0.70), (0.17, 1.18),
        (0.0, 1.30), (-0.17, 1.18), (-0.17, 0.70), (-0.09, 0.62)]
cl_root = P.make_root(scn, "club_root", rot=(0, -120, 0), loc=(-0.06, -0.72, 1.06))
clubparts = [P.add_prism(scn, "bclub", club, 0.17, M["wood"]),
             P.add_box(scn, "bclubgrip", (0, 0, -0.10), (0.12, 0.19, 0.26), M["rag"])]
for z in (0.80, 1.02, 1.20):
    for s in (-1, 1):
        clubparts.append(P.add_cone(scn, "bspike", (s * 0.17, 0, z), 0.05, 0.0, 0.20, M["steel"],
                                    rot=(0, math.radians(s * 90), 0), verts=5))
P.parent_all(cl_root, clubparts)

B.finish(scn, px, "bandit_brute", figure, detail, noline,
         roots=[tors_root, cl_root], skip_extra=tuple(o.name for o in hd_det),
         role="brute", body_roots=[tors_root])
