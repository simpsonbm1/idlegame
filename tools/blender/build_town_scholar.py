"""Scholar -- M15_ASSET_SPECS.md entry 12.

  "a scholar in blue robes, flat cap, and round spectacles, carrying a thick open
   book, rolled scroll under one arm"

The open book held at chest height is the read: a pale rectangle turned toward
the viewer, and the only flat bright plane on a townsperson.

His spectacles are two small dark rings on a lit face. At this size that is
four pixels doing the work, which is enough only because the face behind them
is the brightest thing on the figure.
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
figure += T.robe(scn, M, M["blue"], top=1.74, r_base=0.80, r_top=0.42)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.43, 0.37, 0.88, M["blue"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.38, 1.66), (0.56, 0.09, 0.12), M["leath"]))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.50), 0.62, 0.28, 0.40, M["blue"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.45, -0.04, 2.42), 0.21, M["blue"],
                               scale=(1, .95, .8)))

hd, hd_det = T.head(scn, M, (0, -0.04, 2.84), r=0.28)
figure += hd
detail += hd_det
# flat cap
figure.append(P.add_cyl(scn, "cap", (0, -0.02, 3.06), 0.36, 0.11, M["blue"], verts=12))
figure.append(P.add_cyl(scn, "capband", (0, -0.02, 2.98), 0.29, 0.09, M["blue"], verts=12))
# round spectacles: two small rings on the brightest part of the figure
for s in (-1, 1):
    detail.append(P.add_cyl(scn, "spectacle", (s * 0.10, -0.28, 2.86), 0.075, 0.05, M["brass"],
                            verts=8, rot=(math.radians(90), 0, 0)))
detail.append(P.add_box(scn, "specbridge", (0, -0.28, 2.86), (0.09, 0.04, 0.04), M["brass"]))

figure += S.limb(scn, (-0.46, -0.12, 2.34), (-0.40, -0.60, 2.00), M["blue"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.46, -0.12, 2.36), (0.40, -0.60, 2.02), M["blue"], 0.13, 0.115,
                 hand_mat=M["skin"])

# the open book, held flat and turned toward the viewer
bk_root = P.make_root(scn, "book_root", rot=(-34, 0, 0), loc=(0, -0.66, 2.06))
book = [P.add_box(scn, "bookleafL", (-0.24, 0, 0), (0.46, 0.34, 0.07), M["white"]),
        P.add_box(scn, "bookleafR", (0.24, 0, 0), (0.46, 0.34, 0.07), M["white"]),
        P.add_box(scn, "bookspine", (0, 0, -0.03), (0.09, 0.36, 0.10), M["leath"]),
        P.add_box(scn, "bookcover", (0, 0, -0.06), (0.98, 0.38, 0.06), M["leath"])]
for s in (-1, 1):
    for i in range(3):
        book.append(P.add_box(scn, "textline", (s * 0.24, -0.06 + i * 0.09, 0.05),
                              (0.32, 0.05, 0.02), M["dark"]))
P.parent_all(bk_root, book)

# rolled scroll under the other arm
sc_root = P.make_root(scn, "scroll_root", rot=(0, 96, 0), loc=(0.52, -0.30, 2.14))
scroll = [P.add_cyl(scn, "scroll", (0, 0, 0), 0.09, 0.62, M["white"], verts=8),
          P.add_cyl(scn, "scrollcap", (0, 0, 0.32), 0.10, 0.07, M["brass"], verts=8),
          P.add_cyl(scn, "scrollcapB", (0, 0, -0.32), 0.10, 0.07, M["brass"], verts=8)]
P.parent_all(sc_root, scroll)

T.finish(scn, px, "town_scholar", figure, detail, noline, roots=[bk_root, sc_root])
