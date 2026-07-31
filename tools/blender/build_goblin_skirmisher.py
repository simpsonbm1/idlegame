"""Goblin Raid skirmisher -- M15_ASSET_SPECS.md entry 17.

  "a goblin skulker hunched under a ragged dark hood, clutching two crude daggers"

The family's small fast one. He is the deepest hunch in the set, which is what
separates him from the slinger standing beside him at the same height: both are
2.5 units tall, and only one of them is folded over.

Two daggers held low and forward. Low matters -- the reaver in the Undead Legion
holds his blades out wide, and if this one did too the two skirmishers would read
as the same pose in two palettes.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import goblin_kit as G
import pixelrig as P
importlib.reload(P)
importlib.reload(G)

scn = P.get_scene()
px = G.start(scn, res=96)
M = G.palette()

figure, detail, noline = [], [], []

HIP = 1.02
figure += G.wiry_legs(scn, M, HIP, spread=0.28)
figure.append(P.add_box(scn, "ghips", (0, 0, HIP), (0.64, 0.44, 0.28), M["skin"], bevel=0.05))
figure.append(P.add_prism(scn, "gloin", [(-0.20, 0.20), (0.20, 0.20), (0.16, -0.44), (-0.16, -0.44)],
                          0.09, M["leath"], loc=(0.02, -0.26, 0.98)))

# ---- the deepest hunch in the family, which is his read against the slinger ----
tors_root, tors = G.hunch(scn, M, HIP + 0.14, chest_r=0.30, lean=21)
tors.append(P.add_box(scn, "gbelt", (0, -0.02, 0.16), (0.66, 0.46, 0.12), M["leath"]))

# Hood over the head. **It has to be bigger than the head and set BACK.** The
# first pass sized it to just clear the skull, so the face filled it exactly and
# the hood rendered entirely behind the head -- he came out bare-headed. A hood
# is only visible as the margin around a face, so that margin has to exist.
hd_fig, hd_det = G.head(scn, M, (0, -0.02, 0.84), r=0.24, ears=True, tusks=True)
tors += hd_fig
tors.append(P.add_cone(scn, "ghood", (0, 0.12, 0.96), 0.42, 0.13, 0.56, M["rag"], verts=10))
tors.append(P.add_sphere(scn, "ghoodback", (0, 0.16, 0.84), 0.30, M["rag"],
                         scale=(1.0, 0.9, 1.0), segs=10, rings=6))
tors.append(P.add_cone(scn, "gcowl", (0, 0.08, 0.50), 0.42, 0.26, 0.36, M["rag"], verts=10))
# the brow shadow that turns the opening into a face rather than a hole
tors.append(P.add_box(scn, "ghoodbrow", (0, -0.22, 0.98), (0.40, 0.10, 0.10), M["rag"]))

# arms tucked in and low, elbows out
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "gshoulder", (s * 0.36, -0.06, 0.56), 0.17, M["skin"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "gupperL", (-0.42, -0.18, 0.34), 0.125, 0.44, M["skin"], verts=8,
                      rot=(0, math.radians(-12), 0)))
tors.append(P.add_cyl(scn, "gforeL", (-0.48, -0.44, 0.08), 0.11, 0.44, M["skin"], verts=8,
                      rot=(math.radians(48), 0, 0)))
tors.append(P.add_sphere(scn, "gfistL", (-0.50, -0.60, -0.10), 0.14, M["skin"]))
tors.append(P.add_cyl(scn, "gupperR", (0.42, -0.18, 0.36), 0.125, 0.42, M["skin"], verts=8,
                      rot=(0, math.radians(14), 0)))
tors.append(P.add_cyl(scn, "gforeR", (0.46, -0.46, 0.16), 0.11, 0.42, M["skin"], verts=8,
                      rot=(math.radians(56), 0, 0)))
tors.append(P.add_sphere(scn, "gfistR", (0.46, -0.62, 0.00), 0.14, M["skin"]))

# ---- two crude daggers, held low. Short and straight, against the reaver's long
# curves, so the two skirmishers do not share a silhouette.
#
# **Their roots parent to the TORSO root, in torso-local coordinates.** The first
# pass parented them to the figure root and gave them figure-space positions, so
# they sat where the fists would have been if the goblin were standing straight
# and floated well below the hunched ones he actually has. Anything held by a
# hand belongs to whatever root moves that hand.
dag = [(-0.05, 0.0), (0.05, 0.0), (0.07, 0.36), (0.0, 0.50), (-0.07, 0.36)]
dagger_roots = []
for name, rot, loc in (("dagL_root", (0, 112, 0), (-0.56, -0.70, -0.06)),
                       ("dagR_root", (0, 68, 0), (0.52, -0.72, 0.06))):
    dr = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(dr, [P.add_prism(scn, "dagblade", dag, 0.055, M["rust"]),
                      P.add_box(scn, "daggrip", (0, 0, -0.12), (0.075, 0.075, 0.22), M["leath"]),
                      P.add_box(scn, "dagguard", (0, 0, 0.03), (0.19, 0.09, 0.055), M["iron"])])
    dagger_roots.append(dr)

P.parent_all(tors_root, tors + hd_det + dagger_roots)

G.finish(scn, px, "goblin_skirmisher", figure, detail, noline,
         roots=[tors_root],
         skip_extra=tuple(o.name for o in hd_det))
