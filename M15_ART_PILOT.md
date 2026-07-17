# M15 art pilot — Gemini generation specs (round 1)

> **PILOT PASSED — 2026-07-17.** All four assets delivered and verified in
> `tools/pilot-scene.html` (knight vs goblin on the backdrop band inside frame chrome):
> 1 ✅ knight/goblin style consistency holds; 2 ✅ readable at 96/64/48px + 52px portrait
> crop; 3 ✅ magenta keys clean (flood fallback also works for flat non-magenta);
> 4 ✅ frame slices into working `border-image` chrome (tune: thicker border + edge repeat
> `round` at T1 integration; also add CSS ground-shadow ellipses under units in T2).
> **Pipeline requirement found by the user (2026-07-17): trim-box ≠ body-box.** Weapon
> overhang skews trimmed bounding boxes (the goblin's club is ~200px of his width), so slot
> seating must register to a computed **foot anchor** — alpha-weighted centroid X of the
> bottom 12% of opaque pixels, lowest opaque row in a narrow band around it (thin weapon tips
> ignored). Implemented and verified in `tools/pilot-scene.html`; `process-art` must export
> per-sprite anchors in a **sprite manifest** (JSON: trimmed size + anchor), and the game
> registers slots, HP bars, mirror axis, and lunge transform-origins to the anchor.
> Aspect finding: user's Gemini surface is 1:1-only — squares accepted, pipeline band-crops
> (ground rule 7). Next deliverable: the full asset spec doc (~47 character prompts, batched
> heroes → per-tier enemies → bosses → townsfolk → backdrops/chrome), pending the user's
> aesthetic sign-off on the pilot scene.

Goal: prove the asset workflow on **4 assets** before committing to the full run (~47 characters
+ backdrops + chrome). This pilot tests all four asset categories: character consistency
(hero + enemy), backdrop, and UI chrome. Claude wrote these specs; Ben generates in Gemini;
Claude post-processes and integrates a test scene.

## How to run a generation (applies to every asset)
1. **One asset per image.** Never ask for a sheet of multiple characters — style holds better
   per-image and cutting sheets apart is lossy.
2. **Asset 1 is the style anchor.** Generate it first. For every asset after it, attach the
   anchor image to the prompt and keep the line "exactly the same art style, palette, outline
   weight, and proportions as the attached reference image."
3. If a result is wrong (bad pose, extra limbs, text in the image, wrong background), ask for
   a correction in the same chat — don't hand-edit anything.
4. **Save as PNG** at the largest size offered (JPG compression ruins background removal).
   Don't crop, scale, or retouch — raw output only; post-processing is Claude's job.
5. Put files in `assets/raw/` (create the folder) with the exact filenames below.
6. When done, note in chat roughly how many attempts each asset took — that number calibrates
   the full-run estimate.
7. **Aspect ratio**: square for everything — pilot finding 2026-07-17: the user's Gemini
   surface outputs 1:1 only, regardless of prompting. That's fine: the battle column is
   roughly square anyway, and wide uses get a horizontal band cropped from the square by the
   pipeline (pixel art upscales and edge-tiles gracefully). Do NOT stitch multiple generated
   squares into panoramas — cross-generation seams (horizon/lighting mismatch) are the risky
   path. If a true wide panorama is ever needed (T1), we extract *layers* (sky / mountain /
   ground strips) from squares and composite, rather than seam-stitching whole scenes.
8. **Generate 2–3 candidates per asset and save the best** — variance between generations is
   free quality.
9. **Always attach Asset 1 as the reference — never the most recent output.** Chaining
   reference images accumulates style drift; anchoring to one fixed image doesn't.
10. **Don't tell Gemini about the game.** Subject + style only. Game context is what made the
    mockups invent gems, build queues, and wall buttons — mechanics talk produces fictional UI.

## What NOT to ask for (Gemini can't honor these; our pipeline owns them)
- **Output pixel dimensions** ("make it 64×64"): image models generate at fixed large
  resolutions regardless. Real sizes come from Claude's downscaling step.
- **A true pixel grid**: AI "pixel art" is faux — the chunky pixels aren't grid-aligned.
  What we control instead is *apparent* chunkiness (in the boilerplate), kept consistent
  across assets so nothing looks higher-res than its neighbors; alignment is post-processing.
- **Transparent backgrounds**: it fakes checkerboards. Magenta stays.
- **Exact hex palettes**: won't be honored; the style anchor is the palette mechanism.

## Boilerplate block — paste at the end of every CHARACTER prompt
> Single character only, full body with feet visible, centered, filling about 80% of the
> image height with clear margin on every side — no part of the character touches the image
> edge. Three-quarter front view, neutral combat-idle stance, lit from the upper left.
> The background must be plain flat solid magenta (#FF00FF) filling the entire image — no
> vignette, no texture, and no ground, dirt, or shadow under the feet. No text, no watermark,
> no frame or border, no other objects. Retro fantasy RPG pixel art style as if drawn on a
> canvas only about 48 pixels tall and then upscaled: bold simple shapes, flat shading with
> at most 3 tones per surface, minimal dithering, thick dark outlines, warm earthy tones,
> readable silhouette, mid-to-bright overall values so the character stands out against dark
> backgrounds.
>
> (Pilot lesson 1, 2026-07-17: the first knight came back ~128px-class painterly detail on a
> GRAY background with a dirt base — too fine for battle-slot size, and gray keying would
> eat gray armor. The phrasing above is the corrected version; watch every generation for
> those two deviations. Detailed v1 kept as `raw_hero_knight_v1.png` for the A/B downscale
> test.)
>
> (Pilot lesson 2, 2026-07-17 — from the v1/v2 A/B in `tools/process-art.html`: **value
> brightness beats detail level.** v1's small-size failure was as much dark-on-dark (units sit
> on a dark UI and muted field) as fine detail; v2's bright steel read at every size. Every
> character prompt now carries "mid-to-bright overall values so the character stands out
> against dark backgrounds." Also validated: magenta keys with no fringe; the border-flood
> fallback key handles non-magenta flat backgrounds; ~950px trimmed sprites leave ample
> resolution. v2's failure mode is the opposite one: monochrome and personality-free — v3
> merges v2's chunk scale + brightness with v1's color interest (surcoat, heraldry, leather
> accents, 3-tone steel).)

---

## Asset 1 — style anchor + hero: Knight (guardian) — ✅ DONE 2026-07-17
**The style anchor is `raw_hero_knight_v3.png`** (chunky scale + bright 3-tone steel + blue
surcoat/gold lion heraldry — the v1/v2 merge). Attach THIS image to every subsequent
generation. Sim-of-record: passes 96/64/48px readability and the 52px portrait crop on both
backgrounds in `tools/process-art.html`; magenta keyed clean.
**Filename:** `raw_hero_knight.png` (original spec below, superseded by the v1→v3 iteration)

> A stalwart human knight in full plate armor with a closed great helm, holding a tall kite
> shield in the left hand and a lowered longsword in the right, facing slightly to the right.

…then the boilerplate block. This image becomes the style anchor for everything else — if you
don't love it, iterate until you do before generating anything further.

## Asset 2 — enemy: Goblin Brute
**Filename:** `raw_enemy_goblin_brute.png` · attach the anchor.

> A hulking goblin brute with mossy green skin, a heavy jaw with underbite tusks, crude
> leather-and-scrap armor, gripping a spiked wooden club in both hands, facing slightly to
> the left, exactly the same art style, palette, outline weight, and proportions as the
> attached reference image.

…then the boilerplate block (note: facing LEFT — enemies face the town).

## Asset 3 — battlefield backdrop
**Filename:** `raw_bg_battlefield_v1.png` · attach the anchor. Square output accepted (see
ground rule 7) — composition should put sky in the top third, the wall/gate at the left
edge, and open field lower-right, so a wide band crops cleanly out of the square.

> A wide empty battlefield landscape in 16-bit fantasy RPG pixel art style, matching the art
> style and palette of the attached reference image: trampled grass and dirt in the
> foreground, a sturdy stone kingdom wall with a wooden gate at the far left edge, dark pine
> forest and mountains in the distance to the right, overcast late-afternoon light. Muted,
> desaturated colors so that characters and UI will stand out on top of it. No characters,
> no creatures, no text, no UI elements, no borders.

## Asset 4 — UI panel frame (for CSS chrome)
**Filename:** `raw_ui_frame.png` · attach the anchor.

> An ornate rectangular user-interface panel frame in 16-bit fantasy RPG pixel art style,
> matching the palette of the attached reference image: dark aged wood edges with antique
> gold corner ornaments and subtle rivets, perfectly symmetrical top-to-bottom and
> left-to-right, surrounding a plain flat very dark parchment center. The frame border is the
> subject — keep the center empty and undecorated. Solid magenta background (#FF00FF) outside
> the frame, no text, no icons, no watermark.

(The center gets discarded — this becomes a CSS `border-image`, so symmetry and a clean
uniform border width matter more than beauty.)

---

## What Claude does once the raws land
- Build `tools/process-art.html` — a zero-dependency browser-canvas tool: keys out the
  magenta, trims to content, downscales to target sizes (battle-unit and 52px portrait-crop
  test), exports processed PNGs into `assets/`. (Downscale method — nearest-neighbor vs
  smooth + palette quantization — gets decided by eye during the pilot; faux-pixel grids
  sometimes shimmer under nearest-neighbor.)
- Note: every character fills its frame at generation time regardless of the creature's size —
  relative in-game scale (a boss looming over a goblin) is set at integration by rendering
  size, which spends the model's resolution where it helps. Target pixel sizes are pipeline
  parameters, dialed when the first sprites land in the real battle column.
- Build a throwaway test scene: knight vs goblin standing on the backdrop at battle size,
  HP bars overlaid, inside a frame-chrome panel — screenshot for judgment.
- Create `assets/CREDITS.md` with the batch entry ("Generated with Google Gemini, date").

## Pilot pass/fail criteria (judged together in chat)
1. Do assets 1 and 2 read as the same game? (The consistency question — the whole run
   depends on it.)
2. Does a downscaled character stay readable at battle-slot size and as a 52px portrait crop?
3. Does the magenta key cleanly, or do edges halo? (Halo is usually fixable in post — but we
   want to know now.)
4. Does the frame slice into usable CSS chrome?

If any fail, we adjust prompts/process and re-pilot — cheap. Only after a pass do we commit
to the full asset list (Claude will produce the complete spec doc with all ~47 character
prompts, batched by category: heroes → per-tier enemy rosters → bosses → townsfolk →
remaining backdrops/chrome).

## Licensing / disclosure notes (for the record)
- Log every batch in `assets/CREDITS.md`: tool, date, who generated.
- AI-generated assets: fine for this project; if the game is ever published on a storefront
  (itch.io, Steam), those stores require disclosing AI-generated assets at submission — a
  checkbox, not a problem, but remember it exists.
