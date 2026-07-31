"""Infernal Siege sapper -- M15_ASSET_SPECS.md entry 44.

  "a cinder imp: small, winged, soot-black with glowing ember cracks and a
   mischievous fanged grin, carrying a smoldering brazier of hot coals"

The family's smallest, and the only WINGED figure among the enemies. The wings
are what make him, and they are built as flat prisms rather than volumes: a
membrane at this size is a shape with an edge, and giving it thickness only
makes it read as a slab.

"Small" here is proportion, not height. The role system puts him at a sapper's
2.74 units like every other sapper, and the ruling that normal enemies are all
roughly one size is the reason. So he is small the way a child is small -- an
oversized head, stubby limbs and a short body -- rather than by being a
correctly proportioned figure scaled down, which just reads as a distant adult.
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

# ---- stubby legs. Short limbs against a big head is what reads as small. ----
for s, yoff in ((-1, -0.20), (1, 0.18)):
    figure.append(P.add_box(scn, "ifoot", (s * 0.26, yoff - 0.10, 0.10), (0.30, 0.42, 0.20),
                            M["horn"], bevel=0.03))
    figure.append(P.add_cyl(scn, "ishin", (s * 0.25, yoff, 0.36), 0.115, 0.42, M["hide"], verts=8))
    figure.append(P.add_cyl(scn, "ithigh", (s * 0.24, yoff * 0.6, 0.72), 0.135, 0.36, M["hide"], verts=8))

figure.append(P.add_box(scn, "ihips", (0, 0, 0.94), (0.56, 0.40, 0.26), M["hide"], bevel=0.04))
figure.append(P.add_sphere(scn, "ibelly", (0, -0.06, 1.26), 0.36, M["hide"],
                           scale=(1.14, 0.86, 0.96), segs=12, rings=8))
noline += I.cracks(scn, M, [(-0.14, -0.34, 1.24, 0.20), (0.16, -0.34, 1.10, 0.16)])

# ---- the oversized head, which is most of the "small" ----
figure.append(P.add_sphere(scn, "iskull", (0, -0.04, 1.86), 0.40, M["hide"],
                           scale=(1.04, 1.0, 0.94), segs=12, rings=8))
figure.append(P.add_box(scn, "ijaw", (0, -0.34, 1.66), (0.56, 0.42, 0.26), M["hide"], bevel=0.05))
# the grin: a bright band with fangs, which is his whole expression at this size
detail.append(P.add_box(scn, "igrin", (0, -0.54, 1.62), (0.44, 0.06, 0.09), M["bone"]))
for s in (-1, 1):
    detail.append(P.add_cone(scn, "ifang", (s * 0.14, -0.54, 1.54), 0.05, 0.0, 0.16, M["bone"],
                             rot=(math.radians(180), 0, 0), verts=5))
    figure.append(P.add_cone(scn, "iear", (s * 0.40, 0.02, 1.96), 0.13, 0.0, 0.44, M["hide"],
                             rot=(0, math.radians(s * 62), 0), verts=6))
figure += I.horns(scn, M, (0, -0.02, 1.98), r=0.34, curl=2, sweep=36, length=0.24)
noline += [P.add_box(scn, "ieye", (s * 0.15, -0.40, 1.90), (0.14, 0.06, 0.10), M["ember_h"])
           for s in (-1, 1)]

# ---- the wings: flat prisms, because a membrane is a shape with an edge and
# giving it thickness only makes it read as a slab.
wing = [(0.0, 0.0), (0.34, 0.46), (0.72, 0.60), (0.62, 0.30), (0.86, 0.24),
        (0.66, 0.02), (0.80, -0.24), (0.50, -0.16), (0.42, -0.44), (0.20, -0.14)]
for s in (-1, 1):
    wr = P.make_root(scn, "wing%d_root" % (s + 2), rot=(0, 0, s * 26), loc=(s * 0.30, 0.30, 1.48))
    parts = [P.add_prism(scn, "iwing", [(x * s, z) for x, z in wing], 0.05, M["hide"],
                         loc=(0, 0, 0))]
    for i, (ax, az) in enumerate(((0.30, 0.38), (0.56, 0.20), (0.44, -0.16))):
        parts.append(S.aimed_cyl(scn, "iwingrib", (0, 0, 0), (ax * s, 0, az), 0.035,
                                 M["horn"], verts=4))
    P.parent_all(wr, parts)
    figure.append(wr)

# ---- short arms, both under the brazier ----
figure += I.clawed_limb(scn, M, (-0.38, -0.10, 1.42), (-0.42, -0.48, 1.10),
                        upper_r=0.105, fore_r=0.095)
figure += I.clawed_limb(scn, M, (0.38, -0.10, 1.44), (0.42, -0.48, 1.12),
                        upper_r=0.105, fore_r=0.095)

# ---- the smouldering brazier of coals ----
bz_root = P.make_root(scn, "brazier_root", loc=(0, -0.62, 1.12))
brazier = [P.add_cone(scn, "ibowl", (0, 0, 0.06), 0.16, 0.30, 0.24, M["iron"], verts=10),
           P.add_cyl(scn, "ibrazrim", (0, 0, 0.19), 0.31, 0.06, M["brass"], verts=10),
           P.add_cyl(scn, "ibrazfoot", (0, 0, -0.09), 0.13, 0.06, M["iron"], verts=8)]
coals = [P.add_cyl(scn, "icoals", (0, 0, 0.22), 0.26, 0.05, M["ember"], verts=10)]
coals += S.flame(scn, (0, -0.02, 0.30), M["ember_h"], M["ember_d"], scale=0.62)
for dx, dy in ((-0.13, -0.05), (0.11, 0.04)):
    coals.append(P.add_sphere(scn, "icoal", (dx, dy, 0.25), 0.06, M["ember_d"], segs=8, rings=5))
P.parent_all(bz_root, brazier + coals)

I.finish(scn, px, "infernal_sapper", figure, detail, noline, roots=[bz_root],
         skip_extra=tuple(o.name for o in coals), role="sapper")
