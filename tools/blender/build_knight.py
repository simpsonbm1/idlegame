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

figure, detail = [], []

# ---- legs: front leg pulled toward camera so the two read apart ----
for s, yoff, zoff in ((-1, -0.22, 0.0), (1, 0.20, 0.02)):
    figure.append(P.add_box(scn, "boot", (s * 0.44, yoff - 0.05, 0.15 + zoff), (0.48, 0.66, 0.30), STEEL, bevel=0.04))
    figure.append(P.add_box(scn, "greave", (s * 0.41, yoff, 0.58 + zoff), (0.40, 0.42, 0.66), STEEL, bevel=0.05))
    figure.append(P.add_sphere(scn, "poleyn", (s * 0.41, yoff - 0.14, 0.90 + zoff), 0.22, STEEL, scale=(1, .85, .72)))
    figure.append(P.add_box(scn, "cuisse", (s * 0.38, yoff * 0.6, 1.12), (0.42, 0.46, 0.48), STEEL,
                            rot=(0, math.radians(-s * 7), 0), bevel=0.05))

# ---- hips, belt, faceted breastplate ----
figure.append(P.add_box(scn, "tassets", (0, 0, 1.38), (1.12, 0.62, 0.34), STEEL, bevel=0.05))
figure.append(P.add_box(scn, "belt", (0, -0.02, 1.54), (1.16, 0.66, 0.17), LEATH))
detail.append(P.add_box(scn, "buckle", (0.04, -0.36, 1.54), (0.15, 0.06, 0.14), GOLD))
figure.append(P.add_box(scn, "pouch", (0.36, -0.34, 1.42), (0.30, 0.24, 0.32), LEATH, bevel=0.04))
figure += P.add_ridged(scn, "torso", (0, 0, 1.94), (1.14, 0.56, 0.82), STEEL, splay=13, bevel=0.07)

# ---- surcoat, sitting proud of the breastplate so it outlines against it ----
figure.append(P.add_box(scn, "surcoat", (0, -0.30, 1.52), (0.56, 0.07, 1.24), SURCOAT))
figure.append(P.add_box(scn, "surcoatB", (0, 0.29, 1.52), (0.56, 0.07, 1.24), SURCOAT))
detail.append(P.add_box(scn, "lion", (0, -0.35, 1.86), (0.22, 0.04, 0.30),
                        BRIGHTGOLD if TIER == "legendary" else GOLD))

# ---- shoulders and arms, pulled forward off the torso ----
# `pauldronR` is the pivot the attack animation swings his sword arm about
# (build_attack.knight), so it may grow but must stay the topmost right-arm part.
PAULD = {"common": 0.35, "rare": 0.37, "epic": 0.46, "legendary": 0.44}[TIER]
figure.append(P.add_sphere(scn, "pauldronR", (-0.70, -0.10, 2.18), PAULD, STEEL, scale=(1, .95, .76)))
figure.append(P.add_sphere(scn, "pauldronL", (0.70, -0.10, 2.20),
                           PAULD - 0.05, STEEL, scale=(1, .95, .78)))
if TIER == "epic":
    # The Vanguard is the heavy: spiked cops standing out past the pauldrons.
    for s, r in ((-1, 0.46), (1, 0.41)):
        figure.append(P.add_cone(scn, "spike", (s * 0.86, -0.10, 2.40), 0.16, 0.0, 0.40,
                                 STEEL, rot=(0, math.radians(-s * 22), 0), verts=6))
figure.append(P.add_cyl(scn, "upperR", (-0.70, -0.18, 1.84), 0.18, 0.60, STEEL))
figure.append(P.add_cyl(scn, "foreR", (-0.63, -0.32, 1.38), 0.17, 0.50, STEEL, rot=(math.radians(16), 0, 0)))
figure.append(P.add_box(scn, "gauntR", (-0.59, -0.42, 1.12), (0.26, 0.26, 0.24), STEEL))
figure.append(P.add_cyl(scn, "upperL", (0.70, -0.16, 1.86), 0.17, 0.56, STEEL))
figure.append(P.add_cyl(scn, "foreL", (0.66, -0.30, 1.46), 0.16, 0.48, STEEL, rot=(math.radians(24), 0, 0)))

