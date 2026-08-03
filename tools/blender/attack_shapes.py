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

# ---------------------------------------------------------------------------
# WHERE A PIVOT GOES DECIDES WHETHER ANYTHING SWINGS
# ---------------------------------------------------------------------------
# Two rules, and between them they are most of what makes an attack read.
#
# **An arm turns about the TOP OF ITS OWN UPPER ARM.** That point is the shoulder
# joint, and it is the one point a rotation leaves exactly where it was, so the
# shoulder ball on the torso keeps covering the arm's top. Any other centre --
# the ball's own middle, the midpoint between two shoulders -- TRANSLATES the arm
# as well as turning it, and the joint visibly comes apart.
#
# **A weapon needs a pivot FAR from itself.** Radius is the whole of it: a hammer
# turned about the fist holding it is a wrist flick, whatever the angle. The two
# far pivots a figure has are its shoulder and its waist, and `torso_root` sits
# exactly on the hip, so `[("torso_root",)]` is a waist swing that carries the
# whole upper body. A two-handed grip has to come from the waist, because both
# hands are then rigid with the weapon and cannot drift off it.

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

# **DO NOT ROTATE `torso_root`.** It sits on the hip, so it looks like the waist
# joint a big swing wants, and it is not one: the torso is a cylinder and a sphere
# meeting the legs flat, and turning them 20 degrees tears the belt off the hips
# and sinks the head between the shoulders. The fighter and the paladin were both
# tried that way and both came out broken. Reach comes from the shoulder and the
# wrist, which are real joints on these models.

# A TWO-HANDED CHOP. Both fists are on the hilt 0.65 apart, so the arms, both
# shoulder balls and the sword turn as ONE solid piece about the midpoint between
# the shoulder JOINTS. Nothing can leave anything.
#
# **Keep the arm rotation under about 20 degrees.** It is the one rotation that
# slides the shoulder balls off the torso: they sit 0.60 from that midpoint and
# travel twice that times the half-angle, so 18 degrees moves them under five
# pixels and reads as a shoulder rolling. At 58 they came off the body outright
# (user, 2026-08-02).
#
# The blade's reach comes from CHOP_BLADE, which turns the sword about the point
# between the fists. The hands stay put and the blade sweeps through them, which
# is what a two-handed chop looks like anyway.
CHOP_ARMS = [(0, 0, 0), (-4, -7, -0.04), (-7, -12, -0.07), (-6, -5, -0.02),
             (-9, 18, 0.20), (-6, 13, 0.13), (-2, 5, 0.05), (0, 0, 0)]
CHOP_BLADE = [(0, 0, 0), (0, -22, 0), (0, -38, 0), (0, -14, 0),
              (0, 65, 0), (0, 45, 0), (0, 18, 0), (0, 0, 0)]

# ---------------------------------------------------------------------------
# WEAPON-DRIVEN SHAPES: five columns, and the arms are SOLVED rather than turned
# ---------------------------------------------------------------------------
# `(lift, swing, lunge, dx, dz)`. The last two MOVE the weapon in world x and z,
# and they are the columns a rigid pivot can never have. `animkit.twohand_sheet`
# then solves each arm to reach its own grip, so the elbows bend to follow.
#
# **A rotation cannot raise a sword.** Every hero above turns a rigid arm about
# one fixed point, which spins a weapon and moves a hand along a short arc and
# nothing else. The fighter's chop was rejected as "holding the sword at
# crotch-level and flicking it at the enemy" (user, 2026-08-02) and that is
# exactly what the geometry can produce: his fists never left his hips, so the
# only motion on screen was the blade turning through his grip.
#
# The travel is where the attack lives now, and the rotation only angles the
# blade. Judge one of these by whether the HANDS go somewhere.

