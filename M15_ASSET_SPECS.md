# M15 asset run — Gemini series brief

**For Ben:** hand everything below the divider to Gemini as **one paste**, in the same
conversation that generated the knight. Save each result to `assets/raw/` under the filename
Gemini announces. If the style starts drifting mid-run (it can, in long conversations),
re-attach the original knight image and tell it to re-ground on that. Deliver batches to
Claude at any pace — order below is most-valuable-first.
Already done, skipped in the list: guardian hero (`raw_hero_knight_v3.png`), goblin brute
(`raw_enemy_goblin_brute.png`). Portraits are cropped from these sprites by the pipeline —
no separate portrait generations needed.

**Batch priority (updated 2026-07-18, after the scene-prototype sign-off):** the scene
layout (see `tools/scene-prototype.html`) changed what unblocks what. Recommended order:
1. **Section: World — town vista + buildings (entries 46–55)** — the layout overhaul is
   blocked on these; everything else already has a working fallback.
2. Remaining enemies in tier order (17–45) — battle variety for the current game.
3. Townsfolk (10–16).
4. **Hero rarity variants (56–82) — deliberately last and lazy**: the game falls back to the
   base archetype sprite per missing file, and a pipeline-drawn rarity rim covers the gap,
   so these can trickle in at any pace, in any order (rares before epics before legendaries
   matches when players actually see them).

---

I need a numbered series of sprites and scene paintings (entries 1–82) for my medieval
fantasy game, in **exactly the art style of the knight you generated earlier in this
conversation** — same palette approach, same thick dark outlines, same proportions, same
chunky pixel scale. That knight is the style anchor for the whole series: before drawing
each new entry, match it, not your most recent output. (Later sections override some rules
for buildings and scene paintings — each section states its own.)

**Work through the numbered list below one at a time, in order.** One character per image —
never a sheet. Before each image, state the entry number and filename so I can save it
correctly. After each image, wait for me to approve or ask for a correction before moving on.

**Rules for every image (unless an entry says otherwise):**
- Single character, full body with feet visible, centered, filling about 80% of the image
  height, no part touching the image edge.
- Three-quarter front view; neutral combat-idle stance; lit from the upper left.
- Facing: heroes and townsfolk face slightly RIGHT; all enemies and bosses face slightly LEFT.
- Background: plain flat solid magenta (#FF00FF) filling the entire image — no vignette, no
  texture, and no ground, dirt, or shadow under the feet.
- No text, no watermark, no frame or border, no objects other than the character and their gear.
- Style: retro fantasy RPG pixel art as if drawn on a canvas about 48 pixels tall and then
  upscaled — bold simple shapes, flat shading with at most 3 tones per surface, minimal
  dithering, thick dark outlines, mid-to-bright overall values, readable silhouette.
- Bosses (marked BOSS): fill about 85% of the image height, imposing commanding stance.

## Heroes (face slightly right)
1. [DONE] `raw_hero_fighter.png` — a hardened human footman soldier in a chainmail shirt,
   open-faced kettle helmet, and red-and-steel tabard, gripping a longsword in both hands.
2. [DONE] `raw_hero_ranged.png` — a keen-eyed human archer in a forest-green hood and brown leather
   armor, longbow with an arrow nocked but pointed down, quiver on the back.
3. [DONE] `raw_hero_mender.png` — a gentle human healer in cream-and-gold hooded robes, wooden
   staff topped with a small glowing golden sun emblem, satchel of bandages at the hip.
4. [DONE] `raw_hero_paladin.png` — a holy paladin in polished silver-white plate armor with gold
   trim, warhammer in one hand, radiant golden holy symbol in the other.
5. [DONE] `raw_hero_assassin.png` — a slim hooded assassin in dark charcoal-and-purple leathers,
   face in shadow, slightly crouched, twin curved daggers held low.
6. [DONE] `raw_hero_battlemage.png` — a battle-mage in deep blue robes with purple trim and glowing
   arcane runes on the sleeves, tall staff crackling with bright arcane blue energy.
7. [DONE] `raw_hero_banneret.png` — a banner-bearing knight in steel half-plate, tall
   crimson-and-gold war banner on a pole in one hand, short sword in the other.
8. [DONE] `raw_hero_frostadept.png` — a frost mage in pale ice-blue robes with white fur trim,
   crystal-tipped staff swirling with snowflakes and cold blue mist.

## Townsfolk (face slightly right; relaxed friendly standing pose instead of combat-idle)
9. [DONE] `raw_town_villager.png` — a cheerful villager in a simple brown tunic and straw hat,
   carrying a basket of vegetables.
10. `raw_town_tavernkeeper.png` — a stout jolly tavernkeeper, apron over rolled-up sleeves,
    foaming mug in one hand, cleaning rag in the other.
11. `raw_town_blacksmith.png` — a brawny blacksmith in a heavy leather apron, smithing
    hammer resting on one shoulder, tongs tucked in the belt.
12. `raw_town_scholar.png` — a scholar in blue robes, flat cap, and round spectacles,
    carrying a thick open book, rolled scroll under one arm.
13. `raw_town_builder.png` — a builder in a work smock and cloth cap, wooden mallet in hand,
    coil of rope over one shoulder.
14. `raw_town_alchemist.png` — an alchemist in a green apron, brass goggles pushed up on the
    forehead, holding up a bubbling glass flask of luminous green liquid.
15. `raw_town_mage.png` — a town mage in modest violet robes and a tall pointed hat, plain
    wooden staff topped with a small glowing crystal.
16. `raw_town_highpriest.png` — a high priest in white-and-gold ceremonial vestments and a
    tall mitre, holding an ornate golden staff with both hands.

## Goblin Raid enemies (face slightly left; small wiry hunched builds — noticeably smaller
than the big goblin brute from earlier — mossy yellow-green skin, ragged mismatched leather
scraps, crude rusty iron)
17. `raw_enemy_goblin_skirmisher.png` — a goblin skulker hunched under a ragged dark hood,
    clutching two crude daggers.
