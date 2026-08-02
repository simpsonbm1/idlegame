"""Fighter -- M15_ASSET_SPECS.md entry 1.

  "a hardened human footman soldier in a chainmail shirt, open-faced kettle
   helmet, and red-and-steel tabard, gripping a longsword in both hands"

The rank-and-file soldier, and the hero closest to the guardian knight, so the
two are separated the way real infantry differ from real knights: MAIL rather
than plate, a brimmed open helmet rather than a great helm, and a tabard rather
than a surcoat over armour.

His sword is held in both hands down the centre line, which is the most stable
silhouette in the roster and right for the unit a player sees most.

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
# The fighter line: Footman, Sellsword, Blademaster, Warlord (DESIGN.md).
#
# Four soldiers from four different places, not one footman re-equipped (USER
# RULING 2026-08-01). The blade carries most of it, because a sword held down the
# centre line is the tallest thin object this figure owns: a plain arming sword,
# a broad falchion, a long slender duelling blade, a massive war sword. Then the
# head, and then the armour underneath.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

# USER REVIEW 2026-08-01: the common used to be mail under a trimmed tabard with
# a steel helm, and read as a HIGHER tier than the rare and the epic. The bottom
# of this ladder came down rather than the top going up, so escalation now runs
# through armour: a padded gambeson, a brigandine with one looted pauldron,
# lamellar over a dark under-layer, then full mail beneath a tabard.
# The four torso values are also four different values -- pale cloth, brown
# leather, near-black, grey steel -- so the tiers separate at sprite scale and
# not only blown up on a contact sheet.
BODY = {"common": "cream", "rare": "leath", "epic": "charcoal", "legendary": "mail"}[TIER]
COAT = {"common": "leath", "rare": "crimson", "epic": "violet", "legendary": "crimson"}[TIER]
# An arm must be one connected mass in a different value from whatever it sits in
# front of, or the forearm reads as a floating blob (user, 2026-08-01).
ARM = {"common": "leath", "rare": "mail", "epic": "mail", "legendary": "steel"}[TIER]
CUFF = {"common": "leath", "rare": "steel", "epic": "steel", "legendary": "steel"}[TIER]

figure, detail, noline = [], [], []

HIP = 1.18
figure += H.legs(scn, M, HIP, spread=0.34 * H.stance(TIER), mat=M[BODY], boot=M["leath"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.80, 0.52, 0.30), M[BODY], bevel=0.05))

CHEST = {"common": 0.46, "rare": 0.44, "epic": 0.42, "legendary": 0.52}[TIER]
tors_root, tors = H.torso(scn, M, HIP + 0.14, chest_r=CHEST, lean=6, mat=M[BODY])
# Anything worn on the chest has to clear the chest SPHERE. At the old y=-0.32
# the sphere pushed through the middle of the tabard and one garment rendered as
# two floating red patches with grey between them.
FRONT = -(CHEST + 0.06)
if LEGEND:
    tors.append(P.add_box(scn, "tabard", (0, FRONT, 0.34), (0.50, 0.08, 1.10), M[COAT]))
    tors.append(P.add_box(scn, "tabardback", (0, 0.30, 0.34), (0.50, 0.08, 1.10), M[COAT]))
elif TIER == "common":
    # the Footman: a padded gambeson, a rope belt and no livery at all. He is the
    # poorest figure in the line and has to look it.
    tors.append(P.add_box(scn, "gambesonseam", (0, FRONT, 0.36), (0.16, 0.07, 1.06), M[COAT]))
    for i, z in enumerate((0.10, 0.44, 0.78)):
        tors.append(P.add_box(scn, "quilt%d" % i, (0, FRONT + 0.01, z), (0.74, 0.05, 0.07),
                              M[COAT]))
elif TIER == "rare":
    # the Sellsword: mismatched kit, one shoulder plated and the other bare. He
    # is the only fighter in the line who is not symmetrical.
    tors.append(P.add_sphere(scn, "pauldron", (-0.60, -0.10, 0.80), 0.32, M["steel"],
                             scale=(1.10, 0.88, 0.72), segs=10, rings=6))
    tors.append(P.add_box(scn, "baldric", (0, FRONT, 0.44), (0.96, 0.10, 0.16), M[COAT],
                          rot=(0, math.radians(28), 0)))
else:
    # the Blademaster: lamellar plates laced over a near-black under-layer. He
    # used to wear a sash and nothing else, which put him BELOW the Sellsword's
    # brigandine on a ladder he is supposed to sit above.
    for i, z in enumerate((0.26, 0.54, 0.82)):
        tors.append(P.add_box(scn, "lamellar%d" % i, (0, FRONT, z), (0.94, 0.09, 0.22),
                              M["steel"]))
    tors.append(P.add_box(scn, "sash", (0, FRONT, 0.02), (0.94, 0.14, 0.26), M[COAT],
                          rot=(0, math.radians(-18), 0)))
    tors.append(P.add_box(scn, "sashtail", (0.34, FRONT, -0.34), (0.18, 0.10, 0.54), M[COAT]))
tors.append(P.add_box(scn, "belt", (0, -0.04, 0.10), (0.92, 0.56, 0.15), M["leath"]))
if TRIM and LEGEND:
    tors.append(P.add_box(scn, "tabardedge", (0, FRONT - 0.03, 0.34), (0.13, 0.05, 1.10), TRIM))
    tors.append(P.add_box(scn, "pauldrontrim", (0, -0.30, 0.78), (0.98, 0.10, 0.11), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["crimson"], HIP + 0.56, height=1.62,
                      r_base=0.62, r_top=0.32, y=0.46)

# ---- the head is the second read, and no two of them are the same shape ----
# It escalates too: nothing, then cloth, then a warrior's knot, then a great helm.
if TIER == "common":
    # the Footman owns no helmet. Cropped hair, and that is the whole of it.
    hd, hd_det = H.head(scn, M, (0, -0.04, 1.06), r=0.30)
    tors += hd
    tors.append(P.add_sphere(scn, "crop", (0, 0.02, 1.14), 0.31, M["leath"],
                             scale=(1.0, 1.0, 0.78), segs=12, rings=7))
elif TIER == "rare":
    # bare head, bandana and stubble: a soldier who owns no helmet
    hd, hd_det = H.head(scn, M, (0, -0.04, 1.06), r=0.30)
    tors += hd
    # Two ways this band goes wrong, both seen on a render. Wider than the head
    # it reads as a plank laid across the skull; level with the eyes it reads as
    # a blindfold. It belongs on the FOREHEAD, and the head sphere is only 0.46
    # across up there, so the box has to shrink to match.
    tors.append(P.add_box(scn, "bandana", (0, -0.04, 1.25), (0.46, 0.44, 0.13), M[COAT]))
    tors.append(P.add_box(scn, "bandanatail", (0.22, 0.20, 1.12), (0.11, 0.24, 0.28), M[COAT],
                          rot=(math.radians(24), 0, 0)))
    detail.append(P.add_box(scn, "stubble", (0, -0.30, 0.90), (0.32, 0.20, 0.18), M["charcoal"]))
elif TIER == "epic":
    # bare head, topknot: the only hair standing UP on any hero
    hd, hd_det = H.head(scn, M, (0, -0.04, 1.06), r=0.30)
    tors += hd
    tors.append(P.add_sphere(scn, "hair", (0, 0.06, 1.12), 0.33, M["charcoal"],
                             scale=(1.0, 1.02, 0.92), segs=12, rings=7))
    tors.append(P.add_cone(scn, "topknot", (0, 0.16, 1.44), 0.10, 0.05, 0.42,
                           M["charcoal"], rot=(math.radians(-18), 0, 0), verts=7))
else:
    # the Warlord: horned helm, face in shadow
    hd, hd_det = H.head(scn, M, (0, -0.04, 1.06), r=0.30, helm=M["steel"])
    tors += hd
    for s in (-1, 1):
        tors.append(P.add_cone(scn, "warhorn", (s * 0.32, 0.04, 1.30), 0.12, 0.0, 0.56,
                               M["brightgold"], rot=(0, math.radians(-s * 42), 0), verts=7))
if GLOW:
    noline.append(P.add_box(scn, "helmcrest", (0, 0.06, 1.44), (0.10, 0.30, 0.18), GLOW))

for s in (-1, 1):
    # Forward of the old y=-0.08 and slightly larger, so it actually swallows the
    # upper arm's top cap. It did not, and that cap's rim drew the one dark line
    # still crossing the arm after the segments were tapered.
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.54, -0.14, 0.68), 0.25, M[ARM],
                             scale=(1, .95, .88)))
# The whole arm is steel, not mail. A mail upper arm is the same value as a mail
# torso, so it vanished into the chest and left the steel forearms reading as two
# floating blobs with outlines all the way round -- the "disjointed arms" the
# developer saw (user, 2026-08-01). An arm has to be one connected mass in a
# different value from whatever it is in front of.
# The forearm tilts elbow-BACK, wrist-FORWARD, so its X rotation is negative:
# positive put the elbow in front of the wrist and zigzagged the limb.
# ---------------------------------------------------------------------------
# THE ARM IS TAPERED CONES, NOT CYLINDERS, AND THAT IS NOT A STYLE CHOICE.
#
# The outline is a per-object inverted hull (`pixelrig.outline`). Every part's
# end CAP therefore carries its own dark shell, and a cap sitting in open air
# draws a line straight across the limb. Four parts in a row gave the developer
# "upper arm, joint 1, another arm segment, joint 2, another arm segment, joint
# 3, another arm segment, hand" (user, 2026-08-01).
#
# Adding an elbow sphere makes it WORSE, not better: one more part is one more
# line. It also breaks the attack sheet, because `animkit.twohand_sheet` solves
# this arm with IK and poses only `upper`, `fore` and `hand` -- a separate elbow
# would stay put while the rest of the arm swung away from it.
#
# The fix is that each segment ENDS NARROWER THAN THE PIECE THAT SWALLOWS IT.
# The shoulder sphere buries the upper arm's top, the forearm's wide elbow mouth
# sleeves over the upper arm's narrow bottom, and the fist buries the wrist. No
# cap is left in open air, so the only dark line is the true silhouette.
# ---------------------------------------------------------------------------
tors.append(P.add_cone(scn, "upperL", (-0.56, -0.20, 0.42), 0.10, 0.155, 0.52, M[ARM],
                       verts=8))
tors.append(P.add_cone(scn, "foreL", (-0.4525, -0.44, 0.03), 0.115, 0.155, 0.613, M[CUFF],
                       verts=8, rot=(math.radians(41.4), 0, math.radians(-152.6))))
tors.append(P.add_sphere(scn, "fistL", (-0.36, -0.62, -0.20), 0.155, M[CUFF]))
tors.append(P.add_cone(scn, "upperR", (0.56, -0.20, 0.44), 0.10, 0.155, 0.50, M[ARM],
                       verts=8))
tors.append(P.add_cone(scn, "foreR", (0.4325, -0.45, 0.07), 0.115, 0.155, 0.609, M[CUFF],
                       verts=8, rot=(math.radians(46.4), 0, math.radians(149.4))))
tors.append(P.add_sphere(scn, "fistR", (0.32, -0.64, -0.14), 0.155, M[CUFF]))
P.parent_all(tors_root, tors + hd_det)

# Four blades. A falchion is wide at the tip and a duelling blade is narrow the
# whole way, and those two outlines are unmistakable even at 112 pixels.
BLADE = {
    "common":    [(-0.07, 0.14), (0.07, 0.14), (0.07, 1.24), (0.0, 1.50), (-0.07, 1.24)],
    "rare":      [(-0.06, 0.14), (0.09, 0.14), (0.19, 0.86), (0.17, 1.16),
                  (0.02, 1.26), (-0.07, 0.92)],
    "epic":      [(-0.045, 0.14), (0.045, 0.14), (0.045, 1.54), (0.0, 1.82), (-0.045, 1.54)],
    "legendary": [(-0.13, 0.14), (0.13, 0.14), (0.13, 1.30), (0.0, 1.64), (-0.13, 1.30)],
}[TIER]
blade = BLADE
sw_root = P.make_root(scn, "sword_root", rot=(0, 6, 0), loc=(-0.02, -0.80, 1.02))
sword = [P.add_prism(scn, "blade", blade, 0.11, M["blade"]),
         P.add_box(scn, "guard", (0, 0, 0.12), (0.46, 0.11, 0.10), TRIM or M["steel"]),
         P.add_box(scn, "grip", (0, 0, -0.10), (0.11, 0.10, 0.26), M["leath"]),
         P.add_sphere(scn, "pommel", (0, 0, -0.26), 0.10, TRIM or M["steel"])]
P.parent_all(sw_root, sword)

H.finish(scn, px, "hero_fighter", figure, detail, noline,
         roots=[tors_root, sw_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
