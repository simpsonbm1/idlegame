"""Paladin -- M15_ASSET_SPECS.md entry 4.

  "a holy paladin in polished silver-white plate armor with gold trim, warhammer
   in one hand, radiant golden holy symbol in the other"

The brightest ARMOURED figure in the game, and the counterweight to the guardian
knight's blue steel: same plate build, near-white rather than blue, gold rather
than navy. The two are meant to be recognisably the same class of soldier.

His holy symbol is held out at arm's length rather than worn, which makes it the
only hero silhouette with a bright point detached from the body.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Epic (the Crusader)**, so that tier gets no separate file.
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

HIP = 1.20
figure += H.legs(scn, M, HIP, spread=0.36, mat=M["fur"], boot=M["fur"])
figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.92, 0.56, 0.32), M["fur"], bevel=0.05))
figure.append(P.add_box(scn, "belt", (0, -0.02, HIP + 0.20), (0.96, 0.60, 0.16), M["gold"]))

tors_root, tors = H.torso(scn, M, HIP + 0.20, chest_r=0.48, lean=5, mat=M["fur"])
tors += P.add_ridged(scn, "cuirass", (0, -0.06, 0.52), (1.00, 0.48, 0.78), M["fur"],
                     splay=13, bevel=0.07)
tors.append(P.add_box(scn, "placket", (0, -0.34, 0.50), (0.12, 0.07, 0.72), M["gold"]))
if TRIM:
    tors.append(P.add_box(scn, "cuirasstrim", (0, -0.32, 0.86), (0.94, 0.08, 0.10), TRIM))
    tors.append(P.add_box(scn, "cuirassbase", (0, -0.32, 0.16), (0.90, 0.08, 0.09), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["fur"], HIP + 0.66, height=1.76, r_base=0.62, r_top=0.32)

hd, hd_det = H.head(scn, M, (0, -0.04, 1.10), r=0.30, helm=M["fur"])
tors += hd
if LEGEND:
    for s in (-1, 1):
        tors.append(P.add_prism(scn, "helmwing",
                                [(0.0, 0.0), (0.34, 0.30), (0.46, 0.10), (0.30, -0.10)],
                                0.05, M["brightgold"],
                                loc=(s * 0.30, 0.06, 1.36), rot=(0, 0, math.radians(s * 90 - 90))))

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "pauldron", (s * 0.60, -0.08, 0.74), 0.28, M["fur"],
                             scale=(1, .95, .82)))
    if TRIM:
        tors.append(P.add_cyl(scn, "pauldronrim", (s * 0.60, -0.08, 0.60), 0.26, 0.08, TRIM, verts=10))
tors.append(P.add_cyl(scn, "upperL", (-0.60, -0.22, 0.44), 0.16, 0.46, M["fur"], verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.56, -0.50, 0.12), 0.145, 0.46, M["fur"], verts=8,
                      rot=(math.radians(30), 0, 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.54, -0.64, -0.10), 0.16, M["fur"]))
tors.append(P.add_cyl(scn, "upperR", (0.60, -0.20, 0.60), 0.16, 0.46, M["fur"], verts=8,
                      rot=(0, math.radians(22), 0)))
tors.append(P.add_cyl(scn, "foreR", (0.74, -0.42, 0.90), 0.145, 0.46, M["fur"], verts=8,
                      rot=(math.radians(-24), math.radians(16), 0)))
tors.append(P.add_sphere(scn, "fistR", (0.80, -0.54, 1.14), 0.16, M["fur"]))
P.parent_all(tors_root, tors + hd_det)

# the holy symbol, held out at arm's length
hs_root = P.make_root(scn, "symbol_root", loc=(0.84, -0.60, 2.62))
symbol = [P.add_box(scn, "symbolstem", (0, 0, 0.10), (0.09, 0.06, 0.46), M["gold"]),
          P.add_box(scn, "symbolbar", (0, 0, 0.20), (0.34, 0.06, 0.09), M["gold"])]
radiance = [P.add_sphere(scn, "symbolcore", (0, -0.04, 0.20), 0.10, M["holy"], segs=8, rings=5)]
if GLOW or LEGEND:
    for i in range(4):
        radiance.append(P.add_box(scn, "symbolray", (0, -0.06, 0.20), (0.52, 0.04, 0.06),
                                  M["holy"], rot=(0, math.radians(-i * 45), 0)))
P.parent_all(hs_root, symbol + radiance)

# warhammer in the low hand
hm_root = P.make_root(scn, "hammer_root", rot=(0, -14, 0), loc=(-0.56, -0.72, 1.02))
hammer = [P.add_cyl(scn, "hammerhaft", (0, 0, 0.46), 0.06, 1.30, M["wood"], verts=6),
          P.add_box(scn, "hammerhead", (0, 0, 1.16), (0.30, 0.28, 0.40), M["fur"], bevel=0.05),
          P.add_box(scn, "hammerband", (0, 0, 1.16), (0.34, 0.32, 0.10), M["gold"]),
          P.add_box(scn, "hammergrip", (0, 0, -0.14), (0.10, 0.10, 0.24), M["leath"])]
P.parent_all(hm_root, hammer)

H.finish(scn, px, "hero_paladin", figure, detail, noline,
         roots=[tors_root, hs_root, hm_root],
         skip_extra=tuple(o.name for o in hd_det + radiance),
         body_roots=[tors_root])
