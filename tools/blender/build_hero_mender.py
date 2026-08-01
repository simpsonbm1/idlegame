"""The mender line -- M15_ASSET_SPECS.md entry 3, plus its rarity variants.

  "a gentle human healer in cream-and-gold hooded robes, wooden staff topped
   with a small glowing golden sun emblem, satchel of bandages at the hip"

The lightest figure in the game. Cream against a field of steel-blue heroes and
green, brown and charcoal enemies means the support unit is the easiest thing to
find on a crowded battle line, which is exactly what a player needs of a healer.

The sun emblem is a disc with spokes, the same construction the cathedral's rose
window uses, because a radiating shape at this size is spokes or it is a blob.

## Four healers, not one healer promoted (USER RULING 2026-08-01)

`DESIGN.md` names them Acolyte, Cleric, Druid and Saint, and they are four
different faiths as much as four ranks. The STAFF TOP is the read here, because
every one of them holds a staff in the same hand at the same angle, so the thing
on the end of it is where the eye goes: a bound wooden crook, a golden sun, a
living branch, a radiant sun in a ring. Then the head, then the robe.

**This hero's own sprite is Rare, the Cleric**, so that tier gets no separate
file and every branch below leaves it exactly as it was.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import hero_kit as H
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(H)

scn = P.get_scene()
px = H.start(scn, res=112)
M = H.palette()
TRIM = H.trim_mat(M)        # None on a common hero: plain and field-worn
GLOW = H.glow_mat(M)        # epic and legendary only
LEGEND = H.is_legendary()

TIER = H.tier()
if TIER == "base":
    TIER = "rare"           # the Cleric IS this builder's own sprite

ROBE = {"common": "cream", "rare": "cream", "epic": "green", "legendary": "cream"}[TIER]
BAND = {"common": None, "rare": "gold", "epic": "leath", "legendary": "brightgold"}[TIER]

figure, detail, noline = [], [], []

# ---------------------------------------------------------------------------
# robe and torso
# ---------------------------------------------------------------------------
figure += H.robe(scn, M, M[ROBE], top=1.74, r_base=0.82, r_top=0.42)
detail += S.tatters(scn, (0, -0.42, 0.10), 1.16, M[ROBE], count=6, drop=0.16, seed=3)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.44, 0.38, 0.88, M[ROBE], verts=12))
if BAND:
    figure.append(P.add_box(scn, "sash", (0, -0.40, 1.66), (0.58, 0.09, 0.13), M[BAND]))
    detail.append(P.add_box(scn, "placket", (0, -0.38, 2.06), (0.10, 0.06, 0.68), M[BAND]))

if TIER == "rare":
    figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.52), 0.64, 0.28, 0.42, M[ROBE], verts=12))
elif TIER == "epic":
    # the Druid wears a hide over the robe, not a churchman's mantle
    figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.50), 0.70, 0.30, 0.46, M["fur"], verts=12))
elif TIER == "legendary":
    figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.52), 0.66, 0.28, 0.44,
                             M["brightgold"], verts=12))
# the Acolyte gets no mantle at all: a novice in an unadorned robe

for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.42), 0.22, M[ROBE],
                               scale=(1, .95, .8)))
if TRIM and TIER == "legendary":
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.66), 0.42, 0.10, TRIM, verts=10))
if LEGEND:
    noline.append(P.add_cyl(scn, "halo", (0, 0.16, 2.98), 0.46, 0.05, M["holy"], verts=12,
                            rot=(math.radians(90), 0, 0)))

# ---------------------------------------------------------------------------
# head. Only the Cleric is hooded; the rest are deliberately not, so that four
# healers standing together are not four cream cones with faces in them.
# ---------------------------------------------------------------------------
HEAD_AT = (0, -0.06, 2.86)
if TIER == "rare":
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27, hood=M[ROBE])
elif TIER == "common":
    # a novice: bare headed, cropped hair, no ornament anywhere on him
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.04, 2.92), 0.29, M["leath"],
                               scale=(1.0, 1.0, 0.86), segs=12, rings=7))
elif TIER == "epic":
    # the Druid: antlers. Nothing else in the roster has them, and they are the
    # widest thing that can sit on a head without touching the shoulders.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.06, 2.90), 0.31, M["charcoal"],
                               scale=(1.0, 1.04, 0.94), segs=12, rings=7))
    for s in (-1, 1):
        figure.append(P.add_cone(scn, "antler", (s * 0.22, 0.04, 3.16), 0.05, 0.02, 0.46,
                                 M["wood"], rot=(0, math.radians(-s * 26), 0), verts=6))
        for i, dz in enumerate((0.10, 0.26)):
            figure.append(P.add_cone(scn, "antlertine",
                                     (s * (0.30 + i * 0.06), 0.04, 3.16 + dz), 0.035, 0.0, 0.24,
                                     M["wood"], rot=(0, math.radians(-s * 62), 0), verts=5))
    detail.append(P.add_box(scn, "druidbeard", (0, -0.30, 2.66), (0.28, 0.18, 0.26), M["charcoal"]))
else:
    # the Saint: a tall mitre. Height is normally not spendable, but this figure
    # is a cone already and the mitre replaces the hood rather than stacking on
    # top of a head that is otherwise unchanged.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_cone(scn, "mitre", (0, -0.02, 3.14), 0.30, 0.06, 0.54,
                             M["cream"], verts=10))
    detail.append(P.add_box(scn, "mitreband", (0, -0.22, 2.96), (0.52, 0.14, 0.10),
                            M["brightgold"]))
figure += hd
detail += hd_det

# satchel of bandages at the hip. The Druid carries pouches of herbs instead.
if TIER == "epic":
    figure.append(P.add_sphere(scn, "herbpouch", (0.48, -0.28, 1.56), 0.22, M["leath"],
                               scale=(1.0, 0.9, 1.1), segs=10, rings=6))
    detail.append(P.add_cone(scn, "herbsprig", (0.48, -0.34, 1.78), 0.10, 0.0, 0.24,
                             M["green"], verts=6))
else:
    figure.append(P.add_box(scn, "satchel", (0.46, -0.26, 1.58), (0.40, 0.30, 0.36),
                            M["leath"], bevel=0.04))
    detail.append(P.add_box(scn, "satchelflap", (0.46, -0.40, 1.72), (0.42, 0.18, 0.14), M["leath"]))
    detail.append(P.add_box(scn, "bandage", (0.46, -0.42, 1.52), (0.30, 0.05, 0.16), M["cream"]))

# ---- arms. The ORDER of these two calls names armL before armR, and
# ---- attack_roster.py drives this hero by armL_*. Do not swap them.
figure += S.limb(scn, (-0.48, -0.12, 2.34), (-0.66, -0.56, 1.80), M[ROBE], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.48, -0.12, 2.36), (0.66, -0.58, 2.30), M[ROBE], 0.13, 0.115,
                 hand_mat=M["skin"])

# ---------------------------------------------------------------------------
# the staff, and the thing on the end of it
# ---------------------------------------------------------------------------
st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.70, -0.60, 1.92))
SHAFT = M["wood"]
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.055, 2.70, SHAFT, verts=6)]
for z in (-0.90, -0.10, 0.70):
    staff.append(P.add_cyl(scn, "lash", (0, 0, z), 0.075, 0.08, M["leath"], verts=6))

sun = []
if TIER == "common":
    # a bound crook: no emblem at all. The novice has not earned one.
    staff.append(P.add_cyl(scn, "crook", (0, 0, 1.40), 0.075, 0.34, SHAFT, verts=6,
                           rot=(math.radians(28), 0, 0)))
    staff.append(P.add_cyl(scn, "crooklash", (0, -0.05, 1.30), 0.10, 0.12, M["leath"], verts=6))
elif TIER == "epic":
    # a living branch: the Druid's staff is still growing
    for s, dz, ang in ((-1, 1.24, 34), (1, 1.40, -28), (-1, 1.58, 22)):
        staff.append(P.add_cyl(scn, "branch", (s * 0.14, 0, dz), 0.032, 0.36, SHAFT, verts=5,
                               rot=(0, math.radians(-s * ang), 0)))
    for s, dz in ((-1, 1.36), (1, 1.54), (-1, 1.70), (1, 1.24)):
        staff.append(P.add_sphere(scn, "leaves", (s * 0.26, 0.0, dz), 0.17, M["green"],
                                  scale=(1.1, 0.8, 0.9), segs=9, rings=6))
else:
    RAY = 0.56 if TIER == "rare" else 0.72
    DISC = M["sun"] if TIER == "rare" else M["holy"]
    sun = [P.add_cyl(scn, "sundisc", (0, -0.02, 1.50), 0.20 if TIER == "rare" else 0.26,
                     0.07, DISC, verts=12, rot=(math.radians(90), 0, 0))]
    for i in range(4):
        sun.append(P.add_box(scn, "sunray", (0, -0.05, 1.50), (RAY, 0.05, 0.07), DISC,
                             rot=(0, math.radians(-i * 45), 0)))
    if TRIM:
        staff.append(P.add_cyl(scn, "sunring", (0, 0.02, 1.50), 0.26 if TIER == "rare" else 0.40,
                               0.08, TRIM, verts=12, rot=(math.radians(90), 0, 0)))
P.parent_all(st_root, staff + sun)

H.finish(scn, px, "hero_mender", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in sun))
