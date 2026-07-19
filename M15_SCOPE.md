# M15 Scope — Game Feel: Visuals & Sound

> Working scope doc, drafted 2026-07-17 during the M15 scoping conversation. Untracked until
> the open decisions at the bottom are made; fold the final decisions into CLAUDE.md's M15
> section when the milestone starts.

## Constraints (standing)
- Plain HTML/CSS/JS, no build step. Any assets committed to the repo.
- Must stay smooth at 100× dev speed — effects are budgeted/coalesced, never per-event at high speed.
- **Balance-independent by construction**: the juice layer consumes *events with payload data*
  (damage amounts, tier names, the live escalation multiplier). No effect keys off a specific
  balance value or threshold, so future balance passes (post-M14 adjustments are expected)
  never touch M15 code, and vice versa.
- The developer authors no visuals; audio uses prefab (CC0) assets until/unless they decide to
  compose their own — the architecture must make that swap trivial (see the sound manifest).

## Phase 0 — Render-layer refactor — ✅ DONE 2026-07-17 (all exit criteria met)
Verified: 100× dev speed measured at a **true 100× effective** (500 game-seconds in 5.0 wall
seconds; sim tick ~0.02ms — was 5–8× effective before); CSS animations survive across ticks
(persistent battle slots — hit flashes and floating numbers confirmed live in battle); zero
console errors across fresh boot, three organic run-ends (repelled waves, squad wipe → siege →
overrun → summary → new Age), hires, level-ups, and the dismiss-arming flow. First FX
consumers shipped with the bus: damage/heal floats, hit/heal flashes, kingdom-hit flash, with
per-frame coalescing and a `prefers-reduced-motion` guard. Death/revive FX deferred to
Phase 1 as planned. Architecture documented in CLAUDE.md (*Render architecture*).

Original scope (for the record):

**Why this must come first:** `tickRender()` rebuilds panels with `innerHTML` every tick.
Two consequences:
1. The known perf debt — 100× dev speed runs at ~5–8× effective (DOM rebuild cost).
2. **It makes animation impossible.** A CSS animation dies when its element is recreated;
   at 1× every element is recreated every second. (Visible today: the siege-pulse banner's
   animation restarts every tick — it only *looks* right because the pulse period happens to
   be ~1s.) Hit-flashes, lunges, death fades, HP-bar transitions all require DOM nodes that
   persist across ticks.

Work items:
- **Sim/render decoupling:** `tick()` becomes pure simulation. A `requestAnimationFrame` loop
  renders instead, capped (~10–15fps for panel updates; FX layer runs at full rAF rate).
  Mutating functions set per-panel dirty flags rather than calling render directly.
- **Keyed battle-slot DOM:** `renderSquad` creates each slot element once and updates it in
  place (name/stats text nodes, HP-fill width, alive/dead/armed classes). Slots get stable
  identity so effects can target them.
- **FX/event bus:** combat and economy functions emit typed events
  (`{type:'hit', target, dmg}`, `{type:'death'}`, …). One FX consumer renders floating
  numbers / flashes / sounds from the queue **with a central budget**: per-window caps,
  damage-number coalescing per unit (at 100×, one aggregated number per unit per ~100ms, not
  100 numbers). This is the single mechanism that satisfies the "100× must not fire 100× the
  particles and sounds" constraint — no scattered throttles.

Exit criteria: 100× runs at ~100× effective (measure with the existing soak approach); a test
animation on a battle slot runs uninterrupted across ticks; zero console errors in a full run.

## Phase 1 — Combat & kingdom juice — ✅ DONE 2026-07-17 (browser-verified same day)
Shipped: attacker micro-lunges (heroes lunge right, enemies left, on every attack fire incl.
kingdom attacks); death FX (enemies flash-and-settle in place; heroes spawn a fading "ghost"
card in the overlay layer since their slot frees instantly — geometry captured pre-rebuild by
draining FX at the top of renderAll); revive golden flash (necromancer + Blessing, emitted by
resolveAttack checking alive-state after onUnitDeath); chill = steady blue tint + ❄ badge
(state-driven in updateSquad); Kingdom HP crimson damage-trail (structure memoized without
live values, widths updated in place, trail lags 0.7%/frame and snaps up on heal); kingdom
hits = panel flash + small screen shake + red screen-edge vignette pulse; sapper injury =
town-panel flash; raid arrival = status-bar slam; repelled = gold flash + "+Ng" loot float +
"+N" Legacy badge on the admin resource row; escalation = deepening red wash on the enemy
squad container driven live by escalationMult. Floats/ghosts live in an #fx-layer overlay
(squad rebuilds can't kill them); all spawns skip under prefers-reduced-motion (JS-gated for
removal-dependent nodes, CSS-gated for flashes). Verified: floats/ghost/trail/payoff moment
captured live in-browser; tick cost ~0.009ms with FX emits; zero console errors.
Not visually exercised (class-bound, low risk): chill tint (no chill source in goblin tier),
injury flash (sappers debut at Bandit), escalation wash (needs a 60s+ battle) — confirm in
the next real playtest.

