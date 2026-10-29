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
# Shoulders named by SIDE and arms AIMED shoulder to elbow to fist, both for the
# attack's solver: it needs to tell the two balls apart, and it reads each joint
# off a segment's ends, which only works when the segments actually meet. Placed
# one cylinder at a time, they did not.
for s, side in ((-1, "L"), (1, "R")):
    tors.append(P.add_sphere(scn, "bshoulder" + side, (s * 0.52, -0.08, 0.66), 0.22, M["leath"],
                             scale=(1, .95, .88)))
for side, shoulder, elbow, fist in (("L", (-0.56, -0.16, 0.72), (-0.56, -0.30, 0.30), (-0.20, -0.72, 0.28)),
                                    ("R", (0.56, -0.16, 0.72), (0.54, -0.30, 0.32), (0.26, -0.74, 0.36))):
    tors.append(S.aimed_cyl(scn, "bupper" + side, shoulder, elbow, 0.15, M["coat"], verts=8))
    tors.append(S.aimed_cyl(scn, "bfore" + side, elbow, fist, 0.135, M["skin"], verts=8))
    tors.append(P.add_sphere(scn, "bfist" + side, fist, 0.15, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the crossbow, held RIFLE-LIKE: it runs from fist to fist ----
# His fists sit side by side at the same depth (in this file's own coordinates),
# so the tiller lies along x with the front to the left. The RIGHT fist grips the
# NECK of the stock, local y +0.26, so the butt runs on past the hand toward his
# shoulder; gripping its back end at +0.56 left the butt lying on his forearm
# (user, 2026-10-29). The LEFT fist is under the tiller at -0.20, behind the bow:
# at -0.36 it sat on the join of the bow arms, and the flat bow is drawn on a
# diagonal from this camera, so its far arm passed behind a hand kept that close. It used to lie ACROSS the fists, and once enlarged
# each hand landed on a bow arm: "it looks like hes holding it by the side arms
# instead of rifle-like" (user, 2026-10-29). The tiller's front is local -y, so a
# -90 turn about z points it along -x.
# Height: the stock sits IN the fists, not under them. At z 1.60 the fists rode
# 0.27 on top of it, so at the aim his trigger fist sat over his eye and its
# forearm hung across his face whichever way the elbow bent (2026-10-29).
CB_ROT, CB_LOC = (0, 0, -90), (0.0, -0.66, 1.83)
cb_root = P.make_root(scn, "bow_root", rot=CB_ROT, loc=CB_LOC)
# No flat steel `blath` any more: the swept limbs below ARE the bow. The bar was
# left behind when they replaced it, sitting at x 0.51 to 1.61, wholly off to one
# side of the crossbow, and it read as a staff (user, 2026-10-29).
# Sized up 2026-10-29: at 0.86 long and 1.12 across it "turns into a blob when he
# holds it up" (user), because a crossbow shrinks to a stub the moment it points
# away from the camera.
bow = [P.add_box(scn, "btiller", (0, 0, 0), (0.18, 1.10, 0.13), M["wood"], bevel=0.03),
       P.add_box(scn, "bstock", (0, 0.40, -0.07), (0.17, 0.36, 0.24), M["wood"], bevel=0.03)]
# the limbs swept back, built as two aimed segments so the bow is not a flat bar
for s in (-1, 1):
    bow.append(S.aimed_cyl(scn, "blimb", (s * 0.10, -0.42, 0.02), (s * 0.80, -0.28, 0.02),
                           0.055, M["steel"], verts=4))
    bow.append(S.aimed_cyl(scn, "bstring", (s * 0.80, -0.28, 0.02), (0.0, 0.12, 0.02),
                           0.025, M["cloth"], verts=4))
P.parent_all(cb_root, bow)

# ---- the loaded bolt: its OWN root, same placement as the crossbow, so the
# attack can fire it off the tiller rather than it being welded on.
bolt_root = P.make_root(scn, "bolt_root", rot=CB_ROT, loc=CB_LOC)
P.parent_all(bolt_root, [
    P.add_cyl(scn, "bloadedbolt", (0, -0.16, 0.11), 0.035, 0.62, M["wood"], verts=4,
              rot=(math.radians(90), 0, 0)),
    P.add_box(scn, "bloadedfletch", (0, 0.13, 0.11), (0.06, 0.10, 0.11), M["red"])])

B.finish(scn, px, "bandit_caster", figure, detail, noline,
         roots=[tors_root, cb_root, bolt_root], skip_extra=tuple(o.name for o in hd_det),
         role="caster", body_roots=[tors_root])
