"""Alchemist -- M15_ASSET_SPECS.md entry 14.

  "an alchemist in a green apron, brass goggles pushed up on the forehead, holding
   up a bubbling glass flask of luminous green liquid"

The only townsperson holding something that GLOWS, and the flask is raised to
head height so the light sits beside his face rather than at his hip.

The goggles are pushed up onto the forehead rather than worn, which is a
stronger read: two brass discs above the eyes leave the face open, and an open
face is what marks everyone on the player's side of the wall.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import townsfolk_kit as T
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(T)

scn = P.get_scene()
px = T.start(scn, res=112)
M = T.palette()

figure, detail, noline = [], [], []

HIP = 1.16
figure += T.legs(scn, M, HIP, spread=0.33, mat=M["wool"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.78, 0.50, 0.28), M["wool"], bevel=0.05))

tors_root, tors = T.torso(scn, M, HIP + 0.14, chest_r=0.43, lean=6, mat=M["linen"])
tors.append(P.add_box(scn, "apron", (0, -0.40, 0.24), (0.78, 0.10, 1.08), M["green"]))
tors.append(P.add_box(scn, "apronstrap", (0, -0.34, 0.78), (0.42, 0.09, 0.12), M["green"]))
tors.append(P.add_box(scn, "belt", (0, -0.04, -0.04), (0.88, 0.56, 0.14), M["leath"]))
# small vials in a chest loop, staggered so they are not a printed row
for i, dx in enumerate((-0.30, -0.08, 0.16)):
    tors.append(P.add_cyl(scn, "vial", (dx, -0.36, 0.50 + (i % 2) * 0.09), 0.055, 0.20,
                          M["white"], verts=6))

hd, hd_det = T.head(scn, M, (0, -0.04, 1.02), r=0.29)
tors += hd
# goggles pushed up on the forehead: two brass discs ABOVE the eyes, so the face
# stays open
for s in (-1, 1):
    tors.append(P.add_cyl(scn, "goggle", (s * 0.13, -0.22, 1.26), 0.11, 0.09, M["brass"],
                          verts=8, rot=(math.radians(90), 0, 0)))
tors.append(P.add_box(scn, "gogglestrap", (0, 0.02, 1.24), (0.60, 0.44, 0.09), M["leath"]))

lh, rh = T.relaxed_arms(scn, M, tors, shoulder_z=0.66, spread=0.50, sleeve=M["linen"],
                        right_hand=(0.62, -0.50, 0.90))
P.parent_all(tors_root, tors + hd_det)

# the bubbling flask, raised beside the face
fl_root = P.make_root(scn, "flask_root", loc=(0.64, -0.56, 2.06))
flask = [P.add_cone(scn, "flask", (0, 0, 0), 0.20, 0.07, 0.34, M["white"], verts=10),
         P.add_cyl(scn, "flaskneck", (0, 0, 0.22), 0.05, 0.14, M["white"], verts=6),
         P.add_cyl(scn, "flaskcork", (0, 0, 0.31), 0.055, 0.07, M["wood"], verts=6)]
brew = [P.add_cone(scn, "brew", (0, 0, -0.04), 0.16, 0.06, 0.20, M["tonic"], verts=10)]
for i, (dx, dz) in enumerate(((-0.04, 0.16), (0.05, 0.24), (0.0, 0.34))):
    brew.append(P.add_sphere(scn, "bubble", (dx, -0.02, dz), 0.045 - i * 0.008, M["tonic"],
                             segs=8, rings=5))
P.parent_all(fl_root, flask + brew)

T.finish(scn, px, "town_alchemist", figure, detail, noline,
         roots=[tors_root, fl_root],
         skip_extra=tuple(o.name for o in hd_det + brew),
         body_roots=[tors_root])
