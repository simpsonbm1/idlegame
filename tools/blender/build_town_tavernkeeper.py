"""Tavernkeeper -- M15_ASSET_SPECS.md entry 10.

  "a stout jolly tavernkeeper, apron over rolled-up sleeves, foaming mug in one
   hand, cleaning rag in the other"

The only STOUT figure among the townsfolk, and the widest waist in the game. The
size ruling fixes his height at everyone else's, so his build is the whole
difference and it has to be carried entirely by width.

The foaming mug is a small object with a bright cap on it. Foam is the only
white in his palette, which is what stops the mug reading as a fist.
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
figure += T.legs(scn, M, HIP, spread=0.38, mat=M["wool"], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.94, 0.58, 0.30), M["wool"], bevel=0.05))

tors_root, tors = T.torso(scn, M, HIP + 0.14, chest_r=0.54, lean=3, mat=M["linen"])
tors.append(P.add_cyl(scn, "belly", (0, -0.06, 0.30), 0.50, 0.52, M["linen"], verts=12,
                      scale=(1.12, 0.88, 1)))
tors.append(P.add_box(scn, "apron", (0, -0.42, 0.22), (0.78, 0.09, 1.00), M["apron"]))
tors.append(P.add_box(scn, "apronstrap", (0, -0.36, 0.76), (0.42, 0.09, 0.12), M["apron"]))
tors.append(P.add_box(scn, "belt", (0, -0.04, -0.10), (1.02, 0.62, 0.15), M["leath"]))

hd, hd_det = T.head(scn, M, (0, -0.04, 1.04), r=0.30)
tors += hd
detail.append(P.add_box(scn, "moustache", (0, -0.32, 2.16), (0.34, 0.06, 0.09), M["wool"]))

lh, rh = T.relaxed_arms(scn, M, tors, shoulder_z=0.70, spread=0.56, sleeve=M["linen"],
                        left_hand=(-0.62, -0.58, 0.14), right_hand=(0.60, -0.58, 0.06))
P.parent_all(tors_root, tors + hd_det)

# the foaming mug
mg_root = P.make_root(scn, "mug_root", loc=(-0.64, -0.64, 1.42))
mug = [P.add_cyl(scn, "mug", (0, 0, 0), 0.16, 0.32, M["wood"], verts=8),
       P.add_cyl(scn, "mugband", (0, 0, -0.10), 0.17, 0.06, M["iron"], verts=8),
       P.add_box(scn, "mughandle", (0.19, 0, 0), (0.09, 0.06, 0.20), M["wood"])]
foam = [P.add_cyl(scn, "foam", (0, 0, 0.19), 0.17, 0.09, M["white"], verts=8),
        P.add_sphere(scn, "foamblob", (0.05, -0.03, 0.25), 0.08, M["white"], segs=8, rings=5)]
P.parent_all(mg_root, mug + foam)

# the cleaning rag, hanging from the other hand
rg_root = P.make_root(scn, "rag_root", loc=(0.62, -0.62, 1.30))
rag = [P.add_box(scn, "rag", (0, 0, -0.12), (0.24, 0.10, 0.28), M["white"])]
rag += S.tatters(scn, (0, 0, -0.26), 0.24, M["white"], count=3, drop=0.14, seed=2)
P.parent_all(rg_root, rag)

T.finish(scn, px, "town_tavernkeeper", figure, detail, noline,
         roots=[tors_root, mg_root, rg_root],
         skip_extra=tuple(o.name for o in hd_det + foam),
         body_roots=[tors_root])
