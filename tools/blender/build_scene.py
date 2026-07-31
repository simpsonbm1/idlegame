"""Town-to-battlefield vista, rendered as ONE continuous image.

This is the part the AI pipeline kept failing on. M15_ASSET_SPECS.md records it:
"every seam problem this project has hit ... came from marrying mismatched
images at a line of open ground." Here there is nothing to marry. Town, wall and
field are one scene under one camera and one sun, so no seam can exist.

Wide render: 288x96. Ortho scale governs the LARGER axis, so 26 world units wide
and 26*96/288 = 8.67 tall.
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
P.setup_render(scn, res=96)
scn.render.resolution_x = 288
scn.render.resolution_y = 96
P.clear_scene(scn)

P.place_cam(scn, target=(3.0, 7.0, 1.6), rx_deg=83, rz_deg=-14, dist=90, ortho=34.0)
px = scn.camera.data.ortho_scale / scn.render.resolution_x
scn.collection.objects["KeySun"].rotation_euler = (math.radians(46), 0, math.radians(-36))

GRASS = P.toon_mat("GRASS", "#3f5c2e", "#5b7f3e", "#7ea355")
DIRT = P.toon_mat("DIRT", "#4a3a26", "#6d5738", "#8f7752")
STONE = P.toon_mat("WALLSTONE", "#4e4e4a", "#767670", "#9d9d95")
THATCH = P.toon_mat("THATCH", "#a8863c", "#d4b563", "#ecd591")
PLASTER = P.toon_mat("PLASTER", "#8e8474", "#b9ae9c", "#dcd3c4")
TIMBER = P.toon_mat("TIMBER", "#472d18", "#6b4526", "#8f6539")
PINE = P.toon_mat("PINE", "#223a22", "#33512f", "#46693c")
FAR = P.toon_mat("FARHILL", "#4a5566", "#5d6a7d", "#717f93")
SKY_HI = P.flat_mat("SKYHI", "#6f86a8")
SKY_LO = P.flat_mat("SKYLO", "#a8b4c2")
GLOW = P.flat_mat("SCENEGLOW", "#ffcf5c")

near, far_ = [], []      # far_ objects get no outline: too small, would go solid black

# ---- sky bands (flat emission planes, well behind everything) ----
far_.append(P.add_box(scn, "skyhi", (0, 46, 12), (170, 0.4, 30), SKY_HI))
far_.append(P.add_box(scn, "skylo", (0, 45, 1.0), (170, 0.4, 7.0), SKY_LO))

# ---- ground: grass on the town side, trampled dirt on the field side ----
far_.append(P.add_box(scn, "grass", (-22, 2, -0.6), (42, 76, 1.2), GRASS))
far_.append(P.add_box(scn, "dirt", (20, 2, -0.6), (42, 76, 1.2), DIRT))

# ---- distant ridge and forest ----
for i, (x, y, r, h) in enumerate([(-28, 33, 11, 5.5), (-8, 37, 14, 7.5), (14, 34, 10, 4.5),
                                  (32, 38, 13, 6.5)]):
    far_.append(P.add_cone(scn, "ridge", (x, y, 0), r, 0.6, h * 2, FAR, verts=7))
for i in range(18):
    x = 4 + (i % 9) * 3.9 + (i // 9) * 1.9
    y = 19 + (i // 9) * 5.5 + (i % 3) * 1.8
    s = 0.85 + 0.1 * (i % 4)
    far_.append(P.add_cyl(scn, "trunk", (x, y, 0.6 * s), 0.22, 1.4 * s, TIMBER, verts=6))
    for k, (zz, rr) in enumerate(((1.6, 1.5), (2.7, 1.15), (3.6, 0.75))):
        far_.append(P.add_cone(scn, "pine", (x, y, zz * s), rr * s, 0.05, 1.9 * s, PINE, verts=7))

# ---- the kingdom wall: runs along Y, gate facing the field ----
WX, WT, WH = -1.6, 1.4, 3.9        # wall centre-x, thickness, height
for y0, y1 in ((-14, 1.2), (5.0, 17)):
    near.append(P.add_box(scn, "wall", (WX, (y0 + y1) / 2, WH / 2), (WT, y1 - y0, WH), STONE))
    n = int((y1 - y0) / 1.5)
    for i in range(n):                                   # crenellations
        near.append(P.add_box(scn, "crenel", (WX, y0 + 0.75 + i * 1.5, WH + 0.34),
                              (WT * 0.9, 0.8, 0.68), STONE))
# gate: lintel over a recessed wooden door, flanked by drum towers
near.append(P.add_box(scn, "lintel", (WX, 3.1, WH - 0.7), (WT, 3.8, 1.4), STONE))
near.append(P.add_box(scn, "gate", (WX - 0.1, 3.1, 1.6), (WT * 0.55, 3.2, 3.2),
                      P.toon_mat("GATEWOOD", "#3a2413", "#5a3a1f", "#7a5230")))
ROOFTILE = P.toon_mat("ROOFTILE", "#5a2f2a", "#84463c", "#a86054")
for gy in (0.9, 5.3):
    near.append(P.add_cyl(scn, "tower", (WX, gy, 3.1), 1.45, 6.2, STONE, verts=10))
    for i in range(10):                                   # tower crenellations
        a = math.radians(i * 36)
        near.append(P.add_box(scn, "tcrenel",
                              (WX + 1.28 * math.sin(a), gy + 1.28 * math.cos(a), 6.5),
                              (0.5, 0.5, 0.7), STONE, rot=(0, 0, -a)))
    near.append(P.add_cone(scn, "towercap", (WX, gy, 7.4), 1.55, 0.0, 1.9, ROOFTILE, verts=10))


def cottage(loc, rot_z, scale=1.0):
    """Same cottage geometry as the standalone sprite, placed in the vista.
    One model, reused -- the town cannot drift out of style with itself."""
    W, D, PL, WT_ = 1.35 * scale, 0.95 * scale, 0.36 * scale, 2.0 * scale
    r = P.make_root(scn, "cot_root", rot=(0, 0, rot_z), loc=loc)
    parts = [P.add_box(scn, "c_plinth", (0, 0, PL / 2), (W * 2.09, D * 2.09, PL), STONE),
             P.add_box(scn, "c_walls", (0, 0, (PL + WT_) / 2), (W * 2, D * 2, WT_ - PL), PLASTER)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(P.add_box(scn, "c_post", (sx * W, sy * D, (PL + WT_) / 2),
                                   (0.19, 0.19, WT_ - PL), TIMBER))
    parts.append(P.add_box(scn, "c_plate", (0, 0, WT_ - 0.09), (W * 2.05, D * 2.05, 0.18), TIMBER))
    OH, RG, EA = 0.28 * scale, 0.95 * scale, 0.26 * scale
    parts.append(P.add_prism(scn, "c_roof",
                             [(-W - OH, WT_ - 0.07), (0, WT_ + RG), (W + OH, WT_ - 0.07),
                              (W + OH, WT_ - 0.07 - EA), (0, WT_ + RG - EA), (-W - OH, WT_ - 0.07 - EA)],
                             D * 2 + 0.44, THATCH))
    for sy in (-1, 1):
        parts.append(P.add_prism(scn, "c_gable",
                                 [(-W, WT_ - 0.09), (0, WT_ + RG - 0.24), (W, WT_ - 0.09)],
                                 0.15, PLASTER, loc=(0, sy * D, 0)))
    parts.append(P.add_box(scn, "c_win", (W + 0.02, -0.15, 1.30 * scale), (0.12, 0.55, 0.50), TIMBER))
    parts.append(P.add_box(scn, "c_pane", (W + 0.07, -0.15, 1.30 * scale), (0.09, 0.38, 0.34), GLOW))
    parts.append(P.add_box(scn, "c_chim", (0.5 * scale, 0.5 * scale, WT_ + 0.72 * scale),
                           (0.32, 0.32, 1.45 * scale), STONE))
    P.parent_all(r, parts)
    return parts, r


roots = []
for loc, rz, sc in [((-7.0, -1.5, 0), 18, 1.0), ((-13.0, 3.0, 0), -12, 0.95),
                    ((-6.2, 6.5, 0), 34, 0.88), ((-15.5, 10.5, 0), 8, 0.8),
                    ((-8.5, 13.0, 0), -22, 0.72)]:
    parts, r = cottage(loc, rz, sc)
    near += parts
    roots.append(r)

# a few field rocks so the battle side is not empty ground
for x, y, s in ((9.5, 1.0, 0.6), (15.0, 6.0, 0.45), (5.5, 9.5, 0.7), (20.0, 2.5, 0.42)):
    near.append(P.add_sphere(scn, "rock", (x, y, s * 0.45), s, STONE, scale=(1, 0.9, 0.55), segs=7, rings=4))
SCRUB = P.toon_mat("SCRUB", "#3a4a25", "#556b33", "#6f8845")
for i in range(22):
    x = 3.0 + ((i * 7) % 23) * 1.15
    y = -3.0 + ((i * 11) % 19) * 1.05
    far_.append(P.add_sphere(scn, "tuft", (x, y, 0.06), 0.28 + 0.08 * (i % 3), SCRUB,
                             scale=(1.5, 1.1, 0.36), segs=6, rings=3))

P.outline_all(scn, px, width_px=1.5, skip=tuple(o.name for o in far_))
P.render_to(scn, os.path.join(OUT, "out_scene.png"))
P.upscale_nearest(os.path.join(OUT, "out_scene.png"), os.path.join(OUT, "out_scene_big.png"), 4)
print("scene done | near:", len(near), "far:", len(far_), "| px:", round(px, 4))
