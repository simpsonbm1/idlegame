"""Battle-mage -- M15_ASSET_SPECS.md entry 6.

  "a battle-mage in deep blue robes with purple trim and glowing arcane runes on
   the sleeves, tall staff crackling with bright arcane blue energy"

The roster now holds six staff-carrying casters, so this one is separated by the
ENERGY rather than the staff: a vertical crackle running up the shaft, where the
undead necromancer's flame sits on top and the orc warcaster's bolt is thrown
clear of the body.

His sleeve runes are the only place in the game where a glow sits on cloth rather
than at the end of something, which is what makes him read as a mage rather than
as a man holding a lamp.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Common**, so that tier gets no separate file.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import hero_kit as H
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(H)

scn = P.get_scene()
px = H.start(scn, res=112)
M = H.palette()
TRIM = H.trim_mat(M)        # None on a common hero: plain and field-worn
GLOW = H.glow_mat(M)        # epic and legendary only
LEGEND = H.is_legendary()

figure, detail, noline = [], [], []

figure += H.robe(scn, M, M["azure"], top=1.76, r_base=0.84, r_top=0.42)
detail += S.tatters(scn, (0, -0.42, 0.12), 1.18, M["violet"], count=6, drop=0.18, seed=5)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.10), 0.44, 0.38, 0.88, M["azure"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.40, 1.68), (0.58, 0.09, 0.13), M["violet"]))
detail.append(P.add_box(scn, "placket", (0, -0.38, 2.08), (0.10, 0.06, 0.66), M["violet"]))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.54), 0.64, 0.28, 0.42, M["violet"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.44), 0.22, M["azure"],
                               scale=(1, .95, .8)))
if TRIM:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.68), 0.42, 0.09, TRIM, verts=10))
if LEGEND:
    figure.append(P.add_cone(scn, "overrobe", (0, 0.26, 1.30), 0.78, 0.44, 2.40, M["violet"], verts=10))

hd, hd_det = H.head(scn, M, (0, -0.06, 2.88), r=0.27, hood=M["azure"])
figure += hd
detail += hd_det

figure += S.limb(scn, (-0.48, -0.12, 2.36), (-0.68, -0.56, 1.84), M["azure"], 0.13, 0.115,
                 joint_mat=M["skin"])
figure += S.limb(scn, (0.48, -0.12, 2.38), (0.68, -0.58, 2.32), M["azure"], 0.13, 0.115,
                 joint_mat=M["skin"])
# arcane runes ON THE SLEEVES: the only glow in the game that sits on cloth
for s, z in ((-1, 2.10), (1, 2.16)):
    noline.append(P.add_box(scn, "rune", (s * 0.56, -0.36, z), (0.09, 0.05, 0.16), M["arcane"]))
    noline.append(P.add_box(scn, "runebar", (s * 0.56, -0.36, z - 0.14), (0.17, 0.05, 0.06), M["arcane"]))

st_root = P.make_root(scn, "staff_root", rot=(0, -8, 0), loc=(-0.72, -0.60, 1.96))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.058, 2.90, M["wood"], verts=6)]
for z in (-1.00, -0.20, 0.60):
    staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.085, 0.09, M["violet"], verts=6))
staff.append(P.add_cone(scn, "cradle", (0, 0, 1.44), 0.17, 0.08, 0.24, TRIM or M["steel"], verts=8))
# the crackle: short bars zig-zagging UP the shaft, which is this caster's read
crackle = [P.add_sphere(scn, "arccore", (0, -0.02, 1.66), 0.135, M["arcane"], segs=10, rings=7)]
for i in range(6):
    z = 0.10 + i * 0.26
    crackle.append(P.add_box(scn, "arcbolt", (0.10 * (1 if i % 2 else -1), -0.06, z),
                             (0.16, 0.05, 0.07), M["arcane"],
                             rot=(0, math.radians(38 * (1 if i % 2 else -1)), 0)))
if LEGEND:
    for i, (dx, dz) in enumerate(((-0.22, 1.94), (0.22, 2.04), (0.0, 2.22))):
        crackle.append(P.add_sphere(scn, "arcorb", (dx, -0.04, dz), 0.075, M["arcane"], segs=8, rings=5))
P.parent_all(st_root, staff + crackle)

H.finish(scn, px, "hero_battlemage", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in crackle))
