# Idle Kingdom — Project Context

## What this is
A medieval fantasy **incremental kingdom-defense game**: the passive town-building and gold generation of a Realm Grinder feeds an active Legionbound-style autobattler at the town gates — and the autobattler is the *primary* mechanic. No click-to-earn; the economy is fully idle once set up.

**It is deliberately a finite experience, not an infinite number-go-up idle.** Target shape: a ~5-hour arc (Gnorp Apologue / Wizard Tower scale) of **8–10 death-and-rebuild runs**, each ending when the Kingdom falls, funding permanent upgrades until the player can defeat a scripted **Final Siege** — the victory condition. An optional endless mode unlocks after victory. See *Progression loop redesign*.

This is the developer's first coding project. Keep explanations clear, define new terms, and prefer small working milestones over large upfront designs.

**Design-first, not code-first:** the current `game.js` is a prototype hodgepodge of half-baked concepts mid-transition to something playable. The design sections of this file (especially *Progression loop redesign*) are the source of truth; the code gets redesigned around them. Don't treat what the code currently does as a design constraint or authority — read it to estimate implementation cost or find gaps, not to justify design choices.

## Keeping this file current
**Before committing or pushing changes, update this file to reflect the current state of the project.** Mechanics, formulas, balance values, and design decisions documented here should match what's actually implemented in `game.js` — this file is the map other sessions (and the developer) use to understand the game without re-reading all the code.

## Session handoff + cross-machine WIP sync
This project follows the global session-handoff practice (`~/.claude/CLAUDE.md`): maintain a
`SESSION_HANDOFF.md` at repo root, kept continuously current during a session, as a safety net
against a usage-limit cutoff with no warning. Gitignored, not auto-committed to this repo's own
history — normal ask-first commit policy applies to real commits here.

**Opted in to cross-machine WIP sync** (see `~/.claude/CLAUDE.md` → Session Handoff Continuity —
this exact phrase is the marker the `handoff-sync.ps1` hook greps for). On every `SESSION_HANDOFF.md`
update, the PostToolUse hook automatically snapshots this repo's uncommitted changes (tracked +
untracked, respecting `.gitignore`) to a disposable `wip/<hostname>` branch on `origin` — never to
`main`. At session start, act on the SessionStart hook's report: `git cherry-pick --no-commit` an
incoming `wip/<other-hostname>` branch (stop and ask on conflict), then **delete the remote branch
immediately after the cherry-pick succeeds**.

## Tech stack
Plain HTML + CSS + JavaScript. No frameworks, no build step. Open `index.html` in a browser to run.

## File structure
- `index.html` — page structure and UI elements
- `style.css` — medieval dark theme styling
- `game.js` — all game logic
- `tools/balance-sim.js` — Node balance simulator (`node tools/balance-sim.js`): models a greedy player at 1× with a mirror of game.js constants and a port of the combat engine; prints run timelines, squad-vs-wave win-rate tables, fair-fight win durations (validates the escalation grace), and a stalemate/grind table (endless siege + continuous rehires — the model that captures the real wall-grinding strategy the discrete win-rate table misses). Used for the M9/M9.6 tuning passes; rerun for any balance change (M14). **Keep its constant tables in sync with game.js.**

## Core mechanics

### Buildings
Buildings are slot containers — they don't generate income directly. Each building purchased opens a fixed number of resident slots. Each building type has its own cost growth rate (`costGrowth` in `game.js`), individually tuned so early buildings (Cottage, Tavern, Smithy, Library) stay affordable for longer while late-game buildings (Apothecary, Tower, Cathedral) ramp up faster — replacing the old single global 1.15x multiplier.

**Keep is the one exception:** it has `slotsPerBuilding: 0` and never houses residents. See *Heroes & combat* below for what it does instead.

### Residents
Residents are hired to fill building slots. Each hire costs gold and does a **one-time random roll** that permanently determines that resident's income — gold/sec for most buildings, Kingdom-HP-regen/sec for Workshop's Builders (see *Heroes & combat*). Residents can be fired for free (no cost) and re-hired to reroll — this is the core optimization loop.

### Resources
- **Gold** — the primary resource, used for buildings, residents, and hero recruiting.
- **Kingdom HP** — a persistent health pool (see *Heroes & combat*); not spendable, but a key survival stat.

### Heroes & combat
See *Invasion & combat system* for the full design — heroes are recruited separately from townspeople, fight raids in a 2x3 squad grid, and their losses damage Kingdom HP rather than the heroes themselves.

## Recruit pool system
Instead of hiring on demand, a pool of 5 recruits refreshes every 10 seconds in the "Town Square" section. Each recruit has a rarity tier that scales their income and cost.

**Rarity tiers:**
| Tier | Income mult | Cost mult | Color |
|---|---|---|---|
| Common | 1× | 1× | Gray |
| Rare | 2.5× | 3× | Blue |
| Epic | 5× | 8× | Purple |
| Legendary | 10× | 20× | Gold |

Rarity weights improve with kingdom level, and they are **deliberately stingy early** (M9): one rarity step is worth ~1.5 raid tiers of squad power (sim-verified), so rarity availability is the main knob pacing how deep a run can push. Commons dominate through City; epic appears at City (2%), legendary at Kingdom (1%), and the curve only opens up at Empire+ (`RARITY_WEIGHT_TABLE`).

**Recruit types** map to building types (Villager→Cottage, Tavernkeeper→Tavern, etc.). Only recruits for unlocked buildings appear in the pool.

The old per-resident lucky-roll system is replaced by the rarity tier system.

**Portrait grid:** Buildings show a grid of slot icons instead of a text list. Filled slots show a pixel-style portrait (letter + type color background + rarity glow border). Clicking a portrait dismisses that resident. Empty slots shown as dim squares.

A second, separate pool works the same way for **hero recruiting** — see *Invasion & combat system*.

## Design decisions locked in
- Fully idle economy — no clicking to earn resources
- One-time roll on hire (not per-tick variance)
- Free eviction (fire and re-hire to reroll)
- Buildings are slot containers, not direct income sources
- Cost scaling: per-building growth rates (no single global multiplier) — each building's curve is tuned to its place in the progression
- **Finite game** (~5 hours, 8–10 runs), with the Final Siege as the victory condition and an endless mode after victory — not an infinite idle
- **The autobattler is the primary mechanic**; the town economy exists to fuel it
- **Single in-run currency: gold** (buildings, residents, and hero hiring all paid in gold — no separate "Spoils" combat currency). The meta currency (Legacy Points) exists only between runs
- **A wave repeats until beaten** (losing a raid re-fights the same wave — no skipping ahead), and **meta-currency credit is first-ever-clear** with a small repeat trickle (~10–20%): each wave pays full value once across the whole campaign, so pushing new depth is the way to earn and restart-farming is pointless
- **Battles are persistent sieges** — no end on squad wipe; hero hiring stays available mid-battle (pool keeps refreshing), and Kingdom HP soaks damage while no hero stands. Raids end only Repelled or Overrun (Kingdom HP 0 → forced restart) — and **sieges escalate** (see *Combat*), so every battle is guaranteed to eventually resolve one way or the other
- RPG/dungeon elements are a possible future addition

