"""Goblin Raid parts, M15_ASSET_SPECS.md entries 17-21 (plus the existing brute).

Family rules from that doc: "small wiry hunched builds -- noticeably smaller than
the big goblin brute from earlier -- mossy yellow-green skin, ragged mismatched
leather scraps, crude rusty iron". Enemies face LEFT.

**The size rule is the family's whole identity and it is a WORLD-HEIGHT rule, not
a fill-fraction one.** Every sprite shares `SPRITE_PX`, so how large a figure
reads on screen is decided by how tall it is in world units and by nothing else.
The brute stands 3.3 units; the commons here stand about 2.5, which is what
"noticeably smaller" has to mean when the camera is locked. Their 96 cell then
has headroom above them, and that is correct rather than wasteful -- fitting them
to 80% of the cell the way the generator brief asks would have silently made them
the same size as the brute.

The palette is lifted unchanged from `build_goblin.py`, the family's pilot, plus
one addition: the commons carry rusted iron where the brute carries plain grey,
which the spec asks for and which also separates the mob from its heavy.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S

start = S.start
tatters = S.tatters
FACING = S.FACE_LEFT

COMMON_HEIGHT = 2.5     # world units, against the brute's 3.3


def palette():
    return {
        "skin":  P.toon_mat("SKIN", "#3d6b2e", "#5f9440", "#8ec25c"),
        "leath": P.toon_mat("GLEATHER", "#4a3520", "#7a5638", "#a3764c"),
        "wood":  P.toon_mat("WOOD", "#4a3018", "#6f4a24", "#96693a"),
        "iron":  P.toon_mat("IRON", "#5c5c58", "#8b8b84", "#bcbcb4"),
        # "crude rusty iron": the commons' gear against the brute's plain grey.
        "rust":  P.toon_mat("CRUDEIRON", "#57402f", "#7d6046", "#a08462"),
        "tusk":  P.toon_mat("TUSK", "#b09a6a", "#d8c99a", "#f2e8c8"),
        "rag":   P.toon_mat("GRAG", "#3b3324", "#5c5138", "#807253"),
        "bone":  P.toon_mat("GBONE", "#a89a7c", "#d8ceb0", "#f4eeda"),
        "green": P.flat_mat("GCHARM", "#8cff7a"),
        "green_d": P.flat_mat("GCHARMDIM", "#3f8f3a"),
        "fire":  P.flat_mat("GFIRE", "#ffcc55"),
        "fire_d": P.flat_mat("GFIREDIM", "#c07a22"),
        "dark":  P.flat_mat("GDARK", "#141a12"),
    }


def head(scn, M, loc, r=0.34, ears=True, tusks=True):
    """The family face: heavy jaw, brow ridge, tusks, big pointed ears.

    Returns (figure, detail). The EARS are the family's read at sprite size --
    they break the head's silhouette in a way no amount of facial detail does, so
    they are figure parts and get outlined, while the brow and eyes are detail and
    do not.
    """
    x, y, z = loc
    fig = [P.add_sphere(scn, "gskull", (x, y - 0.02, z), r, M["skin"],
                        scale=(1.06, 1.0, 0.98), segs=12, rings=8),
           P.add_box(scn, "gjaw", (x, y - r * 0.60, z - r * 0.52),
                     (r * 1.48, r * 1.04, r * 0.68), M["skin"], bevel=0.05)]
    det = [P.add_box(scn, "gbrow", (x, y - r * 0.88, z + r * 0.28),
                     (r * 1.56, r * 0.32, r * 0.28), M["skin"]),
           P.add_box(scn, "gmouth", (x, y - r * 1.12, z - r * 0.48),
                     (r * 1.04, r * 0.10, r * 0.14), M["dark"])]
    for s in (-1, 1):
        det.append(P.add_box(scn, "geye", (x + s * r * 0.38, y - r * 0.96, z + r * 0.04),
                             (r * 0.26, r * 0.10, r * 0.20), M["dark"]))
        if tusks:
            det.append(P.add_cone(scn, "gtusk", (x + s * r * 0.44, y - r * 1.10, z - r * 0.36),
                                  r * 0.15, 0.0, r * 0.60, M["tusk"], verts=6))
        if ears:
            fig.append(P.add_cone(scn, "gear", (x + s * r * 1.00, y + 0.04, z + r * 0.20),
                                  r * 0.34, 0.0, r * 1.08, M["skin"],
                                  rot=(0, math.radians(s * 68), 0), verts=6))
    return fig, det


def wiry_legs(scn, M, hip_z, spread=0.30, mat=None):
    """Thin bent legs with a foot, one forward. Wiry is thin limbs plus a WIDE
    stance: the gap between the legs is what stops a small figure reading as a
    lump."""
    mat = mat or M["skin"]
    out = []
    for s, yoff in ((-1, -0.20), (1, 0.18)):
        out.append(P.add_box(scn, "gfoot", (s * spread, yoff - 0.10, 0.10),
                             (0.34, 0.52, 0.20), mat, bevel=0.03))
        out.append(P.add_cyl(scn, "gshin", (s * spread, yoff, hip_z * 0.36),
                             0.115, hip_z * 0.52, mat, verts=8))
        out.append(P.add_box(scn, "gwrap", (s * spread, yoff, hip_z * 0.22),
                             (0.28, 0.30, 0.16), M["leath"]))
        out.append(P.add_cyl(scn, "gthigh", (s * spread * 0.92, yoff * 0.6, hip_z * 0.76),
                             0.135, hip_z * 0.46, mat, verts=8))
    return out


def hunch(scn, M, hip_z, chest_r=0.34, lean=18):
    """The family posture: a torso root pitched forward.

    Every common goblin is hunched, and a hunch has to be a ROOT rotation rather
    than a set of tilted parts, or the head and arms hung off it stop agreeing
    with the spine. Returns (root, parts) -- add more parts to the list and
    parent them yourself.
    """
    root = P.make_root(scn, "torso_root", rot=(-lean, 0, 0), loc=(0, 0, hip_z))
    parts = [P.add_cyl(scn, "gwaist", (0, 0, 0.10), 0.30, 0.30, M["skin"], verts=10,
                       scale=(1.10, 0.82, 1)),
             P.add_sphere(scn, "gchest", (0, -0.04, 0.42), chest_r, M["skin"],
                          scale=(1.22, 0.84, 0.88), segs=12, rings=8)]
    return root, parts


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACING):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra, facing)
