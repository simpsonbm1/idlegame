"""Battle-mage -- M15_ASSET_SPECS.md entry 6.

The roster holds six staff-carrying casters, so this one is separated by the
ENERGY rather than the staff: a vertical crackle running up the shaft, where the
undead necromancer's flame sits on top and the orc warcaster's bolt is thrown
clear of the body.

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
# USER REVIEW 2026-08-01: "all the same guy with a different staff and hat", and
# the line was one of five filed under "same guy in different clothes". It was
# literally true in the code: one shared robe cone, one chest, one arm pose and
# one vertical staff, with only the head and the staff's tip branching.
#
# So the four differ in BODY SHAPE first, which is the thing a 112-pixel figure
# is read from. Four outlines, not four hats:
#
#   Adept       a narrow hooded cone. The smallest mass in the line.
#   Battlemage  a MAN, with armoured legs showing under a knee-length coat, and
#               a war-staff angled across his body instead of stood upright.
#   Warmage     an inverted triangle: a wide armoured mantle and pauldrons over
#               a robe, under a transverse-crested helm.
#   Archmage    a diamond: broad hat, narrow shoulders, the widest hem, and a
#               drawn sword lowered on the hand the staff is not in.
#
# Hue carries the second read, because four blues would not: undyed roughspun, a
# crimson war coat, deep azure, then violet. The arcane blue is the one thing
# they all share, and it is what makes them one line; the AMOUNT of it is the
# ladder, from a single spark to a contained storm.
#
# The Adept is UNDYED CREAM rather than the brown he was first built in. Brown
# roughspun over brown sleeves under a brown hood holding a brown staff came out
# as one solid figure with no internal edges at all -- "one material over a whole
# figure reads as carved wood" (README), and he read as exactly that. Undyed wool
# is pale anyway, and it gives his brown hood, belt and staff something to sit
# against.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

BODY = {"common": "cream", "rare": "crimson", "epic": "azure",
        "legendary": "violet"}[TIER]
BD = M[BODY]

figure, detail, noline = [], [], []
# Headgear goes under its own root so it is OUTLINED but NOT MEASURED. Height is
# not spendable: `spritekit.finish()` scales the assembled body to the role
# height, so a hat in `figure` makes the man under it smaller, and the Archmage
# would have paid for his hat by standing shorter than the Warmage. Weapons
# already dodge this by living on their own root; headgear needs the same.
crown_root = P.make_root(scn, "crown_root")
crown = []

SHOULDER_Z = 2.44
HEAD_AT = (0, -0.06, 2.88)

# ---- the body, which is where the four separate ----
if TIER == "common":
    # the Adept: roughspun, narrow, and carrying no metal at all
    figure.append(P.add_cone(scn, "robe", (0, 0, 0.95), 0.66, 0.34, 1.90, BD, verts=12))
    figure.append(P.add_cyl(scn, "ropebelt", (0, 0, 1.60), 0.41, 0.11, M["leath"], verts=10))
    figure.append(P.add_cone(scn, "chest", (0, 0, 2.12), 0.36, 0.31, 0.86, BD, verts=12))
    detail += S.tatters(scn, (0, -0.34, 0.10), 0.94, M["leath"], count=5, drop=0.14, seed=3)
elif TIER == "rare":
    # the Battlemage: a soldier who learned magic, so he is built like one. The
    # LEGS are the whole point -- he is the only figure in this line who is not
    # a cone, and that reads before his colour or his staff does.
    figure += H.legs(scn, M, 1.55, spread=0.36, mat=M["mail"], boot=M["charcoal"])
    figure.append(P.add_cone(scn, "coat", (0, 0, 1.70), 0.62, 0.42, 1.30, BD, verts=12))
    figure.append(P.add_box(scn, "warbelt", (0, -0.04, 1.92), (0.94, 0.50, 0.16), M["charcoal"]))
    figure.append(P.add_cone(scn, "chest", (0, 0, 2.12), 0.44, 0.38, 0.86, BD, verts=12))
    # Armour is WIDER than the body under it, or hide shows all round the plate
    # and he reads as an unarmoured man with a grey patch (the orc brute's rule).
    # It also sits LOW on the chest: at 2.16 both arms crossed in front of it and
    # the only part left showing was a narrow band that read as a scarf.
    figure += P.add_ridged(scn, "cuirass", (0, -0.12, 2.06), (0.96, 0.46, 0.90),
                           M["steel"], splay=12, bevel=0.06)
elif TIER == "epic":
    # the Warmage: a commander. WIDTH is what a tier can spend most cheaply on a
    # small figure, so he spends all of it -- mantle, pauldrons and a crest that
    # runs side to side rather than front to back.
    figure.append(P.add_cone(scn, "robe", (0, 0, 0.90), 0.88, 0.44, 1.80, BD, verts=12))
    figure.append(P.add_cone(scn, "chest", (0, 0, 2.12), 0.46, 0.40, 0.88, BD, verts=12))
    figure += P.add_ridged(scn, "cuirass", (0, -0.08, 2.14), (1.02, 0.46, 0.78),
                           M["steel"], splay=12, bevel=0.06)
    # ONE mass at the shoulder line, and it is the pauldrons. A wide shallow
    # mantle cone here as well fused with them and with the cuirass into a single
    # flat plate jutting out across his chest, which is the cones-fuse rule
    # collecting on the widest part of the figure. Spheres survive it where a
    # 0.32-deep cone cannot: they are curved, so the ramp lands three tones on
    # them, and they read as two bumps rather than one slab.
    for s in (-1, 1):
        figure.append(P.add_sphere(scn, "pauldron", (s * 0.68, -0.16, 2.50), 0.34,
                                   M["steel"], scale=(1.10, 0.86, 0.74), segs=10, rings=6))
    # a fauld ring standing proud of the robe, so the waist is a notch in the
    # outline rather than a smooth taper. The robe is 0.49 across here.
    figure.append(P.add_cyl(scn, "fauld", (0, 0, 1.66), 0.62, 0.22, M["steel"], verts=12))
else:
    # the Archmage: the widest hem in the line under the narrowest shoulders, so
    # the hat and the robe make a diamond with a waist in the middle of it.
    figure.append(P.add_cone(scn, "robe", (0, 0, 0.93), 0.98, 0.42, 1.86, BD, verts=12))
    figure.append(P.add_cone(scn, "overrobe", (0, 0.28, 1.32), 0.80, 0.40, 2.44,
                             M["navy"], verts=10))
    figure.append(P.add_cone(scn, "chest", (0, 0, 2.14), 0.42, 0.36, 0.88, BD, verts=12))
    figure.append(P.add_cyl(scn, "girdle", (0, 0, 1.74), 0.44, 0.13, M["brightgold"], verts=12))
    detail += S.tatters(scn, (0, -0.44, 0.10), 1.26, M["brightgold"], count=7,
                        drop=0.16, seed=5)

SH_R = {"common": 0.19, "rare": 0.21, "epic": 0.22, "legendary": 0.20}[TIER]
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.04, SHOULDER_Z), SH_R, BD,
                               scale=(1, .95, .8)))
if TRIM:
    detail.append(P.add_cyl(scn, "collarband", (0, -0.10, 2.68), 0.42, 0.09, TRIM, verts=10))

# ---- the head: a hood, a bare soldier, a war helm, a hat ----
if TIER == "common":
    # His own hood, not the shared one. A hood is only ever visible as the
    # MARGIN around a face, so it is bigger than the head and set BACK -- sized
    # to just clear the skull it renders entirely behind the man and he comes
    # out bare-headed (the goblin skulker's rule).
    # The hood is BROWN over the cream robe, which is the second mass his figure
    # needs. In the robe's own colour the hood, the head and the shoulders were
    # one continuous shape and he had no head at all.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure += [P.add_cone(scn, "hoodpeak", (0, 0.06, 2.99), 0.41, 0.09, 0.50, M["leath"], verts=10),
               P.add_sphere(scn, "hoodback", (0, 0.13, 2.88), 0.35, M["leath"],
                            scale=(1.0, 0.94, 1.04), segs=10, rings=6),
               P.add_cone(scn, "cowl", (0, 0.0, 2.56), 0.45, 0.27, 0.28, M["leath"], verts=10)]
elif TIER == "rare":
    # bare headed and cropped: the only uncovered head in the line
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "hair", (0, 0.04, 2.95), 0.29, M["charcoal"],
                               scale=(1.0, 1.0, 0.80), segs=12, rings=7))
elif TIER == "epic":
    # His own open-faced war helm, with a TRANSVERSE crest. Every other crest in
    # the roster runs front to back and therefore reads as nothing from a camera
    # that is nearly side-on; this one runs across and is a wide bar. It clears
    # the helm shell by 0.16, about four pixels a side, because a detail that
    # stays inside another part's hull does not exist.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    figure.append(P.add_sphere(scn, "helm", (0, -0.02, 2.94), 0.31, M["steel"],
                               scale=(0.96, 1.02, 0.94), segs=14, rings=8))
    for s in (-1, 1):
        figure.append(P.add_box(scn, "cheekguard", (s * 0.22, -0.18, 2.82),
                                (0.16, 0.30, 0.34), M["steel"], bevel=0.03))
    # It is an ARC that grows out of the helm, and a third of it is buried inside
    # the shell. Built as a tall box standing on top it read as a gold signboard
    # floating over his head: a rectangle has no shape that says "crest", and
    # anything that merely touches another part reads as a separate object.
    crown.append(P.add_prism(scn, "helmcrest",
                             [(-0.44, 0.0), (0.44, 0.0), (0.34, 0.28), (0.0, 0.46),
                              (-0.34, 0.28)],
                             0.11, TRIM, loc=(0, 0.0, 2.96)))
    detail.append(P.add_box(scn, "visorslit", (0, -0.32, 2.94), (0.40, 0.06, 0.08), M["dark"]))
else:
    # the Archmage: the broadest brim on any head in the roster, and a beard long
    # enough to change the outline of his chest rather than decorate his chin.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=0.27)
    crown.append(P.add_cone(scn, "hatbrim", (0, -0.04, 3.06), 0.70, 0.32, 0.11,
                            BD, verts=14))
    crown.append(P.add_cone(scn, "hatcone", (0, 0.02, 3.46), 0.32, 0.03, 0.78, BD,
                            rot=(math.radians(-9), 0, 0), verts=12))
    crown.append(P.add_cyl(scn, "hatband", (0, -0.02, 3.11), 0.34, 0.09,
                           M["brightgold"], verts=12))
    figure.append(P.add_cone(scn, "beard", (0, -0.30, 2.56), 0.22, 0.05, 0.72,
                             M["fur"], rot=(math.radians(180), 0, 0), verts=8))
figure += hd
detail += hd_det

# ---- arms, and where each man's hands are ----
# The LEFT arm holds the staff and its parts must keep the `armL_*` names, which
# is what `attack_roster.LIMB_L` addresses, so it stays on the shared limb
# builder. Limb construction is one of the things the kits are FOR; identity is
# not (user ruling 2026-08-02).
GRIP = {"common":    (-0.70, -0.58, 1.90),
        "rare":      (-0.84, -0.60, 1.76),
        "epic":      (-0.74, -0.60, 2.00),
        "legendary": (-0.76, -0.60, 2.02)}[TIER]
RHAND = {"common":    (0.64, -0.54, 1.84),
         "rare":      (0.76, -0.56, 1.98),
         "epic":      (0.70, -0.60, 2.30),
         "legendary": (0.62, -0.48, 1.98)}[TIER]
#
# USER 2026-08-02: "their hands are too big. compare them with the assassin."
# Measured, because the difference is about one pixel a side and eyeballing it
# would not have found the cause. This line scales to 0.91-0.93 and the assassin
# to 1.10-1.16, so at the stock radii his hands land at 0.158 world and these at
# 0.180. But the ratio is the real culprit: `S.limb` builds a hand 2.02 times the
# wrist it grows from, where the assassin's hand-written arms give 1.40. Half the
# mitt is a wrist too THIN. So the hand comes down to 0.170 and the forearm goes
# up to 0.14, which puts both within a pixel of his.
ARM = dict(upper_r=0.145, fore_r=0.14, hand_r=0.17, hand_mat=M["skin"])
figure += S.limb(scn, (-0.48, -0.12, SHOULDER_Z - 0.08), GRIP, BD, **ARM)
figure += S.limb(scn, (0.48, -0.12, SHOULDER_Z - 0.06), RHAND, BD, **ARM)
if TIER == "rare":
    # "reinforced robes with BRACERS" (entry 74). They ride the forearm, so they
    # are placed a fifth of the way from each fist back toward the shoulder
    # rather than at fixed coordinates, which is what left the assassin's
    # floating at his waist when his arms moved.
    for hx, hy, hz in (GRIP, RHAND):
        sx = -0.48 if hx < 0 else 0.48
        d = math.sqrt((sx - hx) ** 2 + (-0.12 - hy) ** 2 + (SHOULDER_Z - 0.08 - hz) ** 2)
        t = 0.22 / d
        figure.append(P.add_box(scn, "bracer",
                                (hx + (sx - hx) * t, hy + (-0.12 - hy) * t,
                                 hz + (SHOULDER_Z - 0.08 - hz) * t),
                                (0.30, 0.30, 0.24), M["steel"], bevel=0.03))

# Arcane runes on the sleeve: the only glow in the game sitting on CLOTH rather
# than at the end of something, which is what makes the line read as mages
# rather than as men holding lamps. The Adept has none, because an apprentice
# has not earned them; after that the count is part of the ladder.
RUNES = {"common": 0, "rare": 1, "epic": 2, "legendary": 3}[TIER]
for i in range(RUNES):
    for s in (-1, 1):
        z = 2.14 + i * 0.20
        noline.append(P.add_box(scn, "rune", (s * 0.56, -0.36, z),
                                (0.09, 0.05, 0.16), M["arcane"]))
        noline.append(P.add_box(scn, "runebar", (s * 0.56, -0.36, z - 0.13),
                                (0.17, 0.05, 0.06), M["arcane"]))
if TIER == "epic":
    # Entry 75 asks for a "glowing rune circlet", and the glow ended up in the
    # visor slit instead. A brow band had nowhere to sit that the crest's buried
    # base did not already occupy, and two lights inside a helm read at sprite
    # scale where a 0.07-tall band across a curved shell does not.
    for s in (-1, 1):
        noline.append(P.add_box(scn, "helmeye", (s * 0.10, -0.37, 2.94),
                                (0.09, 0.04, 0.06), M["arcane"]))

# USER 2026-08-02: "give the legendary a sword instead of a book for the
# offhand. like a gandalf staff-and-sword deal." He is the only caster in the
# roster carrying a weapon in the hand that is not on the staff, and it is what
# makes him read as the one who FIGHTS rather than the one who casts.
#
# It hangs LOWERED and angled OUT, 158 degrees about Y, which puts the point down
# and away from him. Every part of the blade then falls outside the robe's flare,
# so it reads as one clean diagonal on the side the staff does not occupy. Raised
# it would have crossed the hat, which is his other read. A weapon overlapping a
# body has to separate by VALUE at this size, and pale steel on violet does.
sword_root = None
if LEGEND:
    sword_root = P.make_root(scn, "sword_root", rot=(0, 158, 0), loc=(0.62, -0.52, 1.98))
    P.parent_all(sword_root, [
        # 1.55 long, which is 36 pixels on a 75-pixel man. At the 1.18 it started
        # at it came out 27 and read as a long dagger rather than a sword.
        P.add_prism(scn, "swblade",
                    [(-0.085, 0.0), (0.085, 0.0), (0.085, 1.32), (0.0, 1.55),
                     (-0.085, 1.32)],
                    0.055, M["blade"], loc=(0, 0, 0.20)),
        P.add_box(scn, "swguard", (0, 0, 0.17), (0.46, 0.10, 0.09), TRIM, bevel=0.02),
        P.add_box(scn, "swgrip", (0, 0, 0.0), (0.075, 0.075, 0.26), M["leath"]),
        P.add_sphere(scn, "swpommel", (0, 0, -0.17), 0.08, TRIM, segs=8, rings=5)])

# ---- the staff, one per man ----
# The Battlemage's is ANGLED across his body and everyone else's is upright,
# which is the second silhouette break in the line after the legs.
# The rare angle came down from 24 to 12 and the grip moved out to -0.84,
# because a staff tilted top-toward-the-body swings its head across the face.
# The tilt is measured against the HEAD, which spans -0.27 to 0.27: the iron cap
# now lands at -0.55, seven pixels clear of his cheek, and 12 degrees over this
# shaft still leans ten pixels, so it reads as angled rather than upright. The
# lean is his second silhouette break after the legs, and it is the only staff
# in the line that is not vertical.
ST_ROT = {"common": (0, -6, 0), "rare": (0, 12, 0),
          "epic": (0, -6, 0), "legendary": (0, -5, 0)}[TIER]
# 2.95 for the rare, up from 2.30: losing the spearhead cost the staff the 0.56
# it projected past the shaft, and the top dropped below his own head.
SHAFT = {"common": 2.55, "rare": 2.95, "epic": 3.05, "legendary": 3.10}[TIER]
st_root = P.make_root(scn, "staff_root", rot=ST_ROT, loc=GRIP)
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.058, SHAFT, M["wood"], verts=6)]
glow = []

if TIER == "common":
    # a plain crooked stick: no bands, no metal, no cradle. He is a student.
    glow.append(P.add_sphere(scn, "arccore", (0, -0.02, 1.30), 0.10, M["arcane"],
                             segs=10, rings=7))
elif TIER == "rare":
    # USER 2026-08-02: "he does read like a spearman, go for the staff." The leaf
    # blade was doing it on its own -- a point on a long shaft is a polearm
    # whatever the man holding it is wearing, and no amount of robe fixed it.
    # An iron shoe at BOTH ends is what says quarterstaff rather than haft: one
    # cap alone reads as the business end of something.
    staff.append(P.add_cone(scn, "staffhead", (0, 0, 1.36), 0.095, 0.125, 0.30,
                            M["steel"], verts=8))
    staff.append(P.add_cone(scn, "buttshoe", (0, 0, -1.36), 0.125, 0.095, 0.30,
                            M["steel"], verts=8))
    for z in (-0.60, 0.60):
        staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.085, 0.09, TRIM, verts=6))
    # The core wells out of the iron head instead of tipping it like a spearpoint,
    # and it sits 0.14 above his own head so it reads as the staff's rather than
    # as a plume on his. The other three carry theirs well clear; at the shaft
    # length this started at, his landed exactly level with his temple.
    glow.append(P.add_sphere(scn, "arccore", (0, -0.02, 1.58), 0.14, M["arcane"],
                             segs=10, rings=7))
    for i in range(3):
        glow.append(P.add_box(scn, "arcbolt", (0.10 * (1 if i % 2 else -1), -0.06, 0.30 + i * 0.24),
                              (0.16, 0.05, 0.07), M["arcane"],
                              rot=(0, math.radians(38 * (1 if i % 2 else -1)), 0)))
elif TIER == "epic":
    for z in (-1.05, -0.25, 0.55):
        staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.085, 0.09, TRIM, verts=6))
    staff.append(P.add_cone(scn, "cradle", (0, 0, 1.20), 0.17, 0.08, 0.24, TRIM, verts=8))
    for i in range(4):
        staff.append(P.add_box(scn, "cagebar", (0, 0, 1.62), (0.46, 0.06, 0.07), M["steel"],
                               rot=(0, math.radians(-i * 45), 0)))
    staff.append(P.add_cyl(scn, "cagering", (0, 0, 1.62), 0.25, 0.07, M["steel"], verts=12,
                           rot=(math.radians(90), 0, 0)))
    glow.append(P.add_sphere(scn, "arccore", (0, -0.02, 1.62), 0.19, M["arcane"],
                             segs=10, rings=7))
    for i in range(6):
        glow.append(P.add_box(scn, "arcbolt", (0.10 * (1 if i % 2 else -1), -0.06, 0.16 + i * 0.24),
                              (0.16, 0.05, 0.07), M["arcane"],
                              rot=(0, math.radians(38 * (1 if i % 2 else -1)), 0)))
    # sigils orbiting the cage, which is entry 75's read
    for dx, dz in ((-0.40, 1.44), (0.40, 1.80), (0.0, 2.02)):
        glow.append(P.add_box(scn, "arcsigil", (dx, -0.04, dz), (0.13, 0.05, 0.13), M["arcane"]))
else:
    for z in (-1.10, -0.30, 0.50):
        staff.append(P.add_cyl(scn, "band", (0, 0, z), 0.085, 0.09, TRIM, verts=6))
    staff.append(P.add_cone(scn, "cradle", (0, 0, 1.22), 0.18, 0.08, 0.26, TRIM, verts=8))
    staff.append(P.add_cyl(scn, "orbring", (0, 0, 1.70), 0.36, 0.08, TRIM, verts=14,
                           rot=(math.radians(90), 0, 0)))
    glow.append(P.add_sphere(scn, "arccore", (0, -0.02, 1.70), 0.26, M["arcane"],
                             segs=10, rings=7))
    for i in range(8):
        glow.append(P.add_box(scn, "arcbolt", (0.10 * (1 if i % 2 else -1), -0.06, 0.10 + i * 0.22),
                              (0.16, 0.05, 0.07), M["arcane"],
                              rot=(0, math.radians(38 * (1 if i % 2 else -1)), 0)))
    # the contained storm: motes thrown clear of the orb on every side
    for dx, dz in ((-0.44, 1.50), (0.44, 1.62), (-0.22, 2.06), (0.30, 2.10), (0.0, 2.28)):
        glow.append(P.add_sphere(scn, "arcmote", (dx, -0.04, dz), 0.085, M["arcane"],
                                 segs=8, rings=5))

P.parent_all(st_root, staff + glow)
P.parent_all(crown_root, crown)

H.finish(scn, px, "hero_battlemage", figure, detail, noline,
         roots=[st_root, crown_root] + ([sword_root] if sword_root else []),
         skip_extra=tuple(o.name for o in glow))
