"""Attack animation on top of the finished models.

An animation here is a TABLE OF ANGLES, not a set of drawn frames. Every frame
goes through the same rig as the static sprite, so palette, outline weight and
pixel grid cannot drift between frames, and a model change means a re-render
rather than a re-animation.

**Every joint is DERIVED from the model, never typed.** That is the whole point of
this module. The first version of `build_attack.py` hard-coded the knight's
shoulder at one coordinate and the goblin's arm bone lengths at two numbers, both
read off the builder by hand. Nothing errors when a model's proportions change
underneath those: the arm simply detaches, silently, and only a human looking at
the sheet would catch it. Deriving them means an animation survives any change to
a figure that does not rename or remove a limb.

That matters more now than it did, because `spritekit.finish()` scales every
figure to its role height, so a builder's own coordinates are no longer the
figure's real ones. A typed shoulder position is wrong by whatever the role scale
happens to be.

## The two techniques

**One hand on the weapon is a pivot problem.** Put one empty at the shoulder,
hand it the arm parts and the weapon root, and turn it once per frame.

**Two hands is an IK problem.** Turning each arm about its own shoulder keeps both
shoulders attached but does not keep the hands a fixed distance apart: the gap
between the shoulders is fixed while each hand's offset from its shoulder
rotates, so the weapon floats free of the fists. Drive the WEAPON instead and
solve each arm to reach its grip point.

## A frame needs two angles, not one

`swing` turns about **Y**, which is the arc the camera sees, measured from
straight up: 0 overhead, 90 level and forward, 180 straight down.

`lift` turns about **X**, carrying the arm forward in depth toward the direction
the figure faces. Negative is forward.

Swing alone looks right in a wireframe and is wrong on screen, because a figure's
weapon hand is on the opposite side from the direction it attacks, so a flat arc
drags the arm through the torso. Any frame with a real swing needs a real lift,
roughly a third of it.
"""

import bpy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S


# --------------------------------------------------------------------------
# deriving the rig from the model
# --------------------------------------------------------------------------

def world_of(ob):
    """World transform, composed by hand up the parent chain.

    Not `ob.matrix_world`: that is evaluated by the ACTIVE scene's depsgraph, and
    in background Blender the active scene is the startup file's, not the one the
    builders work in. See `spritekit._world_matrix`.
    """
    return S._world_matrix(ob)


def centre_of(ob):
    """World-space centre of an object's bounding box."""
    from mathutils import Vector
    m = world_of(ob)
    cs = [m @ Vector(c) for c in ob.bound_box]
    return sum(cs, Vector((0, 0, 0))) / len(cs)


def top_joint(scn, names):
    """The shoulder, derived: the centre of whichever named part sits highest.

    A shoulder ball or a pauldron is always the topmost piece of an arm, so this
    finds the joint without anyone typing a coordinate. A pivot MUST sit on the
    joint the limb actually turns about -- anywhere else and the limb translates
    as well as rotating, which reads unmistakably as the arm coming away from the
    shoulder.
    """
    parts = P.find(scn, *names)
    if not parts:
        raise KeyError("no parts found for %s" % (names,))
    return centre_of(max(parts, key=lambda o: centre_of(o).z))


def segment_length(scn, name):
    """A limb segment's real length, after the figure's role scaling.

    `dimensions` is the world-space bounding box, so this already includes
    whatever `spritekit.finish()` scaled the figure by. Reading the depth out of
    the builder source instead is what went stale.
    """
    parts = P.find(scn, name)
    if not parts:
        raise KeyError("no part named %s" % name)
    return max(parts[0].dimensions)


def figure_root(scn, key):
    """The root `spritekit.finish()` parented everything to."""
    found = P.find(scn, key + "_root")
    if not found:
        raise KeyError("no root for %s" % key)
    return found[0]


# --------------------------------------------------------------------------
# the camera
# --------------------------------------------------------------------------

def anim_cam(scn, res):
    """Same derived ground line as a static sprite, in a bigger cell.

    **The cell grows; the ground line does not move.** An animated frame needs
    headroom a portrait frame does not, because a raised weapon leaves the static
    cell. Grow the RESOLUTION, never the ortho scale, or the figure renders at a
    different size than its own idle sprite.

    The original attack sheets set this by hand to 2.11 where the derived value
    for a 128 cell is 2.00, which put every attack frame about three pixels off
    its own idle sprite.
    """
    frame = P.SPRITE_PX * res
    P.sprite_cam(scn, res=res, target_z=frame * (0.5 - S.GROUND_FRAC))
    return P.pixel_size(scn)


# --------------------------------------------------------------------------
# technique one: a pivot, for a one-handed weapon
# --------------------------------------------------------------------------

def pivot_arm(scn, root, arm_names, weapon_root_name=None):
    """One empty at the derived shoulder, holding the arm and the weapon."""
    pivot = P.make_root(scn, "atk_pivot", loc=tuple(top_joint(scn, arm_names)))
    pivot.parent = root
    pivot.matrix_parent_inverse = world_of(root).inverted()
    names = list(arm_names)
    if weapon_root_name:
        names.append(weapon_root_name)
    P.reparent_keep(pivot, P.find(scn, *names))
    return pivot


def swing_sheet(scn, key, root, pivots, frames, res=128, out_name=None):
    """Render one frame per (lift, swing, lunge) triple as a horizontal sheet."""
    base = tuple(root.location)
    px = anim_cam(scn, res)

    def make(f):
        lift, swing, lunge = f

        def pose():
            for p in pivots:
                p.rotation_euler = (math.radians(lift), math.radians(swing), 0)
            root.location = (base[0], base[1] + lunge, base[2])
        return pose

    out = P.out_dir()
    name = out_name or ("atk_" + key)
    path = P.render_strip(scn, [make(f) for f in frames], os.path.join(out, name + ".png"))
    P.upscale_nearest(path, os.path.join(out, name + "_big.png"), 4, bg="#2a2320")
    print("%s -> %d frames (pivot)" % (name, len(frames)))
    return path