## Current building roster (M9 shrink)

Buildings are deliberately scarce — a handful of each, 2–3 slots each, so every purchase and staffing choice matters. Hire costs are sized for **~60–190s payback** at the average roll, so income ramps over minutes.

| Building | Cost | Growth | Slots | Resident | Hire cost | Income roll |
|---|---|---|---|---|---|---|
| Cottage | 10g | 1.30× | 2 | Villager | 25g | 1–3 g/s |
| Tavern | 250g | 1.30× | 2 | Tavernkeeper | 300g | 4–8 g/s |
| Smithy | 1,500g | 1.35× | 2 | Blacksmith | 1,200g | 10–20 g/s |
| Library | 6,000g | 1.35× | 2 | Scholar | 4,500g | 30–60 g/s |
| Workshop | 400g | 1.35× | 2 | Builder | 250g | 0.3–0.8 hp/s |
| Keep | 40,000g | 1.50× | 0 | — | — | — (each Keep owned biases hero recruit rarity, see below) |
| Apothecary | 25,000g | 1.40× | 3 | Alchemist | 15,000g | 80–160 g/s |
| Wizard's Tower | 100,000g | 1.45× | 3 | Mage | 60,000g | 250–500 g/s |
| Cathedral | 400,000g | 1.50× | 3 | High Priest | 200,000g | 700–1,400 g/s |

Income rolls are then multiplied by the recruit's rarity tier (see *Recruit pool system*). Numbers set by the M9 sim pass (`tools/balance-sim.js`); final calibration is M14.

## Kingdom level system
The player's kingdom has a level (Hamlet → Village → Town → City → Kingdom) that acts as the unified progression gate. Leveling up costs gold and does two things simultaneously:
1. Raises the cap on how many of each building you can own
2. Unlocks new building types

This replaces a separate "unlock threshold" system — kingdom level IS the unlock gate.

Level-up is manual (spend gold via a button), not automatic.

| Level | Name | Cost | Cottage | Tavern | Smithy | Library | Workshop | Keep | Apothecary | Tower | Cathedral | Unlocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Hamlet | — | 3 | — | — | — | — | — | — | — | — | Cottage |
| 1 | Village | 400g | 5 | 2 | — | — | 1 | — | — | — | — | Tavern, Workshop |
| 2 | Town | 3,000g | 7 | 3 | 2 | — | 2 | — | — | — | — | Smithy |
| 3 | City | 20,000g | 9 | 4 | 3 | 2 | 2 | — | — | — | — | Library |
| 4 | Kingdom | 80,000g | 11 | 5 | 4 | 3 | 3 | — | — | — | — | — |
| 5 | Empire | 300,000g | 13 | 6 | 5 | 4 | 3 | 1 | 2 | — | — | Apothecary, Keep |
| 6 | Dynasty | 1,000,000g | 15 | 7 | 6 | 5 | 4 | 2 | 3 | 2 | — | Wizard's Tower |
| 7 | Realm | 3,000,000g | 16 | 8 | 7 | 6 | 4 | 3 | 4 | 3 | 2 | Cathedral |

Locked buildings show in the UI with a hint ("Unlocks at Village") so the player can see what they're working toward.

Since raid tiers now advance by boss-kill (not kingdom level), leveling the kingdom is a purely economic ladder: more caps, better rarity weights, new building types. Level costs are deliberately steep from City up — they compete with hero spending for the same gold, and gating rarity weights behind them is what paces squad power across a run.

All numbers are tunable (M9 sim pass; final calibration M14).

## Invasion & combat system

