"""Infernal Siege skirmisher -- M15_ASSET_SPECS.md entry 41.

  "a hellhound: four-legged, standing on all four legs with every paw visible,
   three-quarter side view; charcoal-black hide, glowing ember-orange mane and
   eyes, fire licking from its jaws"

The only QUADRUPED in the game, which makes it the strongest silhouette in the
whole roster: a long horizontal mass where every other sprite is a vertical one.
Nothing else needs to be distinctive about it.

Two things follow from being four-legged. It faces further round than the other
enemies, because a dog seen at the standard three-quarter angle is mostly chest
and no body -- the root turn is -62 degrees rather than -30, which shows the
flank. And its height goes into LENGTH instead: the role system sizes it to a
skirmisher's 2.83 units at the shoulder-and-head, and the body then runs about
as far again backwards.

The mane is emissive rather than modelled fur. A ruff of small bright blocks
along the neck reads as burning at sprite size; individual hairs do not exist at
this resolution.
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

# The body runs along Y, which after the facing turn lands across the screen.
# Front of the animal is -Y, the direction every character in the rig faces.
BODY_Z = 1.32

# ---- four legs, every paw visible. The two far legs are pushed away in Y and
# the two near ones forward, so all four read separately instead of pairing into
# two thick columns.
for name, ybase, zknee in (("fore", -0.66, 0.74), ("hind", 0.62, 0.80)):
    for s, ynudge in ((-1, -0.16), (1, 0.16)):
        yy = ybase + ynudge * 0.42
        figure.append(P.add_box(scn, "ipaw", (s * 0.30, yy - 0.06, 0.12),
                                (0.30, 0.44, 0.24), M["horn"], bevel=0.04))
        figure.append(P.add_cyl(scn, "ilowerleg", (s * 0.30, yy, zknee * 0.50),
                                0.115, zknee * 0.72, M["hide"], verts=8))
        figure.append(P.add_sphere(scn, "iknee", (s * 0.30, yy - 0.06, zknee),
                                   0.155, M["hide"], scale=(1, .9, .85)))
        figure.append(P.add_cyl(scn, "iupperleg", (s * 0.30, yy * 0.92, (BODY_Z + zknee) * 0.52),
                                0.185, BODY_Z - zknee + 0.20, M["hide"], verts=8))

# ---- the barrel body, running front to back ----
figure.append(P.add_sphere(scn, "ibody", (0, 0.14, BODY_Z), 0.50, M["hide"],
                           scale=(0.86, 1.62, 0.94), segs=12, rings=8))
figure.append(P.add_sphere(scn, "ichest", (0, -0.58, BODY_Z + 0.04), 0.44, M["hide"],
                           scale=(0.98, 0.90, 1.02), segs=12, rings=8))
figure.append(P.add_sphere(scn, "ihaunch", (0, 0.84, BODY_Z + 0.06), 0.42, M["hide"],
                           scale=(1.0, 0.92, 1.04), segs=12, rings=8))
noline += I.cracks(scn, M, [(-0.26, 0.10, BODY_Z + 0.30, 0.30),
                            (0.22, 0.46, BODY_Z + 0.26, 0.24),
                            (-0.20, 0.70, BODY_Z + 0.20, 0.20)])

# ---- neck and head, carried low and forward the way a hound's is ----
figure.append(P.add_cyl(scn, "ineck", (0, -0.92, BODY_Z + 0.20), 0.24, 0.46, M["hide"], verts=8,
                        rot=(math.radians(-52), 0, 0)))
figure.append(P.add_sphere(scn, "iskull", (0, -1.22, BODY_Z + 0.36), 0.29, M["hide"],
                           scale=(0.94, 1.10, 0.96), segs=10, rings=7))
figure.append(P.add_box(scn, "isnout", (0, -1.56, BODY_Z + 0.22), (0.32, 0.52, 0.26),
                        M["hide"], bevel=0.05))
detail.append(P.add_box(scn, "ifangs", (0, -1.78, BODY_Z + 0.14), (0.28, 0.10, 0.07), M["bone"]))
for s in (-1, 1):
    figure.append(P.add_cone(scn, "iear", (s * 0.20, -1.06, BODY_Z + 0.62), 0.11, 0.0, 0.34,
                             M["hide"], rot=(math.radians(-16), 0, math.radians(s * 24)), verts=6))
noline += [P.add_box(scn, "ieye", (s * 0.15, -1.44, BODY_Z + 0.40), (0.12, 0.06, 0.09), M["ember_h"])
           for s in (-1, 1)]

# ---- the burning mane: a ruff of bright blocks along the neck and spine.
# Emissive blocks, not modelled fur -- at this resolution a hair does not exist.
# Clustered around the NECK. Run back along the spine instead, which is where
# the first pass put them, and they read as a ridge on a bull rather than as a
# mane on a hound.
for i in range(8):
    a = math.radians(-104 + i * 30)
    noline.append(P.add_box(scn, "imane",
                            (math.sin(a) * 0.34, -0.96 + i * 0.055,
                             BODY_Z + 0.44 + math.cos(a) * 0.34),
                            (0.15, 0.13, 0.20), M["ember"] if i % 2 == 0 else M["ember_d"],
                            rot=(0, -a, 0)))
# fire licking from the jaws
noline += S.flame(scn, (0, -1.80, BODY_Z + 0.06), M["ember_h"], M["ember_d"], scale=0.85)

# ---- tail, which finishes the horizontal read at the back ----
tail_pts = [(0, 1.16, BODY_Z + 0.24), (0, 1.52, BODY_Z + 0.44), (0, 1.78, BODY_Z + 0.30)]
for i in range(len(tail_pts) - 1):
    figure.append(S.aimed_cyl(scn, "itail", tail_pts[i], tail_pts[i + 1], 0.10 - i * 0.025,
                              M["hide"], verts=6))
noline.append(P.add_box(scn, "itailfire", (0, 1.84, BODY_Z + 0.28), (0.12, 0.14, 0.16), M["ember"]))

# Turned further round than the other enemies. At the standard -30 a dog is all
# chest and no body, and the body is the entire point of the only quadruped.
I.finish(scn, px, "infernal_skirmisher", figure, detail, noline,
         role="skirmisher", facing=-62)
