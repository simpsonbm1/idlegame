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
from mathutils import noise as bnoise, Vector
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
# Screen-up on this camera is world +Y, not world +Z as it is for the character
# sprites, so "lit from the upper left" needs a different azimuth here. At -40 the
# light came from -X and -Y, which on a top-down view is the BOTTOM left, and every
# shadow fell up-screen.
#
# Do not swing it all the way to the top either. We look along -Y, so the slopes we
# SEE are the ones facing -Y; light straight down-screen back-lights every one of
# them and the whole ground goes dark. -105 keeps the light left-and-slightly-above,
# which throws shadows right and a little down while the ground stays lit.
scn.collection.objects["KeySun"].rotation_euler = (math.radians(50), 0, math.radians(-105))
scn.collection.objects["KeySun"].data.energy = 2.6

# A surface in cast shadow receives ZERO direct light, so it lands on the darkest
# ramp stop no matter how many stops the ramp has -- which is why raising the step
# count alone left every shadow one flat colour. This fill throws no shadow of its
# own, so shadowed ground still gets a contribution that varies with its slope and
# the shading inside shadow has somewhere to go.
fill_data = bpy.data.lights.new("FillSun", 'SUN')
fill_data.energy = 1.5
fill_data.angle = 0.0
fill_data.use_shadow = False
fill = bpy.data.objects.new("FillSun", fill_data)
fill.rotation_euler = (math.radians(62), 0, math.radians(88))
scn.collection.objects.link(fill)

FRAME_H = ORTHO * RES_Y / RES_X            # 31.7 world units top to bottom
# World size of one rendered pixel along each ground axis. Depth foreshortens by
# cos(elevation), so a step in Y covers fewer pixels than the same step in X.
SNAP_U = px
SNAP_V = px / math.cos(math.radians(RX))
WALL_X = -ORTHO / 2 + 0.46 * ORTHO         # 46% across, where game.js seats the wall
GROUND_FAR = 10.0                          # ground stops; range and sky stand beyond
# Town building plots occupy roughly x -23..-7, y -3..6.5 at this framing. Keep clear.

