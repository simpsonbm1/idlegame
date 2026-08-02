"""The shared attack shapes: eight frames of (lift, swing, lunge) each.

Kept free of `bpy` on purpose. `attack_roster.py` is read by the SYSTEM Python
when `render_attacks.py` lists or schedules work, exactly as `roster.py` is, so
nothing it imports may need Blender.

Most of the roster reuses one of these rather than getting its own table.

An attack whose end pose resembles its rest pose reads as nothing happening,
which is what the goblin's smash did until frame 1 gained a backward dip as
anticipation. Every shape here has one.

## SWING IS SIGNED AGAINST THE FIGURE, NOT AGAINST THE WORLD

**Positive swing carries the weapon FORWARD AND DOWN, the way the figure faces.**
Negative raises it up and behind. `animkit` reads the figure's own facing off its
root and flips the world rotation to suit, so one table drives a hero and an
enemy alike.

That rule is here because it was got wrong, and silently. `swing_sheet` turns the
pivot about world Y, which is one fixed direction, while heroes face +30 degrees
and every enemy family faces -30. A table authored against one of them therefore
plays BACKWARDS on the other, and nothing errors: the sheet renders, the limbs
stay attached, and the attack merely reads as an underhand scoop. `OVERHAND` was
authored on the knight, who faces right, and `SMASH` on the goblin brute, who
faces left, so the two disagreed from the start and half the roster inherited the
wrong one.

`lift` does not flip. It turns about X, carrying the arm toward the camera, and
both facings are only 30 degrees off camera-on.

## LUNGE IS A STEP TOWARD THE ENEMY

**Positive lunge steps forward, the way the figure faces.** It used to translate
the figure in world Y, which is the axis the camera looks down: at this camera's
3-degree tilt a 0.3 lunge moved the sprite under half a pixel, so every table's
lunge column had been doing nothing at all since the first sheet. Every value
below is signed for the new meaning -- step back on the wind-up, drive forward on
the strike -- and the magnitudes are raised, because a step now has to be seen.
About 0.4 world units is ten pixels at a 128 cell, which reads without walking a
figure out of its own frame.

## KEEPING A SWING FROM TEARING THE ARM OFF

A rigid pivot rotates whatever it is given about one point, so a large angle
moves an upper arm's top clear of the shoulder ball that is meant to swallow it.
Two things keep a swing attached: take the shoulder masses WITH the arm, and stay
under about 60 degrees. `SMASH` peaked at 92 and the fighter's arms visibly came
off his body (user, 2026-08-02). What buys back the impact is the lunge, not more
rotation.
"""

# A one-handed overhead cut: raise behind the head, cut down and forward.
OVERHAND = [(0, 0, 0), (-26, -40, -0.06), (-38, -86, -0.10), (-32, -66, -0.06),
            (-42, 28, 0.38), (-26, 14, 0.26), (-11, 5, 0.10), (0, 0, 0)]

# A two-handed smash. Held under 60 degrees so the shoulders stay in their
# sockets; the step is what sells it.
SMASH = [(0, 0, 0), (-14, 20, -0.08), (-32, -58, -0.14), (-28, -42, -0.08),
         (-38, 46, 0.44), (-26, 30, 0.30), (-11, 12, 0.11), (0, 0, 0)]

# A lunging cut, for daggers and short blades: little wind-up, then the fighter
# steps INTO it. The assassin read as waving his knives about until the step
# arrived, because a rotation alone never sends a blade at anybody.
SLASH = [(0, 0, 0), (-12, -24, -0.10), (-22, -40, -0.18), (-28, 18, 0.36),
         (-24, 46, 0.54), (-16, 28, 0.34), (-7, 11, 0.13), (0, 0, 0)]

# A two-handed horizontal sweep, for great weapons swung across the body.
SWEEP = [(0, 0, 0), (-18, -34, -0.08), (-34, -66, -0.14), (-40, -20, 0.10),
         (-44, 40, 0.46), (-30, 26, 0.32), (-13, 10, 0.12), (0, 0, 0)]

# A caster's push: almost no arc, the arm thrusts forward and holds.
CAST = [(0, 0, 0), (-10, -18, -0.04), (-20, -32, -0.07), (-46, -6, 0.26),
        (-52, 8, 0.36), (-40, 6, 0.23), (-18, 2, 0.09), (0, 0, 0)]

# For a weapon already carried HEAD-UP, where a raise only takes it past vertical
# and behind the man. Short wind back, one long drive forward and down.
CHOP = [(0, 0, 0), (-14, -22, -0.06), (-24, -34, -0.10), (-38, 20, 0.28),
        (-44, 58, 0.46), (-30, 40, 0.31), (-13, 16, 0.12), (0, 0, 0)]

