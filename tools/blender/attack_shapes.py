"""The shared attack shapes: eight frames of (lift, swing, lunge) each.

Kept free of `bpy` on purpose. `attack_roster.py` is read by the SYSTEM Python
when `render_attacks.py` lists or schedules work, exactly as `roster.py` is, so
nothing it imports may need Blender.

Most of the roster reuses one of these rather than getting its own table.

An attack whose end pose resembles its rest pose reads as nothing happening,
which is what the goblin's smash did until frame 1 gained a backward dip as
anticipation. Every shape here has one.
"""

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