# Three tones is right for a character and wrong for a backdrop: large surfaces
# hold one flat tone each and the scene reads as cut paper. Six gives slopes and
# curved forms somewhere to go while staying hard-banded. The anchors are widened
# too, since six shades interpolated between narrow anchors are six near-identical
# colours.
N = 6
# MEASURED by rendering with the ramp swapped for a linear black-to-white one and
# reading the pixels back (remembering the saved image is sRGB while the ramp reads
# linear). Histogram of the ground in this scene: a shadow cluster over 0.13-0.33
# peaking at 0.23, a lit cluster over 0.63-0.83 peaking at 0.77, and NOTHING
# between 0.375 and 0.625, because hard shadows give a bimodal distribution.
# Evenly spaced stops therefore strand half of themselves in the empty middle,
# which is why raising the step count kept rendering as two-tone. These positions
# put three stops inside each cluster, so both the lit ground and the shadow have
# shades to move through. Re-measure if the lights change.
SHADE_POS = (0.0, 0.17, 0.235, 0.66, 0.735, 0.768)
GRASS = P.toon_mat("BG_GRASS", "#31502a", "#4d7536", "#7cab54", steps=N, positions=SHADE_POS)
GRASS2 = P.toon_mat("BG_GRASS2", "#2a4422", "#446630", "#6d9a4a", steps=N, positions=SHADE_POS)
DIRT = P.toon_mat("BG_DIRT", "#3a2d1e", "#665238", "#a08862", steps=N, positions=SHADE_POS)
STONE = P.toon_mat("BG_STONE", "#524e45", "#8a8474", "#c4bda3", steps=N, positions=SHADE_POS)
STONE_A = P.toon_mat("BG_STONEA", "#4d4941", "#827b6c", "#b9b29a", steps=N, positions=SHADE_POS)
STONE_B = P.toon_mat("BG_STONEB", "#595348", "#918a78", "#ccc5a9", steps=N, positions=SHADE_POS)
STONE_C = P.toon_mat("BG_STONEC", "#474339", "#797364", "#aea891", steps=N, positions=SHADE_POS)
MORTAR = P.toon_mat("BG_MORTAR", "#302d28", "#4f4a42", "#767061", steps=N, positions=SHADE_POS)
BLOCKS = (STONE_A, STONE_B, STONE_C)
PAVE = P.toon_mat("BG_PAVE", "#504d46", "#837f6c", "#b8b499", steps=N, positions=SHADE_POS)
PINE = P.toon_mat("BG_PINE", "#132214", "#2b4829", "#517b48", steps=N, positions=SHADE_POS)
BARK = P.toon_mat("BG_BARK", "#241810", "#493424", "#725438", steps=N, positions=SHADE_POS)
LEAF = P.toon_mat("BG_LEAF", "#1c2f1d", "#3c5e32", "#679651", steps=N, positions=SHADE_POS)
MTN = P.toon_mat("BG_MTN", "#414f66", "#68789a", "#a3b3cd", steps=N, positions=SHADE_POS)
MTN_FAR = P.toon_mat("BG_MTNFAR", "#54637e", "#7d8cab", "#aebbd2", steps=N, positions=SHADE_POS)
SNOW = P.toon_mat("BG_SNOW", "#93a3b8", "#c6d3e2", "#f4f9ff", steps=N, positions=SHADE_POS)
PINE_FAR = P.toon_mat("BG_PINEFAR", "#1b2b1f", "#354c37", "#56744c", steps=N, positions=SHADE_POS)
HAZE = P.flat_mat("BG_HAZE", "#89aec2")
SKY_HI = P.flat_mat("BG_SKYHI", "#4a7cb4")
SKY_LO = P.flat_mat("BG_SKYLO", "#a3c6e0")
DARK = P.flat_mat("BG_DARK", "#20211c")

solid, flat = [], []       # `flat` gets no outline: ground, decals, sky, distance

# ---- sky panel, distant range, ground ----
# The sky panel is a 200-unit box standing 44 tall. Left casting, its shadow falls
# right across the battlefield and reads as a huge unexplained dark region, since
# nothing visible is there to throw it. Backdrop panels never cast.
for _n, _loc, _sz, _m in (("sky", (0, 13.0, 12.0), (200, 0.4, 44), SKY_HI),
                          ("skyband", (0, 12.6, 1.4), (200, 0.4, 5.0), SKY_LO)):
    _o = P.add_box(scn, _n, _loc, _sz, _m)
    _o.visible_shadow = False
    flat.append(_o)
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
    m.visible_shadow = False
    flat.append(m)
for x, y, r, h in ((-26, 11.4, 6.4, 6.2), (-13, 11.9, 5.6, 7.4), (-1, 11.1, 5.0, 5.2),
                   (9, 11.8, 6.2, 7.0), (20, 11.2, 5.4, 5.6), (30, 11.9, 6.6, 6.6)):
    m = P.add_cone(scn, "mtn", (x, y, 0), r, 0.4, h * 2, MTN, verts=7)
    m.scale = (1, MTN_FLAT, 1)
    m.visible_shadow = False
    flat.append(m)
    cap = P.add_cone(scn, "snow", (x, y - 0.25, h - 1.05), r * 0.21, 0.25, 2.1, SNOW, verts=7)
    cap.scale = (1, MTN_FLAT, 1)
    cap.visible_shadow = False
    flat.append(cap)
