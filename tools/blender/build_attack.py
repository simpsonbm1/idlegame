"""Attack animations as sprite sheets.

The figures were already built around roots (`sword_root`, `club_root`), so an
animation needs no remodelling. It adds ONE pivot at the shoulder, hands the arm
parts and the weapon root to it, and turns that pivot per frame. The lunge is a
separate small translation of the whole figure.

Every frame goes through the identical rig, so frame-to-frame the palette,
outline weight and pixel grid cannot drift. Hand-drawn frames are where sprite
animation normally gets expensive; here the cost is one table of angles.

A swing takes TWO angles per frame, and it needs both:

  swing (Y)  the arc the camera sees. The camera looks down world +Y, so XZ is
             the only plane a swing shows in, and that is a turn about Y.
             Measured from straight up: 0 overhead, 90 level and forward, 180
             straight down.
  lift  (X)  how far the arm is carried in FRONT of the body, toward the
             direction the figure faces. Negative is forward.

Swing alone is what a first pass looks like, and it fails. A figure's weapon arm
sits on the opposite side from the direction it attacks, so a flat arc drags the
arm straight through the torso, and on a two-handed swing it drives the shoulders
up through the head. Lift moves the arc forward in depth so it passes in front of
the body instead. Any frame with a real swing needs a real lift.

Run:
    import build_attack; build_attack.knight(); build_attack.goblin()
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
importlib.reload(P)
OUT = P.out_dir()


def _rig(scn, groups, figure_root_name):
    """One pivot per group, each at a real joint, all turned by the same angles.

    A pivot MUST sit on the joint the limb actually rotates about. Put it
    anywhere else and the limb translates as well as turns, which reads as the
    arm coming away from the shoulder. A two-handed weapon therefore needs three
    pivots -- one at each shoulder, plus one at their midpoint carrying the
    weapon. The hands stay the correct distance apart because each arm turns by
    the same amount about its own joint, and the weapon tracks the midpoint of
    the two hands exactly.

    groups: list of (pivot_location, part_names). Returns (pivots, figure_root).
    """
    figure_root = P.find(scn, figure_root_name)[0]
    pivots = []
    for loc, names in groups:
        pivot = P.make_root(scn, "atk_pivot", loc=loc)
        pivot.parent = figure_root
        pivot.matrix_parent_inverse = figure_root.matrix_world.inverted()
        bpy.context.view_layer.update()
        P.reparent_keep(pivot, P.find(scn, *names))
        pivots.append(pivot)
    return pivots, figure_root


def _swing(scn, pivots, figure_root, frames, out_name):
    """frames: one (lift, swing, lunge) triple per frame, angles in degrees."""
    base_loc = tuple(figure_root.location)

    def make(i):
        lift, swing, lunge = frames[i]

        def pose():
            for pivot in pivots:
                pivot.rotation_euler = (math.radians(lift), math.radians(swing), 0)
            figure_root.location = (base_loc[0], base_loc[1] + lunge, base_loc[2])
        return pose

    # An animated cell needs headroom a portrait cell does not: a raised weapon
    # leaves the static frame. Grow the RESOLUTION, never the ortho scale, so the
    # figure renders at exactly the size it does in its static sprite.
    P.sprite_cam(scn, res=128, target_z=2.11)
    poses = [make(i) for i in range(len(frames))]
    path = P.render_strip(scn, poses, os.path.join(OUT, out_name + ".png"))
    P.upscale_nearest(path, os.path.join(OUT, out_name + "_big.png"), 4, bg="#2a2320")
    print(out_name, "->", len(frames), "frames")
    return path


def knight():
    """Overhand sword cut: raise overhead, cut down and forward, recover.

    His sword hand is on the screen-left side and he attacks to the screen right,
    so the arc crosses the body. The lift column is what carries it in front of
    the breastplate rather than through it.
    """
    import build_knight
    importlib.reload(build_knight)
    scn = P.get_scene()
    pivot, root = _rig(scn, [((-0.70, -0.10, 2.18),
                              ("upperR", "foreR", "gauntR", "pauldronR", "sword_root"))],
                       "knight_root")
    #          lift  swing  lunge
    frames = [(0, 0, 0),
              (-26, -40, 0.04),
              (-38, -86, 0.09),
              (-32, -66, 0.05),
              (-42, 28, -0.22),
              (-26, 14, -0.16),
              (-11, 5, -0.06),
              (0, 0, 0)]
    return _swing(scn, pivot, root, frames, "atk_knight")


def goblin():
    """Two-handed overhead smash: raise high, drive down, settle.

    Three pivots. Each arm turns about its own shoulder ball, so the shoulder end
    of the arm stays welded to the torso, and the club rides the midpoint of the
    two shoulders, which is exactly where the midpoint of the two hands goes.
    A single shared pivot in front of the chest was what made the arms look
    detached, because it translated them as well as turning them.
    """
    import build_goblin
    importlib.reload(build_goblin)
    scn = P.get_scene()
    pivot, root = _rig(scn, [
        ((-0.80, -0.10, 2.24), ("gshoulderL", "gupperL", "gforeL", "gfistL")),
        ((0.80, -0.10, 2.26), ("gshoulderR", "gupperR", "gforeR", "gfistR", "gpauldron")),
        ((0.0, -0.10, 2.25), ("club_root",)),
    ], "goblin_root")
    #          lift  swing  lunge
    # His club already points forward at rest, so a plain raise-and-drop returns
    # to a pose that looks like the rest frame. Frame 1 dips the club backward
    # first: the anticipation makes the raise register and gives the smash a
    # visibly different endpoint than where it started.
    #          lift  swing  lunge
    frames = [(0, 0, 0),
              (-16, -20, 0.06),
              (-38, 96, 0.10),
              (-34, 60, 0.06),
              (-40, -54, -0.26),
              (-30, -36, -0.20),
              (-14, -15, -0.08),
              (0, 0, 0)]
    return _swing(scn, pivot, root, frames, "atk_goblin")
