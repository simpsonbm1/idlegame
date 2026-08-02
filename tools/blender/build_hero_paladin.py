"""Paladin -- M15_ASSET_SPECS.md entry 4.

  "a holy paladin in polished silver-white plate armor with gold trim, warhammer
   in one hand, radiant golden holy symbol in the other"

The brightest ARMOURED figure in the game, and the counterweight to the guardian
knight's blue steel: same plate build, near-white rather than blue, gold rather
than navy. The two are meant to be recognisably the same class of soldier.

His holy symbol is held out at arm's length rather than worn, which makes it the
only hero silhouette with a bright point detached from the body.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Epic (the Crusader)**, so that tier gets no separate file.
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
# The paladin line: Squire, Paladin, Crusader, Highlord (DESIGN.md).
#
# The HELD HOLY SYMBOL is this line's read. No other hero has a bright point
# detached from the body, so how much of one each man carries says his rank at a
# glance: the Squire has none and has not earned one, the Paladin wears a small
# one, the Crusader holds one out, the Highlord's throws rays.
#
# **This hero's own sprite is Epic, the Crusader**, and every branch below leaves
# that tier byte-for-byte as it was.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "epic"

# The base calls his silver-white plate "fur", which is the palette's near-white.
PLATE = {"common": "mail", "rare": "steel", "epic": "fur", "legendary": "fur"}[TIER]
GILT = {"common": "leath", "rare": "gold", "epic": "gold", "legendary": "brightgold"}[TIER]
PL, GI = M[PLATE], M[GILT]

figure, detail, noline = [], [], []

HIP = 1.20
# Spread is written out, NOT taken from H.stance(): that helper keys off the tier
# name and widens epic, and epic is this hero's own shipped sprite. A hero's base
# tier must never take a stance multiplier.
SPREAD = {"common": 0.32, "rare": 0.34, "epic": 0.36, "legendary": 0.44}[TIER]
figure += H.legs(scn, M, HIP, spread=SPREAD, mat=PL, boot=PL)
figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.92, 0.56, 0.32), PL, bevel=0.05))
figure.append(P.add_box(scn, "belt", (0, -0.02, HIP + 0.20), (0.96, 0.60, 0.16), GI))

tors_root, tors = H.torso(scn, M, HIP + 0.20,
                          chest_r=0.44 if TIER == "common" else 0.48, lean=5, mat=PL)
if TIER == "common":
    # the Squire: a mail shirt and a leather jerkin, no cuirass. He is the only
    # one of the four without a plate chest, and the smallest of them.
    tors.append(P.add_box(scn, "jerkin", (0, -0.14, 0.52), (0.86, 0.44, 0.74),
                          M["leath"], bevel=0.05))
    tors.append(P.add_box(scn, "strap", (0, -0.36, 0.54), (0.92, 0.09, 0.15), M["leath"],
                          rot=(0, math.radians(26), 0)))
else:
    tors += P.add_ridged(scn, "cuirass", (0, -0.06, 0.52), (1.00, 0.48, 0.78), PL,
                         splay=13, bevel=0.07)
    tors.append(P.add_box(scn, "placket", (0, -0.34, 0.50), (0.12, 0.07, 0.72), GI))
if TRIM and TIER != "common":
    tors.append(P.add_box(scn, "cuirasstrim", (0, -0.32, 0.86), (0.94, 0.08, 0.10), TRIM))
    tors.append(P.add_box(scn, "cuirassbase", (0, -0.32, 0.16), (0.90, 0.08, 0.09), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.62, height=1.70,
                      r_base=0.64, r_top=0.32, y=0.46)

# ---- head ----
# USER RULING 2026-08-02: every character and variant is INDIVIDUALLY DESIGNED,
# not reassembled from parts shared with other units. So these three helms are
# built here rather than taken from `hero_kit.head(helm=...)`, whose generic
# dome-and-brim read as a soft cap (user, 2026-08-02).
#
# They are CLOSED, which is a deliberate exception to the heroes' open-face rule:
# a paladin's identity is that you never see his face. None of the three may
# repeat one of the guardian knight's four, so the faceted great helm with a
# cross slit, the smooth sallet with a tail, the horned barbute and the winged
# open crown are all spoken for.
# Visor slits go in `tors`, NOT `detail`. Everything in `tors` is parented to
# `tors_root` at z = HIP + 0.20; anything in `detail` is parented to the FIGURE
# root instead, so a slit written in torso-local coordinates landed 1.4 units
# down inside the body and never appeared. That was true of the rare's slit
# before this rework too. They are outline-skipped through `visor` instead.
hd, hd_det, visor = [], [], []
if TIER == "common":
    # bare headed under a leather coif: a boy, and the only open face in the line
    hd, hd_det = H.head(scn, M, (0, -0.04, 1.10), r=0.30)
    tors.append(P.add_sphere(scn, "coif", (0, 0.04, 1.14), 0.34, M["leath"],
                             scale=(1.0, 1.02, 0.90), segs=12, rings=7))
elif TIER == "rare":
    # the Paladin: a pointed conical helm over a mail aventail. A CONE is the one
    # head silhouette nobody else owns -- the guardian's four and the other two
    # paladins are all domes and blocks. The previous attempt was a squared shell
    # with a lower lip jutting off it, which read as the nose of a truck (user,
    # 2026-08-02).
    # The cone IS the closed helm: at face height it is 0.29 across and centred on
    # the head, so it encloses the face without a separate plate bolted to the
    # front. Bolting one on is how the truck nose happened.
    # Blunt, and finished with a ball. Taken to a 0.03 point over 0.66 it read as
    # a spike rather than a helmet.
    tors.append(P.add_cone(scn, "helmshell", (0, -0.06, 1.20), 0.38, 0.12, 0.52, PL,
                           verts=10))
    tors.append(P.add_sphere(scn, "helmfinial", (0, -0.06, 1.48), 0.10, GI, segs=8, rings=6))
    tors.append(P.add_cone(scn, "aventail", (0, -0.04, 0.92), 0.46, 0.36, 0.36, M["mail"],
                           verts=10))
    # a T-slot cut into the cone. Each piece is placed just proud of the cone's
    # surface AT ITS OWN HEIGHT, which is a different radius for each. Keep them
    # SMALL: at 0.38 wide the horizontal bar read as a hole punched in his face.
    visor.append(P.add_box(scn, "visorslit", (0, -0.36, 1.14), (0.30, 0.09, 0.055), M["dark"]))
    visor.append(P.add_box(scn, "visorvent", (0, -0.42, 1.02), (0.07, 0.09, 0.20), M["dark"]))
elif TIER == "epic":
    # the Crusader: a pig-faced bascinet. The snout is the whole read, and it is
    # the only pointed face in the roster.
    tors.append(P.add_sphere(scn, "helmshell", (0, -0.04, 1.16), 0.34, PL,
                             scale=(0.98, 1.0, 1.08), segs=12, rings=8))
    tors.append(P.add_cone(scn, "helmsnout", (0, -0.36, 1.08), 0.30, 0.06, 0.66, PL,
                           rot=(math.radians(108), 0, 0), verts=8))
    for s in (-1, 1):
        visor.append(P.add_box(scn, "visorslit", (s * 0.13, -0.42, 1.21), (0.17, 0.10, 0.08),
                               M["dark"]))
else:
    # the Highlord: a crowned armet. A tall comb over the crown of the head, a
    # gold circlet round it, and the gold wings below.
    tors.append(P.add_sphere(scn, "helmshell", (0, -0.04, 1.16), 0.35, PL,
                             scale=(0.96, 1.0, 1.12), segs=12, rings=8))
    tors.append(P.add_prism(scn, "helmcomb",
                            [(-0.34, 0.0), (-0.18, 0.30), (0.18, 0.30), (0.34, 0.0)],
                            0.08, M["brightgold"], loc=(0, -0.04, 1.44),
                            rot=(0, 0, math.radians(90))))
    tors.append(P.add_cyl(scn, "helmcirclet", (0, -0.04, 1.04), 0.36, 0.10, M["brightgold"],
                          verts=12))
    visor.append(P.add_box(scn, "visorslit", (0, -0.44, 1.20), (0.48, 0.10, 0.09), M["dark"]))
tors += hd + visor
if LEGEND:
    for s in (-1, 1):
        tors.append(P.add_prism(scn, "helmwing",
                                [(0.0, 0.0), (0.34, 0.30), (0.46, 0.10), (0.30, -0.10)],
                                0.05, M["brightgold"],
                                loc=(s * 0.30, 0.06, 1.36), rot=(0, 0, math.radians(s * 90 - 90))))

# `pauldron` is the pivot attack_roster.py swings his hammer arm about, so it
# must stay the topmost left-arm part on every tier.
PAULD = {"common": 0.26, "rare": 0.28, "epic": 0.30, "legendary": 0.34}[TIER]
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "pauldron", (s * 0.60, -0.08, 0.74), PAULD, PL,
                             scale=(1, .95, .82)))
    if TRIM and TIER != "common":
        tors.append(P.add_cyl(scn, "pauldronrim", (s * 0.60, -0.08, 0.60), 0.26, 0.08, TRIM, verts=10))

# Arms taper so each end cap is buried in the piece that swallows it -- the limb
# rule in README.md. The hammer arm hangs the same way on all four.
tors.append(P.add_cone(scn, "upperL", (-0.60, -0.18, 0.44), 0.115, 0.15, 0.48, PL, verts=8))
tors.append(P.add_cone(scn, "foreL", (-0.57, -0.47, 0.06), 0.125, 0.155, 0.471, PL, verts=8,
                       rot=(math.radians(47.2), 0, math.radians(-170))))
tors.append(P.add_sphere(scn, "fistL", (-0.54, -0.64, -0.10), 0.16, PL))

# THE OFF HAND IS WHERE THIS LINE WENT WRONG (user, 2026-08-01). The Squire held
# his shield up in the air instead of in front of him. The Paladin's and the
# Crusader's holy symbols were too small to read as anything. And the Highlord sat
# too close to the Crusader, so the Highlord takes a great gilded tower shield and
# hands his radiant relic DOWN to the Crusader.
# Two arms follow from that: a shield arm, down and across the chest, and a relic
# arm, raised.
SHIELD_ARM = TIER in ("common", "legendary")
if SHIELD_ARM:
    tors.append(P.add_cone(scn, "upperR", (0.62, -0.20, 0.46), 0.115, 0.15, 0.48, PL, verts=8))
    tors.append(P.add_cone(scn, "foreR", (0.46, -0.46, 0.14), 0.125, 0.155, 0.48, PL, verts=8,
                           rot=(math.radians(70.6), 0, math.radians(135))))
    tors.append(P.add_sphere(scn, "fistR", (0.30, -0.62, 0.06), 0.16, PL))
else:
    tors.append(P.add_cone(scn, "upperR", (0.60, -0.16, 0.60), 0.115, 0.13, 0.46, PL, verts=8,
                           rot=(0, math.radians(22), 0)))
    tors.append(P.add_cone(scn, "foreR", (0.74, -0.42, 0.90), 0.125, 0.155, 0.46, PL, verts=8,
                           rot=(math.radians(-24), math.radians(16), 0)))
    tors.append(P.add_sphere(scn, "fistR", (0.80, -0.54, 1.14), 0.16, PL))
P.parent_all(tors_root, tors + hd_det)

# ---- what the off hand carries ----
roots = [tors_root]
radiance = []
if TIER == "common":
    # A boarded buckler, held in front of the chest where a shield belongs. It
    # used to float beside his head at z 2.56, which is what "holding it in the
    # sky" meant.
    sq_root = P.make_root(scn, "buckler_root", rot=(0, -12, 0), loc=(0.30, -0.88, 1.56))
    buckler = [P.add_cyl(scn, "bucklerface", (0, 0, 0), 0.46, 0.10, M["leath"], verts=12,
                         rot=(math.radians(90), 0, 0)),
               P.add_sphere(scn, "bucklerboss", (0, -0.09, 0), 0.15, M["steel"], segs=10, rings=6)]
    P.parent_all(sq_root, buckler)
    roots.append(sq_root)
elif LEGEND:
    # The Highlord's great tower shield, gilded. This is what separates him from
    # the Crusader, who now carries the radiant relic that used to be his.
    tower = [(-0.50, 0.86), (0.50, 0.86), (0.54, 0.10), (0.40, -0.62), (0.0, -0.94),
             (-0.40, -0.62), (-0.54, 0.10)]
    sh_root = P.make_root(scn, "shield_root", rot=(0, -12, 0), loc=(0.30, -0.88, 1.66))
    shield = [P.add_prism(scn, "shieldback", tower, 0.12, M["brightgold"]),
              P.add_prism(scn, "shieldface", [(x * 0.76, z * 0.80) for x, z in tower],
                          0.12, M["crimson"], loc=(0, -0.07, 0.02))]
    # His device is the same cross the Paladin raises, not a plain boss. It goes
    # in the no-outline bucket: the bars are about four pixels across at this
    # size and a 1.75px outline on each side would eat the shape.
    radiance = [P.add_box(scn, "shieldcross", (0, -0.16, 0.10), (0.19, 0.06, 0.98),
                          M["brightgold"]),
                P.add_box(scn, "shieldcrossbar", (0, -0.16, 0.36), (0.64, 0.06, 0.20),
                          M["brightgold"])]
    P.parent_all(sh_root, shield + radiance)
    roots.append(sh_root)
else:
    # A cross big enough to READ. At a 0.46 stem and a 0.34 bar it was a gold
    # speck in a raised fist and the developer could not tell what it was.
    hs_root = P.make_root(scn, "symbol_root", loc=(0.84, -0.60, 2.62))
    symbol = [P.add_box(scn, "symbolstem", (0, 0, 0.16), (0.12, 0.07, 0.70), GI),
              P.add_box(scn, "symbolbar", (0, 0, 0.26), (0.54, 0.07, 0.13), GI)]
    radiance = [P.add_sphere(scn, "symbolcore", (0, -0.05, 0.26),
                             0.10 if TIER == "rare" else 0.15, M["holy"], segs=8, rings=5)]
    if TIER == "epic":
        # the Highlord's old radiance, handed down
        for i in range(4):
            radiance.append(P.add_box(scn, "symbolray", (0, -0.07, 0.26), (0.78, 0.05, 0.07),
                                      M["holy"], rot=(0, math.radians(-i * 45), 0)))
    P.parent_all(hs_root, symbol + radiance)
    roots.append(hs_root)

# ---- the hammer in the low hand, sized to the man ----
# Written out per tier rather than derived from the haft length. Deriving them
# put epic's numbers a float's width off the originals, which was enough to
# change pixels on a sprite that must not change at all.
HAFT, HAFT_Z, HEAD_Z, HEAD = {
    "common":    (1.00, 0.36, 0.90, 0.80),
    "rare":      (1.14, 0.40, 1.02, 0.92),
    "epic":      (1.30, 0.46, 1.16, 1.00),
    "legendary": (1.46, 0.52, 1.30, 1.24),
}[TIER]
hm_root = P.make_root(scn, "hammer_root", rot=(0, -14, 0), loc=(-0.56, -0.72, 1.02))
hammer = [P.add_cyl(scn, "hammerhaft", (0, 0, HAFT_Z), 0.06, HAFT, M["wood"], verts=6),
          P.add_box(scn, "hammerhead", (0, 0, HEAD_Z),
                    (0.30 * HEAD, 0.28 * HEAD, 0.40 * HEAD), PL, bevel=0.05),
          P.add_box(scn, "hammerband", (0, 0, HEAD_Z),
                    (0.34 * HEAD, 0.32 * HEAD, 0.10), GI),
          P.add_box(scn, "hammergrip", (0, 0, -0.14), (0.10, 0.10, 0.24), M["leath"])]
P.parent_all(hm_root, hammer)
roots.append(hm_root)

H.finish(scn, px, "hero_paladin", figure, detail, noline, roots=roots,
         skip_extra=tuple(o.name for o in hd_det + radiance + visor),
         body_roots=[tors_root])
