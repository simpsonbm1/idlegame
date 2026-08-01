"""The ranged line -- M15_ASSET_SPECS.md entry 2, plus its rarity variants.

  "a keen-eyed human archer in a forest-green hood and brown leather armor,
   longbow with an arrow nocked but pointed down, quiver on the back"

## Four people, not one person promoted (USER RULING 2026-08-01)

The first two attempts at rarity dressed ONE model in better gear, and both were
rejected on sight: "this is still the same guy with different clothes." The bar
the user set is the orc family, which he judged the most successful set in the
roster -- "theyre not just the same guy with better gear, theyre four different
people." Six orcs are six separate builders with different bodies, weapons and
poses, and the hero tiers have to reach that.

So a tier here is a DIFFERENT CHARACTER who happens to fill the same battle role.
`DESIGN.md` already names them, and the names were always four people:

| tier | name | the read |
|---|---|---|
| common | Archer | a hooded villager with a longbow |
| rare | Sharpshooter | a lean professional, brimmed hat, bare arms, recurve |
| epic | Hunter | a wild ranger in wolf pelt, heavy war bow |
| legendary | Marksman | elite, deep hood and cloak, gilded great bow |

They differ on head shape, arm covering, bow silhouette, torso mass and palette.
Any ONE of those read alone would be a costume change; changing all five at once
is what makes them separate people.

## What a tier may NOT change

The attack animation finds this figure's parts by name (`attack_roster.py`), so
every tier must still provide `upperL/foreL/fistL`, `upperR/foreR/fistR`, parts
named `shoulder`, and a root named `bow_root`. Rename any of those and the arm
detaches silently on the attack sheet.

Height is also fixed. `spritekit.finish()` scales the assembled body to the role
height, so a taller tier just shrinks its own body to compensate. Tiers are spent
on WIDTH, MASS, SHAPE and COLOUR.
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

TIER = H.tier()
if TIER == "base":
    TIER = "common"          # this hero's own sprite IS the common tier
TRIM = H.trim_mat(M, TIER)
LEGEND = TIER == "legendary"

figure, detail, noline = [], [], []

# ---------------------------------------------------------------------------
# the four builds, as data. Everything below reads from this one table, so the
# characters stay comparable and a new tier is an entry rather than a branch.
# ---------------------------------------------------------------------------
BUILD = {
    # coat/cloth       arm skin?  boots      hip     spread  chest
    "common":    dict(cloth="green", bare=False, boot="leath", hip=1.16,
                      spread=0.32, chest=0.42, lean=8),
    "rare":      dict(cloth="cream", bare=True,  boot="leath", hip=1.22,
                      spread=0.30, chest=0.38, lean=6),
    "epic":      dict(cloth="green", bare=False, boot="charcoal", hip=1.10,
                      spread=0.40, chest=0.46, lean=11, leg="charcoal",
                      torso="green", sleeve="charcoal"),
    "legendary": dict(cloth="navy",  bare=False, boot="mail",  hip=1.14,
                      spread=0.42, chest=0.48, lean=9),
}[TIER]

CLOTH = M[BUILD["cloth"]]
# **The torso material matters more than the jerkin.** `H.torso()` builds a chest
# sphere scaled 1.22 wide, so at any decent chest radius it is WIDER than the
# jerkin box in front of it and shows past it on both sides. Leaving it leather
# under a green jerkin is what made the Hunter's chest read brown (user,
# 2026-08-01: "his torso is reading as a big brown beard").
TORSO_MAT = M[BUILD.get("torso", "leath")]
SLEEVE = (M["skin"] if BUILD["bare"]
          else M[BUILD.get("sleeve", "leath")])
# The Hunter was "just kind of a brown blob" (user, 2026-08-01): his legs, hips,
# belt and sleeves were all the same leather as his boots, so only the jerkin had
# its own colour. Legs in a dark material split the figure in half by value.
LEG = M[BUILD.get("leg", "leath")]
HIP = BUILD["hip"]

# ---------------------------------------------------------------------------
# legs
# ---------------------------------------------------------------------------
figure += H.legs(scn, M, HIP, spread=BUILD["spread"], mat=LEG,
                 boot=M[BUILD["boot"]])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.74, 0.50, 0.28),
                        LEG, bevel=0.05))

# ---------------------------------------------------------------------------
# torso
# ---------------------------------------------------------------------------
tors_root, tors = H.torso(scn, M, HIP + 0.14, chest_r=BUILD["chest"],
                          lean=BUILD["lean"], mat=TORSO_MAT)
tors.append(P.add_box(scn, "jerkin", (0, -0.12, 0.48), (0.84, 0.42, 0.64),
                      CLOTH, bevel=0.05))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.10), (0.88, 0.54, 0.14), M["leath"]))

if TIER == "common":
    tors.append(P.add_box(scn, "baldric", (0, -0.34, 0.46), (0.94, 0.09, 0.14),
                          M["leath"], rot=(0, math.radians(30), 0)))
elif TIER == "rare":
    # A shooting glove and a long bracer, on bare arms. The Sharpshooter's whole
    # read is that he is dressed for speed and carries nothing spare.
    tors.append(P.add_cyl(scn, "bracer", (-0.58, -0.42, 0.18), 0.17, 0.40,
                          M["leath"], verts=8, rot=(math.radians(64), 0, 0)))
    tors.append(P.add_box(scn, "sash", (0, -0.30, 0.30), (0.92, 0.14, 0.20),
                          M["crimson"], rot=(0, math.radians(-22), 0)))
elif TIER == "epic":
    # A wolf pelt over ONE shoulder, and a strap crossing to the opposite hip.
    # Asymmetry is the strongest silhouette tool left in this line, and no other
    # ranged hero has any. A symmetric mantle just read as more shoulders.
    # The pelt stays ON the shoulder. Its strap and its wolf-head both sat across
    # the chest, and anything crossing the chest at this size merges with the
    # beard above it into one shape.
    tors.append(P.add_cone(scn, "hpelt", (0.42, 0.04, 0.78), 0.40, 0.20, 0.38,
                           M["fur"], verts=10))
    # No third belt. `hips` and `belt` already stack here, and a third box turned
    # the pelvis into an unreadable square (user, 2026-08-01).
else:
    # Pauldrons ONLY at the shoulder line. A mantle on top of them put three
    # masses at one height and the shoulders stopped being findable.
    tors += H.pauldrons(scn, M, M["brightgold"], 0.70, span=0.62, r=0.32)
    # Narrow and pushed well back, so the legs stay visible under it.
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.46, height=1.46,
                      r_base=0.60, r_top=0.30, y=0.44)

# ---------------------------------------------------------------------------
# head: the single biggest difference between the four, so each gets its own
# ---------------------------------------------------------------------------
HEAD_AT = (0, -0.04, 1.04)
HR = 0.29

if TIER == "common":
    hd, hd_det = H.head(scn, M, HEAD_AT, r=HR, hood=CLOTH)
    tors += hd
elif TIER == "rare":
    # bare head under a wide brimmed hat: the only tier whose face is fully lit,
    # and the only one with a horizontal line above the shoulders
    hd, hd_det = H.head(scn, M, HEAD_AT, r=HR)
    tors += hd
    tors.append(P.add_cone(scn, "hatbrim", (0, -0.02, 1.30), 0.62, 0.54, 0.08,
                           M["leath"], verts=14))
    tors.append(P.add_cone(scn, "hatcrown", (0, -0.02, 1.44), 0.30, 0.22, 0.30,
                           M["leath"], verts=12))
    detail.append(P.add_box(scn, "hatfeather", (0.16, 0.16, 1.52),
                            (0.06, 0.34, 0.30), M["crimson"],
                            rot=(math.radians(-28), 0, 0)))
elif TIER == "epic":
    # BARE HEADED, deliberately. The Marksman owns the hood, and a second hooded
    # figure in a four-figure line is a wasted read (user rejected the fur hood,
    # 2026-08-01). The Hunter is the only one of the four with loose hair and a
    # beard, and the only one whose head is not covered by anything.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=HR)
    tors += hd
    tors.append(P.add_sphere(scn, "hhair", (0, 0.09, 1.11), HR * 1.26, M["charcoal"],
                             scale=(1.02, 1.04, 1.00), segs=12, rings=7))
    tors.append(P.add_cone(scn, "hmane", (0, 0.20, 0.84), HR * 1.10, HR * 0.46,
                           0.52, M["charcoal"], verts=10))
    detail.append(P.add_box(scn, "hbeard", (0, -0.30, 0.86), (0.32, 0.20, 0.24),
                            M["charcoal"]))
else:
    # Hood kept close to the skull. At 2.20 reach it met the shoulder mass and
    # the head stopped being a separate shape.
    hd, hd_det = H.head(scn, M, HEAD_AT, r=HR)
    tors += hd
    tors += H.deep_hood(scn, M, M["navy"], HEAD_AT, r=HR, reach=1.70,
                        shadow=M["dark"])
    detail.append(P.add_box(scn, "hcircle", (0, -0.46, 1.20), (0.52, 0.10, 0.10),
                            M["brightgold"]))

# ---------------------------------------------------------------------------
# quiver: on the back for three of them, at the hip for the Sharpshooter
# ---------------------------------------------------------------------------
if TIER == "rare":
    tors.append(P.add_cyl(scn, "quiver", (0.34, 0.16, 0.06), 0.14, 0.62,
                          M["leath"], verts=8, rot=(math.radians(-52), 0, 0)))
    for dx in (-0.05, 0.05):
        detail.append(P.add_box(scn, "fletch", (0.40 + dx, -0.18, 0.34),
                                (0.06, 0.06, 0.14), M["crimson"]))
else:
    tors.append(P.add_cyl(scn, "quiver", (0.30, 0.26, 0.46), 0.15, 0.72,
                          M["leath"], verts=8,
                          rot=(math.radians(-14), 0, math.radians(-22))))
    ARROWS = (-0.05, 0.0, 0.05) if TIER == "common" else (-0.10, -0.05, 0.0, 0.05, 0.10)
    for dx in ARROWS:
        detail.append(P.add_box(scn, "fletch", (0.40 + dx, 0.34, 1.66),
                                (0.06, 0.06, 0.14), M["crimson"]))

# ---------------------------------------------------------------------------
# arms. The names here are a CONTRACT with attack_roster.py -- see the docstring.
# ---------------------------------------------------------------------------
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.50, -0.08, 0.66), 0.21,
                             CLOTH, scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "upperL", (-0.54, -0.20, 0.48), 0.145, 0.46, SLEEVE, verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.60, -0.48, 0.30), 0.13, 0.46, SLEEVE, verts=8,
                      rot=(math.radians(58), 0, 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.62, -0.66, 0.24), 0.15, M["skin"]))
tors.append(P.add_cyl(scn, "upperR", (0.54, -0.22, 0.44), 0.145, 0.46, SLEEVE, verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.42, -0.50, 0.20), 0.13, 0.46, SLEEVE, verts=8,
                      rot=(math.radians(46), 0, math.radians(16))))
tors.append(P.add_sphere(scn, "fistR", (0.30, -0.64, 0.10), 0.15, M["skin"]))
P.parent_all(tors_root, tors + hd_det)

# ---------------------------------------------------------------------------
# the bow. Four different weapons, and the clearest read of the four at any size
# because the bow is the tallest thin object the hero owns.
#
# `recurve` bends the tips back the other way past |t| = 0.70, which is the shape
# difference between a stave and a composite bow. It is worth the four lines: the
# outline of the weapon is legible even when the figure is not.
# ---------------------------------------------------------------------------
BOW = {
    "common":    dict(bulge=0.56, reach=1.46, r=0.045, recurve=0.00, mat="wood"),
    "rare":      dict(bulge=0.44, reach=1.16, r=0.042, recurve=0.34, mat="wood"),
    "epic":      dict(bulge=0.70, reach=1.74, r=0.060, recurve=0.00, mat="wood"),
    "legendary": dict(bulge=0.82, reach=1.78, r=0.062, recurve=0.30, mat="brightgold"),
}[TIER]

bw_root = P.make_root(scn, "bow_root", rot=(0, 4, 0), loc=(-0.66, -0.82, 1.60))
bow = []
# **The common archer keeps 10 segments.** He is approved, shipped art, and
# raising the count for the recurve tips reshaped his bow as a side effect. A
# recurve needs 12 to bend its tips without beading; nobody else does.
N = 12 if BOW["recurve"] else 10
pts = []
for i in range(N + 1):
    t = -1.0 + 2.0 * i / N
    # A 0.30 bulge is eight pixels and reads as a bent stick. A longbow has to
    # bow visibly or it is just a pole with a string beside it.
    x = -abs(1.0 - t * t) * BOW["bulge"]
    if BOW["recurve"] and abs(t) > 0.70:
        x += (abs(t) - 0.70) / 0.30 * BOW["recurve"]
    pts.append((x, 0.0, t * BOW["reach"]))
for i in range(N):
    bow.append(S.aimed_cyl(scn, "bowlimb", pts[i], pts[i + 1], BOW["r"],
                           M[BOW["mat"]], verts=5))
bow.append(S.aimed_cyl(scn, "bowstring", pts[0], pts[-1], 0.020, M["cream"], verts=4))
bow.append(P.add_box(scn, "bowgrip", (-0.30, 0.0, 0.0), (0.10, 0.13, 0.30), M["leath"]))
bow.append(P.add_cyl(scn, "arrow", (-0.16, -0.04, -0.34), 0.024, 1.20, M["wood"], verts=4,
                     rot=(0, math.radians(14), 0)))
bow.append(P.add_cone(scn, "arrowhead", (-0.30, -0.04, -0.94), 0.05, 0.0, 0.16,
                      TRIM or M["steel"], rot=(math.radians(180), 0, 0), verts=5))
if TRIM:
    for z in (-BOW["reach"] * 0.46, BOW["reach"] * 0.46):
        bow.append(P.add_cyl(scn, "bownock", (-0.10, 0.0, z), 0.07, 0.10, TRIM, verts=6))
P.parent_all(bw_root, bow)

H.finish(scn, px, "hero_ranged", figure, detail, noline,
         roots=[tors_root, bw_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
