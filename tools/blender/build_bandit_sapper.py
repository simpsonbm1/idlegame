"""Bandit Horde sapper -- M15_ASSET_SPECS.md entry 32.

  "a bandit torchman gripping a burning torch and an oil flask, coil of fuse rope
   at the belt"

The family's smallest, and the roster's third torch-carrier after the goblin
tunneler's candle and the orc saboteur's brand. That repetition is fine and the
distances are what matter: the goblin's flame sits ON HIS HEAD, the orc holds his
out to one side at arm's length, and this one holds his HIGH above his head with
the oil flask down at his hip. Three positions, three shapes.

He is the only bandit whose face is lit from below by his own torch in concept
but not in fact -- the rig has one key light and adding a second for one sprite
would break the family. The flame is bright enough at the top of the frame that
nothing is lost.
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

HIP = 1.10
figure += B.lean_legs(scn, M, HIP, spread=0.32)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.72, 0.48, 0.28), M["leath"], bevel=0.05))

tors_root, tors = B.torso(scn, M, HIP + 0.14, chest_r=0.40, lean=18)
tors.append(P.add_box(scn, "bjerkin", (0, -0.12, 0.46), (0.80, 0.40, 0.62), M["leath"], bevel=0.05))
tors += B.patches(scn, M, (0.0, -0.33, 0.50), count=3, seed=6)
tors.append(P.add_box(scn, "bbelt", (0, -0.04, 0.10), (0.86, 0.52, 0.14), M["rag"]))

# ---- coil of fuse rope at the belt: a ring of touching segments, because six
# separate blocks on a circle render as six unrelated dots at this size.
R, N = 0.17, 12
pts = [(math.cos(math.radians(i * 360.0 / N)) * R, -0.30,
        math.sin(math.radians(i * 360.0 / N)) * R * 0.86 + 0.02) for i in range(N)]
for i in range(N):
    tors.append(S.aimed_cyl(scn, "bfuse", pts[i], pts[(i + 1) % N], 0.032, M["cloth"], verts=4))

hd_fig, hd_det = B.head(scn, M, (0, -0.04, 1.00), r=0.28, cover="scarf", hood=True)
tors += hd_fig

# ---- torch arm straight up, flask arm down at the hip ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.48, -0.08, 0.64), 0.21, M["leath"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "bupperL", (-0.54, -0.16, 0.86), 0.145, 0.46, M["coat"], verts=8,
                      rot=(0, math.radians(-16), 0)))
tors.append(P.add_cyl(scn, "bforeL", (-0.64, -0.24, 1.28), 0.13, 0.46, M["skin"], verts=8,
                      rot=(0, math.radians(-8), 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.68, -0.28, 1.52), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "bupperR", (0.54, -0.22, 0.38), 0.145, 0.44, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeR", (0.56, -0.46, 0.04), 0.13, 0.44, M["skin"], verts=8,
                      rot=(math.radians(26), 0, 0)))
tors.append(P.add_sphere(scn, "bfistR", (0.58, -0.58, -0.18), 0.15, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the torch, held high above the head ----
tc_root = P.make_root(scn, "torch_root", rot=(0, -14, 0), loc=(-0.72, -0.34, 2.68))
torch = [P.add_cyl(scn, "btorchhaft", (0, 0, 0.06), 0.055, 0.76, M["wood"], verts=6),
         P.add_cyl(scn, "btorchhead", (0, 0, 0.50), 0.115, 0.22, M["rag"], verts=8),
         P.add_box(scn, "btorchband", (0, 0, 0.36), (0.15, 0.13, 0.07), M["iron"])]
fire = S.flame(scn, (0, -0.02, 0.68), M["fire"], M["fire_d"], scale=1.05)
P.parent_all(tc_root, torch + fire)

# ---- the oil flask, hanging from the low hand ----
fl_root = P.make_root(scn, "flask_root", loc=(0.62, -0.66, 1.02))
flask = [P.add_sphere(scn, "bflask", (0, 0, -0.10), 0.155, M["cloth"], scale=(1, 1, 1.10),
                      segs=10, rings=6),
         P.add_cyl(scn, "bflaskneck", (0, 0, 0.08), 0.055, 0.14, M["cloth"], verts=6),
         P.add_cyl(scn, "bflaskcork", (0, 0, 0.17), 0.06, 0.07, M["wood"], verts=6),
         P.add_box(scn, "bflaskrag", (0, -0.06, 0.24), (0.07, 0.06, 0.13), M["red"])]
P.parent_all(fl_root, flask)

B.finish(scn, px, "bandit_sapper", figure, detail, noline,
         roots=[tors_root, tc_root, fl_root],
         skip_extra=tuple(o.name for o in hd_det + fire),
         role="sapper", body_roots=[tors_root])