Original emitter table:

| Event | Source | Effect |
|---|---|---|
| Hit lands | `resolveAttack` | floating damage number, hit-flash, attacker micro-lunge toward target |
| Heal lands | `resolveHeal` | green float + brief glow on target |
| Unit dies | `onUnitDeath` path | collapse/fade; slot release reads as a death, not a vanish |
| Revive (necro/Blessing) | `onUnitDeath` | distinct dramatic rise effect — these are teachable moments |
| Chill applied | `resolveAttack` | frost tint while `chilled()` |
| Kingdom takes a hit | `attackKingdom` | screen-edge vignette pulse + small shake; HP-bar ghost/damage-trail |
| Resident injured | `maybeInjureResident` | town-panel flash so sapper pressure reads from the battle column |
| Escalation active | `escalationMult` > 1 | enemy-side tint deepening with the live multiplier; banner intensifies |
| Raid arrives | `startInvasion` | banner slam-in (horn lands in Phase 3) |
| Repelled | `winInvasion` | victory sting frame, loot + Legacy pop |

## Phase 2 — Town & progression juice — ✅ DONE 2026-07-17 (browser-verified same day)
Shipped (all pure CSS/JS, zero assets):
- **Gold counter easing**: display rolls 25% of the gap per frame toward true gold, snaps
  within 2 — purchases visibly "spend down". Purely presentational; all checks read real gold.
- **"+N g/s" hire floater**: badge on the admin per-second row (hp/s hires badge the Kingdom
  HP panel); coalesced in drainFx so an auto-hire spree floats ONE summed badge.
- **Building purchase flash**: gold pulse on the bought card via the postRenderFlashes queue —
  a new mechanism for flashes targeting memoized-panel content (drainFx runs before panels
  render, so panel-content flashes must apply after the rebuild settles).
- **Pool-refresh shuffle**: fresh cards deal in with a 50ms stagger (pool/hero-pool generation
  counters); wall-clock gated ≥400ms between replays so 100× can't strobe.
- **Level-up fanfare**: full-width "The realm rises — <LEVEL>" banner, 2.2s, one at a time.
- **Kingdom-fall shroud**: endRun darkens the screen (950ms dramatic / 450ms for abandoned),
  THEN the summary rises through the lifting shroud. Reload-mid-summary still shows instantly.
- **Dawn wash** on Found a New Age; **victory polish** (shimmering title, ages stagger in).
- **Reduced-motion toggle**: Motion panel (Full/Reduced) persisted in `meta.reduceMotion`
  (additive, no SAVE_VERSION bump); system `prefers-reduced-motion` forces+locks it. Single
  mechanism: `reducedMotion()` gates JS spawns, `body.reduce-motion` (synced each frame)
  gates CSS animation classes; `removeOnAnimationDone` also listens for `animationcancel` so
  toggling mid-animation can't leak invisible nodes.
- Legacy pop at wave clear shipped earlier with Phase 1 (repelled loot float + Legacy badge).

Verified in-browser: easing lag+converge measured, hire badge text exact, built-flash class
observed, shroud beat → overlay reveal timings confirmed, dawn suppressed under Reduced,
toggle persists across reload, zero console errors — including through an organic Age fall
that happened mid-test at speed.

## Phase 3 — Audio — ✅ IMPLEMENTED 2026-07-19 (browser-verified; the developer's
## by-ear audition via the DEV sound board is the remaining acceptance gate)
Shipped exactly per the plan below: engine + manifest (24 sounds: 15 file-backed from the
three Kenney packs in `assets/audio/` — RPG/Impact/UI, 232 files committed, CC0 verified —
and 9 synth recipes for the gaps: heal/revive chimes, war horn, heartbeat, win/fall
stingers, fanfares, dawn), FX-bus audio consumer reading the same per-frame aggregates as
the visuals, per-class wall-clock gaps + per-sound minGaps + 8-voice cap + master
compressor, `meta.soundVolume`/`meta.soundMuted` with UI in the scene corner chip and the
classic admin Sound row, state-driven escalation heartbeat, DEV "SFX board" (corner chip →
SFX). Instrumented soak: 107 sim-seconds of battle at ~36× → 1 horn, 15 hits, 10 heals,
4 deaths, 1 heartbeat, voices drained to 0, zero console errors. The CREDITS pre-commit
guard is live (`.githooks/pre-commit` + `core.hooksPath`; fail/pass/idempotency
scratch-tested; NOTE: each machine wires `git config core.hooksPath .githooks` once).

