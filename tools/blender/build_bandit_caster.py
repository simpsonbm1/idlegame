"""Bandit Horde caster -- M15_ASSET_SPECS.md entry 30.

  "a bandit marksman in a dark hood holding a heavy loaded crossbow at the ready,
   quiver of bolts at the hip"

The roster's second caster with no magic, after the goblin slinger, and the only
one holding a MACHINE. A crossbow is a wide horizontal bar across a vertical
figure, which is a silhouette nothing else in the game has -- every other weapon
runs along the body or above it.

He holds it level and forward at chest height rather than aimed off to one side,
because the crossed shape only reads when the bow limbs are square to the camera.
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
figure += B.lean_legs(scn, M, HIP, spread=0.34)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.76, 0.50, 0.30), M["leath"], bevel=0.05))

# ---- quiver of bolts at the hip, fletchings showing ----
figure.append(P.add_cyl(scn, "bquiver", (0.42, -0.06, 1.10), 0.15, 0.52, M["leath"], verts=8,
                        rot=(math.radians(12), 0, math.radians(14))))
for i, dx in enumerate((-0.05, 0.0, 0.05)):
    detail.append(P.add_cyl(scn, "bbolt", (0.46 + dx, -0.10, 1.44), 0.028, 0.26, M["wood"],
                            verts=4, rot=(0, math.radians(14), 0)))
    detail.append(P.add_box(scn, "bfletch", (0.46 + dx, -0.12, 1.56), (0.05, 0.04, 0.10), M["red"]))

tors_root, tors = B.torso(scn, M, HIP + 0.14, chest_r=0.42, lean=10)
tors.append(P.add_box(scn, "bjerkin", (0, -0.12, 0.48), (0.86, 0.42, 0.66), M["leath"], bevel=0.05))
tors += B.patches(scn, M, (0.0, -0.35, 0.52), count=2, seed=3)
tors.append(P.add_box(scn, "bbelt", (0, -0.04, 0.12), (0.90, 0.54, 0.14), M["rag"]))

hd_fig, hd_det = B.head(scn, M, (0, -0.04, 1.04), r=0.29, cover="scarf", hood=True)
tors += hd_fig

# ---- both arms forward and level, one on the tiller, one under the stock ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.52, -0.08, 0.66), 0.22, M["leath"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "bupperL", (-0.56, -0.24, 0.52), 0.15, 0.44, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeL", (-0.52, -0.54, 0.34), 0.135, 0.46, M["skin"], verts=8,
                      rot=(math.radians(62), 0, 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.50, -0.72, 0.28), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "bupperR", (0.56, -0.24, 0.54), 0.15, 0.42, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeR", (0.42, -0.56, 0.40), 0.135, 0.46, M["skin"], verts=8,
                      rot=(math.radians(58), 0, math.radians(18))))
tors.append(P.add_sphere(scn, "bfistR", (0.26, -0.74, 0.36), 0.15, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the crossbow: a wide bar across a vertical figure ----
cb_root = P.make_root(scn, "bow_root", rot=(0, 0, -6), loc=(-0.16, -0.82, 1.62))
bow = [P.add_box(scn, "btiller", (0, 0, 0), (0.16, 0.86, 0.12), M["wood"], bevel=0.03),
       P.add_box(scn, "bstock", (0, 0.28, -0.06), (0.15, 0.30, 0.20), M["wood"], bevel=0.03),
       P.add_box(scn, "blath", (1.06, -0.22, 0.02), (1.10, 0.13, 0.09), M["steel"], bevel=0.02)]
# the limbs swept back, built as two aimed segments so the bow is not a flat bar
for s in (-1, 1):
    bow.append(S.aimed_cyl(scn, "blimb", (s * 0.10, -0.24, 0.02), (s * 0.56, -0.16, 0.02),
                           0.045, M["steel"], verts=4))
    bow.append(S.aimed_cyl(scn, "bstring", (s * 0.56, -0.16, 0.02), (0.0, 0.14, 0.02),
                           0.022, M["cloth"], verts=4))
bow.append(P.add_cyl(scn, "bloadedbolt", (0, -0.10, 0.10), 0.03, 0.52, M["wood"], verts=4,
                     rot=(math.radians(90), 0, 0)))
bow.append(P.add_box(scn, "bloadedfletch", (0, 0.14, 0.10), (0.05, 0.09, 0.10), M["red"]))
P.parent_all(cb_root, bow)

B.finish(scn, px, "bandit_caster", figure, detail, noline,
         roots=[tors_root, cb_root], skip_extra=tuple(o.name for o in hd_det),
         role="caster", body_roots=[tors_root])
