# Asset credits & provenance

Policy (M15_SCOPE.md): every file under `assets/` gets a line here in the same commit that
adds it — source, method, date. If the game is ever published on a storefront (itch.io,
Steam), AI-generated assets must be disclosed at submission per store policy.

Generator routes (attribution corrected 2026-07-18): **Antigravity** = Google's
Antigravity surface, the stronger image model (all character sprites, the original
battlefield, the UI frame); **Gemini web app** = the weaker, barely-rate-limited route
(the 2026-07-18 backdrop candidates and wall segment). Earlier notes calling the weak
route "AI Studio" meant the web app.

## Batch 1 — M15 art pilot (2026-07-17)
All generated via Antigravity (Gemini image generation) by Ben Simpson, from prompts in
`M15_ART_PILOT.md`, style-anchored to `raw_hero_knight_v3.png`:

- `raw/raw_hero_knight_v1.png` — knight, detailed style (superseded; kept for the A/B record)
- `raw/raw_hero_knight_v2.png` — knight, chunky monochrome (superseded; kept for the A/B record)
- `raw/raw_hero_knight_v3.png` — knight, chunky + color — **the style anchor**
- `raw/raw_enemy_goblin_brute.png` — goblin brute (consistency test vs the anchor: passed)
- `raw/raw_bg_battlefield_v1.png` — battlefield backdrop (square; band-cropped in pipeline)
- `raw/raw_ui_frame.png` — UI panel frame (square; sliced as CSS border-image)

## Batch 2 — heroes + first townsfolk (2026-07-17)
All generated via Antigravity (Gemini image generation) by Ben Simpson, from entries 1–9 of
`M15_ASSET_SPECS.md`, style-anchored to `raw_hero_knight_v3.png`. Confirmed 2026-07-17:
filenames match `SPRITE_SOURCES`, runtime pipeline keys all with zero magenta residue,
live in-game render verified:

- `raw/raw_hero_fighter.png` — fighter (footman, kettle helm, longsword)
- `raw/raw_hero_ranged.png` — ranged (green-hooded archer)
- `raw/raw_hero_mender.png` — mender (cream-and-gold healer, sun staff)
- `raw/raw_hero_paladin.png` — paladin (silver-gold plate, warhammer + holy symbol)
- `raw/raw_hero_assassin.png` — assassin (charcoal-purple leathers, twin daggers)
- `raw/raw_hero_battlemage.png` — battlemage (blue robes, crackling staff)
- `raw/raw_hero_banneret.png` — banneret (half-plate, crimson lion banner)
- `raw/raw_hero_frostadept.png` — frost adept (ice-blue fur robes, crystal staff)
- `raw/raw_town_villager.png` — villager (straw hat, vegetable basket)

## Batch 3 — building sprites (2026-07-18)
All generated via Antigravity (Gemini image generation) by Ben Simpson, from entries
47–55 of `M15_ASSET_SPECS.md`, style-anchored to `raw_hero_knight_v3.png`. Solid magenta
background, high-camera three-quarter view; consumed by the runtime pipeline via the
`bldg_<id>` keys in `SPRITE_SOURCES` and shown on the M15 scene town vista. Files are
JPEG bytes under a `.png` name (the series convention — the character sprites are the same).

- `raw/raw_bldg_cottage.png` — peasant cottage
- `raw/raw_bldg_tavern.png` — two-story tavern
- `raw/raw_bldg_smithy.png` — stone smithy (the active sprite = the "smithy2" variant; see below)
- `raw/raw_bldg_workshop.png` — carpenter's workshop
- `raw/raw_bldg_library.png` — scholarly library
- `raw/raw_bldg_keep.png` — stone keep tower
- `raw/raw_bldg_apothecary.png` — herbalist's shop
- `raw/raw_bldg_tower.png` — wizard's tower
- `raw/raw_bldg_cathedral.png` — cathedral

Smithy variants (3 generated; **option 2 chosen 2026-07-18** — most detailed, warmest,
strongest forge, and pipeline-clean). Copied to `raw_bldg_smithy.png` as the active
sprite; the three source variants are kept on disk for reference (user call — may revisit):
- `raw/raw_bldg_smithy1.png` — option 1 (smoke plume runs off the top edge → a 24% smoke
  column after keying, so the building seats ~a quarter smaller; retired, kept for reference)
- `raw/raw_bldg_smithy2.png` — option 2 (chosen; identical bytes to the active `raw_bldg_smithy.png`)
- `raw/raw_bldg_smithy3.png` — option 3 (no smoke, cold all-stone; alternate, kept for reference)

## Batch 4 — Goblin Raid enemies (2026-07-18) + orc/bandit tiers (2026-07-19)
Generated via Antigravity (Gemini image generation) by Ben Simpson, from the enemy
entries of `M15_ASSET_SPECS.md`, style-anchored to `raw_hero_knight_v3.png`. Wired
automatically via existing `SPRITE_SOURCES` keys (battle slots). The 2026-07-19
integration pass (Claude) added `SPRITE_FLIP` in game.js: 8 of these raws face right
(spec says enemies face LEFT) and are mirrored in memory at load — do NOT regenerate
them for facing. Antigravity quota froze 2026-07-19 (~40 assets, resets 07-24);
still missing: bandit sapper + Bandit King, all undead + infernal enemies/bosses.