18. `raw_enemy_goblin_caster.png` — a goblin slinger whirling a leather sling with a stone,
    pouch of pebbles at the hip.
19. `raw_enemy_goblin_shaman.png` — a goblin shaman in a bone-and-feather headdress, gnarled
    totem staff with a glowing green charm.
20. `raw_enemy_goblin_sapper.png` — a goblin tunneler with a stubby candle strapped to a
    leather cap, hefting a pickaxe, dirt-stained clothes.
21. `raw_boss_goblin.png` — BOSS: the Goblin Warmaster, bigger and prouder than any common
    goblin, scavenged iron crown-helmet, patchwork cape, raising a crude war horn in one
    hand and a notched blade in the other.

## Orc Warband enemies (face slightly left; hulking broad builds, olive gray-green hide —
darker than the goblins — heavy black iron, red war paint)
22. `raw_enemy_orc_brute.png` — an orc brute in heavy black iron armor, red war paint across
    the face, hefting a massive two-handed spiked maul.
23. `raw_enemy_orc_skirmisher.png` — a frenzied orc berserker, bare-chested with war paint
    and battle scars, a jagged axe in each hand.
24. `raw_enemy_orc_caster.png` — an orc warcaster in dark furs and black iron pauldrons,
    skull-topped staff, hurling crackling red-orange battle magic from a clawed hand.
25. `raw_enemy_orc_shaman.png` — an orc witch doctor in a horned wooden mask and bone
    jewelry, feathered fetish staff with a glowing charm.
26. `raw_enemy_orc_sapper.png` — an orc saboteur carrying a wooden powder keg under one arm
    and a lit torch in the other hand, bandolier of crude bombs across the chest.
27. `raw_boss_orc.png` — BOSS: the Orc Warlord, immense, in trophy-laden black iron armor
    with skull pauldrons and a red war banner cape, gripping a colossal double-headed axe.

## Bandit Horde enemies (face slightly left; human outlaws, worn browns and muted red cloth,
leather armor, hoods and masks)
28. `raw_enemy_bandit_brute.png` — a burly bandit enforcer in patched brigandine, scarf over
    the lower face, gripping a heavy spiked club.
29. `raw_enemy_bandit_skirmisher.png` — a lean masked cutthroat in worn brown leathers and a
    muted red sash, a knife in each hand.
