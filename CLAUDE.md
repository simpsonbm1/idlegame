# Idle Kingdom — Project Context

## What this is
A medieval fantasy idle game. The player builds a town by constructing buildings and hiring residents, who generate passive gold income. No click-to-earn mechanic — everything is fully idle once set up.

This is the developer's first coding project. Keep explanations clear, define new terms, and prefer small working milestones over large upfront designs.

## Keeping this file current
**Before committing or pushing changes, update this file to reflect the current state of the project.** Mechanics, formulas, balance values, and design decisions documented here should match what's actually implemented in `game.js` — this file is the map other sessions (and the developer) use to understand the game without re-reading all the code.

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
- Fully idle — no clicking to earn resources
- One-time roll on hire (not per-tick variance)
- Free eviction (fire and re-hire to reroll)
- Buildings are slot containers, not direct income sources
- Cost scaling: per-building growth rates (no single global multiplier) — each building's curve is tuned to its place in the progression
- Single resource (gold) to start; more added iteratively
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

**Siege effect:** While a battle is in progress (`currentInvasion` is set), gold income drops to 25% of normal.

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

The original full-idle "always growing" framing (Adventure Capitalist/Realm Grinder style) is replaced by a death-and-rebuild loop closer to Gnorp Apologue / Wizard and Minion / Scritchy Scratchy: each run ends when the Kingdom falls, and that run's combat progress funds permanent upgrades that make the next run faster and stronger. The kingdom's economy now exists to fuel the battle, not as the end goal itself. Numbers below are placeholders pending playtesting.

### The run loop
1. Start at Hamlet with starting gold, full Kingdom HP. **Every run starts here** — there is no persistent tier-ratchet that skips a run ahead in raid tiers.
2. Build economy, level up the kingdom, reach Town level → Goblin Raid begins.
3. Clear raid waves; defeating a tier's boss wave advances immediately to the next tier's wave 1 (Goblin Raid → Orc Warband → Bandit Horde → Dark Army → Dragon Siege). Every wave cleared banks currency (see below).
4. Eventually `kingdomHP` reaches 0 — the run ends ("Found a New Age" reset). Gold, buildings, residents, kingdom level, and raid tier/wave all reset to start-of-run state.
5. Currency banked this run is spent on the Economy and Military upgrade trees (permanent, persists across resets).
6. Next run repeats from step 1, but upgrades mean earlier tiers clear much faster, so playtime concentrates near whatever tier is currently the frontier.

The upgrade trees **are** the ratchet — there's no separate "tier unlock" flag. A heavily-upgraded player still technically starts at Goblin Raid wave 1 each run, but blows through it in seconds.

