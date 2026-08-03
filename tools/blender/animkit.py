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


def top_of(ob):
    """The world point at the top of a part, on its own centre line."""
    from mathutils import Vector
    m = world_of(ob)
    cs = [m @ Vector(c) for c in ob.bound_box]
    c = sum(cs, Vector((0, 0, 0))) / len(cs)
    return Vector((c.x, c.y, max(p.z for p in cs)))


def top_joint(scn, names):
    """The shoulder, derived: the centre of whichever named part sits highest.

    A shoulder ball or a pauldron is always the topmost piece of an arm, so this
    finds the joint without anyone typing a coordinate. A pivot MUST sit on the
    joint the limb actually turns about -- anywhere else and the limb translates
    as well as rotating, which reads unmistakably as the arm coming away from the
    shoulder.

    **A name written `^part` means the TOP of that part rather than its centre**,
    which is how a dual-wielder gets one pivot per arm. Both his shoulder balls
    are usually built in one loop and so share a single name, and a name is all
    this has to choose by: `("shoulder",)` on both arms puts BOTH pivots on
    whichever ball happened to sit highest, and the far arm then swings about the
    other shoulder, a foot away. The assassin's knives went over his head that
    way. `^upperL` needs no name to be unique, because an upper arm's top IS its
    own shoulder joint.
    """
    tops = [n[1:] for n in names if n.startswith("^")]
    plain = [n for n in names if not n.startswith("^")]
    if tops:
        parts = P.find(scn, *tops)
        if not parts:
            raise KeyError("no parts found for %s" % (tops,))
        return top_of(max(parts, key=lambda o: top_of(o).z))
    parts = P.find(scn, *plain)
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


def facing_sign(root):
    """+1 for a figure facing screen-right, -1 for one facing screen-left.

    Read off the figure's own root, because that is where `spritekit.finish()`
    put the facing: heroes and townsfolk at +30 degrees about Z, every enemy
    family at -30.

    A swing turns the pivot about WORLD Y, which points one fixed way, so the
    same table of angles drives a right-facing figure forward and a left-facing
    one backward. Multiplying swing by this makes a shape mean the same thing on
    both, which is what `attack_shapes` documents: positive is forward and down,
    the way the figure faces.
    """
    return -1.0 if root.rotation_euler.z < 0.0 else 1.0


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

def joint_between(scn, shoulder_groups):
    """The pivot point: one shoulder, or the midpoint between two.

    A one-handed swing turns about the weapon shoulder. A TWO-handed swing turns
    about the point between both shoulders, which reads as the torso twisting
    rather than as one arm dragging the other.
    """
    from mathutils import Vector
    pts = [top_joint(scn, g) for g in shoulder_groups]
    return sum(pts, Vector((0, 0, 0))) / len(pts)


def pivot_arm(scn, root, shoulder_groups, part_names, weapon_root_name=None,
              name="atk_pivot"):
    """One empty at the derived joint, holding the arm parts AND the weapon.

    **The weapon goes in the pivot with the arms, which is what makes this safe
    for a two-handed grip.** The failure the README records -- hands drifting off
    a two-handed weapon -- happens when the weapon is driven separately from the
    arms, so their offsets rotate independently. Rotating arms and weapon
    together as one rigid body cannot come apart at all, because nothing moves
    relative to anything else.

    Inverse kinematics is still the better answer when the weapon must follow a
    path of its own rather than the arms' arc, which is why `twohand_sheet` and
    the goblin brute stay as the worked example. For a plain swing this is
    simpler, has no bone lengths to get wrong, and works on figures whose limb
    parts share a name.

    **`name` must be unique per pivot.** `P.find` matches on the name before
    Blender's `.001` suffix, so two pivots called `atk_pivot` are one name to it
    and a chained pivot would collect its own sibling.
    """
    pivot = P.make_root(scn, name, loc=tuple(joint_between(scn, shoulder_groups)))
    pivot.parent = root
    pivot.matrix_parent_inverse = world_of(root).inverted()
    names = list(part_names)
    if weapon_root_name:
        names.append(weapon_root_name)
    found = P.find(scn, *names)
    if not found:
        raise KeyError("no parts to animate for %s" % (names,))
    P.reparent_keep(pivot, found)
    return pivot


def chain_pivot(child, parent):
    """Hang one pivot off another, so the child's joint rides the parent's arc.

    **This is what lets a weapon turn about the FIST while the arm turns about
    the shoulder.** A weapon whose mass sits at the shoulder cannot be swung from
    the shoulder at all: the paladin's hammer head is at world z 2.14 and so is
    his shoulder, so rotating his arm moved the head 0.58 units across a whole
    chop and read as a caster's gesture. Rotating the hammer about the fist gives
    it the haft's length as a lever, and chaining that pivot under the arm's keeps
    the grip in the hand.

    The child must be built FIRST, so it has already taken the weapon, and the
    parent then takes the arm. Order the other way round and the arm pivot
    collects the weapon too.
    """
    P.reparent_keep(parent, [child])
    return child