**Trigger:** Town level (2) + 4,000 total gold *earned* (`goldEarned`, a counter that only goes up, separate from current gold — spending down can't delay an invasion). The very first raid arrives after a `FIRST_RAID_GRACE` (75s) prep window — the player needs time to hire their first heroes; after that, raids repeat on the tier's own interval (`RAID_TRIGGER_LEVEL = 2`, `RAID_TRIGGER_GOLD = 4000`).

**No income penalty during battles.** (Removed 2026-07-10: the old "income drops to 25% during a siege" rule was a soft-cap stakes mechanism from the infinite-idle era. With a real loss condition and mid-battle reinforcement hiring, it's obsolete — and it would throttle income at exactly the moment the player needs gold for reinforcements. The small "(siege)" tag next to gold/sec remains as flavor only.)

**Invasion schedule:** Once triggered, a new raid starts every `raidInterval` seconds (per-tier, 45s early tightening to 30s at Dragon Siege) of non-battle time. The raid status bar (right column) shows "Next: <raid name> · Arrives in M:SS" while waiting.

### Raid tiers — one continuous ladder, climbed by boss-kill (M9)
The five tiers form a single ~55-wave ladder. **Kingdom level no longer selects the raid tier**: every run starts at Goblin Raid wave 1, each tier has a fixed `waveCount` ending in a **boss wave**, and killing the boss advances to the next tier's wave 1 (wave counter and win streak reset). A lost wave just re-attacks — the ladder climbs only on wins.

Each tier's `powerMult` picks up where the previous tier's boss left off (`defenseGrowth = 1.088`/wave, continuous across the whole ladder — a new tier is a roster change, not a stat cliff). The final boss lands at ~95× goblin wave 1 stats, inside the 80–100× design target.

| Tier | `powerMult` | Waves (boss on last) | Interval | Boss | Base loot | Roster (brute / skirmisher / caster / shaman) |
|---|---|---|---|---|---|---|
| Goblin Raid | 1.0 | 5 | 45s | Goblin Warmaster | 1,200g | Goblin Brute / Skulker / Slinger / Shaman |
| Orc Warband | 1.52 | 8 | 45s | Orc Warlord | 5,000g | Orc Brute / Berserker / Warcaster / Witch Doctor |
| Bandit Horde | 3.0 | 11 | 40s | Bandit King | 30,000g | Bandit Enforcer / Cutthroat / Marksman / Medic |
| Dark Army | 7.6 | 14 | 35s | Lich Commander | 120,000g | Death Knight / Shadow Reaver / Necromancer / Bone Priest |
| Dragon Siege | 24.7 | 17 | 30s | Dragon Empress | 500,000g | Dragon Guard / Wyrmling / Dragon Mage / Dragonpriest |

**Boss waves:** the tier's named boss is a heavily scaled-up brute (×1.8 power, ×4 HP on top of the wave multiplier) leading an honor guard (brute + skirmisher front, shaman back). Unique boss abilities arrive with M11. Past the Dragon Empress the waves just keep climbing — placeholder until the Final Siege (M13).

**Wave naming:** first wave of a tier shows as just the tier name; later waves as "Goblin Raid (Wave 2)"; boss waves as "Goblin Raid — Goblin Warmaster".

### Combat
Each raid spawns a 2x3 enemy squad (brute + skirmisher front, caster + shaman back, two empty slots) that fights the player's hero squad in the same 2x3 grid layout. Combat runs automatically, advancing by one game-second per `tick()` (so dev-speed multipliers speed up battles too):

- Each unit has independent `attack` and/or `heal` **actions**, each with its own `power`, `speed`, and cooldown (`cooldown = BASE_ATTACK_INTERVAL / speed`, `BASE_ATTACK_INTERVAL = 2500ms`). This lets future hybrid units (e.g. a Paladin) attack and heal on staggered timers without special-casing.
- **Targeting** is weighted, not absolute: an attacker rolls its own `backlineChance` (`DEFAULT_BACKLINE_CHANCE = 0.15`, skirmishers are 0.4) to decide whether it goes after the front row or back row, then picks randomly within that row.
- **Healers** (shamans, menders) always target the lowest-HP% wounded ally on their side; if nobody's wounded the heal is held for next tick.
- Damage: `dmg = max(1, round(attackPower * (1 - defense / 100)))`.
- **Siege escalation (added 2026-07-17):** after `SIEGE_ESCALATION_GRACE` (60) game-seconds of a single battle, enemy **attack** power grows linearly by `SIEGE_ESCALATION_RATE` (+1%) per second — attacks only, never heals (boosting the enemy healer would deepen stalemates, not break them). Applies to hero damage and Kingdom damage alike (`escalationMult` in `resolveAttack`/`attackKingdom`, driven by `currentInvasion.duration`). The raid status bar shows "The siege escalates! Enemy attack +X%" once active. Fair fights never notice it (sim: median win 8–43s across the whole ladder); a battle the squad can't win now ends in an Overrun instead of stalemating forever.
- A battle ends when the enemy squad is wiped (**Repelled** — `winInvasion`) or `kingdomHP` reaches 0 (**Overrun** — the run ends). A hero-squad wipe does *not* end the battle; the siege continues against Kingdom HP while the player can hire reinforcements mid-battle. On a win, surviving heroes are topped off to full HP (menders don't tick between battles and heroes respawn at full HP anyway — wounded bars after a win were a display lie).

**Enemy scaling:** `generateEnemy` scales each archetype's base stats (`ENEMY_ARCHETYPES`) by `mult = tier.powerMult * tier.defenseGrowth^wave` for power stats, and `sqrt(mult)` for HP; boss units additionally multiply by the tier's `boss.powerMult` / `boss.hpMult`. Base stats were softened ~30% in M9 so the tutorial wave is winnable by a few commons — the ladder growth carries the difficulty.

**Loot — win-streak combo system:** each raid tier tracks a win streak:
- **Win**: payout = `baseLoot × lootGrowth^streak` (`lootGrowth` 1.10 everywhere), then the streak increments.
- There is no non-fatal loss anymore: a raid either ends Repelled or the Kingdom is Overrun and the run ends. A lost-but-not-fatal wave simply re-attacks after the raid interval (`tierWave` only advances on wins).

Base loot per tier is in the raid-tier table above — cut ~170× from the pre-M9 values so a win pays roughly **0.2–0.7 minutes of contemporaneous income** (sim-measured): a welcome bonus that helps fund reinforcements, never a substitute for the town economy. Loot does not count toward `goldEarned`. Advancing to the next tier resets the streak.

**Result display:** the raid status bar shows "Repelled: <name> +Xg · +Y Legacy" for the most recent win (`lastVictory`); the "Survived"/"Overrun" inline results are gone (an Overrun goes straight to the run-summary screen instead). While the hero squad is wiped but the battle continues, a pulsing "The Kingdom is under siege!" banner appears in the status bar.

### Kingdom HP
Kingdom HP (`kingdomHP`, max `KINGDOM_HP_MAX = 1000`) is the persistent consequence of losing the hero squad in battle:

- **Heroes "respawn" at full HP at the start of every battle** (`startInvasion` resets `hp = maxHp, alive = true` for the whole squad) — survivors start each battle healed up.
- **The Kingdom is the last line of defense.** While any hero is alive, enemies target the hero squad as normal (`pickTarget`). Once the hero squad is wiped, every surviving enemy attack instead hits `kingdomHP` directly (`attackKingdom`), using the same `dmg = max(1, round(power * (1 - defense/100)))` formula against a flat `KINGDOM_DEFENSE = 15` (placeholder — could later be tied to a "Walls"-type building).
- A battle now ends when **either** the enemy squad is wiped (win) **or** `kingdomHP` reaches 0 (loss). The old "lump sum of dead heroes' maxHp at battle end" penalty has been removed entirely — all Kingdom HP loss now comes from this real-time siege.
- Regenerated continuously by **Builders** (Workshop residents), `kingdomHpRegen` HP/sec, applied once per tick alongside gold income (including mid-battle).
- If `kingdomHP` reaches 0 it clamps there and **the run ends**: `endRun('overrun')` records the fall (`kingdomFallRecord` for the HP-panel marker, plus an entry in the persistent `meta.fallHistory`), freezes the game (`tick()` no-ops while `runEnded`), and shows the run-summary overlay with the upgrade shop — see *Run loop implementation (M8)*.

### Heroes
Heroes are recruited separately from townspeople and are **not building-gated** — the squad cap is simply the 6 slots on the 2x3 battlefield grid (a future "zoom" upgrade could grow this while keeping the panel's footprint fixed).

**Hero archetypes** (`HERO_ARCHETYPES`):

| Archetype | Names by rarity (common→legendary) | Base cost | Role |
|---|---|---|---|
| guardian | Knight / Sentinel / Vanguard / Paragon | 1,000g | Tanky attacker (35 defense, 140 hp, 8 atk) |
| ranged | Archer / Sharpshooter / Hunter / Marksman | 750g | Fast attacker (5 defense, 60 hp, 18 atk) |
| mender | Acolyte / Cleric / Druid / Saint | 850g | Healer (5 defense, 55 hp, 20 heal) |

A hero costs a meaningful slice of early income (~30–60s of gold at raid-trigger time), so a full 6-slot squad is a real investment — mid-battle emergency rehires compete with everything else the gold could buy.

`generateHero` scales `attack`/`heal` power by the rarity tier's `incomeMult` and HP by `sqrt(incomeMult)` (same `rarityTiers` table used for townspeople — see *Recruit pool system*). Hero cost scales by the tier's `costMult`.

**Hero rarity bias — Keep's new role:** each Keep owned shifts the hero rarity roll up the `RARITY_WEIGHT_TABLE` as if the kingdom were that many levels higher: `getHeroRarityWeights() = RARITY_WEIGHT_TABLE[kingdomLevel + buildings.keep.count]`. Keep has no residents or slots — owning more of them is purely a hero-rarity investment.

**Hero rarity ceiling — Hall of Legends (added 2026-07-13):** the hero weights are then **clamped to the Hall of Legends rank** (Military tree, 3 ranks, 50/750/5,000 Legacy): rank 0 = Common only, then Rare / Epic / Legendary per rank (`heroRarityCap()`, filtered in `getHeroRarityWeights` — `weightedRarityRoll` renormalizes over what remains). In-run gold can never buy hero rarity past the ceiling; kingdom level and Keeps only improve the odds *under* it. This is the fix for the run-1 min/max break (see *Open questions*): sim-verified walls per ceiling — Common: Orc boss; Rare: Bandit boss/early Dark; Epic: Dark boss; Legendary: deep Dragon, final boss still closed until M10–12 content. Townsperson rarity is deliberately NOT capped (income rarity is harmless once hero power is gated). Veteran's Welcome still grants its free Rare Knight regardless of ceiling (it's Legacy-bought, which is the point).

**Hero recruit pool:** unlocks at `RAID_TRIGGER_LEVEL` (Town, level 2) — the Battle column shows "Unlocks at Town" until then. A pool of `HERO_POOL_SIZE = 3` recruits refreshes every `HERO_POOL_REFRESH_INTERVAL` (15) seconds. Hiring is manual only (no auto-recruit for heroes — placement matters) and requires gold plus an empty squad slot. Firing a hero is free.

**Squad formation:** drag-and-drop a hero portrait onto another slot to swap positions (`swapHeroes`); this works mid-battle. Row 0 = frontline (nearest the gate), row 1 = backline.

**Dismissing heroes:** clicking a hero portrait in the Defenders squad arms it (red highlight, tooltip changes to "Click again to dismiss") for `ARM_TIMEOUT_MS` (3s); a second click within that window fires the hero for free — same free-dismiss pattern as residents, with a misclick guard. **Heroes that die in battle free their squad slot at the moment of death** (`combatTick` nulls any `!alive` slot each tick), so reinforcements can be hired into the ongoing fight even after a full squad wipe. Dead heroes are gone for good; only survivors respawn at full HP for the next battle.

### Workshop & Builders
- Unlocks at Village level (one level before the first raid trigger).
- Residents are **Builders**, rolling 0.3–1.0 Kingdom-HP-regen/sec (×rarity), same hire/fire/reroll mechanic as every other townsperson.
- Builders generate no gold — each Workshop hire is an income sacrifice in exchange for surviving raids longer-term.

## Raid system redesign — autobattler (implemented)

The hero-squad-vs-enemy-squad autobattle described above replaces the old duration/ratio siege system (`totalDefense` vs. a flat `defenseRequired`, `clamp(60/ratio, 10, 180)`). The 3-column "battle at the gates" layout (Admin / Town / Battle) from `layout-prototype.html` is now the live UI in `index.html`. `autobattler-prototype.html` and `layout-prototype.html` remain as standalone references but are no longer the source of truth.

**Remaining open items:**
- Hero squad cap growth — now planned as Military-tree expansion milestones, see *Progression loop redesign*.
- See *Progression loop redesign* and *Difficulty & meta-progression design* for the raid-tier vs. hero-rarity vs. Kingdom-siege balance pass — now an M9 tuning job (the run loop and currency flow landed in M8).

## Progression loop redesign — end-to-end storyboard (core run loop implemented in M8; wave/boss structure, new content, and tuning pending M9+)

The original full-idle "always growing" framing (Adventure Capitalist/Realm Grinder style) is replaced by a death-and-rebuild loop closer to Gnorp Apologue / Wizard and Minion / Scritchy Scratchy: each run ends when the Kingdom falls, and that run's combat progress funds permanent upgrades that make the next run faster and stronger. The kingdom's economy now exists to fuel the battle, not as the end goal itself.

**Target shape: 8–10 runs ("Ages"), ~20–40 minutes each, ~5 hours total**, ending in a winnable Final Siege (see below). Numbers below are placeholders pending playtesting.

### The run loop
1. Start at Hamlet with starting gold, full Kingdom HP. **Every run starts here** — there is no persistent tier-ratchet that skips a run ahead in raid tiers.
2. Build economy, level up the kingdom, reach Town level → Goblin Raid begins.
3. Clear raid waves; defeating a tier's boss wave advances immediately to the next tier's wave 1 (Goblin Raid → Orc Warband → Bandit Horde → Dark Army → Dragon Siege). Every **newly reached** wave cleared banks currency (see below).
4. Eventually `kingdomHP` reaches 0 — the run ends ("Found a New Age" reset). Gold, buildings, residents, heroes, kingdom level, and raid tier/wave all reset to start-of-run state. (QoL: a manual "Found a New Age" button is also available once raids have begun — for when a run's frontier attempts are spent and waiting out the kingdom's actual fall would just waste time.)
5. Currency banked this run is spent on the Economy and Military upgrade trees (permanent, persists across resets).
6. Next run repeats from step 1, but upgrades mean earlier tiers clear much faster, so playtime concentrates near whatever tier is currently the frontier.

The upgrade trees **are** the ratchet — there's no separate "tier unlock" flag. A heavily-upgraded player still technically starts at Goblin Raid wave 1 each run, but blows through it in seconds.

### Wave & boss structure per raid tier
- **Implemented in M9.** Each raid tier has a fixed wave count ending in its boss: Goblin 5, Orc 8, Bandit 11, Dark 14, Dragon 17 (`waveCount` per tier — see the raid-tier table under *Invasion & combat system*).
- A **boss wave** is the tier's named boss (Goblin Warmaster, Orc Warlord, Bandit King, Lich Commander, Dragon Empress — a scaled-up brute, ×1.8 power ×4 HP) plus an honor guard of roster minions. Unique per-boss abilities are M11.
- Clearing a tier's boss wave immediately advances to the next tier's wave 1 (wave counter and streak reset — boss-kill is the only tier-advance trigger; kingdom level plays no part).
- **A wave repeats until beaten** (locked in, implemented in M8): the ladder only climbs on wins — `winInvasion` is the only place the wave advances, and it only runs when the enemy squad is wiped.
- Bosses need no special rule — like any wave they repeat until killed, and killing one is what advances the tier. They're still the natural per-run walls because their stat block spikes above the tier's normal waves.
- A wall wave resolves as an **escalating last stand**: reinforcement hires inside the one ongoing battle are the "attempts", and siege escalation guarantees the battle ends — Repelled if the wall cracks under the grind, Overrun (Age over) if it doesn't. Sim-checked with the grind model: money can push roughly one wave past a squad's honest wall, not tiers (pre-escalation, the 2026-07-17 playtest ground from the predicted Orc-boss wall all the way to Bandit w3).
- **Wave composition varies within a tier**: squads fill more of the grid as waves climb (4 units early → full grid at the boss), with varied mixes (double-brute wave, skirmisher swarm, twin-healer wave). Waves feel distinct, and AoE / target-priority tools have something to answer.

### Enemy & hero grid expansion
- The **enemy grid auto-expands** at certain tier transitions (not every tier) — e.g. Goblin Raid and Orc Warband stay 2x3, Bandit Horde jumps to 3x4. Exact placements TBD.
- The **hero grid does not auto-expand** — squad size growth is a Military-tree purchase only, with multiple expansion milestones (2x3 → 3x4 → 4x4, etc.) timed to land roughly alongside the enemy-grid jumps. This makes "I'm suddenly outnumbered, I need more squad slots" a concrete, must-buy upgrade rather than a passive bonus.

### Kingdom HP interplay — persistent siege & mid-battle reinforcement (locked in)
The flow: enemies fight the hero squad; only once every hero is dead do they damage `kingdomHP` directly; Kingdom HP reaching 0 forces the loss/restart.

**A battle is a persistent, ongoing siege — it does not end when the hero squad wipes.** The recovery mechanism is **hiring heroes mid-battle**: the hero recruit pool keeps refreshing on its normal timer during combat, so a player whose squad goes down can hire reinforcements into the ongoing fight. New hires join immediately, enemies switch back from the kingdom to targeting them, and the Kingdom HP drained during the undefended gap is the attrition cost of the wipe. Gold, pool RNG, and the refresh timer are what you're scrambling against while the kingdom bleeds.

Consequences of this design:
- A raid has exactly **two outcomes**: **Repelled** (enemy squad wiped — possibly after several mid-battle squad rebuilds) or **Overrun** (`kingdomHP` hits 0 → the run ends). The old "Survived" outcome is retired.
- **No stalemate soft-lock — enforced by siege escalation** (the original "if Builder regen can't hold the line, the kingdom falls" assumption was falsified by the 2026-07-17 playtest: every wave's roster includes a healer, and at a wall the enemy healer out-healed the reinforcement trickle's chip damage while cheap rehires + Builder regen kept the Kingdom topped up — one endless battle with no exit but the manual reset button). Escalation (see *Combat*) breaks the lock structurally: a dragging siege ramps enemy attack until it either gets repelled or overruns the Kingdom. Income still flows mid-battle at the full rate, so reinforcement remains the recovery mechanism — it just can't sustain a forever-war anymore.
- Gold reserves effectively act as extra lives (feeding replacements into a wall wave). Likely self-balancing — cheap commons die near-instantly to deep-tier enemies and hero costs scale with rarity — but watch it in playtests.

Implementation state: fully working as of M8 — `hireHero` isn't gated on battle, `generateHero` initializes action cooldowns so `combatTick` picks new units up immediately, `heroPoolTimer` runs during combat, and dead heroes free their squad slot at the moment of death (browser-verified: a reinforcement was hired into a freed slot mid-battle after a wipe).

### Difficulty arc across runs — the tuning contract
When tuning any number, tune *toward this table*, not toward abstract fairness. Each run's tree purchases should buy roughly +50–70% effective squad power, worth ~5–6 waves of extra depth:

| Run | Expected wall (where the Kingdom falls) | Notable new purchases after |
|---|---|---|
| 1 | Goblin wave 4–5 (the boss) | Starting gold, hero power I |
| 2 | Orc wave 3–5 | **Paladin unlock**, cheaper heroes |
| 3 | Orc boss (w8) / Bandit w1–2 | **Assassin unlock**, first squad expansion |
| 4 | Bandit wave 6–8 | **Smithy doctrine**, Kingdom HP+ |
| 5 | Bandit boss (w11) / Dark w1–3 | **Battlemage (AoE)**, start at Village |
| 6 | Dark wave 7–10 | **Banneret (buffer)**, second squad expansion |
| 7 | Dark boss (w14) / Dragon w2–4 | **Cathedral doctrine (revive)**, hero power III |
| 8 | Dragon wave 9–13 | Remaining doctrines, Frost Adept |
| 9 | Dragon boss (w17) → first Final Siege attempt (expected loss) | Last power ranks |
| 10 | **Final Siege — victory** | — |

### Scaling & tuning targets — implemented in M9
- **Continuous curve across tier transitions** (implemented): each tier's `powerMult` = the previous tier's boss-wave multiplier (1.0 / 1.52 / 3.0 / 7.6 / 24.7), `defenseGrowth = 1.088`/wave everywhere. The final boss lands at ~95× goblin wave 1 (target was 80–100×), with the boss unit's own ×1.8/×4 on top. No stat cliffs — the old Dragon-wave-7 spike class of problem is gone by construction.
- Raid pacing (implemented): per-tier `raidInterval` — 45s at Goblin/Orc tightening to 30s at Dragon — plus a 75s grace before the first raid ever.
- Sim-measured expectations at these numbers (`tools/balance-sim.js`): optimal greedy run 1 ≈ 24 min, wall at Orc boss (a realistic first run fields fewer heroes and walls at the Goblin boss / early Orc); 6 rares + tree ×1.2 wall at Bandit boss; 6 epics ×1.6 at Dark boss; 6 legendaries ×2.0 reach Dragon wave 9+ but score ~0% on the final boss — that last stretch is deliberately closed until M10–12 content (squad expansion, new archetypes) opens it.

### Victory condition — the Final Siege (locked in)
After the Dragon Siege boss (wave 17) falls, a herald announces the **Final Siege** arrives in 3 raids' time — a countdown the player preps through. Then a **3-phase gauntlet**: vanguard squad → elite squad → a phase-changing final boss with guards. Heroes do **not** reset to full HP between phases (menders and the Cathedral revive get their showcase), and Kingdom HP is the buffer that can carry a partial wipe across phases.
- **Loss**: counts as a Kingdom fall, but grants a large one-time "Lessons of the Last Siege" currency bonus so the failed attempt visibly funds the winning one.
- **Win**: victory screen with the campaign's stats — Ages founded, total time, where each Age fell (`kingdomFallRecord` already tracks fall points).

### Endless mode (locked in)
After victory the player may keep playing the current run (or start fresh runs) with raids scaling indefinitely — number-chasing for those who want it, clearly framed as post-game. The completion flag persists.

### Currency (name TBD; shown in-game as "Legacy")
- **First-ever-clear credit (locked in, implemented):** each wave on each tier's ladder pays out full value the first time it is cleared *across the whole campaign* — `meta.waveCredit[tierIndex]` is the per-tier "waves credited" high-water mark, persisted with meta state (`bankWaveLegacy` in `game.js`). Pushing past the all-time frontier is the primary way to earn meta currency.
- **Repeat-clear trickle (locked in, implemented):** re-clearing an already-credited wave pays `REPEAT_LEGACY_FRACTION = 0.15` of its first-clear value (min 1) so no run banks literally zero. Restart-farming stays pointless — the trickle on cheap early waves is negligible next to frontier pushes at 5x/tier values.
- Per-wave value scales **5x per raid tier**: `WAVE_LEGACY_VALUES = [10, 50, 250, 1250, 6250]` (Goblin → Dragon, flat within a tier for now). Boss waves pay **×4** (`BOSS_LEGACY_MULT`) as the "breakthrough" bonus (implemented in M9). First-clear campaign total ≈ 150k Legacy; the current 9-node tree costs ~19k, leaving deliberate headroom for the big-ticket M10–12 nodes (squad expansions, archetype unlocks, doctrines).
- Legacy is banked **at wave-clear time** (not at run end), so a mid-run quit or crash loses nothing.
- Currency persists across resets and is spent on the two upgrade trees below. The old gold-`goldEarned`-based formula (`floor(sqrt(goldEarned/100000))`) and the automatic "+5% income / +5% hero power per point" effect are both superseded by this.
- Possible future Economy-tree QoL: a "start at wave N" skip upgrade to shorten the retread on later runs (open to it, not yet designed).
- **Pricing philosophy:** total tree cost ≈ slightly under expected lifetime earnings across the 8–10 run arc, with the Final Siege realistically beatable at ~⅔ of the trees purchased — full completion is for thoroughness, not a requirement.

### Upgrade trees (Economy / Military)
Two permanent, currency-funded trees spent into after each reset. Full planned scope:

- **Economy tree** — income multipliers (global or per-building), starting gold, "Old Foundations" (start runs at Village level), building cost-growth reduction, building cap increases beyond kingdom-level grants, Builder Kingdom-HP-regen multiplier, recruit-pool quality-of-life (refresh speed, rarity weights, pool size, reroll button), **townsperson auto-buy** (decided 2026-07-13: the current auto-recruit toggle becomes a purchasable Economy node — "QoL as upgrades", the incremental-genre pattern of an interactive mechanic earning its own automation; it stays always-available in the dev build for testing), **Doctrines** (below).
- **Military tree** — **Hall of Legends** (the hero rarity ceiling — implemented, see *Hero rarity ceiling* under *Heroes*), hero stat multipliers (HP/attack/defense/heal, ranked, global or per-archetype), **hero squad-size expansion milestones** (the must-buy nodes tied to enemy-grid jumps), **new hero archetype unlocks** (below), "Veteran's Welcome" (start each run with a free rare Knight), cheaper hero hires, hero recruit-pool quality-of-life, Kingdom HP max / Kingdom defense ("Walls") / base HP regen, a scout report (see the next raid's composition).

**M8 starter set (implemented, `UPGRADE_TREES` in `game.js` — all numbers placeholder pending M9):**

| Tree | Node | Effect per rank | Ranks | Costs (Legacy, rescaled in M9) |
|---|---|---|---|---|
| Military | Hall of Legends | unlocks Rare / Epic / Legendary heroes in the pool (the run-depth gate — see *Hero rarity ceiling*) | 3 | 50 / 750 / 5,000 |
| Economy | Prosperous Trade | +25% gold income | 5 | 15 / 60 / 250 / 1,000 / 4,000 |
| Economy | Royal Treasury | starting gold 50 → 250 / 1,000 / 4,000 / 15,000 | 4 | 10 / 40 / 150 / 500 |
| Economy | Master Builders | +50% Builder HP regen | 3 | 25 / 100 / 400 |
| Economy | Old Foundations | new Ages begin at Village | 1 | 400 |
| Military | Weapon Drills | +20% hero attack & healing | 5 | 15 / 60 / 250 / 1,000 / 4,000 |
| Military | Hardened Armor | +20% hero HP | 5 | 15 / 60 / 250 / 1,000 / 4,000 |
| Military | Muster Rolls | hero hiring −15% (multiplicative) | 3 | 20 / 80 / 300 |
| Military | Reinforced Walls | +250 max Kingdom HP | 4 | 15 / 60 / 250 / 1,000 |
| Military | Veteran's Welcome | free Rare Knight each new Age | 1 | 100 |

Effects route through helper functions (`econIncomeMult`, `heroPowerMult`, `getKingdomHpMax`, etc.) so later nodes slot in without special-casing. Squad expansion, archetype unlocks, doctrines, and pool QoL arrive in M10–M12.

### Doctrines — building↔army synergy nodes (Economy tree)
Each doctrine makes a building type directly feed the army, so town composition stays a battle decision all game and the Economy tree keeps late-game relevance. Keep's existing hero-rarity bias is the template for this family:
- **Smithy Forgework** — +1.5% hero attack per Smithy owned
- **Library Tactics** — +1% hero action speed per Library owned
- **Apothecary Salves** — heroes slowly regenerate HP mid-battle
- **Cathedral Blessing** — the first hero to fall each battle revives at 30% HP (requires a Cathedral)

### New hero archetypes (Military-tree unlocks, ~one per run for novelty)
Sequenced so the zero-engine-work heroes arrive first:

| Hero | Role | Engine work needed |
|---|---|---|
| Paladin | attack + heal hybrid | **none** — the multi-action system already supports it |
| Assassin | backlineChance ~0.9, high power, fragile | none — just stats |
| Battlemage | hits an entire enemy row | AoE action type |
| Banneret | aura: adjacent allies gain power | buff system |
| Frost Adept | attacks slow the target's cooldowns | debuff-on-hit |

### Enemy tier mechanics (one tactical lesson per tier)
Later tiers must be new problems, not just bigger numbers — each reuses an engine feature from the hero list:
- **Goblins** — vanilla; teaches the basics.
- **Orcs** — brutes *enrage* below 50% HP (+attack speed); teaches burst-vs-tank priority.
- **Bandits** — marksmen hunt the backline (high `backlineChance`); medics out-heal unfocused damage. Teaches protecting menders and the Assassin's job.
- **Dark Army** — necromancers revive a fallen ally once (on-death hook); teaches kill order.
- **Dragons** — breath attacks hit a whole row (AoE); teaches formation splitting.
- **Bosses** — unique named unit + minions per tier (`BOSS_ARCHETYPES`-style table extending `generateEnemy`); the Final Siege boss adds phases.
- **Sappers — kingdom/villager targeting (folded into M11 on 2026-07-17):** a sapper-style enemy unit that attacks the Kingdom (and possibly residents) *while heroes still stand*, instead of fighting the squad. Purpose: gives Builders a live role in every fight and keeps town management ongoing rather than "staff it and forget it" (no longer needed for anti-stall — siege escalation covers that). Working assumptions, final call at implementation: residents are **injured** (income paused until they recover), never killed — losing a legendary roll permanently would be brutal; sappers likely debut with the **Bandit Horde** (pillaging fits the fiction, and it stacks with their protect-the-backline lesson) and recur in later tiers' compositions. Engine cost is small: `attackKingdom` already exists — a sapper is an archetype whose attack routes there (plus the resident-injury system if residents are targetable).

### Gold & loot rebalance (single-currency decision, locked in)
The in-run economy stays **gold-only** — no separate combat currency for hero hiring. For that to work, **raid gold loot must shrink drastically**: current values (200,000g for a goblin raid vs. a 2,500g Smithy) let one raid win pay for the entire midgame, collapsing the "town fuels the army" loop into "raids fund everything". Target: a raid win pays roughly **1–2 minutes of contemporaneous resident income**. The win-streak multiplier stays, on the much smaller base.

### Open questions
- [x] **Run-1 min/max break (found in the 2026-07-13 playtest — FIXED same day):** a player who
  min/maxed in-run resources cleared the entire 38-wave ladder in Age 1 with **zero Legacy upgrades**
  (fell only at Dragon Siege, Realm level; conditions: mostly 10× dev speed, dev auto-buy at
  rare+/epic+). Root cause: hero rarity — worth ~1.5 raid tiers per step, ~4.5 tiers
  common→legendary — was gated only by kingdom level + Keeps, i.e. by gold, and **stalling is free**
  (waves repeat until beaten, income never throttles, Builders out-regen wall-attempt attrition), so
  patient play bought Empire + Keeps and fielded 6 legendaries within run 1 (sim: 6 no-tree
  legendaries beat the Dark boss ~45%/attempt). The trees (×1.2–2.0) were dwarfed by in-run rarity
  (×10). **Fix implemented: the Hall of Legends hero rarity ceiling** (see *Heroes*) — epic/legendary
  hero access is now a Military-tree meta-unlock. The complementary "make stalling itself cost
  something" lever landed in M9.6 as **siege escalation** (the 2026-07-17 playtest showed in-battle
  stalling was still free — see *Kingdom HP interplay*); sapper-type enemies remain a possible M11
  flavor mechanic but are no longer load-bearing for anti-stall.
- [ ] Exact numbers throughout — wave counts, per-tier currency multiplier, boss bonus, `defenseGrowth`, loot values, Legacy wave values, upgrade costs — all placeholder until the M9/M14 playtests against the *Difficulty arc across runs* table.
- [ ] Exact tier transitions where the enemy grid expands, and where the matching hero squad-expansion milestones sit in the Military tree.
- [ ] Boss unit stat blocks and any per-boss unique abilities beyond the tier gimmick.
- [x] UI for the run-end/reset summary screen and the two upgrade trees — implemented in M8 as a full-screen overlay (see *Run loop implementation (M8)*).

### Ideas under consideration (raised 2026-07-13)
- **The kingdom & villagers as rare combat targets — SCHEDULED into M11 (2026-07-17):** now a
  planned sapper enemy mechanic; details and working assumptions live under *Enemy tier mechanics*.
  (Its original anti-stalling role is obsolete — siege escalation covers that; it survives on the
  town-engagement rationale alone.)
- **Per-building interactive minigames that automate later:** the classic incremental arc — each
  building has a small active mechanic (e.g. assemble horseshoes at the Smithy for a productivity
  boost) that an upgrade later automates at equal-or-better efficiency. (The auto-buy Economy node
  above is the first, already-decided instance of this "QoL as upgrades" pattern.) Risk: splits focus from the
  battle at the gates, and is a large content lift (one designed minigame per building) — if pursued,
  likely post-M14 scope, possibly starting with a single building as a pilot.

## Difficulty & meta-progression design — to-do

Playtesting at 100x surfaced a hard difficulty wall: an all-legendary hero squad was wiped and the Kingdom (1000 HP) was drained in ~5 seconds around Dragon Siege Wave 7 (`kingdomFallRecord` tracks the latest failure point for this kind of test). The *Progression loop redesign* section above now answers most of the structural questions this raised; remaining items are tuning/implementation details within that structure:

- [x] **What does the difficulty curve represent?** Decided: within a single run, the curve is *meant* to eventually become unwinnable — that's what triggers the reset (see *Progression loop redesign*). Across runs, the Economy/Military trees push that ceiling further out, so progress is measured run-over-run, not within one run.
- [x] **What triggers the first forced reset?** `kingdomHP` reaching 0 — wired up in M8: `tick()` short-circuits into `endRun('overrun')`, which freezes the game and opens the run-summary/upgrade-shop overlay. See *Run loop implementation (M8)*.
- [x] **Re-tune the raid-tier curve** — done in M9 via `tools/balance-sim.js` (continuous 1.088/wave growth, no tier cliffs, final boss ≈ 95× goblin wave 1, economy shrink, loot cut). `KINGDOM_DEFENSE`/`KINGDOM_HP_MAX`/Builder regen kept as-is for now; final calibration against real playtests is M14.
- [x] **Design meta-progression between resets** — see *Progression loop redesign*: currency earned from in-run wave/boss progress, spent on Economy and Military trees.
- [x] **What does completing the game look like?** Decided: the **Final Siege** 3-phase gauntlet after the Dragon Siege boss is the victory condition; endless mode unlocks after victory. See *Progression loop redesign*.
- [ ] **Hero permadeath economics:** dead heroes are auto-fired (gone for good, see *Heroes & combat*); rebuilding the squad after a rough raid costs real gold/time within a run. Does this need its own lever (cheaper recruits at low kingdom levels, a "veteran" bonus, etc.), or does the run-restart-from-Hamlet structure make this moot since squads rebuild from scratch each run anyway?

## Run loop implementation (M8)

How the death-and-rebuild loop from *Progression loop redesign* is wired in `game.js`:

- **Two-key save model:** run state stays in `idleKingdomSave`; everything that survives a reset lives in `meta` (localStorage key `idleKingdomMeta`, `META_SAVE_KEY`): `age` counter, `legacy` balance, `waveCredit` high-water marks, `upgrades` ranks, and `fallHistory` (one entry per ended Age: age, fall wave, kingdom level, waves cleared, Legacy earned). The dev "Reset game" button wipes **both** keys — it's the full debug wipe, distinct from the in-fiction Age reset.
- **Save versioning (M9):** both saves carry `version: SAVE_VERSION`; a mismatch on load discards the save (fresh start). Bump `SAVE_VERSION` whenever a rebalance makes old saves meaningless.
- **Run end:** `endRun(reason)` — `'overrun'` from `tick()` when `kingdomHP` hits 0 mid-battle, `'abandoned'` from the manual left-panel "Found a New Age" button (visible once raids have begun, two-click confirm). Either way: fall recorded, `runEnded = true` (the whole game freezes — `tick()` no-ops), and the full-screen run-summary overlay opens showing Age number, fall point, waves repelled, Legacy earned/available, both upgrade trees with Buy buttons, and the "Found a New Age" button. Closing the browser mid-summary is safe: `runEnded`/`runSummary` are saved, so the overlay reopens on load.
- **The reset:** `foundNewAge()` increments `meta.age` and rebuilds run state: gold = `getStartingGold()` (Royal Treasury), kingdom level = Hamlet (or Village with Old Foundations), Kingdom HP = `getKingdomHpMax()` (Reinforced Walls), buildings back to zero at base costs (`BUILDING_BASE_COSTS`), residents/heroes/pools cleared, raid tier/wave/streak zeroed, free Rare Knight placed if Veteran's Welcome is owned. Upgrades are bought *on* the summary screen, so purchases there apply to the very next Age.
- **What resets:** gold, `goldEarned`, buildings, residents, heroes, kingdom level, raid tier/wave/streak, Kingdom HP.
- **What persists:** Legacy, tree purchases, `waveCredit`, `fallHistory`, auto-recruit setting, dev speed (also survives reload now), and later the completion flag / endless-mode unlock (M13).
- The **Legacy balance** shows as a third resource line in the admin panel; the left panel shows "Kingdom · Age N".

(The original prestige design — Legacy Points from lifetime `goldEarned`, manual prestige at Realm level, automatic +5%/point bonuses — is fully superseded by the above.)

## Game feel pass — visuals & sound (M15)

**Rationale (added 2026-07-17):** M14 ends with a working gameplay arc and tuned mechanics — but
that's a working *simulation*, not a working *game*. The incremental/autobattler genre lives on
feedback: the game isn't done until it feels good to play. M15 is the dedicated juice pass.

**Guiding principle:** every player action and every important game event gets an immediate,
legible, satisfying response. Juice is information delivery, not decoration — a hit you can see
and hear is a hit the player understands.

This is a first-pass scope sketch; detailed design happens when M14 wraps. Constraints that hold
regardless: plain HTML/CSS/JS with no build step (per the tech-stack decision), any assets
committed to the repo, and everything must stay smooth at 100× dev speed (throttle/batch effects —
a 100× battle must not fire 100× the particles and sounds).

### Visuals (candidate scope)
- **Combat juice:** floating damage/heal numbers, hit-flash on the struck unit, attack
  lunge/recoil, death collapse/fade, heal glow. Escalation should *read* — the battle visibly
  intensifies as the multiplier climbs (e.g. deepening tint on the enemy side).
- **Kingdom stakes:** vignette/shake pulse when the Kingdom itself takes a hit; HP-bar damage
  trail (ghost bar); the siege banner intensifying with escalation.
- **Town feedback:** gold counter tick, "+N g/s" floater on hire, purchase flash, a real
  level-up fanfare moment, recruit-pool refresh animation.
- **Run drama:** Kingdom-fall transition into the run summary (the fall should land emotionally);
  "Found a New Age" dawn transition; Legacy pop at wave clear.
- **Portrait/sprite pass:** the letter-portraits get real pixel art (or a polished CSS take) —
  the biggest pure-asset lift; scope decided at milestone start.

### Sound (candidate scope)
- **Web Audio API** — fits the no-build-step stack. Either tiny committed audio files or
  procedurally synthesized chiptune-style SFX (zero asset files); decide at milestone start.
- **Event coverage:** hits (light/heavy differentiated), unit death, heal, hero hire, building
  buy, kingdom level-up, raid horn on arrival, an escalation heartbeat/drum that builds with the
  multiplier, Repelled sting, Kingdom-fall sting, upgrade purchase, Final Siege victory fanfare.
- **Discipline:** per-tick sound budget (throttled hard at dev speeds), master mute + volume
  persisted in the save, and no audio before first user interaction (browser autoplay policy).
- **Music:** stretch goal — one ambient town loop + one battle loop; decide at milestone start.

### Feel-adjacent QoL
- Reduced-motion / no-shake toggle alongside the volume controls.

## Milestone tracker
- [x] Milestone 1: Gold counter ticking automatically
- [x] Milestone 2: Cottage building — buy to earn gold/sec
- [x] Milestone 3: Residents with random rolls, hire/fire system
- [x] Milestone 4: Multiple building types with different residents; dynamic rendering
- [x] Milestone 5: Kingdom level system — building caps + unlock gates unified
- [x] Milestone 6: Workshop + defense meter + invasion system
- [x] Milestone 7: Autobattler combat — hero squad vs. enemy squad, Kingdom HP, Keep/Workshop repurposed (hero rarity bias / Builders), 3-column "battle at the gates" layout
- [x] Milestone 8: **The run loop** — `kingdomHP` 0 → run-summary screen → currency banking (first-ever-clear credit via per-tier high-water mark) → upgrade-tree shop → reset to Hamlet; meta-state persistence; manual "Found a New Age" button; battle-end fix (waves repeat on loss — `tierWave++` is win-only); dead heroes free their squad slot at the moment of death so mid-battle reinforcement works after a full wipe. See *Run loop implementation (M8)*.
- [x] Milestone 9: **Economy & pacing pass** — loot cut (~170×), per-tier raid intervals + first-raid grace, per-tier wave counts + boss waves, tier advance by boss-kill, continuous 1.088/wave enemy curve, economy shrink (caps/slots/costs/incomes way down), rarity-weight gating, Legacy boss bonus + upgrade-cost rescale, save versioning; wall targets sim-verified via `tools/balance-sim.js` (real-1× confirmation happens in play)
- [x] Milestone 9.5: **Hero rarity ceiling (Hall of Legends)** — fix for the run-1 min/max break found in the first M9 playtest (full ladder cleared with zero upgrades): hero rarity above Common is now a 3-rank Military-tree unlock (50/750/5,000 Legacy); sim-verified per-ceiling walls land on the difficulty arc; SAVE_VERSION → 3 (old saves discarded); browser smoke-tested (pool filtering, node purchase)
- [x] Milestone 9.6: **Siege escalation** — anti-stalemate fix from the 2026-07-17 1× playtest (run 1 hit a true soft-lock at Bandit w3: enemy Medic out-healed reinforcement chip damage while rehires + Builder regen kept the Kingdom maxed — one endless battle, ~2 runs deeper than the arc target, 1,130 Legacy banked): past a 60s per-battle grace, enemy attack ramps +1%/s until the siege resolves; healer top-off on win (survivors leave the field at full HP); sim gained escalation, win-duration stats, and the reinforcement-grind model; SAVE_VERSION → 4 (old saves + broken-run Legacy discarded); browser smoke-tested (banner, overrun path, top-off, win path)
- [ ] Milestone 10: **First new heroes** — Paladin + Assassin unlocks and the first squad-expansion milestone (no engine work needed)
- [ ] Milestone 11: **Combat engine features** — AoE actions, buffs/debuffs, on-death hooks; enemy tier mechanics, boss units, wave composition variety, enemy grid expansion; **kingdom/villager targeting** (scheduled 2026-07-17: sapper-style enemies that hit the Kingdom — and possibly injure residents — while heroes still stand; see *Enemy tier mechanics*)
- [ ] Milestone 12: **Doctrines** — building↔army synergy nodes
- [ ] Milestone 13: **Final Siege** — 3-phase gauntlet, victory screen, endless mode
- [ ] Milestone 14: **Full-game balance playtest** against the *Difficulty arc across runs* table
- [ ] Milestone 15: **Game feel — visuals & sound** — the juice pass that turns the mechanically-complete game (M14) into one that feels good to play: combat/UI feedback animations, floating numbers, kingdom-damage and run-transition drama, portrait/sprite art pass; Web Audio SFX (hits, hires, raid horn, escalation heartbeat, stingers) with mute/volume; reduced-motion toggle. Scope sketch in *Game feel pass — visuals & sound (M15)*

## Starting state
- Player begins with 50 gold (enough to buy first Cottage at 10g + hire first Villager at 25g); Royal Treasury ranks raise this for later Ages
- No base income — gold only accrues from hired residents
- Kingdom HP starts full (base `KINGDOM_HP_MAX` = 1000, +250 per Reinforced Walls rank)
