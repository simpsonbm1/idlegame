"""Goblin brute sprite. Palette and pose read off raw_enemy_goblin_brute.png.

Same rig, same lighting, same outline weight, same tone-band positions as the
knight. Only the geometry and the palette change. Enemies face LEFT, so the
root turn is -30 instead of +30; local +X is still SCREEN RIGHT either way.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

scn = P.get_scene()
bpy.context.window.scene = scn
P.setup_render(scn)
P.clear_scene(scn)

# wider and taller than the knight, so a BIGGER CELL -- not a bigger ortho,
# which would silently shrink him relative to every other figure
P.sprite_cam(scn, res=112, target_z=1.76)
px = P.pixel_size(scn)
scn.collection.objects["KeySun"].rotation_euler = (math.radians(50), 0, math.radians(-40))

SKIN = P.toon_mat("SKIN", "#3d6b2e", "#5f9440", "#8ec25c")
LEATH = P.toon_mat("GLEATHER", "#4a3520", "#7a5638", "#a3764c")
WOOD = P.toon_mat("WOOD", "#4a3018", "#6f4a24", "#96693a")
IRON = P.toon_mat("IRON", "#5c5c58", "#8b8b84", "#bcbcb4")
TUSK = P.toon_mat("TUSK", "#b09a6a", "#d8c99a", "#f2e8c8")
DARK = P.flat_mat("GDARK", "#141a12")

figure, detail = [], []

# ---- short thick legs, wide brutish stance ----
for s, yoff in ((-1, -0.24), (1, 0.22)):
    figure.append(P.add_box(scn, "gfoot", (s * 0.50, yoff - 0.08, 0.13), (0.54, 0.72, 0.26), SKIN, bevel=0.04))
    figure.append(P.add_cyl(scn, "gshin", (s * 0.46, yoff, 0.55), 0.26, 0.68, SKIN, verts=8))
    figure.append(P.add_box(scn, "gwrap", (s * 0.46, yoff, 0.34), (0.50, 0.50, 0.22), LEATH))
    figure.append(P.add_cyl(scn, "gthigh", (s * 0.42, yoff * 0.6, 1.06), 0.31, 0.62, SKIN, verts=8))

# ---- hips + loincloth ----
figure.append(P.add_box(scn, "ghips", (0, 0, 1.30), (1.06, 0.66, 0.42), SKIN, bevel=0.06))
figure.append(P.add_prism(scn, "gloin", [(-0.30, 0.30), (0.30, 0.30), (0.24, -0.62), (-0.24, -0.62)],
                          0.10, LEATH, loc=(0.02, -0.36, 1.24)))
figure.append(P.add_box(scn, "gbelt", (0, -0.02, 1.48), (1.10, 0.70, 0.16), LEATH))

# ---- heavy hunched torso: barrel chest over a narrower waist ----
figure.append(P.add_cyl(scn, "gwaist", (0, 0, 1.66), 0.48, 0.42, SKIN, verts=10, scale=(1.10, 0.80, 1)))
figure.append(P.add_sphere(scn, "gchest", (0, -0.06, 2.06), 0.62, SKIN, scale=(1.24, 0.82, 0.86), segs=12, rings=8))
# crossed leather straps
figure.append(P.add_box(scn, "gbaldric", (0, -0.40, 2.02), (1.34, 0.10, 0.15), LEATH,
                        rot=(0, math.radians(34), 0)))

# ---- shoulders: one bare, one with a scrap-iron pauldron ----
figure.append(P.add_sphere(scn, "gshoulderL", (-0.80, -0.10, 2.24), 0.36, SKIN, scale=(1, .95, .88)))
figure.append(P.add_sphere(scn, "gshoulderR", (0.80, -0.10, 2.26), 0.38, SKIN, scale=(1, .95, .88)))
figure.append(P.add_sphere(scn, "gpauldron", (0.86, -0.12, 2.38), 0.36, IRON, scale=(1, 1, .62)))

# ---- thick arms, both forward gripping the club ----
figure.append(P.add_cyl(scn, "gupperL", (-0.84, -0.24, 1.86), 0.24, 0.68, SKIN, verts=8))
figure.append(P.add_cyl(scn, "gforeL", (-0.74, -0.48, 1.44), 0.22, 0.56, SKIN, rot=(math.radians(22), 0, 0), verts=8))
figure.append(P.add_sphere(scn, "gfistL", (-0.68, -0.60, 1.20), 0.22, SKIN))
figure.append(P.add_cyl(scn, "gupperR", (0.84, -0.24, 1.88), 0.24, 0.66, SKIN, verts=8))
figure.append(P.add_cyl(scn, "gforeR", (0.62, -0.52, 1.52), 0.22, 0.60, SKIN, rot=(math.radians(34), 0, math.radians(18)), verts=8))
figure.append(P.add_sphere(scn, "gfistR", (0.40, -0.64, 1.30), 0.22, SKIN))

# ---- head: heavy jaw, brow ridge, tusks, pointed ears ----
figure.append(P.add_cyl(scn, "gneck", (0, 0, 2.44), 0.24, 0.22, SKIN, verts=8))
figure.append(P.add_sphere(scn, "gskull", (0, -0.02, 2.82), 0.50, SKIN, scale=(1.06, 1.0, 0.98), segs=12, rings=8))
figure.append(P.add_box(scn, "gjaw", (0, -0.30, 2.56), (0.74, 0.52, 0.34), SKIN, bevel=0.07))
detail.append(P.add_box(scn, "gbrow", (0, -0.44, 2.96), (0.78, 0.16, 0.14), SKIN))
detail.append(P.add_box(scn, "geyeL", (-0.19, -0.48, 2.84), (0.13, 0.05, 0.10), DARK))
detail.append(P.add_box(scn, "geyeR", (0.19, -0.48, 2.84), (0.13, 0.05, 0.10), DARK))
detail.append(P.add_box(scn, "gmouth", (0, -0.56, 2.58), (0.52, 0.05, 0.07), DARK))
for s in (-1, 1):
    detail.append(P.add_cone(scn, "gtusk", (s * 0.22, -0.55, 2.64), 0.075, 0.0, 0.30, TUSK, verts=6))
    figure.append(P.add_cone(scn, "gear", (s * 0.50, 0.02, 2.92), 0.17, 0.0, 0.54, SKIN,
                             rot=(0, math.radians(s * 68), 0), verts=6))

# ---- spiked club: own root, angled down toward the screen-left ----
club = [(-0.10, -0.20), (0.10, -0.20), (0.10, 0.78), (0.19, 0.86), (0.19, 1.42),
        (0.0, 1.54), (-0.19, 1.42), (-0.19, 0.86), (-0.10, 0.78)]
cl_root = P.make_root(scn, "club_root", rot=(0, -122, 0), loc=(-0.02, -0.78, 1.30))
clubparts = [P.add_prism(scn, "clubshaft", club, 0.20, WOOD),
             P.add_box(scn, "clubgrip", (0, 0, -0.12), (0.14, 0.22, 0.30), LEATH)]
for i, z in enumerate((0.98, 1.20, 1.40)):
    for s in (-1, 1):
        clubparts.append(P.add_cone(scn, "spike", (s * 0.20, 0, z), 0.055, 0.0, 0.22, IRON,
                                    rot=(0, math.radians(s * 90), 0), verts=5))
P.parent_all(cl_root, clubparts)

root = P.make_root(scn, "goblin_root", rot=(0, 0, -30))
P.parent_all(root, figure + detail + [cl_root])

P.outline_all(scn, px, width_px=1.75, skip=tuple(d.name for d in detail))
P.render_to(scn, os.path.join(OUT, "out_goblin.png"))
P.upscale_nearest(os.path.join(OUT, "out_goblin.png"), os.path.join(OUT, "out_goblin_big.png"), 8, bg="#ff00ff")
print("goblin done, figure parts:", len(figure), "| club parts:", len(clubparts))