30. `raw_enemy_bandit_caster.png` — a bandit marksman in a dark hood holding a heavy loaded
    crossbow at the ready, quiver of bolts at the hip.
31. `raw_enemy_bandit_shaman.png` — a bandit field medic, leather satchel of bandages and
    tonics across the chest, holding up a small bottle of red medicine.
32. `raw_enemy_bandit_sapper.png` — a bandit torchman gripping a burning torch and an oil
    flask, coil of fuse rope at the belt.
33. `raw_boss_bandit.png` — BOSS: the Bandit King, a swaggering outlaw in a stolen golden
    crown and fine embroidered coat over brigandine, one hand resting on an ornate crossbow,
    gold rings on his fingers.

## Undead Legion enemies (face slightly left; pale bone and gray dead flesh, ancient rusted
armor, glowing spectral teal-violet accents — keep overall values mid-bright, bone reads
bright)
34. `raw_enemy_undead_brute.png` — a towering death knight in ancient rusted plate armor,
    glowing spectral teal eye sockets behind the visor, gripping a cracked greatsword.
35. `raw_enemy_undead_skirmisher.png` — a gaunt shadow reaver with pale gray dead flesh,
    wrapped in a tattered black cloak trailing wisps of violet mist, two wicked curved blades.
36. `raw_enemy_undead_caster.png` — a skeletal necromancer in dark violet robes with
    bone-white trim, staff topped with a skull glowing sickly green.
37. `raw_enemy_undead_shaman.png` — a bone priest in regalia of carved bones over tattered
    gray vestments, staff of stacked vertebrae topped with a teal ghost-flame.
38. `raw_enemy_undead_sapper.png` — a grave digger, a hunched skeleton in a ragged hood,
    worn shovel over one shoulder, lantern glowing pale green at the belt.
39. `raw_boss_undead.png` — BOSS: the Lich Commander, a crowned skeletal sorcerer-king in
    ancient royal vestments over rusted armor, radiating teal-violet ghost-light, ornate
    staff with a caged swirling soulflame.

## Infernal Siege enemies (face slightly left; charcoal-black and deep crimson demon hide,
curling horns, glowing ember-orange accents)
40. `raw_enemy_infernal_brute.png` — a massive pit fiend demon with curling ram horns and
    glowing ember-orange cracks across its muscles, hefting a huge jagged cleaver blade.
41. `raw_enemy_infernal_skirmisher.png` — a snarling hellhound: four-legged, standing on all
    four legs with every paw visible, about 70% of image height, three-quarter side view;
    charcoal-black hide, glowing ember-orange mane and eyes, fire licking from its jaws.
42. `raw_enemy_infernal_caster.png` — a demon flamecaller in charred dark robes, crimson
    skin and small curved horns, conjuring a sweeping arc of bright hellfire between clawed
    hands.
43. `raw_enemy_infernal_shaman.png` — a blood acolyte in deep crimson hooded vestments, pale
    horns curling from the hood, holding up a chalice glowing with sinister red light.
44. `raw_enemy_infernal_sapper.png` — a cinder imp: small (about 75% of image height),
    winged, soot-black with glowing ember cracks and a mischievous fanged grin, carrying a
    smoldering brazier of hot coals.
45. `raw_boss_infernal.png` — BOSS, the showpiece of the whole series: the Demon Empress, a
    towering regal demoness in obsidian-black and gold war regalia with a crown of curling
    horns, great wings folded behind her, wreathed in ember-orange hellfire, holding a
    blazing scepter; about 88% of image height.

## World — town vista & buildings (added 2026-07-18; HIGHEST priority — the scene layout is blocked on these)

**Backdrop rule change for entries 46/83 only:** no magenta, no single character — full
scene squares. **Attach BOTH the knight anchor AND the battlefield backdrop image**
(`raw_bg_battlefield_v1.png`) — same style, palette, and overcast light.

**Camera decision (2026-07-18): high angle, piloted by entry 46.** At eye level the
horizon sits ~43% up the frame, capping all standing room to the lower half — 16-unit
late-game squads plus 9 building plots don't fit (measured in the scene prototype). The
vista is therefore generated at a steep high-angle view (strategy-game map, not eye-level
vista); the battlefield companion (entry 83) is HELD until the vista's camera passes
judgment in `tools/scene-prototype.html`.

