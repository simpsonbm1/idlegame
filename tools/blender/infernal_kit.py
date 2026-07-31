"""Infernal Siege parts, M15_ASSET_SPECS.md entries 40-45.

Family rules from that doc: "charcoal-black and deep crimson demon hide, curling
horns, glowing ember-orange accents". Enemies face LEFT.

**This is the only family that is not five variants on one build.** Entry 41 is a
four-legged hellhound seen side-on and entry 44 a small winged imp, so the shared
parts here are narrower than the other kits': a palette, horns, and the ember
cracks. Bodies are built per entry.

The ember cracks are the family's signature and they are the one thing that has
to be got right in the palette rather than per figure. Charcoal hide is the
darkest material in the whole roster, which would normally be a mistake -- an
outline cannot read against it. It works here only because every one of these
figures carries bright emissive cracks, and those do the separating that an
outline does elsewhere. Take the cracks off one of them and it becomes an
unreadable blob.
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
flame = S.flame
FACING = S.FACE_LEFT


def palette():
    return {
        # Charcoal, and it is the darkest hide in the roster. Its light stop is
        # pushed well up anyway, or the tone ramp has nowhere to go and a whole
        # figure collapses to one flat shape.
        "hide":  P.toon_mat("DEMONHIDE", "#1c1a1f", "#35313a", "#5c565f"),
        "crim":  P.toon_mat("DEMONCRIMSON", "#4a1418", "#7a2226", "#a83d38"),
        "horn":  P.toon_mat("DEMONHORN", "#3a332c", "#5c5145", "#867a68"),
        "bone":  P.toon_mat("DEMONBONE", "#8f826a", "#c0b498", "#e6dcc4"),
        "iron":  P.toon_mat("HELLIRON", "#241f24", "#403944", "#69606f"),
        "brass": P.toon_mat("HELLBRASS", "#6b4a12", "#a37727", "#d4a850"),
        "robe":  P.toon_mat("DEMONROBE", "#2a1418", "#48232a", "#6b3a3f"),
        # the emissive family: cracks, eyes, fire
        "ember": P.flat_mat("EMBER", "#ff8a2b"),
        "ember_d": P.flat_mat("EMBERDIM", "#c04a12"),
        "ember_h": P.flat_mat("EMBERHOT", "#ffd166"),
        "blood": P.flat_mat("HELLBLOOD", "#ff3a2e"),
        "dark":  P.flat_mat("DEMONDARK", "#0d0a0c"),
    }


def horns(scn, M, loc, r=0.30, curl=3, sweep=44, length=0.34, mat=None):
    """A pair of curling horns, each built from `curl` shrinking segments.

    The curl is what makes them demonic rather than bovine, and a curl at this
    size is a short chain of straight pieces each turned a little further than
    the last. A single swept cone reads as a spike.

    Returned as figure parts: they break the head's silhouette, which is the
    whole reason the family has them.
    """
    mat = mat or M["horn"]
    x, y, z = loc
    out = []
    for s in (-1, 1):
        px_, pz = x + s * r * 0.72, z + r * 0.42
        ang = 0.0
        for i in range(curl):
            ang += sweep
            seg = length * (1.0 - 0.22 * i)
            out.append(P.add_cone(scn, "ihorn", (px_, y + 0.02, pz),
                                  r * (0.20 - 0.045 * i), r * (0.15 - 0.04 * i), seg, mat,
                                  rot=(0, math.radians(s * ang), 0), verts=6))
            px_ += math.sin(math.radians(ang)) * seg * s * 0.86
            pz += math.cos(math.radians(ang)) * seg * 0.86
    return out


def cracks(scn, M, spots, w=0.09, hot=True):
    """Glowing fissures in the hide.

    `spots` is a list of (x, y, z, length) in the figure's own frame. Each is a
    short vertical bar rather than a drawn line, because a line one pixel wide
    disappears and a bar two pixels wide does not.

    Return these as NO-OUTLINE parts. An outline around a glow puts it out.
    """
    mat = M["ember"] if hot else M["ember_d"]
    return [P.add_box(scn, "icrack", (x, y, z), (w, 0.05, ln), mat)
            for (x, y, z, ln) in spots]


def clawed_limb(scn, M, shoulder, hand, upper_r=0.16, fore_r=0.14, claws=3):
    """An arm ending in splayed claws rather than a fist.

    Every infernal hand is open. It costs three small cones and it is the
    cheapest way to say a figure is not human when the figure is otherwise
    roughly humanoid.
    """
    out = S.limb(scn, shoulder, hand, M["hide"], upper_r, fore_r)
    hx, hy, hz = hand
    for i in range(claws):
        t = (i - (claws - 1) / 2.0)
        out.append(P.add_cone(scn, "iclaw",
                              (hx + t * fore_r * 0.62, hy - fore_r * 1.10, hz + t * fore_r * 0.30),
                              fore_r * 0.30, 0.0, fore_r * 1.50, M["bone"],
                              rot=(math.radians(74), 0, math.radians(t * 16)), verts=5))
    return out


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           facing=FACING, role=None, body_roots=()):
    return S.finish(scn, px, key, figure, detail, noline, roots, skip_extra,
                    facing, role, body_roots)
