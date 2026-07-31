"""Frost adept -- M15_ASSET_SPECS.md entry 8.

  "a frost mage in pale ice-blue robes with white fur trim, crystal-tipped staff
   swirling with snowflakes and cold blue mist"

The palest robed figure after the healer, and the two are separated by
temperature: cream and gold against ice-blue and white. On a battle line the
healer reads warm and this one cold, which is as much as two support-shaped
silhouettes need.

Her snowflakes are separate small blocks scattered around the staff head rather
than a cloud. Scattered points read as falling; a mass reads as smoke, which is
what the first infernal flame looked like before it was made to climb.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Common**, so that tier gets no separate file.
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

figure += H.robe(scn, M, M["ice"], top=1.74, r_base=0.82, r_top=0.42)
figure.append(P.add_cyl(scn, "hemfur", (0, 0, 0.10), 0.86, 0.20, M["fur"], verts=12))
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.44, 0.38, 0.88, M["ice"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.40, 1.66), (0.58, 0.09, 0.13), M["fur"]))
figure.append(P.add_cone(scn, "furmantle", (0, -0.02, 2.50), 0.68, 0.30, 0.46, M["fur"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.42), 0.22, M["ice"],
                               scale=(1, .95, .8)))
if TRIM:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.66), 0.44, 0.09, TRIM, verts=10))
if LEGEND:
    figure.append(P.add_cone(scn, "overrobe", (0, 0.26, 1.28), 0.78, 0.44, 2.38, M["fur"], verts=10))

hd, hd_det = H.head(scn, M, (0, -0.06, 2.86), r=0.27, hood=M["ice"])
figure += hd
detail += hd_det
if LEGEND:
    for i, s in enumerate((-1, 0, 1)):
        figure.append(P.add_cone(scn, "icecrown", (s * 0.16, -0.10, 3.14 + (1 - abs(s)) * 0.10),
                                 0.05, 0.0, 0.26 + (1 - abs(s)) * 0.12, M["fur"],
                                 rot=(0, math.radians(s * 16), 0), verts=5))

figure += S.limb(scn, (-0.48, -0.12, 2.34), (-0.68, -0.56, 1.82), M["ice"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.48, -0.12, 2.36), (0.68, -0.58, 2.30), M["ice"], 0.13, 0.115,
                 hand_mat=M["skin"])

st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.72, -0.60, 1.94))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.056, 2.80, M["wood"], verts=6)]
for z in (-0.96, -0.16, 0.64):
    staff.append(P.add_cyl(scn, "lash", (0, 0, z), 0.08, 0.08, M["fur"], verts=6))
staff.append(P.add_cone(scn, "cradle", (0, 0, 1.36), 0.16, 0.08, 0.22, TRIM or M["steel"], verts=8))
crystal = [P.add_cone(scn, "crystal", (0, -0.02, 1.66), 0.15, 0.0, 0.46, M["frost"], verts=6),
           P.add_cone(scn, "crystalbase", (0, -0.02, 1.50), 0.15, 0.0, 0.24, M["frost"], verts=6,
                      rot=(math.radians(180), 0, 0))]
# snowflakes: scattered points, not a cloud. Points read as falling; a mass reads
# as smoke.
for i, (dx, dz) in enumerate(((-0.30, 1.30), (0.28, 1.52), (-0.22, 1.92), (0.32, 2.02),
                              (0.02, 2.20), (-0.34, 1.68))):
    crystal.append(P.add_box(scn, "snowflake", (dx, -0.06, dz),
                             (0.075, 0.05, 0.075), M["frost"],
                             rot=(0, math.radians(i * 29), 0)))
P.parent_all(st_root, staff + crystal)

H.finish(scn, px, "hero_frostadept", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in crystal))
