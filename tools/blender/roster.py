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
    def __init__(self, entry, key, module, out, group, cell=112, note="", env=None):
        self.entry = entry
        self.key = key
        self.module = module        # tools/blender/<module>.py, or None if unbuilt
        self.out = out              # filename inside out/
        self.group = group
        self.cell = cell
        self.note = note
        # Environment for this render. A hero rarity variant is the same builder
        # dressed differently, so it reuses the module and sets HERO_TIER rather
        # than existing as a script of its own.
        self.env = env or {}

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
    Asset(1, "hero_fighter", "build_hero_fighter", "out_hero_fighter.png", "heroes", 112),
    Asset(2, "hero_ranged", "build_hero_ranged", "out_hero_ranged.png", "heroes", 112),
    Asset(3, "hero_mender", "build_hero_mender", "out_hero_mender.png", "heroes", 112),
    Asset(4, "hero_paladin", "build_hero_paladin", "out_hero_paladin.png", "heroes", 112),
    Asset(5, "hero_assassin", "build_hero_assassin", "out_hero_assassin.png", "heroes", 112),
    Asset(6, "hero_battlemage", "build_hero_battlemage", "out_hero_battlemage.png", "heroes", 112),
    Asset(7, "hero_banneret", "build_hero_banneret", "out_hero_banneret.png", "heroes", 128),
    Asset(8, "hero_frostadept", "build_hero_frostadept", "out_hero_frostadept.png", "heroes", 112),

    # ---- hero rarity variants (entries 56-82) --------------------------------
    # Same builder, dressed by HERO_TIER. Each hero's OWN sprite already
    # occupies one tier and that tier gets no file, per the audit in
    # M15_ASSET_SPECS.md -- the game falls back to the base sprite for it.
    Asset(56, "knight_rare", "build_knight", "out_knight_rare.png", "variants", 96,
          env={"HERO_TIER": "rare"}),
    Asset(57, "knight_epic", "build_knight", "out_knight_epic.png", "variants", 96,
          env={"HERO_TIER": "epic"}),
    Asset(58, "knight_legendary", "build_knight", "out_knight_legendary.png", "variants", 96,
          env={"HERO_TIER": "legendary"}),
    Asset(59, "hero_fighter_rare", "build_hero_fighter", "out_hero_fighter_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(60, "hero_fighter_epic", "build_hero_fighter", "out_hero_fighter_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(61, "hero_fighter_legendary", "build_hero_fighter", "out_hero_fighter_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(62, "hero_ranged_rare", "build_hero_ranged", "out_hero_ranged_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(63, "hero_ranged_epic", "build_hero_ranged", "out_hero_ranged_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(64, "hero_ranged_legendary", "build_hero_ranged", "out_hero_ranged_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(65, "hero_mender_common", "build_hero_mender", "out_hero_mender_common.png", "variants", 112,
          env={"HERO_TIER": "common"}),
    Asset(66, "hero_mender_epic", "build_hero_mender", "out_hero_mender_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(67, "hero_mender_legendary", "build_hero_mender", "out_hero_mender_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(68, "hero_paladin_common", "build_hero_paladin", "out_hero_paladin_common.png", "variants", 112,
          env={"HERO_TIER": "common"}),
    Asset(69, "hero_paladin_rare", "build_hero_paladin", "out_hero_paladin_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(70, "hero_paladin_legendary", "build_hero_paladin", "out_hero_paladin_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(71, "hero_assassin_rare", "build_hero_assassin", "out_hero_assassin_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(72, "hero_assassin_epic", "build_hero_assassin", "out_hero_assassin_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(73, "hero_assassin_legendary", "build_hero_assassin", "out_hero_assassin_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(74, "hero_battlemage_rare", "build_hero_battlemage", "out_hero_battlemage_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(75, "hero_battlemage_epic", "build_hero_battlemage", "out_hero_battlemage_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(76, "hero_battlemage_legendary", "build_hero_battlemage", "out_hero_battlemage_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),
    Asset(77, "hero_banneret_rare", "build_hero_banneret", "out_hero_banneret_rare.png", "variants", 128,
          env={"HERO_TIER": "rare"}),
    Asset(78, "hero_banneret_epic", "build_hero_banneret", "out_hero_banneret_epic.png", "variants", 128,
          env={"HERO_TIER": "epic"}),
    Asset(79, "hero_banneret_legendary", "build_hero_banneret", "out_hero_banneret_legendary.png", "variants", 128,
          env={"HERO_TIER": "legendary"}),
    Asset(80, "hero_frostadept_rare", "build_hero_frostadept", "out_hero_frostadept_rare.png", "variants", 112,
          env={"HERO_TIER": "rare"}),
    Asset(81, "hero_frostadept_epic", "build_hero_frostadept", "out_hero_frostadept_epic.png", "variants", 112,
          env={"HERO_TIER": "epic"}),
    Asset(82, "hero_frostadept_legendary", "build_hero_frostadept", "out_hero_frostadept_legendary.png", "variants", 112,
          env={"HERO_TIER": "legendary"}),

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
    # Buildings render at the CHARACTER pixel density (see building_kit.py), so
    # their cells are large: a building stands about twice a character's height
    # and the density is the same, so it needs about twice the pixels.
    Asset(47, "cottage", "build_cottage", "out_cottage.png", "buildings", 192),
    Asset(48, "tavern", "build_tavern", "out_tavern.png", "buildings", 224),
    Asset(49, "smithy", "build_smithy", "out_smithy.png", "buildings", 192),
    Asset(50, "workshop", "build_workshop", "out_workshop.png", "buildings", 192),
    Asset(51, "library", "build_library", "out_library.png", "buildings", 224),
    Asset(52, "keep", "build_keep", "out_keep.png", "buildings", 224),
    Asset(53, "apothecary", "build_apothecary", "out_apothecary.png", "buildings", 192),
    Asset(54, "tower", "build_tower", "out_tower.png", "buildings", 256),
    Asset(55, "cathedral", "build_cathedral", "out_cathedral.png", "buildings", 256),

    # ---- townsfolk ----------------------------------------------------------
    # The only figures in the game not holding a weapon, which is their read.
    # Same height as the heroes, per the size ruling.
    Asset(9, "town_villager", "build_town_villager", "out_town_villager.png", "townsfolk", 112),
    Asset(10, "town_tavernkeeper", "build_town_tavernkeeper", "out_town_tavernkeeper.png", "townsfolk", 112),
    Asset(11, "town_blacksmith", "build_town_blacksmith", "out_town_blacksmith.png", "townsfolk", 112),
    Asset(12, "town_scholar", "build_town_scholar", "out_town_scholar.png", "townsfolk", 112),
    Asset(13, "town_builder", "build_town_builder", "out_town_builder.png", "townsfolk", 112),
    Asset(14, "town_alchemist", "build_town_alchemist", "out_town_alchemist.png", "townsfolk", 112),
    Asset(15, "town_mage", "build_town_mage", "out_town_mage.png", "townsfolk", 112),
    Asset(16, "town_highpriest", "build_town_highpriest", "out_town_highpriest.png", "townsfolk", 112),
]

GROUPS = ["heroes", "variants", "goblin", "orc", "bandit", "undead",
          "infernal", "buildings", "townsfolk"]


def by_group(group):
    return [a for a in ROSTER if a.group == group]


def built():
    return [a for a in ROSTER if a.built]


def todo():
    return [a for a in ROSTER if not a.built]
