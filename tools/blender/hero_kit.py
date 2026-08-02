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

Escalation is SILHOUETTE first (user ruling 2026-08-01). See the rarity-ladder
section further down for the table and for what the old trim-only ladder got
wrong. Trim material still steps steel to gold to bright gold, but it is now the
last thing a tier changes rather than the only thing.

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
    # `helm` IS DEPRECATED. Do not reach for it on a new hero.
    # USER RULING 2026-08-02: every character and every rarity variant is
    # INDIVIDUALLY DESIGNED, not reassembled from parts shared with other units.
    # A helmet is the most identity-bearing thing an armoured figure owns, so it
    # belongs in that hero's own builder. This generic one survives because the
    # fighter's legendary and the banneret still use it and their art is either
    # approved or unjudged; both should grow their own and drop it.
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


def cloak(scn, M, mat, z, height=1.40, r_base=0.52, r_top=0.30, y=0.24):
    """A shell standing PROUD of the back so it outlines against the torso.

    **Keep it BEHIND the figure and keep it narrow.** A cloak widened until it
    surrounds the legs stops being a cloak: the hero renders as one solid cone
    and the user's verdict was "a multicolored triangle with a bow" (2026-08-01).
    The legs have to stay visible under it, because the gap between them is most
    of the negative space a small figure has. Push `y` back rather than growing
    `r_base` when a cloak needs more presence.
    """
    return [P.add_cone(scn, "hcloak", (0, y, z), r_base, r_top, height, mat, verts=10)]


# --------------------------------------------------------------------------
# the rarity ladder
# --------------------------------------------------------------------------
# USER RULING 2026-08-01, after judging the labelled variants sheet: "they are
# all way too similar. i cant even tell a difference at all in the archers." The
# bar he set is a player scanning the hire pool thinking "oh hey, i havent seen
# that one before", not squinting at a collar.
#
# The old ladder put every tier step into TRIM MATERIAL. On the archer that came
# to one 0.30-wide bracer, an arrowhead and two bow nocks changing from steel to
# gold on a figure 2.95 units tall: rare and epic were geometrically identical.
#
# A sprite reads in one order -- outline, then large colour masses, then detail.
# So every step here changes the OUTLINE, and detail is what it changes last.

def pauldrons(scn, M, mat, z, span=0.56, r=0.26, squash=0.66):
    """Shoulder caps: the widest, earliest-read change available on a small figure.

    **Check the hero's entry in `attack_roster.py` before adding these.**
    `animkit.top_joint()` takes the TOPMOST part matching that arm's shoulder
    names as the pivot the arm turns about. Most heroes list `shoulder`, so a cap
    named `pauldron` is invisible to them and safe. The paladin does not: its
    entry names `("pauldron",)` as the shoulder group, so adding one of these to
    that hero moves its swing pivot up into the armour.
    """
    return [P.add_sphere(scn, "pauldron", (s * span, -0.04, z), r, mat,
                         scale=(1.10, 0.84, squash), segs=10, rings=6)
            for s in (-1, 1)]


def crest(scn, M, mat, z, height=0.38, width=0.10, depth=0.34):
    """A blade of metal standing above the head.

    **Height barely reads and this is why.** `spritekit.finish()` measures the
    assembled body and scales the root until it hits `role_height(role)` exactly,
    so a crest that makes a hero taller shrinks everything under it to
    compensate. The figure ends the same height with a slightly smaller body: the
    crest costs silhouette instead of adding it. The user's 2026-07-31 ruling
    fixes hero height across tiers, so height cannot be spent at all.

    Use it as a small accent on a head that has room, never as a tier's read.
    """
    return [P.add_box(scn, "hcrest", (0, 0.04, z + height / 2),
                      (width, depth, height), mat, bevel=0.02)]


def mantle(scn, M, mat, z, span=0.94, thick=0.34, drop=0.42):
    """A wide shoulder mantle, the biggest silhouette change a tier can buy.

    WIDTH is the axis to spend. It is not normalised by anything, so a mantle
    reads at full strength where a crest of the same volume reads as nothing.
    """
    return [P.add_cone(scn, "hmantle", (0, 0.02, z), span, span * 0.46, thick,
                       mat, verts=12),
            P.add_cone(scn, "hmantlehem", (0, 0.02, z - drop * 0.5), span * 0.86,
                       span * 0.62, drop, mat, verts=12)]


