"""Blacksmith -- M15_ASSET_SPECS.md entry 11.

  "a brawny blacksmith in a heavy leather apron, smithing hammer resting on one
   shoulder, tongs tucked in the belt"

The one townsperson whose arm is RAISED, which normally marks a combatant. He
gets away with it because the thing on his shoulder is a work hammer with a
square head, not a war hammer with a faced one, and because his other arm hangs.

Bare forearms are his second read. Every other townsperson is sleeved, so the
two blocks of skin between his apron and his fists are unique to him.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import townsfolk_kit as T
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(T)

scn = P.get_scene()
px = T.start(scn, res=112)
M = T.palette()

figure, detail, noline = [], [], []

HIP = 1.16
figure += T.legs(scn, M, HIP, spread=0.36, mat=M["wool"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.88, 0.54, 0.30), M["leath"], bevel=0.05))

tors_root, tors = T.torso(scn, M, HIP + 0.14, chest_r=0.50, lean=5, mat=M["linen"])
tors.append(P.add_box(scn, "apron", (0, -0.40, 0.24), (0.84, 0.11, 1.12), M["leath"]))
tors.append(P.add_box(scn, "apronstrap", (0, -0.34, 0.80), (0.44, 0.10, 0.13), M["leath"]))
tors.append(P.add_box(scn, "belt", (0, -0.04, -0.06), (0.96, 0.60, 0.15), M["leath"]))
# tongs tucked in the belt
detail.append(P.add_box(scn, "tongs", (0.44, -0.36, 1.28), (0.09, 0.07, 0.52), M["iron"]))
detail.append(P.add_box(scn, "tongsjaw", (0.44, -0.38, 1.56), (0.18, 0.06, 0.10), M["iron"]))

hd, hd_det = T.head(scn, M, (0, -0.04, 1.04), r=0.30)
tors += hd
tors.append(P.add_box(scn, "headband", (0, -0.10, 1.24), (0.64, 0.58, 0.12), M["linen"]))

# one arm up on the hammer, one hanging. Bare forearms, which no other
# townsperson has.
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.56, -0.08, 0.70), 0.24, M["linen"],
                             scale=(1, .95, .88)))
tors += S.limb(scn, (-0.56, -0.10, 0.70), (-0.62, -0.46, 1.10), M["skin"], 0.16, 0.145)
tors += S.limb(scn, (0.56, -0.10, 0.70), (0.60, -0.56, -0.14), M["skin"], 0.16, 0.145)
P.parent_all(tors_root, tors + hd_det)

# the smithing hammer, resting back over the shoulder
hm_root = P.make_root(scn, "hammer_root", rot=(0, -148, 0), loc=(-0.58, -0.50, 2.36))
hammer = [P.add_cyl(scn, "haft", (0, 0, 0.42), 0.055, 1.10, M["wood"], verts=6),
          P.add_box(scn, "hammerhead", (0, 0, 1.02), (0.24, 0.24, 0.42), M["iron"], bevel=0.04),
          P.add_box(scn, "hammerband", (0, 0, 1.02), (0.27, 0.27, 0.09), M["brass"]),
          P.add_box(scn, "hammergrip", (0, 0, -0.10), (0.09, 0.09, 0.22), M["leath"])]
P.parent_all(hm_root, hammer)

T.finish(scn, px, "town_blacksmith", figure, detail, noline,
         roots=[tors_root, hm_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