# ---------------------------------------------------------------------------
# Pairs: two tables driving two pivots of one figure. See `attack_roster.Swing`.
# ---------------------------------------------------------------------------

# A BOW DRAW. One table cannot express this: a draw is the string hand traveling
# back while the bow hand holds still, and a single pivot can only rock the whole
# assembly, which swung a two-unit bow across the archer's face.
#
# BOW_HOLD is the bow arm, and carries the body's step. BOW_DRAW is the string
# hand, and takes the arrow and the string with it, so the arrow visibly goes
# back on the nock and then leaves.
BOW_HOLD = [(0, 0, 0), (3, -4, -0.05), (5, -7, -0.09), (6, -8, -0.11),
            (1, 5, 0.20), (-2, 4, 0.12), (-1, 1, 0.04), (0, 0, 0)]
BOW_DRAW = [(0, 0, 0), (5, -22, 0), (9, -40, 0), (11, -48, 0),
            (0, 16, 0), (-4, 9, 0), (-2, 3, 0), (0, 0, 0)]

# The single-pivot fallback, for a thrown or slung weapon where one arm IS the
# whole motion and there is no second hand to hold anything still. Kept small for
# the reason above: rotating a bow far enough to see swings it over its owner's
# face. Anything with a real bowstring wants the BOW_HOLD/BOW_DRAW pair instead.
LOOSE = [(0, 0, 0), (5, -12, -0.06), (9, -22, -0.11), (10, -26, -0.13),
         (2, 12, 0.24), (-4, 8, 0.15), (-2, 3, 0.05), (0, 0, 0)]

# A HAMMER SWUNG FROM THE FIST. A warhammer carried head-up puts its mass at the
# shoulder, and a pendulum pivoted at its own mass barely moves: measured across
# the paladin's whole chop, his hammer head traveled 0.58 units and the attack
# read as a caster's gesture (user, 2026-08-02). Turning the hammer about the
# FIST instead gives it the haft as a lever, and chaining that pivot under the
# arm's keeps the grip in the hand.
HAMMER_ARM = [(0, 0, 0), (-10, -16, -0.08), (-18, -24, -0.13), (-24, 10, 0.28),
              (-28, 26, 0.46), (-20, 18, 0.31), (-9, 7, 0.12), (0, 0, 0)]
HAMMER_HEAD = [(0, 0, 0), (0, -34, 0), (0, -58, 0), (0, 44, 0),
               (0, 104, 0), (0, 74, 0), (0, 30, 0), (0, 0, 0)]

# A POLEARM CHOPPED OVERHEAD, same construction and for the same reason: the
# banner's mass is all at the top of a five-unit pole, so the pole turns about the
# fist while the arm only carries it.
POLE_ARM = [(0, 0, 0), (-12, -18, -0.08), (-22, -28, -0.14), (-30, 12, 0.28),
            (-34, 30, 0.46), (-24, 20, 0.31), (-10, 8, 0.12), (0, 0, 0)]
POLE_HEAD = [(0, 0, 0), (0, -26, 0), (0, -44, 0), (0, 30, 0),
             (0, 76, 0), (0, 52, 0), (0, 21, 0), (0, 0, 0)]

# ---------------------------------------------------------------------------
# Three casters who must not move alike
# ---------------------------------------------------------------------------
# The mender, the battlemage and the frost adept all hold a staff in the left
# hand and all ran `CAST`, so all three played the identical animation (user,
# 2026-08-02). They are separated by the PATH the staff takes, which is the only
# thing a silhouette can carry: one holds at the top of a raise, one drives
# straight forward off a step, one travels a wide arc and never steps at all.

# The mender BLESSES: the staff tips back and HOLDS there. The hold is the read.
# Kept under 30 degrees. At 50 the staff lay across his own face and chest, which
# is the same failure as a shaft tilting its head over a figure's cheek: a raise
# expressed as a ROTATION tips a vertical staff flat long before it lifts it.
BLESS = [(0, 0, 0), (-10, -12, 0), (-18, -22, 0), (-26, -28, 0.02),
         (-28, -30, 0.02), (-24, -26, 0.02), (-14, -14, 0), (0, 0, 0)]

# The battlemage JABS: a short pull back, then the staff goes straight out on the
# longest step any hero takes.
JAB = [(0, 0, 0), (-8, -16, -0.12), (-14, -26, -0.22), (-30, 24, 0.32),
       (-34, 44, 0.58), (-24, 30, 0.39), (-10, 12, 0.15), (0, 0, 0)]

# The frost adept SWEEPS: the widest arc of the three, and his feet never move.
FROST = [(0, 0, 0), (-14, -40, 0), (-26, -66, 0), (-30, -20, 0),
         (-32, 34, 0.04), (-24, 50, 0.04), (-11, 22, 0.02), (0, 0, 0)]
