"""Townsfolk parts, M15_ASSET_SPECS.md entries 9-16.

Family rules from that doc: townsfolk face RIGHT and stand in a "relaxed friendly
standing pose instead of combat-idle". They are the only figures in the game who
are not holding a weapon, and that is their whole read.

**They are the same size as the heroes**, per the ruling that normal figures are
all roughly one height. What separates a villager from a fighter is not scale but
three things:

1. Both hands hold a TOOL or an object of daily life, never a blade.
2. Homespun colours -- undyed wool, plain linen, working leather -- against the
   heroes' saturated steel-blue, cream and gold.
3. Arms down and relaxed. Every hero and enemy in the roster has at least one arm
   raised or braced; a figure with both arms hanging reads as a civilian before
   any of its detail is legible.

The body comes from `hero_kit`, since a townsperson and a hero are the same
human. Only the palette and what they carry differ.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import spritekit as S
import hero_kit as H

start = S.start
tatters = S.tatters
FACING = S.FACE_RIGHT

# reused wholesale: a townsperson and a hero are the same human
head = H.head
legs = H.legs
torso = H.torso
robe = H.robe


def palette():
    return {
        # homespun: undyed wool, plain linen, working leather
        "wool":   P.toon_mat("TWOOL", "#4d3f2c", "#726046", "#9b8765"),
        "linen":  P.toon_mat("TLINEN", "#7a715c", "#a49a82", "#cdc4ab"),
        "leath":  P.toon_mat("TLEATHER", "#43301c", "#6b4c2c", "#916d45"),
        "apron":  P.toon_mat("TAPRON", "#5a4326", "#82653c", "#aa8b5c"),
        "straw":  P.toon_mat("TSTRAW", "#8a7330", "#bda253", "#e0cb8b"),
        "green":  P.toon_mat("TGREEN", "#2f4a26", "#49693a", "#6c8f56"),
        "blue":   P.toon_mat("TBLUE", "#23385c", "#375383", "#5478b0"),
        "violet": P.toon_mat("TVIOLET", "#33244c", "#4d3970", "#6d569a"),
        "white":  P.toon_mat("TWHITE", "#8f8d84", "#bfbdb2", "#eae8dd"),
        "gold":   P.toon_mat("TGOLD", "#8a5f14", "#c9962c", "#f0d264"),
        "iron":   P.toon_mat("TIRON", "#3c3c3a", "#5c5c58", "#82827c"),
        "brass":  P.toon_mat("TBRASS", "#6f5518", "#a1802f", "#cfae5a"),
        "wood":   P.toon_mat("TWOOD", "#4a3018", "#6f4a24", "#96693a"),
        "skin":   P.toon_mat("TSKIN", "#7d5638", "#b0805a", "#dcae83"),
        "dark":   P.flat_mat("TDARK", "#14110d"),
        "ale":    P.flat_mat("TALE", "#e8bb52"),
        "tonic":  P.flat_mat("TTONIC", "#8cff7a"),
        "crystal": P.flat_mat("TCRYSTAL", "#bfa8ff"),
        "holy":   P.flat_mat("THOLY", "#fff2c2"),
    }


def relaxed_arms(scn, M, tors, shoulder_z=0.66, spread=0.50, sleeve=None,
                 left_hand=None, right_hand=None):
    """Both arms hanging, which is the family's posture.

    `left_hand` and `right_hand` are (x, y, z) in torso-local space; passing None
    uses the default hanging position. Returns the hand positions so a builder can
    hang an object off them without recomputing anything.
    """
    sleeve = sleeve or M["wool"]
    lh = left_hand or (-spread - 0.04, -0.56, -0.14)
    rh = right_hand or (spread + 0.04, -0.56, -0.14)
    for s in (-1, 1):
        tors.append(P.add_sphere(scn, "tshoulder", (s * spread, -0.08, shoulder_z), 0.22,
                                 sleeve, scale=(1, .95, .88)))
    tors += S.limb(scn, (-spread, -0.10, shoulder_z), lh, sleeve, 0.145, 0.13,
                   hand_mat=M["skin"])
    tors += S.limb(scn, (spread, -0.10, shoulder_z), rh, sleeve, 0.145, 0.13,
                   hand_mat=M["skin"])
    return lh, rh


def brim_hat(scn, M, loc, r=0.30, mat=None, crown=0.34, brim=1.95):
    """A wide-brimmed hat. The brim is the widest thing on the figure, which is
    what makes a hat a silhouette rather than a hair colour."""
    mat = mat or M["straw"]
    x, y, z = loc
    return [P.add_cyl(scn, "thatbrim", (x, y, z + r * 0.52), r * brim, r * 0.16, mat, verts=12),
            P.add_cyl(scn, "thatcrown", (x, y, z + r * 0.52 + crown / 2), r * 1.02, crown, mat,
                      verts=12)]


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           body_roots=()):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra,
                    FACING, "hero", body_roots)
