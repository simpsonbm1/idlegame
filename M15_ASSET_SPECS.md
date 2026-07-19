# M15 asset run — Gemini series brief

**For Ben:** hand everything below the divider to Gemini as **one paste**, in the same
conversation that generated the knight. Save each result to `assets/raw/` under the filename
Gemini announces. If the style starts drifting mid-run (it can, in long conversations),
re-attach the original knight image and tell it to re-ground on that. Deliver batches to
Claude at any pace — order below is most-valuable-first.
Already done, skipped in the list: guardian hero (`raw_hero_knight_v3.png`), goblin brute
(`raw_enemy_goblin_brute.png`). Portraits are cropped from these sprites by the pipeline —
no separate portrait generations needed.

**Generator routing (corrected 2026-07-18 evening):** two routes exist —
**Antigravity** (the STRONG model: made every character sprite and the original
battlefield; ~10 images/5h, **1:1 aspect only**) and the **Gemini web app** (weak model,
barely rate-limited: made the current town/battlefield candidates and the wall segment —
"workable in the right light" at best). Backdrops and characters go to Antigravity;
spend its window on whatever is most blocking. The web app is a fallback for low-stakes
fills only.

**Batch priority (updated 2026-07-18 evening, after the seam experiments):** the scene
layout (see `tools/scene-prototype.html`) changed what unblocks what. Recommended order:
1. **The scene pair (entry 85, Antigravity)** — two 1:1 squares that join AT the wall.
   Supersedes the old two-half entries (46/83) and the wall sprite (84): every seam
   problem this project has hit — style clash between halves from different models,
   wall-salvage projection mismatches — came from marrying mismatched images at a line
   of open ground. The pair fixes both causes: same strong model for both halves (the
   second generated with the first attached), and the joint falls ON the painted wall,
   which hides it. Then buildings (47–55).
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

## World — the scene pair & buildings (updated 2026-07-18 evening; HIGHEST priority)

**Backdrop rule change for entry 85 only:** no magenta, no single character — full scene
paintings. **Generate in ANTIGRAVITY** (1:1 only, so the scene is two squares joining AT
the wall). Attach only what each sub-entry says — references demonstrably bleed landmarks
into new generations, so the layout is fully described in words instead.

**Camera (locked 2026-07-18):** steep high angle, strategy-map-from-a-watchtower — at eye
level the horizon caps all standing room to the lower half of the frame; 16-unit late-game
squads plus 9 building plots don't fit (measured in the scene prototype).

46. **SUPERSEDED by entry 85a** (the town square, redesigned to carry the wall at its
    right edge). `towncandidate1.png` (web app) stays on disk as reference only.

83. **SUPERSEDED by entry 85b** (the battlefield square, which now starts at the wall's
    base instead of marrying open ground). `battlefieldcandidate1.png` stays as reference.

84. **SUPERSEDED by entry 85** (no wall-as-sprite seam layer: the wall and gate are painted
    into the town square in correct perspective). The `townwall.png` salvage experiments
    proved composited wall pieces clash in projection even when the style matches. Gate
    open/damage states, if ever wanted, become edit-in-place variants of 85a (T4).

