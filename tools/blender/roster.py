"""The asset manifest: every sprite the game needs, and which builder makes it.

Plain data with no `bpy` import, so both the system Python (`render_all.py`) and
Blender's Python (`compose_contact.py`) can read it. Entry numbers are the ones
in `M15_ASSET_SPECS.md`, which stays the source of truth for what each asset
depicts; this file only records how it gets built.

`cell` is the render resolution in pixels, which is how a figure is fitted. Never
change the ortho scale to fit a character -- see the scale-matching section of
README.md.
"""


class Asset:
    def __init__(self, entry, key, module, out, group, cell=112, note=""):
        self.entry = entry
        self.key = key
        self.module = module        # tools/blender/<module>.py, or None if unbuilt
        self.out = out              # filename inside out/
        self.group = group
        self.cell = cell
        self.note = note

    @property
    def built(self):
        return self.module is not None

    def __repr__(self):
        return "<%s %s %s>" % (self.entry, self.key, "built" if self.built else "TODO")


def _todo(entry, key, group, cell=112, note=""):
    return Asset(entry, key, None, "out_%s.png" % key, group, cell, note)


ROSTER = [
    # ---- heroes (face right) ------------------------------------------------
    Asset(0, "knight", "build_knight", "out_knight.png", "heroes", 96,
          "the guardian; the style anchor for every other character"),
    _todo(1, "hero_fighter", "heroes"),
    _todo(2, "hero_ranged", "heroes"),
    _todo(3, "hero_mender", "heroes"),
    _todo(4, "hero_paladin", "heroes"),
    _todo(5, "hero_assassin", "heroes"),
    _todo(6, "hero_battlemage", "heroes"),
    _todo(7, "hero_banneret", "heroes"),
    _todo(8, "hero_frostadept", "heroes"),

    # ---- goblin raid (face left) -------------------------------------------
    Asset(0, "goblin", "build_goblin", "out_goblin.png", "goblin", 112,
          "the brute; the family's body plan"),
    _todo(17, "goblin_skirmisher", "goblin"),
    _todo(18, "goblin_caster", "goblin"),
    _todo(19, "goblin_shaman", "goblin"),
    _todo(20, "goblin_sapper", "goblin"),
    _todo(21, "goblin_boss", "goblin", 128, "BOSS: the Goblin Warmaster"),

    # ---- orc warband --------------------------------------------------------
    _todo(22, "orc_brute", "orc", 128),
    _todo(23, "orc_skirmisher", "orc", 128),
    _todo(24, "orc_caster", "orc", 128),
    _todo(25, "orc_shaman", "orc", 128),
    _todo(26, "orc_sapper", "orc", 128),
    _todo(27, "orc_boss", "orc", 144, "BOSS: the Orc Warlord"),

    # ---- bandit horde -------------------------------------------------------
    _todo(28, "bandit_brute", "bandit"),
    _todo(29, "bandit_skirmisher", "bandit"),
    _todo(30, "bandit_caster", "bandit"),
    _todo(31, "bandit_shaman", "bandit"),
    _todo(32, "bandit_sapper", "bandit"),
    _todo(33, "bandit_boss", "bandit", 128, "BOSS: the Bandit King"),

    # ---- undead legion ------------------------------------------------------
    _todo(34, "undead_brute", "undead", 128),
    _todo(35, "undead_skirmisher", "undead"),
    Asset(36, "undead_caster", "build_undead_caster", "out_undead_caster.png",
          "undead", 112, "the necromancer; built from spec prose with no reference"),
    _todo(37, "undead_shaman", "undead"),
    _todo(38, "undead_sapper", "undead"),
    _todo(39, "undead_boss", "undead", 144, "BOSS: the Lich Commander"),

    # ---- infernal siege -----------------------------------------------------
    _todo(40, "infernal_brute", "infernal", 128),
    _todo(41, "infernal_skirmisher", "infernal", 128, "hellhound: four legs, side-on"),
    _todo(42, "infernal_caster", "infernal"),
    _todo(43, "infernal_shaman", "infernal"),
    _todo(44, "infernal_sapper", "infernal", 96, "cinder imp: small and winged"),
    _todo(45, "infernal_boss", "infernal", 144, "BOSS: the Demon Empress"),

    # ---- buildings (near-isometric camera, not the sprite camera) -----------
    Asset(47, "cottage", "build_cottage", "out_cottage.png", "buildings", 128),
    _todo(48, "tavern", "buildings", 128),
    _todo(49, "smithy", "buildings", 128),
    _todo(50, "workshop", "buildings", 128),
    _todo(51, "library", "buildings", 128),
    _todo(52, "keep", "buildings", 128),
    _todo(53, "apothecary", "buildings", 128),
    _todo(54, "tower", "buildings", 144),
    _todo(55, "cathedral", "buildings", 160),

    # ---- townsfolk ----------------------------------------------------------
    _todo(9, "town_villager", "townsfolk", 96),
    _todo(10, "town_tavernkeeper", "townsfolk", 96),
    _todo(11, "town_blacksmith", "townsfolk", 96),
    _todo(12, "town_scholar", "townsfolk", 96),
    _todo(13, "town_builder", "townsfolk", 96),
    _todo(14, "town_alchemist", "townsfolk", 96),
    _todo(15, "town_mage", "townsfolk", 96),
    _todo(16, "town_highpriest", "townsfolk", 96),
]

# Hero rarity variants (entries 56-82) are deliberately absent until their base
# hero exists: a variant is the same figure re-dressed, so it is a parameter on
# the base builder rather than a script of its own. See M15_ASSET_SPECS.md for
# which tier each base sprite already occupies -- the audited tier gets no file.

GROUPS = ["heroes", "goblin", "orc", "bandit", "undead", "infernal",
          "buildings", "townsfolk"]


def by_group(group):
    return [a for a in ROSTER if a.group == group]


def built():
    return [a for a in ROSTER if a.built]


def todo():
    return [a for a in ROSTER if not a.built]
