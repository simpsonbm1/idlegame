"""Goblin Raid boss -- M15_ASSET_SPECS.md entry 21.

  "BOSS: the Goblin Warmaster, bigger and prouder than any common goblin,
   scavenged iron crown-helmet, patchwork cape, raising a crude war horn in one
   hand and a notched blade in the other"

"Bigger and prouder" is two separate jobs and both are silhouette work.

BIGGER is world height, since the camera is locked: 3.5 units against the
commons' 2.5 and the brute's 3.3, so he is the tallest goblin on the field
without being a different species.

PROUDER is the one goblin who is NOT hunched. Every other member of the family
leans forward; he stands upright with both arms raised, so at a glance the
faction reads as five stooping raiders around one who is not stooping. Posture
carries that further than a crown does, though he gets a crown as well.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import goblin_kit as G
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(G)

scn = P.get_scene()
px = G.start(scn, res=128)
M = G.palette()

figure, detail, noline = [], [], []

# ---- heavier legs than the commons: he is the brute's build, not the mob's ----
for s, yoff in ((-1, -0.26, ), (1, 0.24, )):
    figure.append(P.add_box(scn, "gfoot", (s * 0.46, yoff - 0.10, 0.13), (0.50, 0.68, 0.26),
                            M["skin"], bevel=0.04))
    figure.append(P.add_cyl(scn, "gshin", (s * 0.44, yoff, 0.56), 0.23, 0.72, M["skin"], verts=8))
    figure.append(P.add_box(scn, "gwrap", (s * 0.44, yoff, 0.34), (0.46, 0.46, 0.20), M["leath"]))
    figure.append(P.add_cyl(scn, "gthigh", (s * 0.40, yoff * 0.6, 1.10), 0.28, 0.66, M["skin"], verts=8))

figure.append(P.add_box(scn, "ghips", (0, 0, 1.38), (1.00, 0.62, 0.40), M["skin"], bevel=0.06))
figure.append(P.add_prism(scn, "gloin", [(-0.30, 0.28), (0.30, 0.28), (0.24, -0.60), (-0.24, -0.60)],
                          0.10, M["leath"], loc=(0.02, -0.34, 1.32)))
figure.append(P.add_box(scn, "gbelt", (0, -0.02, 1.56), (1.06, 0.66, 0.17), M["leath"]))
detail.append(P.add_box(scn, "gbuckle", (0, -0.36, 1.56), (0.18, 0.06, 0.15), M["rust"]))

# ---- UPRIGHT torso. The rest of the family is hunched; he is not, and that is
# most of what "prouder" means at sprite size.
figure.append(P.add_cyl(scn, "gwaist", (0, 0, 1.78), 0.44, 0.40, M["skin"], verts=10,
                        scale=(1.10, 0.82, 1)))
figure.append(P.add_sphere(scn, "gchest", (0, -0.06, 2.18), 0.58, M["skin"],
                           scale=(1.24, 0.84, 0.90), segs=12, rings=8))
figure.append(P.add_box(scn, "gbaldric", (0, -0.38, 2.14), (1.26, 0.10, 0.14), M["leath"],
                        rot=(0, math.radians(34), 0)))

# ---- patchwork cape: a shell behind the shoulders, standing proud so it
# outlines, with a ragged hem. Mismatched panels are the family's whole look.
figure.append(P.add_cone(scn, "gcape", (0, 0.34, 1.94), 0.86, 0.46, 1.44, M["rag"], verts=10))
detail += S.tatters(scn, (0, 0.40, 1.24), 1.34, M["leath"], count=7, drop=0.34, seed=6)
for dx, dz, w in ((-0.34, 2.10, 0.30), (0.18, 1.78, 0.26), (0.40, 2.34, 0.22)):
    detail.append(P.add_box(scn, "gpatch", (dx, 0.30, dz), (w, 0.06, w * 0.86), M["leath"]))

# ---- shoulders, one scrap pauldron, both arms RAISED ----
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "gshoulder", (s * 0.74, -0.10, 2.36), 0.34, M["skin"],
                               scale=(1, .95, .88)))
figure.append(P.add_sphere(scn, "gpauldron", (0.80, -0.12, 2.50), 0.34, M["rust"], scale=(1, 1, .62)))
figure.append(P.add_cyl(scn, "gupperL", (-0.84, -0.16, 2.60), 0.21, 0.60, M["skin"], verts=8,
                        rot=(0, math.radians(-26), 0)))
figure.append(P.add_cyl(scn, "gforeL", (-1.02, -0.28, 3.04), 0.19, 0.56, M["skin"], verts=8,
                        rot=(math.radians(-16), math.radians(-14), 0)))
figure.append(P.add_sphere(scn, "gfistL", (-1.10, -0.38, 3.32), 0.20, M["skin"]))
figure.append(P.add_cyl(scn, "gupperR", (0.84, -0.18, 2.56), 0.21, 0.58, M["skin"], verts=8,
                        rot=(0, math.radians(24), 0)))
figure.append(P.add_cyl(scn, "gforeR", (0.98, -0.34, 2.94), 0.19, 0.54, M["skin"], verts=8,
                        rot=(math.radians(-14), math.radians(16), 0)))
figure.append(P.add_sphere(scn, "gfistR", (1.04, -0.44, 3.18), 0.20, M["skin"]))

# ---- head, and the scavenged iron crown-helmet ----
figure.append(P.add_cyl(scn, "gneck", (0, 0, 2.54), 0.22, 0.20, M["skin"], verts=8))
hd_fig, hd_det = G.head(scn, M, (0, -0.02, 2.90), r=0.46)
figure += hd_fig
detail += hd_det
figure.append(P.add_cyl(scn, "ghelm", (0, -0.04, 3.24), 0.44, 0.26, M["rust"], verts=10))
for i in range(5):
    a = math.radians(-90 + (i - 2) * 33)
    figure.append(P.add_cone(scn, "gcrownspike",
                             (math.cos(a) * 0.40, math.sin(a) * 0.40 - 0.04, 3.50),
                             0.075, 0.0, 0.34, M["rust"], verts=5))
detail.append(P.add_box(scn, "ghelmrivet", (0, -0.42, 3.24), (0.44, 0.06, 0.09), M["iron"]))

# ---- war horn in the raised left hand ----
hn_root = P.make_root(scn, "horn_root", rot=(0, -34, 0), loc=(-1.14, -0.42, 3.40))
horn = [P.add_cone(scn, "ghornbody", (0, 0, 0.30), 0.09, 0.24, 0.72, M["tusk"], verts=8,
                   rot=(0, math.radians(20), 0)),
        P.add_cyl(scn, "ghornrim", (0.14, 0, 0.62), 0.25, 0.08, M["rust"], verts=8,
                  rot=(0, math.radians(20), 0)),
        P.add_cyl(scn, "ghornband", (-0.05, 0, 0.10), 0.11, 0.09, M["rust"], verts=8)]
P.parent_all(hn_root, horn)

# ---- notched blade in the raised right hand. The notches are cut from the
# SILHOUETTE, not drawn inside it: a line at this size is one pixel and vanishes.
blade = [(-0.09, 0.14), (0.09, 0.14), (0.09, 0.62), (0.02, 0.70), (0.09, 0.78),
         (0.09, 1.16), (0.01, 1.24), (0.09, 1.32), (0.06, 1.62), (-0.09, 1.44)]
bl_root = P.make_root(scn, "blade_root", rot=(0, 22, 0), loc=(1.08, -0.48, 3.26))
sword = [P.add_prism(scn, "gblade", blade, 0.12, M["rust"]),
         P.add_box(scn, "gguard", (0, 0, 0.10), (0.42, 0.12, 0.10), M["iron"]),
         P.add_box(scn, "ggrip", (0, 0, -0.12), (0.12, 0.11, 0.26), M["leath"])]
P.parent_all(bl_root, sword)

G.finish(scn, px, "goblin_boss", figure, detail, noline,
         roots=[hn_root, bl_root])