# The ground plane simply ends, and an ortho camera renders that as a clean cut
# across the frame. A haze strip plus a continuous distant treeline hides the cut.
_hz = P.add_box(scn, "haze", (0, GROUND_FAR + 0.5, 0.7), (200, 0.3, 2.6), HAZE)
_hz.visible_shadow = False
flat.append(_hz)
for i in range(78):
    x = -42.0 + i * 1.12 + 0.35 * (i % 3)
    s_ = 0.58 + 0.11 * (i % 4)
    for row, dy in ((0, 0.0), (1, 0.62)):
        t_ = P.add_cone(scn, "fartree",
                        (x + row * 0.55, GROUND_FAR - 0.15 + dy, 0.9 * s_),
                        1.05 * s_, 0.05, 2.6 * s_, PINE_FAR, verts=6)
        # This row spans the whole frame purely to mask the ground's cut edge.
        # Left casting, it lays one continuous shadow bar across the battlefield
        # that reads as coming from the wall, which only runs halfway.
        t_.visible_shadow = False
        flat.append(t_)


# Flatter than it needs to be for TEXTURE, because smooth shading extracts plenty
# of tonal variation from very little slope: crossing one ramp stop in the lit
# cluster takes about 2.3 degrees of tilt. The relief was cranked up when the
# ground was flat-shaded and every tone had to come from a visible facet.
AMP = 0.60

# Patches where the relief eases off. The plaza already produced one of these as a
# side effect of being flattened for the paving, and that break was the part of the
# ground that read best, so the effect is now placed deliberately.
CALM = ((-24.0, -3.0, 6.5), (-11.5, 3.5, 5.0), (3.0, -12.5, 6.5),
        (14.5, -1.5, 5.5), (23.0, -14.0, 6.0), (-6.5, -17.0, 5.0),
        (26.5, 4.5, 5.0), (-19.0, -15.0, 4.5))
PLAZA = (-16.8, -8.6)


def flatten(x, y):
    """Relief tapers to nothing where the wall and the plaza stand, so nothing
    has to be sunk into a slope."""
    k = min(1.0, max(0.0, (abs(x - WALL_X) - 2.4) / 3.0))
    d = math.hypot(x - PLAZA[0], y - PLAZA[1])
    k = min(k, min(1.0, max(0.0, (d - 4.6) / 3.0)))
    return k


# The battle line is already the busiest part of the frame: two formations, their
# contact shadows and the road all land here. Textured ground underneath competes
# with the thing the player is actually meant to be watching, so it is flattened
# hardest of all. Centre, then the two radii of the ellipse.
BATTLE = (14.0, -7.0, 12.5, 7.0)


def calm(x, y):
    """Ease the relief toward flat inside the CALM patches and the battle zone."""
    k = 1.0
    for cx, cy, r in CALM:
        d = math.hypot(x - cx, y - cy) / r
        k = min(k, max(0.10, min(1.0, d * d)))
    bx, by, brx, bry = BATTLE
    d = math.hypot((x - bx) / brx, (y - by) / bry)
    if d < 1.0:
        t = max(0.0, min(1.0, (d - 0.62) / 0.38))
        k = min(k, 0.05 + 0.95 * t * t)
    return k


def hgt(x, y):
    # Fractal noise, NOT a stack of sines. Separable sin(x)*cos(y) terms are a
    # regular lattice by construction, and however many octaves are added they
    # still line their peaks up in rows, which is what produced the diagonal
    # ribbons. Perlin has no preferred direction and no repeat.
    n = bnoise.fractal(Vector((x * 0.15, y * 0.15, 0.0)), 0.85, 2.0, 5)
    return AMP * flatten(x, y) * calm(x, y) * n


ROAD_PTS = []


def decal(name, x, y, rx_, ry_, mat, z=0.10):
    """Flat ground marking, riding the terrain. Casts no shadow: it is paint,
    not an object, and a floating disc would otherwise throw one."""
    ob = P.add_cyl(scn, name, (x, y, hgt(x, y) + z), 1.0, 0.06, mat,
                   verts=9, scale=(rx_, ry_, 1))
    ob.visible_shadow = False
    if name.startswith("road") or name == "plazapath":
        ROAD_PTS.append((x, y))
    flat.append(ob)
    return ob


