"""Undead Legion caster -- M15_ASSET_SPECS.md entry 36.

  "a skeletal necromancer in dark violet robes with bone-white trim, staff
   topped with a skull glowing sickly green"

Family rules from the same doc: "pale bone and gray dead flesh, ancient rusted
armor, glowing spectral teal-violet accents -- keep overall values mid-bright,
bone reads bright". Enemies face LEFT.

Built from the written spec alone. No sprite exists for any Undead Legion entry,
so nothing here is traced off a reference. The rig settings (resolution, sun,
outline width, tone-band positions) are copied verbatim from the knight and the
goblin, which is the whole point: a new character inherits the style instead of
being asked to match it.

The new shape problem this one poses is the robe. There are no legs to build a
stance from, so the silhouette has to come from a flared cone, a shoulder mantle
and a hood -- none of which the two earlier figures used.
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

# the staff reaches above the hood, so the cell is taller than the knight's
P.sprite_cam(scn, res=112, target_z=1.76)
px = P.pixel_size(scn)
scn.collection.objects["KeySun"].rotation_euler = (math.radians(50), 0, math.radians(-40))

ROBE = P.toon_mat("ROBE", "#2a1c3f", "#443063", "#63498c")
ROBE_D = P.toon_mat("ROBEDARK", "#1d1230", "#33234c", "#4b3670")
BONE = P.toon_mat("BONE", "#a89a7c", "#d8ceb0", "#f4eeda")
IRON = P.toon_mat("RUSTIRON", "#4a382c", "#6e5340", "#93725a")
GLOW = P.flat_mat("NECROGLOW", "#8cff7a")
GLOW_D = P.flat_mat("NECROHALO", "#3f8f3a")
TEAL = P.flat_mat("SPECTRAL", "#5fe6d8")
DARK = P.flat_mat("SOCKET", "#0d1410")

figure, detail, noline = [], [], []

# ---- robe: a flared cone to the ground, which is the whole lower silhouette ----
figure.append(P.add_cone(scn, "skirt", (0, 0, 0.88), 0.90, 0.44, 1.76, ROBE, verts=12))
figure.append(P.add_cyl(scn, "hem", (0, 0, 0.06), 0.93, 0.10, BONE, verts=12))
figure.append(P.add_cone(scn, "chest", (0, 0, 2.14), 0.47, 0.40, 0.98, ROBE, verts=12))
# bone-white placket down the front of the robe
detail.append(P.add_box(scn, "placket", (0, -0.45, 2.16), (0.10, 0.08, 0.78), BONE))
detail.append(P.add_box(scn, "sash", (0, -0.44, 1.72), (0.62, 0.09, 0.13), IRON))

# ---- shoulder mantle + hood: the upper silhouette ----
figure.append(P.add_sphere(scn, "shoulderL", (-0.50, -0.04, 2.48), 0.25, ROBE, scale=(1, .95, .8)))
figure.append(P.add_sphere(scn, "shoulderR", (0.50, -0.04, 2.50), 0.25, ROBE, scale=(1, .95, .8)))
figure.append(P.add_cone(scn, "mantle", (0, -0.02, 2.60), 0.72, 0.30, 0.46, ROBE_D, verts=12))
figure.append(P.add_cone(scn, "hood", (0, -0.04, 2.96), 0.44, 0.16, 0.56, ROBE_D, verts=10))

# ---- skull inside the hood, the brightest thing on the figure ----
figure.append(P.add_sphere(scn, "skull", (0, -0.24, 2.88), 0.24, BONE, scale=(1, 1.02, 1.06), segs=10, rings=7))
detail.append(P.add_box(scn, "jaw", (0, -0.30, 2.68), (0.25, 0.20, 0.14), BONE))
detail.append(P.add_box(scn, "teeth", (0, -0.41, 2.76), (0.22, 0.04, 0.04), DARK))
detail.append(P.add_box(scn, "cheek", (0, -0.40, 2.83), (0.30, 0.04, 0.04), DARK))
for s in (-1, 1):
    detail.append(P.add_box(scn, "socket", (s * 0.10, -0.42, 2.92), (0.12, 0.05, 0.10), DARK))
    noline.append(P.add_box(scn, "eyefire", (s * 0.10, -0.45, 2.92), (0.05, 0.04, 0.04), TEAL))

# ---- sleeves: his staff arm forward, his free hand raised in a casting gesture ----
figure.append(P.add_cone(scn, "sleeveA1", (-0.56, -0.16, 2.16), 0.21, 0.16, 0.60, ROBE, verts=8))
figure.append(P.add_cone(scn, "sleeveA2", (-0.62, -0.34, 1.70), 0.18, 0.13, 0.54, ROBE,
                         rot=(math.radians(18), 0, 0), verts=8))
figure.append(P.add_sphere(scn, "handA", (-0.66, -0.44, 1.44), 0.14, BONE))
figure.append(P.add_cone(scn, "sleeveB1", (0.56, -0.18, 2.20), 0.21, 0.16, 0.56, ROBE, verts=8))
figure.append(P.add_cone(scn, "sleeveB2", (0.60, -0.40, 2.02), 0.17, 0.12, 0.50, ROBE,
                         rot=(math.radians(62), 0, 0), verts=8))
figure.append(P.add_sphere(scn, "handB", (0.62, -0.56, 2.22), 0.14, BONE))
# a flame rising from the free hand, not a cluster -- three blobs at the same
# height read as a symbol rather than as fire
for i, (dz, r, m) in enumerate(((0.19, 0.085, GLOW), (0.31, 0.065, GLOW), (0.42, 0.045, GLOW_D))):
    noline.append(P.add_sphere(scn, "wisp", (0.62 + 0.03 * i, -0.58, 2.22 + dz), r, m, segs=8, rings=5))

# ---- staff: own root so the lean is one number ----
st_root = P.make_root(scn, "staff_root", rot=(0, -13, 0), loc=(-0.70, -0.50, 1.90))
staff = [P.add_cyl(scn, "shaft", (0, 0, 0), 0.058, 2.70, IRON, verts=6),
         P.add_cyl(scn, "ferrule", (0, 0, 1.24), 0.085, 0.16, BONE, verts=6),
         P.add_sphere(scn, "staffskull", (0, -0.02, 1.47), 0.19, BONE, scale=(1, 1.02, 1.08), segs=10, rings=7),
         P.add_box(scn, "staffjaw", (0, -0.09, 1.34), (0.17, 0.14, 0.09), BONE)]
glowbits = [P.add_box(scn, "sfire", (s * 0.075, -0.19, 1.50), (0.07, 0.05, 0.07), GLOW) for s in (-1, 1)]
glowbits.append(P.add_box(scn, "sgrin", (0, -0.19, 1.38), (0.15, 0.04, 0.03), GLOW_D))
for i, (dz, r) in enumerate(((0.30, 0.11), (0.44, 0.085), (0.56, 0.055))):
    glowbits.append(P.add_sphere(scn, "plume", (0.02 * i, -0.04, 1.47 + dz), r,
                                 GLOW if i < 2 else GLOW_D, segs=8, rings=5))
P.parent_all(st_root, staff + glowbits)

root = P.make_root(scn, "caster_root", rot=(0, 0, -30))
P.parent_all(root, figure + detail + noline + [st_root])

skip = tuple(o.name for o in detail + noline) + ("sfire", "sgrin", "plume")
P.outline_all(scn, px, width_px=1.75, skip=skip)
P.render_to(scn, os.path.join(OUT, "out_undead_caster.png"))
P.upscale_nearest(os.path.join(OUT, "out_undead_caster.png"),
                  os.path.join(OUT, "out_undead_caster_big.png"), 8, bg="#ff00ff")
print("undead caster done, figure parts:", len(figure), "| staff parts:", len(staff) + len(glowbits))
