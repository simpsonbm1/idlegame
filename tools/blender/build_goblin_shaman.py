"""Goblin Raid shaman -- M15_ASSET_SPECS.md entry 19.

  "a goblin shaman in a bone-and-feather headdress, gnarled totem staff with a
   glowing green charm"

The headdress is the entry. Feathers give him the one thing no other goblin has
-- an irregular, spiky top edge -- and at 96 pixels a broken outline is worth
more than any facial detail underneath it.

The staff is deliberately GNARLED rather than straight: a stack of short segments
each kicked a few degrees off the last. Every other staff in the roster is a
clean shaft, so the crookedness is what says these are scavengers rather than
scholars.
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
px = G.start(scn, res=112)
M = G.palette()

figure, detail, noline = [], [], []

HIP = 1.04
figure += G.wiry_legs(scn, M, HIP, spread=0.29)
figure.append(P.add_box(scn, "ghips", (0, 0, HIP), (0.62, 0.44, 0.28), M["skin"], bevel=0.05))
figure.append(P.add_prism(scn, "gskirt", [(-0.26, 0.22), (0.26, 0.22), (0.20, -0.50), (-0.20, -0.50)],
                          0.10, M["rag"], loc=(0.02, -0.24, 1.00)))

tors_root, tors = G.hunch(scn, M, HIP + 0.14, chest_r=0.29, lean=16)
tors.append(P.add_box(scn, "gbelt", (0, -0.02, 0.14), (0.66, 0.48, 0.12), M["leath"]))
# bone charms strung across the chest, staggered so they do not read as a row
for dx, dz in ((-0.18, 0.44), (0.02, 0.36), (0.20, 0.46)):
    tors.append(P.add_box(scn, "gcharm", (dx, -0.30, dz), (0.06, 0.05, 0.16), M["bone"]))

hd_fig, hd_det = G.head(scn, M, (0, -0.04, 0.90), r=0.27)
tors += hd_fig

# ---- the headdress: a bone band, then feathers fanned back and up. Their tips
# are what break his outline, so they are figure parts and get outlined.
tors.append(P.add_cyl(scn, "gband", (0, -0.06, 1.10), 0.29, 0.11, M["bone"], verts=10))
for i, s in enumerate((-2, -1, 0, 1, 2)):
    lean = 26 + abs(s) * 9
    tors.append(P.add_cone(scn, "gfeather", (s * 0.13, 0.10 + abs(s) * 0.02, 1.34),
                           0.055, 0.012, 0.42 + (2 - abs(s)) * 0.10,
                           M["rag"] if i % 2 else M["tusk"],
                           rot=(math.radians(lean), 0, math.radians(s * 11)), verts=5))

# arms: staff hand forward, free hand raised with the charm's light on it
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "gshoulder", (s * 0.35, -0.06, 0.58), 0.16, M["skin"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "gupperL", (-0.42, -0.18, 0.36), 0.12, 0.44, M["skin"], verts=8))
tors.append(P.add_cyl(scn, "gforeL", (-0.48, -0.44, 0.10), 0.105, 0.42, M["skin"], verts=8,
                      rot=(math.radians(44), 0, 0)))
tors.append(P.add_sphere(scn, "gfistL", (-0.50, -0.58, -0.06), 0.135, M["skin"]))
tors.append(P.add_cyl(scn, "gupperR", (0.42, -0.16, 0.56), 0.12, 0.42, M["skin"], verts=8,
                      rot=(0, math.radians(20), 0)))
tors.append(P.add_cyl(scn, "gforeR", (0.52, -0.38, 0.80), 0.105, 0.42, M["skin"], verts=8,
                      rot=(math.radians(-40), math.radians(12), 0)))
tors.append(P.add_sphere(scn, "gfistR", (0.56, -0.48, 1.02), 0.135, M["skin"]))

P.parent_all(tors_root, tors + hd_det)

# ---- gnarled totem staff: segments kicked off each other, not one shaft ----
st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.56, -0.62, 1.10))
staff = []
z, x, ang = -0.42, 0.0, 0.0
for i in range(7):
    ang = (14 if i % 2 else -11) + (4 if i == 3 else 0)
    staff.append(P.add_cyl(scn, "gknot", (x, 0, z), 0.052, 0.30, M["wood"], verts=6,
                           rot=(0, math.radians(ang), 0)))
    x += math.sin(math.radians(ang)) * 0.30
    z += 0.29
# lashings and a small skull totem below the charm
for zz in (-0.12, 0.46, 1.04):
    staff.append(P.add_cyl(scn, "glash", (0, 0, zz), 0.07, 0.07, M["leath"], verts=6))
staff.append(P.add_sphere(scn, "gtotem", (x * 0.9, -0.05, z - 0.16), 0.13, M["bone"],
                          scale=(1, 1.02, 1.08), segs=8, rings=6))
for s in (-1, 1):
    staff.append(P.add_cone(scn, "gprong", (x * 0.9 + s * 0.11, 0, z + 0.06), 0.035, 0.0, 0.22,
                            M["wood"], rot=(0, math.radians(s * 30), 0), verts=5))
glow = [P.add_sphere(scn, "gcharmcore", (x * 0.9, -0.06, z + 0.18), 0.10, M["green"], segs=8, rings=5),
        P.add_sphere(scn, "gcharmhalo", (x * 0.9, -0.08, z + 0.30), 0.06, M["green_d"], segs=8, rings=5)]
P.parent_all(st_root, staff + glow)

G.finish(scn, px, "goblin_shaman", figure, detail, noline,
         roots=[tors_root, st_root],
         skip_extra=tuple(o.name for o in hd_det + glow), role="shaman", body_roots=[tors_root])
