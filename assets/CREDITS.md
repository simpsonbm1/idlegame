# Asset credits & provenance

Policy (M15_SCOPE.md): every file under `assets/` gets a line here in the same commit that
adds it — source, method, date. If the game is ever published on a storefront (itch.io,
Steam), AI-generated assets must be disclosed at submission per store policy.

## Batch 1 — M15 art pilot (2026-07-17)
All generated with Google Gemini (image generation) by Ben Simpson, from prompts in
`M15_ART_PILOT.md`, style-anchored to `raw_hero_knight_v3.png`:

- `raw/raw_hero_knight_v1.png` — knight, detailed style (superseded; kept for the A/B record)
- `raw/raw_hero_knight_v2.png` — knight, chunky monochrome (superseded; kept for the A/B record)
- `raw/raw_hero_knight_v3.png` — knight, chunky + color — **the style anchor**
- `raw/raw_enemy_goblin_brute.png` — goblin brute (consistency test vs the anchor: passed)
- `raw/raw_bg_battlefield_v1.png` — battlefield backdrop (square; band-cropped in pipeline)
- `raw/raw_ui_frame.png` — UI panel frame (square; sliced as CSS border-image)

## Batch 2 — heroes + first townsfolk (2026-07-17)
All generated with Google Gemini (image generation) by Ben Simpson, from entries 1–9 of
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
