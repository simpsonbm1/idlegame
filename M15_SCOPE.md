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

## Phase 1 — Combat & kingdom juice (pure CSS/JS, zero assets)
All emitter sites already exist and are single functions:

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

## Phase 2 — Town & progression juice (pure CSS/JS, zero assets)
- Gold counter easing (lerp toward the true value instead of snapping).
- "+N g/s" floater on hire; purchase flash on buildings; pool-refresh shuffle animation.
- Kingdom level-up fanfare moment (full-width flourish — it's the economic ratchet, make it land).
- Legacy pop at wave clear (`bankWaveLegacy`).
- Run drama: Kingdom-fall transition into the run summary (`endRun`) — darken/crumble beat
  before the overlay; "Found a New Age" dawn transition (`foundNewAge`); victory-screen polish
  (`campaignVictory`).
- QoL alongside: reduced-motion/no-shake toggle; auto-respect `prefers-reduced-motion`.

## Phase 3 — Audio (SoundBoard engine + prefab CC0 assets)
Engine (small, ~150–250 lines):
- Web Audio API. `AudioContext` created/resumed on first user gesture (autoplay policy).
- **Sound manifest**: `SOUNDS = { hit_light: {file:'assets/sfx/hit1.ogg', vol:0.5, pitchVar:0.1}, … }`
  keyed by event name. Each entry is a file reference (or later, synth params) — **swapping in
  the developer's own recordings is editing one line per sound**, which is the contract that
  keeps prefabs non-committal.
- Pitch-varied playback (±10%) so repeated hits don't machine-gun; per-window sound budget
  shared with the FX bus (at 100×, hits collapse to a capped rate).
- Master volume + mute, persisted in `meta` (additive field — no SAVE_VERSION bump needed).
- Event coverage: light/heavy hits, death, heal, revive, hero hire, resident hire, building
  buy, level-up, raid horn, escalation heartbeat (builds with the multiplier), Repelled sting,
  Kingdom-fall sting, Legacy chime, upgrade purchase, Final Siege victory fanfare.

Assets: CC0 packs (see sourcing below), a few hundred KB of .ogg committed to `assets/sfx/`.
**Music is deliberately out of Phase 3** — see decisions.

## Phase 4 — Art pass (DIRECTION CHOSEN 2026-07-17: Gemini-generated, user-in-the-loop)
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
| 4 art pass | M–XL depending on option | nothing — deferrable indefinitely |

## Open decisions (owner: developer)
1. **Art direction** — DECIDED 2026-07-17 (superseding the same-day SVG-portrait decision):
   Gemini-generated pixel-flavored assets via the user-in-the-loop workflow, per the
   developer's mockups. See Phase 4 for tiers and workflow. Battlefield representation
   resolved: full-body sprites on a painted field (T2). **Next gate: the 4-asset pilot**
   (`M15_ART_PILOT.md`) — pass/fail on consistency, downscale readability, keying, and
   chrome slicing before committing to the full run. Phase 0 note stands: battle-slot DOM
   is a layered positioned container (art layer + HP overlay + effect layer), not a text card.
2. **Audio route** — CC0 sample packs (recommended: medieval-appropriate, manifest keeps them
   swappable) vs ZzFX-style synthesis (zero assets, chiptune flavor).
3. **Music** — recommended: defer entirely; the manifest + a town/battle crossfade hook is
   cheap to add later, and the developer may want to compose these themselves. Prefab CC0
   music exists but is the weakest CC0 category.
4. Confirm phase order (0 → 1 → 2 → 3, with 4 floating).