### Original firmed plan (2026-07-19) — kept for the record
Sketch above superseded by this build plan (route recommendation: see decision 2).

**Constraint check (new since the sketch):** Web Audio buffer loading (`fetch` +
`decodeAudioData`) is blocked on `file://` exactly like canvas pixel access — same
already-accepted constraint as sprites (http dev serving; M17 owns shipping). Loader
degrades to silence per missing file, mirroring the letter-portrait fallback.

**Engine (S, ~200 lines in game.js — same single-file convention as everything else):**
- `AudioContext` lazily created/resumed on first pointer gesture, hooked into the existing
  `bindActionDispatch` document listeners (mechanism reuse, satisfies autoplay policy).
- Master chain: per-sound gain → master gain (from `meta.soundVolume`) →
  `DynamicsCompressorNode` → destination. The compressor is the 100×-pileup clipping guard.
- **Sound manifest**: `SOUNDS = { hit_light: { file:'assets/sfx/…', vol:0.5, pitchVar:0.1 }, … }`
  — one entry per event name; an entry may instead carry `synth:` params (ZzFX-style) so the
  route is swappable PER SOUND. Missing file = that sound is silent, never an error.
- Playback: pitch variance (±8–12%) on repeat-prone sounds; per-class wall-clock rate
  limits + a per-drain voice budget (below); voice cap ~8, lowest priority dropped.
- **Settings**: `meta.soundVolume` (0–1, default ~0.6) + `meta.soundMuted` — additive meta
  fields, no SAVE_VERSION bump; UI in the scene corner system chip + classic admin panel,
  next to the Motion toggle (same pattern).

**Integration — one stream, two consumers:** the audio consumer drains the SAME FX bus the
visuals use (`drainFx`), with its own budget. Simulation-driven sounds ride existing bus
types; user-initiated one-shots (clicks — already self-rate-limited) call `playSfx` direct.
The **escalation heartbeat** is state-driven like the red wash, not bus-driven: a scheduled
loop whose tempo/intensity tracks `escalationMult`, running only while a battle escalates.
Hidden-tab silence falls out for free (rAF stops → no drain).

**Event → sound map (budget class in brackets; bus type where it exists):**
| Sound | Trigger | Class |
|---|---|---|
| hit_light / hit_heavy (by damage share) | bus `hit` | [combat: ≥70ms apart, ≤2/drain] |
| heal chime | bus `heal` | [combat] |
| unit death (hero vs enemy variants) | bus death path | [accent: ≥120ms, always allow boss] |
| revive shimmer | bus revive | [accent] |
| kingdom thud (pairs with shake/vignette) | bus `kingdomHit` | [accent] |
| hire (hero / resident), building buy, upgrade buy, muster press | direct on click | [ui: ≥60ms] |
| level-up fanfare, Legacy chime (wave bank) | bus `levelup` / repelled payout | [sting: one at a time] |
| raid horn | `startInvasion` | [sting] |
| escalation heartbeat | state-driven loop | [own scheduler] |
| Repelled sting / Kingdom-fall sting / dawn motif / victory fanfare | run-event paths | [sting] |

**Assets & workflow (mirrors the art loop — developer supplies, Claude integrates):**
CC0 packs, a few hundred KB of .ogg into `assets/sfx/`; Kenney "RPG Audio" + "Impact
Sounds" + "Interface Sounds" cover most of the map (horn + heartbeat likely freesound.org
CC0). The DEVELOPER downloads the packs (license verified on the download page at grab
time); Claude curates files out of them, normalizes names, wires the manifest, and logs
every file in `assets/CREDITS.md` in the same commit. **Mechanize the CREDITS ritual now**
(process-hygiene: first multi-file asset influx): a `.githooks/pre-commit` that fails if
any file under `assets/` lacks a CREDITS.md line, wired via `core.hooksPath`.

**Acceptance — the sound board:** a DEV_MODE-only in-game panel listing every manifest
entry with a play button (reuses the live engine, no separate tool page). The developer's
by-ear audition pass is the gate, exactly like the art pilot; plus a 100× soak with a
voice-count instrument proving the budget holds (~1× soundscape at any sim speed) and
zero console errors.

