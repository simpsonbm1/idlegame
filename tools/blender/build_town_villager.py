"""Villager -- M15_ASSET_SPECS.md entry 9.

  "a cheerful villager in a simple brown tunic and straw hat, carrying a basket
   of vegetables"

The plainest figure in the game, deliberately. He is the baseline the other
seven townsfolk are read against, so he carries exactly one identifying object
and wears nothing but wool.

His straw hat is the widest brim in the roster. A brim makes a hat a silhouette
rather than a hair colour, which is the only way headwear survives at this
size.
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
figure += T.legs(scn, M, HIP, spread=0.33, mat=M["wool"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.76, 0.50, 0.28), M["wool"], bevel=0.05))

tors_root, tors = T.torso(scn, M, HIP + 0.14, chest_r=0.42, lean=4, mat=M["wool"])
tors.append(P.add_box(scn, "tunic", (0, -0.10, 0.44), (0.82, 0.42, 0.66), M["wool"], bevel=0.05))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.10), (0.86, 0.54, 0.13), M["leath"]))

hd, hd_det = T.head(scn, M, (0, -0.04, 1.02), r=0.29)
tors += hd
tors += T.brim_hat(scn, M, (0, -0.02, 1.14), r=0.29)

lh, rh = T.relaxed_arms(scn, M, tors, shoulder_z=0.64, spread=0.48,
                        left_hand=(-0.54, -0.54, -0.06))
P.parent_all(tors_root, tors + hd_det)

# the basket, hooked over the low hand
bk_root = P.make_root(scn, "basket_root", loc=(0.56, -0.60, 0.94))
basket = [P.add_cone(scn, "basket", (0, 0, 0), 0.24, 0.32, 0.34, M["straw"], verts=10),
          P.add_cyl(scn, "basketrim", (0, 0, 0.17), 0.33, 0.06, M["straw"], verts=10),
          P.add_box(scn, "baskethandle", (0, 0, 0.30), (0.30, 0.06, 0.06), M["straw"])]
veg = [P.add_sphere(scn, "veg", (dx, dy, 0.22), 0.10, m, segs=8, rings=6)
       for dx, dy, m in ((-0.11, -0.04, M["green"]), (0.06, 0.05, M["straw"]),
                         (0.12, -0.07, M["green"]))]
P.parent_all(bk_root, basket + veg)

T.finish(scn, px, "town_villager", figure, detail, noline,
         roots=[tors_root, bk_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
