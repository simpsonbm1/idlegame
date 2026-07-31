"""Banneret -- M15_ASSET_SPECS.md entry 7.

  "a banner-bearing knight in steel half-plate, tall crimson-and-gold war banner
   on a pole in one hand, short sword in the other"

The banner is the tallest object on any hero and the only large FLAT surface in
the roster. It breaks the top of his cell and hangs well clear of his body, so he
is identifiable from further away than anything else the player owns, which is
the point of a standard-bearer.

He needs a 128 cell for the pole. The figure inside it is a normal 2.95 units
like every other hero; only the banner needs the headroom.

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
px = H.start(scn, res=128)
M = H.palette()
TRIM = H.trim_mat(M)        # None on a common hero: plain and field-worn
GLOW = H.glow_mat(M)        # epic and legendary only
LEGEND = H.is_legendary()

figure, detail, noline = [], [], []

HIP = 1.18
figure += H.legs(scn, M, HIP, spread=0.34, mat=M["steel"], boot=M["leath"])
figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.86, 0.54, 0.30), M["steel"], bevel=0.05))

tors_root, tors = H.torso(scn, M, HIP + 0.16, chest_r=0.46, lean=6, mat=M["steel"])
tors += P.add_ridged(scn, "cuirass", (0, -0.06, 0.50), (0.98, 0.46, 0.74), M["steel"],
                     splay=13, bevel=0.07)
tors.append(P.add_box(scn, "surcoat", (0, -0.32, 0.20), (0.48, 0.08, 1.00), M["crimson"]))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.06), (0.94, 0.56, 0.15), M["leath"]))
if TRIM:
    tors.append(P.add_box(scn, "surcoatedge", (0, -0.36, 0.20), (0.12, 0.05, 1.00), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.62, height=1.72, r_base=0.60, r_top=0.32)

hd, hd_det = H.head(scn, M, (0, -0.04, 1.08), r=0.30, helm=M["steel"])
tors += hd
if GLOW:
    noline.append(P.add_box(scn, "crest", (0, 0.08, 1.46), (0.09, 0.28, 0.20), GLOW))

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "pauldron", (s * 0.58, -0.08, 0.72), 0.27, M["steel"],
                             scale=(1, .95, .84)))
tors.append(P.add_cyl(scn, "upperL", (-0.58, -0.18, 0.62), 0.155, 0.46, M["steel"], verts=8,
                      rot=(0, math.radians(-16), 0)))
tors.append(P.add_cyl(scn, "foreL", (-0.70, -0.36, 0.94), 0.14, 0.46, M["steel"], verts=8,
                      rot=(math.radians(-16), math.radians(-10), 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.76, -0.46, 1.18), 0.16, M["steel"]))
tors.append(P.add_cyl(scn, "upperR", (0.58, -0.22, 0.42), 0.155, 0.46, M["steel"], verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.56, -0.50, 0.10), 0.14, 0.46, M["steel"], verts=8,
                      rot=(math.radians(32), 0, 0)))
tors.append(P.add_sphere(scn, "fistR", (0.56, -0.64, -0.12), 0.16, M["steel"]))
P.parent_all(tors_root, tors + hd_det)

# the banner: pole plus a large flat panel, the only broad flat surface on a hero
bn_root = P.make_root(scn, "banner_root", rot=(0, -5, 0), loc=(-0.80, -0.46, 1.30))
banner = [P.add_cyl(scn, "pole", (0, 0, 1.20), 0.055, 3.60, M["wood"], verts=6),
          P.add_cone(scn, "poletip", (0, 0, 3.14), 0.075, 0.0, 0.36, TRIM or M["steel"], verts=6),
          P.add_box(scn, "crossbar", (0.34, 0, 2.70), (0.76, 0.07, 0.08), TRIM or M["steel"])]
panel = [(0.0, 0.0), (1.32, 0.0), (1.32, -1.30), (0.96, -1.04), (0.60, -1.34),
         (0.24, -1.06), (0.0, -1.30)]
banner.append(P.add_prism(scn, "bannerpanel", panel, 0.05, M["crimson"],
                          loc=(0.08, 0.10, 2.64)))
banner.append(P.add_box(scn, "bannerband", (0.72, 0.06, 2.02), (1.30, 0.06, 0.13), M["gold"]))
if TRIM:
    banner.append(P.add_box(scn, "bannerband2", (0.72, 0.06, 1.68), (1.06, 0.06, 0.10), TRIM))
P.parent_all(bn_root, banner)

sw_root = P.make_root(scn, "sword_root", rot=(0, 156, 0), loc=(0.58, -0.72, 1.02))
sword = [P.add_prism(scn, "blade", [(-0.07, 0.12), (0.07, 0.12), (0.07, 0.92), (0.0, 1.12),
                                    (-0.07, 0.92)], 0.10, M["blade"]),
         P.add_box(scn, "guard", (0, 0, 0.10), (0.38, 0.10, 0.09), TRIM or M["steel"]),
         P.add_box(scn, "grip", (0, 0, -0.10), (0.10, 0.09, 0.24), M["leath"])]
P.parent_all(sw_root, sword)

H.finish(scn, px, "hero_banneret", figure, detail, noline,
         roots=[tors_root, bn_root, sw_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
