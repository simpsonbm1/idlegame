"""Bandit Horde parts, M15_ASSET_SPECS.md entries 28-33.

Family rules from that doc: "human outlaws, worn browns and muted red cloth,
leather armor, hoods and masks". Enemies face LEFT.

**These are the first HUMAN enemies, which is the family's real problem.** The
goblins and orcs are told apart from the player's side by being green; a bandit
has the same build and the same skin as the knight defending the wall. So the
faction is carried by three things that are all about the head and the value
range, not the body:

1. Every one of them covers his face -- hood, scarf, mask or all three. The
   heroes' faces are open. That is the fastest read on a battlefield.
2. Muted browns and one muted red, against the heroes' saturated steel-blue and
   gold. The palettes never overlap.
3. Nothing they wear fits. Patched brigandine and wrapped rags, never plate.

The covered face is doing most of the work, so no bandit gets a bare head, not
even the boss -- his crown sits above a scarf.
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


def palette():
    return {
        # Worn browns, the family's bulk -- but SPREAD ACROSS THE VALUE RANGE, not
        # clustered. The first pass gave leather, coat and skin nearly the same
        # warm brown, so every head merged into its hood and the six of them read
        # as one tan smear. Coat is now the darkest thing they wear and skin the
        # lightest, with leather between.
        "coat":  P.toon_mat("BCOAT", "#241d14", "#3c3122", "#584a33"),
        "leath": P.toon_mat("BLEATHER", "#3c2a1a", "#63472c", "#8a6742"),
        "rag":   P.toon_mat("BRAG", "#33302a", "#514c42", "#756d5f"),
        # the one muted red: sashes, scarves, medicine
        "red":   P.toon_mat("BRED", "#6b2823", "#9e4133", "#c86a52"),
        # human skin. It has to be the LIGHTEST tone on the figure, because a
        # covered face is the family's whole read and a face only reads as one
        # when it is brighter than what is wrapped around it.
        "skin":  P.toon_mat("BSKIN", "#7d5638", "#b0805a", "#dcae83"),
        "steel": P.toon_mat("BSTEEL", "#4a4e56", "#71767f", "#9ba0ac"),
        "iron":  P.toon_mat("BIRON", "#38302a", "#574b41", "#7a6b5d"),
        "wood":  P.toon_mat("BWOOD", "#3d2a16", "#5e4222", "#835f36"),
        "gold":  P.toon_mat("BGOLD", "#7a5c15", "#b8912c", "#e6c65c"),
        "cloth": P.toon_mat("BCLOTH", "#4a4437", "#6e6752", "#948c72"),
        "fire":  P.flat_mat("BFIRE", "#ffb03a"),
        "fire_d": P.flat_mat("BFIREDIM", "#c26418"),
        "tonic": P.flat_mat("BTONIC", "#ff5546"),
        "dark":  P.flat_mat("BDARK", "#14110d"),
    }


def head(scn, M, loc, r=0.30, cover="scarf", hood=True):
    """A human head with its face covered. `cover` is "scarf", "mask" or None.

    Returns (figure, detail). The covering is a figure part and gets an outline,
    because it has to survive as a shape; the eyes above it are detail.

    A hood is built as a shell that stands PROUD of the skull and sits BACK from
    it. Sized to just clear the head it renders entirely behind the face and the
    figure comes out bare-headed, which is the mistake the goblin skulker made.
    """
    x, y, z = loc
    fig = [P.add_sphere(scn, "bhead", (x, y, z), r, M["skin"],
                        scale=(0.94, 1.0, 1.08), segs=10, rings=7)]
    det = []
    # The covering is a BAND across the lower face, not a box wrapped round the
    # whole head. Sized to the skull it swallowed the face entirely and the head
    # came out as a featureless wedge with a stripe on it.
    if cover == "scarf":
        fig.append(P.add_box(scn, "bscarf", (x, y - r * 0.50, z - r * 0.46),
                             (r * 1.72, r * 1.02, r * 0.62), M["red"], bevel=0.03))
    elif cover == "mask":
        fig.append(P.add_box(scn, "bmask", (x, y - r * 0.54, z - r * 0.42),
                             (r * 1.64, r * 0.96, r * 0.66), M["rag"], bevel=0.03))
    # **The brow is a SHADOW, not a skin-coloured ledge.** Built in skin and stood
    # proud of the face it simply extended the pale mass forward, and every
    # bandit came out with what read as a beak. Dark, it does the opposite job:
    # it caps the face and gives the eyes a band to sit in.
    det.append(P.add_box(scn, "bbrow", (x, y - r * 0.92, z + r * 0.50),
                         (r * 1.66, r * 0.20, r * 0.30), M["dark"]))
    for s in (-1, 1):
        # pushed clear of the skull. Flush with the sphere's front they were
        # inside it, and at two pixels across nothing showed at all.
        det.append(P.add_box(scn, "beye", (x + s * r * 0.34, y - r * 1.14, z + r * 0.20),
                             (r * 0.36, r * 0.10, r * 0.24), M["dark"]))
    if hood:
        # A margin around the face and a shell behind it, both in the DARKEST
        # material on the figure. A hood the same tone as the skin under it is
        # not a hood, it is a bigger head.
        fig.append(P.add_cone(scn, "bhood", (x, y + r * 0.34, z + r * 0.40),
                              r * 1.30, r * 0.34, r * 1.58, M["coat"], verts=10))
        fig.append(P.add_sphere(scn, "bhoodback", (x, y + r * 0.46, z + r * 0.02),
                                r * 1.06, M["coat"], scale=(1.0, 0.88, 1.0), segs=10, rings=6))
        fig.append(P.add_cone(scn, "bcowl", (x, y + r * 0.22, z - r * 1.24),
                              r * 1.42, r * 0.86, r * 0.96, M["coat"], verts=10))
    return fig, det


def lean_legs(scn, M, hip_z, spread=0.34, mat=None):
    """Ordinary human legs in wrapped boots. Narrower than an orc's and wider
    than a goblin's, which is most of what makes the family read as people."""
    mat = mat or M["leath"]
    out = []
    for s, yoff in ((-1, -0.24), (1, 0.22)):
        out.append(P.add_box(scn, "bboot", (s * spread, yoff - 0.10, 0.13),
                             (0.38, 0.62, 0.26), mat, bevel=0.04))
        out.append(P.add_cyl(scn, "bshin", (s * spread, yoff, hip_z * 0.36),
                             0.155, hip_z * 0.50, mat, verts=8))
        out.append(P.add_box(scn, "bwrap", (s * spread, yoff, hip_z * 0.56),
                             (0.34, 0.36, 0.16), M["rag"]))
        out.append(P.add_cyl(scn, "bthigh", (s * spread * 0.94, yoff * 0.6, hip_z * 0.78),
                             0.185, hip_z * 0.44, mat, verts=8))
    return out


