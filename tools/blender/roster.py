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
    # USER RULING 2026-07-31: normal enemies and heroes are all roughly one size
    # and bosses are much bigger, so height is set by ROLE in spritekit.py, not
    # per family. A goblin is a goblin because he is WIRY, not because he is short.
    Asset(17, "goblin_skirmisher", "build_goblin_skirmisher", "out_goblin_skirmisher.png", "goblin", 112),
    Asset(18, "goblin_caster", "build_goblin_caster", "out_goblin_caster.png", "goblin", 112),
    Asset(19, "goblin_shaman", "build_goblin_shaman", "out_goblin_shaman.png", "goblin", 112),
    Asset(20, "goblin_sapper", "build_goblin_sapper", "out_goblin_sapper.png", "goblin", 112),
    Asset(21, "goblin_boss", "build_goblin_boss", "out_goblin_boss.png", "goblin", 144,
          "BOSS: the Goblin Warmaster"),

    # ---- orc warband --------------------------------------------------------
    # Orcs are the BROAD family, not the tall one -- see the ruling above.
    Asset(22, "orc_brute", "build_orc_brute", "out_orc_brute.png", "orc", 112),
    Asset(23, "orc_skirmisher", "build_orc_skirmisher", "out_orc_skirmisher.png", "orc", 112),
    Asset(24, "orc_caster", "build_orc_caster", "out_orc_caster.png", "orc", 112),
    Asset(25, "orc_shaman", "build_orc_shaman", "out_orc_shaman.png", "orc", 112),
    Asset(26, "orc_sapper", "build_orc_sapper", "out_orc_sapper.png", "orc", 112),
    Asset(27, "orc_boss", "build_orc_boss", "out_orc_boss.png", "orc", 144,
          "BOSS: the Orc Warlord"),

    # ---- bandit horde -------------------------------------------------------
    # The first HUMAN enemies: same build and skin as the heroes, so the faction
    # is carried by covered faces, worn browns and gear that does not fit.
    Asset(28, "bandit_brute", "build_bandit_brute", "out_bandit_brute.png", "bandit", 112),
    Asset(29, "bandit_skirmisher", "build_bandit_skirmisher", "out_bandit_skirmisher.png", "bandit", 112),
    Asset(30, "bandit_caster", "build_bandit_caster", "out_bandit_caster.png", "bandit", 112),
    Asset(31, "bandit_shaman", "build_bandit_shaman", "out_bandit_shaman.png", "bandit", 112),
    Asset(32, "bandit_sapper", "build_bandit_sapper", "out_bandit_sapper.png", "bandit", 112),
    Asset(33, "bandit_boss", "build_bandit_boss", "out_bandit_boss.png", "bandit", 144,
          "BOSS: the Bandit King"),

    # ---- undead legion ------------------------------------------------------
    Asset(34, "undead_brute", "build_undead_brute", "out_undead_brute.png", "undead", 112),
    Asset(35, "undead_skirmisher", "build_undead_skirmisher", "out_undead_skirmisher.png", "undead", 112),
    Asset(36, "undead_caster", "build_undead_caster", "out_undead_caster.png",
          "undead", 112, "the necromancer; built from spec prose with no reference"),
    Asset(37, "undead_shaman", "build_undead_shaman", "out_undead_shaman.png", "undead", 112),
    Asset(38, "undead_sapper", "build_undead_sapper", "out_undead_sapper.png", "undead", 112),
    Asset(39, "undead_boss", "build_undead_boss", "out_undead_boss.png", "undead", 144,
          "BOSS: the Lich Commander"),

    # ---- infernal siege -----------------------------------------------------
    # The only family that is NOT five variants on one build: 41 is a quadruped
    # and 44 is winged, so infernal_kit carries only palette, horns and cracks.
    Asset(40, "infernal_brute", "build_infernal_brute", "out_infernal_brute.png", "infernal", 112),
    Asset(41, "infernal_skirmisher", "build_infernal_skirmisher", "out_infernal_skirmisher.png",
          "infernal", 112, "hellhound: four legs, turned further round than the others"),
    Asset(42, "infernal_caster", "build_infernal_caster", "out_infernal_caster.png", "infernal", 112),
    Asset(43, "infernal_shaman", "build_infernal_shaman", "out_infernal_shaman.png", "infernal", 112),
    Asset(44, "infernal_sapper", "build_infernal_sapper", "out_infernal_sapper.png", "infernal", 112,
          "cinder imp: small by PROPORTION, since role sets the height"),
    Asset(45, "infernal_boss", "build_infernal_boss", "out_infernal_boss.png", "infernal", 144,
          "BOSS: the Demon Empress, the series showpiece"),

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
