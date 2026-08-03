"""Banneret -- M15_ASSET_SPECS.md entry 7.

The banner is the tallest object on any hero and the only large FLAT surface in
the roster. It breaks the top of his cell and hangs well clear of his body, so he
is identifiable from further away than anything else the player owns, which is
the point of a standard-bearer.

He needs a 160 cell for the pole. The figure inside it is a normal 2.95 units
like every other hero; only the banner needs the headroom.

**His banner IS his weapon** (user 2026-08-02): the pole carries a polearm head
above the flag, and he has no sword. Four heads, escalating in mass and in the
number of things they can do to a man -- spear, glaive, bardiche, halberd.

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
px = H.start(scn, res=160)
M = H.palette()
TRIM = H.trim_mat(M)        # None on a common hero: plain and field-worn
GLOW = H.glow_mat(M)        # epic and legendary only
LEGEND = H.is_legendary()

# ---------------------------------------------------------------------------
# The banneret line: Herald, Banneret, Marshal, High Marshal (DESIGN.md).
#
# USER REVIEW 2026-08-01: "the banner is the only at-a-glance difference, and the
# legendary's banner covers his face." Both were literally true. All four wore
# one identical steel body -- same legs, same cuirass, same belt, same arms, same
# shared helm -- and only the flag panel, the surcoat colour and the pauldron
# radius branched. So the FOUR MEN are now four builds, and the flag is what they
# carry rather than what they are:
#
#   Herald       no plate at all: a quilted gambeson, cloth legs, and the only
#                BARE HEAD in the line. A messenger, not a knight.
#   Banneret     half-plate and a closed great helm. Faceless, and the only one.
#   Marshal      command plate, the broadest shoulders, an open barbute under a
#                tall transverse plume.
#   High Marshal gold-chased regalia, a crimson cloak, a crowned winged helm.
#
# The FIELD stays crimson on all four on purpose. They serve one crown, so four
# different flag colours would read as four armies; what escalates is the gold on
# it and the shape of it. Four shapes nobody could confuse: a small forked
# standard, a long tapering pennon, a wide gonfalon on a gilded crossbar, and a
# great square with a streaming tail.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

FL = M["crimson"]
POLE_MAT = M["brightgold"] if LEGEND else M["wood"]

figure, detail, noline = [], [], []

# ---- the body: four builds, not one ----
# The LIMBS carry the escalation as much as the plate does, and they do it by
# VALUE. One material over a whole figure reads as carved wood (README): built
# entirely in `steel` these three came out as blue mannequins, exactly as the
# Herald came out as a brown one. So the ladder is cloth, then mail showing under
# half-plate, then full plate, then gilded full plate -- and dark mail limbs
# against a bright steel cuirass is what gives the middle two any internal edge.
#
# THE ARM'S VALUE BREAK GOES AT THE ELBOW, NEVER AT THE WRIST. This is the
# approved fighter's arrangement and the reason his hands read: his forearm and
# his fist share one material, so the hand is the end of the vambrace rather than
# a ball stuck on it. Split the other way -- a bright steel gauntlet closing a
# dark mail sleeve -- and the fist reads as one more joint however well its cap
# is buried, which is what these still did after the geometry was rebuilt.
UPPER = {"common": "mail", "rare": "mail", "epic": "steel", "legendary": "steel"}[TIER]
CUFF = {"common": "leath", "rare": "steel", "epic": "steel", "legendary": "brightgold"}[TIER]
UP, CU = M[UPPER], M[CUFF]
HIP = 1.18
if TIER == "common":
    # the Herald. Cloth and leather, no plate anywhere, and a narrow frame: he is
    # the only one in the line who could run a message rather than hold a line.
    figure += H.legs(scn, M, HIP, spread=0.30, mat=M["charcoal"], boot=M["leath"])
    figure.append(P.add_box(scn, "skirt", (0, 0, HIP), (0.74, 0.50, 0.34), M["leath"], bevel=0.05))
    CHEST_R, LEAN = 0.40, 8
elif TIER == "rare":
    # the Banneret. HALF-plate, so the mail under it has to show: plate cuirass
    # over mail legs and mail sleeves.
    figure += H.legs(scn, M, HIP, spread=0.34, mat=M["mail"], boot=M["leath"])
    figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.86, 0.54, 0.30), M["steel"], bevel=0.05))
    CHEST_R, LEAN = 0.46, 6
elif TIER == "epic":
    # the Marshal. Full command plate, no mail left showing, and the widest man
    # in the line.
    figure += H.legs(scn, M, HIP, spread=0.38, mat=M["steel"], boot=M["charcoal"])
    figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.98, 0.58, 0.38), M["steel"], bevel=0.05))
    figure.append(P.add_cyl(scn, "fauld", (0, 0, HIP + 0.20), 0.60, 0.18, TRIM, verts=12))
    CHEST_R, LEAN = 0.50, 4
else:
    # the High Marshal. Gold-chased plate under a crimson cloak.
    figure += H.legs(scn, M, HIP, spread=0.38, mat=M["steel"], boot=M["charcoal"])
    figure.append(P.add_box(scn, "tassets", (0, 0, HIP), (0.98, 0.58, 0.40), M["steel"], bevel=0.05))
    figure.append(P.add_cyl(scn, "fauld", (0, 0, HIP + 0.22), 0.64, 0.20, TRIM, verts=12))
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.58, height=1.72,
                      r_base=0.64, r_top=0.32, y=0.48)
    CHEST_R, LEAN = 0.50, 5

BODY = M["leath"] if TIER == "common" else M["steel"]
tors_root, tors = H.torso(scn, M, HIP + 0.16, chest_r=CHEST_R, lean=LEAN, mat=BODY)

if TIER == "common":
    # a quilted gambeson: horizontal padding rolls, which is the cheapest armour
    # in the game and has to LOOK like cloth rather than like unpainted plate
    for i, z in enumerate((0.22, 0.44, 0.66)):
        tors.append(P.add_box(scn, "quilt", (0, -0.30, z), (0.78, 0.16, 0.13), M["leath"]))
    tors.append(P.add_cyl(scn, "mailcollar", (0, -0.04, 0.86), 0.36, 0.14, M["mail"], verts=10))
else:
    tors += P.add_ridged(scn, "cuirass", (0, -0.06, 0.50),
                         (0.98 if TIER == "rare" else 1.08, 0.46, 0.74), M["steel"],
                         splay=13, bevel=0.07)
tors.append(P.add_box(scn, "surcoat", (0, -0.34, 0.20), (0.48, 0.08, 1.00), FL))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.06), (0.94, 0.56, 0.15), M["leath"]))
if TRIM:
    tors.append(P.add_box(scn, "surcoatedge", (0, -0.38, 0.20), (0.12, 0.05, 1.00), TRIM))

# ---- the head: four of his own, and the shared helm is gone ----
# USER RULING 2026-08-02: every character and variant is individually designed.
# `hero_kit.head(helm=...)` used to dress all four of these, and it read as a soft
# cap on every one -- the same failure the paladin's three helms were built to fix.
HEAD_AT = (0, -0.04, 1.08)
hd, hd_det = H.head(scn, M, HEAD_AT, r=0.30)
tors += hd
if TIER == "common":
    # bare-headed, and the ONLY uncovered head in the line. His whole tier reads
    # off it: three helmed knights and one young man who has not earned one.
    tors.append(P.add_sphere(scn, "hair", (0, 0.06, 1.15), 0.32, M["leath"],
                             scale=(1.0, 1.0, 0.80), segs=12, rings=7))
elif TIER == "rare":
    # his own closed great helm: a flat-topped cylinder, faceless, with a cross
    # of slits cut into it. Nothing else in the roster is a straight-sided head.
    tors.append(P.add_cyl(scn, "greathelm", (0, -0.04, 1.14), 0.35, 0.62, M["steel"],
                          verts=12, scale=(1.0, 0.94, 1.0)))
    tors.append(P.add_cone(scn, "helmcrown", (0, -0.04, 1.46), 0.35, 0.24, 0.12,
                           M["steel"], verts=12))
    detail.append(P.add_box(scn, "visorslit", (0, -0.36, 1.20), (0.46, 0.08, 0.07), M["dark"]))
    detail.append(P.add_box(scn, "visorbar", (0, -0.36, 1.10), (0.09, 0.08, 0.30), M["dark"]))
elif TIER == "epic":
    # an open barbute under a TRANSVERSE plume. The face is bare, which is the
    # deliberate opposite of the tier below him, and the plume runs side to side
    # so it is a wide bar rather than a line the camera cannot see.
    tors.append(P.add_sphere(scn, "barbute", (0, -0.02, 1.16), 0.34, M["steel"],
                             scale=(0.98, 1.02, 0.94), segs=14, rings=8))
    for s in (-1, 1):
        tors.append(P.add_box(scn, "cheekguard", (s * 0.24, -0.20, 1.04),
                              (0.17, 0.32, 0.36), M["steel"], bevel=0.03))
    tors.append(P.add_prism(scn, "plume",
                            [(-0.46, 0.0), (0.46, 0.0), (0.35, 0.30), (0.0, 0.48),
                             (-0.35, 0.30)],
                            0.12, FL, loc=(0, 0.0, 1.20)))
else:
    # a crowned great helm with wings. The wings are the widest thing on any head
    # in the roster and they clear the shell by 0.30, because a detail that stays
    # inside another part's hull does not exist.
    tors.append(P.add_sphere(scn, "greathelm", (0, -0.02, 1.16), 0.35, M["steel"],
                             scale=(0.98, 1.04, 0.98), segs=14, rings=8))
    tors.append(P.add_cyl(scn, "crown", (0, -0.02, 1.44), 0.34, 0.16, M["brightgold"], verts=12))
    for i in range(5):
        tors.append(P.add_cone(scn, "crownpoint", (-0.26 + i * 0.13, -0.06, 1.58),
                               0.05, 0.0, 0.20, M["brightgold"], verts=6))
    for s in (-1, 1):
        # pulled in from 0.62 to 0.56: the far wing reached x -0.92 against a
        # banner pole standing at -0.94, and the two touched.
        tors.append(P.add_prism(scn, "helmwing",
                                [(0.0, -0.10), (0.56, 0.16), (0.54, 0.40), (0.10, 0.26)],
                                0.05, M["brightgold"],
                                loc=(s * 0.26, 0.08, 1.20),
                                rot=(0, 0, math.radians(s * 90 - 90))))
    detail.append(P.add_box(scn, "visorslit", (0, -0.36, 1.18), (0.46, 0.08, 0.07), M["dark"]))
if GLOW:
    noline.append(P.add_box(scn, "crest", (0, 0.10, 1.62), (0.09, 0.26, 0.18), GLOW))

# ---- arms ----
# `pauldron` is the pivot `attack_roster.py` swings his sword arm about, and
# HERO_ARM_R names upperR/foreR/fistR, so those five names are fixed.
#
PAULD = {"common": 0.24, "rare": 0.30, "epic": 0.36, "legendary": 0.37}[TIER]
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "pauldron", (s * 0.58, -0.08, 0.72), PAULD,
                             M["mail"] if TIER == "common" else M["steel"],
                             scale=(1, .95, .84)))
def _arm(side, shoulder, elbow, hand):
    """The fighter's arm chain, which is the only one that does not read as a
    stack of parts (user 2026-08-02: these had "the arms-with-extra-joints
    problem that we had to solve on the fighters").

    These were four fixed cylinders with a ball on the end, and the geometry was
    worse than it looked: the forearm was 0.46 long across a 0.91 gap between the
    upper arm's end and the fist, so the segments did not even meet. Every
    segment is now AIMED between two named joints and TAPERS into the piece that
    swallows it -- the shoulder cap sits at the pauldron's own centre, the elbow
    sphere is wider than both caps that meet inside it, and the fist is wider
    than the wrist. The outline is a per-object inverted hull, so an exposed cap
    draws a dark line straight across the limb.

    The elbow sphere is named after the FOREARM deliberately: `attack_roster`
    lists upperL/foreL/fistL and `pixelrig.find` matches names before Blender's
    .001 suffix, so a second "foreL" travels with the arm where an "elbowL"
    would be left behind mid-swing.
    """
    return [S.aimed_cone(scn, "upper" + side, shoulder, elbow, 0.155, 0.105, UP, verts=8),
            P.add_sphere(scn, "fore" + side, elbow, 0.135, CU, segs=8, rings=5),
            S.aimed_cone(scn, "fore" + side, elbow, hand, 0.135, 0.10, CU, verts=8),
            P.add_sphere(scn, "fist" + side, hand, 0.145, CU)]


# BOTH HANDS ARE ON THE POLE (user asked for two hands, 2026-08-02, and approved
# the sprite change it costs). His right arm used to hang at his side, which meant
# his attack could only ever be a one-handed swing of a five-unit polearm.
#
# **The pole had to come in for it.** At x -0.94 it stood 1.5 from the right
# shoulder and his arm reaches about 1.0, so no pose could get that hand onto it.
# It now sits at -0.72, which is as far in as it can come: measured against the
# head's own span, anything past about -0.70 puts the shaft across his face. That
# leaves the right arm reaching 1.3 where it used to reach 1.0, which the aimed
# cones absorb, and it is close enough for a bent arm to cross the body and grip
# low. That is the placement the README warns grazes the surcoat --
# the difference is that a hand is now ON it at two points, so the overlap reads
# as a grip rather than as a pole laid over the tabard.
#
# The left hand grips at chest height rather than at head height. Up at 1.18 the
# forearm came out 1.7 times the upper arm, and a limb whose halves are that far
# apart reads as broken however well its caps are buried.
tors += _arm("L", (-0.58, -0.08, 0.72), (-0.72, -0.34, 0.54), (-0.68, -0.50, 0.95))
tors += _arm("R", (0.58, -0.08, 0.72), (0.40, -0.48, 0.26), (-0.63, -0.44, 0.34))
P.parent_all(tors_root, tors + hd_det)

# ---- the banner ----
# USER 2026-08-01: "the legendary's banner covers his face." It did, and so did
# the common's. The panel hung from a fixed height whatever its own DROP was, so
# a tall panel simply reached further down -- the legendary's bottom edge landed
# at 2.32 against a head top of about 2.80.
#
# So the hang height is DERIVED from the drop rather than written per tier: the
# panel's lowest point is placed at HEAD_CLEAR and it grows upward from there.
# The pole then has to be long enough to carry it, which is what the 144 cell is
# for. Get this wrong on a future banner and it will cover the face again.
HEAD_CLEAR = 3.05
BN_ROOT_Z = 1.30
PANEL = {
    # a small forked standard, the plainest flag in the line
    "common":    [(0.0, 0.0), (1.16, 0.0), (1.16, -0.88), (0.87, -0.66), (0.58, -0.92),
                  (0.29, -0.66), (0.0, -0.88)],
    # a long pennon tapering to a single point: narrow, and twice as long
    "rare":      [(0.0, 0.0), (0.62, 0.0), (2.30, -0.44), (0.62, -0.84), (0.0, -0.84)],
    # a gonfalon hung from the crossbar: wide, short, three tails
    "epic":      [(0.0, 0.0), (1.68, 0.0), (1.68, -0.92), (1.40, -0.66), (1.12, -0.98),
                  (0.84, -0.66), (0.56, -0.98), (0.28, -0.66), (0.0, -0.92)],
    # a great square with one long streaming tail. Its drop is trimmed against
    # the shape it started at, because the drop pushes the whole stack up: flag
    # bottom, flag height, pole, then a halberd head on top of that, all inside
    # one cell. His was the tier that ran out of room first.
    "legendary": [(0.0, 0.0), (1.54, 0.0), (1.54, -0.83), (2.46, -1.03), (1.50, -1.21),
                  (0.72, -1.12), (0.0, -1.17)],
}[TIER]
DROP = max(-z for _, z in PANEL)
PANEL_Z = HEAD_CLEAR + DROP - BN_ROOT_Z          # panel origin, in root space
# 0.06, not the 0.18 it was: the flag is tied just UNDER the head, and at 0.18
# there were eight pixels of bare pole between them so the head read as a second
# object floating above a flagpole rather than as the top of one weapon.
POLE_TOP = PANEL_Z + 0.06
# The BUTT is pinned too, not derived from a length. Written as a fixed length it
# moved with the panel, and on every tier the pole drove down through the ground
# and out of the bottom of the cell. -0.78 in root space is world 0.52, about his
# knee, which is where a grounded standard ends.
POLE_BUTT = -0.78
POLE_LEN = POLE_TOP - POLE_BUTT

# x -0.94, not the -0.80 it was: at -0.80 the pole's screen position landed
# within a couple of pixels of the torso's own edge and grazed the surcoat all
# the way down. The fist moved out with it, since the hand has to stay on it.
bn_root = P.make_root(scn, "banner_root", rot=(0, -5, 0), loc=(-0.72, -0.48, BN_ROOT_Z))
banner = [P.add_cyl(scn, "pole", (0, 0, (POLE_TOP + POLE_BUTT) / 2), 0.055, POLE_LEN,
                    POLE_MAT, verts=6),
          P.add_cyl(scn, "socket", (0, 0, POLE_TOP + 0.02), 0.085, 0.18,
                    TRIM or M["steel"], verts=8)]

# ---- the head, which is why this is a weapon and not a flagpole ----
# USER 2026-08-02: "can we have all of the banners double as polearms?
# spear-glaive-bardiche-halberd?" So the sword is gone from all four tiers, and
# what replaces it sits ABOVE the flag where nothing occludes it. It reads second
# after the flag's own shape, and it escalates by mass: a point, a point with a
# belly, a great crescent, and then a head that does three jobs at once.
HEAD_Z = POLE_TOP + 0.06
if TIER == "common":
    # a plain spear: one leaf blade, the only head here with no cutting edge
    banner.append(P.add_prism(scn, "spearhead",
                              [(-0.085, 0.0), (0.085, 0.0), (0.105, 0.30), (0.0, 0.62),
                               (-0.105, 0.30)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z)))
elif TIER == "rare":
    # a glaive: a single-edged blade with the belly swept forward, so its
    # outline is lopsided where the spear's is symmetrical
    banner.append(P.add_prism(scn, "glaiveblade",
                              [(-0.075, 0.0), (0.075, 0.0), (0.21, 0.34), (0.27, 0.64),
                               (0.13, 0.96), (0.02, 0.66), (-0.075, 0.32)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z)))
elif TIER == "epic":
    # a bardiche: one long CRESCENT running up the shaft, and by a wide margin
    # the biggest piece of steel on any hero. The inner edge hugs the shaft while
    # the outer bows away from it -- built as a solid wedge it came back as a
    # paddle, and a paddle is just a bigger spear at this size.
    banner.append(P.add_prism(scn, "bardicheblade",
                              [(0.04, 0.0), (0.28, 0.14), (0.48, 0.48), (0.44, 0.88),
                               (0.18, 1.08), (0.11, 0.74), (0.17, 0.44), (0.07, 0.20)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z)))
else:
    # a halberd: spike, axe and rear hook. Three silhouettes on one head, which
    # is the only place in the roster that happens.
    banner.append(P.add_prism(scn, "halberdspike",
                              [(-0.055, 0.0), (0.055, 0.0), (0.045, 0.34), (0.0, 0.58),
                               (-0.045, 0.34)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z + 0.30)))
    banner.append(P.add_prism(scn, "halberdaxe",
                              [(0.04, 0.0), (0.34, 0.10), (0.45, 0.36), (0.30, 0.58),
                               (0.05, 0.48)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z + 0.06)))
    banner.append(P.add_prism(scn, "halberdhook",
                              [(-0.04, 0.06), (-0.30, 0.20), (-0.35, 0.40), (-0.07, 0.32)],
                              0.06, M["blade"], loc=(0, 0.10, HEAD_Z + 0.06)))
# The Banneret's pennon hangs straight off the pole, so he alone has no crossbar,
# and that missing horizontal is visible from right across the battle line.
if TIER != "rare":
    banner.append(P.add_box(scn, "crossbar", (0.34, 0, PANEL_Z + 0.06),
                            (1.10 if TIER == "epic" else 0.76, 0.07, 0.08),
                            TRIM or M["steel"]))
banner.append(P.add_prism(scn, "bannerpanel", PANEL, 0.05, FL, loc=(0.08, 0.10, PANEL_Z)))
# gold on the field is the tier ladder, since the field itself never changes
# Two bands on the legendary, not three: with the gilded crossbar above them a
# third made four gold horizontals across one crimson field, and it read as an
# awning rather than as a standard.
BANDS = {"common": 1, "rare": 1, "epic": 2, "legendary": 2}[TIER]
BW = {"common": 1.10, "rare": 0.98, "epic": 1.58, "legendary": 1.46}[TIER]
for i in range(BANDS):
    banner.append(P.add_box(scn, "bannerband",
                            (0.08 + BW / 2, 0.06, PANEL_Z - 0.26 - i * 0.30),
                            (BW, 0.06, 0.13),
                            M["brightgold"] if LEGEND else (TRIM or M["gold"])))
P.parent_all(bn_root, banner)

# No sword on any tier. `attack_roster.py` was pointing at a `sword_root` that no
# longer exists, and it now swings the LEFT arm and `banner_root` through
# `attack_shapes.SWEEP`, which that file already describes as the two-handed
# horizontal sweep for polearms.

H.finish(scn, px, "hero_banneret", figure, detail, noline,
         roots=[tors_root, bn_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