def deep_hood(scn, M, mat, loc, r=0.29, reach=1.9, shadow=None):
    """A hood that still reads as a hood at 112 pixels: a cowl standing well clear
    of the skull, projecting forward over the face, with the face in shadow.

    The stock `head(hood=...)` cowl hugs the head, so at sprite size it reads as a
    green cap rather than as a hood. This one is deliberately oversized.
    """
    x, y, z = loc
    out = [P.add_cone(scn, "hdeephood", (x, y + r * 0.30, z + r * 0.34),
                      r * reach, r * 0.30, r * 2.05, mat, verts=12),
           P.add_sphere(scn, "hdeephoodback", (x, y + r * 0.62, z - r * 0.06),
                        r * 1.44, mat, scale=(1.0, 0.94, 1.10), segs=12, rings=7),
           P.add_cone(scn, "hdeepcowl", (x, y + r * 0.10, z - r * 1.30),
                      r * 1.86, r * 1.10, r * 1.15, mat, verts=12)]
    if shadow is not None:
        out.append(P.add_sphere(scn, "hhoodshadow", (x, y - r * 0.62, z + r * 0.10),
                                r * 0.92, shadow, scale=(1.0, 0.44, 1.0),
                                segs=10, rings=6))
    return out


def half_cape(scn, M, mat, z, height=0.92, r_base=0.48, r_top=0.30):
    """A short cape off the shoulders. Gives epic a new back edge without spending
    the full cloak, which is legendary's."""
    return [P.add_cone(scn, "hcape", (0, 0.22, z), r_base, r_top, height, mat, verts=10)]


def stance(t=None):
    """Leg-spread multiplier. A legendary hero plants wider, which widens the base
    of the silhouette and reads before any piece of gear does.

    Safe for animation: the attack sheets drive the ARMS from derived joints and
    never touch the legs, so a stance carries through a swing unchanged.

    **Never call this on a hero whose OWN sprite is epic or legendary.** It keys
    off the tier name, so on the paladin, whose base art is the Epic Crusader, it
    silently widened the shipped sprite. Those builders write their spread out
    per tier instead.
    """
    return {"legendary": 1.24, "epic": 1.10}.get(t or tier(), 1.0)


def regalia(scn, M, shoulder_z, head_top, span=0.56, cape_mat=None,
            cape_z=None, t=None):
    """Every tier addition that is not specific to one archetype.

    Returns parts in the caller's local space, so a builder appends them to the
    same list its torso parts go in and they lean with the torso.

    | tier | outline change | detail change |
    |---|---|---|
    | common | none | none, plain and field-worn |
    | rare | pauldrons | steel |
    | epic | bigger pauldrons, crest, half-cape | gold |
    | legendary | widest pauldrons, tall crest, full cloak, stance | bright gold |

    The full cloak and the archetype's own signature shape stay with the builder:
    a cloak needs the figure's real height, and a signature is by definition not
    generic.
    """
    t = t or tier()
    trim = trim_mat(M, t)
    if trim is None:
        return []
    cape_mat = cape_mat or trim
    if t == "rare":
        return pauldrons(scn, M, trim, shoulder_z, span=span, r=0.27)
    if t == "epic":
        return (mantle(scn, M, cape_mat, shoulder_z + 0.10, span=0.86, drop=0.36)
                + pauldrons(scn, M, trim, shoulder_z, span=span, r=0.30)
                + half_cape(scn, M, cape_mat,
                            cape_z if cape_z is not None else shoulder_z - 0.30))
    return (mantle(scn, M, cape_mat, shoulder_z + 0.12, span=1.02, drop=0.48)
            + pauldrons(scn, M, trim, shoulder_z + 0.04, span=span + 0.06, r=0.34))


def finish(scn, px, key, figure, detail, noline, roots=(), skip_extra=(),
           role="hero", body_roots=()):
    """Close a hero. The output filename carries the tier suffix, so one builder
    produces the base sprite and its three variants from four runs."""
    return S.finish(scn, px, key + suffix(), figure, detail, noline, roots,
                    skip_extra, FACING, role, body_roots)
