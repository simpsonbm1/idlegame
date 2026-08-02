"""Assassin -- M15_ASSET_SPECS.md entry 5.

  "a slim hooded assassin in dark charcoal-and-purple leathers, face in shadow,
   slightly crouched, twin curved daggers held low"

The one hero whose face is NOT open, which would normally break the rule that
separates heroes from bandits. He gets away with it because his palette is
charcoal and violet where every bandit is brown, and because he is the only
crouched hero -- two differences carrying the load one usually does.

The Rogue's daggers are held LOW and close, against the goblin skulker's
low-and-forward and the undead reaver's wide. Three twin-blade figures, three
poses -- and within this line each tier grips its own knives differently, which
is what separates the four silhouettes.

Rarity works by tier, set through the `HERO_TIER` environment variable and driven
from `roster.py`. See `hero_kit.py` for what each tier changes. This hero's own
sprite is **Common**, so that tier gets no separate file.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import hero_kit as H
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(H)

scn = P.get_scene()
px = H.start(scn, res=112)
M = H.palette()
TRIM = H.trim_mat(M)        # None on a common hero: plain and field-worn
GLOW = H.glow_mat(M)        # epic and legendary only
LEGEND = H.is_legendary()

# ---------------------------------------------------------------------------
# The assassin line: Rogue, Assassin, Nightblade, Phantom (DESIGN.md).
#
# The FACE is this line's read, because a killer is defined by how much of him
# you can see: a hood framing a shadowed void, a half-mask with the eyes bare,
# a cloth mask under cropped hair, and finally a hood over nothing at all with
# two embers in it. The blade shape carries the next read -- curved kris, long
# single edge, straight stiletto, wide flared -- and the GRIP carries the
# silhouette: each tier holds his knives the way his kind of killer would.
#
# USER 2026-08-02, approving the line: "it passes, but swap rare and epic. the
# rare one is reading as a higher tier than epic." So the black-and-red masked
# killer and the blue-coated duellist traded places, whole: body, accent, lean,
# gear, face, blade and grip all move together, because a tier here IS a person
# rather than a set of upgrades. The tier-driven things stay put and now push
# the right way -- gold trim and glowing eyes land on the black killer, steel on
# the duellist. The names fit better this way round too: Nightblade suits the
# one dressed in black.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

# USER REVIEW 2026-08-01: "assassins need some more thought, they just have a
# different color, bigger swords, and more stuff on their face through the
# tiers." All four were charcoal head to toe, so a sash was the only thing that
# ever changed. The BODY value is the fix, the same one the menders needed:
# brown leather, deep blue, charcoal, then a spectral violet. A killer in
# leathers, a duellist in a blue coat, a killer in black, and a thing that is
# not wearing clothes at all.
BODY = {"common": "leath", "rare": "azure", "epic": "charcoal",
        "legendary": "violet"}[TIER]
# The Assassin's accent is DARK on purpose. His sash, strap, collar and mask all
# use it, and in cream those four converged into one pale mass over his face and
# chest. His blue coat is his read; the trim must not compete with it.
ACCENT = {"common": "green", "rare": "charcoal", "epic": "crimson",
          "legendary": "ice"}[TIER]
BD, AC = M[BODY], M[ACCENT]

figure, detail, noline, rags = [], [], [], []

HIP = 1.10
figure += H.legs(scn, M, HIP, spread=0.30 * H.stance(TIER), mat=BD,
                 boot=M["charcoal"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.68, 0.46, 0.26), BD, bevel=0.04))

# The Assassin stands taller than the rest: the crouch is the Rogue's tell, and
# a duellist who has outgrown skulking is a different person at a glance.
tors_root, tors = H.torso(scn, M, HIP + 0.12, chest_r=0.38,
                          lean={"common": 20, "rare": 8, "epic": 18, "legendary": 14}[TIER],
                          mat=BD)
tors.append(P.add_box(scn, "jerkin", (0, -0.12, 0.46), (0.76, 0.38, 0.60), BD, bevel=0.05))
tors.append(P.add_box(scn, "sash", (0, -0.06, 0.10), (0.80, 0.48, 0.16), AC))
tors.append(P.add_box(scn, "strap", (0, -0.30, 0.46), (0.84, 0.09, 0.12), AC,
                      rot=(0, math.radians(34), 0)))

if TIER == "rare":
    # a long coat split into tails, which is the only long garment in this line
    for s in (-1, 1):
        tors.append(P.add_box(scn, "coattail", (s * 0.22, 0.14, -0.34),
                              (0.32, 0.12, 0.86), BD,
                              rot=(0, math.radians(-s * 6), 0)))
    tors.append(P.add_box(scn, "collar", (0, -0.22, 0.76), (0.62, 0.26, 0.24), AC))
elif TIER == "epic":
    # spare throwing knives, the only hero carrying any. They ride the chest
    # strap, so they are torso-local and live in `tors`; written in `detail`
    # they rendered on his shin.
    for x, z in ((-0.14, 0.55), (-0.04, 0.48)):
        tors.append(P.add_box(scn, "throwknife", (x, -0.36, z),
                              (0.04, 0.05, 0.16), M["blade"]))
elif TIER == "legendary":
    # the Phantom trails rather than wears: rags, not a cloak with a hem.
    # ICE rags, not violet ones: violet rags on a violet body are invisible.
    # They hang off the hip line, so they are torso-local: in `detail` (figure
    # root) the same coordinates sat below the ground plane and rendered as a
    # detached strip under his feet.
    rags = S.tatters(scn, (0, 0.20, -0.30), 0.90, AC, count=7, drop=0.44, seed=9)
    tors += rags

if LEGEND:
    figure += H.cloak(scn, M, M["charcoal"], HIP + 0.48, height=1.46,
                      r_base=0.50, r_top=0.26, y=0.42)

# ---- the face, which is the whole point of this line ----
# The hooded tiers have NO skin head. A dark box laid across a skin face was the
# user's verdict 2026-08-02: "the masks on common and legendary don't work, it's
# just a black square over their face." What worked instead: the hood cone, a
# skull-back sphere and a dark void filling the opening, so the hood's OWN
# outline frames the shadow. Each hood is this tier's own build, not a shared
# part -- the Rogue's is snug and practical, the Phantom's deep and heavy.
dark_parts, glow_parts = [], []
if TIER == "common":
    hd_det = []
    tors += [P.add_cone(scn, "hoodpeak", (0, 0.04, 1.08), 0.43, 0.085, 0.53, BD, verts=10),
             P.add_sphere(scn, "hoodback", (0, 0.11, 0.98), 0.36, BD,
                          scale=(1.0, 0.95, 1.05), segs=10, rings=6),
             P.add_cone(scn, "cowl", (0, 0.0, 0.63), 0.48, 0.28, 0.29, BD, verts=10)]
    dark_parts.append(P.add_sphere(scn, "hoodvoid", (0, -0.17, 0.98), 0.22, M["dark"],
                                   scale=(0.92, 0.55, 1.0), segs=10, rings=6))
elif TIER == "rare":
    # a half-mask: eyes bare above it, the most of a face this line ever shows
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28)
    tors += hd
    tors.append(P.add_sphere(scn, "hair", (0, 0.08, 1.02), 0.31, M["charcoal"],
                             scale=(1.0, 1.06, 0.90), segs=12, rings=7))
    tors.append(P.add_box(scn, "halfmask", (0, -0.26, 0.84), (0.44, 0.18, 0.20), AC))
elif TIER == "epic":
    # no hood: cropped hair and a cloth pulled over the nose and mouth, with the
    # eyes left bare above it -- which is what the glow below lands on
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28)
    tors += hd
    tors.append(P.add_sphere(scn, "hair", (0, 0.05, 1.04), 0.30, M["charcoal"],
                             scale=(1.0, 1.0, 0.82), segs=12, rings=7))
    tors.append(P.add_box(scn, "maskcloth", (0, -0.24, 0.88), (0.50, 0.22, 0.26), AC))
    detail.append(P.add_box(scn, "masktie", (0.24, 0.16, 0.92), (0.12, 0.26, 0.12), AC))
else:
    # the Phantom: a hood over nothing. The void is the face.
    hd_det = []
    tors += [P.add_cone(scn, "hoodpeak", (0, 0.09, 1.10), 0.50, 0.07, 0.62, BD, verts=10),
             P.add_sphere(scn, "hoodback", (0, 0.16, 0.97), 0.40, BD,
                          scale=(1.0, 0.98, 1.10), segs=10, rings=6),
             P.add_cone(scn, "cowl", (0, 0.03, 0.56), 0.55, 0.32, 0.36, BD, verts=10)]
    dark_parts.append(P.add_sphere(scn, "hoodvoid", (0, -0.20, 0.98), 0.26, M["dark"],
                                   scale=(0.92, 0.50, 1.05), segs=10, rings=6))

# Eye glints sit on the FACE, so they are torso-local and belong in `tors` with
# their names passed through `skip_extra` (the README's torso-local rule). They
# used to go in `noline`, which parents to the FIGURE root, and rendered buried
# at hip height -- the paladin-visor bug again, never visible on any sheet.
if GLOW:
    if TIER == "epic":
        # bare eyes above the cloth mask. The mask's top edge reaches z 1.01, so
        # the glints sit at 1.05 rather than the half-mask's old 1.02, which the
        # taller cloth would have clipped.
        glow_parts += [P.add_box(scn, "eyeglint", (s * 0.095, -0.37, 1.05),
                                 (0.06, 0.04, 0.05), GLOW) for s in (-1, 1)]
    else:
        # two embers floating in the hood's void, proud of the dark so they read
        glow_parts += [P.add_box(scn, "eyeglint", (s * 0.10, -0.35, 1.00),
                                 (0.09, 0.04, 0.09), GLOW) for s in (-1, 1)]
tors += dark_parts + glow_parts

# ---- arms and grips: where the four silhouettes separate ----
# USER 2026-08-02: "the silhouette really hasn't changed at all throughout the
# progression" -- all four held both daggers in the identical place. The rejected
# fix (recorded in M15_ASSET_SPECS.md) picked four arm angles for outline shape
# alone and read as nonsense grips. So each pose here is a grip a knife fighter
# actually uses, and the outline change falls out of the stance:
#   common     the settled skulker's crouch, both blades low and close
#   rare       a duellist's line: long blade extended at chest height,
#              parry dagger raised close to the body
#   epic       a knife-fighter's guard: lead blade forward at the waist,
#              rear blade reversed at the hip
#   legendary  a wraith's drift: arms spread low, blades reversed,
#              points hanging down and out
for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.08, 0.62), 0.22, BD,
                             scale=(1, .95, .88)))

POSE = {
    #        elbow                  fist
    "rare": dict(
        L=((-0.56, -0.16, 0.28), (-0.44, -0.36, 0.70)),
        R=((0.51, -0.50, 0.48), (0.54, -0.92, 0.44)),
        dagL=((0, -14, 0), (-0.44, -0.38, 0.72)),
        dagR=((80, 0, 0), (0.54, -0.96, 0.44))),
    "epic": dict(
        L=((-0.58, 0.02, 0.22), (-0.48, -0.36, -0.02)),
        R=((0.50, -0.42, 0.30), (0.52, -0.86, 0.16)),
        dagL=((-168, 0, 0), (-0.48, -0.36, -0.06)),
        dagR=((82, 0, 0), (0.52, -0.90, 0.16))),
    "legendary": dict(
        L=((-0.64, -0.18, 0.26), (-0.86, -0.34, -0.06)),
        R=((0.64, -0.18, 0.26), (0.86, -0.34, -0.06)),
        dagL=((0, -160, 0), (-0.88, -0.34, -0.10)),
        dagR=((0, 160, 0), (0.88, -0.34, -0.10))),
}


def _arm(side, elbow, fist):
    """A posed arm whose every end cap is buried (the README limb rule): the
    upper's top inside the shoulder sphere, both elbow-side caps inside the
    elbow sphere, and the wrist inside the fist. The elbow sphere is named after
    the FOREARM deliberately: attack_roster's arm groups list upperL/foreL/fistL
    and `pixelrig.find` matches names before Blender's .001 suffix, so a second
    "foreL" travels with the arm where an "elbowL" would be left behind."""
    s = -1 if side == "L" else 1
    sh = (s * 0.46, -0.08, 0.62)
    return [S.aimed_cone(scn, "upper" + side, sh, elbow, 0.115, 0.10, BD, verts=8),
            P.add_sphere(scn, "fore" + side, elbow, 0.135, BD, segs=8, rings=5),
            S.aimed_cone(scn, "fore" + side, elbow, fist, 0.13, 0.10, BD, verts=8),
            P.add_sphere(scn, "fist" + side, fist, 0.14, M["skin"])]


if TIER == "common":
    # The settled Rogue arms, kept verbatim: hand-tuned tapers, no elbow sphere.
    # The shoulder grew from 0.19 to 0.22 for the same burial reason: at 0.19 it
    # did not reach over the upper arm and left a line across the shoulder.
    tors.append(P.add_cone(scn, "upperL", (-0.50, -0.14, 0.38), 0.10, 0.115, 0.46, BD, verts=8))
    tors.append(P.add_cone(scn, "foreL", (-0.51, -0.40, 0.015), 0.10, 0.13, 0.483, BD, verts=8,
                           rot=(math.radians(56.0), 0, math.radians(177))))
    tors.append(P.add_sphere(scn, "fistL", (-0.52, -0.60, -0.12), 0.14, M["skin"]))
    tors.append(P.add_cone(scn, "upperR", (0.50, -0.14, 0.40), 0.10, 0.115, 0.46, BD, verts=8))
    tors.append(P.add_cone(scn, "foreR", (0.50, -0.41, 0.055), 0.10, 0.13, 0.479, BD, verts=8,
                           rot=(math.radians(61.3), 0, math.radians(180))))
    tors.append(P.add_sphere(scn, "fistR", (0.50, -0.62, -0.06), 0.14, M["skin"]))
else:
    p = POSE[TIER]
    tors += _arm("L", *p["L"])
    tors += _arm("R", *p["R"])
    # Wrist bracers follow the FISTS: fixed coordinates left them stranded at
    # the common pose's wrists, rendering as boxes floating at the waist. Seat
    # each one a fifth of a forearm up-arm from the fist it belongs to.
    if TRIM:
        for side in ("L", "R"):
            (ex, ey, ez), (fx, fy, fz) = p[side]
            d = math.sqrt((ex - fx) ** 2 + (ey - fy) ** 2 + (ez - fz) ** 2)
            t = 0.20 / d
            tors.append(P.add_box(scn, "bracer",
                                  (fx + (ex - fx) * t, fy + (ey - fy) * t,
                                   fz + (ez - fz) * t),
                                  (0.26, 0.26, 0.20), TRIM))

curve = {
    "common":    [(-0.045, 0.0), (0.045, 0.0), (0.12, 0.32), (0.14, 0.58), (0.02, 0.70),
                  (0.02, 0.54), (-0.035, 0.30)],
    # a long single edge, straight back and a raked point
    "rare":      [(-0.040, 0.0), (0.055, 0.0), (0.075, 0.62), (0.055, 0.96),
                  (-0.010, 0.92), (-0.040, 0.44)],
    # a needle: no belly and no curve, so it reads as a puncture weapon
    "epic":      [(-0.035, 0.0), (0.035, 0.0), (0.040, 0.56), (0.0, 0.78), (-0.040, 0.56)],
    # wide and flared, the heaviest thing in the line
    "legendary": [(-0.060, 0.0), (0.060, 0.0), (0.175, 0.42), (0.140, 0.76),
                  (0.010, 0.90), (-0.050, 0.48)],
}[TIER]
# The Assassin fights long-and-short, which makes him the only hero in the
# roster holding a MISMATCHED pair. Everyone else carries twins.
SHORT = [(-0.035, 0.0), (0.048, 0.0), (0.058, 0.32), (0.020, 0.46), (-0.030, 0.28)]
if TIER == "common":
    spots = (("dagL_root", (0, 152, 0), (-0.54, -0.66, -0.14), curve),
             ("dagR_root", (0, 30, 0), (0.52, -0.68, -0.08), curve))
else:
    p = POSE[TIER]
    spots = (("dagL_root", p["dagL"][0], p["dagL"][1], SHORT if TIER == "rare" else curve),
             ("dagR_root", p["dagR"][0], p["dagR"][1], curve))
dagger_roots = []
for name, rot, loc, shape in spots:
    dr = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(dr, [P.add_prism(scn, "dagblade", shape, 0.05, M["blade"]),
                      P.add_box(scn, "daggrip", (0, 0, -0.12), (0.07, 0.07, 0.22), AC),
                      P.add_box(scn, "dagguard", (0, 0, 0.02), (0.18, 0.08, 0.05),
                                TRIM or M["steel"])])
    dagger_roots.append(dr)
P.parent_all(tors_root, tors + hd_det + dagger_roots)

H.finish(scn, px, "hero_assassin", figure, detail, noline,
         roots=[tors_root],
         skip_extra=tuple(o.name for o in hd_det + dark_parts + glow_parts + rags),
         body_roots=[tors_root])
