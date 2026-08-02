"""Guardian knight sprite. Palette and pose read off raw_hero_knight_v3.png.

Local frame: the figure faces -Y, up is +Z, and local +X lands on SCREEN RIGHT
after the root's +30 deg facing turn. So the shield (his left) is built at +X and
the sword and big pauldron (his right) at -X, matching the reference.

Two rules this file exists to obey:
  1. A part belongs to exactly ONE root. Sub-assemblies (sword, shield) parent to
     their own root, and only that root parents to the figure.
  2. Overlapping parts must be SEPARATED IN DEPTH. The outline is an inverted
     hull, so it only draws where a part stands clear of what is behind it.
     Arms flush with the torso produce no internal outline and read as mush.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S
import hero_kit as H
importlib.reload(P)
importlib.reload(S)
importlib.reload(H)
OUT = P.out_dir()

scn = P.get_scene()
P.ensure_rig(scn)          # no window in background Blender; ensure_rig activates safely
P.setup_render(scn)
P.clear_scene(scn)

P.sprite_cam(scn, res=96, target_z=1.50)
px = P.pixel_size(scn)
scn.collection.objects["KeySun"].rotation_euler = (math.radians(50), 0, math.radians(-40))

STEEL = P.toon_mat("STEEL", "#4a6d94", "#7ba3c9", "#b6d8ef")
BLADE = P.toon_mat("BLADE", "#8fb4d6", "#cbe4f6", "#f4fbff")
NAVY = P.toon_mat("NAVY", "#1b2a52", "#2a3f73", "#3d5691")
GOLD = P.toon_mat("GOLD", "#8a5f14", "#c9962c", "#f0d264")
LEATH = P.toon_mat("LEATHER", "#4a2e18", "#7a4d28", "#a06a3a")
DARK = P.flat_mat("VISORDARK", "#10141f")

CRIMSON = P.toon_mat("HCRIMSON", "#6b1d1c", "#9c2f27", "#c85641")
BRIGHTGOLD = P.toon_mat("HBRIGHTGOLD", "#a8790f", "#e0b132", "#ffeb9a")
GREEN = P.toon_mat("HGREEN", "#26401f", "#3d6330", "#5d8a48")

# ---------------------------------------------------------------------------
# The guardian line: Knight, Sentinel, Vanguard, Paragon (DESIGN.md).
#
# Four different soldiers, not one knight with better plate (USER RULING
# 2026-08-01). The helm is the read, because it is the only part of an armoured
# figure that is never covered by anything: a slit-cross great helm, a smooth
# sallet, a horned barbute, a winged crown. Then the shield changes shape, the
# surcoat changes colour, and the sword changes length.
#
# TIER == "base" IS the Knight, and his geometry below is untouched: he is
# shipped art and every branch here is additive or keyed off a higher tier.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

SURCOAT = {"common": NAVY, "rare": GREEN, "epic": CRIMSON, "legendary": NAVY}[TIER]

# USER REVIEW 2026-08-01: the guardians were "just different, but not necessarily
# better as the tiers progress". They were four helmets on ONE suit of full plate,
# and the common already wore the best armour in the game, so there was nowhere
# above him to go. The developer's own suggestion was to start him with less.
#
# The ladder is now ARMOUR, climbing mail -> plate -> ornate plate -> gilded
# plate, with the shield climbing beside it. Helm shape still separates the four
# people; it is no longer carrying the escalation on its own.
MAIL = P.toon_mat("KMAIL", "#3f4650", "#626b78", "#8e97a5")
WOOD = P.toon_mat("KWOOD", "#4a3018", "#6f4a24", "#96693a")
DARKSTEEL = P.toon_mat("KDARKSTEEL", "#26303d", "#3d4e63", "#5f7591")

# Each tier is a DIFFERENT METAL, because the developer's second look found the
# top three still reading alike. Dull mail, bright steel, then blackened steel for
# the top two, which the Paragon wears under gold rather than in place of it (user,
# 2026-08-02). Helm shape and shield shape separate the four people; metal is what
# separates them at sprite scale.
BODY = {"common": MAIL, "rare": STEEL, "epic": DARKSTEEL, "legendary": DARKSTEEL}[TIER]
# The Paragon's major plates are GOLD. A gilded helm on an otherwise steel body
# left him looking like the Sentinel and the Vanguard.
ACCENT = BRIGHTGOLD if TIER == "legendary" else BODY
# Gilt fittings. The common has NONE, which is most of why he stops outranking
# the tiers above him.
TRIM_M = {"common": None, "rare": GOLD, "epic": GOLD, "legendary": BRIGHTGOLD}[TIER]
PLATED = TIER != "common"       # knee cops and a faceted breastplate: plate only

figure, detail = [], []

# ---- legs: front leg pulled toward camera so the two read apart ----
for s, yoff, zoff in ((-1, -0.22, 0.0), (1, 0.20, 0.02)):
    figure.append(P.add_box(scn, "boot", (s * 0.44, yoff - 0.05, 0.15 + zoff), (0.48, 0.66, 0.30),
                            BODY if PLATED else LEATH, bevel=0.04))
    figure.append(P.add_box(scn, "greave", (s * 0.41, yoff, 0.58 + zoff), (0.40, 0.42, 0.66), BODY, bevel=0.05))
    if PLATED:
        figure.append(P.add_sphere(scn, "poleyn", (s * 0.41, yoff - 0.14, 0.90 + zoff), 0.22, ACCENT, scale=(1, .85, .72)))
    figure.append(P.add_box(scn, "cuisse", (s * 0.38, yoff * 0.6, 1.12), (0.42, 0.46, 0.48), BODY,
                            rot=(0, math.radians(-s * 7), 0), bevel=0.05))

# ---- hips, belt, breastplate (faceted plate, or a plain mail hauberk) ----
figure.append(P.add_box(scn, "tassets", (0, 0, 1.38), (1.12, 0.62, 0.34), ACCENT, bevel=0.05))
figure.append(P.add_box(scn, "belt", (0, -0.02, 1.54), (1.16, 0.66, 0.17), LEATH))
detail.append(P.add_box(scn, "buckle", (0.04, -0.36, 1.54), (0.15, 0.06, 0.14), TRIM_M or STEEL))
figure.append(P.add_box(scn, "pouch", (0.36, -0.34, 1.42), (0.30, 0.24, 0.32), LEATH, bevel=0.04))
if PLATED:
    figure += P.add_ridged(scn, "torso", (0, 0, 1.94), (1.14, 0.56, 0.82), BODY, splay=13, bevel=0.07)
else:
    figure.append(P.add_box(scn, "torso", (0, 0, 1.94), (1.10, 0.54, 0.82), BODY, bevel=0.06))

# ---- surcoat, sitting proud of the breastplate so it outlines against it ----
figure.append(P.add_box(scn, "surcoat", (0, -0.30, 1.52), (0.56, 0.07, 1.24), SURCOAT))
figure.append(P.add_box(scn, "surcoatB", (0, 0.29, 1.52), (0.56, 0.07, 1.24), SURCOAT))
if TRIM_M:
    detail.append(P.add_box(scn, "lion", (0, -0.35, 1.86), (0.22, 0.04, 0.30), TRIM_M))

# ---- shoulders and arms, pulled forward off the torso ----
# `pauldronR` is the pivot the attack animation swings his sword arm about
# (build_attack.knight), so it may grow but must stay the topmost right-arm part.
# The common's shoulders come down with the rest of him: a mail-clad man-at-arms
# does not have the widest silhouette in the line.
PAULD = {"common": 0.30, "rare": 0.37, "epic": 0.46, "legendary": 0.44}[TIER]
figure.append(P.add_sphere(scn, "pauldronR", (-0.70, -0.10, 2.18), PAULD, ACCENT, scale=(1, .95, .76)))
figure.append(P.add_sphere(scn, "pauldronL", (0.70, -0.10, 2.20),
                           PAULD - 0.05, ACCENT, scale=(1, .95, .78)))
if TIER == "epic":
    # The Vanguard is the heavy: spiked cops standing out past the pauldrons.
    for s, r in ((-1, 0.46), (1, 0.41)):
        figure.append(P.add_cone(scn, "spike", (s * 0.86, -0.10, 2.40), 0.16, 0.0, 0.40,
                                 BODY, rot=(0, math.radians(-s * 22), 0), verts=6))
# Arms taper so each segment's end cap is buried in the piece that swallows it --
# see the limb rule in README.md. Cylinders left a dark outline across every joint
# and the arm read as a chain of separate lumps.
figure.append(P.add_cone(scn, "upperR", (-0.70, -0.18, 1.84), 0.12, 0.19, 0.60, BODY, verts=10))
figure.append(P.add_cone(scn, "foreR", (-0.63, -0.32, 1.38), 0.15, 0.185, 0.50, BODY, verts=10,
                         rot=(math.radians(16), 0, 0)))
figure.append(P.add_box(scn, "gauntR", (-0.59, -0.42, 1.10), (0.34, 0.34, 0.28), ACCENT, bevel=0.04))
figure.append(P.add_cone(scn, "upperL", (0.70, -0.16, 1.86), 0.11, 0.18, 0.56, BODY, verts=10))
figure.append(P.add_cone(scn, "foreL", (0.66, -0.30, 1.46), 0.14, 0.175, 0.48, BODY, verts=10,
                         rot=(math.radians(24), 0, 0)))

# ---- gorget, then a different head on every tier ----
figure.append(P.add_box(scn, "gorget", (0, 0, 2.40), (0.52, 0.46, 0.18), ACCENT, bevel=0.04))

if TIER == "common":
    # the Knight: faceted great helm with a cross slit
    figure += P.add_ridged(scn, "helm", (0, -0.02, 2.68), (0.66, 0.56, 0.50), STEEL, splay=12, bevel=0.05)
    detail.append(P.add_box(scn, "crossH", (0, -0.32, 2.69), (0.50, 0.05, 0.08), DARK))
    detail.append(P.add_box(scn, "crossV", (0, -0.32, 2.68), (0.09, 0.05, 0.36), DARK))
elif TIER == "rare":
    # the Sentinel: a smooth sallet with a long tail and one horizontal slit. No
    # facets and no cross, so his head is a curve where the Knight's is a block.
    figure.append(P.add_sphere(scn, "helm", (0, -0.02, 2.70), 0.38, STEEL,
                               scale=(0.92, 1.10, 0.98), segs=14, rings=8))
    figure.append(P.add_cone(scn, "helmtail", (0, 0.30, 2.56), 0.34, 0.14, 0.44,
                             STEEL, rot=(math.radians(52), 0, 0), verts=10))
    detail.append(P.add_box(scn, "visorslit", (0, -0.36, 2.74), (0.46, 0.06, 0.09), DARK))
elif TIER == "epic":
    # the Vanguard: a horned barbute. Horns are the widest thing on any hero head
    # and read at any size.
    figure += P.add_ridged(scn, "helm", (0, -0.02, 2.70), (0.68, 0.58, 0.56), BODY, splay=9, bevel=0.05)
    detail.append(P.add_box(scn, "visorslit", (0, -0.34, 2.72), (0.13, 0.06, 0.34), DARK))
    for s in (-1, 1):
        # STEEL, not BLADE. The blade material is nearly white, so horns made of
        # it read as a separate pale shape stuck on the helm rather than as part
        # of it.
        figure.append(P.add_cone(scn, "horn", (s * 0.34, 0.02, 2.92), 0.13, 0.0, 0.62,
                                 BODY, rot=(0, math.radians(-s * 38), 0), verts=7))
else:
    # the Paragon: a winged crown, gilded, face open. He is the only guardian
    # whose face is visible at all, which is the whole point of him.
    figure.append(P.add_sphere(scn, "helm", (0, -0.02, 2.70), 0.36, BRIGHTGOLD,
                               scale=(0.94, 1.02, 0.94), segs=14, rings=8))
    detail.append(P.add_box(scn, "visorslit", (0, -0.36, 2.68), (0.40, 0.06, 0.16), DARK))
    for s in (-1, 1):
        figure.append(P.add_prism(scn, "helmwing",
                                  [(0.0, -0.10), (0.30, 0.16), (0.46, 0.54), (0.16, 0.34), (0.06, 0.16)],
                                  0.07, BRIGHTGOLD, loc=(s * 0.30, 0.04, 2.78),
                                  rot=(0, math.radians(-s * 90 + 90), 0)))

# ---- shield: it climbs WITH the armour, and every tier carries one ----
# The Vanguard used to carry no shield at all and the Paragon's was smaller than
# the Knight's, which is two of the places the ladder ran backwards.
# FOUR SHAPES, EACH BIGGER THAN THE LAST. Measured, not judged by eye: the round
# shields have to be compared on DIAMETER against the tall ones' height, and a
# 1.20-across roundel lost to a 1.82-tall tower even though it was meant to be the
# best shield in the line (user, 2026-08-01).
#   buckler  0.76 x 0.76      kite   0.88 x 1.48
#   octagon  1.24 x 1.72      pavise 1.24 x 2.04
buckler = [(0.38 * math.cos(math.radians(a)), 0.38 * math.sin(math.radians(a)))
           for a in range(0, 360, 30)]
kite = [(-0.20, 0.60), (-0.40, 0.50), (-0.44, 0.22), (-0.38, -0.16), (-0.22, -0.56),
        (0.0, -0.88), (0.22, -0.56), (0.38, -0.16), (0.44, 0.22), (0.40, 0.50), (0.20, 0.60)]
octagon = [(-0.30, 0.86), (0.30, 0.86), (0.62, 0.26), (0.62, -0.26), (0.30, -0.86),
           (-0.30, -0.86), (-0.62, -0.26), (-0.62, 0.26)]
pavise = [(-0.56, 1.00), (0.56, 1.00), (0.62, 0.22), (0.46, -0.70), (0.0, -1.04),
          (-0.46, -0.70), (-0.62, 0.22)]

SHIELD_SHAPE = {"common": buckler, "rare": kite, "epic": octagon, "legendary": pavise}[TIER]
sh_root = P.make_root(scn, "shield_root", rot=(0, -14, 18), loc=(0.84, -0.58, 1.80))
shield, sh_lion = [], None
if TIER == "common":
    # boards and a steel boss. No heraldry and no gilt rim, because those are
    # exactly what the tiers above him are supposed to introduce.
    shield = [P.add_prism(scn, "shieldback", SHIELD_SHAPE, 0.11, WOOD),
              P.add_prism(scn, "shieldface", [(x * 0.80, z * 0.80) for x, z in SHIELD_SHAPE],
                          0.11, LEATH, loc=(0, -0.06, 0.02))]
    sh_lion = P.add_sphere(scn, "shieldlion", (0, -0.13, 0.0), 0.14, STEEL)
else:
    back = TRIM_M
    shield = [P.add_prism(scn, "shieldback", SHIELD_SHAPE, 0.11, back),
              P.add_prism(scn, "shieldface", [(x * 0.78, z * 0.80) for x, z in SHIELD_SHAPE],
                          0.11, SURCOAT, loc=(0, -0.06, 0.02))]
    sh_lion = P.add_box(scn, "shieldlion", (0, -0.14, 0.06), (0.26, 0.05, 0.36), back)
P.parent_all(sh_root, shield + [sh_lion])

# ---- sword: local z=0 sits at the hand, blade runs up +Z ----
# Every tier now carries a shield, so the blade grows steadily instead of the
# Vanguard jumping to a two-hander because his shield hand was empty. The common
# carries the shortest and plainest, with steel fittings rather than gilt.
BL = {"common": 0.88, "rare": 1.00, "epic": 1.12, "legendary": 1.26}[TIER]
BW = {"common": 0.88, "rare": 0.98, "epic": 1.16, "legendary": 1.10}[TIER]
blade = [(-0.06 * BW, 0.14), (0.06 * BW, 0.14), (0.06 * BW, 1.08 * BL),
         (0.0, 1.32 * BL), (-0.06 * BW, 1.08 * BL)]
sw_root = P.make_root(scn, "sword_root", rot=(0, 132, 0), loc=(-0.60, -0.66, 1.10))
FITTING = TRIM_M or STEEL
sword = [P.add_prism(scn, "blade", blade, 0.11, BLADE),
         P.add_box(scn, "guard", (0, 0, 0.12), (0.44 * BW, 0.10, 0.10), FITTING),
         P.add_box(scn, "grip", (0, 0, -0.08), (0.11, 0.10, 0.24), LEATH),
         P.add_sphere(scn, "pommel", (0, 0, -0.23), 0.10, FITTING)]
P.parent_all(sw_root, sword)

if TIER == "epic":
    figure.append(P.add_cone(scn, "plume", (0, 0.20, 3.06), 0.10, 0.03, 0.44,
                             CRIMSON, rot=(math.radians(-14), 0, 0), verts=6))
if TIER == "legendary":
    # Narrow and well behind him, so the greaves stay visible under it. A cloak
    # widened to surround the legs turns any figure into a triangle (see
    # hero_kit.cloak).
    figure.append(P.add_cone(scn, "cloak", (0, 0.46, 1.72), 0.66, 0.32, 1.72,
                             CRIMSON, verts=10))

# The guardian is the baseline the USER RULING sizes everything else against, so
# he goes through the same role-driven sizing as everyone else rather than being
# left at whatever height his coordinates happen to give.
S.finish(scn, px, "knight" + H.suffix(), figure, detail, [],
         roots=([sh_root] if shield else []) + [sw_root],
         skip_extra=("shieldlion",), facing=S.FACE_RIGHT, role="hero")
