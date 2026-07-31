"""High priest -- M15_ASSET_SPECS.md entry 16.

  "a high priest in white-and-gold ceremonial vestments and a tall mitre, holding
   an ornate golden staff with both hands"

The most ornate townsperson, and the one who has to stay clear of the healer,
who is also white-and-gold and also holds a staff. Three things separate them:
the MITRE, a cleft peak no other head has; both hands on the staff instead of
one; and no hood, so his head is bare where hers is covered.

Gold is structural on him rather than trim. He is a townsperson rather than a
combatant, so the game will never draw a rarity rim on him, and there is nothing
for the gold to compete with.
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
figure += T.robe(scn, M, M["white"], top=1.76, r_base=0.82, r_top=0.42)
figure.append(P.add_cyl(scn, "hembraid", (0, 0, 0.07), 0.85, 0.12, M["gold"], verts=12))
figure.append(P.add_cone(scn, "chest", (0, 0, 2.10), 0.43, 0.37, 0.88, M["white"], verts=12))
detail.append(P.add_box(scn, "placket", (0, -0.38, 2.06), (0.12, 0.06, 0.72), M["gold"]))
figure.append(P.add_box(scn, "sash", (0, -0.38, 1.66), (0.58, 0.09, 0.13), M["gold"]))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.52), 0.66, 0.28, 0.44, M["white"], verts=12))
detail.append(P.add_cyl(scn, "mantletrim", (0, -0.02, 2.32), 0.66, 0.10, M["gold"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.42), 0.22, M["white"],
                               scale=(1, .95, .8)))

hd, hd_det = T.head(scn, M, (0, -0.04, 2.86), r=0.28)
figure += hd
detail += hd_det
# the mitre: a cleft peak, which no other head in the game has
figure.append(P.add_cyl(scn, "mitreband", (0, -0.02, 3.08), 0.34, 0.13, M["gold"], verts=12))
for sy in (-1, 1):
    figure.append(P.add_prism(scn, "mitreface",
                              [(-0.30, 0.0), (0.30, 0.0), (0.20, 0.52), (0.0, 0.80), (-0.20, 0.52)],
                              0.10, M["white"], loc=(0, sy * 0.20, 3.14)))
detail.append(P.add_box(scn, "mitrecross", (0, -0.26, 3.46), (0.07, 0.05, 0.26), M["gold"]))
detail.append(P.add_box(scn, "mitrecrossbar", (0, -0.26, 3.48), (0.20, 0.05, 0.07), M["gold"]))

# both hands on the staff, which is what separates him from the healer
figure += S.limb(scn, (-0.46, -0.12, 2.34), (-0.60, -0.60, 2.06), M["white"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.46, -0.12, 2.36), (-0.44, -0.62, 1.60), M["white"], 0.13, 0.115,
                 hand_mat=M["skin"])

st_root = P.make_root(scn, "staff_root", rot=(0, -6, 0), loc=(-0.56, -0.66, 1.96))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.06, 2.80, M["gold"], verts=6)]
for z in (-0.90, -0.10, 0.70):
    staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.09, 0.09, M["white"], verts=6))
staff.append(P.add_cyl(scn, "crook", (0, -0.02, 1.44), 0.22, 0.10, M["gold"], verts=12,
                       rot=(math.radians(90), 0, 0)))
staff.append(P.add_cyl(scn, "crookinner", (0, -0.06, 1.44), 0.13, 0.10, M["white"], verts=12,
                       rot=(math.radians(90), 0, 0)))
for s in (-1, 1):
    staff.append(P.add_cone(scn, "crookpoint", (s * 0.20, -0.02, 1.62), 0.05, 0.0, 0.22,
                            M["gold"], rot=(0, math.radians(s * 24), 0), verts=5))
halo = [P.add_sphere(scn, "staffgem", (0, -0.08, 1.44), 0.085, M["holy"], segs=8, rings=5)]
P.parent_all(st_root, staff + halo)

T.finish(scn, px, "town_highpriest", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in halo))
