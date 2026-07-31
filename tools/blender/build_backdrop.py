"""The game backdrop, rebuilt in the rig's style.

Matches what game.js actually expects of `scene_backdrop_v2.png`:

  - the locked camera from M15_ASSET_SPECS.md, "steep high angle,
    strategy-map-from-a-watchtower"
  - the wall running vertically down the frame, seated so game.js can put its
    centre on 46% across (`SCENE_WALL_FRAC`)
  - composition aspect 2400/1270, the kept region after the watermark crop
  - NO buildings: game.js draws building sprites onto the plots itself, so the
    town ground stays clear across the `BUILDING_PLOTS` band
  - a round stone plaza with a well in the lower left, where `TOWN_CROWD_SPOTS`
    puts the crowd

Pixel density is exactly 2x SPRITE_PX. M15_ASSET_SPECS.md measured the painted
backdrop at 3-4x chunkier than the characters and recorded "2x finer is the sweet
spot", so 2x is the documented target rather than a guess. Holding that density
while covering a whole town and battlefield is what sets the resolution: 60 world
units at 2x density needs 768 pixels across, not 384.

An orthographic camera has no horizon, so distance never thins anything out and
the ground would otherwise run past the top of the frame. The ground therefore
STOPS at GROUND_FAR, with the range and the sky panel standing just beyond it.
That is the same trick the painting uses, made explicit.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()

RES_X, RES_Y = 768, 406          # 768/406 = 1.891, the 2400/1270 kept-region aspect
ORTHO = P.SPRITE_PX * 2 * RES_X  # 60.0 world units across

scn = P.get_scene()
bpy.context.window.scene = scn
P.setup_render(scn)
P.clear_scene(scn)
scn.render.resolution_x, scn.render.resolution_y = RES_X, RES_Y

RX = 28.0                        # 62 degrees above horizontal: the watchtower angle
P.place_cam(scn, target=(0, 0, 0), rx_deg=RX, rz_deg=0, dist=90, ortho=ORTHO)
px = ORTHO / RES_X
scn.collection.objects["KeySun"].rotation_euler = (math.radians(50), 0, math.radians(-40))

FRAME_H = ORTHO * RES_Y / RES_X            # 31.7 world units top to bottom
WALL_X = -ORTHO / 2 + 0.46 * ORTHO         # 46% across, where game.js seats the wall
GROUND_FAR = 10.0                          # ground stops; range and sky stand beyond
# Town building plots occupy roughly x -23..-7, y -3..6.5 at this framing. Keep clear.

GRASS = P.toon_mat("BG_GRASS", "#3f612d", "#537c39", "#6d9c4b") if False else \
        P.toon_mat("BG_GRASS", "#3f612d", "#537c39", "#6d9c4b")
GRASS2 = P.toon_mat("BG_GRASS2", "#37552a", "#496e33", "#608a41")
DIRT = P.toon_mat("BG_DIRT", "#4a3b28", "#6b5740", "#8a7458")
STONE = P.toon_mat("BG_STONE", "#6a655a", "#8e8878", "#b2ab94")
PAVE = P.toon_mat("BG_PAVE", "#66635a", "#87836f", "#a8a48c")
PINE = P.toon_mat("BG_PINE", "#1e3320", "#2c4a2b", "#3d6238")
BARK = P.toon_mat("BG_BARK", "#33241a", "#4a3524", "#63492f")
LEAF = P.toon_mat("BG_LEAF", "#2c4526", "#3f6134", "#547f44")
MTN = P.toon_mat("BG_MTN", "#4b525d", "#616976", "#828a96")
MTN_FAR = P.toon_mat("BG_MTNFAR", "#565d68", "#6b7380", "#89909c")
SNOW = P.toon_mat("BG_SNOW", "#9aa3af", "#bcc3cd", "#e2e7ee")
PINE_FAR = P.toon_mat("BG_PINEFAR", "#283a2c", "#354c37", "#456045")
HAZE = P.flat_mat("BG_HAZE", "#5b6668")
SKY_HI = P.flat_mat("BG_SKYHI", "#464c56")
SKY_LO = P.flat_mat("BG_SKYLO", "#6f7783")
DARK = P.flat_mat("BG_DARK", "#20211c")

solid, flat = [], []       # `flat` gets no outline: ground, decals, sky, distance

# ---- sky panel, distant range, ground ----
flat.append(P.add_box(scn, "sky", (0, 13.0, 12.0), (200, 0.4, 44), SKY_HI))
flat.append(P.add_box(scn, "skyband", (0, 12.6, 1.4), (200, 0.4, 5.0), SKY_LO))
# Two ranges. The far one is hazier and reads as distance, which an ortho camera
# gives no other way of suggesting.
# Squashed almost flat in Y. A cone wide enough to read as a mountain is also
# wide in DEPTH, and its near edge then reaches forward past the wall and out
# onto the town grass, which is exactly what happened. Distant scenery in an
# ortho render wants to be a standing flat, not a solid.
MTN_FLAT = 0.16
for x, y, r, h in ((-31, 13.4, 8.5, 5.0), (-17, 13.8, 7.5, 6.2), (-2, 13.2, 8.0, 5.4),
                   (13, 13.9, 7.8, 6.0), (27, 13.3, 8.6, 5.2)):
    m = P.add_cone(scn, "mtnfar", (x, y, 0), r, 0.4, h * 2, MTN_FAR, verts=7)
    m.scale = (1, MTN_FLAT, 1)
    flat.append(m)
for x, y, r, h in ((-26, 11.4, 6.4, 6.2), (-13, 11.9, 5.6, 7.4), (-1, 11.1, 5.0, 5.2),
                   (9, 11.8, 6.2, 7.0), (20, 11.2, 5.4, 5.6), (30, 11.9, 6.6, 6.6)):
    m = P.add_cone(scn, "mtn", (x, y, 0), r, 0.4, h * 2, MTN, verts=7)
    m.scale = (1, MTN_FLAT, 1)
    flat.append(m)
    cap = P.add_cone(scn, "snow", (x, y - 0.25, h - 1.05), r * 0.21, 0.25, 2.1, SNOW, verts=7)
    cap.scale = (1, MTN_FLAT, 1)
    flat.append(cap)
flat.append(P.add_box(scn, "ground", (0, (GROUND_FAR - 34) / 2, -0.5),
                      (200, 34 + GROUND_FAR, 1.0), GRASS))
# The ground plane simply ends, and an ortho camera renders that as a clean cut
# across the frame. A haze strip plus a continuous distant treeline hides the cut.
flat.append(P.add_box(scn, "haze", (0, GROUND_FAR + 0.5, 0.7), (200, 0.3, 2.6), HAZE))
for i in range(78):
    x = -42.0 + i * 1.12 + 0.35 * (i % 3)
    s_ = 0.58 + 0.11 * (i % 4)
    for row, dy in ((0, 0.0), (1, 0.62)):
        flat.append(P.add_cone(scn, "fartree",
                               (x + row * 0.55, GROUND_FAR - 0.15 + dy, 0.9 * s_),
                               1.05 * s_, 0.05, 2.6 * s_, PINE_FAR, verts=6))


def decal(name, x, y, rx_, ry_, mat, z=0.03):
    ob = P.add_cyl(scn, name, (x, y, z), 1.0, 0.06, mat, verts=9, scale=(rx_, ry_, 1))
    flat.append(ob)
    return ob


# ---- ground variation: churned dirt on the field, scrub on both sides ----
for cx, cy, n in ((6.0, -4.0, 5), (16.0, -9.0, 6), (24.0, -3.0, 4),
                  (11.0, -14.0, 5), (27.0, -13.0, 4)):
    for i in range(n):                     # clustered, so the field reads churned
        x = cx + ((i * 7) % 5 - 2) * 1.5
        y = cy + ((i * 5) % 5 - 2) * 1.1
        decal("churn", x, y, 1.5 + 0.7 * (i % 3), 0.95 + 0.4 * (i % 2), DIRT)
for i in range(48):
    x = -29.0 + ((i * 11) % 31) * 1.95
    y = -15.5 + ((i * 5) % 21) * 1.3
    decal("scrub", x, y, 0.75 + 0.4 * (i % 3), 0.5 + 0.25 * (i % 2), GRASS2)

# ---- roads: out through the gate, and west to the plaza ----
for i in range(22):
    t = i / 21.0
    decal("roadE", WALL_X + 1.6 + t * 29.0, -2.6 + t * t * 11.0, 1.9, 1.25, DIRT, z=0.05)
for i in range(16):
    t = i / 15.0
    decal("roadW", WALL_X - 1.4 - t * 13.5, -3.2 - t * 3.6, 1.7, 1.15, DIRT, z=0.05)
for i in range(12):
    t = i / 11.0
    decal("plazapath", -16.6 + t * 1.0, -13.2 - t * 4.2, 1.0, 1.15, DIRT, z=0.05)

# ---- round stone plaza and well, lower left ----
solid.append(P.add_cyl(scn, "plaza", (-16.8, -8.6, 0.06), 4.2, 0.16, PAVE, verts=18))
solid.append(P.add_cyl(scn, "wellwall", (-16.8, -8.3, 0.42), 0.8, 0.78, STONE, verts=10))
flat.append(P.add_cyl(scn, "wellmouth", (-16.8, -8.3, 0.82), 0.54, 0.06, DARK, verts=10))

# ---- the wall: long run down the frame, plus the back wall along the town ----
WH, WT = 3.2, 1.15
GATE_Y0, GATE_Y1 = -4.6, -1.6
for y0, y1 in ((-22.0, GATE_Y0), (GATE_Y1, GROUND_FAR - 0.6)):
    solid.append(P.add_box(scn, "wall", (WALL_X, (y0 + y1) / 2, WH / 2),
                           (WT, y1 - y0, WH), STONE))
    for i in range(int((y1 - y0) / 1.3)):
        solid.append(P.add_box(scn, "crenel", (WALL_X, y0 + 0.65 + i * 1.3, WH + 0.32),
                               (WT * 0.92, 0.7, 0.64), STONE))
BW_X0, BW_Y = -30.0, GROUND_FAR - 0.6
solid.append(P.add_box(scn, "backwall", ((BW_X0 + WALL_X) / 2, BW_Y, WH / 2),
                       (WALL_X - BW_X0, WT, WH), STONE))
for i in range(int((WALL_X - BW_X0) / 1.3)):
    solid.append(P.add_box(scn, "bcrenel", (BW_X0 + 0.65 + i * 1.3, BW_Y, WH + 0.32),
                           (0.7, WT * 0.92, 0.64), STONE))

# gatehouse: two drum-square towers with a lintel and a recessed timber gate
solid.append(P.add_box(scn, "corner", (WALL_X, BW_Y, 2.5), (2.5, 2.5, 5.0), STONE))
for sx, sy in ((-0.8, 0), (0.8, 0), (0, -0.8), (0, 0.8)):
    solid.append(P.add_box(scn, "ccrenel", (WALL_X + sx, BW_Y + sy, 5.3),
                           (0.85, 0.85, 0.6), STONE))
for gy in (GATE_Y0, GATE_Y1):
    solid.append(P.add_box(scn, "gtower", (WALL_X, gy, 2.7), (2.9, 2.0, 5.4), STONE))
    for sx in (-0.95, 0, 0.95):
        solid.append(P.add_box(scn, "gcrenel", (WALL_X + sx, gy, 5.72), (0.7, 2.1, 0.64), STONE))
solid.append(P.add_box(scn, "lintel", (WALL_X, (GATE_Y0 + GATE_Y1) / 2, WH - 0.55),
                       (WT, GATE_Y1 - GATE_Y0, 2.1), STONE))
solid.append(P.add_box(scn, "gate", (WALL_X - 0.14, (GATE_Y0 + GATE_Y1) / 2, 0.95),
                       (WT * 0.5, 2.4, 1.9),
                       P.toon_mat("BG_GATEWOOD", "#3a2413", "#5a3a1f", "#7a5230")))

# ---- pine forest on the field side, breaking the far edge ----
for i in range(30):
    x = 5.0 + ((i * 17) % 37) * 0.72
    y = 5.4 + ((i * 5) % 13) * 0.34
    s = 0.9 + 0.14 * (i % 4)
    solid.append(P.add_cyl(scn, "trunk", (x, y, 0.3 * s), 0.16, 0.66 * s, BARK, verts=6))
    for zz, rr in ((0.9, 1.0), (1.55, 0.74), (2.1, 0.46)):
        solid.append(P.add_cone(scn, "pine", (x, y, zz * s), rr * s, 0.04, 1.25 * s, PINE, verts=7))

# ---- broadleaf trees inside the town, clear of the plot band ----
for x, y, s in ((-27.5, 3.0, 1.0), (-26.4, -6.4, 0.9), (-9.0, -11.0, 0.95),
                (-23.0, -13.5, 0.85), (-5.5, 7.6, 0.9)):
    solid.append(P.add_cyl(scn, "ttrunk", (x, y, 0.4 * s), 0.2, 0.85 * s, BARK, verts=6))
    solid.append(P.add_sphere(scn, "canopy", (x, y, 1.42 * s), 1.2 * s, LEAF,
                              scale=(1, 1, 0.82), segs=10, rings=6))

# ---- field boulders ----
for x, y, s in ((8.0, -5.6, 0.62), (18.0, -11.5, 0.5), (25.0, -2.4, 0.7),
                (12.0, -15.0, 0.45), (5.0, -11.0, 0.4), (28.0, -8.0, 0.55)):
    solid.append(P.add_sphere(scn, "rock", (x, y, s * 0.4), s, STONE,
                              scale=(1.15, 0.95, 0.6), segs=7, rings=4))

P.outline_all(scn, px, width_px=1.4, skip=tuple(o.name for o in flat))
P.render_to(scn, os.path.join(OUT, "out_backdrop.png"))
P.upscale_nearest(os.path.join(OUT, "out_backdrop.png"),
                  os.path.join(OUT, "out_backdrop_big.png"), 2)
print("backdrop %dx%d | px %.4f (2x sprite) | frame %.1f x %.1f | wall x %.2f = 46%%"
      % (RES_X, RES_Y, px, ORTHO, FRAME_H, WALL_X))