# A TWO-HANDED OVERHEAD CHOP. The hilt climbs about 0.8 to head height while the
# blade tips back over the shoulder, then drives down and forward off the step.
# Total blade travel is 136 degrees, which a rigid arm could not survive and a
# solved one does not care about: nothing is turning about a shoulder.
CHOP_SWORD = [(0, 0, 0, 0, 0),
              (-6, -30, -0.10, -0.10, 0.34),
              (-10, -58, -0.18, -0.18, 0.72),
              (-8, -52, -0.14, -0.14, 0.80),
              (-12, 78, 0.40, 0.34, 0.12),
              (-8, 62, 0.28, 0.24, -0.04),
              (-3, 26, 0.10, 0.10, -0.01),
              (0, 0, 0, 0, 0)]

# A ONE-HANDED OVERHAND HAMMER BLOW, weapon-driven. Heavier than the sword chop:
# a longer wind-up, a beat held at the top, and a harder shorter strike. The head
# is ABOVE the grip at rest, so it leads the arc down onto the target, which is
# what makes it read as hammering rather than as swiping.
#
# **The strike angle is set by where the HEAD ends, not by how far it turns.** At
# 86 degrees the head finished at world z 1.65 with the grip at 1.29, so it was
# still above the hand and pointing forward: a swipe. It has to pass horizontal
# and come down, which on a hammer resting near-vertical means about 125.
HAMMER_BLOW = [(0, 0, 0, 0, 0),
               (-5, -34, -0.08, -0.12, 0.30),
               (-9, -66, -0.16, -0.22, 0.68),
               (-7, -60, -0.12, -0.20, 0.78),
               (-11, 124, 0.44, 0.36, -0.10),
               (-7, 100, 0.30, 0.26, -0.18),
               (-3, 42, 0.11, 0.11, -0.06),
               (0, 0, 0, 0, 0)]

# A ONE-HANDED HAMMER: shoulder, then wrist. The arm turns about the top of its
# own upper arm, which is the shoulder joint and the one point a rotation leaves
# in place, so the pauldron keeps covering it.
#
# **A BUSINESS END BELOW ITS PIVOT INVERTS THE SIGN.** Rotating about Y sends a
# point ABOVE the pivot forward and a point BELOW it backward, so a hammer hanging
# head-down and a dagger pointing blade-down both need their swing column negated
# against the table convention. Measure the tip rather than reasoning about it: the
# assassin's blade read +0.41 forward on his WIND-UP frame and -0.92 back on his
# strike, which is the whole attack playing in reverse.
#
# **The two angles ADD UP, so budget the total.** A hammer carried head-up needs
# both: the wrist alone is a flick, and the shoulder alone spins the hammer about
# its own head, because that head sits at world z 2.14 and the shoulder joint is
# at the same height. Around 115 degrees together puts the head down and in front,
# where a hammer lands. At 182 it passed straight down and came back up behind
# him, and the measured path doubled back between two frames.
HAMMER_WRIST = [(0, 0, 0), (0, 18, 0), (0, 30, 0), (0, -8, 0), (0, -52, 0), (0, -36, 0), (0, -14, 0), (0, 0, 0)]
HAMMER_SWING = [(0, 0, 0), (-8, 12, -0.06), (-14, 20, -0.1), (-10, 2, 0.06), (-16, -34, 0.3), (-10, -24, 0.2), (-4, -9, 0.07), (0, 0, 0)]

# A TWIN-DAGGER STAB, weapon-driven, ONE TABLE PER KNIFE. The pivot version was
# rejected as "still not extending his arms to make a stabbing motion" (user,
# 2026-08-02), and a pivot cannot do anything else: it swings each fist along a
# short arc at whatever radius the arm happens to be, so the hands orbit his hips.
#
# **The two knives must not move together.** Both arms running one table is a man
# shoving both fists out at once, which reads as a push rather than a knife
# attack. The near hand leads and the far hand lands two frames behind it, so
# there are two separate strikes inside eight frames.
#
# The drive is the `dx` column: about 0.6 units of travel, where the pivot
# version moved a fist a tenth of that. The body's step stays small on purpose --
# a body sliding forward as one rigid piece read as him thrusting his pelvis at
# the enemy (user, 2026-08-02). The extension is the attack; the step underlines it.
# **The sixth column POINTS the blade**, blending from the idle grip at 0 to level
# and straight at the enemy at 1. It exists because a stab that only travels is
# still the idle silhouette sliding forward: "he's just pushing it forward in the
# same orientation as the idle" (user, 2026-08-03). A knife has to turn to face
# what it is going into.
#
# It is a DIRECTION rather than an angle for a reason. This line's four tiers grip
# their knives at four different rotations by design, so one swing column leaves
# four blades pointing four ways, and only naming the target direction is correct
# on all of them.
STAB_LEAD = [(0, 0, 0, 0, 0, 0.00),
             (0, 0, 0, -0.16, 0.06, 0.30),
             (0, 0, 0, -0.24, 0.10, 0.55),
             (0, 0, 0, 0.34, 0.04, 0.90),
             (0, 0, 0, 0.62, -0.02, 1.00),
             (0, 0, 0, 0.40, -0.02, 0.85),
             (0, 0, 0, 0.16, 0.00, 0.40),
             (0, 0, 0, 0, 0, 0.00)]
