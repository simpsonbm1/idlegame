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
        self.groups = groups
        self.frames = frames
        self.cell = cell
        self.env = env or {}


def _dual(sh, left, right, lroot, rroot):
    return [(sh, left, lroot), (sh, right, rroot)]


HERO_ARM_L = ("upperL", "foreL", "fistL")
HERO_ARM_R = ("upperR", "foreR", "fistR")
G_L, G_R = ("gupperL", "gforeL", "gfistL"), ("gupperR", "gforeR", "gfistR")
O_L, O_R = ("oupperL", "oforeL", "ofistL"), ("oupperR", "oforeR", "ofistR")
B_L, B_R = ("bupperL", "bforeL", "bfistL"), ("bupperR", "bforeR", "bfistR")
LIMB_L = ("armL_shoulder", "armL_upper", "armL_elbow", "armL_fore", "armL_hand")
LIMB_R = ("armR_shoulder", "armR_upper", "armR_elbow", "armR_fore", "armR_hand")

ATTACKS = [
    # ---- heroes -------------------------------------------------------------
    Attack("hero_fighter", "build_hero_fighter",
           [([("upperL",), ("upperR",)], HERO_ARM_L + HERO_ARM_R + ("shoulder",), "sword_root")],
           A.SMASH),
    Attack("hero_ranged", "build_hero_ranged",
           [([("upperL",), ("upperR",)], HERO_ARM_L + HERO_ARM_R + ("shoulder",), "bow_root")],
           A.LOOSE),
    Attack("hero_mender", "build_hero_mender",
           [([("armL_shoulder",)], LIMB_L, "staff_root")], A.CAST),
    Attack("hero_paladin", "build_hero_paladin",
           [([("pauldron",)], HERO_ARM_L, "hammer_root")], A.OVERHAND),
    Attack("hero_assassin", "build_hero_assassin",
           _dual([("shoulder",)], HERO_ARM_L, HERO_ARM_R, "dagL_root", "dagR_root"),
           A.SLASH),
    Attack("hero_battlemage", "build_hero_battlemage",
           [([("armL_shoulder",)], LIMB_L, "staff_root")], A.CAST),
    Attack("hero_banneret", "build_hero_banneret",
           [([("pauldron",)], HERO_ARM_R, "sword_root")], A.SLASH, cell=144),
    Attack("hero_frostadept", "build_hero_frostadept",
           [([("armL_shoulder",)], LIMB_L, "staff_root")], A.CAST),

    # ---- goblin raid --------------------------------------------------------
    Attack("goblin_skirmisher", "build_goblin_skirmisher",
           _dual([("gshoulder",)], G_L, G_R, "dagL_root", "dagR_root"), A.SLASH),
    Attack("goblin_caster", "build_goblin_caster",
           [([("gshoulder",)], G_L, "sling_root")], A.LOOSE),
    Attack("goblin_shaman", "build_goblin_shaman",
           [([("gshoulder",)], G_L, "staff_root")], A.CAST),
    Attack("goblin_sapper", "build_goblin_sapper",
           [([("gupperL",), ("gupperR",)], G_L + G_R + ("gshoulder",), "pick_root")],
           A.SMASH),
    Attack("goblin_boss", "build_goblin_boss",
           [([("gshoulder",)], G_R, "blade_root")], A.OVERHAND, cell=144),

    # ---- orc warband --------------------------------------------------------
    Attack("orc_brute", "build_orc_brute",
           [([("oupperL",), ("oupperR",)], O_L + O_R + ("oshoulder",), "maul_root")],
           A.SMASH),
    Attack("orc_skirmisher", "build_orc_skirmisher",
           _dual([("oshoulder",)], O_L, O_R, "axeL_root", "axeR_root"), A.SLASH),
    Attack("orc_caster", "build_orc_caster",
           [([("oshoulder",)], O_L, "staff_root")], A.CAST),
    Attack("orc_shaman", "build_orc_shaman",
           [([("oshoulder",)], O_L, "staff_root")], A.CAST),
    Attack("orc_sapper", "build_orc_sapper",
           [([("oshoulder",)], O_R, "torch_root")], A.SLASH),
    Attack("orc_boss", "build_orc_boss",
           [([("oupperL",), ("oupperR",)], O_L + O_R + ("oshoulder",), "axe_root")],
           A.SWEEP, cell=176),

    # ---- bandit horde -------------------------------------------------------
    Attack("bandit_brute", "build_bandit_brute",
           [([("bupperL",), ("bupperR",)], B_L + B_R + ("bshoulder",), "club_root")],
           A.SMASH),
    Attack("bandit_skirmisher", "build_bandit_skirmisher",
           _dual([("bshoulder",)], B_L, B_R, "knifeL_root", "knifeR_root"), A.SLASH),
    Attack("bandit_caster", "build_bandit_caster",
           [([("bupperL",), ("bupperR",)], B_L + B_R + ("bshoulder",), "bow_root")],
           A.LOOSE),
    Attack("bandit_shaman", "build_bandit_shaman",
           [([("bshoulder",)], B_R, "bottle_root")], A.CAST),
    Attack("bandit_sapper", "build_bandit_sapper",
           [([("bshoulder",)], B_L, "torch_root")], A.SLASH),
    Attack("bandit_boss", "build_bandit_boss",
           [([("bshoulder",)], B_R, "bow_root")], A.LOOSE, cell=144),

    # ---- undead legion ------------------------------------------------------
    # His arm parts share a name on both sides, which is exactly the case the
    # rigid-pivot technique handles and inverse kinematics cannot.
    Attack("undead_brute", "build_undead_brute",
           [([("pauldron",)], ("upper", "fore", "bonehand", "pauldron"), "sword_root")],
           A.SMASH),
    Attack("undead_skirmisher", "build_undead_skirmisher",
           _dual([("shoulder",)], ("upperL", "foreL", "handL"), ("upperR", "foreR", "handR"),
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
           [([("armL_shoulder",), ("armR_shoulder",)], LIMB_L + LIMB_R + ("iclaw",),
             "cleaver_root")], A.SMASH),
    # The only quadruped: no arms to swing, so the attack is a head-snap driven
    # from the neck.
    Attack("infernal_skirmisher", "build_infernal_skirmisher",
           [([("ineck",)], ("iskull", "isnout", "iear", "ifangs", "ieye", "imane"), None)],
           BITE),
    # No weapon root: the hellfire arc IS the weapon, so it swings with the arms.
    Attack("infernal_caster", "build_infernal_caster",
           [([("armL_shoulder",), ("armR_shoulder",)],
             LIMB_L + LIMB_R + ("iclaw", "iarc", "ispark"), None)], A.CAST),
    Attack("infernal_shaman", "build_infernal_shaman",
           [([("armR_shoulder",)], LIMB_R + ("iclaw",), "chalice_root")], A.CAST),
    Attack("infernal_sapper", "build_infernal_sapper",
           [([("armL_shoulder",), ("armR_shoulder",)], LIMB_L + LIMB_R + ("iclaw",),
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
