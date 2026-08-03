"""Where a part actually IS, and where it actually GOES, in world units.

    blender -b --factory-startup --python tools/blender/probe_rig.py -- <ATTACK_KEY> <part>...

Prints each named part's world position at rest, then its position on every frame
of that entry's attack, alongside the swing angle driving it.

**This exists because looking at the frames does not work.** Three animation
rounds were rejected in one day and every diagnosis came from these numbers
rather than from the renders. Each failure was invisible in a strip and obvious
in one column of measurements:

  - The fighter's fist jumped 1.64 units on reparenting alone and landed below
    the ground line. The sheet rendered fine and the limbs merely looked odd.
  - The paladin's hammer head sat at world z 2.14 with his shoulder joint at
    2.15, so the arm was spinning the hammer about its own head. No amount of
    staring says "these two numbers are the same".
  - The assassin's blade read +0.41 forward on his WIND-UP frame and -0.92 back
    on his strike, which is the whole attack playing in reverse. It looked
    plausible in a strip and survived a review that way.

Screen-x is world x and screen-up is world z for the sprite camera, so the two
numbers printed are where the part sits on screen. `top` is the highest point of
the part's own bounding box, which is what `^name` joints resolve to.

Companions: `render_attacks.py --check` measures FRAMING the same way, because a
clipped blade tip just looks like a short blade.
"""

import importlib
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P      # noqa: E402
import animkit as A       # noqa: E402
import attack_roster as R  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) < 2:
        print(__doc__)
        return 2
    key, names = argv[0], argv[1:]

    match = [a for a in R.ATTACKS if a.key == key]
    if not match:
        print("no attack entry named %r" % key)
        return 2
    spec = match[0]

    # A rarity variant is the same builder under a different HERO_TIER, exactly as
    # `render_attacks.py` runs it. Without this a tier key silently probes common.
    os.environ.update(spec.env)
    importlib.import_module(spec.module)

    scn = P.get_scene()
    root = A.figure_root(scn, key)
    sign = A.facing_sign(root)

    # An inverse-kinematics entry has no pivots at all: the weapon is placed
    # directly and the arms are solved to reach it. `animkit.ik_poses` is the
    # renderer's own posing code, called here so the numbers below describe the
    # attack that actually ships.
    poses = A.ik_poses(scn, root, spec.ik.weapon, spec.ik.arms, spec.frames,
                       mid=spec.ik.mid, stretch=spec.ik.stretch) if spec.ik else None

    made = [] if poses else [A.pivot_arm(scn, root, g.joint, g.parts, g.weapon,
                                         name="probe_pivot_%d" % i)
                             for i, g in enumerate(spec.groups)]
    for g, piv in zip(spec.groups, made):
        if g.parent is not None:
            A.chain_pivot(piv, made[g.parent])
    tracks = list(zip(made, [g.frames for g in spec.groups]))

    # `name#2` picks the SECOND part of that name, in build order. A dual-wielder
    # builds both blades in one loop, so both are called "dagblade" and probing
    # the name alone silently measures only the first one -- which is how a knife
    # attack could read forwards on one hand and backwards on the other and still
    # look measured.
    parts = []
    for n in names:
        base, _, idx = n.partition("#")
        found = P.find(scn, base)
        if not found:
            print("no part named %r on %s" % (base, key))
            continue
        i = int(idx) - 1 if idx else 0
        if i >= len(found):
            print("only %d part(s) named %r on %s" % (len(found), base, key))
            continue
        parts.append((n, found[i]))
    if not parts:
        return 2

    print("%s  facing %+.0f  %d pivot(s)" % (key, sign, len(made)))
    for n, ob in parts:
        c, t = A.centre_of(ob), A.top_of(ob)
        print("  REST %-14s x=%+.2f y=%+.2f z=%+.2f   top z=%+.2f"
              % (n, c.x, c.y, c.z, t.z))

    for i in range(len(spec.frames)):
        if poses:
            poses[i]()
        for piv, own in tracks:
            lift, swing, _ = (own or spec.frames)[i]
            piv.rotation_euler = (math.radians(lift), math.radians(swing * sign), 0)
        bpy.context.view_layer.update()
        cells = []
        for n, ob in parts:
            c = A.centre_of(ob)
            cells.append("%s x=%+.2f z=%+.2f" % (n, c.x, c.z))
        print("  f%d  body swing %+4d   %s"
              % (i, spec.frames[i][1], "   ".join(cells)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
