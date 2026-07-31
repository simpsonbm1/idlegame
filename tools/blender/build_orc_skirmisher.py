"""Orc Warband skirmisher -- M15_ASSET_SPECS.md entry 23.

  "a frenzied orc berserker, bare-chested with war paint and battle scars, a
   jagged axe in each hand"

The berserker is the family's contrast piece: the brute beside him is armoured in
black iron from hip to helm, and this one wears none at all. Bare olive hide
against black plate separates them by VALUE across most of their area, which is
the only kind of difference that survives at forty pixels.

His axes go out and UP, where the brute's maul hangs low. Two figures of the same
build and palette are told apart by what their arms are doing before anything
else.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import orc_kit as O
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(O)

scn = P.get_scene()
px = O.start(scn, res=128)
M = O.palette()

figure, detail, noline = [], [], []

HIP = 1.38
figure += O.heavy_legs(scn, M, HIP, spread=0.50)
figure.append(P.add_box(scn, "ohips", (0, 0, HIP), (1.16, 0.68, 0.40), M["hide"], bevel=0.06))
figure.append(P.add_prism(scn, "oloin", [(-0.32, 0.28), (0.32, 0.28), (0.24, -0.70), (-0.24, -0.70)],
                          0.11, M["fur"], loc=(0.02, -0.36, 1.32)))
detail += S.tatters(scn, (0, -0.38, 1.00), 0.60, M["fur"], count=4, drop=0.22, seed=7)

tors_root, tors = O.barrel_torso(scn, M, HIP + 0.16, chest_r=0.70, lean=14)
tors.append(P.add_box(scn, "obelt", (0, -0.04, 0.16), (1.22, 0.72, 0.18), M["leath"]))

# ---- bare chest: war paint and scars instead of armour. Both are BANDS, since
# a band is a shape at this size and a mark is a lost pixel.
# These carry TORSO-local coordinates, so they belong to the torso root. Added to
# the figure-level `detail` list they were parented to the figure root instead and
# landed near his groin as a stray red mark.
tors_det = [P.add_box(scn, "ochestpaint", (0, -0.52, 0.72), (0.66, 0.08, 0.16), M["paint"])]
for dx, dz, w in ((-0.30, 0.50, 0.34), (0.26, 0.42, 0.28)):
    tors_det.append(P.add_box(scn, "oscar", (dx, -0.52, dz), (0.07, 0.06, w), M["paint"],
                              rot=(0, math.radians(28), 0)))

hd_fig, hd_det = O.head(scn, M, (0, -0.04, 1.20), r=0.46)
tors += hd_fig
# a topknot, which gives him the only broken top edge in the family's commons
tors.append(P.add_cyl(scn, "oknotband", (0, 0.04, 1.58), 0.15, 0.12, M["leath"], verts=6))
tors.append(P.add_cone(scn, "otopknot", (0, 0.10, 1.86), 0.13, 0.03, 0.50, M["fur"],
                       rot=(math.radians(-16), 0, 0), verts=6))

# ---- both arms out and up, which is the whole pose ----
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "oshoulder", (s * 0.92, -0.10, 0.86), 0.40, M["hide"],
                             scale=(1, .95, .88)))
    tors.append(P.add_box(scn, "oarmband", (s * 0.98, -0.14, 0.72), (0.34, 0.30, 0.13), M["leath"]))
tors.append(P.add_cyl(scn, "oupperL", (-1.06, -0.22, 1.06), 0.26, 0.66, M["hide"], verts=8,
                      rot=(0, math.radians(-32), 0)))
tors.append(P.add_cyl(scn, "oforeL", (-1.28, -0.36, 1.48), 0.23, 0.60, M["hide"], verts=8,
                      rot=(math.radians(-14), math.radians(-20), 0)))
tors.append(P.add_sphere(scn, "ofistL", (-1.38, -0.48, 1.78), 0.24, M["hide"]))
tors.append(P.add_cyl(scn, "oupperR", (1.06, -0.24, 1.02), 0.26, 0.64, M["hide"], verts=8,
                      rot=(0, math.radians(30), 0)))
tors.append(P.add_cyl(scn, "oforeR", (1.24, -0.40, 1.38), 0.23, 0.58, M["hide"], verts=8,
                      rot=(math.radians(-12), math.radians(22), 0)))
tors.append(P.add_sphere(scn, "ofistR", (1.32, -0.52, 1.64), 0.24, M["hide"]))

P.parent_all(tors_root, tors + hd_det + tors_det)

# ---- two jagged axes. The jaggedness is cut from the SILHOUETTE of the bit, not
# drawn inside it: a notch survives being three pixels wide, a line does not.
bit = [(0.0, -0.34), (0.30, -0.40), (0.44, -0.16), (0.38, 0.02), (0.46, 0.20),
       (0.28, 0.40), (0.0, 0.34)]
axe_roots = []
for name, rot, loc in (("axeL_root", (0, -34, 0), (-1.44, -0.54, 3.06)),
                       ("axeR_root", (0, 30, 0), (1.38, -0.58, 2.90))):
    ar = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(ar, [P.add_cyl(scn, "oaxehaft", (0, 0, 0.14), 0.075, 1.00, M["wood"], verts=6),
                      P.add_prism(scn, "oaxebit", bit, 0.09, M["steel"], loc=(0.10, 0, 0.54)),
                      P.add_box(scn, "oaxecollar", (0, 0, 0.52), (0.15, 0.13, 0.20), M["iron"]),
                      P.add_box(scn, "oaxewrap", (0, 0, -0.24), (0.11, 0.11, 0.26), M["leath"])])
    axe_roots.append(ar)

O.finish(scn, px, "orc_skirmisher", figure, detail, noline,
         roots=[tors_root] + axe_roots,
         skip_extra=tuple(o.name for o in hd_det + tors_det))
