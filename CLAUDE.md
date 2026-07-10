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

Rarity weights improve with kingdom level. Legendary only available at City+ level.

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
- **Battles are persistent sieges** — no end on squad wipe; hero hiring stays available mid-battle (pool keeps refreshing), and Kingdom HP soaks damage while no hero stands. Raids end only Repelled or Overrun (Kingdom HP 0 → forced restart)
- RPG/dungeon elements are a possible future addition

## Current building roster

| Building | Cost | Slots | Resident | Hire cost | Income roll |
|---|---|---|---|---|---|
| Cottage | 10g (scales) | 3 | Villager | 25g | 1–5 g/s |
| Tavern | 300g (scales) | 4 | Tavernkeeper | 120g | 5–12 g/s |
| Smithy | 2500g (scales) | 3 | Blacksmith | 700g | 15–40 g/s |
| Library | 15000g (scales) | 5 | Scholar | 3500g | 50–130 g/s |
| Workshop | 400g (scales) | 4 | Builder | 200g | 0.3–1.0 hp/s |
| Keep | 500,000g (scales) | 0 | — | — | — (each Keep owned biases hero recruit rarity, see below) |
| Apothecary | 80,000g (scales) | 8 | Alchemist | 25,000g | 190–440 g/s |
| Wizard's Tower | 600,000g (scales) | 10 | Mage | 150,000g | 650–1,450 g/s |
| Cathedral | 5,000,000g (scales) | 14 | High Priest | 1,000,000g | 2,050–5,150 g/s |

Income rolls are then multiplied by the recruit's rarity tier (see *Recruit pool system*). All numbers are tunable — balance pass pending.

## Kingdom level system
The player's kingdom has a level (Hamlet → Village → Town → City → Kingdom) that acts as the unified progression gate. Leveling up costs gold and does two things simultaneously:
1. Raises the cap on how many of each building you can own
2. Unlocks new building types

This replaces a separate "unlock threshold" system — kingdom level IS the unlock gate.

Level-up is manual (spend gold via a button), not automatic.

| Level | Name | Cost | Cottage | Tavern | Smithy | Library | Workshop | Keep | Apothecary | Tower | Cathedral | Unlocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Hamlet | — | 10 | — | — | — | — | — | — | — | — | Cottage |
| 1 | Village | 500g | 25 | 8 | — | — | 1 | — | — | — | — | Tavern, Workshop |
| 2 | Town | 5,000g | 50 | 20 | 8 | — | 5 | — | — | — | — | Smithy |
| 3 | City | 35,000g | 75 | 35 | 20 | 8 | 8 | — | — | — | — | Library |
| 4 | Kingdom | 200,000g | 100 | 60 | 35 | 20 | 12 | — | — | — | — | — |
| 5 | Empire | 1,000,000g | 150 | 90 | 55 | 30 | 18 | 3 | 8 | — | — | Apothecary, Keep |
| 6 | Dynasty | 8,000,000g | 200 | 120 | 75 | 50 | 25 | 6 | 15 | 6 | — | Wizard's Tower |
| 7 | Realm | 60,000,000g | 250 | 160 | 100 | 70 | 35 | 10 | 25 | 12 | 5 | Cathedral |

Locked buildings show in the UI with a hint ("Unlocks at Village") so the player can see what they're working toward.

All numbers are tunable.

## Invasion & combat system