85. **RESOLVED 2026-07-18 by `scenebothhalves.png`** — a single continuous widescreen
    generation (town + wall/gatehouse mid-frame + battlefield, road through the gate,
    detail density matching the characters) made the pair approach below unnecessary.
    The prototype loads it full-stage; the pair rig below survives only as fallback
    and as the record of the sketch-reference + measured-color-grade techniques.

    **85-EDIT-1 — SUPERSEDED by 85-V2 same day (2026-07-19).** The watermark-move
    edit pass (remove/cover the sparkle + sacrificial margin, with a fallback
    ladder) died on the user's observation that EVERY web-Gemini output gets a
    fresh watermark and the app won't remove its own even when the net result
    would be equally watermarked — so no edit pass can ever produce a clean file,
    and relying on the watermark landing inside a requested margin is Gemini-
    cooperation we don't control. The only robust pattern: Claude strips
    watermarks by CROPPING on our side, both on inputs and outputs.

    **85-V2 — RESOLVED 2026-07-19 by `scene_backdrop_v2.png`** (2400×1792 4:3 regen
    anchored to the clean crop; the 4:3 rule below worked exactly as designed:
    watermark at rows 1440+, in-game clip keeps rows 0–1270 — chosen so the wall
    also seats exactly on the 46% seam at 16:9 — density ~1.3–1.5× finer than v1,
    wall faithful, plots re-seated, browser-verified zero-console-error). Extra
    battlefield debris in the mid-right field accepted as wreckage-under-the-armies;
    a future edit pass can clean it if it grates. Playbook below kept for the next
    backdrop generation (prosperity variants, any v3 attempt).
    Backdrop cells are 6–12px at 2752 wide and render 3–4× chunkier on screen than
    the characters (measured); 2× finer is the sweet spot (3–4× collapses into
    sub-grid noise, and a residual 1.5–2× softness reads as depth-of-field).
    - **Conditioning input (already cut, committed):**
      `assets/reference/scene_regen_input.png` — the current backdrop cropped at
      row 1245, just above the sparkle, so the input is watermark-free and the
      regen can't repaint the sparkle as scene content. The regen re-invents the
      foreground band (plaza bottom, rope coil) — expect drift there, it's
      accepted.
    - **Prompt (attach scene_regen_input.png):**
      > Re-render this pixel-art scene at twice the detail density — each pixel
      > cell about half its current size, so everything resolves twice as finely —
      > keeping the composition, layout, colors, lighting, and style exactly as
      > shown: walled medieval town on the left, stone wall and gatehouse
      > mid-frame, open battlefield with a dirt road on the right, mountains
      > behind. The image is cut off at the bottom: continue the scene downward to
      > complete the foreground (finish the round stone plaza on the left;
      > continue open grass with occasional dirt patches on the right), then keep
      > extending about 10% further with plain grassy foreground. Output in
      > widescreen at the largest resolution available.
      The plain-grass tail is deliberate slack: the output WILL come back
      watermarked (bottom-right, wherever its canvas ends), and grass is free to
      clip. If the watermark lands on real composition instead, Claude still
      clips — worst case re-roll with a bigger tail.
    - **THE 4:3 RULE (discovered 2026-07-19 from two window iterations):** the web
      app's watermark ALWAYS lands at ~90% across / ~84% down of the output canvas
      (fixed relative position, fixed 16:9 canvas 2752×1536 by default — which is
      why clipping a 16:9 output always costs ~22% zoom). Ask for **4:3 output**
      with all important content in the upper three quarters and a plain-grass
      bottom quarter: clipping 4:3 → 16:9 keeps the top 75%, and 84% is always
      below that line. Watermark discarded at ZERO zoom. Also: anchor regens to
      `assets/reference/scene_regen_input.png` (the watermark-free crop of the
      ORIGINAL) — never to a window-chain intermediate (drift compounds; one
      attempt carried a mangled wall) and never to a sparkle-bearing file (the
      regen paints the sparkle back as scene content). First 4:3 attempt confirmed
      the geometry works; density asks land ~1.3–1.5× finer, not the 2× requested.
    - **Integration (Claude, full re-placement, not a trim):** locate the
      watermark, set the clip bounds to exclude it (`SCENE_COMP_ASPECT` /
      explicit crop), re-derive `SCENE_WALL_FRAC` from the new wall/gate center,
      re-seat all `BUILDING_PLOTS` against the new painted plaza/road, verify
      in-game (46% seam, plots clear of the belt, crowd zone, diorama, density
      next to the character sprites).
    **THE scene pair — town square + battlefield square (Antigravity).** Final filenames
    `raw_bg_scene_town.png` / `raw_bg_scene_field.png`; save candidates as
    `scenetown1.png` / `scenefield1.png` (`2`, …) — `tools/scene-prototype.html`
    auto-loads them, town square right-aligned and field square left-aligned so they meet
    at the seam. The joint falls ON the town square's painted right-edge wall, so the two
    images never have to agree across open ground — only the mountain-band height and the
    road through the gate cross the joint. **Order: generate 85a first, judge it in the
    prototype, THEN 85b with the accepted 85a attached.**
    **LAYOUT SKETCHES (added 2026-07-18 after prose-only attempts kept drifting on
    geometry — the generator respects reference images far more than prose):** each
    sub-entry attaches its annotated layout mockup — `assets/reference/
    mockup_town_square.png` / `mockup_field_square.png`, regenerable via
    `tools/make-scene-mockups.ps1`. The prompt must tell the model the sketch is a
    PLACEMENT plan only: don't copy its flat colors, don't render its text/arrows.

    **85a — the town square** (attach the knight anchor ONLY). Attempt-1 lesson
    (2026-07-18): "steep three-quarter angle" produced true vanishing-point perspective —
    a diagonal east wall with exterior ground already visible bottom-right, which
    re-complicates the join; the projection must be named explicitly. Attempt-2 lesson:
    flat oblique landed, but the gatehouse spawned freestanding in the courtyard joined
    to the east wall by a stub — a gate embedded in an edge-parallel wall would be
    half-cropped, so the model pulls it inward to show the whole structure. Fix via
    EDIT-IN-PLACE on the otherwise-good attempt (flush the gatehouse against the east
    wall as a slightly-protruding barbican, extend the road to it, extend the west wall
    to the bottom edge — it visibly terminated mid-frame). Attempts 3–5 lesson: the
    model anchors hard on its composition (edits regenerate near-identical output) and
    insists on an INSET east wall with an exterior strip beyond it — ACCEPTED (attempt 5
    = `scenetown1.png`): gate embedded, road passes through and exits the frame, walls
    screen-axis aligned. Known flaw: below the gatehouse the wall turns EAST off-frame
    instead of continuing south, so the image's lower-right is town interior.
    **STANDING USER RULE (2026-07-18, set after two failed salvage attempts): no
    pipeline pixel-surgery on generated art — an image either works as delivered or
    gets regenerated. Whole-image CSS cropping/positioning is fine; compositing,
    clone-stamping, and patching are not.** The prototype therefore renders the square
    AS GIVEN, gatehouse outer face (x 956/1024) on the seam; below the gate the seam
    joint is ground-to-ground under the seam shadow. If that reads poorly once 85b is
    in place, the fallback is ONE model-side edit ask on this image ("extend the east
    wall from the gatehouse straight down to the bottom edge of the image"), never a
    pipeline patch. The exterior pocket previews the ground tone and road height
    (road exits at ~40% down) that 85b must continue at its left edge.
    **Prompt (attach the knight anchor + `mockup_town_square.png`):**
    A square scene painting: the grounds inside a medieval kingdom's stone walls. One
    attached image is a LAYOUT SKETCH — a rough schematic with flat colors, text labels,
    and arrows. Follow its placement EXACTLY: every wall, the gatehouse, the road, the
    plaza and well, and the trees go precisely where the sketch puts them, at the same
    sizes. The sketch is only a plan: do NOT copy its flat drawing style, and do NOT
    render any of its text, labels, or arrows into the painting. Render everything as
    retro 16-bit fantasy pixel art in exactly the style of the other attached image
    (the knight sprite) — same palette approach, chunky pixel scale, thick dark
    outlines — but muted and slightly desaturated overall so bright character sprites
    drawn on top of it stand out. Key constraints repeated from the sketch: flat
    oblique projection like a classic 16-bit RPG town map (no vanishing-point
    perspective); the east wall runs PERFECTLY VERTICAL along the entire right edge,
    top to bottom, no bends; the fortified gatehouse with heavy CLOSED wooden double
    doors sits midway down it; only a narrow band of distant mountains and sky across
    the very top; and the grounds are otherwise COMPLETELY EMPTY — no buildings,
    tents, market stalls, carts, people, or animals. One light source from the upper
    left. No text, no UI, no borders.

    **85b — the battlefield square** (attach the ACCEPTED 85a = `scenetown2.png`, the
    knight anchor, AND `mockup_field_square.png`). First-attempt lessons
    (scenebattle2.png, 2026-07-18): it drew a forbidden wall+buildings strip on its
    left edge, went full desert-tan against the town's olive grass, mismatched the
    mountain style, and put the road at 37% vs the town gate's 50% — so the prompt now
    names the town painting as the explicit color authority and the sketch carries the
    corrected road height. Prompt:
    A second square painting that will be placed IMMEDIATELY TO THE RIGHT of the
    attached town scene: the open battlefield just outside that town's wall. One
    attached image is a LAYOUT SKETCH — a rough schematic with flat colors, text
    labels, and arrows. Follow its placement EXACTLY: the road, the treeline, and the
    trampled patches go precisely where the sketch puts them. The sketch is only a
    plan: do NOT copy its flat drawing style, and do NOT render any of its text,
    labels, or arrows into the painting. The attached TOWN PAINTING is the color and
    style authority: use EXACTLY its palette — the same green of its grass, the same
    stone gray, the same sky color, and the same mountain shapes and colors continuing
    at the same height across the very top — plus its flat oblique projection and
    upper-left light, so the two images join seamlessly side by side. The battlefield
    ground is that same green grass, heavily trampled with mud patches — NOT desert,
    NOT brown dirt. Key constraints repeated from the sketch: the town's wall stands
    just beyond this image's LEFT edge — draw NO wall, NO buildings, nothing built,
    only trampled ground at the wall's base; the dirt road enters from the left edge
    50% of the way down — level with the town gate — and bends toward a dense treeline
    in the upper right (the road enemy raids arrive down); sparse battle debris (a
    broken arrow, a rock or two); and NOTHING else — no creatures, no structures, and
    none of the town image's landmarks (no well, no plaza). No text, no UI, no
    borders.

**Building sprite rules (entries 47–55):** back to solid magenta (#FF00FF) background, one
building per image, whole building visible with clear margin, filling about 85% of the image
height, three-quarter front view **seen slightly from above so part of the roof reads —
matching the high camera of the vista** — angled toward the lower-left (door and front face
visible), lit from the upper left, standing on bare ground with **no ground, path, fence,
or vegetation around the base** (feet-on-magenta, like the characters). Same pixel scale,
thick outlines, and palette family as the attached knight; mid-to-bright values. These sit
directly on the town half of the scene painting (entry 85), so silhouettes must read at
roughly twice a character's height.

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
