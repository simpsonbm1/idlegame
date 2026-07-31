"""Undead Legion shaman -- M15_ASSET_SPECS.md entry 37.

  "a bone priest in regalia of carved bones over tattered gray vestments, staff
   of stacked vertebrae topped with a teal ghost-flame"

He and the necromancer (entry 36) are the family's two robed casters, so the risk
is that they read as the same figure in two colours. Three things separate them:
his vestments are GREY where the necromancer's are violet, his bone is worn on
the OUTSIDE as regalia rather than hidden under a hood, and his staff is a stack
of discs where the necromancer's is a smooth shaft. Silhouette, palette and
surface -- one difference alone would not survive being 40 pixels tall.

Cheap, as robed figures are: a cone replaces two legs, two boots, two knees and
two thighs.
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
px = U.start(scn, res=112)
M = U.palette()

figure, detail, noline = [], [], []

# ---- vestments: the flared cone that is the whole lower silhouette ----
figure.append(P.add_cone(scn, "vestment", (0, 0, 0.86), 0.86, 0.42, 1.72, M["vest"], verts=12))
detail += U.tatters(scn, (0, -0.44, 0.10), 1.30, M["vest"],
                        count=7, drop=0.30, seed=5)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.45, 0.38, 0.92, M["vest"], verts=12))

# ---- bone regalia worn OVER the vestments: the family badge, and the thing
# that keeps him from reading as the necromancer in grey ----
figure += U.ribcage(scn, M, (0, -0.36, 2.06), width=0.74, height=0.80, ribs=4)
figure.append(P.add_cyl(scn, "collarbone", (0, -0.30, 2.50), 0.40, 0.10, M["bone"], verts=10))
detail.append(P.add_box(scn, "sash", (0, -0.42, 1.66), (0.58, 0.09, 0.12), M["wood"]))
# small carved bones hung from the collar, staggered so they do not read as a row
for i, (dx, dz) in enumerate(((-0.24, -0.20), (0.0, -0.30), (0.26, -0.18))):
    detail.append(P.add_box(scn, "charm", (dx, -0.44, 2.50 + dz), (0.07, 0.05, 0.17), M["bone"]))

# ---- shoulder mantle and the antlered bone headdress ----
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.56), 0.68, 0.28, 0.44, M["rag"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.48, -0.04, 2.44), 0.23, M["vest"], scale=(1, .95, .8)))

fig_s, det_s, nol_s = U.skull(scn, M, (0, -0.06, 2.94), radius=0.24, eye=M["teal"])
figure += fig_s
detail += det_s
noline += nol_s
# the headdress: curved bone horns off the temples, which is his read at 40px
for s in (-1, 1):
    figure.append(P.add_cone(scn, "horn", (s * 0.26, 0.0, 3.16), 0.075, 0.02, 0.44, M["bone"],
                             rot=(0, math.radians(s * 34), 0), verts=6))
    figure.append(P.add_cone(scn, "hornTip", (s * 0.42, 0.0, 3.44), 0.045, 0.0, 0.30, M["bone"],
                             rot=(0, math.radians(s * 66), 0), verts=6))

# ---- arms: bare bone, one gripping the staff, one raised palm-up ----
figure += U.bone_arm(scn, M, (-0.50, -0.14, 2.36), (-0.70, -0.52, 1.72))
figure += U.bone_arm(scn, M, (0.50, -0.14, 2.38), (0.62, -0.60, 2.28))
# a small flame cupped over the raised hand
noline += U.ghostflame(scn, M, (0.62, -0.62, 2.46), scale=0.8)

# ---- vertebrae staff: stacked discs, its own root so the lean is one number ----
st_root = P.make_root(scn, "staff_root", rot=(0, -11, 0), loc=(-0.74, -0.56, 1.86))
staff = [P.add_cyl(scn, "spineshaft", (0, 0, 0), 0.05, 2.60, M["bone"], verts=6)]
for i in range(9):
    staff.append(P.add_cyl(scn, "vertebra", (0, 0, -1.10 + i * 0.27), 0.105, 0.11, M["bone"], verts=6))
staff.append(P.add_cyl(scn, "cradle", (0, 0, 1.34), 0.16, 0.13, M["iron"], verts=8))
for s in (-1, 1):
    staff.append(P.add_cone(scn, "prong", (s * 0.13, 0, 1.50), 0.045, 0.02, 0.28, M["bone"],
                            rot=(0, math.radians(s * 22), 0), verts=6))
flame = U.ghostflame(scn, M, (0, -0.02, 1.62), scale=1.15)
P.parent_all(st_root, staff + flame)

U.finish(scn, px, "undead_shaman", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in flame))
