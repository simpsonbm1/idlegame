"""Frost adept -- M15_ASSET_SPECS.md entry 8.

The palest robed figure after the healer, and the two are separated by
temperature: cream and gold against ice-blue and white. On a battle line the
healer reads warm and this one cold, which is as much as two support-shaped
silhouettes need.

Her snowflakes are separate small blocks scattered around the staff head rather
than a cloud. Scattered points read as falling; a mass reads as smoke, which is
what the first infernal flame looked like before it was made to climb.

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
# The frost line: Frost Apprentice, Frost Adept, Rimecaller, Winter's Voice
# (DESIGN.md).
#
# USER REVIEW 2026-08-01: "at scale they effectively look the exact same." This
# was the hardest line to separate and the code had not tried: one robe cone at
# one width, one arm pose, one wooden staff, and every tier in the SAME pale
# ice-blue, so the only differences were a hood swapped for hair and a few
# crystals. The Rimecaller's ice shards were modelled in `ice` growing out of an
# `ice` robe, which is to say they were invisible.
#
# ICE ACCUMULATES up this line, which is the one escalation that suits a cold
# mage, and it is spent on BODY SHAPE first:
#
#   Frost Apprentice  narrow-hemmed and buried in a borrowed fur wrap. A person
#                     who is COLD, not a person made of cold.
#   Frost Adept       the clean one: no shoulder mass at all, a high standing
#                     collar, bare head, long pale hair.
#   Rimecaller        ice bursting out of her shoulders and back, asymmetric, the
#                     only broken outline in the line.
#   Winter's Voice    the widest hem, a train behind her, a tall crown. More ice
#                     than person.
#
# Hue does the second job, and the ladder runs DARK TO PALE because becoming
# winter is this line's whole arc: charcoal wool, then ice blue, then a deep
# azure, then near-white. The frost itself is the one thing all four share.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

BODY = {"common": "charcoal", "rare": "ice", "epic": "azure",
        "legendary": "fur"}[TIER]
BD = M[BODY]
# Her ornament is ICE, not the gold the ladder would otherwise hand her. A gold
# collar and a gold staff-cradle on Winter's Voice read as a warm figure wearing
# a cold hat, which is the one thing this hero cannot be. `TRIM` still gates
# WHETHER a tier gets ornament at all; only the material is overridden.
ORN = {"common": None, "rare": M["ice"], "epic": M["frost"],
       "legendary": M["frost"]}[TIER]

figure, detail, noline = [], [], []

# ---- the body, which is where the four separate ----
HEM = {"common": 0.70, "rare": 0.84, "epic": 0.86, "legendary": 1.00}[TIER]
figure.append(P.add_cone(scn, "robe", (0, 0, 0.87), HEM, 0.40, 1.74, BD, verts=12))
figure.append(P.add_cyl(scn, "hemfur", (0, 0, 0.10), HEM + 0.04, 0.20, M["fur"], verts=12))
figure.append(P.add_cone(scn, "chest", (0, 0, 2.08), 0.44, 0.38, 0.88, BD, verts=12))
figure.append(P.add_box(scn, "sash", (0, -0.40, 1.66), (0.58, 0.09, 0.13), M["fur"]))

# ONE mass at the shoulder line, and each tier's is a different object. Stacking
# a mantle and a collar and shards all at this height fuses them into one flat
# plate, which is what the warmage's deleted mantle cost to learn.
if TIER == "common":
    # A heavy fur wrap he is buried in, built as TWO OVERLAPPING SPHERES across
    # the shoulders rather than as a cone. As a cone it was wide at the bottom
    # and narrow at the neck, which is a shape that flares DOWNWARD over the
    # chest, and at 112 pixels on a dark robe it read as a white bib rather than
    # as fur (user 2026-08-02: "i dont really understand the white cone under the
    # common one's head"). What says fur-over-the-shoulders is a mass that is
    # wide horizontally and SHORT vertically, following the shoulder line. The
    # two spheres share a material and overlap at the centre, so the inverted-hull
    # outline draws no seam between them and they read as one wrap.
    for s in (-1, 1):
        figure.append(P.add_sphere(scn, "furwrap", (s * 0.34, -0.02, 2.46), 0.36,
                                   M["fur"], scale=(1.15, 0.95, 0.62), segs=12, rings=7))
elif TIER == "rare":
    # a high collar standing BEHIND the head instead of a mantle lying on the
    # shoulders: the only vertical shoulder line in the roster, and the only tier
    # here with no bulk on the shoulders at all.
    figure.append(P.add_cone(scn, "collar", (0, 0.26, 2.72), 0.54, 0.30, 0.72,
                             M["fur"], verts=12))
elif TIER == "epic":
    pass          # her shards are built below, on their own root
else:
    # Winter's Voice. She has NO fur mantle: her SHOULDERS ARE ICE, built below
    # on the ice root. Two reasons. The Rimecaller was out-doing her at the one
    # thing this line escalates -- the legendary carried a crown and no shoulder
    # ice at all, so the tier below her had more of it. And the mantle was the
    # same downward-flaring cone the apprentice's fur was, which read as a bib
    # (user 2026-08-02, of the common: "i dont really understand the white cone
    # under the common one's head", and of this one: "legendary appears to have a
    # bib too").
    figure.append(P.add_cone(scn, "train", (0, 0.30, 1.24), 0.86, 0.42, 2.30,
                             M["ice"], verts=10))
    # A NAVY gown down the front, because a figure this pale has nothing to read
    # against. Near-white robe, near-white sleeves and pale-blue ice came out as
    # one washed mass with no internal edges; one dark vertical is enough to give
    # every white thing on her a value to sit against.
    figure.append(P.add_box(scn, "gown", (0, -0.40, 1.60), (0.44, 0.10, 1.60), M["navy"]))

for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, 2.42), 0.22, BD,
                               scale=(1, .95, .8)))
if ORN:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.66), 0.44, 0.09, ORN, verts=10))

# ---- the head ----
HEAD_AT = (0, -0.06, 2.86)
if TIER == "common":
    # Hood up, because he is the one who feels the cold. The hood is the ROBE's
    # charcoal and not fur: in fur it met the fur wrap below it and the two fused
    # into a single white mass covering his head and his whole chest, which is the
    # overlapping-cones rule collecting at the shoulder line again. Dark hood,
    # white collar, dark robe reads as three bands instead of one blob.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure += [P.add_cone(scn, "hoodpeak", (0, 0.06, 2.97), 0.42, 0.10, 0.52, BD, verts=10),
               P.add_sphere(scn, "hoodback", (0, 0.13, 2.86), 0.36, BD,
                            scale=(1.0, 0.94, 1.04), segs=10, rings=6)]
elif TIER == "rare":
    # bare headed, long pale hair swept back over the collar
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.06, 2.92), 0.30, M["fur"],
                               scale=(1.0, 1.06, 0.94), segs=12, rings=7))
    figure.append(P.add_cone(scn, "hairfall", (0, 0.22, 2.62), 0.26, 0.10, 0.56, M["fur"], verts=9))
elif TIER == "epic":
    # a ring of rime spikes growing straight out of the skull, uneven on purpose
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.04, 2.90), 0.29, M["fur"],
                               scale=(1.0, 1.0, 0.88), segs=12, rings=7))
    for sx, hgt in ((-0.22, 0.44), (-0.08, 0.62), (0.09, 0.50), (0.23, 0.36)):
        figure.append(P.add_cone(scn, "rimespike", (sx, -0.02, 3.08), 0.065, 0.0, hgt,
                                 M["fur"], rot=(0, math.radians(sx * 70), 0), verts=5))
else:
    # a tall crown of ice on a bare head. It is `ice` on her near-white body, and
    # it goes on its OWN root so it is outlined but not measured -- height is not
    # spendable, and a crown in `figure` shrinks the woman wearing it.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.06, 2.92), 0.30, M["fur"],
                               scale=(1.0, 1.04, 0.92), segs=12, rings=7))
figure += hd
detail += hd_det

# Everything that GROWS out of her rides its own root: outlined by `outline_all`,
# which walks the whole scene, but never measured by `finish()`. Height is not
# spendable -- a crown or a shard listed in `figure` makes the woman under it
# shorter to pay for itself.
ice_root = P.make_root(scn, "ice_root")
ice = []
if TIER == "epic":
    # Ice growing OUT of her, and the only broken outline in the line. Two things
    # had to be fixed before any of it existed. It was modelled in `ice` on an
    # `ice` robe, so it was invisible; her body went deep azure and the shards
    # near-white. And the rotation was `-s * 90 + ang`, which aimed every shard
    # back INTO her chest and downward -- a cone's axis is local +Z, so +Z maps
    # to (sin ry, 0, cos ry) and pointing a left-side shard outward and up needs
    # ry NEGATIVE. It is `s * ang` now, and the tips clear her shoulder by five
    # pixels rather than sitting a centimetre inside it.
    # SHORT AND FAT, not long and thin: at 0.13 across a 1.20 length they tapered
    # away within a couple of pixels and read as antennae, where ice is a chunk.
    #
    # And each one is anchored at its BASE. `add_cone` centres on the location it
    # is given, so half of every shard sat inside her and the visible halves read
    # as a fringe on the collar rather than as spikes. The centre is computed from
    # the base and the direction instead, which puts the whole length outside her
    # and the tips eleven pixels past the shoulder they grow from.
    for s, bx, bz, ang, ln, r in ((-1, 0.40, 2.34, 58, 0.85, 0.20),
                                  (1, 0.42, 2.50, 48, 0.78, 0.19),
                                  (-1, 0.36, 2.62, 76, 0.66, 0.17),
                                  (1, 0.38, 2.20, 70, 0.70, 0.17)):
        a = math.radians(ang)
        dx, dz = s * math.sin(a), math.cos(a)
        ice.append(P.add_cone(scn, "shard",
                              (s * bx + dx * ln / 2, 0.08, bz + dz * ln / 2),
                              r, 0.0, ln, M["fur"],
                              rot=(0, math.radians(s * ang), 0), verts=5))
elif LEGEND:
    # She has to out-do the Rimecaller at ice, so she gets SIX shoulder shards to
    # her four and each is bigger, plus spikes rising off the hem and a crown half
    # again as tall. Same base-anchored construction as the Rimecaller's.
    for s, bx, bz, ang, ln, r in ((-1, 0.42, 2.36, 55, 1.00, 0.23),
                                  (1, 0.44, 2.52, 45, 0.94, 0.22),
                                  (-1, 0.38, 2.66, 72, 0.80, 0.19),
                                  (1, 0.40, 2.22, 68, 0.86, 0.21),
                                  (-1, 0.34, 2.08, 80, 0.72, 0.18),
                                  (1, 0.34, 2.74, 60, 0.70, 0.18)):
        a = math.radians(ang)
        dx, dz = s * math.sin(a), math.cos(a)
        ice.append(P.add_cone(scn, "shard",
                              (s * bx + dx * ln / 2, 0.08, bz + dz * ln / 2),
                              r, 0.0, ln, M["ice"],
                              rot=(0, math.radians(s * ang), 0), verts=5))
    # ice growing UP off the hem, so the bottom of her outline is frozen too
    for s, bx, ang, ln, r in ((-1, 0.74, 18, 0.62, 0.14), (1, 0.80, 14, 0.70, 0.15),
                              (-1, 0.50, 10, 0.48, 0.12), (1, 0.54, 22, 0.52, 0.13)):
        a = math.radians(ang)
        dx, dz = s * math.sin(a), math.cos(a)
        ice.append(P.add_cone(scn, "hemspike",
                              (s * bx + dx * ln / 2, -0.06, 0.14 + dz * ln / 2),
                              r, 0.0, ln, M["ice"],
                              rot=(0, math.radians(s * ang), 0), verts=5))
    for s in (-2, -1, 0, 1, 2):
        ice.append(P.add_cone(scn, "icecrown", (s * 0.15, -0.08, 3.10),
                              0.07, 0.0, 0.50 + (2 - abs(s)) * 0.26, M["ice"],
                              rot=(0, math.radians(s * 13), 0), verts=5))
P.parent_all(ice_root, ice)

# ---- arms ----
# The hand numbers the battlemage and mender share, per the 2026-08-02 sizing
# rule in README.md: the stock `limb()` hand is 2.02x the wrist it grows from
# where the assassin's is 1.40, and half of a mitt is a wrist too thin.
ARM = dict(upper_r=0.145, fore_r=0.14, hand_r=0.17, hand_mat=M["skin"])
figure += S.limb(scn, (-0.48, -0.12, 2.34), (-0.68, -0.56, 1.82), BD, **ARM)
figure += S.limb(scn, (0.48, -0.12, 2.36), (0.68, -0.58, 2.30), BD, **ARM)

# ---- the staff, which ices over as she does ----
SHAFT_MAT = M["ice"] if LEGEND else M["wood"]
st_root = P.make_root(scn, "staff_root", rot=(0, -9, 0), loc=(-0.72, -0.60, 1.94))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.056, 2.80, SHAFT_MAT, verts=6)]
for z in (-0.96, -0.16, 0.64):
    staff.append(P.add_cyl(scn, "lash", (0, 0, z), 0.08, 0.08,
                           ORN or M["fur"], verts=6))
staff.append(P.add_cone(scn, "cradle", (0, 0, 1.36), 0.16, 0.08, 0.22,
                        ORN or M["steel"], verts=8))
CR = {"common": 0.84, "rare": 1.00, "epic": 1.20, "legendary": 1.34}[TIER]
crystal = [P.add_cone(scn, "crystal", (0, -0.02, 1.66), 0.15 * CR, 0.0, 0.46 * CR, M["frost"], verts=6),
           P.add_cone(scn, "crystalbase", (0, -0.02, 1.50), 0.15 * CR, 0.0, 0.24 * CR, M["frost"], verts=6,
                      rot=(math.radians(180), 0, 0))]
if TIER == "rare":
    # three small crystals held in a ring rather than one on the tip
    for ang in (0, 120, 240):
        crystal.append(P.add_cone(scn, "ringcrystal",
                                  (0.30 * math.cos(math.radians(ang)), -0.04,
                                   1.66 + 0.30 * math.sin(math.radians(ang))),
                                  0.08, 0.0, 0.26, M["frost"],
                                  rot=(0, math.radians(ang), 0), verts=5))
elif TIER == "epic":
    # a cluster: the Rimecaller's staff has grown as much ice as she has
    for dx, dz, hgt in ((-0.26, 1.54, 0.34), (0.24, 1.62, 0.30), (-0.16, 1.94, 0.26),
                        (0.20, 1.98, 0.22)):
        crystal.append(P.add_cone(scn, "clustercrystal", (dx, -0.04, dz), 0.09, 0.0, hgt,
                                  M["frost"], rot=(0, math.radians(dx * 90), 0), verts=5))
elif TIER == "legendary":
    # a broken ring standing clear of the tip, which no other staff in the game has
    for ang in range(0, 360, 40):
        if 150 < ang < 210:
            continue
        crystal.append(P.add_box(scn, "haloshard",
                                 (0.46 * math.cos(math.radians(ang)), -0.05,
                                  1.96 + 0.46 * math.sin(math.radians(ang))),
                                 (0.10, 0.05, 0.16), M["frost"],
                                 rot=(0, math.radians(-ang), 0)))

# snowflakes: scattered points, not a cloud. Points read as falling; a mass reads
# as smoke. The count is part of the ladder.
FLAKES = {"common": 3, "rare": 5, "epic": 8, "legendary": 10}[TIER]
for i, (dx, dz) in enumerate((((-0.30, 1.30), (0.28, 1.52), (-0.22, 1.92), (0.32, 2.02),
                               (0.02, 2.20), (-0.34, 1.68), (0.40, 1.32), (-0.42, 2.20),
                               (0.16, 2.44), (-0.10, 2.62))[:FLAKES])):
    crystal.append(P.add_box(scn, "snowflake", (dx, -0.06, dz),
                             (0.075, 0.05, 0.075), M["frost"],
                             rot=(0, math.radians(i * 29), 0)))
P.parent_all(st_root, staff + crystal)

H.finish(scn, px, "hero_frostadept", figure, detail, noline,
         roots=[st_root, ice_root], skip_extra=tuple(o.name for o in crystal))
