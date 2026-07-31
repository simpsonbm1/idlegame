"""Building parts, M15_ASSET_SPECS.md entries 47-55.

Buildings use the NEAR-ISOMETRIC camera, not the character camera: a steep
three-quarter down-angle so part of the roof reads, matching the high camera of
the vista they stand on. The angle is the cottage pilot's and is locked here so
every building shares it.

**Buildings render at the character pixel density**, `pixelrig.SPRITE_PX`, and not
at the cottage pilot's ad-hoc `6.1 / 96`. That pilot was built before the scale
discipline existed and its pixels came out 1.6 times larger than a character's.
Buildings and characters are both sprites the game composites over the backdrop,
and two composited sprite layers at different densities read as two different
resolutions -- the same artefact the README records for flat-shaded terrain. The
backdrop itself stays at 2x, because it is one background image rather than a
layer of sprites.

Height works the way a character's role does: a builder declares a `scale`
against `BUILDING_HEIGHT` and `finish()` measures the assembled model and hits it
exactly. The spec asks that building silhouettes read at roughly twice a
character's height, so the base is 5.6 world units against a normal figure's
2.95.

Screen orientation at this azimuth: the -Y wall lands on screen LEFT and the +X
wall on screen RIGHT. Doors go left, windows right.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S

CAM_RX = 59          # elevation; part of the roof has to read
CAM_RZ = 38          # azimuth, which decides which walls face the screen
SUN = (46, 0, -39)   # biased toward the camera so BOTH visible faces stay lit
OUTLINE_PX = 1.6     # the cottage pilot's weight, kept
GROUND_FRAC = 0.10   # the base sits this far up the cell, as characters do

BUILDING_HEIGHT = 5.6   # about 1.9x a normal character, per the spec

SCALE = {
    "cottage": 1.00, "smithy": 1.05, "apothecary": 1.00, "workshop": 0.98,
    "tavern": 1.20, "library": 1.30, "keep": 1.42,
    "tower": 1.62, "cathedral": 1.85,
}


def height_for(kind):
    return BUILDING_HEIGHT * SCALE.get(kind, 1.0)


def palette():
    """One palette for the whole street. Buildings that share a town have to
    share their materials or the row reads as a collection of unrelated props."""
    return {
        "plaster": P.toon_mat("PLASTER", "#8e8474", "#b9ae9c", "#dcd3c4"),
        "timber":  P.toon_mat("TIMBER", "#472d18", "#6b4526", "#8f6539"),
        "stone":   P.toon_mat("STONE", "#55554f", "#77776f", "#9c9c94"),
        "darkstone": P.toon_mat("DARKSTONE", "#3b3b38", "#575751", "#767670"),
        "thatch":  P.toon_mat("THATCH", "#a8863c", "#d4b563", "#ecd591"),
        "shingle": P.toon_mat("SHINGLE", "#4a3b30", "#6b5747", "#8d7761"),
        "slate":   P.toon_mat("SLATE", "#39414d", "#535d6c", "#76818f"),
        "mossroof": P.toon_mat("MOSSROOF", "#3d5236", "#587348", "#7a955f"),
        "bluetile": P.toon_mat("BLUETILE", "#23324f", "#374c70", "#526c96"),
        "door":    P.toon_mat("DOORWOOD", "#3a2413", "#5a3a1f", "#7a5230"),
        "iron":    P.toon_mat("BIRONWORK", "#33322e", "#4e4c46", "#6e6b63"),
        "gold":    P.toon_mat("BLDGGOLD", "#7a5c15", "#b8912c", "#e6c65c"),
        "cloth":   P.toon_mat("BLDGCLOTH", "#5e2320", "#8c3a2e", "#b45f4a"),
        "glow":    P.flat_mat("WINDOWGLOW", "#ffcf5c"),
        "forge":   P.flat_mat("FORGEGLOW", "#ff8a2b"),
        "arcane":  P.flat_mat("ARCANEGLOW", "#7fd4ff"),
        "green":   P.flat_mat("APOTHGLOW", "#8cff7a"),
        "dark":    P.flat_mat("BLDGDARK", "#14110d"),
    }


def start(scn, res):
    """Open a building. Same camera, same sun, same density, every time."""
    P.ensure_rig(scn)
    P.setup_render(scn, res=res)
    P.clear_scene(scn)
    scn.render.resolution_x = res
    scn.render.resolution_y = res
    frame = P.SPRITE_PX * res
    # A tilted camera maps a world-z offset onto the screen by sin(elevation), so
    # putting the base 10% up the cell takes that factor out. Passing the
    # character formula unchanged would seat every building too low.
    target_z = frame * (0.5 - GROUND_FRAC) / math.sin(math.radians(CAM_RX))
    P.place_cam(scn, target=(0, 0, target_z), rx_deg=CAM_RX, rz_deg=CAM_RZ,
                dist=40, ortho=frame)
    scn.collection.objects["KeySun"].rotation_euler = tuple(math.radians(a) for a in SUN)
    return P.pixel_size(scn)


def walls(scn, M, w, d, h, base=0.0, mat=None, plinth=0.0, plinth_mat=None):
    """A rectangular storey, optionally on a stone plinth. `w` and `d` are HALF
    extents, which is how every other measurement in this rig works."""
    mat = mat or M["plaster"]
    out = []
    if plinth:
        out.append(P.add_box(scn, "plinth", (0, 0, base + plinth / 2),
                             (w * 2.10, d * 2.10, plinth), plinth_mat or M["stone"]))
    out.append(P.add_box(scn, "wall", (0, 0, base + plinth + (h - plinth) / 2),
                         (w * 2, d * 2, h - plinth), mat))
    return out


def framing(scn, M, w, d, z0, z1, rails=(), mat=None):
    """Corner posts, mid posts and horizontal rails.

    Timber framing is what stops a plastered box reading as a poured slab, for
    the same reason `tile_top` exists for masonry: one box is one normal and
    therefore one tone, and the structure has to be built rather than coloured.
    """
    mat = mat or M["timber"]
    h = z1 - z0
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append(P.add_box(scn, "post", (sx * w, sy * d, z0 + h / 2),
                                 (0.21, 0.21, h), mat))
        out.append(P.add_box(scn, "midpostX", (sx * w, 0, z0 + h / 2), (0.18, 0.18, h), mat))
        out.append(P.add_box(scn, "midpostY", (0, sx * d, z0 + h / 2), (0.18, 0.18, h), mat))
    for z, t in rails:
        out.append(P.add_box(scn, "rail", (0, 0, z), (w * 2.04, d * 2.04, t), mat))
    return out


def gable_roof(scn, M, w, d, z, ridge, mat, overhang=0.30, eave=0.28, depth_pad=0.48):
    """A pitched roof whose ridge runs along Y, so both slopes show on screen."""
    pts = [(-w - overhang, z), (0, z + ridge), (w + overhang, z),
           (w + overhang, z - eave), (0, z + ridge - eave), (-w - overhang, z - eave)]
    return [P.add_prism(scn, "roof", pts, depth=d * 2 + depth_pad, mat=mat)]


def gable_ends(scn, M, w, d, z, ridge, mat, inset=0.26):
    return [P.add_prism(scn, "gable", [(-w, z), (0, z + ridge - inset), (w, z)],
                        depth=0.16, mat=mat, loc=(0, sy * d, 0))
            for sy in (-1, 1)]


def hip_roof(scn, M, w, d, z, ridge, mat):
    """A four-sided roof, built as a squashed pyramid. Reads flatter and more
    civic than a gable, which is why the keep and the cathedral use it."""
    return [P.add_cone(scn, "hiproof", (0, 0, z + ridge / 2), max(w, d) * 1.42, 0.0,
                       ridge, mat, verts=4, rot=(0, 0, math.radians(45)))]


def door(scn, M, x, y_wall, z0, wide=0.62, tall=1.52, arch=False):
    """A door on the screen-LEFT wall, which at this azimuth is the -Y face."""
    out = [P.add_box(scn, "doorframe", (x, y_wall - 0.02, z0 + (tall + 0.12) / 2),
                     (wide + 0.24, 0.14, tall + 0.12), M["timber"]),
           P.add_box(scn, "door", (x, y_wall - 0.08, z0 + tall / 2),
                     (wide, 0.10, tall), M["door"])]
    if arch:
        out.append(P.add_cyl(scn, "doorarch", (x, y_wall - 0.05, z0 + tall),
                             (wide + 0.24) / 2, 0.14, M["timber"], verts=10,
                             rot=(math.radians(90), 0, 0)))
    return out


def window(scn, M, side, a, wall, z, w=0.50, h=0.46, glow=None, frame_mat=None):
    """A window on a named wall.

    `side` is "left" for the -Y face or "right" for the +X face, `a` is the
    position along that wall and `wall` is the wall's own coordinate. Returns
    (frame, pane); the pane belongs in the no-outline list, because an outline
    around a lit window closes it up.
    """
    glow = glow or M["glow"]
    fm = frame_mat or M["timber"]
    if side == "left":
        frame = P.add_box(scn, "winframe", (a, wall - 0.02, z), (w + 0.22, 0.14, h + 0.20), fm)
        pane = P.add_box(scn, "winpane", (a, wall - 0.08, z), (w, 0.10, h), glow)
    else:
        frame = P.add_box(scn, "winframe", (wall + 0.02, a, z), (0.14, w + 0.22, h + 0.20), fm)
        pane = P.add_box(scn, "winpane", (wall + 0.08, a, z), (0.10, w, h), glow)
    return frame, pane


def chimney(scn, M, x, y, z, h=1.6, w=0.36, mat=None):
    return [P.add_box(scn, "chimney", (x, y, z + h / 2), (w, w, h), mat or M["stone"]),
            P.add_box(scn, "chimneycap", (x, y, z + h + 0.06), (w * 1.24, w * 1.24, 0.14),
                      mat or M["stone"])]


def hanging_sign(scn, M, x, y, z, face_mat, arm=0.62):
    """A bracket and a board. The board is what says what the building is, and at
    this size it is one flat colour with a single mark on it."""
    return [P.add_box(scn, "signarm", (x, y - arm / 2, z + 0.34), (0.09, arm, 0.09), M["iron"]),
            P.add_box(scn, "signchain", (x, y - arm * 0.82, z + 0.16), (0.05, 0.05, 0.30), M["iron"]),
            P.add_box(scn, "signboard", (x, y - arm * 0.82, z - 0.14), (0.44, 0.09, 0.44), face_mat)]


def finish(scn, px, key, parts, noline=(), detail=(), kind=None):
    """Close a building: parent under one root, size it, outline, render.

    Buildings do not turn to face the camera the way characters do -- the camera
    azimuth already presents them at three-quarters -- so the root carries only
    the scale.
    """
    root = P.make_root(scn, key + "_root")
    P.parent_all(root, list(parts) + list(noline) + list(detail))
    k = 1.0
    if kind:
        h = S.measure_height(parts)
        if h > 0.01:
            k = height_for(kind) / h
            root.scale = (k, k, k)
    skip = tuple(o.name for o in list(noline) + list(detail))
    P.outline_all(scn, px, width_px=OUTLINE_PX / k, skip=skip)
    out = P.out_dir()
    small = os.path.join(out, "out_%s.png" % key)
    P.render_to(scn, small)
    P.upscale_nearest(small, os.path.join(out, "out_%s_big.png" % key), 8, bg="#ff00ff")
    print("%s done: %d parts, scaled %.3f to %.2f units"
          % (key, len(parts), k, height_for(kind) if kind else 0.0))
    return small
