"""Attack sheets for the guardian knight and the goblin brute.

Kept as the two worked examples of the two techniques: the knight is a one-handed
pivot, the goblin a two-handed inverse-kinematics solve. Everything they use now
lives in `animkit.py`, and the rest of the roster is animated from the table in
`attack_roster.py`.

**Every joint is derived from the model here, where it used to be typed.** This
file previously carried the knight's shoulder as a literal coordinate and the
goblin's arm bone lengths as two literals read off the builder by hand. Nothing
errors when a model changes underneath those; the arm just detaches. That became
a live problem the moment `spritekit.finish()` started scaling every figure to
its role height, because a builder's own coordinates stopped being the figure's
real ones.

Run:
    import build_attack; build_attack.knight(); build_attack.goblin()
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import animkit as A
importlib.reload(P)
importlib.reload(A)


def knight():
    """Overhand sword cut: raise overhead, cut down and forward, recover.

    His sword hand is on the screen-left side and he attacks to the screen right,
    so the arc crosses the body. The lift column is what carries it in front of
    the breastplate rather than through it.
    """
    import build_knight
    importlib.reload(build_knight)
    scn = P.get_scene()
    root = A.figure_root(scn, "knight")
    arm = ("upperR", "foreR", "gauntR", "pauldronR")
    pivot = A.pivot_arm(scn, root, [("pauldronR",)], arm, "sword_root")
    return A.swing_sheet(scn, "knight", root, [pivot], A.OVERHAND)


def goblin():
    """Two-handed overhead smash: raise high, drive down, settle.

    The club is driven and the ARMS FOLLOW IT. Turning each arm rigidly about its
    own shoulder keeps the shoulders attached but lets the hands drift apart,
    because the gap between the shoulders is fixed while each hand's offset from
    its shoulder rotates. The club then floats between the fists.

    His club already points forward at rest, so a plain raise-and-drop would
    return to a pose resembling the rest frame. Frame 1 dips the club backward
    first: the anticipation makes the raise register and gives the smash a
    visibly different endpoint from where it started.
    """
    import build_goblin
    importlib.reload(build_goblin)
    scn = P.get_scene()
    root = A.figure_root(scn, "goblin")
    arms = [
        {"shoulder": ("gshoulderL",), "upper": "gupperL", "fore": "gforeL",
         "hand": "gfistL", "pole": (-1.1, 0.30, -0.8)},
        {"shoulder": ("gshoulderR",), "upper": "gupperR", "fore": "gforeR",
         "hand": "gfistR", "pole": (1.1, 0.30, -0.8)},
    ]
    return A.twohand_sheet(scn, "goblin", root, "club_root", arms, A.SMASH)