# --------------------------------------------------------------------------
# technique two: inverse kinematics, for a two-handed weapon
# --------------------------------------------------------------------------

def twohand_sheet(scn, key, root, weapon_name, arms, frames, res=128,
                  mid=None, stretch=0.22, out_name=None):
    """Drive the weapon; solve each arm to reach its grip.

    `arms` is a list of dicts with `shoulder` (part names to derive the joint
    from), `upper`, `fore`, `hand` (part names) and `pole` (which way the elbow
    breaks). Bone lengths are measured off the model.

    Grip points are captured from the REST POSE, so frame 0 reproduces the static
    sprite exactly and a change to where the hands sit needs no edit here.

    Swing a two-handed weapon about a point BELOW the shoulder line. Pivoting on
    the shoulders themselves lifts the grip to head height at full raise and
    folds both forearms across the face.
    """
    from mathutils import Matrix, Euler, Vector
    weapon = P.find(scn, weapon_name)[0]
    solved = []
    for a in arms:
        S_pos = top_joint(scn, a["shoulder"])
        solved.append({
            "S": Vector(S_pos),
            "a": segment_length(scn, a["upper"]),
            "b": segment_length(scn, a["fore"]),
            "pole": Vector(a["pole"]),
            "up": P.find(scn, a["upper"])[0],
            "fo": P.find(scn, a["fore"])[0],
            "fi": P.find(scn, a["hand"])[0],
        })

    rest = weapon.matrix_basis.copy()
    for a in solved:
        a["grip"] = rest.inverted() @ a["fi"].location.copy()

    if mid is None:
        # below the shoulder line, midway between the two shoulders
        mids = sum((a["S"] for a in solved), Vector((0, 0, 0))) / len(solved)
        mid = Vector((0.0, mids.y - 0.16, mids.z - 0.38))
    else:
        mid = Vector(mid)

    base = tuple(root.location)
    px = anim_cam(scn, res)

    def make(f):
        lift, swing, lunge = f

        def pose():
            R = Euler((math.radians(lift), math.radians(swing), 0), 'XYZ').to_matrix().to_4x4()
            weapon.matrix_basis = (Matrix.Translation(mid) @ R
                                   @ Matrix.Translation(-mid) @ rest)
            for a in solved:
                target = weapon.matrix_basis @ a["grip"]
                elbow, hand, la, lb = P.two_bone_ik(a["S"], target, a["a"], a["b"],
                                                    a["pole"], stretch=stretch)
                P.aim_segment(a["up"], a["S"], elbow, a["a"])
                P.aim_segment(a["fo"], elbow, hand, a["b"])
                a["fi"].location = hand
            root.location = (base[0], base[1] + lunge, base[2])
        return pose

    out = P.out_dir()
    name = out_name or ("atk_" + key)
    path = P.render_strip(scn, [make(f) for f in frames], os.path.join(out, name + ".png"))
    P.upscale_nearest(path, os.path.join(out, name + "_big.png"), 4, bg="#2a2320")
    print("%s -> %d frames (IK)" % (name, len(frames)))
    return path


# --------------------------------------------------------------------------
# the shared attack shapes
# --------------------------------------------------------------------------
#
# Most of the roster reuses one of these rather than getting its own table. Each
# is eight frames of (lift, swing, lunge), starting and ending at rest.
#
# An attack whose end pose resembles its rest pose reads as nothing happening,
# which is what the goblin's smash did until frame 1 gained a backward dip as
# anticipation. Every shape here has one.

OVERHAND = [(0, 0, 0), (-26, -40, 0.04), (-38, -86, 0.09), (-32, -66, 0.05),
            (-42, 28, -0.22), (-26, 14, -0.16), (-11, 5, -0.06), (0, 0, 0)]

SMASH = [(0, 0, 0), (-16, -20, 0.06), (-40, 92, 0.10), (-36, 60, 0.06),
         (-42, -52, -0.26), (-30, -34, -0.20), (-13, -14, -0.08), (0, 0, 0)]

# a short flat cut, for daggers and short blades: less wind-up, more lunge
SLASH = [(0, 0, 0), (-14, -26, 0.05), (-26, -54, 0.08), (-34, 10, -0.24),
         (-30, 44, -0.30), (-20, 26, -0.18), (-9, 10, -0.07), (0, 0, 0)]

# a two-handed horizontal sweep, for polearms and great weapons
SWEEP = [(0, 0, 0), (-18, 34, 0.06), (-34, 74, 0.10), (-40, 20, -0.18),
         (-44, -40, -0.28), (-30, -26, -0.19), (-13, -10, -0.08), (0, 0, 0)]

# a caster's push: almost no arc, the arm thrusts forward and holds
CAST = [(0, 0, 0), (-10, -18, 0.03), (-20, -32, 0.05), (-46, -6, -0.16),
        (-52, 8, -0.22), (-40, 6, -0.14), (-18, 2, -0.06), (0, 0, 0)]

# a bow draw and release: the arm pulls back, then snaps forward
LOOSE = [(0, 0, 0), (8, 14, -0.02), (14, 26, -0.04), (16, 30, -0.05),
         (2, -10, 0.06), (-6, -18, 0.04), (-3, -8, 0.02), (0, 0, 0)]
