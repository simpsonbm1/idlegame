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
figure.append(P.add_box(scn, "surcoat", (0, -0.30, 1.52), (0.56, 0.07, 1.24), NAVY))
figure.append(P.add_box(scn, "surcoatB", (0, 0.29, 1.52), (0.56, 0.07, 1.24), NAVY))
detail.append(P.add_box(scn, "lion", (0, -0.35, 1.86), (0.22, 0.04, 0.30), GOLD))

# ---- shoulders and arms, pulled forward off the torso ----
figure.append(P.add_sphere(scn, "pauldronR", (-0.70, -0.10, 2.18), 0.35, STEEL, scale=(1, .95, .76)))
figure.append(P.add_sphere(scn, "pauldronL", (0.70, -0.10, 2.20), 0.30, STEEL, scale=(1, .95, .78)))
figure.append(P.add_cyl(scn, "upperR", (-0.70, -0.18, 1.84), 0.18, 0.60, STEEL))
figure.append(P.add_cyl(scn, "foreR", (-0.63, -0.32, 1.38), 0.17, 0.50, STEEL, rot=(math.radians(16), 0, 0)))
figure.append(P.add_box(scn, "gauntR", (-0.59, -0.42, 1.12), (0.26, 0.26, 0.24), STEEL))
figure.append(P.add_cyl(scn, "upperL", (0.70, -0.16, 1.86), 0.17, 0.56, STEEL))
figure.append(P.add_cyl(scn, "foreL", (0.66, -0.30, 1.46), 0.16, 0.48, STEEL, rot=(math.radians(24), 0, 0)))

# ---- gorget and faceted great helm ----
figure.append(P.add_box(scn, "gorget", (0, 0, 2.40), (0.52, 0.46, 0.18), STEEL, bevel=0.04))
figure += P.add_ridged(scn, "helm", (0, -0.02, 2.68), (0.66, 0.56, 0.50), STEEL, splay=12, bevel=0.05)
detail.append(P.add_box(scn, "crossH", (0, -0.32, 2.69), (0.50, 0.05, 0.08), DARK))
detail.append(P.add_box(scn, "crossV", (0, -0.32, 2.68), (0.09, 0.05, 0.36), DARK))

# ---- kite shield ----
kite = [(-0.20, 0.60), (-0.40, 0.50), (-0.44, 0.22), (-0.38, -0.16), (-0.22, -0.56),
        (0.0, -0.88), (0.22, -0.56), (0.38, -0.16), (0.44, 0.22), (0.40, 0.50), (0.20, 0.60)]
sh_root = P.make_root(scn, "shield_root", rot=(0, -14, 18), loc=(0.84, -0.58, 1.80))
shield = [P.add_prism(scn, "shieldback", kite, 0.11, GOLD),
          P.add_prism(scn, "shieldface", [(x * 0.78, z * 0.80) for x, z in kite], 0.11,
                      NAVY, loc=(0, -0.06, 0.02))]
sh_lion = P.add_box(scn, "shieldlion", (0, -0.14, 0.06), (0.26, 0.05, 0.36), GOLD)
P.parent_all(sh_root, shield + [sh_lion])

# ---- longsword: local z=0 sits at the hand, blade runs up +Z ----
blade = [(-0.06, 0.14), (0.06, 0.14), (0.06, 1.08), (0.0, 1.32), (-0.06, 1.08)]
sw_root = P.make_root(scn, "sword_root", rot=(0, 132, 0), loc=(-0.60, -0.66, 1.10))
sword = [P.add_prism(scn, "blade", blade, 0.11, BLADE),
         P.add_box(scn, "guard", (0, 0, 0.12), (0.44, 0.10, 0.10), GOLD),
         P.add_box(scn, "grip", (0, 0, -0.08), (0.11, 0.10, 0.24), LEATH),
         P.add_sphere(scn, "pommel", (0, 0, -0.23), 0.10, GOLD)]
P.parent_all(sw_root, sword)

# Rarity flourishes. The guardian carries entries 56-58, and his own sprite is
# the Common tier, so only rare, epic and legendary produce files.
TRIM = H.trim_mat(M := {"steel": STEEL, "gold": GOLD, "brightgold":
                        P.toon_mat("HBRIGHTGOLD", "#a8790f", "#e0b132", "#ffeb9a")})
if TRIM:
    detail.append(P.add_box(scn, "shieldrim", (0, -0.34, 1.86), (0.30, 0.05, 0.10), TRIM))
    detail.append(P.add_box(scn, "gorgettrim", (0, -0.26, 2.40), (0.52, 0.07, 0.09), TRIM))
if H.tier() in ("epic", "legendary"):
    figure.append(P.add_cone(scn, "plume", (0, 0.20, 3.06), 0.10, 0.03, 0.44,
                             P.toon_mat("HCRIMSON", "#6b1d1c", "#9c2f27", "#c85641"),
                             rot=(math.radians(-14), 0, 0), verts=6))
if H.is_legendary():
    figure.append(P.add_cone(scn, "cloak", (0, 0.30, 1.76), 0.62, 0.34, 1.80,
                             P.toon_mat("HCRIMSON", "#6b1d1c", "#9c2f27", "#c85641"), verts=10))

# The guardian is the baseline the USER RULING sizes everything else against, so
# he goes through the same role-driven sizing as everyone else rather than being
# left at whatever height his coordinates happen to give.
S.finish(scn, px, "knight" + H.suffix(), figure, detail, [], roots=[sh_root, sw_root],
         skip_extra=("shieldlion",), facing=S.FACE_RIGHT, role="hero")
