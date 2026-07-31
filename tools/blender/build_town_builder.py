"""Builder -- M15_ASSET_SPECS.md entry 13.

  "a builder in a work smock and cloth cap, wooden mallet in hand, coil of rope
   over one shoulder"

The coil of rope is the entry, and it is the only closed loop on a townsperson.
Built as segments that touch, the same construction the goblin slinger's sling
and the bandit torchman's fuse need, because separated blocks on a circle render
as unrelated dots.

His mallet is wood where the blacksmith's hammer is iron, which is what keeps two
tool-carrying tradesmen apart at a glance.
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
figure += T.legs(scn, M, HIP, spread=0.34, mat=M["wool"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.80, 0.52, 0.28), M["wool"], bevel=0.05))

tors_root, tors = T.torso(scn, M, HIP + 0.14, chest_r=0.44, lean=6, mat=M["linen"])
tors.append(P.add_box(scn, "smock", (0, -0.14, 0.44), (0.86, 0.40, 0.72), M["linen"], bevel=0.05))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.08), (0.90, 0.56, 0.14), M["leath"]))

hd, hd_det = T.head(scn, M, (0, -0.04, 1.02), r=0.29)
tors += hd
# cloth cap: a soft dome with a short peak, against the villager's wide brim
tors.append(P.add_sphere(scn, "cap", (0, -0.02, 1.16), 0.32, M["wool"],
                         scale=(1.0, 1.0, 0.62), segs=12, rings=6))
tors.append(P.add_box(scn, "cappeak", (0, -0.30, 1.10), (0.44, 0.26, 0.07), M["wool"]))

# the coil of rope over the shoulder: a closed loop of touching segments
R, N = 0.30, 14
pts = [(math.cos(math.radians(i * 360.0 / N)) * R * 0.72 - 0.40,
        -0.10,
        math.sin(math.radians(i * 360.0 / N)) * R + 0.62) for i in range(N)]
for i in range(N):
    tors.append(S.aimed_cyl(scn, "rope", pts[i], pts[(i + 1) % N], 0.045, M["straw"], verts=4))

lh, rh = T.relaxed_arms(scn, M, tors, shoulder_z=0.66, spread=0.50, sleeve=M["linen"],
                        right_hand=(0.56, -0.58, -0.10))
P.parent_all(tors_root, tors + hd_det)

# wooden mallet in the low hand
ml_root = P.make_root(scn, "mallet_root", rot=(0, -12, 0), loc=(0.58, -0.62, 1.06))
mallet = [P.add_cyl(scn, "mallethaft", (0, 0, -0.24), 0.055, 0.72, M["wood"], verts=6),
          P.add_cyl(scn, "mallethead", (0, 0, 0.22), 0.19, 0.42, M["wood"], verts=8,
                    rot=(0, math.radians(90), 0)),
          P.add_cyl(scn, "malletband", (-0.16, 0, 0.22), 0.20, 0.06, M["iron"], verts=8,
                    rot=(0, math.radians(90), 0)),
          P.add_cyl(scn, "malletbandB", (0.16, 0, 0.22), 0.20, 0.06, M["iron"], verts=8,
                    rot=(0, math.radians(90), 0))]
P.parent_all(ml_root, mallet)

T.finish(scn, px, "town_builder", figure, detail, noline,
         roots=[tors_root, ml_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