def torso(scn, M, hip_z, chest_r=0.44, lean=8, mat=None):
    """A human torso on its own root. Returns (root, parts)."""
    mat = mat or M["coat"]
    root = P.make_root(scn, "torso_root", rot=(-lean, 0, 0), loc=(0, 0, hip_z))
    parts = [P.add_cyl(scn, "bwaist", (0, 0, 0.12), 0.33, 0.34, mat, verts=10,
                       scale=(1.10, 0.82, 1)),
             P.add_sphere(scn, "bchest", (0, -0.04, 0.50), chest_r, mat,
                          scale=(1.22, 0.84, 0.92), segs=12, rings=8)]
    return root, parts


def patches(scn, M, loc, count=3, seed=0):
    """Mismatched squares stitched onto worn gear. Nothing a bandit owns fits or
    matches, and at sprite size that has to be a few hard-edged blocks of a
    different tone rather than any kind of texture."""
    x, y, z = loc
    out = []
    mats = (M["rag"], M["red"], M["cloth"])
    for i in range(count):
        dx = ((i * 5 + seed) % 7) / 7.0 - 0.5
        dz = ((i * 3 + seed) % 5) / 5.0 - 0.5
        w = 0.13 + 0.05 * (((i * 2 + seed) % 3) / 2.0)
        out.append(P.add_box(scn, "bpatch", (x + dx * 0.66, y, z + dz * 0.60),
                             (w, 0.05, w * 0.88), mats[(i * 2 + seed) % 3]))
    return out


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACING, role=None, body_roots=()):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra,
                    facing, role, body_roots)
