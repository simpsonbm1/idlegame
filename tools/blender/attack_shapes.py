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
wrong one. `SMASH`, `SWEEP` and `LOOSE` are negated from what they were, which is
what puts all six into the one convention. The two figures the tables were
authored on come through unchanged by arithmetic: `OVERHAND` kept its numbers and
the right-facing knight multiplies by +1, `SMASH` was negated and the left-facing
goblin multiplies by -1, so both receive exactly the world rotation they did
before.

`lift` does not flip. It turns about X, carrying the arm toward the camera, and
both facings are only 30 degrees off camera-on, so forward in depth is the same
direction for all of them.
"""

OVERHAND = [(0, 0, 0), (-26, -40, 0.04), (-38, -86, 0.09), (-32, -66, 0.05),
            (-42, 28, -0.22), (-26, 14, -0.16), (-11, 5, -0.06), (0, 0, 0)]

SMASH = [(0, 0, 0), (-16, 20, 0.06), (-40, -92, 0.10), (-36, -60, 0.06),
         (-42, 52, -0.26), (-30, 34, -0.20), (-13, 14, -0.08), (0, 0, 0)]

# a short flat cut, for daggers and short blades: less wind-up, more lunge
SLASH = [(0, 0, 0), (-14, -26, 0.05), (-26, -54, 0.08), (-34, 10, -0.24),
         (-30, 44, -0.30), (-20, 26, -0.18), (-9, 10, -0.07), (0, 0, 0)]

# a two-handed horizontal sweep, for polearms and great weapons
SWEEP = [(0, 0, 0), (-18, -34, 0.06), (-34, -74, 0.10), (-40, -20, -0.18),
         (-44, 40, -0.28), (-30, 26, -0.19), (-13, 10, -0.08), (0, 0, 0)]

# a caster's push: almost no arc, the arm thrusts forward and holds
CAST = [(0, 0, 0), (-10, -18, 0.03), (-20, -32, 0.05), (-46, -6, -0.16),
        (-52, 8, -0.22), (-40, 6, -0.14), (-18, 2, -0.06), (0, 0, 0)]

# For a weapon already carried HEAD-UP at rest, where a raise would only take it
# past vertical and behind the man. The paladin's warhammer sits at about 45
# degrees behind vertical in his rest pose, so `OVERHAND` spent its whole wind-up
# laying the haft flat across his face and never got the head overhead at all.
# A short wind back, then one long drive forward and down.
CHOP = [(0, 0, 0), (-14, -22, 0.05), (-24, -34, 0.08), (-38, 20, -0.18),
        (-44, 78, -0.28), (-30, 54, -0.20), (-13, 22, -0.08), (0, 0, 0)]

# A bow draw and release: the arm pulls back, then snaps forward.
# Kept SMALL on purpose. A rigid pivot turns the bow, the arms and the string as
# one body, so it cannot draw anything, and the 30-degree version of this simply
# rocked a two-unit bow back and forth across the archer's face. What survives at
# this size is a shallow tilt plus the depth lunge, which reads as a shot.
LOOSE = [(0, 0, 0), (5, -8, -0.04), (9, -14, -0.07), (10, -16, -0.08),
         (2, 9, 0.06), (-4, 6, 0.04), (-2, 2, 0.02), (0, 0, 0)]
