"""Archer -- M15_ASSET_SPECS.md entry 2.

  "a keen-eyed human archer in a forest-green hood and brown leather armor,
   longbow with an arrow nocked but pointed down, quiver on the back"

The longbow is the read, and it is the tallest thin object on any hero: a
near-vertical arc as high as the figure. The bandit marksman's crossbow is a
horizontal bar, so the game's two ranged units cannot be confused.

His bow is built from segments that touch, the same construction the goblin
slinger's loop and the infernal caster's arc need. A curve made of separated
pieces reads as beads.

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

HIP = 1.16
figure += H.legs(scn, M, HIP, spread=0.32, mat=M["leath"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.74, 0.50, 0.28), M["leath"], bevel=0.05))

tors_root, tors = H.torso(scn, M, HIP + 0.14, chest_r=0.42, lean=8, mat=M["leath"])
tors.append(P.add_box(scn, "jerkin", (0, -0.12, 0.48), (0.84, 0.42, 0.64), M["green"], bevel=0.05))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.10), (0.88, 0.54, 0.14), M["leath"]))
tors.append(P.add_box(scn, "baldric", (0, -0.34, 0.46), (0.94, 0.09, 0.14), M["leath"],
                      rot=(0, math.radians(30), 0)))
if TRIM:
    tors.append(P.add_box(scn, "bracer", (-0.52, -0.50, 0.06), (0.30, 0.28, 0.22), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["green"], HIP + 0.56, height=1.60, r_base=0.56, r_top=0.30)

hd, hd_det = H.head(scn, M, (0, -0.04, 1.04), r=0.29, hood=M["green"])
tors += hd

# quiver on the back, fletchings showing over the shoulder
tors.append(P.add_cyl(scn, "quiver", (0.30, 0.26, 0.46), 0.15, 0.72, M["leath"], verts=8,
                      rot=(math.radians(-14), 0, math.radians(-22))))
for i, dx in enumerate((-0.05, 0.0, 0.05)):
    detail.append(P.add_box(scn, "fletch", (0.40 + dx, 0.34, 1.66), (0.06, 0.06, 0.14), M["crimson"]))

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.50, -0.08, 0.66), 0.21, M["green"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "upperL", (-0.54, -0.20, 0.48), 0.145, 0.46, M["leath"], verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.60, -0.48, 0.30), 0.13, 0.46, M["leath"], verts=8,
                      rot=(math.radians(58), 0, 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.62, -0.66, 0.24), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "upperR", (0.54, -0.22, 0.44), 0.145, 0.46, M["leath"], verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.42, -0.50, 0.20), 0.13, 0.46, M["leath"], verts=8,
                      rot=(math.radians(46), 0, math.radians(16))))
tors.append(P.add_sphere(scn, "fistR", (0.30, -0.64, 0.10), 0.15, M["skin"]))
P.parent_all(tors_root, tors + hd_det)

# the longbow: an arc of touching segments, held vertically, arrow pointed down
bw_root = P.make_root(scn, "bow_root", rot=(0, 4, 0), loc=(-0.66, -0.82, 1.60))
bow = []
N = 10
pts = []
for i in range(N + 1):
    t = -1.0 + 2.0 * i / N
    # A 0.30 bulge is eight pixels and reads as a bent stick. A longbow has to
    # bow visibly or it is just a pole with a string beside it.
    pts.append((-abs(1.0 - t * t) * 0.56, 0.0, t * 1.46))
for i in range(N):
    bow.append(S.aimed_cyl(scn, "bowlimb", pts[i], pts[i + 1], 0.045, M["wood"], verts=5))
bow.append(S.aimed_cyl(scn, "bowstring", pts[0], pts[-1], 0.020, M["cream"], verts=4))
bow.append(P.add_box(scn, "bowgrip", (-0.30, 0.0, 0.0), (0.10, 0.13, 0.30), M["leath"]))
bow.append(P.add_cyl(scn, "arrow", (-0.16, -0.04, -0.34), 0.024, 1.20, M["wood"], verts=4,
                     rot=(0, math.radians(14), 0)))
bow.append(P.add_cone(scn, "arrowhead", (-0.30, -0.04, -0.94), 0.05, 0.0, 0.16,
                      TRIM or M["steel"], rot=(math.radians(180), 0, 0), verts=5))
if TRIM:
    for z in (-0.70, 0.70):
        bow.append(P.add_cyl(scn, "bownock", (-0.10, 0.0, z), 0.06, 0.09, TRIM, verts=6))
P.parent_all(bw_root, bow)

H.finish(scn, px, "hero_ranged", figure, detail, noline,
         roots=[tors_root, bw_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