# ---- gorget, then a different head on every tier ----
figure.append(P.add_box(scn, "gorget", (0, 0, 2.40), (0.52, 0.46, 0.18), STEEL, bevel=0.04))

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
    figure += P.add_ridged(scn, "helm", (0, -0.02, 2.70), (0.68, 0.58, 0.56), STEEL, splay=9, bevel=0.05)
    detail.append(P.add_box(scn, "visorslit", (0, -0.34, 2.72), (0.13, 0.06, 0.34), DARK))
    for s in (-1, 1):
        figure.append(P.add_cone(scn, "horn", (s * 0.34, 0.02, 2.92), 0.13, 0.0, 0.62,
                                 BLADE, rot=(0, math.radians(-s * 38), 0), verts=7))
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

# ---- shield: a different shape per tier, and none at all for the Vanguard ----
kite = [(-0.20, 0.60), (-0.40, 0.50), (-0.44, 0.22), (-0.38, -0.16), (-0.22, -0.56),
        (0.0, -0.88), (0.22, -0.56), (0.38, -0.16), (0.44, 0.22), (0.40, 0.50), (0.20, 0.60)]
tower = [(-0.40, 0.78), (0.40, 0.78), (0.44, 0.10), (0.34, -0.62), (0.0, -0.86),
         (-0.34, -0.62), (-0.44, 0.10)]
roundel = [(0.52 * math.cos(math.radians(a)), 0.52 * math.sin(math.radians(a)))
           for a in range(0, 360, 30)]

SHIELD_SHAPE = {"common": kite, "rare": tower, "epic": None, "legendary": roundel}[TIER]
sh_root = P.make_root(scn, "shield_root", rot=(0, -14, 18), loc=(0.84, -0.58, 1.80))
shield, sh_lion = [], None
if SHIELD_SHAPE is not None:
    back = BRIGHTGOLD if TIER == "legendary" else GOLD
    shield = [P.add_prism(scn, "shieldback", SHIELD_SHAPE, 0.11, back),
              P.add_prism(scn, "shieldface", [(x * 0.78, z * 0.80) for x, z in SHIELD_SHAPE],
                          0.11, SURCOAT, loc=(0, -0.06, 0.02))]
    sh_lion = P.add_box(scn, "shieldlion", (0, -0.14, 0.06), (0.26, 0.05, 0.36), back)
    P.parent_all(sh_root, shield + [sh_lion])

# ---- sword: local z=0 sits at the hand, blade runs up +Z ----
# The Vanguard carries no shield, so his blade is the long two-handed one. The
# Paragon's is longer still and gilded at the guard.
BL = {"common": 1.00, "rare": 0.96, "epic": 1.30, "legendary": 1.22}[TIER]
BW = {"common": 1.00, "rare": 0.92, "epic": 1.26, "legendary": 1.10}[TIER]
blade = [(-0.06 * BW, 0.14), (0.06 * BW, 0.14), (0.06 * BW, 1.08 * BL),
         (0.0, 1.32 * BL), (-0.06 * BW, 1.08 * BL)]
sw_root = P.make_root(scn, "sword_root", rot=(0, 132, 0), loc=(-0.60, -0.66, 1.10))
sword = [P.add_prism(scn, "blade", blade, 0.11, BLADE),
         P.add_box(scn, "guard", (0, 0, 0.12), (0.44 * BW, 0.10, 0.10),
                   BRIGHTGOLD if TIER == "legendary" else GOLD),
         P.add_box(scn, "grip", (0, 0, -0.08), (0.11, 0.10, 0.24), LEATH),
         P.add_sphere(scn, "pommel", (0, 0, -0.23), 0.10,
                      BRIGHTGOLD if TIER == "legendary" else GOLD)]
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
