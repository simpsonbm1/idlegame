"""Which attack each fighting character performs, and out of which parts.

One entry per combatant. Townsfolk are absent on purpose: they never fight, so
they never need an attack sheet.

An entry names PART BASES, not coordinates. `animkit` derives the joint from
whichever named shoulder part sits highest and the bone lengths from the parts
themselves, so nothing here goes stale when a model's proportions change. Only
renaming or removing a limb breaks an entry, and that raises a KeyError rather
than silently detaching an arm.

`groups` is a list of (shoulder_groups, part_names, weapon_root). Two entries in
the list means dual-wielding: two pivots turning by the same angles. Two
shoulder_groups inside one entry means a two-handed grip, which pivots about the
midpoint between the shoulders and reads as the torso twisting.

`build_attack.py` keeps the guardian knight and the goblin brute as the two
worked examples of the pivot and the inverse-kinematics techniques, so they are
deliberately not repeated here.
"""

import attack_shapes as A

# a hound's head-snap: no arms to swing, so the bite is the whole animation
BITE = [(0, 0, 0), (6, -14, -0.04), (10, -22, -0.06), (-8, 26, 0.12),
        (-12, 34, 0.16), (-6, 18, 0.08), (-2, 6, 0.03), (0, 0, 0)]


class Attack:
    def __init__(self, key, module, groups, frames, cell=128, env=None, ik=None):
        self.key = key
        self.module = module
        self.groups = [Swing.of(g) for g in groups]
        self.frames = frames
        self.cell = cell
        self.env = env or {}
        self.ik = ik


class IK:
    """The inverse-kinematics technique: drive the weapon, solve the arms to it.

    An entry carrying one of these ignores `groups` entirely. `animkit.twohand_sheet`
    does the work, and the difference from a pivot is the whole reason this exists:
    a pivot welds an arm and its weapon into one rigid piece about one fixed point,
    so it can spin a weapon but can never raise a grip or extend an arm. Those are
    the two motions most attacks in this game are made of.

    `arms` is a list of dicts with `shoulder` (part names the joint is derived
    from), `upper`, `fore`, `hand`, and `pole` for which way the elbow breaks.
    **Write each shoulder as `^upper<side>`**, meaning that part's TOP: both
    shoulder balls on a hero share the single name "shoulder", and a name is all
    the lookup has to choose by, so naming the ball puts both arms on whichever
    one sits highest.

    `weapon` is one root name, or a LIST of `{"root", "frames", "mid"}` dicts for
    a figure holding one weapon per hand. An arm then picks its own with
    `"weapon": <index>`, and only the entry's own table moves the figure.

    An arm may carry `"track"`, a per-frame `(dx, dy, dz)` added to its grip in
    world space. That is how a hand LEAVES its weapon -- an archer's string hand
    travels back and up while his bow hand holds the bow still.
    """

    def __init__(self, weapon, arms, mid=None, stretch=0.22):
        self.weapon = weapon
        self.arms = arms
        self.mid = mid
        self.stretch = stretch


class Swing:
    """One pivot: where it turns, what it carries, and optionally its own table.

    Most entries are still the plain `(joint, parts, weapon)` tuple and `of()`
    lifts those, so nothing had to be rewritten. The extra fields exist for two
    cases the tuple cannot say:

    `frames` gives this pivot a table of its own. An archer's draw is the string
    hand going back while the bow hand holds, and one shared table can only rock
    the whole bow. The body's own step still follows the entry's default table.

    `parent` names the index of another group whose pivot this one hangs from, so
    a weapon can turn about the FIST while the arm turns about the shoulder. A
    weapon whose mass already sits at the shoulder cannot be swung from there at
    all; the paladin's hammer is the worked case. **Order matters: a child must be
    listed BEFORE its parent**, or the parent's pivot collects the weapon first.
    """

    def __init__(self, joint, parts=(), weapon=None, frames=None, parent=None):
        self.joint = joint
        self.parts = tuple(parts)
        self.weapon = weapon
        self.frames = frames
        self.parent = parent

    @staticmethod
    def of(g):
        return g if isinstance(g, Swing) else Swing(g[0], g[1], g[2])


