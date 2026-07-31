"""Bandit Horde shaman -- M15_ASSET_SPECS.md entry 31.

  "a bandit field medic, leather satchel of bandages and tonics across the chest,
   holding up a small bottle of red medicine"

The roster's only support unit that is not mystical. The undead bone priest and
the orc witch doctor hold staffs; this one holds a bottle, and the bottle is four
pixels across, so it cannot be the read on its own.

What carries him instead is the SATCHEL and the bandages: a big pale slab across
his chest with white wraps on both forearms. He is the palest figure in a faction
of browns, which is the same trick a real field medic uses, and it works at
sprite size for the same reason.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import bandit_kit as B
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(B)

scn = P.get_scene()
px = B.start(scn, res=112)
M = B.palette()

figure, detail, noline = [], [], []

HIP = 1.14
figure += B.lean_legs(scn, M, HIP, spread=0.34)
figure.append(P.add_box(scn, "bhips", (0, 0, HIP), (0.76, 0.50, 0.30), M["leath"], bevel=0.05))

tors_root, tors = B.torso(scn, M, HIP + 0.14, chest_r=0.42, lean=8)
tors.append(P.add_box(scn, "bjerkin", (0, -0.12, 0.48), (0.84, 0.42, 0.64), M["leath"], bevel=0.05))

# ---- the satchel and bandages: a pale slab and pale wraps, which is what makes
# him the lightest figure in a faction of browns and therefore findable at a
# glance. The bottle is four pixels and cannot do this job.
tors.append(P.add_box(scn, "bsatchelstrap", (0, -0.34, 0.52), (1.06, 0.10, 0.17), M["cloth"],
                      rot=(0, math.radians(-30), 0)))
tors.append(P.add_box(scn, "bsatchel", (-0.44, -0.26, 0.06), (0.44, 0.34, 0.40), M["cloth"], bevel=0.04))
detail.append(P.add_box(scn, "bsatchelflap", (-0.44, -0.40, 0.20), (0.46, 0.20, 0.16), M["leath"]))
detail.append(P.add_box(scn, "bsatchelcross", (-0.44, -0.44, 0.04), (0.08, 0.05, 0.24), M["red"]))
detail.append(P.add_box(scn, "bsatchelcrossbar", (-0.44, -0.44, 0.04), (0.24, 0.05, 0.08), M["red"]))
# tonic bottles tucked in a chest loop, staggered so they are not a printed row
for i, dx in enumerate((0.14, 0.30, 0.46)):
    tors.append(P.add_cyl(scn, "bvial", (dx, -0.36, 0.30 + (i % 2) * 0.07), 0.055, 0.19,
                          M["cloth"], verts=6))
tors.append(P.add_box(scn, "bbelt", (0, -0.04, 0.12), (0.88, 0.54, 0.14), M["rag"]))

hd_fig, hd_det = B.head(scn, M, (0, -0.04, 1.02), r=0.29, cover="scarf", hood=True)
tors += hd_fig

# ---- one arm raised with the bottle, one down. Both forearms wrapped in
# bandages, which repeats the pale note away from the chest.
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "bshoulder", (s * 0.52, -0.08, 0.66), 0.22, M["leath"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "bupperL", (-0.56, -0.22, 0.40), 0.15, 0.44, M["coat"], verts=8))
tors.append(P.add_cyl(scn, "bforeL", (-0.54, -0.48, 0.08), 0.135, 0.44, M["cloth"], verts=8,
                      rot=(math.radians(28), 0, 0)))
tors.append(P.add_sphere(scn, "bfistL", (-0.52, -0.60, -0.14), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "bupperR", (0.56, -0.20, 0.72), 0.15, 0.44, M["coat"], verts=8,
                      rot=(0, math.radians(24), 0)))
tors.append(P.add_cyl(scn, "bforeR", (0.68, -0.34, 1.02), 0.135, 0.44, M["cloth"], verts=8,
                      rot=(math.radians(-16), math.radians(14), 0)))
tors.append(P.add_sphere(scn, "bfistR", (0.74, -0.44, 1.24), 0.15, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the bottle of red medicine, held up in the raised hand ----
bt_root = P.make_root(scn, "bottle_root", rot=(0, 12, 0), loc=(0.78, -0.48, 2.52))
bottle = [P.add_cyl(scn, "bbottle", (0, 0, 0.10), 0.095, 0.26, M["cloth"], verts=8),
          P.add_cyl(scn, "bbottleneck", (0, 0, 0.28), 0.045, 0.12, M["cloth"], verts=6),
          P.add_cyl(scn, "bcork", (0, 0, 0.36), 0.05, 0.07, M["wood"], verts=6)]
glow = [P.add_box(scn, "btonic", (0, -0.05, 0.09), (0.11, 0.05, 0.17), M["tonic"])]
P.parent_all(bt_root, bottle + glow)

B.finish(scn, px, "bandit_shaman", figure, detail, noline,
         roots=[tors_root, bt_root],
         skip_extra=tuple(o.name for o in hd_det + glow),
         role="shaman", body_roots=[tors_root])
