"""Undead Legion brute -- M15_ASSET_SPECS.md entry 34.

  "a towering death knight in ancient rusted plate armor, glowing spectral teal
   eye sockets behind the visor, gripping a cracked greatsword"

The family's heavy, and the only entry built on plate rather than bone, so the
job is to keep him reading UNDEAD when almost none of his skeleton shows.

**First pass failed and the reason is worth keeping.** Built entirely from the
rust-brown `iron` material he came back looking like a wooden mannequin: one
material over a whole figure gives the tone ramp nothing to work with, and a
warm brown at armour scale reads as timber rather than metal. The fix is that
rust is TRIM on aged steel, never the suit. Rusted armour still has to be armour
first.

He is also the tallest thing in the faction, which is what "towering" has to mean
at sprite size, so the cell is 128 and the legs carry the extra height. A bigger
ortho would have made him larger on screen than the backdrop agrees he is.
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
px = U.start(scn, res=128)
M = U.palette()

figure, detail, noline = [], [], []

# ---- legs: long, which is where the height comes from ----
for s, yoff, zoff in ((-1, -0.24, 0.0), (1, 0.22, 0.02)):
    figure.append(P.add_box(scn, "sabaton", (s * 0.46, yoff - 0.08, 0.16), (0.48, 0.74, 0.32),
                            M["plate"], bevel=0.05))
    figure.append(P.add_box(scn, "greave", (s * 0.43, yoff, 0.74 + zoff), (0.40, 0.44, 0.92),
                            M["plate"], bevel=0.05))
    detail.append(P.add_box(scn, "greaveband", (s * 0.43, yoff - 0.06, 0.52 + zoff), (0.43, 0.40, 0.10), M["iron"]))
    figure.append(P.add_sphere(scn, "poleyn", (s * 0.43, yoff - 0.17, 1.24 + zoff), 0.24, M["plate"],
                               scale=(1, .85, .72)))
    figure.append(P.add_box(scn, "cuisse", (s * 0.40, yoff * 0.6, 1.56), (0.44, 0.48, 0.62),
                            M["plate"], rot=(0, math.radians(-s * 7), 0), bevel=0.05))

# ---- fauld, with the tatters hung OVER the thighs at the front.
# First pass put them between the legs where nothing could see them.
figure.append(P.add_box(scn, "fauld", (0, 0, 1.94), (1.16, 0.68, 0.42), M["plate"], bevel=0.06))
detail += U.tatters(scn, (0, -0.40, 1.74), 1.04, M["rag"],
                        count=5, drop=0.54, seed=3)
figure.append(P.add_box(scn, "belt", (0, -0.02, 2.18), (1.20, 0.72, 0.19), M["iron"]))
detail.append(P.add_box(scn, "buckle", (0, -0.40, 2.18), (0.18, 0.06, 0.16), M["teal_d"]))

# ---- ridged breastplate: two planes so the ramp lands two tones on one piece ----
figure += P.add_ridged(scn, "cuirass", (0, 0, 2.68), (1.22, 0.60, 0.92), M["plate"], splay=13, bevel=0.08)
# Rust streaked down the plate as bands, not as a colour change: at this size a
# tonal wash is invisible and a hard-edged band is a shape.
detail.append(P.add_box(scn, "ruststreak", (-0.34, -0.34, 2.60), (0.16, 0.06, 0.62), M["iron"]))
detail.append(P.add_box(scn, "ruststreak", (0.30, -0.34, 2.74), (0.11, 0.06, 0.44), M["iron"]))

# ---- the rent in the cuirass: the one place his skeleton shows.
# Wide enough for three rib bars, because the first pass's narrow slot read as a
# name badge pinned to his chest rather than as a hole with a body behind it.
detail.append(P.add_box(scn, "rentdark", (0.02, -0.33, 2.42), (0.46, 0.05, 0.40), M["dark"]))
for i in range(3):
    detail.append(P.add_box(scn, "rentrib", (0.02, -0.36, 2.28 + i * 0.14), (0.40, 0.04, 0.055), M["bone"]))

# ---- pauldrons and arms, pulled forward off the torso so they outline ----
for s, dz, r in ((-1, 0.0, 0.40), (1, 0.02, 0.37)):
    figure.append(P.add_sphere(scn, "pauldron", (s * 0.78, -0.12, 3.02 + dz), r, M["plate"],
                               scale=(1, .95, .78)))
    detail.append(P.add_cyl(scn, "pauldronrim", (s * 0.78, -0.12, 2.86 + dz), r * 0.92, 0.09,
                            M["iron"], verts=10))
    figure.append(P.add_cyl(scn, "upper", (s * 0.78, -0.22, 2.58 + dz), 0.20, 0.66, M["plate"], verts=8))
    figure.append(P.add_cyl(scn, "fore", (s * 0.71, -0.50, 2.12 + dz), 0.18, 0.62, M["plate"],
                            rot=(math.radians(26), 0, 0), verts=8))
    # BONE hands on the grip, not steel gauntlets. It is the cheapest place on an
    # armoured figure to say "undead" without cutting the armour open again.
    figure.append(P.add_sphere(scn, "bonehand", (s * 0.66, -0.70, 1.80 + dz), 0.155, M["bone"]))

# ---- gorget, and a helm that tapers instead of sitting there as a box ----
figure.append(P.add_box(scn, "gorget", (0, 0, 3.26), (0.56, 0.50, 0.20), M["plate"], bevel=0.04))
figure.append(P.add_box(scn, "helmbox", (0, -0.02, 3.52), (0.66, 0.58, 0.36), M["plate"], bevel=0.06))
figure.append(P.add_cone(scn, "helmtop", (0, -0.02, 3.82), 0.36, 0.11, 0.34, M["plate"], verts=8))
figure.append(P.add_cone(scn, "helmsnout", (0, -0.30, 3.46), 0.22, 0.08, 0.26, M["plate"],
                         rot=(math.radians(90), 0, 0), verts=6))
detail.append(P.add_box(scn, "browridge", (0, -0.30, 3.66), (0.62, 0.09, 0.10), M["iron"]))
detail.append(P.add_box(scn, "visor", (0, -0.31, 3.52), (0.52, 0.06, 0.12), M["dark"]))
for s in (-1, 1):
    noline.append(P.add_box(scn, "visorfire", (s * 0.14, -0.34, 3.52), (0.14, 0.05, 0.09), M["teal"]))

# ---- cracked greatsword, point down across the body.
# The crack is a NOTCH cut from the silhouette, not a line drawn inside the
# blade: a line at this scale is one pixel and vanishes, an interruption of the
# edge survives. The blade is pale so it separates from the plate by VALUE --
# README records the knight's sword reading as embedded in his leg until it was
# brightened.
blade = [(-0.10, 0.18), (0.10, 0.18), (0.10, 1.06), (0.02, 1.16), (0.10, 1.26),
         (0.10, 1.92), (0.0, 2.24), (-0.10, 1.92), (-0.10, 1.34), (-0.02, 1.22),
         (-0.10, 1.12)]
sw_root = P.make_root(scn, "sword_root", rot=(0, 148, 0), loc=(-0.72, -0.86, 1.96))
sword = [P.add_prism(scn, "blade", blade, 0.15, M["bone"]),
         P.add_box(scn, "guard", (0, 0, 0.14), (0.66, 0.14, 0.13), M["iron"]),
         P.add_box(scn, "grip", (0, 0, -0.12), (0.14, 0.13, 0.34), M["wood"]),
         P.add_sphere(scn, "pommel", (0, 0, -0.32), 0.115, M["iron"])]
P.parent_all(sw_root, sword)

U.finish(scn, px, "undead_brute", figure, detail, noline, roots=[sw_root])
