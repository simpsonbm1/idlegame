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

One hand on the weapon means the arm can be turned rigidly about the shoulder.
Two hands is a closed loop and needs the reverse: drive the weapon, then solve
each arm to reach its grip point with two-bone IK. knight() shows the first,
goblin() the second.

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
    arm coming away from the shoulder.

    Good for a ONE-HANDED weapon only. Rotating two arms about their own
    shoulders does not keep their hands a fixed distance apart, because the gap
    between the shoulders is fixed while each hand's offset from its shoulder
    rotates, so a two-handed weapon comes loose from the fists. See goblin(),
    which drives the weapon and solves the arms with IK instead.

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

    The club is driven and the ARMS FOLLOW IT, solved with two-bone IK. Turning
    each arm rigidly about its own shoulder keeps the shoulders attached but lets
    the hands drift apart, because the gap between the shoulders is fixed while
    each hand's offset from its shoulder rotates. The club then floats between
    the fists. Driving the club and reaching for it fixes both ends at once.
    """
    from mathutils import Matrix, Euler, Vector
    import build_goblin
    importlib.reload(build_goblin)
    scn = P.get_scene()
    root = P.find(scn, "goblin_root")[0]
    club = P.find(scn, "club_root")[0]

    # Bone lengths are the cylinder depths from build_goblin.
    ARMS = [
        {"S": Vector((-0.80, -0.10, 2.24)), "a": 0.68, "b": 0.56, "pole": Vector((-1.1, 0.30, -0.8)),
         "up": P.find(scn, "gupperL")[0], "fo": P.find(scn, "gforeL")[0], "fi": P.find(scn, "gfistL")[0]},
        {"S": Vector((0.80, -0.10, 2.26)), "a": 0.66, "b": 0.60, "pole": Vector((1.1, 0.30, -0.8)),
         "up": P.find(scn, "gupperR")[0], "fo": P.find(scn, "gforeR")[0], "fi": P.find(scn, "gfistR")[0]},
    ]
    # Where each fist grips the shaft, expressed in the club's own space, taken
    # from the rest pose so frame 0 reproduces the static sprite exactly.
    club_rest = club.matrix_basis.copy()
    for arm in ARMS:
        arm["grip"] = club_rest.inverted() @ arm["fi"].location.copy()

    # Swing the club about a point BELOW the shoulder line. Pivoting on the
    # shoulders themselves lifts the grip to head height at full raise, which
    # folds both forearms across the face.
    MID = Vector((0.0, -0.26, 1.86))
    base_loc = tuple(root.location)

    def pose_for(lift, swing, lunge):
        def pose():
            R = Euler((math.radians(lift), math.radians(swing), 0), 'XYZ').to_matrix().to_4x4()
            club.matrix_basis = (Matrix.Translation(MID) @ R
                                 @ Matrix.Translation(-MID) @ club_rest)
            for arm in ARMS:
                target = club.matrix_basis @ arm["grip"]
                elbow, hand, la, lb = P.two_bone_ik(
                    arm["S"], target, arm["a"], arm["b"], arm["pole"], stretch=0.22)
                P.aim_segment(arm["up"], arm["S"], elbow, arm["a"])
                P.aim_segment(arm["fo"], elbow, hand, arm["b"])
                arm["fi"].location = hand
            root.location = (base_loc[0], base_loc[1] + lunge, base_loc[2])
        return pose

    # His club already points forward at rest, so a plain raise-and-drop returns
    # to a pose resembling the rest frame. Frame 1 dips the club backward first:
    # the anticipation makes the raise register and gives the smash a visibly
    # different endpoint than where it started.
    #          lift  swing  lunge
    frames = [(0, 0, 0),
              (-16, -20, 0.06),
              (-40, 92, 0.10),
              (-36, 60, 0.06),
              (-42, -52, -0.26),
              (-30, -34, -0.20),
              (-13, -14, -0.08),
              (0, 0, 0)]
    P.sprite_cam(scn, res=128, target_z=2.11)
    path = P.render_strip(scn, [pose_for(*f) for f in frames],
                          os.path.join(OUT, "atk_goblin.png"))
    P.upscale_nearest(path, os.path.join(OUT, "atk_goblin_big.png"), 4, bg="#2a2320")
    print("atk_goblin ->", len(frames), "frames (IK arms)")
    return path


