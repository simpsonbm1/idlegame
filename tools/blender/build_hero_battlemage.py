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

# ---------------------------------------------------------------------------
# The battlemage line: Adept, Battlemage, Warmage, Archmage (DESIGN.md).
#
# Four robed casters is the hardest line in the roster to keep apart, because a
# robe is one cone and every one of them holds a staff in the same hand. So the
# HEAD does the work and it does it four completely different ways: a plain hood,
# a bare young face, a crested war helm, and a broad pointed hat over a long
# beard. The staff's head is the second read.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

figure, detail, noline = [], [], []

figure += H.robe(scn, M, M["azure"], top=1.76, r_base=0.84, r_top=0.42)
detail += S.tatters(scn, (0, -0.42, 0.12), 1.18, M["violet"], count=6, drop=0.18, seed=5)
figure.append(P.add_cone(scn, "chest", (0, 0, 2.10), 0.44, 0.38, 0.88, M["azure"], verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.40, 1.68), (0.58, 0.09, 0.13), M["violet"]))
detail.append(P.add_box(scn, "placket", (0, -0.38, 2.08), (0.10, 0.06, 0.66), M["violet"]))

if TIER in ("rare", "epic"):
    # armour OVER the robe: these two went to war and the other two did not
    figure += P.add_ridged(scn, "cuirass", (0, -0.06, 2.16), (0.88, 0.44, 0.72),
                           M["steel"], splay=12, bevel=0.06)
    for s in (-1, 1):
        figure.append(P.add_sphere(scn, "pauldron", (s * 0.56, -0.06, 2.50),
                                   0.26 if TIER == "rare" else 0.31, M["steel"],
                                   scale=(1.10, 0.88, 0.72), segs=10, rings=6))
else:
    figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.54), 0.64, 0.28, 0.42, M["violet"], verts=12))

for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.44), 0.22, M["azure"],
                               scale=(1, .95, .8)))
if TRIM:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.68), 0.42, 0.09, TRIM, verts=10))
if LEGEND:
    figure.append(P.add_cone(scn, "overrobe", (0, 0.26, 1.30), 0.78, 0.44, 2.40, M["violet"], verts=10))

# ---- the head, which is what actually separates four men in cones ----
HEAD_AT = (0, -0.06, 2.88)
if TIER == "common":
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27, hood=M["azure"])
elif TIER == "rare":
    # bare headed and young: a soldier who learned magic, not a scholar who
    # picked up a spear
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.05, 2.94), 0.29, M["leath"],
                               scale=(1.0, 1.0, 0.84), segs=12, rings=7))
elif TIER == "epic":
    # a crested war helm, the crest running front to back like a centurion's
    figure.append(P.add_sphere(scn, "helm", (0, -0.04, 2.92), 0.32, M["steel"],
                               scale=(0.94, 1.04, 0.96), segs=14, rings=8))
    figure.append(P.add_box(scn, "helmcrest", (0, 0.02, 3.20), (0.09, 0.52, 0.26), M["violet"]))
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    detail.append(P.add_box(scn, "visorslit", (0, -0.34, 2.92), (0.40, 0.06, 0.08), M["dark"]))
else:
    # the Archmage: a broad pointed hat and a long beard. The hat brim is the
    # widest thing on any head in the roster, and it is unmistakable at any size.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_cone(scn, "hatbrim", (0, -0.04, 3.06), 0.62, 0.30, 0.10,
                             M["violet"], verts=14))
    figure.append(P.add_cone(scn, "hatcone", (0, 0.02, 3.42), 0.30, 0.03, 0.70,
                             M["violet"], rot=(math.radians(-9), 0, 0), verts=12))
    detail.append(P.add_cone(scn, "beard", (0, -0.26, 2.60), 0.20, 0.05, 0.60,
                             M["fur"], rot=(math.radians(180), 0, 0), verts=8))
figure += hd
detail += hd_det

figure += S.limb(scn, (-0.48, -0.12, 2.36), (-0.68, -0.56, 1.84), M["azure"], 0.13, 0.115,
                 hand_mat=M["skin"])
figure += S.limb(scn, (0.48, -0.12, 2.38), (0.68, -0.58, 2.32), M["azure"], 0.13, 0.115,
                 hand_mat=M["skin"])
# arcane runes ON THE SLEEVES: the only glow in the game that sits on cloth
for s, z in ((-1, 2.10), (1, 2.16)):
    noline.append(P.add_box(scn, "rune", (s * 0.56, -0.36, z), (0.09, 0.05, 0.16), M["arcane"]))
    noline.append(P.add_box(scn, "runebar", (s * 0.56, -0.36, z - 0.14), (0.17, 0.05, 0.06), M["arcane"]))

st_root = P.make_root(scn, "staff_root", rot=(0, -8, 0), loc=(-0.72, -0.60, 1.96))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.058, 2.90, M["wood"], verts=6)]
for z in (-1.00, -0.20, 0.60):
    staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.085, 0.09, M["violet"], verts=6))
staff.append(P.add_cone(scn, "cradle", (0, 0, 1.44), 0.17, 0.08, 0.24, TRIM or M["steel"], verts=8))

# The head of the staff, one per man. The Battlemage put a spearhead on his; the
# Warmage caged the energy in iron; the Archmage carries an orb and needs no cage.
if TIER == "rare":
    staff.append(P.add_prism(scn, "spearhead",
                             [(-0.09, 0.0), (0.09, 0.0), (0.07, 0.42), (0.0, 0.62), (-0.07, 0.42)],
                             0.06, M["blade"], loc=(0, 0, 1.62)))
elif TIER == "epic":
    for i in range(4):
        staff.append(P.add_box(scn, "cagebar", (0, 0, 1.72), (0.44, 0.06, 0.07), M["steel"],
                               rot=(0, math.radians(-i * 45), 0)))
    staff.append(P.add_cyl(scn, "cagering", (0, 0, 1.72), 0.24, 0.07, M["steel"], verts=12,
                           rot=(math.radians(90), 0, 0)))
elif TIER == "legendary":
    staff.append(P.add_cyl(scn, "orbring", (0, 0, 1.78), 0.34, 0.08, M["brightgold"], verts=14,
                           rot=(math.radians(90), 0, 0)))

# the crackle: short bars zig-zagging UP the shaft, which is this caster's read
CORE = {"common": 0.135, "rare": 0.115, "epic": 0.175, "legendary": 0.26}[TIER]
CORE_Z = {"common": 1.66, "rare": 1.30, "epic": 1.72, "legendary": 1.78}[TIER]
crackle = [P.add_sphere(scn, "arccore", (0, -0.02, CORE_Z), CORE, M["arcane"], segs=10, rings=7)]
BOLTS = {"common": 6, "rare": 4, "epic": 7, "legendary": 8}[TIER]
for i in range(BOLTS):
    z = 0.10 + i * 0.26
    crackle.append(P.add_box(scn, "arcbolt", (0.10 * (1 if i % 2 else -1), -0.06, z),
                             (0.16, 0.05, 0.07), M["arcane"],
                             rot=(0, math.radians(38 * (1 if i % 2 else -1)), 0)))
if LEGEND:
    for i, (dx, dz) in enumerate(((-0.30, 2.10), (0.30, 2.24), (0.0, 2.46), (-0.18, 2.40))):
        crackle.append(P.add_sphere(scn, "arcorb", (dx, -0.04, dz), 0.085, M["arcane"], segs=8, rings=5))
P.parent_all(st_root, staff + crackle)

H.finish(scn, px, "hero_battlemage", figure, detail, noline, roots=[st_root],
         skip_extra=tuple(o.name for o in crackle))