def swing_sheet(scn, key, root, pivots, frames, res=128, out_name=None):
    """Render one frame per (lift, swing, lunge) triple as a horizontal sheet.

    `pivots` is a list of pivot empties, or of `(pivot, frames)` pairs when a
    pivot needs a table of its own. **Per-pivot tables are what an archer needs:**
    a draw is the string hand travelling back while the bow hand holds still, and
    one shared table can only rock the whole assembly.

    **`lunge` is a STEP TOWARD THE ENEMY, in world x.** It used to move the figure
    in y, which is the axis the camera looks down, so at this camera's 3-degree
    tilt a 0.3 lunge produced under half a pixel on screen and every attack read
    as happening on the spot. Multiplying by the facing sign sends heroes right
    and enemies left, so one table steps both toward the fight.
    """
    base = tuple(root.location)
    sign = facing_sign(root)
    tracks = [p if isinstance(p, (tuple, list)) else (p, None) for p in pivots]
    px = anim_cam(scn, res)

    def make(i):
        def pose():
            for pivot, own in tracks:
                lift, swing, _ = (own or frames)[i]
                pivot.rotation_euler = (math.radians(lift),
                                        math.radians(swing * sign), 0)
            # The body follows the DEFAULT table, so a per-pivot override moves a
            # limb without teleporting the man it belongs to.
            root.location = (base[0] + frames[i][2] * sign, base[1], base[2])
        return pose

    out = P.out_dir()
    name = out_name or ("atk_" + key)
    path = P.render_strip(scn, [make(i) for i in range(len(frames))],
                          os.path.join(out, name + ".png"))
    P.upscale_nearest(path, os.path.join(out, name + "_big.png"), 4, bg="#2a2320")
    print("%s -> %d frames (pivot)" % (name, len(frames)))
    return path


# --------------------------------------------------------------------------
# technique two: inverse kinematics, for a two-handed weapon
# --------------------------------------------------------------------------

def _parent_world(ob):
    """The matrix taking a part's own space to world.

    Blender's rule is `world = parent.world @ matrix_parent_inverse @ basis`, so
    this is everything in that chain EXCEPT the part's own basis. Writing a
    computed world matrix back onto a part means composing with its inverse.
    """
    from mathutils import Matrix
    if ob.parent is None:
        return Matrix.Identity(4)
    return P.world_matrix(ob.parent) @ ob.matrix_parent_inverse


