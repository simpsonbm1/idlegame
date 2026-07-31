"""Infernal Siege caster -- M15_ASSET_SPECS.md entry 42.

  "a demon flamecaller in charred dark robes, crimson skin and small curved
   horns, conjuring a sweeping arc of hellfire between clawed hands"

The arc between the hands is the entry, and it is a different problem from the
orc warcaster's thrown bolt. That one runs OUTWARD in a line and grows. This one
is a closed curve held between two hands, so it is built the way the goblin
slinger's loop is: a chain of segments that touch. Blobs with gaps between them
would read as beads, not as fire.

He is the only infernal with CRIMSON skin rather than charcoal, which the spec
asks for and which also gives the family one mid-value figure. Five near-black
figures in a row would flatten the whole faction.
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

# ---- charred robe to the ground: a cone, the cheapest lower body in the rig ----
figure.append(P.add_cone(scn, "irobe", (0, 0, 0.86), 0.84, 0.42, 1.72, M["robe"], verts=12))
detail += S.tatters(scn, (0, -0.44, 0.14), 1.26, M["hide"], count=7, drop=0.30, seed=4)
figure.append(P.add_cone(scn, "ichest", (0, 0, 2.06), 0.44, 0.38, 0.90, M["robe"], verts=12))
figure.append(P.add_box(scn, "isash", (0, -0.42, 1.66), (0.60, 0.09, 0.14), M["brass"]))
noline += I.cracks(scn, M, [(-0.24, -0.44, 1.20, 0.28), (0.22, -0.44, 0.86, 0.22)], hot=False)

# ---- crimson skin: the family's one mid-value figure ----
figure.append(P.add_cone(scn, "imantle", (0, -0.02, 2.52), 0.66, 0.28, 0.44, M["hide"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "ishoulder", (s * 0.48, -0.04, 2.42), 0.23, M["crim"],
                               scale=(1, .95, .8)))
figure.append(P.add_sphere(scn, "iskull", (0, -0.06, 2.86), 0.26, M["crim"],
                           scale=(0.96, 1.0, 1.06), segs=10, rings=7))
figure.append(P.add_box(scn, "ijaw", (0, -0.28, 2.68), (0.34, 0.28, 0.18), M["crim"], bevel=0.04))
detail.append(P.add_box(scn, "ifangs", (0, -0.42, 2.62), (0.26, 0.05, 0.05), M["bone"]))
figure += I.horns(scn, M, (0, -0.06, 2.92), r=0.26, curl=2, sweep=38, length=0.26)
noline += [P.add_box(scn, "ieye", (s * 0.10, -0.30, 2.90), (0.09, 0.05, 0.07), M["ember_h"])
           for s in (-1, 1)]

# ---- both arms forward and apart, palms turned in toward the arc ----
figure += I.clawed_limb(scn, M, (-0.50, -0.12, 2.34), (-0.74, -0.62, 1.88),
                        upper_r=0.13, fore_r=0.115)
figure += I.clawed_limb(scn, M, (0.50, -0.12, 2.36), (0.74, -0.62, 2.24),
                        upper_r=0.13, fore_r=0.115)

# ---- the sweeping arc of hellfire, hand to hand.
# A chain of TOUCHING segments, the same construction the goblin slinger's loop
# needed. Separate blobs on a curve render as beads with gaps, not as fire.
A = (-0.80, -0.78, 1.86)
Bp = (0.80, -0.78, 2.26)
N = 9
pts = []
for i in range(N + 1):
    t = i / float(N)
    x = A[0] + (Bp[0] - A[0]) * t
    y = A[1] + (Bp[1] - A[1]) * t
    z = A[2] + (Bp[2] - A[2]) * t - math.sin(math.pi * t) * 0.62   # bows downward
    pts.append((x, y, z))
for i in range(N):
    noline.append(S.aimed_cyl(scn, "iarc", pts[i], pts[i + 1], 0.075,
                              M["ember_h"] if 2 <= i <= 6 else M["ember"], verts=5))
# a few sparks thrown off the arc, so it is not a clean drawn curve
for dx, dy, dz, r in ((-0.30, -0.84, 1.44, 0.075), (0.22, -0.84, 1.40, 0.06),
                      (0.56, -0.84, 1.76, 0.05)):
    noline.append(P.add_sphere(scn, "ispark", (dx, dy, dz), r, M["ember_d"], segs=8, rings=5))

I.finish(scn, px, "infernal_caster", figure, detail, noline, role="caster")
