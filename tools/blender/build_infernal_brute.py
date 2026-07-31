"""Infernal Siege brute -- M15_ASSET_SPECS.md entry 40.

  "a massive pit fiend demon with curling ram horns and glowing ember-orange
   cracks across its muscles, hefting a huge jagged cleaver blade"

The family's body plan. Charcoal hide is the darkest material in the roster and
would normally be unusable, because an outline cannot read against near-black.
It works here only because the ember cracks do the separating instead: they run
down the arms, chest and thighs, and every one of them is a bright bar against
the dark. Strip them off and he is a silhouette with no interior.

His cleaver is a single wide slab. The orc's double axe is the other huge weapon
in the game and it is symmetric, so this one is deliberately one-sided and
top-heavy.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import infernal_kit as I
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(I)

scn = P.get_scene()
px = I.start(scn, res=112)
M = I.palette()

figure, detail, noline = [], [], []

HIP = 1.34
# ---- heavy digitigrade legs: the hock stands well above the foot, which is what
# stops him reading as a big man with horns.
for s, yoff in ((-1, -0.26), (1, 0.24)):
    figure.append(P.add_box(scn, "ihoof", (s * 0.48, yoff - 0.14, 0.14), (0.44, 0.66, 0.28),
                            M["horn"], bevel=0.05))
    figure.append(P.add_cyl(scn, "ishank", (s * 0.46, yoff - 0.02, 0.52), 0.20, 0.68, M["hide"], verts=8))
    figure.append(P.add_sphere(scn, "ihock", (s * 0.46, yoff + 0.14, 0.90), 0.25, M["hide"],
                               scale=(1, .9, .85)))
    figure.append(P.add_cyl(scn, "ithigh", (s * 0.44, yoff * 0.5, 1.16), 0.31, 0.58, M["hide"], verts=8))

figure.append(P.add_box(scn, "ihips", (0, 0, HIP), (1.16, 0.68, 0.40), M["hide"], bevel=0.06))
figure.append(P.add_box(scn, "ibelt", (0, -0.04, 1.54), (1.20, 0.72, 0.18), M["iron"]))
detail.append(P.add_box(scn, "ibuckle", (0, -0.42, 1.54), (0.20, 0.06, 0.17), M["brass"]))

tors_root = P.make_root(scn, "torso_root", rot=(-8, 0, 0), loc=(0, 0, HIP + 0.16))
tors = [P.add_cyl(scn, "iwaist", (0, 0, 0.14), 0.48, 0.42, M["hide"], verts=10, scale=(1.10, 0.80, 1)),
        P.add_sphere(scn, "ichest", (0, -0.06, 0.64), 0.72, M["hide"],
                     scale=(1.26, 0.82, 0.88), segs=12, rings=8)]
# crimson plates over the shoulders and chest, the only non-black hide he wears
tors.append(P.add_box(scn, "ipectoral", (0, -0.34, 0.66), (1.06, 0.20, 0.44), M["crim"], bevel=0.05))

# ---- the cracks. These ARE the figure's interior; without them he is a blob. ----
tors += []
noline += I.cracks(scn, M, [(-0.30, -0.44, 2.12, 0.34), (0.26, -0.44, 2.30, 0.26),
                            (0.02, -0.46, 1.86, 0.22)])
noline += I.cracks(scn, M, [(-0.52, -0.30, 1.04, 0.30), (0.50, -0.30, 1.16, 0.24)], hot=False)

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "ishoulder", (s * 0.94, -0.10, 0.88), 0.40, M["hide"],
                             scale=(1, .95, .88)))
    tors.append(P.add_cone(scn, "ispaulspike", (s * 1.02, -0.08, 1.16), 0.10, 0.02, 0.40, M["horn"],
                           rot=(0, math.radians(s * 26), 0), verts=6))

# ---- both clawed hands on the cleaver ----
tors += I.clawed_limb(scn, M, (-0.94, -0.14, 0.86), (-0.82, -0.72, -0.16), upper_r=0.24, fore_r=0.21)
tors += I.clawed_limb(scn, M, (0.94, -0.14, 0.88), (0.46, -0.78, 0.02), upper_r=0.24, fore_r=0.21)

# ---- head: heavy jaw, ember eyes, curling ram horns ----
tors.append(P.add_cyl(scn, "ineck", (0, 0, 1.06), 0.22, 0.22, M["hide"], verts=8))
tors.append(P.add_sphere(scn, "iskull", (0, -0.04, 1.34), 0.42, M["hide"],
                         scale=(1.06, 1.0, 0.94), segs=12, rings=8))
tors.append(P.add_box(scn, "ijaw", (0, -0.38, 1.14), (0.66, 0.50, 0.32), M["hide"], bevel=0.05))
tors += I.horns(scn, M, (0, -0.02, 1.42), r=0.42, curl=3, sweep=42, length=0.36)
tors_det = [P.add_box(scn, "ifangline", (0, -0.62, 1.10), (0.50, 0.06, 0.07), M["bone"])]
tors_nol = [P.add_box(scn, "ieye", (s * 0.16, -0.44, 1.40), (0.15, 0.06, 0.10), M["ember_h"])
            for s in (-1, 1)]
tors_nol += I.cracks(scn, M, [(0.0, -0.46, 1.56, 0.14)])

P.parent_all(tors_root, tors + tors_det + tors_nol)

# ---- the cleaver: one wide slab, one-sided and top-heavy ----
slab = [(-0.12, -0.10), (0.12, -0.10), (0.16, 0.42), (0.62, 0.60), (0.58, 1.02),
        (0.20, 1.34), (0.06, 1.86), (-0.14, 1.40), (-0.16, 0.62)]
cv_root = P.make_root(scn, "cleaver_root", rot=(0, -126, 0), loc=(-0.16, -0.90, 1.28))
cleaver = [P.add_prism(scn, "icleaver", slab, 0.15, M["iron"]),
           P.add_box(scn, "icleavergrip", (0, 0, -0.28), (0.15, 0.17, 0.36), M["crim"]),
           P.add_cyl(scn, "icleaverpommel", (0, 0, -0.50), 0.11, 0.11, M["brass"], verts=6)]
edge = [P.add_box(scn, "icleaveredge", (0.34, 0, 0.82), (0.30, 0.05, 0.09), M["ember_d"],
                  rot=(0, math.radians(-22), 0))]
P.parent_all(cv_root, cleaver + edge)

I.finish(scn, px, "infernal_brute", figure, detail, noline,
         roots=[tors_root, cv_root],
         skip_extra=tuple(o.name for o in tors_det + tors_nol + edge),
         role="brute", body_roots=[tors_root])
