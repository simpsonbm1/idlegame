"""Orc Warband parts, M15_ASSET_SPECS.md entries 22-27.

Family rules from that doc: "hulking broad builds, olive gray-green hide --
darker than the goblins -- heavy black iron, red war paint". Enemies face LEFT.

Two of those rules are relative and therefore measurable, which is the useful
kind. "Darker than the goblins" is a palette comparison against `goblin_kit.py`
and the hide here sits a full band below it. "Hulking" is world height and width
against the same family: an orc common stands 3.6 units to a goblin common's 2.5
and is close to twice as broad, so the two factions never have to be told apart
by their faces.

**Black iron needs care at three tones.** A near-black armour gives the ramp
almost nowhere to go and the outline nothing to read against -- the same trap the
Undead Legion's shadow reaver fell into. So the iron here is a dark blue-grey
whose light stop is genuinely light, and the RED WAR PAINT does the work of
making the faction identifiable rather than the armour doing it.
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

COMMON_HEIGHT = 3.6     # world units, against a goblin common's 2.5


def palette():
    return {
        # olive grey-green, a full band below the goblins' mossy yellow-green
        "hide":  P.toon_mat("ORCHIDE", "#2f4630", "#4a6647", "#6d8a64"),
        # "heavy black iron", but not literally black: a near-black gives the
        # ramp nowhere to go and leaves the outline nothing to read against
        # Its stops are spread wider than the hide's on purpose. Armour whose mid
        # tone sits at the same luminance as the skin under it disappears, and the
        # brute's first pass read as a green orc with a faint grey patch.
        "iron":  P.toon_mat("BLACKIRON", "#191b22", "#3a4050", "#7b8399"),
        "steel": P.toon_mat("ORCSTEEL", "#4e535e", "#767d8c", "#a3aab8"),
        "fur":   P.toon_mat("ORCFUR", "#332a1f", "#544733", "#77664b"),
        "leath": P.toon_mat("ORCLEATHER", "#402c1c", "#674630", "#8d6748"),
        "wood":  P.toon_mat("ORCWOOD", "#3d2a16", "#5e4222", "#835f36"),
        "tusk":  P.toon_mat("ORCTUSK", "#b09a6a", "#d8c99a", "#f2e8c8"),
        "bone":  P.toon_mat("ORCBONE", "#a89a7c", "#d8ceb0", "#f4eeda"),
        # the faction's identifying colour, since the armour cannot be
        "paint":  P.toon_mat("WARPAINT", "#7e1d16", "#b52f22", "#e05a44"),
        "cloth": P.toon_mat("ORCCLOTH", "#5c1b16", "#8a2c22", "#b34a38"),
        "ember": P.flat_mat("ORCEMBER", "#ff8a2b"),
        "ember_d": P.flat_mat("ORCEMBERDIM", "#c04a12"),
        "dark":  P.flat_mat("ORCDARK", "#12160f"),
    }


def head(scn, M, loc, r=0.48, paint=True, tusks=True):
    """The family face: heavy underslung jaw, deep brow, tusks pointing UP.

    Goblin tusks point down and orc tusks point up, which is the cheapest way to
    tell the two green factions apart at sprite size -- cheaper than any change
    of proportion, because it alters the head's silhouette rather than its
    interior.

    Returns (figure, detail).
    """
    x, y, z = loc
    fig = [P.add_sphere(scn, "oskull", (x, y - 0.02, z), r, M["hide"],
                        scale=(1.08, 1.0, 0.94), segs=12, rings=8),
           P.add_box(scn, "ojaw", (x, y - r * 0.62, z - r * 0.54),
                     (r * 1.56, r * 1.06, r * 0.72), M["hide"], bevel=0.06)]
    det = [P.add_box(scn, "obrow", (x, y - r * 0.86, z + r * 0.30),
                     (r * 1.60, r * 0.34, r * 0.32), M["hide"]),
           P.add_box(scn, "omouth", (x, y - r * 1.10, z - r * 0.52),
                     (r * 1.10, r * 0.10, r * 0.12), M["dark"])]
    if paint:
        # **VERTICAL, and asymmetric.** A broad horizontal band across the eyes is
        # the obvious way to draw war paint and it is wrong: at sprite size it
        # reads unmistakably as a tied bandana over the eyes, and it did so on all
        # six orcs at once. A stripe down the centre of the face plus one cheek
        # bar cannot be mistaken for a worn object, because no garment has that
        # shape.
        det.append(P.add_box(scn, "opaint", (x, y - r * 0.98, z - r * 0.10),
                             (r * 0.30, r * 0.10, r * 1.30), M["paint"]))
        det.append(P.add_box(scn, "opaintcheek", (x - r * 0.52, y - r * 0.94, z - r * 0.16),
                             (r * 0.36, r * 0.10, r * 0.20), M["paint"]))
    for s in (-1, 1):
        det.append(P.add_box(scn, "oeye", (x + s * r * 0.34, y - r * 1.04, z + r * 0.02),
                             (r * 0.22, r * 0.06, r * 0.15), M["dark"]))
        if tusks:
            fig.append(P.add_cone(scn, "otusk", (x + s * r * 0.52, y - r * 1.04, z - r * 0.42),
                                  r * 0.16, 0.0, r * 0.72, M["tusk"],
                                  rot=(math.radians(-18), 0, math.radians(s * 8)), verts=6))
    return fig, det


def heavy_legs(scn, M, hip_z, spread=0.52, mat=None):
    """Thick planted legs. Hulking is width as much as height, and most of the
    width a viewer registers is at the base of the figure."""
    mat = mat or M["hide"]
    out = []
    for s, yoff in ((-1, -0.26), (1, 0.24)):
        out.append(P.add_box(scn, "ofoot", (s * spread, yoff - 0.10, 0.15),
                             (0.60, 0.80, 0.30), mat, bevel=0.05))
        out.append(P.add_cyl(scn, "oshin", (s * spread, yoff, hip_z * 0.34),
                             0.29, hip_z * 0.50, mat, verts=8))
        out.append(P.add_box(scn, "owrap", (s * spread, yoff, hip_z * 0.20),
                             (0.56, 0.56, 0.24), M["leath"]))
        out.append(P.add_cyl(scn, "othigh", (s * spread * 0.92, yoff * 0.6, hip_z * 0.76),
                             0.34, hip_z * 0.46, mat, verts=8))
    return out


def barrel_torso(scn, M, hip_z, chest_r=0.72, lean=8):
    """The family build: a barrel chest over a narrower waist, leaned forward a
    little. Returns (root, parts)."""
    root = P.make_root(scn, "torso_root", rot=(-lean, 0, 0), loc=(0, 0, hip_z))
    parts = [P.add_cyl(scn, "owaist", (0, 0, 0.14), 0.52, 0.42, M["hide"], verts=10,
                       scale=(1.10, 0.80, 1)),
             P.add_sphere(scn, "ochest", (0, -0.06, 0.62), chest_r, M["hide"],
                          scale=(1.26, 0.82, 0.86), segs=12, rings=8)]
    return root, parts


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACING, role=None, body_roots=()):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra,
                    facing, role, body_roots)