46. `raw_bg_town_vista.png` — **CAMERA PILOT — generate 2–3 candidates, keep the best.**
    The grounds INSIDE a medieval kingdom's walls, same 16-bit pixel art style and muted
    overcast palette as the attached battlefield painting, but seen from HIGH ABOVE at a
    steep three-quarter angle, like a strategy-game map viewed from a watchtower: open
    ground fills at least the bottom four-fifths of the image, with only a narrow band of
    distant mountains and sky across the very top. The kingdom's stone wall ENCLOSES the
    grounds — most prominent along the ENTIRE RIGHT EDGE top to bottom with its wooden
    gate midway up, and continuing around the top and left edges of the grounds. Broad
    flat stretches of trampled grass and packed dirt, a dirt road running from the gate
    toward the lower left, a broad cobbled plaza with a stone well in the center-to-lower
    portion, a few scattered trees and bushes near the walls. **Aside from those trees,
    the ground must be EMPTY — absolutely no buildings, tents, market stalls, carts,
    people, or animals** (the game places building sprites as the player builds; a new
    kingdom must start as bare walled ground). Muted, desaturated colors so characters
    and UI stand out on top. No text, no UI, no borders.

83. `raw_bg_battlefield_v2.png` — **camera CONFIRMED 2026-07-18 (AI Studio candidates
    passed the prototype pairing test); regenerate only to refine.** (Numbered out of
    sequence to avoid renumbering; belongs immediately after 46.) The battlefield OUTSIDE
    the same wall: attach the accepted entry-46 image as an additional reference and match
    its camera angle, palette, and light exactly. **The reference is for style, palette,
    and camera ONLY — do NOT copy its landmarks: no well, no plaza, no copied road layout**
    (lesson from the first attempt, which reproduced the town well mid-battlefield).
    Trampled open field, scattered battle debris, dense treeline down the right side, a
    narrow band of the same distant mountains and sky across the very top (matches the
    vista's top edge across the seam), a worn road emerging from the treeline upper-right
    and crossing toward the lower left — the road the raids arrive down. Empty of
    creatures; no text, no UI, no borders. Prefer portrait-ish aspect (~2:3) in AI Studio.
    **Wall: pending the wall-as-sprite decision** — if the seam wall becomes its own
    layered sprite (recommended: gate can open, wall can show damage/upgrades), this image
    needs NO wall at all, just plain ground at its left edge; otherwise the wall runs the
    entire left edge, gate midway. (v1 stays as the live panel-UI page backdrop.)

84. `raw_wall_gatehouse.png` — **the wall-as-sprite (seam layer; added 2026-07-18).**
    Attach `towncandidate1.png` as the reference. Tall portrait aspect (9:16). Prompt:
    a single tall section of a medieval kingdom's stone wall with a central gatehouse, in
    exactly the same 16-bit fantasy pixel art style, palette, and high three-quarter
    viewing angle as the wall in the attached reference image — use the reference ONLY
    for the art style, palette, camera angle, and the wall's stone construction; do not
    copy anything else from it (no ground, no grass, no well, no trees). The wall runs
    straight and vertical from the very top of the image to the very bottom, seen from
    that same high angle: battlemented walkway on top, left-hand face visible. Midway
    along it stands a larger fortified gatehouse with two short square towers and heavy
    CLOSED wooden double doors visible on the left face. The wall sections above and
    below the gatehouse are plain, straight, and uniformly repeating (so they can be
    extended by tiling). Stone intact, no banners. The background must be plain flat
    solid magenta (#FF00FF) everywhere around the wall — no ground plane at all, no
    grass, no shadow, no sky. The wall fills the full image height and roughly the middle
    third of the width. No text, no watermark, no frame, no other objects.
    **Follow-up variants (same chat, edit-in-place, low priority):** "exactly the same
    image, but the wooden doors stand open showing a dark passage" (raid-arrival state);
    "exactly the same image, but battle-damaged — cracked stone, crumbled battlements"
    (low-Kingdom-HP state; T4 upgrades likewise later).

**Building sprite rules (entries 47–55):** back to solid magenta (#FF00FF) background, one
building per image, whole building visible with clear margin, filling about 85% of the image
height, three-quarter front view **seen slightly from above so part of the roof reads —
matching the high camera of the vista** — angled toward the lower-left (door and front face
visible), lit from the upper left, standing on bare ground with **no ground, path, fence,
or vegetation around the base** (feet-on-magenta, like the characters). Same pixel scale,
thick outlines, and palette family as the attached knight; mid-to-bright values. These sit
directly on the town-vista painting, so silhouettes must read at roughly twice a character's
height.

47. `raw_bldg_cottage.png` — a humble one-room peasant cottage: rough fieldstone base,
    wattle-and-daub walls, thatched roof, plank door, one warm lit window.
48. `raw_bldg_tavern.png` — a wide cheerful two-story tavern: timber-framed walls, shingled
    roof, hanging wooden sign with a foaming mug painted on it, several warm lit windows.
49. `raw_bldg_smithy.png` — a sturdy stone smithy: open working front with a glowing forge
    inside, stout chimney trailing smoke, anvil silhouette visible in the doorway.
50. `raw_bldg_workshop.png` — a practical carpenter's workshop: plank walls, wide barn-style
    door, stacked lumber against one wall, sawhorse out front against the wall.
51. `raw_bldg_library.png` — a tall scholarly library: stone lower floor, timbered upper
    floor, steep slate roof, one large arched window glowing warmly.
52. `raw_bldg_keep.png` — a square stone keep tower: crenellated top, arrow slits, heavy
    ironbound door, a small pennant flying from one corner.
53. `raw_bldg_apothecary.png` — a crooked herbalist's shop: moss-green shingled roof, drying
    herb bundles hung under the eaves, round window, hanging sign with a potion bottle.
54. `raw_bldg_tower.png` — a slender wizard's tower: pale stone spiraling slightly as it
    rises, conical deep-blue roof, a single glowing arcane window near the top.
55. `raw_bldg_cathedral.png` — a grand stone cathedral: pointed arched entrance, large round
    rose window glowing gold, twin spires, the tallest and most ornate building of the set.

## Hero rarity variants (added 2026-07-18; LOWEST priority — trickle in whenever, any order)

The game shows the base hero sprite for every rarity until a variant file exists, so nothing
waits on these. Each variant is **the same character concept at a different station in
life**, not a new person: **attach the base archetype's sprite** (plus the knight anchor)
and keep the line "exactly the same character, art style, pose, and proportions as the
attached reference — only the gear and presence change." Escalation is presence and regalia,
not just shine — commons look plain and field-worn; Rare = well-made gear, small flourishes;
Epic = ornate masterwork gear, one subtly glowing element; Legendary = radiant, gilded,
clearly the stuff of legend. Don't recolor the whole palette — the game adds its own
rarity-colored rim. Character rules from the top of this doc all apply.

**Base-art tier audit (2026-07-18):** some existing base sprites already depict a higher
tier (user observation, confirmed by eye). Each base sprite is slotted into the tier its art
actually shows, and only the OTHER three tiers get generated — the audited tier simply has
no separate file (the game falls back to the base sprite for it):
- **guardian, fighter, ranged, assassin, battlemage, banneret, frostadept** — base art =
  **Common**; generate rare/epic/legendary as listed.
- **mender** — base art = **Rare (the Cleric)**: cream-and-gold robes and a glowing sun
  staff outrank a novice. Generate **common** (65) + epic (66) + legendary (67); there is
  deliberately NO `raw_hero_mender_rare.png`.
- **paladin** — base art = **Epic (the Crusader)**: gold-trimmed plate and a radiant holy
  symbol are already near the top of the ladder. Generate **common** (68) + **rare** (69) +
  legendary (70); there is deliberately NO `raw_hero_paladin_epic.png`.

56. `raw_hero_guardian_rare.png` — the Sentinel: the attached knight in finer fluted plate,
    reinforced kite shield with a polished lion emblem, short blue plume.
57. `raw_hero_guardian_epic.png` — the Vanguard: ornate engraved plate with gold edging,
    tower shield with a glowing lion emblem, tall plume.
58. `raw_hero_guardian_legendary.png` — the Paragon: gilded masterwork plate radiating faint
    golden light, resplendent banner-etched shield, crowned great helm.
59. `raw_hero_fighter_rare.png` — the Sellsword: the attached footman in a fitted brigandine,
    better longsword, confident stance flourish.
60. `raw_hero_fighter_epic.png` — the Blademaster: lamellar over fine mail, twin-fullered
    masterwork blade with a faint sheen, battle-worn red cloak.
61. `raw_hero_fighter_legendary.png` — the Warlord: commander's plate with a wolf-pelt
    mantle, huge rune-etched blade, presence of a living legend.
62. `raw_hero_ranged_rare.png` — the Sharpshooter: the attached archer with a recurve bow of
    dark lacquered wood, fletched arrows in a tooled quiver.
63. `raw_hero_ranged_epic.png` — the Hunter: hooded in deep forest greens with a beast-fang
    necklace, elegant longbow with subtle glowing engravings.
64. `raw_hero_ranged_legendary.png` — the Marksman: master archer in emerald-and-gold, a
    legendary bow strung with faint light, arrows glinting gold.
65. `raw_hero_mender_common.png` — the Acolyte: the attached healer as a humble novice —
    plain undyed roughspun robes with a simple rope belt, hood down, unadorned wooden
    walking staff with NO glow, small cloth satchel.
66. `raw_hero_mender_epic.png` — the Druid: layered natural robes with a leaf-and-antler
    circlet, living wooden staff sprouting green shoots, soft glow.
67. `raw_hero_mender_legendary.png` — the Saint: luminous white-gold raiment, a radiant halo
    of light behind the head, staff crowned with a blazing golden sun.
68. `raw_hero_paladin_common.png` — the Squire: the attached holy warrior young and
    unproven — plain dented steel half-plate with no gold trim, simple cloth tabard, plain
    mace, small wooden holy symbol on a cord, NO glow anywhere.
69. `raw_hero_paladin_rare.png` — the Paladin: full polished steel plate with modest gold
    edging only at the collar and belt, plain steel warhammer, small silver holy symbol —
    dignified, but nothing glows yet.
70. `raw_hero_paladin_legendary.png` — the Highlord: gleaming gold-chased armor wreathed in
    soft holy light, winged helm, white cape, hammer trailing radiance.
71. `raw_hero_assassin_rare.png` — the Assassin: the attached rogue in fitted midnight
    leathers, twin balanced daggers, half-mask.
72. `raw_hero_assassin_epic.png` — the Nightblade: wrapped in flowing shadow-touched cloth,
    daggers with a faint violet gleam, only eyes visible.
73. `raw_hero_assassin_legendary.png` — the Phantom: semi-spectral assassin trailing wisps
    of shadow, ghost-pale blades, presence barely of this world.
74. `raw_hero_battlemage_rare.png` — the Battlemage: the attached mage in reinforced robes
    with bracers, staff crackling with steadier arcane energy.
75. `raw_hero_battlemage_epic.png` — the Warmage: armored robes with a glowing rune circlet,
    staff wreathed in orbiting arcane sigils.
76. `raw_hero_battlemage_legendary.png` — the Archmage: majestic robes streaming arcane
    light, levitating tome at the hip, staff crowned with a small contained storm.
77. `raw_hero_banneret_rare.png` — the Banneret: the attached standard-bearer with a finer
    embroidered banner and polished half-plate.
78. `raw_hero_banneret_epic.png` — the Marshal: ornate command plate, great gilded banner
    with a radiant crest, ceremonial sword.
79. `raw_hero_banneret_legendary.png` — the High Marshal: resplendent gold-trimmed regalia,
    an enormous glowing royal standard streaming in the wind.
80. `raw_hero_frostadept_rare.png` — the Frost Adept: the attached frost mage with a clearer
    crystal staff and frost-rimed robe hems.
81. `raw_hero_frostadept_epic.png` — the Rimecaller: deep glacial-blue robes with an ice
    crystal crown, staff swirling with orbiting snowflakes.
82. `raw_hero_frostadept_legendary.png` — Winter's Voice: robes like living blizzard, skin
    faintly frost-touched, staff of pure ice radiating cold pale light.
