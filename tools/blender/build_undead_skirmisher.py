"""Undead Legion skirmisher -- M15_ASSET_SPECS.md entry 35.

  "a gaunt shadow reaver with pale gray dead flesh, wrapped in a tattered black
   cloak trailing wisps of violet mist, two wicked curved blades"

The family's fast one, so his silhouette has to differ from the brute's at a
glance rather than on inspection.

**Three passes, and each failure taught something worth keeping.**

Pass 1 came back as one unreadable dark mass: "tattered black cloak" taken
literally, against a family rule that says "keep overall values mid-bright". An
outline only reads against a light tone (README), so his internal edges vanished
and he lost every shape at once. The palette lift lives in `undead_kit.py`, where
the whole family benefits.

Pass 2 was legible and still wrong: he read as a hulking ape. Gauntness at forty
pixels tall is not a colour or a detail, it is a RATIO -- height against width,
and how much background shows between the limbs. He was as tall as a dwarf and as
broad as the brute. So this pass makes him the tallest common enemy in the family
while keeping the thinnest limbs, and pulls the legs apart so magenta shows
between them.

He is the only entry showing FLESH rather than bone, which is what the spec asks
for and also what stops the faction being six skeletons. Dead flesh sits below
bone in value on purpose, so his hands and face read duller than the bone
priest's skull.
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

# ---- long thin legs, set apart so the gap between them reads ----
for s, yoff, zoff in ((-1, -0.24, 0.0), (1, 0.20, 0.03)):
    figure.append(P.add_box(scn, "foot", (s * 0.30, yoff - 0.12, 0.10), (0.30, 0.56, 0.20),
                            M["rag"], bevel=0.03))
    figure.append(P.add_cyl(scn, "shin", (s * 0.29, yoff, 0.52 + zoff), 0.10, 0.74, M["rag"], verts=8))
    figure.append(P.add_sphere(scn, "knee", (s * 0.29, yoff - 0.08, 0.92 + zoff), 0.125, M["rag"]))
    figure.append(P.add_cyl(scn, "thigh", (s * 0.27, yoff * 0.6, 1.28), 0.125, 0.68, M["rag"], verts=8))

figure.append(P.add_box(scn, "hips", (0, 0, 1.70), (0.52, 0.42, 0.30), M["rag"], bevel=0.05))
detail.append(P.add_box(scn, "sashbelt", (0, -0.04, 1.86), (0.56, 0.46, 0.12), M["vest"]))

# ---- torso: narrow at the waist, widening only at the shoulders, so everything
# below the collarbone reads as starved.
figure.append(P.add_cone(scn, "torso", (0, -0.02, 2.24), 0.24, 0.36, 0.84, M["rag"], verts=10))
detail += U.ribcage(scn, M, (0, -0.25, 2.30), width=0.38, height=0.54, ribs=3, mat=M["flesh"])

# ---- the cloak: narrow, standing PROUD of the back so it outlines against the
# torso. A cloak flush with the spine is invisible at this size.
figure.append(P.add_cone(scn, "cloak", (0, 0.22, 2.06), 0.42, 0.28, 1.44, M["robe_d"], verts=10))
detail += U.tatters(scn, (0, 0.28, 1.36), 0.74, M["robe_d"],
                        count=6, drop=0.46, seed=1)
# violet mist ON the hem rather than floating beside it -- pass 1 left four blobs
# hanging in clear magenta with nothing to belong to
for i, (dx, dz, r) in enumerate(((-0.33, 1.14, 0.10), (-0.39, 1.38, 0.07),
                                 (0.31, 1.04, 0.09), (0.38, 1.30, 0.065))):
    noline.append(P.add_sphere(scn, "mist", (dx, 0.30, dz), r,
                               M["violet"] if i % 2 == 0 else M["teal_d"], segs=8, rings=5))

# ---- narrow shoulders and two thin arms held out wide with the blades ----
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.36, -0.06, 2.62), 0.155, M["rag"],
                               scale=(1, .95, .85)))
figure.append(P.add_cyl(scn, "upperL", (-0.50, -0.20, 2.36), 0.095, 0.60, M["flesh"], verts=8,
                        rot=(0, math.radians(-18), 0)))
figure.append(P.add_cyl(scn, "foreL", (-0.68, -0.48, 2.00), 0.082, 0.58, M["flesh"], verts=8,
                        rot=(math.radians(30), math.radians(-22), 0)))
figure.append(P.add_sphere(scn, "handL", (-0.79, -0.64, 1.74), 0.11, M["flesh"]))
figure.append(P.add_cyl(scn, "upperR", (0.50, -0.22, 2.38), 0.095, 0.58, M["flesh"], verts=8,
                        rot=(0, math.radians(20), 0)))
figure.append(P.add_cyl(scn, "foreR", (0.66, -0.50, 2.14), 0.082, 0.56, M["flesh"], verts=8,
                        rot=(math.radians(36), math.radians(26), 0)))
figure.append(P.add_sphere(scn, "handR", (0.75, -0.66, 1.90), 0.11, M["flesh"]))

# ---- a visible NECK, which is most of what separates gaunt from hulking. Pass 2
# seated the head straight on the shoulders and he read as having none.
figure.append(P.add_cyl(scn, "neck", (0, -0.04, 2.76), 0.085, 0.24, M["flesh"], verts=6))

# ---- head: a gaunt face inside an open hood, not a bare skull ----
figure.append(P.add_sphere(scn, "head", (0, -0.10, 3.00), 0.205, M["flesh"],
                           scale=(0.88, 1, 1.14), segs=10, rings=7))
figure.append(P.add_cone(scn, "hood", (0, 0.06, 3.12), 0.33, 0.10, 0.54, M["robe_d"], verts=10))
detail.append(P.add_box(scn, "browshadow", (0, -0.27, 3.10), (0.30, 0.05, 0.10), M["dark"]))
detail.append(P.add_box(scn, "cheekline", (0, -0.29, 2.90), (0.22, 0.04, 0.04), M["dark"]))
for s in (-1, 1):
    noline.append(P.add_box(scn, "eyeglow", (s * 0.085, -0.30, 3.02), (0.065, 0.04, 0.05), M["violet"]))

# ---- two curved blades, each on its own root so its angle is one number.
# Pale bone so they separate from the cloth by value, not only by outline.
curve = [(-0.05, 0.0), (0.05, 0.0), (0.14, 0.44), (0.17, 0.82), (0.02, 1.00),
         (0.02, 0.76), (-0.04, 0.42)]
blade_roots = []
for name, rot, loc in (("bladeL_root", (0, 156, 0), (-0.83, -0.74, 1.68)),
                       ("bladeR_root", (0, 26, 0), (0.79, -0.76, 1.84))):
    br = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(br, [P.add_prism(scn, "curveblade", curve, 0.07, M["bone"]),
                      P.add_box(scn, "bladegrip", (0, 0, -0.13), (0.09, 0.09, 0.24), M["wood"]),
                      P.add_box(scn, "bladeguard", (0, 0, 0.02), (0.24, 0.10, 0.06), M["iron"])])
    blade_roots.append(br)

U.finish(scn, px, "undead_skirmisher", figure, detail, noline, roots=blade_roots, role="skirmisher")
