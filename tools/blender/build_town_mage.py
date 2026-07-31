"""Town mage -- M15_ASSET_SPECS.md entry 15.

  "a town mage in modest violet robes and a tall pointed hat, plain wooden staff
   topped with a small glowing crystal"

The tall pointed hat is the entry and it is the only cone on a head anywhere in
the game. It also makes him the tallest-reading townsperson while measuring the
same as the rest, which is what the size ruling intends.

MODEST is the operative word against the battle-mage: no runes, no crackle, a
plain shaft and one small crystal. The two are the same silhouette at different
levels of consequence, and that comparison only works if this one stays quiet.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import townsfolk_kit as T
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(T)

scn = P.get_scene()
px = T.start(scn, res=112)
M = T.palette()

figure, detail, noline = [], [], []

HIP = 1.16
figure += T.robe(scn, M, M["violet"], top=1.74, r_base=0.80, r_top=0.42)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.43, 0.37, 0.88, M["violet"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.38, 1.66), (0.56, 0.09, 0.12), M["leath"]))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.50), 0.62, 0.28, 0.40, M["violet"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.45, -0.04, 2.42), 0.21, M["violet"],
                               scale=(1, .95, .8)))

hd, hd_det = T.head(scn, M, (0, -0.04, 2.84), r=0.28)
figure += hd
detail += hd_det
# the tall pointed hat: the only cone on a head in the game
# The hat is DARKER than the robe. Built in the same violet it merged with the
# robe below it and the whole figure rendered as one purple triangle from point
# to floor, with no person inside it.
HAT = P.toon_mat("TVIOLETDARK", "#231832", "#38284f", "#523d6e")
figure.append(P.add_cyl(scn, "hatbrim", (0, -0.02, 3.02), 0.42, 0.10, HAT, verts=12))
figure.append(P.add_cone(scn, "hatcone", (0, 0.02, 3.40), 0.32, 0.03, 0.72, HAT, verts=10,
                         rot=(math.radians(-8), 0, 0)))
detail.append(P.add_cyl(scn, "hatband", (0, -0.02, 3.10), 0.33, 0.10, M["leath"], verts=12))

figure += S.limb(scn, (-0.46, -0.12, 2.34), (-0.64, -0.56, 1.86), M["violet"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.46, -0.12, 2.36), (0.52, -0.58, 1.82), M["violet"], 0.13, 0.115,
                 hand_mat=M["skin"])

# a plain staff: no runes, no crackle, one small crystal
st_root = P.make_root(scn, "staff_root", rot=(0, -8, 0), loc=(-0.68, -0.60, 1.96))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.055, 2.70, M["wood"], verts=6),
         P.add_cyl(scn, "lash", (0, 0, 0.60), 0.075, 0.08, M["leath"], verts=6)]
crystal = [P.add_cone(scn, "crystal", (0, -0.02, 1.46), 0.11, 0.0, 0.30, M["crystal"], verts=6),
           P.add_cone(scn, "crystalbase", (0, -0.02, 1.34), 0.11, 0.0, 0.16, M["crystal"], verts=6,
                      rot=(math.radians(180), 0, 0))]
P.parent_all(st_root, staff + crystal)

T.finish(scn, px, "town_mage", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in crystal))