STAB_REAR = [(0, 0, 0, 0, 0, 0.00),
             (0, 0, 0, -0.10, 0.04, 0.20),
             (0, 0, 0, -0.18, 0.08, 0.40),
             (0, 0, 0, -0.24, 0.12, 0.60),
             (0, 0, 0, 0.30, 0.06, 0.90),
             (0, 0, 0, 0.58, 0.00, 1.00),
             (0, 0, 0, 0.26, -0.01, 0.55),
             (0, 0, 0, 0, 0, 0.00)]
# The body under those two: a small brace back and a small step in. Its lift and
# swing columns drive nothing, because every weapon here carries its own table.
STAB_BODY = [(0, 0, 0), (0, 0, -0.05), (0, 0, -0.09), (0, 0, 0.10),
             (0, 0, 0.18), (0, 0, 0.13), (0, 0, 0.05), (0, 0, 0)]

# A BOW DRAW, weapon-driven: the BOW ARM pushes the bow up and out while the
# STRING HAND travels back and up to the face. The pivot version was rejected as
# "just punching himself in the stomach" (user, 2026-08-02) and could not have
# been anything else -- his string hand rests at his belly and a shoulder rotation
# moves it around his belly.
#
# `BOW_PUSH` drives the bow itself, so the bow hand rides it. `BOW_HAND` is the
# string hand's own world-space track, which is the column no pivot has: it is
# the hand LEAVING the bow rather than following it.
#
# **Keep the bow's own rotation tiny.** It is the tallest thin object the hero
# owns, so a few degrees is already visible and thirty lay it across his face --
# the same rule the staff heroes pay.
BOW_PUSH = [(0, 0, 0, 0, 0),
            (0, 0, 0, 0.06, 0.06),
            (0, 0, 0, 0.12, 0.10),
            (0, 0, 0, 0.15, 0.12),
            (0, 0, 0, 0.19, 0.11),
            (0, 0, 0, 0.10, 0.06),
            (0, 0, 0, 0.04, 0.02),
            (0, 0, 0, 0, 0)]
# The arrow's own draw, RELATIVE TO THE BOW, which it follows. Frame 4 is the
# loose: the shaft leaves the string and is back on it by frame 5, because eight
# frames have no room to fly one anywhere and still return to rest.
ARROW_DRAW = [(0, 0, 0, 0, 0),
              (0, 0, 0, -0.16, 0.06),
              (0, 0, 0, -0.34, 0.12),
              (0, 0, 0, -0.44, 0.15),
              (0, 0, 0, 0.70, 0.10),
              (0, 0, 0, 0, 0),
              (0, 0, 0, 0, 0),
              (0, 0, 0, 0, 0)]
# The NOCK follows the drawing hand and then SNAPS STRAIGHT. Same table as the
# shaft up to frame 3 and nothing like it on frame 4, which is the whole
# difference between a string releasing and a string being towed away by an arrow.
NOCK_DRAW = [(0, 0, 0, 0, 0),
             (0, 0, 0, -0.16, 0.06),
             (0, 0, 0, -0.34, 0.12),
             (0, 0, 0, -0.44, 0.15),
             (0, 0, 0, 0.06, 0.02),
             (0, 0, 0, 0, 0),
             (0, 0, 0, 0, 0),
             (0, 0, 0, 0, 0)]
