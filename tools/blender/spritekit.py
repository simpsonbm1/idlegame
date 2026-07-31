"""Scaffolding shared by every character sprite, whatever family it belongs to.

`pixelrig.py` is the RENDERER: materials, primitives, outlines, cameras. This is
the layer above it that encodes the conventions a character sprite has to obey to
sit beside the others -- ground line, facing, outline weight, sun angle, and the
open/close pair every builder is bracketed by.

A family kit (`undead_kit.py`, and its siblings) imports this and adds only what
is specific to its faction: the palette, and the body parts that faction repeats.

Local frame, for every character: the figure faces -Y and up is +Z. The root turn
at the end is what points it at the camera -- heroes and townsfolk +30 degrees,
enemies -30, per `M15_ASSET_SPECS.md`.
"""

import bpy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P

FACE_LEFT = -30       # enemies and bosses
FACE_RIGHT = 30       # heroes and townsfolk
OUTLINE_PX = 1.75     # matches the knight, goblin and necromancer
SUN = (50, 0, -40)    # character-camera sun; azimuth is per-camera, see README
GROUND_FRAC = 0.10    # z=0 sits this far up from the bottom of every cell


def start(scn, res):
    """Every builder's opening: same rig, same sun, same scale, same ground line.

    **`target_z` is derived, never passed.** The three pilot figures all put world
    z=0 exactly 10% up from the bottom of the cell -- the knight at 96/1.50, the
    goblin and necromancer at 112/1.76 -- and that shared ground row is what lets
    a sprite drop onto the backdrop or a contact sheet without being fitted. Six
    figures whose builders each picked a plausible-looking target_z came out
    standing on six different lines, which is invisible in a single render and
    obvious the moment they line up. Picking it by hand is the bug.

    The CELL RESOLUTION stays the one thing a builder chooses, and it is chosen to
    fit the figure. Never touch the ortho scale (README, scale matching).
    """
    P.ensure_rig(scn)
    P.setup_render(scn)
    P.clear_scene(scn)
    frame = P.SPRITE_PX * res
    P.sprite_cam(scn, res=res, target_z=frame * (0.5 - GROUND_FRAC))
    scn.collection.objects["KeySun"].rotation_euler = tuple(math.radians(a) for a in SUN)
    return P.pixel_size(scn)


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACE_LEFT):
    """Every builder's close: parent under one root, outline, render, upscale.

    `detail` and `noline` are excluded from the outline pass. The difference is
    only intent -- detail is small trim an outline would swallow, noline is
    anything emissive, and an outline around a glow puts it out -- and both end
    up in the same skip list.

    Sub-assembly parts live under their OWN root and so are not in these lists,
    which is the rule that keeps a sword's angle from being silently discarded
    (README). A glowing part inside a staff therefore has to be named in
    `skip_extra`.
    """
    root = P.make_root(scn, key + "_root", rot=(0, 0, facing))
    P.parent_all(root, list(figure) + list(detail) + list(noline) + list(roots))
    skip = tuple(o.name for o in list(detail) + list(noline)) + tuple(skip_extra)
    P.outline_all(scn, px, width_px=OUTLINE_PX, skip=skip)
    out = P.out_dir()
    small = os.path.join(out, "out_%s.png" % key)
    P.render_to(scn, small)
    P.upscale_nearest(small, os.path.join(out, "out_%s_big.png" % key), 8, bg="#ff00ff")
    print("%s done: %d figure parts" % (key, len(figure)))
    return small


# --------------------------------------------------------------------------
# parts that are not specific to any one faction
# --------------------------------------------------------------------------

def aimed_cyl(scn, name, a, b, radius, mat, verts=6):
    """A cylinder spanning two points. Rotation is DERIVED, never eyeballed -- a
    limb segment that misses its joint by a little reads as a broken limb."""
    from mathutils import Vector
    va, vb = Vector(a), Vector(b)
    d = vb - va
    ob = P.add_cyl(scn, name, tuple((va + vb) * 0.5), radius, d.length, mat, verts=verts)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def tatters(scn, loc, width, mat, count=5, drop=0.34, seed=0):
    """Ragged strips hanging off a hem.

    Uneven lengths are the whole point: a level hem reads as tailored cloth.
    Lengths come off an index multiplier COPRIME with the count, because a
    multiplier sharing a factor collapses to a handful of repeated values --
    README records `(i*7) % 21` putting every grass tuft on one of three rows.
    """
    x, y, z = loc
    out = []
    for i in range(count):
        t = (i + 0.5) / count - 0.5
        d = drop * (0.55 + 0.45 * (((i * 5 + seed) % 7) / 6.0))
        out.append(P.add_box(scn, "tatter", (x + t * width, y, z - d * 0.5),
                             (width / count * 0.82, 0.10, d), mat))
    return out


def flame(scn, loc, hot, cool, scale=1.0):
    """A rising flame as three shrinking blobs, hot at the base.

    Three blobs at the SAME height read as a symbol rather than as fire, which is
    the mistake the necromancer's first pass made; they have to climb AND shrink.
    Return these as no-outline parts.
    """
    x, y, z = loc
    out = []
    for i, (dz, r, m) in enumerate(((0.00, 0.115, hot), (0.21, 0.085, hot),
                                    (0.39, 0.055, cool))):
        out.append(P.add_sphere(scn, "flame", (x + 0.02 * i, y, z + dz * scale),
                                r * scale, m, segs=8, rings=5))
    return out


def limb(scn, shoulder, hand, mat, upper_r=0.075, fore_r=0.065, joint_mat=None):
    """Two segments and a hand, aimed shoulder -> hand, with a bend at the elbow.

    The elbow is pushed toward the camera and up, which is what stops the two
    segments reading as one straight tube.
    """
    joint_mat = joint_mat or mat
    sx, sy, sz = shoulder
    hx, hy, hz = hand
    mid = ((sx + hx) * 0.5, (sy + hy) * 0.5 - 0.10, (sz + hz) * 0.5 + 0.10)
    return [P.add_sphere(scn, "shoulderball", shoulder, upper_r * 1.5, joint_mat),
            aimed_cyl(scn, "upperarm", shoulder, mid, upper_r, mat),
            P.add_sphere(scn, "elbow", mid, fore_r * 1.45, joint_mat),
            aimed_cyl(scn, "forearm", mid, hand, fore_r, mat),
            P.add_sphere(scn, "hand", hand, fore_r * 1.7, joint_mat)]