def _dual(left, right, lroot, rroot):
    """Dual wield: one pivot per arm, each on that arm's OWN shoulder.

    Derived from the arm's first part, which is always its upper segment, and
    read as `^name` so the joint is that segment's TOP. A shared shoulder name
    cannot express two sides -- see `animkit.top_joint`.
    """
    return [([("^" + left[0],)], left, lroot),
            ([("^" + right[0],)], right, rroot)]


HERO_ARM_L = ("upperL", "foreL", "fistL")
HERO_ARM_R = ("upperR", "foreR", "fistR")
G_L, G_R = ("gupperL", "gforeL", "gfistL"), ("gupperR", "gforeR", "gfistR")
O_L, O_R = ("oupperL", "oforeL", "ofistL"), ("oupperR", "oforeR", "ofistR")
B_L, B_R = ("bupperL", "bforeL", "bfistL"), ("bupperR", "bforeR", "bfistR")
LIMB_L = ("armL_shoulder", "armL_upper", "armL_elbow", "armL_fore", "armL_hand")
LIMB_R = ("armR_shoulder", "armR_upper", "armR_elbow", "armR_fore", "armR_hand")

# The same arms WITHOUT their shoulder balls, for a two-handed grip. That swing
# pivots about the midpoint between the shoulders, so a shoulder ball taken along
# sweeps from beside the head to above it and lands across the face. Leave the
# balls on the torso: they bury the upper arms' tops, so no gap opens at the
# joint. A ONE-handed pivot is the opposite case -- there the ball is the joint
# itself and turns in place, so those entries keep it.
ARM_L, ARM_R = LIMB_L[1:], LIMB_R[1:]

