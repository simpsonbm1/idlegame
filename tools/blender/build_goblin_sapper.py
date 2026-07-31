"""Goblin Raid sapper -- M15_ASSET_SPECS.md entry 20.

  "a goblin tunneler with a stubby candle strapped to a leather cap, hefting a
   pickaxe, dirt-stained clothes"

The candle is the whole point of this entry. It is the only WARM light anywhere in
the goblin family, and against four green-lit or unlit siblings one small orange
flame on his head identifies him before his outline does.

The pickaxe crosses his body on the diagonal, which is the same trick the undead
grave digger's shovel uses. That is deliberate: sappers across the five factions
carry a tool rather than a weapon, and a tool held across the chest is the pose
that says so.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import goblin_kit as G
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(G)

scn = P.get_scene()
px = G.start(scn, res=112)
M = G.palette()

figure, detail, noline = [], [], []

HIP = 1.00
figure += G.wiry_legs(scn, M, HIP, spread=0.29)
figure.append(P.add_box(scn, "ghips", (0, 0, HIP), (0.64, 0.44, 0.28), M["skin"], bevel=0.05))
# dirt-stained wrap rather than a loincloth: he is dressed for work
figure.append(P.add_box(scn, "gapron", (0, -0.28, 0.82), (0.52, 0.10, 0.52), M["rag"]))
detail += S.tatters(scn, (0, -0.30, 0.56), 0.48, M["rag"], count=4, drop=0.16, seed=4)

tors_root, tors = G.hunch(scn, M, HIP + 0.14, chest_r=0.31, lean=20)
tors.append(P.add_box(scn, "gbelt", (0, -0.02, 0.14), (0.68, 0.48, 0.12), M["leath"]))
tors.append(P.add_box(scn, "gstrap", (0, -0.28, 0.42), (0.72, 0.10, 0.12), M["leath"],
                      rot=(0, math.radians(30), 0)))

hd_fig, hd_det = G.head(scn, M, (0, -0.04, 0.88), r=0.27)
tors += hd_fig

# ---- leather cap with the stubby candle strapped on ----
tors.append(P.add_sphere(scn, "gcap", (0, -0.04, 1.06), 0.29, M["leath"], scale=(1.05, 1.0, 0.62),
                         segs=10, rings=6))
tors.append(P.add_box(scn, "gcapstrap", (0, -0.20, 0.96), (0.56, 0.14, 0.09), M["leath"]))
tors.append(P.add_cyl(scn, "gcandle", (0, -0.12, 1.26), 0.065, 0.26, M["tusk"], verts=6))
candleflame = S.flame(scn, (0, -0.12, 1.42), M["fire"], M["fire_d"], scale=0.55)

# arms: both up on the pickaxe haft
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "gshoulder", (s * 0.36, -0.06, 0.58), 0.17, M["skin"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "gupperL", (-0.44, -0.20, 0.40), 0.125, 0.44, M["skin"], verts=8))
tors.append(P.add_cyl(scn, "gforeL", (-0.44, -0.46, 0.18), 0.11, 0.44, M["skin"], verts=8,
                      rot=(math.radians(40), 0, 0)))
tors.append(P.add_sphere(scn, "gfistL", (-0.44, -0.60, 0.02), 0.14, M["skin"]))
tors.append(P.add_cyl(scn, "gupperR", (0.44, -0.20, 0.44), 0.125, 0.42, M["skin"], verts=8))
tors.append(P.add_cyl(scn, "gforeR", (0.34, -0.48, 0.34), 0.11, 0.44, M["skin"], verts=8,
                      rot=(math.radians(34), 0, math.radians(22))))
tors.append(P.add_sphere(scn, "gfistR", (0.20, -0.62, 0.22), 0.14, M["skin"]))

P.parent_all(tors_root, tors + hd_det + candleflame)

# ---- pickaxe: own root, hafted across the body on the diagonal ----
pk_root = P.make_root(scn, "pick_root", rot=(0, -128, 0), loc=(-0.20, -0.76, 1.16))
head_pts = [(-0.52, 0.04), (-0.20, -0.05), (0.20, -0.05), (0.52, 0.04),
            (0.44, 0.14), (0.0, 0.09), (-0.44, 0.14)]
pick = [P.add_cyl(scn, "gpickhaft", (0, 0, 0.44), 0.05, 1.32, M["wood"], verts=6),
        P.add_prism(scn, "gpickhead", head_pts, 0.10, M["rust"], loc=(0, 0, 1.04)),
        P.add_box(scn, "gpickeye", (0, 0, 1.02), (0.15, 0.13, 0.17), M["rust"]),
        P.add_box(scn, "gpickwrap", (0, 0, 0.12), (0.10, 0.10, 0.22), M["leath"])]
P.parent_all(pk_root, pick)

G.finish(scn, px, "goblin_sapper", figure, detail, noline,
         roots=[tors_root, pk_root],
         skip_extra=tuple(o.name for o in hd_det + candleflame), role="sapper", body_roots=[tors_root])