flat.append(P.add_box(scn, "underground", (0, (GROUND_FAR - 34) / 2, -0.9),
                      (200, 34 + GROUND_FAR, 1.2), GRASS))
# Finer cell AND smooth normals. Flat-shaded quads render as solid blocks of
# one tone the size of the cell, which behind pixel-detailed characters reads
# as a coarser resolution than the rest of the art.
terrain = P.add_terrain(scn, "terrain", -40, 40, -26, GROUND_FAR, 0.45, hgt,
                        GRASS, smooth=True)
flat.append(terrain)

# ---- ground variation: churned dirt on the field, scrub on both sides ----
for cx, cy, n in ((6.0, -4.0, 5), (16.0, -9.0, 6), (24.0, -3.0, 4),
                  (11.0, -14.0, 5), (27.0, -13.0, 4)):
    for i in range(n):                     # clustered, so the field reads churned
        x = cx + ((i * 7) % 5 - 2) * 1.5
        y = cy + ((i * 5) % 5 - 2) * 1.1
        decal("churn", x, y, 1.5 + 0.7 * (i % 3), 0.95 + 0.4 * (i % 2), DIRT)
def clear_ground(x, y, pad=1.9):
    """Keep scatter off the paved plaza, the wall line and the roads."""
    if math.hypot(x - PLAZA[0], y - PLAZA[1]) < 4.9:
        return False
    if abs(x - WALL_X) < 2.2:
        return False
    return all(math.hypot(x - rx, y - ry) > pad for rx, ry in ROAD_PTS)


placed = 0
for i in range(90):
    x = -29.0 + ((i * 11) % 31) * 1.95
    y = -15.5 + ((i * 8) % 21) * 1.3 + 0.45 * ((i * 13) % 7 - 3) / 3.0
    x += 0.5 * ((i * 5) % 7 - 3) / 3.0
    if not clear_ground(x, y) or i % 3 == 0:
        continue
    r = 0.42 + 0.22 * (i % 3)
    solid.append(P.add_sphere(scn, "tuft", (x, y, hgt(x, y) + 0.03), r, GRASS2,
                              scale=(1.4, 1.0, 0.30), segs=7, rings=4))
    placed += 1
for i in range(44):                      # loose stones, small but they cast
    x = -30.0 + ((i * 17) % 37) * 1.7
    y = -16.0 + ((i * 5) % 19) * 1.45 + 0.6 * ((i * 11) % 5 - 2) / 2.0
    if not clear_ground(x, y, 1.4) or i % 2 == 0:
        continue
    r = 0.2 + 0.1 * (i % 3)
    solid.append(P.add_sphere(scn, "pebble", (x, y, hgt(x, y) + 0.02), r, STONE,
                              scale=(1.2, 0.95, 0.55), segs=6, rings=3))

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
solid.append(P.add_cyl(scn, "plaza", (-16.8, -8.6, 0.06), 4.2, 0.16, MORTAR, verts=18))
flat.extend(P.tile_top(scn, -21.0, -12.6, -12.8, -4.4, 0.14, 0.47, 0.42, BLOCKS,
                       clip=lambda x, y: math.hypot(x + 16.8, y + 8.6) < 4.05,
                       gap=SNAP_U, rise=0.09, name="cobble",
                       snap_u=SNAP_U, snap_v=SNAP_V))
solid.append(P.add_cyl(scn, "wellwall", (-16.8, -8.3, 0.55), 0.92, 1.05, MORTAR, verts=12))
for ring, (rr, zz) in enumerate(((1.0, 0.72), (1.0, 1.02))):
    for i in range(12):
        a_ = i * math.tau / 12 + ring * 0.26
        flat.append(P.add_box(scn, "wellstone",
                              (-16.8 + rr * math.sin(a_), -8.3 + rr * math.cos(a_), zz),
                              (0.52, 0.4, 0.3), BLOCKS[(i + ring) % 3], rot=(0, 0, -a_)))