**Trigger:** Town level (2) + 12,000 total gold *earned* (`goldEarned`, a counter that only goes up, separate from current gold — spending down can't delay an invasion). After the first raid, they repeat indefinitely (`RAID_TRIGGER_LEVEL = 2`, `RAID_TRIGGER_GOLD = 12000`).

**No income penalty during battles.** (Removed 2026-07-10: the old "income drops to 25% during a siege" rule was a soft-cap stakes mechanism from the infinite-idle era. With a real loss condition and mid-battle reinforcement hiring, it's obsolete — and it would throttle income at exactly the moment the player needs gold for reinforcements. The small "(siege)" tag next to gold/sec remains as flavor only.)

**Invasion schedule:** Once triggered, a new raid starts every `RAID_INTERVAL` (20 seconds) of non-battle time. The raid status bar (right column) shows "Next: <raid name> · Arrives in M:SS" while waiting.

### Raid tiers
Instead of one global ever-climbing wave counter, each kingdom level from Town onward has its own raid family (`RAID_TIERS` in `game.js`) with its own enemy roster, power curve, and wave counter that **resets when you advance to the next tier**:

| Kingdom level | Raid name | `powerMult` | `defenseGrowth`/wave | Roster (brute / skirmisher / caster / shaman) |
|---|---|---|---|---|
| Town (2) | Goblin Raid | 1.0 | 1.15 | Goblin Brute / Skulker / Slinger / Shaman |
| City (3) | Orc Warband | 1.6 | 1.15 | Orc Brute / Berserker / Warcaster / Witch Doctor |
| Kingdom (4) | Bandit Horde | 2.4 | 1.15 | Bandit Enforcer / Cutthroat / Marksman / Medic |
| Empire (5) | Dark Army | 3.6 | 1.15 | Death Knight / Shadow Reaver / Necromancer / Bone Priest |
| Dynasty/Realm (6+) | Dragon Siege | 5.5 | 1.15 | Dragon Guard / Wyrmling / Dragon Mage / Dragonpriest |

Since there's no raid type defined past Dragon Siege (`minLevel: 6`) and Realm is level 7, both tiers share Dragon Siege — the wave count and win streak carry through that transition without resetting (the lookup naturally "saturates" at the last defined tier).

**Wave naming:** first raid of a tier shows as just the tier name (e.g. "Goblin Raid"); subsequent waves show as "Goblin Raid (Wave 2)", etc.

### Combat
Each raid spawns a 2x3 enemy squad (brute + skirmisher front, caster + shaman back, two empty slots) that fights the player's hero squad in the same 2x3 grid layout. Combat runs automatically, advancing by one game-second per `tick()` (so dev-speed multipliers speed up battles too):

- Each unit has independent `attack` and/or `heal` **actions**, each with its own `power`, `speed`, and cooldown (`cooldown = BASE_ATTACK_INTERVAL / speed`, `BASE_ATTACK_INTERVAL = 2500ms`). This lets future hybrid units (e.g. a Paladin) attack and heal on staggered timers without special-casing.
- **Targeting** is weighted, not absolute: an attacker rolls its own `backlineChance` (`DEFAULT_BACKLINE_CHANCE = 0.15`, skirmishers are 0.4) to decide whether it goes after the front row or back row, then picks randomly within that row.
- **Healers** (shamans, menders) always target the lowest-HP% wounded ally on their side; if nobody's wounded the heal is held for next tick.
- Damage: `dmg = max(1, round(attackPower * (1 - defense / 100)))`.
- A battle ends when one side has no `alive` units left (`squadAlive`). Win = enemy squad wiped; loss = hero squad wiped.

**Enemy scaling:** `generateEnemy` scales each archetype's base stats (`ENEMY_ARCHETYPES`) by `mult = tier.powerMult * tier.defenseGrowth^wave` for power stats, and `sqrt(mult)` for HP.

**Loot — win-streak combo system:** each raid tier tracks a win streak:
- **Win**: payout = `baseLoot × lootGrowth^streak`, then the streak increments — chaining repels compounds the reward.
- **Loss**: payout = a flat `baseLoot × 0.5` consolation amount, and the streak resets to zero.

Per-tier loot values (`baseLoot` / `lootGrowth`): Goblin Raid 200,000 / 1.30, Orc Warband 1,000,000 / 1.30, Bandit Horde 5,000,000 / 1.32, Dark Army 25,000,000 / 1.34, Dragon Siege 120,000,000 / 1.36. Loot does not count toward `goldEarned` (avoids immediately re-triggering the raid-trigger check). Switching raid tiers resets the streak too.

**Result display:** the raid status bar shows "Repelled: <name> +Xg" (win), "Survived: <name> +Xg" (loss with the Kingdom still standing), or "Overrun: <name> +Xg" (loss where Kingdom HP hit 0) for the most recent battle (`lastVictory`). While the hero squad is wiped but the battle continues, a pulsing "The Kingdom is under siege!" banner appears in the status bar.

### Kingdom HP
Kingdom HP (`kingdomHP`, max `KINGDOM_HP_MAX = 1000`) is the persistent consequence of losing the hero squad in battle:

- **Heroes "respawn" at full HP at the start of every battle** (`startInvasion` resets `hp = maxHp, alive = true` for the whole squad) — survivors start each battle healed up.
- **The Kingdom is the last line of defense.** While any hero is alive, enemies target the hero squad as normal (`pickTarget`). Once the hero squad is wiped, every surviving enemy attack instead hits `kingdomHP` directly (`attackKingdom`), using the same `dmg = max(1, round(power * (1 - defense/100)))` formula against a flat `KINGDOM_DEFENSE = 15` (placeholder — could later be tied to a "Walls"-type building).
- A battle now ends when **either** the enemy squad is wiped (win) **or** `kingdomHP` reaches 0 (loss). The old "lump sum of dead heroes' maxHp at battle end" penalty has been removed entirely — all Kingdom HP loss now comes from this real-time siege.
- Regenerated continuously by **Builders** (Workshop residents), `kingdomHpRegen` HP/sec, applied once per tick alongside gold income (including mid-battle).
- If `kingdomHP` reaches 0 it clamps there, the raid ends as an "Overrun" loss, and the left panel shows a "Kingdom Falling!" warning plus a persistent "Fell at: <raid name> (Kingdom Lv N)" marker (`kingdomFallRecord`, saved with the rest of the game state) for tracking failure points across a playtest run. **`kingdomHP` reaching 0 is meant to be the forced reset trigger** (see *Difficulty & meta-progression design*) — there's no real "next battle" to recover into at that point. Currently nothing beyond the warning/marker happens yet, so play continues as if it were a normal loss; this is a placeholder until the reset/Legacy Points flow is wired up (see *Prestige system*).

### Heroes
Heroes are recruited separately from townspeople and are **not building-gated** — the squad cap is simply the 6 slots on the 2x3 battlefield grid (a future "zoom" upgrade could grow this while keeping the panel's footprint fixed).

**Hero archetypes** (`HERO_ARCHETYPES`):

| Archetype | Names by rarity (common→legendary) | Base cost | Role |
|---|---|---|---|
| guardian | Knight / Sentinel / Vanguard / Paragon | 1,000g | Tanky attacker (35 defense, 140 hp, 8 atk) |
| ranged | Archer / Sharpshooter / Hunter / Marksman | 800g | Fast attacker (5 defense, 60 hp, 18 atk) |
| mender | Acolyte / Cleric / Druid / Saint | 900g | Healer (5 defense, 55 hp, 20 heal) |

`generateHero` scales `attack`/`heal` power by the rarity tier's `incomeMult` and HP by `sqrt(incomeMult)` (same `rarityTiers` table used for townspeople — see *Recruit pool system*). Hero cost scales by the tier's `costMult`.

**Hero rarity bias — Keep's new role:** each Keep owned shifts the hero rarity roll up the `RARITY_WEIGHT_TABLE` as if the kingdom were that many levels higher: `getHeroRarityWeights() = RARITY_WEIGHT_TABLE[kingdomLevel + buildings.keep.count]`. Keep has no residents or slots — owning more of them is purely a hero-rarity investment.

**Hero recruit pool:** unlocks at `RAID_TRIGGER_LEVEL` (Town, level 2) — the Battle column shows "Unlocks at Town" until then. A pool of `HERO_POOL_SIZE = 3` recruits refreshes every `HERO_POOL_REFRESH_INTERVAL` (15) seconds. Hiring is manual only (no auto-recruit for heroes — placement matters) and requires gold plus an empty squad slot. Firing a hero is free.

**Squad formation:** drag-and-drop a hero portrait onto another slot to swap positions (`swapHeroes`); this works mid-battle. Row 0 = frontline (nearest the gate), row 1 = backline.

**Dismissing heroes:** clicking a hero portrait in the Defenders squad arms it (red highlight, tooltip changes to "Click again to dismiss") for `ARM_TIMEOUT_MS` (3s); a second click within that window fires the hero for free — same free-dismiss pattern as residents, with a misclick guard. **Heroes that die in battle are auto-fired** at the end of the battle (`endInvasion` clears any `!alive` slot to `null`), so the slot is immediately free for a new recruit — no manual dismiss needed. Dead heroes are gone for good; only survivors respawn at full HP for the next battle.

### Workshop & Builders
- Unlocks at Village level (one level before the first raid trigger).
- Residents are **Builders**, rolling 0.3–1.0 Kingdom-HP-regen/sec (×rarity), same hire/fire/reroll mechanic as every other townsperson.
- Builders generate no gold — each Workshop hire is an income sacrifice in exchange for surviving raids longer-term.

## Raid system redesign — autobattler (implemented)

The hero-squad-vs-enemy-squad autobattle described above replaces the old duration/ratio siege system (`totalDefense` vs. a flat `defenseRequired`, `clamp(60/ratio, 10, 180)`). The 3-column "battle at the gates" layout (Admin / Town / Battle) from `layout-prototype.html` is now the live UI in `index.html`. `autobattler-prototype.html` and `layout-prototype.html` remain as standalone references but are no longer the source of truth.

**Remaining open items:**
- Hero squad cap growth — now planned as Military-tree expansion milestones, see *Progression loop redesign*.
- Kingdom HP reaching 0 ends the raid as an "Overrun" loss and records `kingdomFallRecord`, but doesn't trigger the reset/currency flow yet — see *Progression loop redesign* and *Difficulty & meta-progression design*.
- See *Progression loop redesign* and *Difficulty & meta-progression design* for the raid-tier vs. hero-rarity vs. Kingdom-siege balance pass, now blocked on the wave-count/currency numbers rather than open design questions.

## Progression loop redesign — end-to-end storyboard (planned, not yet implemented)

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
- Each raid tier has a fixed wave count before its boss: **+3 waves per tier** (placeholder — Goblin Raid 4 waves + boss on wave 5, Orc Warband 7 + boss on wave 8, Bandit Horde 10 + boss on wave 11, Dark Army 13 + boss on wave 14, Dragon Siege 16 + boss on wave 17).
- A **boss wave** is a unique named unit (Goblin Warmaster, Orc Warlord, etc.) with its own stat block, plus 2-3 minions from that tier's normal roster filling the remaining grid slots.
- Clearing a tier's boss wave immediately advances to the next tier's wave 1 (the tier's wave counter resets — same "resets on tier advance" behavior as today, just triggered by boss-kill instead of kingdom level).
- **A wave repeats until beaten** (locked in): on a loss, the same wave attacks again after the raid interval — the ladder only climbs on wins. (Implementation note: `endInvasion` currently does `tierWave++` unconditionally, *including on losses* — this must change to win-only in M8/M9.)
- Bosses need no special rule — like any wave they repeat until killed, and killing one is what advances the tier. They're still the natural per-run walls because their stat block spikes above the tier's normal waves.
- Repeated attempts at a wall aren't free: every stretch where no hero is standing drains Kingdom HP (see *Kingdom HP interplay* below), so a wall wave grants a limited number of attempts before the Age ends.
- **Wave composition varies within a tier**: squads fill more of the grid as waves climb (4 units early → full grid at the boss), with varied mixes (double-brute wave, skirmisher swarm, twin-healer wave). Waves feel distinct, and AoE / target-priority tools have something to answer.

### Enemy & hero grid expansion
- The **enemy grid auto-expands** at certain tier transitions (not every tier) — e.g. Goblin Raid and Orc Warband stay 2x3, Bandit Horde jumps to 3x4. Exact placements TBD.
- The **hero grid does not auto-expand** — squad size growth is a Military-tree purchase only, with multiple expansion milestones (2x3 → 3x4 → 4x4, etc.) timed to land roughly alongside the enemy-grid jumps. This makes "I'm suddenly outnumbered, I need more squad slots" a concrete, must-buy upgrade rather than a passive bonus.

### Kingdom HP interplay — persistent siege & mid-battle reinforcement (locked in)
The flow: enemies fight the hero squad; only once every hero is dead do they damage `kingdomHP` directly; Kingdom HP reaching 0 forces the loss/restart.

**A battle is a persistent, ongoing siege — it does not end when the hero squad wipes.** The recovery mechanism is **hiring heroes mid-battle**: the hero recruit pool keeps refreshing on its normal timer during combat, so a player whose squad goes down can hire reinforcements into the ongoing fight. New hires join immediately, enemies switch back from the kingdom to targeting them, and the Kingdom HP drained during the undefended gap is the attrition cost of the wipe. Gold, pool RNG, and the refresh timer are what you're scrambling against while the kingdom bleeds.

Consequences of this design:
- A raid has exactly **two outcomes**: **Repelled** (enemy squad wiped — possibly after several mid-battle squad rebuilds) or **Overrun** (`kingdomHP` hits 0 → the run ends). The old "Survived" outcome is retired.
- **No stalemate soft-lock**: income keeps flowing mid-battle at the full rate (the old 25% siege cap is removed), so even a broke player can eventually afford another reinforcement; if Builder regen can't hold the line while the player rebuilds, the kingdom falls — working as intended.
- Gold reserves effectively act as extra lives (feeding replacements into a wall wave). Likely self-balancing — cheap commons die near-instantly to deep-tier enemies and hero costs scale with rarity — but watch it in playtests.

Implementation state (verified in `game.js`): mid-battle hiring mostly works today — `hireHero` isn't gated on battle, `generateHero` initializes action cooldowns so `combatTick` picks new units up immediately, and `heroPoolTimer` runs during combat. **One gap for M8: dead heroes occupy their squad slots until `endInvasion` clears them**, so after a full wipe there's no empty slot to hire into. Fix: free a hero's slot at the moment of death (consistent with the existing "dead heroes are gone for good" rule — it just frees the slot when it matters).

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

### Scaling & tuning targets
- Enemy scaling keeps its current structure (`mult = powerMult × defenseGrowth^wave`, HP scaled by `√mult`) but the constants change meaning:
- **Make the curve continuous across tier transitions**: each tier's `powerMult` ≈ the previous tier's boss-wave multiplier. A new tier is a roster/mechanic/grid change, not a stat cliff (this removes the documented Dragon-wave-7 spike class of problem).
- **The current `defenseGrowth = 1.15` is too steep for a finite ladder.** The full ladder is ~55 waves; the final boss should land around **80–100× goblin-wave-1 stats** (matching the player's total growth: 10× legendary rarity × ~2.5× tree multipliers × squad growth 6→12+ slots × tactical unlocks). That works out to per-wave growth of roughly **1.08–1.10**, continuous across the whole ladder — the enemy grid expansions add effective power on top of stats. Placeholder pending playtest.
- Raid pacing: `RAID_INTERVAL = 20` is a dev value. Ship target ~45–60s between raids early (the town needs breathing room), tightening at later tiers.

### Victory condition — the Final Siege (locked in)
After the Dragon Siege boss (wave 17) falls, a herald announces the **Final Siege** arrives in 3 raids' time — a countdown the player preps through. Then a **3-phase gauntlet**: vanguard squad → elite squad → a phase-changing final boss with guards. Heroes do **not** reset to full HP between phases (menders and the Cathedral revive get their showcase), and Kingdom HP is the buffer that can carry a partial wipe across phases.
- **Loss**: counts as a Kingdom fall, but grants a large one-time "Lessons of the Last Siege" currency bonus so the failed attempt visibly funds the winning one.
- **Win**: victory screen with the campaign's stats — Ages founded, total time, where each Age fell (`kingdomFallRecord` already tracks fall points).

### Endless mode (locked in)
After victory the player may keep playing the current run (or start fresh runs) with raids scaling indefinitely — number-chasing for those who want it, clearly framed as post-game. The completion flag persists.

### Currency (replaces gold-based Legacy Points; name TBD, "Legacy Points" used for now)
- **First-ever-clear credit (locked in):** each wave on each tier's ladder pays out full value the first time it is cleared *across the whole campaign* (track a per-tier "deepest wave credited" high-water mark, persisted with meta state). Pushing past the all-time frontier is the primary way to earn meta currency.
- **Repeat-clear trickle (locked in):** re-clearing an already-credited wave pays a small fraction of its first-clear value (**~10–20%, exact % tunable**) so no run banks literally zero. Restart-farming stays pointless — the trickle on cheap early waves is negligible next to frontier pushes at 5x/tier values.
- Per-wave value scales roughly **5x per raid tier**. Boss waves pay an extra **3-5x** a normal wave of that tier as a "breakthrough" bonus.
- Currency persists across resets and is spent on the two upgrade trees below. The old gold-`goldEarned`-based formula (`floor(sqrt(goldEarned/100000))`) and the automatic "+5% income / +5% hero power per point" effect are both superseded by this.
- Possible future Economy-tree QoL: a "start at wave N" skip upgrade to shorten the retread on later runs (open to it, not yet designed).
- **Pricing philosophy:** total tree cost ≈ slightly under expected lifetime earnings across the 8–10 run arc, with the Final Siege realistically beatable at ~⅔ of the trees purchased — full completion is for thoroughness, not a requirement.

### Upgrade trees (Economy / Military)
Two permanent, currency-funded trees spent into after each reset:

- **Economy tree** — income multipliers (global or per-building), starting gold, "Old Foundations" (start runs at Village level), building cost-growth reduction, building cap increases beyond kingdom-level grants, Builder Kingdom-HP-regen multiplier, recruit-pool quality-of-life (refresh speed, rarity weights, pool size, reroll button), **Doctrines** (below).
- **Military tree** — hero stat multipliers (HP/attack/defense/heal, ranked, global or per-archetype), **hero squad-size expansion milestones** (the must-buy nodes tied to enemy-grid jumps), **new hero archetype unlocks** (below), "Veteran's Welcome" (start each run with a free rare Knight), cheaper hero hires, hero recruit-pool quality-of-life, Kingdom HP max / Kingdom defense ("Walls") / base HP regen, a scout report (see the next raid's composition).

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

### Gold & loot rebalance (single-currency decision, locked in)
The in-run economy stays **gold-only** — no separate combat currency for hero hiring. For that to work, **raid gold loot must shrink drastically**: current values (200,000g for a goblin raid vs. a 2,500g Smithy) let one raid win pay for the entire midgame, collapsing the "town fuels the army" loop into "raids fund everything". Target: a raid win pays roughly **1–2 minutes of contemporaneous resident income**. The win-streak multiplier stays, on the much smaller base.

### Open questions
- [ ] Exact numbers throughout — wave counts, per-tier currency multiplier, boss bonus, `defenseGrowth`, loot values — all placeholder until the M9/M14 playtests against the *Difficulty arc across runs* table.
- [ ] Exact tier transitions where the enemy grid expands, and where the matching hero squad-expansion milestones sit in the Military tree.
- [ ] Boss unit stat blocks and any per-boss unique abilities beyond the tier gimmick.
- [ ] UI for the run-end/reset summary screen and the two upgrade trees.

## Difficulty & meta-progression design — to-do

Playtesting at 100x surfaced a hard difficulty wall: an all-legendary hero squad was wiped and the Kingdom (1000 HP) was drained in ~5 seconds around Dragon Siege Wave 7 (`kingdomFallRecord` tracks the latest failure point for this kind of test). The *Progression loop redesign* section above now answers most of the structural questions this raised; remaining items are tuning/implementation details within that structure:

- [x] **What does the difficulty curve represent?** Decided: within a single run, the curve is *meant* to eventually become unwinnable — that's what triggers the reset (see *Progression loop redesign*). Across runs, the Economy/Military trees push that ceiling further out, so progress is measured run-over-run, not within one run.
- [x] **What triggers the first forced reset?** `kingdomHP` reaching 0 — see *Kingdom HP* and *Progression loop redesign*. Still needs wiring: `endInvasion` currently just ends the raid as "Overrun" and play continues; a `kingdomHP <= 0` result needs to short-circuit into the reset flow (bank currency, return to Hamlet) instead of looping back to `invasionTimer`.
- [ ] **Re-tune the raid-tier curve** (`powerMult`, `defenseGrowth`) and Kingdom siege values (`KINGDOM_DEFENSE`, `KINGDOM_HP_MAX`, Builder regen) alongside the new wave-count-per-tier and currency-per-wave numbers — concrete targets now live in *Progression loop redesign → Scaling & tuning targets* and the *Difficulty arc across runs* table (continuous ~1.08–1.10/wave growth, no tier cliffs, final boss ≈ 80–100× goblin wave 1).
- [x] **Design meta-progression between resets** — see *Progression loop redesign*: currency earned from in-run wave/boss progress, spent on Economy and Military trees.
- [x] **What does completing the game look like?** Decided: the **Final Siege** 3-phase gauntlet after the Dragon Siege boss is the victory condition; endless mode unlocks after victory. See *Progression loop redesign*.
- [ ] **Hero permadeath economics:** dead heroes are auto-fired (gone for good, see *Heroes & combat*); rebuilding the squad after a rough raid costs real gold/time within a run. Does this need its own lever (cheaper recruits at low kingdom levels, a "veteran" bonus, etc.), or does the run-restart-from-Hamlet structure make this moot since squads rebuild from scratch each run anyway?

## Prestige system — superseded by Progression loop redesign

The original design here (Legacy Points from lifetime `goldEarned`, manual prestige at Realm level, automatic +5% income/+5% hero power per point) is replaced by *Progression loop redesign* above: the reset is always triggered by `kingdomHP` reaching 0, the prestige currency is earned from in-run combat progress, and it's spent into two upgrade trees rather than applying automatic flat bonuses. The "Found a New Age" theme/naming and the basic "what resets / what persists" shape carry over:

- **What resets:** Gold, buildings, residents, heroes, kingdom level, raid tier/wave — back to Hamlet with starting gold.
- **What persists:** Prestige currency (see *Progression loop redesign*), Economy/Military tree purchases, the game-completion flag / endless-mode unlock, `kingdomFallRecord` history, auto-recruit setting, dev speed setting.

## Milestone tracker
- [x] Milestone 1: Gold counter ticking automatically
- [x] Milestone 2: Cottage building — buy to earn gold/sec
- [x] Milestone 3: Residents with random rolls, hire/fire system
- [x] Milestone 4: Multiple building types with different residents; dynamic rendering
- [x] Milestone 5: Kingdom level system — building caps + unlock gates unified
- [x] Milestone 6: Workshop + defense meter + invasion system
- [x] Milestone 7: Autobattler combat — hero squad vs. enemy squad, Kingdom HP, Keep/Workshop repurposed (hero rarity bias / Builders), 3-column "battle at the gates" layout
- [ ] Milestone 8: **The run loop** — `kingdomHP` 0 → run-summary screen → currency banking (first-ever-clear credit via per-tier high-water mark) → upgrade-tree shop → reset to Hamlet; meta-state persistence; manual "Found a New Age" button; battle-end fix (waves repeat on loss — `tierWave++` becomes win-only); free a dead hero's squad slot at the moment of death so mid-battle reinforcement works after a full wipe (see *Kingdom HP interplay*). This changes the *shape* of the game before any content is added — everything below hangs off it.
- [ ] Milestone 9: **Economy & pacing pass** — loot cut, raid interval, per-tier wave counts + boss waves, tier advance by boss-kill, wall targets for runs 1–3 at real 1× speed
- [ ] Milestone 10: **First new heroes** — Paladin + Assassin unlocks and the first squad-expansion milestone (no engine work needed)
- [ ] Milestone 11: **Combat engine features** — AoE actions, buffs/debuffs, on-death hooks; enemy tier mechanics, boss units, wave composition variety, enemy grid expansion
- [ ] Milestone 12: **Doctrines** — building↔army synergy nodes
- [ ] Milestone 13: **Final Siege** — 3-phase gauntlet, victory screen, endless mode
- [ ] Milestone 14: **Full-game balance playtest** against the *Difficulty arc across runs* table

## Starting state
- Player begins with 50 gold (enough to buy first Cottage at 10g + hire first Villager at 25g)
- No base income — gold only accrues from hired residents
- Kingdom HP starts full (1000 / `KINGDOM_HP_MAX`)
