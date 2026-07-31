"""Hero parts, M15_ASSET_SPECS.md entries 1-8, and the rarity variants 56-82.

Heroes face RIGHT. They share the human body the Bandit Horde uses, and they must
NOT share its look: the bandits are worn browns with every face covered, so the
heroes are saturated steel-blue, cream and gold with every face open. That
contrast is the reason the bandit palette was pushed as far toward brown as it
was, and it is the only thing separating the two human factions on a battlefield.

## Rarity, entries 56-82

A variant is the same character at a different station in life, not a new person,
so it is a PARAMETER on the base builder rather than a script of its own. Set
`HERO_TIER` in the environment and the builder re-renders itself dressed for that
tier; `render_all.py` does this from the roster.

The spec's escalation is presence and regalia, not shine, and explicitly not a
palette change -- the game draws its own rarity-coloured rim, so recolouring the
figure would fight it. What actually changes:

| tier | trim | glow | presence |
|---|---|---|---|
| common | none | none | plain, field-worn |
| rare | steel | none | a small flourish |
| epic | gold | one element | ornate masterwork |
| legendary | bright gold | radiant | a cloak, a crest, gilding |

**Each hero's BASE sprite already occupies one tier** and that tier gets no
separate file, per the audit in `M15_ASSET_SPECS.md`. The mender's base art is
Rare and the paladin's is Epic; everyone else's is Common.
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
FACING = S.FACE_RIGHT

TIERS = ("common", "rare", "epic", "legendary")


def tier():
    """The tier this run is rendering. `base` means the hero's own sprite."""
    t = os.environ.get("HERO_TIER", "base")
    return t if t in TIERS else "base"


def suffix(t=None):
    t = t or tier()
    return "" if t == "base" else "_" + t


def palette():
    return {
        # the guardian knight's own steel and navy, since he is the anchor
        "steel": P.toon_mat("HSTEEL", "#4a6d94", "#7ba3c9", "#b6d8ef"),
        "blade": P.toon_mat("HBLADE", "#8fb4d6", "#cbe4f6", "#f4fbff"),
        "navy":  P.toon_mat("HNAVY", "#1b2a52", "#2a3f73", "#3d5691"),
        "gold":  P.toon_mat("HGOLD", "#8a5f14", "#c9962c", "#f0d264"),
        "brightgold": P.toon_mat("HBRIGHTGOLD", "#a8790f", "#e0b132", "#ffeb9a"),
        "leath": P.toon_mat("HLEATHER", "#4a2e18", "#7a4d28", "#a06a3a"),
        "mail":  P.toon_mat("HMAIL", "#3f4650", "#626b78", "#8e97a5"),
        "cream": P.toon_mat("HCREAM", "#8f8156", "#c4b382", "#eee0b4"),
        "crimson": P.toon_mat("HCRIMSON", "#6b1d1c", "#9c2f27", "#c85641"),
        "green": P.toon_mat("HGREEN", "#26401f", "#3d6330", "#5d8a48"),
        "violet": P.toon_mat("HVIOLET", "#2c1d44", "#452f66", "#63498c"),
        "azure": P.toon_mat("HAZURE", "#1b3566", "#2c5093", "#4374c4"),
        "ice":   P.toon_mat("HICE", "#5d7f9c", "#8fb3cc", "#c6e2f2"),
        "fur":   P.toon_mat("HFUR", "#8e9aa4", "#bcc6cf", "#e6edf3"),
        "charcoal": P.toon_mat("HCHARCOAL", "#22222a", "#3a3a46", "#585866"),
        "skin":  P.toon_mat("HSKIN", "#7d5638", "#b0805a", "#dcae83"),
        "wood":  P.toon_mat("HWOOD", "#4a3018", "#6f4a24", "#96693a"),
        "dark":  P.flat_mat("HDARK", "#10141f"),
        "sun":   P.flat_mat("HSUN", "#ffd766"),
        "arcane": P.flat_mat("HARCANE", "#7fd4ff"),
        "frost": P.flat_mat("HFROST", "#bfeaff"),
        "holy":  P.flat_mat("HHOLY", "#fff2c2"),
    }


def trim_mat(M, t=None):
    """The material a tier's flourishes are made of. Common gets none at all,
    which is the point: a common hero is plain and field-worn."""
    t = t or tier()
    return {"common": None, "base": None, "rare": M["steel"],
            "epic": M["gold"], "legendary": M["brightgold"]}[t]


def glow_mat(M, t=None):
    """Epic gets ONE subtly glowing element. Legendary radiates."""
    t = t or tier()
    return {"common": None, "base": None, "rare": None,
            "epic": M["holy"], "legendary": M["holy"]}[t]


