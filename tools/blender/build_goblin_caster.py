"""Goblin Raid caster -- M15_ASSET_SPECS.md entry 18.

  "a goblin slinger whirling a leather sling with a stone, pouch of pebbles at
   the hip"

The family's ranged unit, and the odd one in the whole roster: every other caster
across five factions holds a staff, and this one is a goblin with a bit of string.
That is an advantage rather than a problem, because the WHIRLING SLING is a shape
no other sprite in the game has -- a loop above the head, which breaks the top of
his cell and identifies him instantly from across a battlefield.

The sling is a ring of short segments rather than a torus, because a torus at
this size is either invisible or a blob, and a ring of six blocks reads as a
circle the moment the outline draws between them.
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
px = G.start(scn, res=112)
M = G.palette()

figure, detail, noline = [], [], []

HIP = 1.06
figure += G.wiry_legs(scn, M, HIP, spread=0.30)
figure.append(P.add_box(scn, "ghips", (0, 0, HIP), (0.64, 0.44, 0.28), M["skin"], bevel=0.05))
figure.append(P.add_prism(scn, "gloin", [(-0.20, 0.20), (0.20, 0.20), (0.16, -0.42), (-0.16, -0.42)],
                          0.09, M["leath"], loc=(0.02, -0.26, 1.02)))

# ---- a shallower hunch than the skulker: he is throwing, not creeping ----
tors_root, tors = G.hunch(scn, M, HIP + 0.14, chest_r=0.30, lean=12)
tors.append(P.add_box(scn, "gbelt", (0, -0.02, 0.14), (0.68, 0.48, 0.12), M["leath"]))

hd_fig, hd_det = G.head(scn, M, (0, -0.04, 0.92), r=0.27)
tors += hd_fig
tors.append(P.add_box(scn, "gcap", (0, -0.02, 1.14), (0.46, 0.42, 0.14), M["rag"]))

# arms: the sling arm up and back, the other counterweighting forward
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "gshoulder", (s * 0.36, -0.06, 0.62), 0.17, M["skin"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "gupperL", (-0.44, -0.10, 0.80), 0.125, 0.46, M["skin"], verts=8,
                      rot=(0, math.radians(-34), 0)))
tors.append(P.add_cyl(scn, "gforeL", (-0.62, -0.16, 1.14), 0.11, 0.44, M["skin"], verts=8,
                      rot=(0, math.radians(-22), 0)))
tors.append(P.add_sphere(scn, "gfistL", (-0.70, -0.20, 1.36), 0.14, M["skin"]))
tors.append(P.add_cyl(scn, "gupperR", (0.44, -0.20, 0.52), 0.125, 0.44, M["skin"], verts=8,
                      rot=(0, math.radians(22), 0)))
tors.append(P.add_cyl(scn, "gforeR", (0.56, -0.48, 0.40), 0.11, 0.44, M["skin"], verts=8,
                      rot=(math.radians(40), math.radians(16), 0)))
tors.append(P.add_sphere(scn, "gfistR", (0.60, -0.62, 0.24), 0.14, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- pouch of pebbles at the hip ----
figure.append(P.add_box(scn, "gpouch", (0.40, -0.32, 1.04), (0.28, 0.24, 0.30), M["leath"], bevel=0.04))
detail.append(P.add_box(scn, "gpouchflap", (0.40, -0.36, 1.18), (0.30, 0.20, 0.10), M["rag"]))

# ---- the whirling sling: a closed loop above and behind the raised hand.
#
# **A ring has to be built from segments that TOUCH.** The first pass placed six
# small blocks on a circle and they rendered as six unrelated dots: at this scale
# each block was two pixels and the gaps between them were six, so there was no
# loop for the eye to close. Sixteen segments joined end to end by `aimed_cyl`
# make an actual ring, and the whole thing is only about twenty pixels across.
sl_root = P.make_root(scn, "sling_root", rot=(0, 14, 0), loc=(-0.80, -0.08, 2.04))
sling = []
R, N = 0.34, 16
pts = [(math.cos(math.radians(i * 360.0 / N)) * R, 0.0,
        math.sin(math.radians(i * 360.0 / N)) * R) for i in range(N)]
for i in range(N):
    sling.append(S.aimed_cyl(scn, "slingcord", pts[i], pts[(i + 1) % N], 0.028, M["leath"], verts=4))
sling.append(P.add_box(scn, "slingpouch", (R * 0.96, -0.05, -R * 0.34), (0.19, 0.11, 0.16), M["leath"]))
stone = [P.add_sphere(scn, "slingstone", (R * 1.00, -0.09, -R * 0.34), 0.09, M["iron"], segs=8, rings=5)]
# the two cords running down from the loop to the hand
sling.append(S.aimed_cyl(scn, "cordA", (-0.16, 0.0, -R), (-0.02, 0.0, -0.74), 0.026, M["leath"], verts=4))
sling.append(S.aimed_cyl(scn, "cordB", (0.14, 0.0, -R * 0.92), (0.04, 0.0, -0.74), 0.026, M["leath"], verts=4))
P.parent_all(sl_root, sling + stone)

G.finish(scn, px, "goblin_caster", figure, detail, noline,
         roots=[tors_root, sl_root],
         skip_extra=tuple(o.name for o in hd_det), role="caster", body_roots=[tors_root])
