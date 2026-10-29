"""Undead Legion sapper -- M15_ASSET_SPECS.md entry 38.

  "a grave digger, a hunched skeleton in a ragged hood, worn shovel over one
   shoulder, lantern glowing pale green at the belt"

The family's small one. Every other undead entry stands upright, so his read is
POSTURE: a forward hunch that shortens him and throws the shovel handle across
the diagonal of the cell. Two figures of the same height can still be told apart
instantly if one of them is bent.

He is also the only entry with a second light source. The lantern is green where
everything else in the faction is teal, which is deliberate -- one warm-ish point
low on the body stops the six of them reading as a single teal wash when they
stand in a formation together.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import undead_kit as U
import pixelrig as P
importlib.reload(P)
importlib.reload(U)

scn = P.get_scene()
px = U.start(scn, res=112)
M = U.palette()

figure, detail, noline = [], [], []

# ---- bare bone legs, bent, one forward ----
for s, yoff, zoff in ((-1, -0.24, 0.0), (1, 0.22, 0.02)):
    figure.append(P.add_box(scn, "footbone", (s * 0.33, yoff - 0.10, 0.09), (0.32, 0.54, 0.18), M["bone"], bevel=0.03))
    figure.append(P.add_cyl(scn, "tibia", (s * 0.31, yoff, 0.42 + zoff), 0.085, 0.54, M["bone"], verts=6))
    figure.append(P.add_sphere(scn, "knee", (s * 0.31, yoff - 0.10, 0.72 + zoff), 0.115, M["bone"]))
    figure.append(P.add_cyl(scn, "femur", (s * 0.29, yoff * 0.6, 1.02), 0.095, 0.56, M["bone"], verts=6,
                            rot=(math.radians(s * 5), 0, 0)))

figure.append(P.add_box(scn, "pelvis", (0, 0, 1.32), (0.62, 0.44, 0.30), M["bone"], bevel=0.05))

# ---- the hunch: torso pitched forward, which is his whole silhouette ----
tors_root = P.make_root(scn, "torso_root", rot=(-22, 0, 0), loc=(0, 0, 1.44))
tors = U.ribcage(scn, M, (0, -0.10, 0.34), width=0.56, height=0.62, ribs=4)
tors.append(P.add_cone(scn, "hoodrag", (0, 0.10, 0.42), 0.52, 0.30, 0.86, M["rag"], verts=10))
tors.append(P.add_sphere(scn, "shoulderL", (-0.38, -0.02, 0.66), 0.16, M["bone"]))
tors.append(P.add_sphere(scn, "shoulderR", (0.38, -0.02, 0.68), 0.16, M["bone"]))

# skull inside the hood, tipped down the way a digger's would be
sk_fig, sk_det, sk_nol = U.skull(scn, M, (0, -0.16, 0.98), radius=0.22, eye=M["green"])
tors += sk_fig
tors.append(P.add_cone(scn, "hood", (0, 0.04, 1.10), 0.36, 0.12, 0.50, M["rag"], verts=10))

# arms: one up holding the shovel over the shoulder, one hanging
tors += U.bone_arm(scn, M, (-0.38, -0.10, 0.62), (-0.50, -0.42, 0.92))
tors += U.bone_arm(scn, M, (0.38, -0.10, 0.62), (0.48, -0.44, 0.18))

P.parent_all(tors_root, tors + sk_det + sk_nol)

# ---- worn shovel: own root, a digger leaning on it, blade in the dirt ahead ----
# **The hand holds the GRIP, not the blade.** This root used to sit at his raised
# hand with the blade at the root end, so he held the shovel by its blade and the
# T-grip rested on the floor in front of him: "holding his weapon at the wrong end"
# (user, 2026-10-29). Measured before the fix, his hand was at world z 2.39 beside
# the blade at 2.43 and the grip was down at 0.73.
#
# The root is the BLADE end (local z 0) and the grip is at local z 1.74, so the
# root is placed SHOVEL_HOLD down the shaft from the hand, which puts the hand just
# under the T-grip. The hand's position here is its torso-local (-0.50, -0.42,
# 0.92) carried through the torso's 22-degree hunch, so moving the arm means
# moving this too. Depth is the fist's own, a touch nearer the camera so the shaft
# reads as IN the hand; it used to sit 0.44 in front of it.
SHOVEL_HOLD = 1.58
_hand = (-0.50, -0.42 * math.cos(math.radians(22)) + 0.92 * math.sin(math.radians(22)),
         1.44 + 0.42 * math.sin(math.radians(22)) + 0.92 * math.cos(math.radians(22)))
_up = (math.sin(math.radians(28)), math.cos(math.radians(28)))   # blade-to-grip, in x and z
sh_root = P.make_root(scn, "shovel_root", rot=(0, 28, 0),
                      loc=(_hand[0] - SHOVEL_HOLD * _up[0], _hand[1] - 0.08,
                           _hand[2] - SHOVEL_HOLD * _up[1]))
blade_pts = [(-0.21, 0.0), (0.21, 0.0), (0.23, -0.30), (0.13, -0.46), (-0.13, -0.46), (-0.23, -0.30)]
shovel = [P.add_cyl(scn, "handle", (0, 0, 0.86), 0.048, 1.72, M["wood"], verts=6),
          P.add_prism(scn, "shovelblade", blade_pts, 0.06, M["iron"]),
          P.add_box(scn, "collar", (0, 0, 0.10), (0.13, 0.09, 0.13), M["iron"]),
          P.add_box(scn, "grip", (0, 0, 1.74), (0.20, 0.09, 0.09), M["wood"])]
P.parent_all(sh_root, shovel)

# ---- lantern at the belt: own root, hanging straight down ----
ln_root = P.make_root(scn, "lantern_root", loc=(0.46, -0.46, 1.30))
lantern = [P.add_cyl(scn, "lanterncap", (0, 0, 0.16), 0.13, 0.08, M["iron"], verts=8),
           P.add_box(scn, "lanternbody", (0, 0, -0.02), (0.19, 0.19, 0.28), M["iron"]),
           P.add_cyl(scn, "lanternbase", (0, 0, -0.19), 0.13, 0.07, M["iron"], verts=8),
           P.add_box(scn, "bail", (0, 0, 0.24), (0.15, 0.04, 0.05), M["iron"])]
glass = [P.add_box(scn, "lanternglass", (0, -0.09, -0.02), (0.13, 0.05, 0.20), M["green"]),
         P.add_sphere(scn, "lanternhalo", (0, -0.13, -0.02), 0.10, M["green_d"], segs=8, rings=5)]
P.parent_all(ln_root, lantern + glass)

U.finish(scn, px, "undead_sapper", figure, detail, noline,
         roots=[tors_root, sh_root, ln_root],
         skip_extra=tuple(o.name for o in sk_det + sk_nol + glass), role="sapper", body_roots=[tors_root])
