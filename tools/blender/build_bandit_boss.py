"""Bandit Horde boss -- M15_ASSET_SPECS.md entry 33.

  "BOSS: the Bandit King, a swaggering outlaw in a stolen golden crown and fine
   embroidered coat over brigandine, one hand resting on an ornate crossbow, gold
   rings on his fingers"

The hardest boss in the roster, because he is a human being who has to beat five
other human beings on silhouette while wearing roughly what they wear. Three
things do it, none of them the crown:

1. A long embroidered COAT that flares to the ankles. Every other bandit stops at
   the hip, so he is the only one with a continuous vertical mass.
2. A high collar standing behind his head, which frames it the way the Lich
   Commander's does.
3. GOLD. He is the only figure in the faction carrying a saturated bright colour,
   and everything he has stolen is on him at once.

He is also the only bandit whose stance is asymmetric at the hips -- weight on
one leg, crossbow propped under the other hand. Swagger is a pose before it is a
costume.

The crown sits above a scarf, not a bare face. No bandit gets an open face, and
a king is not the one to break that with.
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
px = B.start(scn, res=144)
M = B.palette()

figure, detail, noline = [], [], []

HIP = 1.34
figure += B.lean_legs(scn, M, HIP, spread=0.38)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.92, 0.58, 0.34), M["leath"], bevel=0.05))

# ---- the long coat: the one continuous vertical mass in the faction ----
figure.append(P.add_cone(scn, "bcoat", (0, 0.04, 0.80), 0.78, 0.50, 1.60, M["coat"], verts=12))
figure.append(P.add_cyl(scn, "bcoathem", (0, 0.04, 0.05), 0.80, 0.11, M["gold"], verts=12))
detail += S.tatters(scn, (0, -0.46, 0.30), 0.90, M["red"], count=5, drop=0.22, seed=8)
# embroidery: two gold bands down the front, which is all that survives at size
detail.append(P.add_box(scn, "bembroidery", (0, -0.48, 1.20), (0.11, 0.06, 1.00), M["gold"]))
detail.append(P.add_box(scn, "bembroideryB", (0.26, -0.44, 1.30), (0.07, 0.06, 0.72), M["gold"]))

tors_root, tors = B.torso(scn, M, HIP + 0.20, chest_r=0.50, lean=6)
tors.append(P.add_box(scn, "bbrig", (0, -0.16, 0.52), (1.00, 0.44, 0.74), M["leath"], bevel=0.05))
for i in range(3):
    for s in (-1, 1):
        tors.append(P.add_box(scn, "bstud", (s * 0.22, -0.38, 0.30 + i * 0.22),
                              (0.12, 0.06, 0.10), M["gold"]))
tors.append(P.add_box(scn, "bbelt", (0, -0.06, 0.14), (1.04, 0.60, 0.17), M["red"]))
detail.append(P.add_box(scn, "bbuckle", (0, -0.44, 1.68), (0.20, 0.07, 0.17), M["gold"]))

# ---- the high collar, framing the head ----
tors.append(P.add_cone(scn, "bcollar", (0, 0.16, 0.94), 0.30, 0.66, 0.56, M["coat"], verts=10))

hd_fig, hd_det = B.head(scn, M, (0, -0.06, 1.16), r=0.31, cover="scarf", hood=False)
tors += hd_fig

# ---- the stolen crown ----
tors.append(P.add_cyl(scn, "bcrownband", (0, -0.06, 1.44), 0.33, 0.14, M["gold"], verts=10))
for i in range(5):
    a = math.radians(-90 + (i - 2) * 34)
    tors.append(P.add_cone(scn, "bcrownpoint",
                           (math.cos(a) * 0.30, math.sin(a) * 0.30 - 0.06, 1.62),
                           0.06, 0.0, 0.28, M["gold"], verts=5))
detail.append(P.add_box(scn, "bcrownjewel", (0, -0.38, 1.44), (0.10, 0.05, 0.10), M["red"]))

# ---- shoulders, one hand on the crossbow, one thumb hooked in the belt ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.62, -0.08, 0.72), 0.26, M["coat"],
                             scale=(1, .95, .88)))
    tors.append(P.add_box(scn, "bepaulette", (s * 0.66, -0.12, 0.84), (0.34, 0.30, 0.10), M["gold"]))
tors.append(P.add_cyl(scn, "bupperL", (-0.66, -0.22, 0.42), 0.175, 0.50, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeL", (-0.68, -0.48, 0.06), 0.155, 0.48, M["coat"], verts=8,
                      rot=(math.radians(24), 0, 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.70, -0.62, -0.18), 0.17, M["skin"]))
for i, dz in enumerate((-0.06, 0.0, 0.06)):
    tors.append(P.add_box(scn, "bring", (-0.72 - i * 0.01, -0.72, -0.18 + dz),
                          (0.09, 0.05, 0.05), M["gold"]))
tors.append(P.add_cyl(scn, "bupperR", (0.66, -0.20, 0.44), 0.175, 0.48, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeR", (0.60, -0.42, 0.16), 0.155, 0.46, M["coat"], verts=8,
                      rot=(math.radians(38), 0, math.radians(10))))
tors.append(P.add_sphere(scn, "bfistR", (0.54, -0.54, -0.06), 0.17, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the ornate crossbow, propped upright under his right hand ----
cb_root = P.make_root(scn, "bow_root", rot=(0, 8, 0), loc=(0.60, -0.62, 1.16))
bow = [P.add_box(scn, "btiller", (0, 0, 0.02), (0.15, 0.16, 1.06), M["wood"], bevel=0.03),
       P.add_box(scn, "bstock", (0, 0.02, -0.50), (0.17, 0.20, 0.30), M["wood"], bevel=0.03),
       P.add_cyl(scn, "btillergold", (0, -0.05, 0.20), 0.10, 0.10, M["gold"], verts=8,
                 rot=(math.radians(90), 0, 0))]
for s in (-1, 1):
    bow.append(S.aimed_cyl(scn, "blimb", (0, -0.06, 0.50), (s * 0.50, -0.02, 0.62),
                           0.042, M["steel"], verts=4))
    bow.append(S.aimed_cyl(scn, "bstring", (s * 0.50, -0.02, 0.62), (0, 0.06, 0.40),
                           0.020, M["cloth"], verts=4))
P.parent_all(cb_root, bow)

B.finish(scn, px, "bandit_boss", figure, detail, noline,
         roots=[tors_root, cb_root], skip_extra=tuple(o.name for o in hd_det),
         role="boss", body_roots=[tors_root])
