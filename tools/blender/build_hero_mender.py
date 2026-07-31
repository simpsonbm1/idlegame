"""Healer -- M15_ASSET_SPECS.md entry 3.

  "a gentle human healer in cream-and-gold hooded robes, wooden staff topped
   with a small glowing golden sun emblem, satchel of bandages at the hip"

The lightest figure in the game. Cream against a field of steel-blue heroes and
green, brown and charcoal enemies means the support unit is the easiest thing to
find on a crowded battle line, which is exactly what a player needs of a healer.

The sun emblem is a disc with spokes, the same construction the cathedral's rose
window uses, because a radiating shape at this size is spokes or it is a blob.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Rare (the Cleric)**, so that tier gets no separate file.
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

figure, detail, noline = [], [], []

figure += H.robe(scn, M, M["cream"], top=1.74, r_base=0.82, r_top=0.42)
detail += S.tatters(scn, (0, -0.42, 0.10), 1.16, M["cream"], count=6, drop=0.16, seed=3)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.44, 0.38, 0.88, M["cream"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.40, 1.66), (0.58, 0.09, 0.13), M["gold"]))
detail.append(P.add_box(scn, "placket", (0, -0.38, 2.06), (0.10, 0.06, 0.68), M["gold"]))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.52), 0.64, 0.28, 0.42, M["cream"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.42), 0.22, M["cream"],
                               scale=(1, .95, .8)))
if TRIM:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.66), 0.42, 0.10, TRIM, verts=10))
if LEGEND:
    for i, r in enumerate((0.46, 0.36, 0.26)):
        noline.append(P.add_cyl(scn, "halo", (0, 0.16, 2.98), r, 0.05, M["holy"], verts=12,
                                rot=(math.radians(90), 0, 0)))
        break

hd, hd_det = H.head(scn, M, (0, -0.06, 2.86), r=0.27, hood=M["cream"])
figure += hd
detail += hd_det

# satchel of bandages at the hip
figure.append(P.add_box(scn, "satchel", (0.46, -0.26, 1.58), (0.40, 0.30, 0.36), M["leath"], bevel=0.04))
detail.append(P.add_box(scn, "satchelflap", (0.46, -0.40, 1.72), (0.42, 0.18, 0.14), M["leath"]))
detail.append(P.add_box(scn, "bandage", (0.46, -0.42, 1.52), (0.30, 0.05, 0.16), M["cream"]))

figure += S.limb(scn, (-0.48, -0.12, 2.34), (-0.66, -0.56, 1.80), M["cream"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.48, -0.12, 2.36), (0.66, -0.58, 2.30), M["cream"], 0.13, 0.115,
                 hand_mat=M["skin"])

st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.70, -0.60, 1.92))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.055, 2.70, M["wood"], verts=6)]
for z in (-0.90, -0.10, 0.70):
    staff.append(P.add_cyl(scn, "lash", (0, 0, z), 0.075, 0.08, M["leath"], verts=6))
sun = [P.add_cyl(scn, "sundisc", (0, -0.02, 1.50), 0.20, 0.07, M["sun"], verts=12,
                 rot=(math.radians(90), 0, 0))]
for i in range(4):
    sun.append(P.add_box(scn, "sunray", (0, -0.05, 1.50), (0.56, 0.05, 0.07), M["sun"],
                         rot=(0, math.radians(-i * 45), 0)))
if TRIM:
    staff.append(P.add_cyl(scn, "sunring", (0, 0.02, 1.50), 0.26, 0.08, TRIM, verts=12,
                           rot=(math.radians(90), 0, 0)))
P.parent_all(st_root, staff + sun)

H.finish(scn, px, "hero_mender", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in sun))