# Back and UP: a draw ends at the cheek, not at the ribs. The release is the jump
# from frame 3 to frame 4, where the hand comes forward and the height holds.
#
# **These are small because the bow's own rise carries the string hand too.** The
# track is added on TOP of the grip's travel with the bow, so a 0.54 lift here put
# his drawing fist at world z 2.72 with his shoulder at 2.13 -- above his own head,
# which is a salute rather than a draw. Measured, not guessed.
BOW_HAND = [(0, 0, 0),
            (-0.16, 0, 0.06),
            (-0.34, 0, 0.12),
            (-0.44, 0, 0.15),
            (-0.06, 0, 0.10),
            (-0.02, 0, 0.05),
            (-0.01, 0, 0.01),
            (0, 0, 0)]

# SUPERSEDED by BOW_PUSH and BOW_HAND above, and kept only for what it records:
# a bow draw expressed as a shoulder rotation. It is not on the roster.
#
# A BOW DRAW: the STRING HAND ONLY, about its own shoulder. Nothing else moves.
#
# **Do not hand the bowstring or the arrow to the drawing arm.** They belong to the
# bow, and an arm rotating about its shoulder carries them off it: the string
# visibly came away from the limbs and waved about in front of him (user,
# 2026-08-02). What reads as a draw is the elbow travelling back and returning,
# which is the one thing here that is true.
BOW_DRAW = [(0, 0, 0), (5, -20, 0), (9, -34, 0), (11, -40, 0),
            (0, 12, 0), (-4, 7, 0), (-2, 2, 0), (0, 0, 0)]
# The body's own table: a small brace and release, and NO swing at all. A step is
# what turned the assassin into a man thrusting his pelvis at the enemy, so it
# stays small on a figure that is meant to stand and shoot.
BOW_BODY = [(0, 0, 0), (0, 0, -0.04), (0, 0, -0.07), (0, 0, -0.08),
            (0, 0, 0.10), (0, 0, 0.06), (0, 0, 0.02), (0, 0, 0)]

# The single-pivot fallback, for a thrown or slung weapon where one arm IS the
# whole motion. Kept small: rotating a bow far enough to see swings it over its
# owner's face.
LOOSE = [(0, 0, 0), (5, -12, -0.06), (9, -22, -0.11), (10, -26, -0.13),
         (2, 12, 0.24), (-4, 8, 0.15), (-2, 3, 0.05), (0, 0, 0)]

# SUPERSEDED by STAB_LEAD and STAB_REAR above, and kept only for what it records:
# a stab expressed as two shoulder rotations. It is not on the roster.
#
# TWIN DAGGERS: each arm about its own shoulder, each blade about its own fist.
#
# **The step stays small.** At 0.54 the assassin slid forward as one rigid piece
# with nothing else changing, and it read as him thrusting his pelvis at the enemy
# (user, 2026-08-02). A body that slides without bending is not lunging. The drive
# has to come from the arm extending, and the step only underlines it.
DAGGER_ARM = [(0, 0, 0), (-10, 12, -0.05), (-18, 20, -0.08), (-24, -12, 0.09), (-20, -26, 0.14), (-14, -17, 0.09), (-6, -7, 0.03), (0, 0, 0)]
DAGGER_WRIST = [(0, 0, 0), (0, 8, 0), (0, 14, 0), (0, -14, 0), (0, -29, 0), (0, -19, 0), (0, -8, 0), (0, 0, 0)]

# ---------------------------------------------------------------------------
# Three casters who must not move alike
# ---------------------------------------------------------------------------
# The mender, the battlemage and the frost adept all hold a staff in the left hand
# and all ran `CAST`, so all three played the identical animation and the developer
# read them as one character twice over (user, 2026-08-02). Each now runs a
# shoulder and a wrist, and what separates them is the PATH the staff takes,
# because that is all a silhouette carries.

