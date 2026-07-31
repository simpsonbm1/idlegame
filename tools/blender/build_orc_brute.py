"""Orc Warband brute -- M15_ASSET_SPECS.md entry 22.

  "an orc brute in heavy black iron armor, red war paint across the face,
   hefting a massive two-handed spiked maul"

The family's body plan, and the figure the other five are variants of. He is the
broadest common enemy in the game: 3.6 units tall against a goblin common's 2.5
and close to twice as wide, which is what "hulking" has to mean under a locked
camera.

The maul is held across the body in two fists rather than raised. A raised weapon
needs headroom and would push him into a taller cell for no gain, and a heavy
weapon reads heavier when it hangs.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import orc_kit as O
import pixelrig as P
importlib.reload(P)
importlib.reload(O)

scn = P.get_scene()
px = O.start(scn, res=128)
M = O.palette()

figure, detail, noline = [], [], []

HIP = 1.42
figure += O.heavy_legs(scn, M, HIP, spread=0.52)
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.24, 0.72, 0.44), M["iron"], bevel=0.06))
figure.append(P.add_prism(scn, "oloin", [(-0.34, 0.30), (0.34, 0.30), (0.26, -0.66), (-0.26, -0.66)],
                          0.11, M["leath"], loc=(0.02, -0.38, 1.36)))

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.16, chest_r=0.72, lean=8)
# black iron over the chest, ridged so the ramp lands two tones on one piece
# Wider than the chest sphere beneath it (1.82 across) and pushed forward, or the
# green shows all round the plate and he reads as an unarmoured orc with a patch.
tors += P.add_ridged(scn, "ocuirass", (0, -0.16, 0.62), (1.94, 0.62, 0.96), M["iron"],
                     splay=14, bevel=0.08)
tors.append(P.add_box(scn, "obelt", (0, -0.04, 0.18), (1.30, 0.76, 0.20), M["leath"]))
detail.append(P.add_box(scn, "obuckle", (0, -0.44, 1.60), (0.22, 0.06, 0.18), M["steel"]))

hd_fig, hd_det = O.head(scn, M, (0, -0.04, 1.24), r=0.48)
tors += hd_fig
# a black iron half-helm that leaves the painted face showing
tors.append(P.add_sphere(scn, "ohelm", (0, -0.04, 1.44), 0.50, M["iron"],
                         scale=(1.06, 1.0, 0.60), segs=12, rings=6))
for s in (-1, 1):
    tors.append(P.add_cone(scn, "ohelmhorn", (s * 0.44, 0.02, 1.54), 0.10, 0.02, 0.44, M["tusk"],
                           rot=(0, math.radians(s * 52), 0), verts=6))

# ---- huge shoulders. Most of the width a viewer registers is here and at the feet.
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 0.96, -0.10, 0.86), 0.42, M["hide"],
                             scale=(1, .95, .88)))
    tors.append(P.add_sphere(scn, "opauldron", (s * 1.02, -0.10, 0.98), 0.42, M["iron"],
                             scale=(1, 1, .64)))
    tors.append(P.add_cone(scn, "ospike", (s * 1.08, -0.10, 1.22), 0.09, 0.02, 0.32, M["steel"],
                           rot=(0, math.radians(s * 22), 0), verts=6))
# both arms forward on the haft
tors.append(P.add_cyl(scn, "oupperL", (-0.98, -0.28, 0.44), 0.28, 0.72, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeL", (-0.86, -0.60, -0.04), 0.25, 0.62, M["hide"], verts=8,
                      rot=(math.radians(24), 0, 0)))
tors.append(P.add_sphere(scn, "ofistL", (-0.80, -0.74, -0.32), 0.25, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (0.98, -0.28, 0.46), 0.28, 0.70, M["hide"], verts=8))
tors.append(P.add_cyl(scn, "oforeR", (0.72, -0.64, 0.06), 0.25, 0.66, M["hide"], verts=8,
                      rot=(math.radians(34), 0, math.radians(20))))
tors.append(P.add_sphere(scn, "ofistR", (0.48, -0.78, -0.18), 0.25, M["hide"]))

P.parent_all(tors_root, tors + hd_det)

# ---- the maul: a blunt iron head with spikes, hafted low across the body ----
ml_root = P.make_root(scn, "maul_root", rot=(0, -118, 0), loc=(-0.14, -0.86, 1.34))
maul = [P.add_cyl(scn, "omaulhaft", (0, 0, 0.60), 0.09, 1.90, M["wood"], verts=6),
        P.add_box(scn, "omaulhead", (0, 0, 1.56), (0.46, 0.46, 0.62), M["iron"], bevel=0.06),
        P.add_box(scn, "omaulband", (0, 0, 1.26), (0.34, 0.34, 0.13), M["steel"]),
        P.add_box(scn, "omaulwrap", (0, 0, -0.16), (0.15, 0.15, 0.34), M["leath"])]
for i, z in enumerate((1.40, 1.70)):
    for s in (-1, 1):
        maul.append(P.add_cone(scn, "omaulspike", (s * 0.26, 0, z), 0.075, 0.0, 0.30, M["steel"],
                               rot=(0, math.radians(s * 90), 0), verts=5))
P.parent_all(ml_root, maul)

O.finish(scn, px, "orc_brute", figure, detail, noline, roots=[tors_root, ml_root],
         skip_extra=tuple(o.name for o in hd_det))