def ik_poses(scn, root, weapon_name, arms, frames, mid=None, stretch=0.22):
    """One callable per frame, each posing the whole figure. No rendering.

    Split out of `twohand_sheet` so `probe_rig.py` can MEASURE an
    inverse-kinematics attack instead of only rendering it. The probe is where
    every diagnosis in three rejected animation rounds came from, and a second
    copy of this maths would drift from this one silently: nothing errors when a
    probe poses a figure differently from the renderer, and the numbers would
    simply describe an attack nobody ships.

    See `twohand_sheet` for what the frame columns mean.
    """
    from mathutils import Matrix, Euler, Vector
    weapon = P.find(scn, weapon_name)[0]

    # ---- ONE SPACE, AND EVERY QUANTITY CONVERTED INTO IT --------------------
    # **A part's `location` is NOT where it is.** It is an offset inside its
    # parent, and on these figures the parents are neither at the origin nor
    # unrotated: a hero's root carries the 30-degree facing and the role-height
    # scale, and the torso hangs under that again. The fighter's left fist reads
    # (-0.36, -0.62, -0.20) as a location and sits at (0.01, -0.79, 1.28) in the
    # world.
    #
    # This solve used to aim an arm from a WORLD shoulder at a target built out
    # of LOCAL fist positions, so the two ends of the same arm were measured in
    # different spaces. Nothing errors: the sheet renders, the arm just reaches
    # for a point roughly 0.8 units from the one it wants. Frame 0 not matching
    # the rest sprite is the tell, and it is the first thing to check on any
    # inverse-kinematics entry.
    #
    # Everything is therefore solved in the ARM'S OWN PARENT SPACE. That is the
    # space the bone lengths and the write-back already speak, so it is the one
    # conversion that leaves `aim_segment` alone.
    rest_w = P.world_matrix(weapon)
    w_par = _parent_world(weapon)

    solved = []
    for a in arms:
        up = P.find(scn, a["upper"])[0]
        par = _parent_world(up)
        par_inv = par.inverted()
        solved.append({
            "par_inv": par_inv,
            "S": par_inv @ Vector(top_joint(scn, a["shoulder"])),
            "a": segment_length(scn, a["upper"]),
            "b": segment_length(scn, a["fore"]),
            # The pole only steers which way the elbow breaks, but it is a
            # DIRECTION and the parent carries a rotation, so it converts too.
            "pole": (par_inv.to_3x3() @ Vector(a["pole"])).normalized(),
            "up": up,
            "fo": P.find(scn, a["fore"])[0],
            "fi": P.find(scn, a["hand"])[0],
        })

    # Grips are captured in the WEAPON's own space off world positions, so the
    # hands stay exactly where the sprite models them at frame 0.
    for a in solved:
        a["grip"] = rest_w.inverted() @ P.world_matrix(a["fi"]).translation

    if mid is None:
        # below the shoulder line, midway between the two shoulders, in world
        mids = sum((Vector(top_joint(scn, x["shoulder"])) for x in arms),
                   Vector((0, 0, 0))) / len(arms)
        mid = Vector((0.0, mids.y - 0.16, mids.z - 0.38))
    elif mid == "hands":
        # the point between the fists: what a two-handed weapon turns about once
        # the grip is free to travel as well as rotate
        mid = sum((P.world_matrix(a["fi"]).translation for a in solved),
                  Vector((0, 0, 0))) / len(solved)
    else:
        mid = Vector(mid)

    base = tuple(root.location)
    sign = facing_sign(root)

    def make(f):
        lift, swing, lunge = f[0], f[1], f[2]
        # The optional travel columns. A weapon that only rotates leaves the
        # hands where they started, which is a flick rather than a chop.
        dx, dz = (f[3], f[4]) if len(f) > 4 else (0.0, 0.0)

        def pose():
            R = Euler((math.radians(lift), math.radians(swing * sign), 0),
                      'XYZ').to_matrix().to_4x4()
            # Travel is applied in WORLD space, after the rotation, so `dz` means
            # "this far up the screen" whatever angle the weapon is at.
            T = Matrix.Translation(Vector((dx * sign, 0.0, dz)))
            world = (T @ Matrix.Translation(mid) @ R
                     @ Matrix.Translation(-mid) @ rest_w)
            weapon.matrix_basis = w_par.inverted() @ world
            for a in solved:
                # The grip in world, then into this arm's own space to solve.
                target = a["par_inv"] @ (world @ a["grip"])
                elbow, hand, la, lb = P.two_bone_ik(a["S"], target, a["a"], a["b"],
                                                    a["pole"], stretch=stretch)
                P.aim_segment(a["up"], a["S"], elbow, a["a"])
                P.aim_segment(a["fo"], elbow, hand, a["b"])
                a["fi"].location = hand
            root.location = (base[0] + lunge * sign, base[1], base[2])
        return pose

    return [make(f) for f in frames]


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

    ## A CHOP NEEDS THE GRIP TO TRAVEL, NOT ONLY TO TURN

    **A frame may carry two more columns, `(lift, swing, lunge, dx, dz)`, which
    MOVE the weapon in world x and z before it is rotated.** Rotation alone
    cannot raise a sword, and that is the whole of what made the fighter read as
    flicking a blade at crotch height (user, 2026-08-02): his hands stayed on his
    hips for all eight frames and only the blade turned through them. A real
    overhead chop lifts the hilt to head height on the wind-up and drives it down
    and forward on the strike, so the hands must climb about 0.7 units and come
    back.

    `dx` is signed by facing exactly as `lunge` is, so one table chops the right
    way on a hero and on an enemy. The arms follow by inverse kinematics, which
    is what makes the travel safe: a rigid pivot would tear the shoulder open at
    this range, while a solved arm simply bends its elbow.

    **`mid="hands"` puts the rotation centre at the midpoint of the two rest
    grips.** That is the pivot a two-handed chop actually turns about, and with
    the grip now travelling it is the correct one: the hands carry the sword and
    the sword turns in the hands. The default chest point stays for anything that
    only turns, where a low centre is what keeps the arc off the face.
    """
    px = anim_cam(scn, res)
    poses = ik_poses(scn, root, weapon_name, arms, frames, mid=mid, stretch=stretch)
    out = P.out_dir()
    name = out_name or ("atk_" + key)
    path = P.render_strip(scn, poses, os.path.join(out, name + ".png"))
    P.upscale_nearest(path, os.path.join(out, name + "_big.png"), 4, bg="#2a2320")
    print("%s -> %d frames (IK)" % (name, len(frames)))
    return path


# The shared attack shapes live in `attack_shapes.py`, which imports no bpy so
# the system Python can read the roster that uses them. Re-exported here for
# anything already importing animkit.
from attack_shapes import (OVERHAND, SMASH, SLASH, SWEEP, CAST,  # noqa: E402,F401
                           CHOP, LOOSE, CHOP_ARMS, CHOP_BLADE,
                           HAMMER_SWING, HAMMER_WRIST, POLE_ARM, POLE_HEAD,
                           BOW_DRAW, BOW_BODY, DAGGER_ARM, DAGGER_WRIST,
                           BLESS, BLESS_HAND, JAB, JAB_HAND, FROST, FROST_HAND)