### Wave & boss structure per raid tier
- Each raid tier has a fixed wave count before its boss: **+3 waves per tier** (placeholder — Goblin Raid 4 waves + boss on wave 5, Orc Warband 7 + boss on wave 8, Bandit Horde 10 + boss on wave 11, Dark Army 13 + boss on wave 14, Dragon Siege 16 + boss on wave 17).
- A **boss wave** is a unique named unit (Goblin Warmaster, Orc Warlord, etc.) with its own stat block, plus 2-3 minions from that tier's normal roster filling the remaining grid slots.
- Clearing a tier's boss wave immediately advances to the next tier's wave 1 (the tier's wave counter resets — same "resets on tier advance" behavior as today, just triggered by boss-kill instead of kingdom level).

### Enemy & hero grid expansion
- The **enemy grid auto-expands** at certain tier transitions (not every tier) — e.g. Goblin Raid and Orc Warband stay 2x3, Bandit Horde jumps to 3x4. Exact placements TBD.
- The **hero grid does not auto-expand** — squad size growth is a Military-tree purchase only, with multiple expansion milestones (2x3 → 3x4 → 4x4, etc.) timed to land roughly alongside the enemy-grid jumps. This makes "I'm suddenly outnumbered, I need more squad slots" a concrete, must-buy upgrade rather than a passive bonus.

### Currency (replaces gold-based Legacy Points; name TBD, "Legacy Points" used for now)
- Earned continuously during a run: **every wave cleared banks currency**, with the per-wave value scaling roughly **5x per raid tier** (consistent with the existing per-tier `baseLoot` ratios in *Invasion & combat system*). Boss waves pay an extra **3-5x** a normal wave of that tier as a "breakthrough" bonus.
- Because wave counts grow only linearly (+3/tier) while per-wave value grows ~5x/tier, repeatedly farming early tiers can never out-earn pushing into a new tier — no farming caps or detection needed, the economics self-regulate.
- Currency persists across resets and is spent on the two upgrade trees below. The old gold-`goldEarned`-based formula (`floor(sqrt(goldEarned/100000))`) and the automatic "+5% income / +5% hero power per point" effect are both superseded by this.

### Upgrade trees (Economy / Military)
Two permanent, currency-funded trees spent into after each reset:

- **Economy tree** — examples: income multipliers (global or per-building), building cost-growth reduction, building cap increases beyond kingdom-level grants, Builder Kingdom-HP-regen multiplier, recruit-pool quality-of-life (refresh speed, rarity weights, pool size).
- **Military tree** — examples: hero stat multipliers (HP/attack/defense/heal, global or per-archetype), **hero squad-size expansion milestones** (the must-buy nodes tied to enemy-grid jumps), hero recruit-pool quality-of-life, Kingdom HP max / Kingdom defense increases, possibly new hero archetypes as late nodes.

### Open questions
- [ ] Exact wave-count progression, per-tier currency multiplier, and boss bonus multiplier — placeholders above, needs playtesting.
- [ ] Exact tier transitions where the enemy grid expands, and where the matching hero squad-expansion milestones sit in the Military tree.
- [ ] What "completing the game" looks like once a run can sustain Dragon Siege indefinitely (or beyond) — is there a final boss/mechanic, or is a long plateau itself the win state?
- [ ] Boss unit design — stat blocks, any unique abilities beyond "much tougher", and how `ENEMY_ARCHETYPES`/`generateEnemy` need to extend to support a `BOSS_ARCHETYPES`-style table.
- [ ] UI for the run-end/reset screen and the two upgrade trees.

## Difficulty & meta-progression design — to-do

Playtesting at 100x surfaced a hard difficulty wall: an all-legendary hero squad was wiped and the Kingdom (1000 HP) was drained in ~5 seconds around Dragon Siege Wave 7 (`kingdomFallRecord` tracks the latest failure point for this kind of test). The *Progression loop redesign* section above now answers most of the structural questions this raised; remaining items are tuning/implementation details within that structure:

- [x] **What does the difficulty curve represent?** Decided: within a single run, the curve is *meant* to eventually become unwinnable — that's what triggers the reset (see *Progression loop redesign*). Across runs, the Economy/Military trees push that ceiling further out, so progress is measured run-over-run, not within one run.
- [x] **What triggers the first forced reset?** `kingdomHP` reaching 0 — see *Kingdom HP* and *Progression loop redesign*. Still needs wiring: `endInvasion` currently just ends the raid as "Overrun" and play continues; a `kingdomHP <= 0` result needs to short-circuit into the reset flow (bank currency, return to Hamlet) instead of looping back to `invasionTimer`.
- [ ] **Re-tune the raid-tier curve** (`powerMult`, `defenseGrowth`) and Kingdom siege values (`KINGDOM_DEFENSE`, `KINGDOM_HP_MAX`, Builder regen) alongside the new wave-count-per-tier and currency-per-wave numbers from *Progression loop redesign* — these all need tuning together now.
- [x] **Design meta-progression between resets** — see *Progression loop redesign*: currency earned from in-run wave/boss progress, spent on Economy and Military trees.
- [ ] **Hero permadeath economics:** dead heroes are auto-fired (gone for good, see *Heroes & combat*); rebuilding the squad after a rough raid costs real gold/time within a run. Does this need its own lever (cheaper recruits at low kingdom levels, a "veteran" bonus, etc.), or does the run-restart-from-Hamlet structure make this moot since squads rebuild from scratch each run anyway?

## Prestige system — superseded by Progression loop redesign

The original design here (Legacy Points from lifetime `goldEarned`, manual prestige at Realm level, automatic +5% income/+5% hero power per point) is replaced by *Progression loop redesign* above: the reset is always triggered by `kingdomHP` reaching 0, the prestige currency is earned from in-run combat progress, and it's spent into two upgrade trees rather than applying automatic flat bonuses. The "Found a New Age" theme/naming and the basic "what resets / what persists" shape carry over:

- **What resets:** Gold, buildings, residents, kingdom level, raid tier/wave — back to Hamlet with starting gold.
- **What persists:** Prestige currency (see *Progression loop redesign*), Economy/Military tree purchases, auto-recruit setting, dev speed setting.

## Milestone tracker
- [x] Milestone 1: Gold counter ticking automatically
- [x] Milestone 2: Cottage building — buy to earn gold/sec
- [x] Milestone 3: Residents with random rolls, hire/fire system
- [x] Milestone 4: Multiple building types with different residents; dynamic rendering
- [x] Milestone 5: Kingdom level system — building caps + unlock gates unified
- [x] Milestone 6: Workshop + defense meter + invasion system
- [x] Milestone 7: Autobattler combat — hero squad vs. enemy squad, Kingdom HP, Keep/Workshop repurposed (hero rarity bias / Builders), 3-column "battle at the gates" layout
- [ ] Milestone 8: Progression loop redesign — death/reset run loop, per-tier wave/boss structure, enemy/hero grid expansions, currency formula, Economy/Military upgrade trees (see *Progression loop redesign*)

## Starting state
- Player begins with 50 gold (enough to buy first Cottage at 10g + hire first Villager at 25g)
- No base income — gold only accrues from hired residents
- Kingdom HP starts full (1000 / `KINGDOM_HP_MAX`)