- `raw/raw_enemy_goblin_skirmisher.png` — goblin skulker (hooded, twin crude daggers)
- `raw/raw_enemy_goblin_caster.png` — goblin slinger (whirling sling, pebble pouch)
- `raw/raw_enemy_goblin_shaman.png` — goblin shaman (bone headdress, glowing charm staff)
- `raw/raw_enemy_goblin_sapper.png` — goblin tunneler (candle helm, pickaxe; flipped)
- `raw/raw_boss_goblin.png` — Goblin Warmaster (crown, bone standard, cleaver)
- `raw/raw_enemy_orc_brute.png` — orc brute (black plate, spiked maul; flipped)
- `raw/raw_enemy_orc_skirmisher.png` — orc berserker (twin axes; off-spec crimson bg —
  keys cleanly via the corner-sampling fallback; coarser/noisier pixel grid than the
  batch — accepted at game scale, the one regen candidate when capacity returns)
- `raw/raw_enemy_orc_caster.png` — orc warcaster (red lightning claw, skull totem)
- `raw/raw_enemy_orc_shaman.png` — orc witch doctor (horned tiki mask, fetish staff; flipped)
- `raw/raw_enemy_orc_sapper.png` — orc saboteur (torch, powder keg shield; flipped)
- `raw/raw_boss_orc.png` — Orc Warlord (skull pauldrons, great axe, red cape; flipped)
- `raw/raw_enemy_bandit_brute.png` — bandit enforcer (spiked club, red scarf; flipped)
- `raw/raw_enemy_bandit_skirmisher.png` — bandit cutthroat (masked, twin daggers; flipped)
- `raw/raw_enemy_bandit_caster.png` — bandit marksman (hooded, crossbow)
- `raw/raw_enemy_bandit_shaman.png` — bandit medic (satchel of potions; flipped)

## The scene backdrop (live)
- `raw/scene_backdrop_v2.png` — **the live scene backdrop** (spec 85-V2): Gemini web
  app 4:3 regeneration anchored to the v1 crop (`reference/scene_regen_input.png`),
  by Ben Simpson, 2026-07-19. Finer pixel density than v1 (~1.3-1.5×); generated in
  4:3 deliberately so the app's baked watermark (always ~90%/84% of canvas, rows
  1440+ here) sits below the in-game clip line — `SCENE_COMP_ASPECT` in game.js
  keeps rows 0-1270 only, so the watermark never renders. No file editing involved.

## Candidates under evaluation (delete or promote before shipping)
- `raw/scenebothhalvesbigger.png` — 16:9 density-regen attempt (2026-07-19), superseded
  same day by scene_backdrop_v2 (watermark at the fixed spot made a zoom-free clip
  impossible on a 16:9 canvas). Kept for reference; delete before shipping.
- `raw/scenebothhalves.png` — **the v1 continuous scene backdrop**
  (spec entry 85 resolution): one widescreen generation, town + wall/gatehouse +
  battlefield, by Ben Simpson, 2026-07-18. First backdrop whose detail density matched
  the character series; superseded by scene_backdrop_v2 (2026-07-19) which clips its
  baked sparkle watermark away instead of shipping it. Its watermark-free crop lives
  at `reference/scene_regen_input.png` as the anchor for future backdrop regens.
  Earlier candidates below are superseded by it.
All three below generated with the **Gemini web app** (weak route) by Ben Simpson,
2026-07-18. All are superseded as final assets by spec entry 85 (the Antigravity scene
pair) and serve as interim/reference material until it lands:
- `raw/towncandidate1.png` — town-vista backdrop candidate (old spec entry 46).
  Composition passed in the scene prototype; carries a small Gemini sparkle watermark in
  the bottom-right corner.
- `raw/battlefieldcandidate1.png` — battlefield companion candidate (old spec entry 83).
  Pairs tolerably with towncandidate1 in the prototype; wall only a top-left scrap.
  Sparkle watermark bottom-right (outside the current crop).
- `raw/townwall.png` — wall-as-sprite candidate (old spec entry 84). Stonework
  style-matched but the geometry hallucinates mid-image (perpendicular second archway,
  diagonal wall run). Salvage outcome 2026-07-18: the straight wall run (x 1290–1805,
  y 1300+) tiles as the prototype's interim seam wall; the tower/gatehouse piece proved
  unusable — its isometric orientation clashes with a vertical wall (projection, not
  style). Sparkle watermark lower-right on magenta — will NOT key out; pipeline must
  corner-scrub.

## Reference (not shipped in-game)
- `reference/idlekingdommockup.png` — the developer's one-scene vision mockup (town →
  wall → battlefield), generated with Google Gemini by Ben Simpson, 2026-07-17; added to
  the repo 2026-07-18. Design reference only: we extract its visual language and layout
  ideas, never its fictional UI (gems, worker levels, etc. don't exist in the game).
- `reference/mockup_town_square.png` + `reference/mockup_field_square.png` — annotated
  layout sketches for the scene-pair generation (spec entry 85), authored
  programmatically by Claude (not AI image generation) via
  `tools/make-scene-mockups.ps1`, 2026-07-18. Attached to Antigravity prompts as
  placement ground truth; never shipped in-game.
