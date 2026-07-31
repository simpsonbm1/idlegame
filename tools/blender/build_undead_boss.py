"""Undead Legion boss -- M15_ASSET_SPECS.md entry 39.

  "BOSS: the Lich Commander, a crowned skeletal sorcerer-king in ancient royal
   vestments over rusted armor, radiating teal-violet ghost-light, ornate staff
   with a caged swirling soulflame"

A boss has to beat its own family on SILHOUETTE before it beats them on detail,
because at sprite size detail is the first thing to go. His comes from three
things none of the other five have: a high standing collar that frames the skull,
a cape that widens him at the shoulders, and a crown that breaks the top edge.

The spec asks for a boss to fill more of the cell than a common enemy. That is a
bigger CELL and a taller figure, never a smaller ortho -- a smaller ortho would
make him larger on screen than the backdrop and every other sprite agree he is.

Both the teal and the violet glow appear on him. Elsewhere in the family they are
kept apart (the sapper's lantern is green, the reaver's mist violet, everyone
else teal) so that the commander carrying all of it reads as rank.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import undead_kit as U
import pixelrig as P
importlib.reload(P)
importlib.reload(U)

scn = P.get_scene()
px = U.start(scn, res=144)
M = U.palette()

figure, detail, noline = [], [], []

# ---- royal vestments to the floor, over a rusted plate skirt ----
figure.append(P.add_cone(scn, "robe", (0, 0, 1.02), 1.00, 0.50, 2.04, M["robe"], verts=12))
figure.append(P.add_cyl(scn, "hembraid", (0, 0, 0.07), 1.03, 0.12, M["gold"], verts=12))
detail += U.tatters(scn, (0, -0.52, 0.14), 1.44, M["robe_d"],
                        count=7, drop=0.26, seed=2)
figure.append(P.add_box(scn, "fauld", (0, 0, 1.98), (1.06, 0.68, 0.44), M["iron"], bevel=0.06))
figure.append(P.add_box(scn, "belt", (0, -0.04, 2.24), (1.10, 0.72, 0.18), M["gold"]))
detail.append(P.add_box(scn, "buckle", (0, -0.42, 2.24), (0.19, 0.06, 0.17), M["teal_d"]))

# ---- cuirass, with the royal placket running down it ----
figure += P.add_ridged(scn, "cuirass", (0, 0, 2.74), (1.06, 0.58, 0.82), M["iron"], splay=13, bevel=0.07)
detail.append(P.add_box(scn, "placket", (0, -0.38, 2.72), (0.13, 0.07, 0.70), M["gold"]))

# ---- the cape: a shell BEHIND the shoulders, standing proud so it outlines ----
figure.append(P.add_cone(scn, "cape", (0, 0.32, 2.34), 0.94, 0.52, 1.72, M["robe_d"], verts=10))

# ---- pauldrons, and the standing collar that frames the skull ----
for s, dz in ((-1, 0.0), (1, 0.02)):
    figure.append(P.add_sphere(scn, "pauldron", (s * 0.80, -0.06, 3.06 + dz), 0.36, M["iron"], scale=(1, .95, .8)))
    figure.append(P.add_cone(scn, "spaulspike", (s * 0.86, -0.06, 3.36 + dz), 0.09, 0.02, 0.34, M["bone"],
                             rot=(0, math.radians(s * 18), 0), verts=6))
figure.append(P.add_cone(scn, "collar", (0, 0.16, 3.30), 0.30, 0.74, 0.70, M["robe_d"], verts=10))

# ---- skull and crown ----
fig_s, det_s, nol_s = U.skull(scn, M, (0, -0.10, 3.52), radius=0.27, eye=M["violet"])
figure += fig_s
detail += det_s
noline += nol_s
figure.append(P.add_cyl(scn, "crownband", (0, -0.08, 3.76), 0.29, 0.13, M["gold"], verts=10))
for i in range(5):
    a = math.radians(-90 + (i - 2) * 34)          # spread across the front of the band
    figure.append(P.add_cone(scn, "crownpoint",
                             (math.cos(a) * 0.26, math.sin(a) * 0.26 - 0.08, 3.94),
                             0.055, 0.0, 0.30, M["gold"], verts=5))
noline.append(P.add_sphere(scn, "crownjewel", (0, -0.35, 3.86), 0.075, M["teal"], segs=8, rings=5))

# ---- arms: bone, one on the staff, one held out commanding ----
figure += U.bone_arm(scn, M, (-0.76, -0.16, 2.94), (-0.86, -0.60, 2.16), upper_r=0.09, fore_r=0.078)
figure += U.bone_arm(scn, M, (0.76, -0.16, 2.96), (0.92, -0.66, 2.72), upper_r=0.09, fore_r=0.078)
noline += U.ghostflame(scn, M, (0.94, -0.70, 2.90), scale=0.85, hot=M["violet"], cool=M["teal_d"])

# ---- ornate staff: a caged soulflame, which is the one thing on him that has
# to survive being four pixels wide. A cage of thin bars around a bright core
# reads at that size; a detailed reliquary does not.
st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.92, -0.64, 2.30))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.062, 3.30, M["iron"], verts=6)]
for z in (-1.10, -0.30, 0.50):
    staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.09, 0.10, M["gold"], verts=6))
staff.append(P.add_cyl(scn, "cagebase", (0, 0, 1.56), 0.20, 0.10, M["gold"], verts=8))
staff.append(P.add_cyl(scn, "cagetop", (0, 0, 2.06), 0.16, 0.09, M["gold"], verts=8))
for i in range(4):
    a = math.radians(45 + i * 90)
    staff.append(P.add_cyl(scn, "cagebar", (math.cos(a) * 0.17, math.sin(a) * 0.17, 1.81),
                           0.022, 0.52, M["gold"], verts=4))
for s in (-1, 1):
    staff.append(P.add_cone(scn, "finial", (s * 0.14, 0, 2.24), 0.05, 0.0, 0.30, M["bone"],
                            rot=(0, math.radians(s * 26), 0), verts=6))
soul = [P.add_sphere(scn, "soulcore", (0, 0, 1.81), 0.145, M["teal"], segs=10, rings=7),
        P.add_sphere(scn, "soulwisp", (0.06, -0.04, 1.96), 0.065, M["violet"], segs=8, rings=5),
        P.add_sphere(scn, "soulwisp", (-0.05, -0.04, 1.68), 0.05, M["teal_d"], segs=8, rings=5)]
P.parent_all(st_root, staff + soul)

U.finish(scn, px, "undead_boss", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in soul), role="boss")