**Build order:** S0 engine + settings UI + CREDITS pre-commit hook + 2 placeholder sounds
proving the chain → developer downloads packs → S1 combat layer (hits/heals/deaths/
kingdom) tuned at 1× and soaked at 100× → S2 UI one-shots + level-up/Legacy → S3 dramatic
layer (horn, heartbeat, stingers, fanfare) → sound-board audition pass → done.
**Music stays out of Phase 3** — see decision 3 (crossfade hook stays cheap to add later).

## Sprite pipeline — ✅ DONE 2026-07-17 (runtime, no build step; T2's foundation)
The game loads the RAW magenta PNGs straight from `assets/raw/` and runs the whole pipeline
at boot in memory: magenta keying, content trim, foot-anchor computation, downscale to
`SPRITE_MAX_H` (160px), stored as tiny `blob:` object URLs. `SPRITE_SOURCES` maps all 47
character keys to spec filenames (`M15_ASSET_SPECS.md` names); a missing file = silent
letter-portrait fallback per key, so **an art drop is "copy PNG into assets/raw/, refresh"**
— no processing step, no duplicate assets, no manifest files. Sprites show in: town recruit
cards, resident portrait grids (✚ still overrides when injured), hero recruit cards, and
battle slots (corner-anchored background, provisional pending the T2 diorama; late async
loads adopted per frame in updateSquad). Enemy units carry `spriteKey` from generateEnemy
(tier `key` field added to RAID_TIERS); heroes derive from `archetypeKey`. Requires http
serving (canvas pixel access is blocked on file:// — loader degrades to letters).
Verified in-browser with the two existing sprites: knight in hero slot + pool chip, goblin
brute in enemy slot, letters everywhere else, zero console errors.

## Phase 4 — Art pass (DIRECTION CHOSEN 2026-07-17: Gemini-generated, user-in-the-loop)

> **THE MOCKUP IS THE DESTINATION (re-affirmed by the developer 2026-07-17).** M15's end state
> is the game *looking like the one-scene mockup*: a complete visual overhaul — town vista →
> wall → battlefield as the primary presentation — not the current panel UI with sprites
> swapped in for letters. All three tiers below are committed scope, in order, as assets
> arrive; T1/T2/T3 is a build sequence, not a priority ranking with an optional tail. The
> sprites-in-old-panels state that exists today is pipeline scaffolding (it makes every asset
> drop immediately visible and testable) and is explicitly NOT a candidate end state.

The developer produced Gemini pixel-art mockups matching their vision (one-scene town→wall→
battlefield panorama). **Workflow:** Claude writes exact per-asset specs/prompts
(`M15_ART_PILOT.md`), the developer generates in Gemini and saves raws to `assets/raw/`,
Claude post-processes (magenta keying, trim, nearest-neighbor downscale) via a
zero-dependency browser-canvas tool (`tools/process-art.html`) and integrates. Consistency
mechanism: a **style-anchor reference image** (first generation) attached to every later
prompt. Mockups are baked paintings — we extract the visual language, not their fictional UI
(gems/wood/build-queue don't exist).

Tiers, in build order:
- **T1 — atmosphere reskin:** continuous painted backdrop + panel chrome as CSS
  `border-image` from a generated frame texture. Panels/buttons/text stay DOM+CSS, never
  baked into images.
- **T2 — battle diorama:** battle column becomes full-body sprites on the battlefield
  backdrop with HP overlays; stats move to hover/selection. (Phase 0's layered slot DOM
  anticipates exactly this.)
- **T3 — living town vista:** building sprites at fixed predrawn positions, toggled by
  ownership, with count plaques (the mockup's "LV" tags pattern). Fixed positions — never
  free placement — is what keeps this affordable. After T1/T2.
- **T4 — kingdom-prosperity progression (STRETCH, post-T3; user idea 2026-07-18):** the
  town half visibly prospers as kingdom tiers are reached. The T3 building layer already
  carries most of this fantasy (Hamlet = 3 cottages on bare ground; Realm = full
  enclosure), so T4 is polish-on-polish — cheapest mechanism first:
  1. Tier-gated **decoration sprites** through the building pipeline (wall banners,
     market stalls, lamp posts, well→fountain, cobble patches) at fixed positions —
     no engine work, ~10–15 small lazy generations; they key off kingdomLevel, which
     resets each Age, so the New-Age return to bare ground strengthens for free.
  2. **CSS grading + crowd density** per tier (warmth/saturation lift on the town half;
     more plaza villagers) — zero assets.
  3. Full **backdrop variants** only if 1+2 underdeliver, and then ONLY by editing the
     accepted vista in place in Gemini ("this exact image, but…"), never fresh
     generation — T3 building anchors are pixel positions and regenerated scenes drift
     geometry. Bucket to ~3 states (frontier / town / imperial), not one per level.

Asset count: ~47 characters (9 heroes, 25 enemies, 5 bosses, 8 townsfolk — rarity stays a
CSS border, no art variants) + backdrops + chrome + portrait busts of the same characters.
The earlier authored-SVG portrait route (samples approved 2026-07-17) is **superseded** for
style consistency — portraits become bust generations of the same characters; SVG remains
the fallback if the pilot fails.
Superseded options for the record: CC0 pixel packs (style-mismatch risk across 47 units);
commissioned art (not while private).

## Asset licensing primer (written for zero prior experience)
- **CC0 / public domain** — no conditions at all. No credit required (crediting is still a
  nice gesture). Safe forever, including if the game is ever sold. **Use this tier only.**
- **CC-BY** — free, but you *must* credit the author in a stated form. Fine, but it creates a
  permanent bookkeeping obligation and a failure mode (forgotten credit = license violation).
- **CC-BY-SA / GPL-style** — "share-alike": can obligate you to license your own work the
  same way. Avoid for game assets unless you've decided you want that.
- **CC-BY-NC** — non-commercial only. Poison for a game that might ever hit itch/Steam. Avoid.
- **"Royalty-free"** — a marketing term, not a license. Means "pay once, no per-use fees";
  the actual terms vary per marketplace. Read them, or stick to CC0.
- **AI-generated** — usable, but provenance/licensing norms are still unsettled and style
  consistency across 47 sprites is genuinely hard; treat as a last resort for gap-filling.

**Policy: CC0-only, enforced by ritual** — every file that lands in `assets/` gets a line in
`assets/CREDITS.md` (source URL, author, license, date) *in the same commit*, and the license
is verified on the download page at grab time, not assumed from the site's reputation.
(Candidate mechanization once assets exist: pre-commit check that every file under `assets/`
has a CREDITS.md line.)

**CC0 sourcing shortlist** (verify license on each download page as part of the ritual):
- **Kenney.nl** — the gold standard; everything CC0. Audio: "RPG Audio", "Impact Sounds",
  "Interface Sounds" packs. Art: "Tiny Dungeon" 16×16 fantasy characters.
- **OpenGameArt.org** — filter by CC0.
- **freesound.org** — filter by CC0; louder/messier library, good for horns/ambience.
- **itch.io asset packs** — many CC0 pixel packs (e.g. 0x72's dungeon tilesets); check each.
- If the zero-binary-assets route is ever wanted instead: **ZzFX / jsfxr** (MIT) generate
  chiptune SFX from ~20 numeric params, no files at all. Chiptune flavor, less "medieval".

## Sequencing & sizing (relative)
| Phase | Size | Depends on |
|---|---|---|
| 0 render refactor | **L** — touches every render path; the risky one | — |
| 1 combat juice | M | 0 |
| 2 town/run juice | M | 0 (parallel with 1) |
| 3 audio | M (engine S; curation is the variable) | 0 (event bus) |
| 4 art pass | M–XL | asset delivery cadence — **committed scope, the milestone's end state** (see Phase 4 banner) |

## Open decisions (owner: developer)
1. **Art direction** — DECIDED 2026-07-17 (superseding the same-day SVG-portrait decision):
   Gemini-generated pixel-flavored assets via the user-in-the-loop workflow, per the
   developer's mockups. See Phase 4 for tiers and workflow. Battlefield representation
   resolved: full-body sprites on a painted field (T2). **Next gate: the 4-asset pilot**
   (`M15_ART_PILOT.md`) — pass/fail on consistency, downscale readability, keying, and
   chrome slicing before committing to the full run. Phase 0 note stands: battle-slot DOM
   is a layered positioned container (art layer + HP overlay + effect layer), not a text card.
2. **Audio route** — RECOMMENDED 2026-07-19 (developer to confirm at Phase 3 start):
   CC0 sample packs as the primary source — medieval foley (horns, steel, thuds) resists
   convincing synthesis, and the art direction settled painterly-soft rather than harsh
   8-bit, so recorded samples fit better than chiptune. The manifest keeps the route
   swappable per sound: any entry can carry ZzFX-style `synth:` params instead of a file,
   which is also the gap-filler when a needed sound can't be curated.
3. **Music** — recommended: defer entirely; the manifest + a town/battle crossfade hook is
   cheap to add later, and the developer may want to compose these themselves. Prefab CC0
   music exists but is the weakest CC0 category.
4. Confirm phase order (0 → 1 → 2 → 3, with 4 floating).