ATTACKS = [
    # ---- heroes -------------------------------------------------------------
    # A TWO-HANDED OVERHEAD CHOP, on INVERSE KINEMATICS rather than a pivot.
    #
    # The pivot version was rejected as "holding the sword at crotch-level and
    # flicking it at the enemy" (user, 2026-08-02), and it could not have been
    # anything else. A pivot welds the arms and the sword into one rigid piece,
    # so raising the blade means rotating that piece about the shoulders, and
    # that rotation had to stay under 20 degrees or the shoulder balls slid off
    # the torso. His fists therefore never left his hips and the only motion left
    # on screen was the blade turning through his grip.
    #
    # Driving the sword instead lets the hilt CLIMB to head height, which is what
    # a chop is, and each arm is solved to reach its own grip so the elbows bend
    # to follow. Nothing rotates about a shoulder, so nothing can be torn off one.
    Attack("hero_fighter", "build_hero_fighter", [], A.CHOP_SWORD, cell=176,
           ik=IK("sword_root",
                 [{"shoulder": ("^upperL",), "upper": "upperL", "fore": "foreL",
                   "hand": "fistL", "pole": (-1.1, 0.30, -0.8)},
                  {"shoulder": ("^upperR",), "upper": "upperR", "fore": "foreR",
                   "hand": "fistR", "pole": (1.1, 0.30, -0.8)}],
                 mid="hands")),
    # A DRAW AND A LOOSE, on INVERSE KINEMATICS. The pivot version turned his
    # string arm about its shoulder and was rejected as "just punching himself in
    # the stomach" (user, 2026-08-02). His string hand rests at his belly, so a
    # rotation about the shoulder can only carry it around his belly; a draw is
    # the hand TRAVELLING to the face, which is the one thing a pivot cannot do.
    #
    # The bow is driven and the bow arm follows it up and out. The string hand
    # holds the same bow but carries its own world-space `track`, so it leaves the
    # bow, goes back to the cheek and returns. The bowstring and the arrow stay on
    # the bow, because an arm that takes them carries them off the limbs.
    Attack("hero_ranged", "build_hero_ranged", [], A.BOW_BODY, cell=128,
           ik=IK([{"root": "bow_root", "frames": A.BOW_PUSH, "mid": "bowgrip"}],
                 [{"shoulder": ("^upperL",), "upper": "upperL", "fore": "foreL",
                   "hand": "fistL", "pole": "rest", "joint": "segment"},
                  {"shoulder": ("^upperR",), "upper": "upperR", "fore": "foreR",
                   "hand": "fistR", "pole": "rest", "joint": "segment",
                   "track": A.BOW_HAND}])),
    # He BLESSES rather than casts. All three staff heroes ran `CAST` and played
    # the identical animation (user, 2026-08-02); his is the one that holds at the
    # top of the raise.
    Attack("hero_mender", "build_hero_mender",
           [Swing([("armL_hand",)], (), "staff_root", frames=A.BLESS_HAND, parent=1),
            Swing([("^armL_upper",)], ARM_L, frames=A.BLESS)],
           A.BLESS),
    # AN OVERHAND HAMMER BLOW, on INVERSE KINEMATICS. Three pivot versions of this
    # were rejected in one day, ending with "holding his hammer upside down and
    # reverse-flicking it at the enemy, completely unhinged" (user, 2026-08-02).
    # Every one of them failed the same way: a pivot can only spin the hammer about
    # a point on the arm, and his head sits at his own shoulder height, so the
    # shoulder spun it about its own head and the wrist made it a flick.
    #
    # Driving the weapon removes the constraint that forced the upside-down carry,
    # so his hammer went back to head-UP and the head now leads the arc down. Only
    # the LEFT arm is solved: his right hand holds a shield or a holy symbol and
    # must not move.
    Attack("hero_paladin", "build_hero_paladin", [], A.HAMMER_BLOW, cell=176,
           ik=IK("hammer_root",
                 [{"shoulder": ("^upperL",), "upper": "upperL", "fore": "foreL",
                   "hand": "fistL", "pole": (-1.1, 0.30, -0.8)}],
                 mid="hands")),
    # TWIN STABS, on INVERSE KINEMATICS and TWO WEAPONS. The pivot version turned
    # each arm about its own shoulder and was rejected as "still not extending his
    # arms to make a stabbing motion" (user, 2026-08-02). It could not extend one:
    # a pivot swings a fist along an arc of fixed radius, so both hands orbited his
    # hips and only the blades turned.
    #
    # Each knife is driven along its own path and each arm is solved to reach the
    # hand that holds it, so the elbows straighten as the blades go out. The near
    # knife leads and the far one lands two frames later, which is what makes it
    # two strikes rather than one shove.
    Attack("hero_assassin", "build_hero_assassin", [], A.STAB_BODY, cell=176,
           ik=IK([{"root": "dagR_root", "frames": A.STAB_LEAD, "mid": "hands"},
                  {"root": "dagL_root", "frames": A.STAB_REAR, "mid": "hands"}],
                 [{"shoulder": ("^upperR",), "upper": "upperR", "fore": "foreR",
                   "hand": "fistR", "pole": "rest", "joint": "segment", "weapon": 0},
                  {"shoulder": ("^upperL",), "upper": "upperL", "fore": "foreL",
                   "hand": "fistL", "pole": "rest", "joint": "segment", "weapon": 1}])),
    # He JABS: the staff goes straight out off the longest step any hero takes.
    Attack("hero_battlemage", "build_hero_battlemage",
           [Swing([("armL_hand",)], (), "staff_root", frames=A.JAB_HAND, parent=1),
            Swing([("^armL_upper",)], ARM_L, frames=A.JAB)],
           A.JAB),
    # His banner IS his polearm (user 2026-08-02) and he carries no sword, so
    # this drove a `sword_root` that no longer exists. `pivot_arm` would not have
    # raised on it either -- it only fails when NOTHING matches, so the arm parts
    # alone kept it quiet and it would have swung an empty hand.
    # The 192 cell is VERIFIED: rendered 2026-08-02, and the polearm stays inside
    # the frame through the whole swing.
    # TWO-HANDED now that both hands are on the pole. Same construction as the
    # fighter: the arms, both pauldrons and the banner turn as ONE piece about the
    # midpoint between the shoulder joints so no hand can leave the pole, and that
    # rotation stays small because it is the one that slides the pauldrons off the
    # torso. The reach comes from the pole's own pivot at the fists.
    Attack("hero_banneret", "build_hero_banneret",
           [Swing([("fistL",), ("fistR",)], (), "banner_root",
                  frames=A.POLE_HEAD, parent=1),
            Swing([("^upperL",), ("^upperR",)],
                  HERO_ARM_L + HERO_ARM_R + ("pauldron",), frames=A.POLE_ARM)],
           A.POLE_ARM, cell=224),
    # He SWEEPS: the widest arc of the three staff heroes, and he never steps.
    Attack("hero_frostadept", "build_hero_frostadept",
           [Swing([("armL_hand",)], (), "staff_root", frames=A.FROST_HAND, parent=1),
            Swing([("^armL_upper",)], ARM_L, frames=A.FROST)],
           A.FROST, cell=144),

    # ---- goblin raid --------------------------------------------------------
    Attack("goblin_skirmisher", "build_goblin_skirmisher",
           _dual(G_L, G_R, "dagL_root", "dagR_root"), A.SLASH),
    Attack("goblin_caster", "build_goblin_caster",
           [([("gshoulder",)], G_L, "sling_root")], A.LOOSE),
    Attack("goblin_shaman", "build_goblin_shaman",
           [([("gshoulder",)], G_L, "staff_root")], A.CAST),
    Attack("goblin_sapper", "build_goblin_sapper",
           [([("gupperL",), ("gupperR",)], G_L + G_R, "pick_root")],
           A.SMASH),
    Attack("goblin_boss", "build_goblin_boss",
           [([("gshoulder",)], G_R, "blade_root")], A.OVERHAND, cell=208),

    # ---- orc warband --------------------------------------------------------
    Attack("orc_brute", "build_orc_brute",
           [([("oupperL",), ("oupperR",)], O_L + O_R, "maul_root")],
           A.SMASH, cell=144),
    Attack("orc_skirmisher", "build_orc_skirmisher",
           _dual(O_L, O_R, "axeL_root", "axeR_root"), A.SLASH),
    Attack("orc_caster", "build_orc_caster",
           [([("oshoulder",)], O_L, "staff_root")], A.CAST),
    Attack("orc_shaman", "build_orc_shaman",
           [([("oshoulder",)], O_L, "staff_root")], A.CAST),
    Attack("orc_sapper", "build_orc_sapper",
           [([("oshoulder",)], O_R, "torch_root")], A.SLASH, cell=144),
    Attack("orc_boss", "build_orc_boss",
           [([("oupperL",), ("oupperR",)], O_L + O_R, "axe_root")],
           A.SWEEP, cell=208),

    # ---- bandit horde -------------------------------------------------------
    Attack("bandit_brute", "build_bandit_brute",
           [([("bupperL",), ("bupperR",)], B_L + B_R, "club_root")],
           A.SMASH),
    Attack("bandit_skirmisher", "build_bandit_skirmisher",
           _dual(B_L, B_R, "knifeL_root", "knifeR_root"), A.SLASH),
    Attack("bandit_caster", "build_bandit_caster",
           [([("bupperL",), ("bupperR",)], B_L + B_R, "bow_root")],
           A.LOOSE),
    Attack("bandit_shaman", "build_bandit_shaman",
           [([("bshoulder",)], B_R, "bottle_root")], A.CAST),
    Attack("bandit_sapper", "build_bandit_sapper",
           [([("bshoulder",)], B_L, "torch_root")], A.SLASH, cell=144),
    Attack("bandit_boss", "build_bandit_boss",
           [([("bshoulder",)], B_R, "bow_root")], A.LOOSE, cell=144),

    # ---- undead legion ------------------------------------------------------
    # His arm parts share a name on both sides, which is exactly the case the
    # rigid-pivot technique handles and inverse kinematics cannot.
    Attack("undead_brute", "build_undead_brute",
           [([("pauldron",)], ("upper", "fore", "bonehand", "pauldron"), "sword_root")],
           A.SMASH),
    Attack("undead_skirmisher", "build_undead_skirmisher",
           _dual(("upperL", "foreL", "handL"), ("upperR", "foreR", "handR"),
                 "bladeL_root", "bladeR_root"), A.SLASH),
    Attack("undead_caster", "build_undead_caster",
           [([("shoulderL",)], ("sleeveA1", "sleeveA2", "handA"), "staff_root")], A.CAST),
    Attack("undead_shaman", "build_undead_shaman",
           [([("armL_shoulder",)], LIMB_L, "staff_root")], A.CAST),
    Attack("undead_sapper", "build_undead_sapper",
           [([("armL_shoulder",)], LIMB_L, "shovel_root")], A.OVERHAND),
    Attack("undead_boss", "build_undead_boss",
           [([("armL_shoulder",)], LIMB_L, "staff_root")], A.CAST, cell=176),

    # ---- infernal siege -----------------------------------------------------
    Attack("infernal_brute", "build_infernal_brute",
           [([("armL_shoulder",), ("armR_shoulder",)], ARM_L + ARM_R + ("iclaw",),
             "cleaver_root")], A.SMASH, cell=160),
    # The only quadruped: no arms to swing, so the attack is a head-snap driven
    # from the neck.
    Attack("infernal_skirmisher", "build_infernal_skirmisher",
           [([("ineck",)], ("iskull", "isnout", "iear", "ifangs", "ieye", "imane"), None)],
           BITE, cell=144),
    # No weapon root: the hellfire arc IS the weapon, so it swings with the arms.
    Attack("infernal_caster", "build_infernal_caster",
           [([("armL_shoulder",), ("armR_shoulder",)],
             ARM_L + ARM_R + ("iclaw", "iarc", "ispark"), None)], A.CAST),
    Attack("infernal_shaman", "build_infernal_shaman",
           [([("armR_shoulder",)], LIMB_R + ("iclaw",), "chalice_root")], A.CAST),
    Attack("infernal_sapper", "build_infernal_sapper",
           [([("armL_shoulder",), ("armR_shoulder",)], ARM_L + ARM_R + ("iclaw",),
             "brazier_root")], A.CAST),
    Attack("infernal_boss", "build_infernal_boss",
           [([("armL_shoulder",)], LIMB_L + ("iclaw",), "scepter_root")], A.CAST, cell=176),
]


