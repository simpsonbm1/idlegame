"""Fighter -- M15_ASSET_SPECS.md entry 1.

  "a hardened human footman soldier in a chainmail shirt, open-faced kettle
   helmet, and red-and-steel tabard, gripping a longsword in both hands"

The rank-and-file soldier, and the hero closest to the guardian knight, so the
two are separated the way real infantry differ from real knights: MAIL rather
than plate, a brimmed open helmet rather than a great helm, and a tabard rather
than a surcoat over armour.

His sword is held in both hands down the centre line, which is the most stable
silhouette in the roster and right for the unit a player sees most.

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

HIP = 1.18
figure += H.legs(scn, M, HIP, spread=0.34, mat=M["mail"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.80, 0.52, 0.30), M["mail"], bevel=0.05))

tors_root, tors = H.torso(scn, M, HIP + 0.14, chest_r=0.46, lean=6)
tors.append(P.add_box(scn, "tabard", (0, -0.32, 0.34), (0.50, 0.08, 1.10), M["crimson"]))
tors.append(P.add_box(scn, "tabardback", (0, 0.30, 0.34), (0.50, 0.08, 1.10), M["crimson"]))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.10), (0.92, 0.56, 0.15), M["leath"]))
if TRIM:
    tors.append(P.add_box(scn, "tabardedge", (0, -0.37, 0.34), (0.13, 0.05, 1.10), TRIM))
    tors.append(P.add_box(scn, "pauldrontrim", (0, -0.30, 0.78), (0.98, 0.10, 0.11), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.60, height=1.70, r_base=0.60, r_top=0.32)

hd, hd_det = H.head(scn, M, (0, -0.04, 1.06), r=0.30, helm=M["steel"])
tors += hd
if GLOW:
    noline.append(P.add_box(scn, "helmcrest", (0, 0.06, 1.44), (0.10, 0.30, 0.18), GLOW))

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.54, -0.08, 0.68), 0.23, M["steel"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "upperL", (-0.56, -0.22, 0.40), 0.155, 0.48, M["mail"], verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.44, -0.52, 0.10), 0.14, 0.48, M["steel"], verts=8,
                      rot=(math.radians(32), 0, math.radians(-16))))
tors.append(P.add_sphere(scn, "fistL", (-0.30, -0.66, -0.10), 0.16, M["steel"]))
tors.append(P.add_cyl(scn, "upperR", (0.56, -0.22, 0.42), 0.155, 0.46, M["mail"], verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.42, -0.54, 0.16), 0.14, 0.48, M["steel"], verts=8,
                      rot=(math.radians(36), 0, math.radians(18))))
tors.append(P.add_sphere(scn, "fistR", (0.26, -0.68, -0.04), 0.16, M["steel"]))
P.parent_all(tors_root, tors + hd_det)

blade = [(-0.07, 0.14), (0.07, 0.14), (0.07, 1.24), (0.0, 1.50), (-0.07, 1.24)]
sw_root = P.make_root(scn, "sword_root", rot=(0, 6, 0), loc=(-0.02, -0.80, 1.02))
sword = [P.add_prism(scn, "blade", blade, 0.11, M["blade"]),
         P.add_box(scn, "guard", (0, 0, 0.12), (0.46, 0.11, 0.10), TRIM or M["steel"]),
         P.add_box(scn, "grip", (0, 0, -0.10), (0.11, 0.10, 0.26), M["leath"]),
         P.add_sphere(scn, "pommel", (0, 0, -0.26), 0.10, TRIM or M["steel"])]
P.parent_all(sw_root, sword)

H.finish(scn, px, "hero_fighter", figure, detail, noline,
         roots=[tors_root, sw_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