flat.append(P.add_cyl(scn, "wellmouth", (-16.8, -8.3, 1.14), 0.62, 0.06, DARK, verts=12))

# ---- the wall: long run down the frame, plus the back wall along the town ----
WH, WT = 3.2, 1.15
GATE_Y0, GATE_Y1 = -4.6, -1.6
for y0, y1 in ((-22.0, GATE_Y0), (GATE_Y1, GROUND_FAR - 0.6)):
    solid.append(P.add_box(scn, "wall", (WALL_X, (y0 + y1) / 2, WH / 2),
                           (WT, y1 - y0, WH), MORTAR))
    flat.extend(P.tile_top(scn, WALL_X - WT / 2, WALL_X + WT / 2, y0, y1, WH,
                           0.37, 0.33, BLOCKS, gap=SNAP_U, rise=0.10,
                           snap_u=SNAP_U, snap_v=SNAP_V))
    for i in range(int((y1 - y0) / 1.3)):
        solid.append(P.add_box(scn, "crenel", (WALL_X, y0 + 0.65 + i * 1.3, WH + 0.32),
                               (WT * 0.92, 0.7, 0.64), BLOCKS[i % 3]))
BW_X0, BW_Y = -30.0, GROUND_FAR - 0.6
solid.append(P.add_box(scn, "backwall", ((BW_X0 + WALL_X) / 2, BW_Y, WH / 2),
                       (WALL_X - BW_X0, WT, WH), MORTAR))
flat.extend(P.tile_top(scn, BW_X0, WALL_X, BW_Y - WT / 2, BW_Y + WT / 2, WH,
                       0.37, 0.33, BLOCKS, gap=SNAP_U, rise=0.10,
                       snap_u=SNAP_U, snap_v=SNAP_V))
flat.extend(P.tile_face_y(scn, BW_X0, WALL_X, 0.15, WH - 0.1, BW_Y - WT / 2,
                          0.62, 0.44, BLOCKS))
for i in range(int((WALL_X - BW_X0) / 1.3)):
    solid.append(P.add_box(scn, "bcrenel", (BW_X0 + 0.65 + i * 1.3, BW_Y, WH + 0.32),
                           (0.7, WT * 0.92, 0.64), BLOCKS[(i * 2) % 3]))

# gatehouse: two drum-square towers with a lintel and a recessed timber gate
solid.append(P.add_box(scn, "corner", (WALL_X, BW_Y, 2.5), (2.5, 2.5, 5.0), MORTAR))
flat.extend(P.tile_top(scn, WALL_X - 1.25, WALL_X + 1.25, BW_Y - 1.25, BW_Y + 1.25, 5.0,
                       0.44, 0.40, BLOCKS, gap=SNAP_U, rise=0.10,
                       snap_u=SNAP_U, snap_v=SNAP_V))
flat.extend(P.tile_face_y(scn, WALL_X - 1.25, WALL_X + 1.25, 0.2, 4.9, BW_Y - 1.25,
                          0.6, 0.44, BLOCKS))
# Merlons belong on the CORNERS of a square tower, not at the edge midpoints.
for sx, sy in ((-0.8, -0.8), (0.8, -0.8), (-0.8, 0.8), (0.8, 0.8)):
    solid.append(P.add_box(scn, "ccrenel", (WALL_X + sx, BW_Y + sy, 5.3),
                           (0.85, 0.85, 0.6), BLOCKS[int(abs(sx * 3 + sy * 5)) % 3]))
