"""Undead Legion parts, M15_ASSET_SPECS.md entries 34-39.

Family rules from that doc: "pale bone and gray dead flesh, ancient rusted
armor, glowing spectral teal-violet accents -- keep overall values mid-bright,
bone reads bright". Enemies face LEFT.

A family is one body plan plus five variants, so what lives here is the palette
and the parts that decide whether six figures read as one faction: the skull, the
ribcage, the bone limb. What each figure DOES with them -- its silhouette, its
weapon, its stance -- stays in its own builder, because that is what a player
tells apart at sprite size.

The generic scaffolding (`start`, `finish`, `tatters`, `flame`, ground line,
facing, outline weight) is in `spritekit.py` and shared with every other family.
This module re-exports it so a builder needs one import.

The palette is lifted unchanged from `build_undead_caster.py`, the family's
pilot. Every entry inherits it rather than re-deriving it, which is the reason
the rendered roster does not drift the way the generated one did.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S

# re-exported so a builder imports one kit
start = S.start
tatters = S.tatters
FACING = S.FACE_LEFT


def palette():
    """The family's materials. Keyed so a builder reads like the spec prose."""
    return {
        "robe":   P.toon_mat("ROBE", "#2a1c3f", "#443063", "#63498c"),
        "robe_d": P.toon_mat("ROBEDARK", "#1d1230", "#33234c", "#4b3670"),
        "bone":   P.toon_mat("BONE", "#a89a7c", "#d8ceb0", "#f4eeda"),
        # Aged steel, cool and mid-bright. A figure built entirely from the rust
        # brown below comes out looking like carved wood, which is exactly what
        # the death knight's first pass did -- rust has to be TRIM on steel, not
        # the whole suit, or the armour stops reading as metal.
        "plate":  P.toon_mat("DEADPLATE", "#3f434c", "#666c78", "#939aa8"),
        "iron":   P.toon_mat("RUSTIRON", "#4a382c", "#6e5340", "#93725a"),
        # Dead flesh is grey-green and sits BELOW bone in value, so a skull reads
        # bright against a face. Keeping them apart is what stops a figure that is
        # part-bone part-flesh turning into one grey mass at sprite size.
        "flesh":  P.toon_mat("DEADFLESH", "#4b5a52", "#6d7f73", "#8fa294"),
        # Tattered near-black cloth, but only NEAR black. The family rule is
        # "keep overall values mid-bright", and the first pass took it literally
        # dark: the shadow reaver came back as one unreadable silhouette with his
        # outline invisible inside it, because an outline only reads against a
        # light tone (README). These stops are lifted about 60% from that.
        "rag":    P.toon_mat("GRAVERAG", "#2e2c3a", "#474558", "#636178"),
        "vest":   P.toon_mat("VESTMENT", "#3a3a42", "#565663", "#767585"),
        "wood":   P.toon_mat("GRAVEWOOD", "#33241a", "#4f3927", "#6d4f36"),
        "gold":   P.toon_mat("DEADGOLD", "#6b5316", "#a5842c", "#d4b45c"),
        "teal":   P.flat_mat("SPECTRAL", "#5fe6d8"),
        "teal_d": P.flat_mat("SPECTRALDIM", "#2f8f88"),
        "green":  P.flat_mat("NECROGLOW", "#8cff7a"),
        "green_d": P.flat_mat("NECROHALO", "#3f8f3a"),
        "violet": P.flat_mat("SOULVIOLET", "#b478ff"),
        "dark":   P.flat_mat("SOCKET", "#0d1410"),
    }


def skull(scn, M, loc, radius=0.24, eye=None, jaw=True):
    """Skull with hollow sockets and a lit eye behind each.

    Returns (figure, detail, noline). The socket boxes are `detail` and get no
    outline, because an outline around a hole reads as a second eyebrow. The
    eyefires are `noline` for the same reason: an outline around a glow kills it.
    """
    eye = eye or M["teal"]
    x, y, z = loc
    r = radius
    fig = [P.add_sphere(scn, "skull", (x, y, z), r, M["bone"],
                        scale=(1, 1.02, 1.06), segs=10, rings=7)]
    det, nol = [], []
    if jaw:
        det.append(P.add_box(scn, "jaw", (x, y - r * 0.25, z - r * 0.83),
                             (r * 1.04, r * 0.83, r * 0.58), M["bone"]))
        det.append(P.add_box(scn, "teeth", (x, y - r * 0.71, z - r * 0.50),
                             (r * 0.92, r * 0.17, r * 0.17), M["dark"]))
    det.append(P.add_box(scn, "cheek", (x, y - r * 0.67, z - r * 0.21),
                         (r * 1.25, r * 0.17, r * 0.17), M["dark"]))
    for s in (-1, 1):
        det.append(P.add_box(scn, "socket", (x + s * r * 0.42, y - r * 0.75, z + r * 0.17),
                             (r * 0.50, r * 0.21, r * 0.42), M["dark"]))
        nol.append(P.add_box(scn, "eyefire", (x + s * r * 0.42, y - r * 0.87, z + r * 0.17),
                             (r * 0.21, r * 0.17, r * 0.17), eye))
    return fig, det, nol


def ribcage(scn, M, loc, width=0.62, height=0.72, ribs=4, mat=None):
    """A stack of curved bars reading as a ribcage.

    Bars, not a textured box: at this size the tone ramp gives a single box one
    colour, and ribs are exactly the case where the reading depends on the GAPS.
    Each rib stands proud of the spine so the outline draws between them.
    """
    mat = mat or M["bone"]
    x, y, z = loc
    out = []
    for i in range(ribs):
        t = i / max(1, ribs - 1)
        w = width * (1.0 - 0.22 * t)              # taper toward the waist
        out.append(P.add_box(scn, "rib", (x, y - 0.06, z + height * (0.5 - t)),
                             (w, 0.17, height * 0.13), mat))
    out.append(P.add_box(scn, "spine", (x, y + 0.10, z), (0.13, 0.16, height), mat))
    return out


def bone_arm(scn, M, shoulder, hand, upper_r=0.075, fore_r=0.065, mat=None):
    """Two bare bone segments and a hand.

    A skeletal arm is the family's cheapest way to look undead: no sleeve to
    model, and the gap between the segments does the work an elbow joint would
    otherwise need geometry for.
    """
    return S.limb(scn, shoulder, hand, mat or M["bone"], upper_r, fore_r)


def ghostflame(scn, M, loc, scale=1.0, hot=None, cool=None):
    """The family's spectral fire, teal by default."""
    return S.flame(scn, loc, hot or M["teal"], cool or M["teal_d"], scale)


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACING, role=None, body_roots=()):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra,
                    facing, role, body_roots)
