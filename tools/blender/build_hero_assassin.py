"""Assassin -- M15_ASSET_SPECS.md entry 5.

  "a slim hooded assassin in dark charcoal-and-purple leathers, face in shadow,
   slightly crouched, twin curved daggers held low"

The one hero whose face is NOT open, which would normally break the rule that
separates heroes from bandits. He gets away with it because his palette is
charcoal and violet where every bandit is brown, and because he is the only
crouched hero -- two differences carrying the load one usually does.

His daggers are held LOW and close, against the goblin skulker's low-and-forward
and the undead reaver's wide. Three twin-blade figures, three poses.

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
# you can see: a shadowed hood, a cloth mask under cropped hair, a half-mask with
# the eyes bare, and finally nothing at all behind a glowing void. The blade
# shape carries the rest -- curved kris, straight stiletto, long single edge,
# wide flared. He is the only hero holding two of anything, so the pair reads.
# ---------------------------------------------------------------------------
TIER = H.tier()
if TIER == "base":
    TIER = "common"

ACCENT = {"common": "violet", "rare": "crimson", "epic": "azure",
          "legendary": "violet"}[TIER]
AC = M[ACCENT]

figure, detail, noline = [], [], []

HIP = 1.10
figure += H.legs(scn, M, HIP, spread=0.30 * H.stance(TIER), mat=M["charcoal"],
                 boot=M["charcoal"])
figure.append(P.add_box(scn, "hips", (0, 0, HIP), (0.68, 0.46, 0.26), M["charcoal"], bevel=0.04))

# The Nightblade stands taller than the rest: the crouch is the Rogue's tell, and
# a duellist who has outgrown skulking is a different person at a glance.
tors_root, tors = H.torso(scn, M, HIP + 0.12, chest_r=0.38,
                          lean={"common": 20, "rare": 18, "epic": 8, "legendary": 14}[TIER],
                          mat=M["charcoal"])
tors.append(P.add_box(scn, "jerkin", (0, -0.12, 0.46), (0.76, 0.38, 0.60), M["charcoal"], bevel=0.05))
tors.append(P.add_box(scn, "sash", (0, -0.06, 0.10), (0.80, 0.48, 0.16), AC))
tors.append(P.add_box(scn, "strap", (0, -0.30, 0.46), (0.84, 0.09, 0.12), AC,
                      rot=(0, math.radians(34), 0)))

if TIER == "rare":
    # a bandolier of throwing knives: the only hero carrying spare weapons
    for i, z in enumerate((0.30, 0.46, 0.62)):
        detail.append(P.add_box(scn, "throwknife", (-0.16 + i * 0.10, -0.40, z),
                                (0.05, 0.06, 0.20), M["blade"]))
elif TIER == "epic":
    # a long coat split into tails, which is the only long garment in this line
    for s in (-1, 1):
        tors.append(P.add_box(scn, "coattail", (s * 0.22, 0.14, -0.34),
                              (0.32, 0.12, 0.86), M["charcoal"],
                              rot=(0, math.radians(-s * 6), 0)))
    tors.append(P.add_box(scn, "collar", (0, -0.22, 0.76), (0.62, 0.26, 0.24), AC))
elif TIER == "legendary":
    # the Phantom trails rather than wears: rags, not a cloak with a hem
    detail += S.tatters(scn, (0, 0.20, -0.30), 0.90, M["violet"], count=7, drop=0.44, seed=9)

if TRIM:
    for s in (-1, 1):
        tors.append(P.add_box(scn, "bracer", (s * 0.48, -0.44, 0.06), (0.26, 0.26, 0.20), TRIM))
if LEGEND:
    figure += H.cloak(scn, M, M["violet"], HIP + 0.48, height=1.46,
                      r_base=0.50, r_top=0.26, y=0.42)

# ---- the face, which is the whole point of this line ----
if TIER == "common":
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28, hood=M["charcoal"], shadowed=True)
    tors += hd
    # the face in shadow: a dark band where the eyes would be, which is the entry
    tors.append(P.add_box(scn, "faceshadow", (0, -0.28, 0.98), (0.36, 0.10, 0.24), M["dark"]))
elif TIER == "rare":
    # no hood: cropped hair and a cloth pulled over the nose and mouth
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28)
    tors += hd
    tors.append(P.add_sphere(scn, "hair", (0, 0.05, 1.04), 0.30, M["charcoal"],
                             scale=(1.0, 1.0, 0.82), segs=12, rings=7))
    tors.append(P.add_box(scn, "maskcloth", (0, -0.24, 0.88), (0.50, 0.22, 0.26), M["charcoal"]))
    detail.append(P.add_box(scn, "masktie", (0.24, 0.16, 0.92), (0.12, 0.26, 0.12), AC))
elif TIER == "epic":
    # a half-mask: eyes bare above it, which is the only lit face in the line
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28)
    tors += hd
    tors.append(P.add_sphere(scn, "hair", (0, 0.08, 1.02), 0.31, M["charcoal"],
                             scale=(1.0, 1.06, 0.90), segs=12, rings=7))
    tors.append(P.add_box(scn, "halfmask", (0, -0.26, 0.84), (0.44, 0.18, 0.20), AC))
else:
    # the Phantom: a hood over nothing. The void is the face.
    hd, hd_det = H.head(scn, M, (0, -0.04, 0.98), r=0.28, hood=M["charcoal"], shadowed=True)
    tors += hd
    tors.append(P.add_box(scn, "faceshadow", (0, -0.28, 0.98), (0.40, 0.10, 0.30), M["dark"]))

if GLOW:
    EYE = (0.06, 0.04, 0.05) if TIER == "epic" else (0.09, 0.04, 0.09)
    noline += [P.add_box(scn, "eyeglint", (s * 0.09, -0.32, 1.00), EYE, GLOW)
               for s in (-1, 1)]

for s in (-1, 1):
    tors.append(P.add_sphere(scn, "shoulder", (s * 0.46, -0.08, 0.62), 0.19, M["charcoal"],
                             scale=(1, .95, .88)))
tors.append(P.add_cyl(scn, "upperL", (-0.50, -0.20, 0.38), 0.135, 0.44, M["charcoal"], verts=8))
tors.append(P.add_cyl(scn, "foreL", (-0.52, -0.46, 0.08), 0.12, 0.44, M["charcoal"], verts=8,
                      rot=(math.radians(40), 0, 0)))
tors.append(P.add_sphere(scn, "fistL", (-0.52, -0.60, -0.12), 0.14, M["skin"]))
tors.append(P.add_cyl(scn, "upperR", (0.50, -0.20, 0.40), 0.135, 0.44, M["charcoal"], verts=8))
tors.append(P.add_cyl(scn, "foreR", (0.50, -0.48, 0.14), 0.12, 0.44, M["charcoal"], verts=8,
                      rot=(math.radians(46), 0, 0)))
tors.append(P.add_sphere(scn, "fistR", (0.50, -0.62, -0.06), 0.14, M["skin"]))

curve = {
    "common":    [(-0.045, 0.0), (0.045, 0.0), (0.12, 0.32), (0.14, 0.58), (0.02, 0.70),
                  (0.02, 0.54), (-0.035, 0.30)],
    # a needle: no belly and no curve, so it reads as a puncture weapon
    "rare":      [(-0.035, 0.0), (0.035, 0.0), (0.040, 0.56), (0.0, 0.78), (-0.040, 0.56)],
    # a long single edge, straight back and a raked point
    "epic":      [(-0.040, 0.0), (0.055, 0.0), (0.075, 0.62), (0.055, 0.96),
                  (-0.010, 0.92), (-0.040, 0.44)],
    # wide and flared, the heaviest thing in the line
    "legendary": [(-0.060, 0.0), (0.060, 0.0), (0.175, 0.42), (0.140, 0.76),
                  (0.010, 0.90), (-0.050, 0.48)],
}[TIER]
dagger_roots = []
for name, rot, loc in (("dagL_root", (0, 152, 0), (-0.54, -0.66, -0.14)),
                       ("dagR_root", (0, 30, 0), (0.52, -0.68, -0.08))):
    dr = P.make_root(scn, name, rot=rot, loc=loc)
    P.parent_all(dr, [P.add_prism(scn, "dagblade", curve, 0.05, M["blade"]),
                      P.add_box(scn, "daggrip", (0, 0, -0.12), (0.07, 0.07, 0.22), AC),
                      P.add_box(scn, "dagguard", (0, 0, 0.02), (0.18, 0.08, 0.05),
                                TRIM or M["steel"])])
    dagger_roots.append(dr)
P.parent_all(tors_root, tors + hd_det + dagger_roots)

H.finish(scn, px, "hero_assassin", figure, detail, noline,
         roots=[tors_root], skip_extra=tuple(o.name for o in hd_det),
         body_roots=[tors_root])