# The mender BLESSES: the staff tips back and HOLDS. The hold is the read, and the
# wrist tips WITH the arm so the staff stays upright rather than laying over.
# **Under 30 degrees at the shoulder.** A vertical staff rotated further lies flat
# across his own face long before it looks raised; genuinely lifting it needs the
# pivot to translate, which a (lift, swing, lunge) table cannot say.
BLESS = [(0, 0, 0), (-8, -14, 0), (-14, -24, 0), (-20, -30, 0.02),
         (-22, -32, 0.02), (-18, -26, 0.02), (-10, -13, 0), (0, 0, 0)]
BLESS_HAND = [(0, 0, 0), (0, -3, 0), (0, -5, 0), (0, -7, 0),
              (0, -8, 0), (0, -6, 0), (0, -3, 0), (0, 0, 0)]

# The battlemage JABS: the staff goes straight out, wrist following the shoulder,
# off the longest step any hero takes.
JAB = [(0, 0, 0), (-8, -16, -0.10), (-14, -26, -0.18), (-30, 26, 0.28),
       (-34, 48, 0.46), (-24, 32, 0.30), (-10, 13, 0.11), (0, 0, 0)]
# **A staff's wrist rotation has to stay small.** The hand grips it near the
# middle, so turning the staff about the hand spins it end over end and reads as
# baton twirling rather than casting. At 38 degrees the battlemage's crystal came
# down to hand height and his butt-end swung up behind him. The arm carries the
# staff; the wrist only angles it.
JAB_HAND = [(0, 0, 0), (0, -4, 0), (0, -7, 0), (0, 7, 0),
            (0, 13, 0), (0, 9, 0), (0, 4, 0), (0, 0, 0)]

# The frost adept SWEEPS: the widest arc of the three, wrist lagging the shoulder
# so the staff head trails and then whips past. His feet barely move.
FROST = [(0, 0, 0), (-14, -34, 0), (-26, -56, 0), (-30, -14, 0),
         (-32, 40, 0.06), (-24, 54, 0.06), (-11, 24, 0.02), (0, 0, 0)]
FROST_HAND = [(0, 0, 0), (0, -8, 0), (0, -13, 0), (0, 3, 0),
              (0, 14, 0), (0, 18, 0), (0, 8, 0), (0, 0, 0)]

# A POLEARM CHOPPED OVERHEAD, weapon-driven. The pivot version swept the head 4.85
# units and read as workable, but the two fists drifted 0.18 apart on the shaft
# while doing it, because two pivots turning about one shared point cannot hold a
# two-handed grip. Solving the arms locks both hands to the pole and frees the
# grip to CLIMB, which is what the wind-up wanted and no rotation could give it.
#
# The head sits about 2.2 above the grip, so it travels far on a modest angle.
# Keep the total under about 100 degrees or it passes vertical and comes back up
# behind him, which is the fault the paladin's hammer paid for at 182.
POLE_CHOP = [(0, 0, 0, 0, 0),
             (-4, -22, -0.06, -0.10, 0.16),
             (-7, -38, -0.12, -0.16, 0.30),
             (-6, -30, -0.08, -0.12, 0.36),
             (-12, 104, 0.44, 0.38, -0.10),
             (-8, 84, 0.30, 0.26, -0.16),
             (-3, 34, 0.12, 0.10, -0.06),
             (0, 0, 0, 0, 0)]

# A POLEARM CHOPPED OVERHEAD, arm then wrist, same construction as the hammer:
# the banner's mass is all at the top of a five-unit pole, so the wrist carries
# most of the travel and the arm throws the grip across.
POLE_ARM = [(0, 0, 0), (-12, -16, -0.08), (-22, -26, -0.14), (-30, 10, 0.26),
            (-34, 34, 0.44), (-24, 23, 0.29), (-10, 9, 0.11), (0, 0, 0)]
POLE_HEAD = [(0, 0, 0), (0, -22, 0), (0, -38, 0), (0, 18, 0),
             (0, 62, 0), (0, 43, 0), (0, 17, 0), (0, 0, 0)]