for gy in (GATE_Y0, GATE_Y1):
    solid.append(P.add_box(scn, "gtower", (WALL_X, gy, 2.7), (2.9, 2.0, 5.4), MORTAR))
    flat.extend(P.tile_top(scn, WALL_X - 1.45, WALL_X + 1.45, gy - 1.0, gy + 1.0, 5.4,
                           0.44, 0.40, BLOCKS, gap=SNAP_U, rise=0.10,
                           snap_u=SNAP_U, snap_v=SNAP_V))
    flat.extend(P.tile_face_y(scn, WALL_X - 1.45, WALL_X + 1.45, 0.2, 5.3, gy - 1.0,
                              0.6, 0.44, BLOCKS))
    for sx in (-0.95, 0, 0.95):
        solid.append(P.add_box(scn, "gcrenel", (WALL_X + sx, gy, 5.72), (0.7, 2.1, 0.64),
                               BLOCKS[int((sx + 1) * 2) % 3]))
solid.append(P.add_box(scn, "lintel", (WALL_X, (GATE_Y0 + GATE_Y1) / 2, WH - 0.55),
                       (WT, GATE_Y1 - GATE_Y0, 2.1), STONE))
solid.append(P.add_box(scn, "gate", (WALL_X - 0.14, (GATE_Y0 + GATE_Y1) / 2, 0.95),
                       (WT * 0.5, 2.4, 1.9),
                       P.toon_mat("BG_GATEWOOD", "#2a1809", "#553618", "#8e6135", steps=N, positions=SHADE_POS)))

# ---- pine forest on the field side, breaking the far edge ----
for i in range(30):
    x = 5.0 + ((i * 17) % 37) * 0.72
    y = 5.4 + ((i * 5) % 13) * 0.34
    s = 0.62 + 0.10 * (i % 4)
    zt = hgt(x, y)
    solid.append(P.add_cyl(scn, "trunk", (x, y, zt + 0.34 * s), 0.16, 0.75 * s, BARK, verts=6))
    for zz, rr in ((1.15, 0.86), (2.05, 0.64), (2.85, 0.40)):
        solid.append(P.add_cone(scn, "pine", (x, y, zt + zz * s), rr * s, 0.04, 1.75 * s, PINE, verts=7))

# ---- broadleaf trees inside the town, clear of the plot band ----
for x, y, s in ((-27.5, 3.0, 1.0), (-26.4, -6.4, 0.9), (-9.0, -11.0, 0.95),
                (-23.0, -13.5, 0.85), (-5.5, 7.6, 0.9)):
    zt = hgt(x, y)
    # A sphere squashed in Z reads as a disc from a steep camera, which is why the
    # canopies looked drawn from straight overhead. Taller than wide shows the side.
    solid.append(P.add_cyl(scn, "ttrunk", (x, y, zt + 0.55 * s), 0.22, 1.15 * s, BARK, verts=6))
    solid.append(P.add_sphere(scn, "canopy", (x, y, zt + 2.05 * s), 1.1 * s, LEAF,
                              scale=(1.0, 0.82, 1.45), segs=10, rings=7))

# ---- field boulders ----
for x, y, s in ((8.0, -5.6, 0.62), (18.0, -11.5, 0.5), (25.0, -2.4, 0.7),
                (12.0, -15.0, 0.45), (5.0, -11.0, 0.4), (28.0, -8.0, 0.55)):
    solid.append(P.add_sphere(scn, "rock", (x, y, hgt(x, y) + s * 0.4), s, STONE,
                              scale=(1.15, 0.95, 0.6), segs=7, rings=4))

P.enable_hard_shadows(scn)
P.outline_all(scn, px, width_px=1.4, skip=tuple(o.name for o in flat))
P.render_to(scn, os.path.join(OUT, "out_backdrop.png"))
P.upscale_nearest(os.path.join(OUT, "out_backdrop.png"),
                  os.path.join(OUT, "out_backdrop_big.png"), 2)
print("backdrop %dx%d | px %.4f (2x sprite) | frame %.1f x %.1f | wall x %.2f = 46%%"
      % (RES_X, RES_Y, px, ORTHO, FRAME_H, WALL_X))
