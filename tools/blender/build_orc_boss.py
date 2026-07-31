"""Orc Warband boss -- M15_ASSET_SPECS.md entry 27.

  "BOSS: the Orc Warlord, immense, in trophy-laden black iron armor with skull
   pauldrons and a red war banner cape, gripping a colossal double-headed axe"

"Immense" against a family already described as hulking is the hardest size ask
in the roster, because he has to beat 3.6-unit commons without leaving the frame.
He stands 4.4 units in a 144 cell, and the rest of the impression comes from
WIDTH: skull pauldrons that overhang his shoulders, and a banner cape that
widens him further still.

The double-headed axe is deliberately the largest single object anywhere in the
game's art. Its two bits break his silhouette on both sides at once, which is
something no other weapon does -- every other figure's weapon reads on one side.

Where the Goblin Warmaster is "prouder" by standing upright among stooping
raiders, this one is simply larger than everything near him. Two bosses in two
factions should not use the same trick.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import orc_kit as O
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(O)

scn = P.get_scene()
px = O.start(scn, res=144)
M = O.palette()

figure, detail, noline = [], [], []

HIP = 1.72
figure += O.heavy_legs(scn, M, HIP, spread=0.62)
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.46, 0.82, 0.50), M["iron"], bevel=0.07))
figure.append(P.add_prism(scn, "oloin", [(-0.38, 0.34), (0.38, 0.34), (0.30, -0.76), (-0.30, -0.76)],
                          0.12, M["cloth"], loc=(0.02, -0.44, 1.64)))
figure.append(P.add_box(scn, "obelt", (0, -0.04, 1.98), (1.52, 0.86, 0.22), M["leath"]))
detail.append(P.add_box(scn, "obuckle", (0, -0.50, 1.98), (0.26, 0.07, 0.20), M["steel"]))

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.34, chest_r=0.84, lean=6)
tors += P.add_ridged(scn, "ocuirass", (0, -0.10, 0.66), (1.60, 0.62, 1.00), M["iron"],
                     splay=14, bevel=0.09)

# ---- trophies hung on the armour: small skulls, staggered ----
for dx, dz in ((-0.42, 0.30), (-0.02, 0.20), (0.40, 0.32)):
    tors.append(P.add_sphere(scn, "otrophy", (dx, -0.50, dz), 0.15, M["bone"],
                             scale=(1, 1.02, 1.08), segs=8, rings=6))

# ---- the war banner cape: a wide shell behind him with a ragged hem ----
figure.append(P.add_cone(scn, "ocape", (0, 0.44, 2.34), 1.28, 0.66, 2.10, M["cloth"], verts=12))
detail += S.tatters(scn, (0, 0.52, 1.32), 1.90, M["cloth"], count=8, drop=0.42, seed=11)

# ---- skull pauldrons, which are most of the "immense" ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 1.10, -0.10, 0.94), 0.46, M["hide"],
                             scale=(1, .95, .88)))
    tors.append(P.add_sphere(scn, "opauldron", (s * 1.20, -0.10, 1.10), 0.52, M["bone"],
                             scale=(1.0, 1.02, 0.86), segs=12, rings=8))
    tors.append(P.add_box(scn, "opauldronjaw", (s * 1.22, -0.34, 0.86), (0.44, 0.34, 0.22), M["bone"]))
    tors.append(P.add_cone(scn, "opauldronhorn", (s * 1.34, -0.06, 1.44), 0.11, 0.02, 0.52,
                           M["tusk"], rot=(0, math.radians(s * 32), 0), verts=6))

# both fists on the haft
tors.append(P.add_cyl(scn, "oupperL", (-1.12, -0.30, 0.50), 0.31, 0.76, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeL", (-1.00, -0.66, -0.02), 0.28, 0.68, M["hide"], verts=8,
                      rot=(math.radians(24), 0, 0)))
tors.append(P.add_sphere(scn, "ofistL", (-0.94, -0.82, -0.32), 0.28, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (1.12, -0.30, 0.52), 0.31, 0.74, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeR", (0.82, -0.70, 0.10), 0.28, 0.72, M["hide"], verts=8,
                      rot=(math.radians(32), 0, math.radians(22))))
tors.append(P.add_sphere(scn, "ofistR", (0.54, -0.86, -0.16), 0.28, M["hide"]))

# ---- head, under a horned great helm ----
hd_fig, hd_det = O.head(scn, M, (0, -0.04, 1.44), r=0.54)
tors += hd_fig
tors.append(P.add_sphere(scn, "ohelm", (0, -0.04, 1.66), 0.58, M["iron"],
                         scale=(1.06, 1.0, 0.66), segs=12, rings=6))
for s in (-1, 1):
    tors.append(P.add_cone(scn, "ohelmhorn", (s * 0.50, 0.02, 1.80), 0.13, 0.02, 0.72, M["tusk"],
                           rot=(0, math.radians(s * 46), 0), verts=6))
tors.append(P.add_cone(scn, "ocrest", (0, 0.10, 2.06), 0.13, 0.04, 0.44, M["cloth"], verts=6))

P.parent_all(tors_root, tors + hd_det)

# ---- the colossal double-headed axe. TWO bits, so it breaks his silhouette on
# both sides at once -- the only weapon in the roster that does.
bit = [(0.0, -0.62), (0.46, -0.74), (0.66, -0.30), (0.60, 0.0), (0.66, 0.30),
       (0.46, 0.74), (0.0, 0.62)]
ax_root = P.make_root(scn, "axe_root", rot=(0, -112, 0), loc=(-0.20, -1.00, 1.68))
axe = [P.add_cyl(scn, "oaxehaft", (0, 0, 0.66), 0.115, 2.40, M["wood"], verts=6),
       P.add_prism(scn, "oaxebitA", bit, 0.13, M["steel"], loc=(0.16, 0, 1.70)),
       P.add_prism(scn, "oaxebitB", [(-x, z) for x, z in bit], 0.13, M["steel"], loc=(-0.16, 0, 1.70)),
       P.add_box(scn, "oaxecollar", (0, 0, 1.70), (0.30, 0.26, 0.60), M["iron"], bevel=0.04),
       P.add_cone(scn, "oaxespike", (0, 0, 2.16), 0.09, 0.0, 0.36, M["steel"], verts=6),
       P.add_box(scn, "oaxewrap", (0, 0, -0.26), (0.18, 0.17, 0.40), M["leath"])]
P.parent_all(ax_root, axe)

O.finish(scn, px, "orc_boss", figure, detail, noline, roots=[tors_root, ax_root],
         skip_extra=tuple(o.name for o in hd_det), role="boss", body_roots=[tors_root])