def is_legendary(t=None):
    return (t or tier()) == "legendary"


def head(scn, M, loc, r=0.30, hood=None, helm=None, shadowed=False):
    """A human head with an OPEN face. That is the heroes' half of the contrast
    against the bandits, every one of whom covers his.

    Returns (figure, detail).
    """
    x, y, z = loc
    fig = [P.add_sphere(scn, "hhead", (x, y, z), r, M["skin"],
                        scale=(0.94, 1.0, 1.08), segs=10, rings=7)]
    det = [P.add_box(scn, "hbrow", (x, y - r * 0.92, z + r * 0.52),
                     (r * 1.60, r * 0.18, r * 0.20), M["dark"])]
    for s in (-1, 1):
        det.append(P.add_box(scn, "heye", (x + s * r * 0.34, y - r * 1.10, z + r * 0.16),
                             (r * 0.30, r * 0.10, r * 0.22),
                             M["dark"] if not shadowed else M["dark"]))
    det.append(P.add_box(scn, "hmouth", (x, y - r * 1.02, z - r * 0.44),
                         (r * 0.46, r * 0.08, r * 0.10), M["dark"]))
    if hood is not None:
        fig.append(P.add_cone(scn, "hhood", (x, y + r * 0.34, z + r * 0.40),
                              r * 1.30, r * 0.34, r * 1.58, hood, verts=10))
        fig.append(P.add_sphere(scn, "hhoodback", (x, y + r * 0.46, z + r * 0.02),
                                r * 1.06, hood, scale=(1.0, 0.88, 1.0), segs=10, rings=6))
        fig.append(P.add_cone(scn, "hcowl", (x, y + r * 0.22, z - r * 1.24),
                              r * 1.42, r * 0.86, r * 0.96, hood, verts=10))
    if helm is not None:
        fig.append(P.add_sphere(scn, "hhelm", (x, y, z + r * 0.30), r * 1.14, helm,
                                scale=(1.0, 1.0, 0.82), segs=12, rings=7))
        fig.append(P.add_box(scn, "hhelmbrim", (x, y - r * 0.30, z + r * 0.16),
                             (r * 2.30, r * 1.90, r * 0.22), helm))
    return fig, det


def legs(scn, M, hip_z, spread=0.34, mat=None, boot=None):
    mat = mat or M["leath"]
    boot = boot or mat
    out = []
    for s, yoff in ((-1, -0.24), (1, 0.22)):
        out.append(P.add_box(scn, "hboot", (s * spread, yoff - 0.10, 0.13),
                             (0.38, 0.62, 0.26), boot, bevel=0.04))
        out.append(P.add_cyl(scn, "hshin", (s * spread, yoff, hip_z * 0.36),
                             0.155, hip_z * 0.50, mat, verts=8))
        out.append(P.add_cyl(scn, "hthigh", (s * spread * 0.94, yoff * 0.6, hip_z * 0.78),
                             0.185, hip_z * 0.44, mat, verts=8))
    return out


def torso(scn, M, hip_z, chest_r=0.44, lean=6, mat=None):
    mat = mat or M["mail"]
    root = P.make_root(scn, "torso_root", rot=(-lean, 0, 0), loc=(0, 0, hip_z))
    parts = [P.add_cyl(scn, "hwaist", (0, 0, 0.12), 0.33, 0.34, mat, verts=10,
                       scale=(1.10, 0.82, 1)),
             P.add_sphere(scn, "hchest", (0, -0.04, 0.50), chest_r, mat,
                          scale=(1.22, 0.84, 0.92), segs=12, rings=8)]
    return root, parts


def robe(scn, M, mat, top=1.72, r_base=0.84, r_top=0.42):
    """A floor-length robe. Cheaper than legs and the shape three heroes need."""
    return [P.add_cone(scn, "hrobe", (0, 0, top / 2), r_base, r_top, top, mat, verts=12)]


def cloak(scn, M, mat, z, height=1.40, r_base=0.52, r_top=0.30):
    """A shell standing PROUD of the back so it outlines against the torso. Only
    legendary heroes get one; it is the tier's clearest silhouette change."""
    return [P.add_cone(scn, "hcloak", (0, 0.24, z), r_base, r_top, height, mat, verts=10)]


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           role="hero", body_roots=()):
    """Close a hero. The output filename carries the tier suffix, so one builder
    produces the base sprite and its three variants from four runs."""
    return S.finish(scn, px, key + suffix(), figure, detail, noline, roots,
                    skip_extra, FACING, role, body_roots)
