"""Attack animations as sprite sheets.

The figures were already built around roots (`sword_root`, `club_root`), so an
animation needs no remodelling. It adds ONE pivot at the shoulder, hands the arm
parts and the weapon root to it, and turns that pivot per frame. The lunge is a
separate small translation of the whole figure.

Every frame goes through the identical rig, so frame-to-frame the palette,
outline weight and pixel grid cannot drift. Hand-drawn frames are where sprite
animation normally gets expensive; here the cost is one list of angles.

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


def _rig(scn, pivot_loc, part_names, figure_root_name):
    """Put a pivot at pivot_loc (figure-local), give it the arm and the weapon,
    and return (pivot, figure_root)."""
    figure_root = P.find(scn, figure_root_name)[0]
    pivot = P.make_root(scn, "atk_pivot", loc=pivot_loc)
    pivot.parent = figure_root
    pivot.matrix_parent_inverse = figure_root.matrix_world.inverted()
    bpy.context.view_layer.update()
    P.reparent_keep(pivot, P.find(scn, *part_names))
    return pivot, figure_root


def _swing(scn, pivot, figure_root, angles, lunges, out_name):
    """angles: degrees about the pivot's Y axis, one per frame.

    Y, not X. The camera looks down world +Y, so the only rotation plane it
    can see a swing in is XZ, which is a turn about Y. Swinging about X moves
    the weapon toward and away from the camera, which reads as the arm merely
    lifting. Angle is measured from straight up: 0 is overhead, 90 is level
    and forward, 180 is straight down.

    lunges: forward offset in world units, one per frame."""
    base_loc = tuple(figure_root.location)

    def make(i):
        def pose():
            pivot.rotation_euler = (0, math.radians(angles[i]), 0)
            figure_root.location = (base_loc[0], base_loc[1] + lunges[i], base_loc[2])
        return pose

    # An animated cell needs headroom a portrait cell does not: a raised weapon
    # leaves the static frame. Grow the RESOLUTION, never the ortho scale, so the
    # figure renders at exactly the size it does in its static sprite.
    P.sprite_cam(scn, res=128, target_z=2.11)
    poses = [make(i) for i in range(len(angles))]
    path = P.render_strip(scn, poses, os.path.join(OUT, out_name + ".png"))
    P.upscale_nearest(path, os.path.join(OUT, out_name + "_big.png"), 4, bg="#2a2320")
    print(out_name, "->", len(angles), "frames")
    return path


def knight():
    """Overhand sword cut: raise overhead, cut down and forward, recover."""
    import build_knight
    importlib.reload(build_knight)
    scn = P.get_scene()
    pivot, root = _rig(scn, (-0.70, -0.10, 2.18),
                       ("upperR", "foreR", "gauntR", "pauldronR", "sword_root"),
                       "knight_root")
    angles = [0, -52, -95, -72, 30, 14, 5, 0]
    lunges = [0, 0.04, 0.09, 0.05, -0.22, -0.16, -0.06, 0]
    return _swing(scn, pivot, root, angles, lunges, "atk_knight")


def goblin():
    """Two-handed overhead smash: raise high, drive down, settle."""
    import build_goblin
    importlib.reload(build_goblin)
    scn = P.get_scene()
    pivot, root = _rig(scn, (0.0, -0.44, 2.06),
                       ("gupperL", "gforeL", "gfistL", "gupperR", "gforeR", "gfistR",
                        "club_root"),
                       "goblin_root")
    angles = [0, 42, 72, 50, -18, -9, -3, 0]
    lunges = [0, 0.05, 0.09, 0.05, -0.24, -0.17, -0.07, 0]
    return _swing(scn, pivot, root, angles, lunges, "atk_goblin")


if __name__ != "__main__":
    pass
