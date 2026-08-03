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
    def __init__(self, key, module, groups, frames, cell=128, env=None):
        self.key = key
        self.module = module
        self.groups = [Swing.of(g) for g in groups]
        self.frames = frames
        self.cell = cell
        self.env = env or {}


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
    # A TWO-HANDED CHOP. His fists are 0.65 apart on the hilt, so the arms, both
    # shoulder balls and the sword turn as ONE piece about the midpoint between his
    # shoulder joints -- nothing can leave anything. That rotation stays under 20
    # degrees because it is the one that slides the balls off the torso. The blade's
    # reach comes from the second pivot, which turns the sword about the point
    # between his fists.
    Attack("hero_fighter", "build_hero_fighter",
           [Swing([("fistL",), ("fistR",)], (), "sword_root",
                  frames=A.CHOP_BLADE, parent=1),
            Swing([("^upperL",), ("^upperR",)],
                  HERO_ARM_L + HERO_ARM_R + ("shoulder",), frames=A.CHOP_ARMS)],
           A.CHOP_ARMS),
    # THE DRAWING ARM AND NOTHING ELSE. The bow, the string and the arrow all stay
    # put: handing the string to the arm carried it off the bow limbs, and it read
    # as him waving a loose bowstring at the enemy (user, 2026-08-02).
    Attack("hero_ranged", "build_hero_ranged",
           [Swing([("^upperR",)], HERO_ARM_R, frames=A.BOW_DRAW)],
           A.BOW_BODY),
    # He BLESSES rather than casts. All three staff heroes ran `CAST` and played
    # the identical animation (user, 2026-08-02); his is the one that holds at the
    # top of the raise.
    Attack("hero_mender", "build_hero_mender",
           [Swing([("armL_hand",)], (), "staff_root", frames=A.BLESS_HAND, parent=1),
            Swing([("^armL_upper",)], ARM_L, frames=A.BLESS)],
           A.BLESS),
    # SHOULDER, then WRIST. His hammer head sits at his own shoulder height, so a
    # shoulder rotation alone spins the hammer about its own head and a wrist
    # rotation alone is a flick; both were rejected (user, 2026-08-02). Chained,
    # the shoulder throws the fist across and the wrist carries the head through
    # another haft-length the same way.
    Attack("hero_paladin", "build_hero_paladin",
           [Swing([("fistL",)], (), "hammer_root", frames=A.HAMMER_WRIST, parent=1),
            Swing([("^upperL",)], HERO_ARM_L, frames=A.HAMMER_SWING)],
           A.HAMMER_SWING),
    # TWIN DAGGERS on real joints: each arm about the TOP OF ITS OWN UPPER ARM,
    # which is its shoulder and the one point a rotation leaves in place, and each
    # blade about its own fist. The drive comes from the arms extending; the step
    # stays small, because a body sliding forward with nothing else changing read
    # as him thrusting his pelvis at the enemy (user, 2026-08-02).
    Attack("hero_assassin", "build_hero_assassin",
           [Swing([("fistL",)], (), "dagL_root", frames=A.DAGGER_WRIST, parent=2),
            Swing([("fistR",)], (), "dagR_root", frames=A.DAGGER_WRIST, parent=3),
            Swing([("^upperL",)], HERO_ARM_L, frames=A.DAGGER_ARM),
            Swing([("^upperR",)], HERO_ARM_R, frames=A.DAGGER_ARM)],
           A.DAGGER_ARM, cell=144),
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
                                _a.cell, env={"HERO_TIER": _t}))
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
