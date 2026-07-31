"""Infernal Siege boss -- M15_ASSET_SPECS.md entry 45.

  "BOSS, the showpiece of the whole series: the Demon Empress, a towering regal
   demoness in obsidian-black and gold war regalia with a crown of curling horns,
   great wings folded behind her, wreathed in ember-orange hellfire, holding a
   blazing scepter"

The last boss, and the spec calls her the showpiece, so she gets the two things
no other figure in the roster has: WINGS at full size, and gold as a structural
material rather than as trim.

The wings are folded rather than spread. Spread wings at this height would run
off both sides of the cell and force a wider one, which would break the shared
cell grid every sprite is placed on. Folded, they rise BEHIND her shoulders and
finish above her crown, so she is the tallest thing in the game by silhouette as
well as by measurement.

Her crown is horns rather than metal. Every other crowned figure in the roster
wears a stolen or scavenged one, so the Empress having grown hers is the point.

Hellfire wreathes her at the hem rather than the hands. Both her hands are
occupied and a figure this large needs its brightest note low, or the eye stops
at the crown and never reads the rest.
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
px = I.start(scn, res=144)
M = I.palette()

figure, detail, noline = [], [], []

# ---- obsidian regalia to the floor, gold at the hem ----
figure.append(P.add_cone(scn, "irobe", (0, 0, 1.06), 1.02, 0.52, 2.12, M["hide"], verts=12))
figure.append(P.add_cyl(scn, "ihembraid", (0, 0, 0.08), 1.05, 0.13, M["brass"], verts=12))
detail += S.tatters(scn, (0, -0.52, 0.18), 1.48, M["crim"], count=8, drop=0.28, seed=12)
# gold panels down the front, the structural use of gold that only she gets
detail.append(P.add_box(scn, "ipanel", (0, -0.50, 1.60), (0.15, 0.07, 1.20), M["brass"]))
for s in (-1, 1):
    detail.append(P.add_box(scn, "ipanelside", (s * 0.34, -0.46, 1.42), (0.09, 0.07, 0.84), M["brass"]))

# hellfire wreathing the hem: her brightest note is LOW, so the eye reads the
# whole figure rather than stopping at the crown
for i in range(7):
    a = math.radians(-140 + i * 47)
    noline.append(P.add_sphere(scn, "iwreath",
                               (math.cos(a) * 1.02, math.sin(a) * 0.44 - 0.10, 0.22 + (i % 3) * 0.14),
                               0.115 - (i % 3) * 0.022,
                               M["ember"] if i % 2 else M["ember_h"], segs=8, rings=5))

figure.append(P.add_box(scn, "ifauld", (0, 0, 2.06), (1.10, 0.70, 0.44), M["iron"], bevel=0.06))
figure.append(P.add_box(scn, "ibelt", (0, -0.04, 2.32), (1.14, 0.74, 0.19), M["brass"]))
detail.append(P.add_box(scn, "ibuckle", (0, -0.44, 2.32), (0.22, 0.06, 0.19), M["blood"]))

# ---- cuirass, ridged so the ramp lands two tones on one piece ----
figure += P.add_ridged(scn, "icuirass", (0, 0, 2.82), (1.12, 0.60, 0.88), M["iron"], splay=13, bevel=0.07)
noline += I.cracks(scn, M, [(-0.32, -0.38, 2.72, 0.30), (0.30, -0.38, 2.92, 0.24)])

# ---- the folded wings, rising behind the shoulders and finishing above the crown.
# Spread wings would run off both sides of the cell and force a wider one, which
# would break the shared cell grid every sprite is placed on.
wing = [(0.0, 0.0), (0.34, 0.86), (0.54, 1.86), (0.32, 1.54), (0.40, 2.06),
        (0.14, 1.58), (0.16, 0.92), (-0.08, 0.46)]
for s in (-1, 1):
    wr = P.make_root(scn, "wing%d_root" % (s + 2), rot=(0, 0, s * 18), loc=(s * 0.56, 0.48, 2.56))
    # CRIMSON membranes. Charcoal wings against a charcoal body were invisible on
    # the one figure in the roster that most needs them to read.
    parts = [P.add_prism(scn, "iwing", [(x * s, z) for x, z in wing], 0.07, M["crim"])]
    for ax, az in ((0.22, 0.66), (0.34, 1.34), (0.16, 1.10)):
        parts.append(S.aimed_cyl(scn, "iwingrib", (0, 0, 0), (ax * s, 0, az), 0.045, M["horn"], verts=4))
    parts.append(P.add_cone(scn, "iwingclaw", (s * 0.32, 0, 1.78), 0.05, 0.0, 0.22, M["bone"],
                            rot=(0, math.radians(s * 18), 0), verts=5))
    P.parent_all(wr, parts)
    figure.append(wr)

# ---- pauldrons and the standing collar ----
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "ipauldron", (s * 0.82, -0.06, 3.14), 0.37, M["iron"],
                               scale=(1, .95, .8)))
    figure.append(P.add_cone(scn, "ipauldronhorn", (s * 0.90, -0.06, 3.44), 0.09, 0.02, 0.38,
                             M["brass"], rot=(0, math.radians(s * 20), 0), verts=6))
# The collar FRAMES the head; it does not contain it. Opened to 0.76 at the top
# it was nearly three times the width of her skull and read as a basin she was
# standing in, with her face lost inside it.
figure.append(P.add_cone(scn, "icollar", (0, 0.24, 3.26), 0.30, 0.48, 0.54, M["crim"], verts=10))

# ---- head, and a crown of grown horns rather than stolen metal ----
figure.append(P.add_sphere(scn, "iskull", (0, -0.10, 3.60), 0.27, M["crim"],
                           scale=(0.96, 1.0, 1.06), segs=10, rings=7))
figure.append(P.add_box(scn, "ijaw", (0, -0.32, 3.44), (0.34, 0.28, 0.18), M["crim"], bevel=0.04))
detail.append(P.add_box(scn, "ilips", (0, -0.44, 3.42), (0.24, 0.05, 0.05), M["blood"]))
noline += [P.add_box(scn, "ieye", (s * 0.10, -0.34, 3.64), (0.10, 0.05, 0.08), M["ember_h"])
           for s in (-1, 1)]
figure += I.horns(scn, M, (0, -0.06, 3.72), r=0.30, curl=3, sweep=44, length=0.34, mat=M["horn"])
figure += I.horns(scn, M, (0, 0.10, 3.80), r=0.20, curl=2, sweep=54, length=0.26, mat=M["brass"])
figure.append(P.add_cyl(scn, "icircle", (0, -0.08, 3.82), 0.29, 0.10, M["brass"], verts=10))

# ---- one clawed hand on the scepter, one out and commanding ----
figure += I.clawed_limb(scn, M, (-0.78, -0.16, 3.00), (-0.90, -0.62, 2.24), upper_r=0.15, fore_r=0.13)
figure += I.clawed_limb(scn, M, (0.78, -0.16, 3.02), (0.96, -0.68, 2.80), upper_r=0.15, fore_r=0.13)
noline += S.flame(scn, (0.98, -0.74, 2.98), M["ember_h"], M["ember_d"], scale=0.85)

# ---- the blazing scepter ----
sc_root = P.make_root(scn, "scepter_root", rot=(0, -8, 0), loc=(-0.96, -0.66, 2.38))
scepter = [P.add_cyl(scn, "ishaft", (0, 0, 0), 0.062, 3.20, M["iron"], verts=6)]
for z in (-1.06, -0.26, 0.54):
    scepter.append(P.add_cyl(scn, "iband", (0, 0, z), 0.09, 0.10, M["brass"], verts=6))
scepter.append(P.add_cone(scn, "icradle", (0, 0, 1.58), 0.20, 0.09, 0.26, M["brass"], verts=8))
for s in (-1, 1):
    scepter.append(P.add_cone(scn, "iprong", (s * 0.15, 0, 1.86), 0.05, 0.0, 0.34, M["brass"],
                              rot=(0, math.radians(s * 26), 0), verts=6))
blaze = [P.add_sphere(scn, "isceptercore", (0, 0, 1.84), 0.155, M["ember_h"], segs=10, rings=7)]
blaze += S.flame(scn, (0, -0.02, 1.98), M["ember"], M["ember_d"], scale=1.05)
P.parent_all(sc_root, scepter + blaze)

I.finish(scn, px, "infernal_boss", figure, detail, noline, roots=[sc_root],
         skip_extra=tuple(o.name for o in blaze), role="boss")
