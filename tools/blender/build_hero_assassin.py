"""Assassin -- M15_ASSET_SPECS.md entry 5.

  "a slim hooded assassin in dark charcoal-and-purple leathers, face in shadow,
   slightly crouched, twin curved daggers held low"

The one hero whose face is NOT open, which would normally break the rule that
separates heroes from bandits. He gets away with it because his palette is
charcoal and violet where every bandit is brown, and because he is the only
crouched hero -- two differences carrying the load one usually does.

His daggers are held LOW and close, against the goblin skulker's low-and-forward
and the undead reaver's wide. Three twin-blade figures, three poses.

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

HIP = 1.10
figure += H.legs(scn, M, HIP, spread=0.30, mat=M["charcoal"], boot=M["charcoal"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.68, 0.46, 0.26), M["charcoal"], bevel=0.04))

tors_root, tors = H.torso(scn, M, HIP + 0.12, chest_r=0.38, lean=20, mat=M["charcoal"])
tors.append(P.add_box(scn, "jerkin", (0, -0.12, 0.46), (0.76, 0.38, 0.60), M["charcoal"], bevel=0.05))
tors.append(P.add_box(scn, "sash", (0, -0.06, 0.10), (0.80, 0.48, 0.16), M["violet"]))
tors.append(P.add_box(scn, "strap", (0, -0.30, 0.46), (0.84, 0.09, 0.12), M["violet"],
                      rot=(0, math.radians(34), 0)))
if TRIM:
    for s in (-1, 1):
        tors.append(P.add_box(scn, "bracer", (s * 0.48, -0.44, 0.06), (0.26, 0.26, 0.20), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["violet"], HIP + 0.52, height=1.52, r_base=0.52, r_top=0.28)

hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28, hood=M["charcoal"], shadowed=True)
tors += hd
# the face in shadow: a dark band where the eyes would be, which is the entry
tors.append(P.add_box(scn, "faceshadow", (0, -0.28, 0.98), (0.36, 0.10, 0.24), M["dark"]))
if GLOW:
    noline += [P.add_box(scn, "eyeglint", (s * 0.09, -0.32, 1.00), (0.06, 0.04, 0.05), GLOW)
               for s in (-1, 1)]

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.08, 0.62), 0.19, M["charcoal"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "upperL", (-0.50, -0.20, 0.38), 0.135, 0.44, M["charcoal"], verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.52, -0.46, 0.08), 0.12, 0.44, M["charcoal"], verts=8,
                      rot=(math.radians(40), 0, 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.52, -0.60, -0.12), 0.14, M["skin"]))
tors.append(P.add_cyl(scn, "upperR", (0.50, -0.20, 0.40), 0.135, 0.44, M["charcoal"], verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.50, -0.48, 0.14), 0.12, 0.44, M["charcoal"], verts=8,
                      rot=(math.radians(46), 0, 0)))
tors.append(P.add_sphere(scn, "fistR", (0.50, -0.62, -0.06), 0.14, M["skin"]))

curve = [(-0.045, 0.0), (0.045, 0.0), (0.12, 0.32), (0.14, 0.58), (0.02, 0.70),
         (0.02, 0.54), (-0.035, 0.30)]
dagger_roots = []
for name, rot, loc in (("dagL_root", (0, 152, 0), (-0.54, -0.66, -0.14)),
                       ("dagR_root", (0, 30, 0), (0.52, -0.68, -0.08))):
    dr = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(dr, [P.add_prism(scn, "dagblade", curve, 0.05, M["blade"]),
                      P.add_box(scn, "daggrip", (0, 0, -0.12), (0.07, 0.07, 0.22), M["violet"]),
                      P.add_box(scn, "dagguard", (0, 0, 0.02), (0.18, 0.08, 0.05),
                                TRIM or M["steel"])])
    dagger_roots.append(dr)
P.parent_all(tors_root, tors + hd_det + dagger_roots)

H.finish(scn, px, "hero_assassin", figure, detail, noline,
         roots=[tors_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