# ---- hero rarity variants -------------------------------------------------
# A variant is the same model re-dressed, so it reuses its hero's entry entirely
# and only sets HERO_TIER. The angles cannot need changing, because nothing about
# the figure's proportions changes.

_BASE_TIER = {"hero_mender": "rare", "hero_paladin": "epic"}
_TIERS = ("common", "rare", "epic", "legendary")

_variants = []
for _a in ATTACKS:
    if not _a.key.startswith("hero_"):
        continue
    for _t in _TIERS:
        if _t == _BASE_TIER.get(_a.key, "common"):
            continue
        _variants.append(Attack(_a.key + "_" + _t, _a.module, _a.groups, _a.frames,
                                _a.cell, env={"HERO_TIER": _t}, ik=_a.ik))
ATTACKS += _variants


# The groups a human reviews an ANIMATION in, and the names their contact sheets
# are published under. Lives here, not in `compose_attack_contact`, because
# `publish.py` runs under the SYSTEM Python and must be able to read it without
# Blender -- the same reason `attack_shapes` carries no `bpy` import.
#
# Heroes are split from their rarity variants because 32 rows in one image is
# about 15,000 pixels tall.
SHEET_GROUPS = [
    ("heroes",   ["=hero_fighter", "=hero_ranged", "=hero_mender", "=hero_paladin",
                  "=hero_assassin", "=hero_battlemage", "=hero_banneret",
                  "=hero_frostadept"]),
    ("variants", ["hero_"]),
    ("goblin",   ["goblin_"]),
    ("orc",      ["orc_"]),
    ("bandit",   ["bandit_"]),
    ("undead",   ["undead_"]),
    ("infernal", ["infernal_"]),
]
