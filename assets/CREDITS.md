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

## Candidates under evaluation (delete or promote before shipping)
- `raw/scenebothhalves.png` — **the accepted-direction continuous scene backdrop**
  (spec entry 85 resolution): one widescreen generation, town + wall/gatehouse +
  battlefield, by Ben Simpson, 2026-07-18. First backdrop whose detail density matches
  the character series. Small baked-in sparkle watermark lower-right (~2560,1297) —
  resolve before shipping. Earlier candidates below are superseded by it.
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
