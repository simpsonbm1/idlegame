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
Buildings are slot containers — they don't generate income directly. Each building purchased opens a fixed number of resident slots. Each building type has its own cost growth rate (`costGrowth` in `game.js`), individually tuned so early buildings (Cottage, Tavern, Smithy, Library) stay affordable for longer while late-game buildings (Workshop, Tower, Cathedral) ramp up faster — replacing the old single global 1.15x multiplier.

### Residents
Residents are hired to fill building slots. Each hire costs gold and does a **one-time random roll** that permanently determines that resident's gold/sec income. Residents can be fired for free (no cost) and re-hired to reroll — this is the core optimization loop.

Roll structure (per building type):
- Normal roll: random value within `incomeMin`–`incomeMax`
- Lucky roll: `luckyChance` probability of rolling `luckyMin`–`luckyMax` instead, marked with ★

### Resources
- **Gold** — the only resource for now. More resource types will be added as the game develops.

### Planned: Defense / Invasion
- A Barracks building will hold soldiers (knights, guards)
- Soldiers generate **defense power** instead of gold
- Invasions scale with town wealth — richer towns are bigger targets
- This creates a core tradeoff: maximize income vs. investing in defense

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

## Design decisions locked in
- Fully idle — no clicking to earn resources
- One-time roll on hire (not per-tick variance)
- Free eviction (fire and re-hire to reroll)
- Buildings are slot containers, not direct income sources
- Cost scaling: per-building growth rates (no single global multiplier) — each building's curve is tuned to its place in the progression
- Single resource (gold) to start; more added iteratively
- RPG/dungeon elements are a possible future addition

## Current building roster

| Building | Cost | Slots | Resident | Hire cost | Normal roll | Lucky roll | Lucky chance |
|---|---|---|---|---|---|---|---|
| Cottage | 10g (scales) | 3 | Villager | 25g | 1–5 g/s | 8–15 g/s | 10% |
| Tavern | 300g (scales) | 4 | Tavernkeeper | 120g | 5–12 g/s | 20–35 g/s | 10% |
| Smithy | 2500g (scales) | 3 | Blacksmith | 700g | 15–40 g/s | 70–120 g/s | 10% |
| Library | 15000g (scales) | 5 | Scholar | 3500g | 50–130 g/s | 220–380 g/s | 10% |

| Keep | 500,000g (scales) | 3 | Knight | 5,000g | 50–120 defense | — | — |
| Alchemist's Workshop | 80,000g (scales) | 4 | Alchemist | 25,000g | 150–350 g/s | — | — |
| Wizard's Tower | 600,000g (scales) | 3 | Mage | 150,000g | 400–900 g/s | — | — |
| Cathedral | 5,000,000g (scales) | 5 | High Priest | 1,000,000g | 1,000–2,500 g/s | — | — |

All numbers are tunable — balance pass pending.

## Kingdom level system
The player's kingdom has a level (Hamlet → Village → Town → City → Kingdom) that acts as the unified progression gate. Leveling up costs gold and does two things simultaneously:
1. Raises the cap on how many of each building you can own
2. Unlocks new building types

This replaces a separate "unlock threshold" system — kingdom level IS the unlock gate.

Level-up is manual (spend gold via a button), not automatic.

| Level | Name | Cost | Cottage | Tavern | Smithy | Library | Barracks | Keep | Workshop | Tower | Cathedral | Unlocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Hamlet | — | 10 | — | — | — | — | — | — | — | — | Cottage |
| 1 | Village | 500g | 25 | 8 | — | — | 1 | — | — | — | — | Tavern, Barracks |
| 2 | Town | 5,000g | 50 | 20 | 8 | — | 5 | — | — | — | — | Smithy |
| 3 | City | 35,000g | 75 | 35 | 20 | 8 | 8 | — | — | — | — | Library |
| 4 | Kingdom | 200,000g | 100 | 60 | 35 | 20 | 12 | — | — | — | — | — |
| 5 | Empire | 1,000,000g | 150 | 90 | 55 | 30 | 18 | 3 | 8 | — | — | Workshop, Keep |
| 6 | Dynasty | 8,000,000g | 200 | 120 | 75 | 50 | 25 | 6 | 15 | 6 | — | Wizard's Tower |
| 7 | Realm | 60,000,000g | 250 | 160 | 100 | 70 | 35 | 10 | 25 | 12 | 5 | Cathedral |

Locked buildings show in the UI with a hint ("Unlocks at Village") so the player can see what they're working toward.

All numbers are tunable.

## Invasion / defense system

**Trigger:** Town level (2) + 12,000 total gold *earned* (a counter that only goes up, separate from current gold — spending down can't delay an invasion). After the first raid, they repeat indefinitely.

**Siege effect:** While under siege, gold income drops to 25% of normal.

**Resolution — duration-based, not a pass/fail gate:** Sieges no longer instantly resolve once defense crosses a threshold. Instead, every siege lasts a set duration that's calculated when it starts, based on how your current defense compares to that raid's benchmark (`ratio = totalDefense / defenseRequired`):
- `siegeDuration = clamp(60 / ratio, 10, 180)` seconds — strong defense means a short siege near the 10s floor, weak defense means a long siege capped at 180s. **Sieges always end** — this is what prevents a "permanent siege" once raids outscale your defense.
- When the timer runs out, the siege resolves as a win (`ratio >= 1`) or a loss, which determines the loot payout (see below).

**Raid types are tied to kingdom tier:** instead of one global ever-climbing wave counter, each kingdom level from Town onward has its own raid family with its own difficulty curve and wave counter that **resets when you advance to the next tier**:

| Kingdom level | Raid name | Base defense | Defense growth/wave |
|---|---|---|---|
| Town (2) | Goblin Raid | 500 | 1.15 |
| City (3) | Orc Warband | 1,200 | 1.15 |
| Kingdom (4) | Bandit Horde | 3,000 | 1.15 |
| Empire (5) | Dark Army | 7,500 | 1.15 |
| Dynasty/Realm (6+) | Dragon Siege | 11,000 | 1.15 |

Since there's no raid type defined past Dragon Siege (minLevel 6) and Realm is level 7, both tiers share Dragon Siege — the wave count and win streak carry through that transition without resetting (the lookup naturally "saturates" at the last defined tier).

**Loot — win-streak combo system:** loot is no longer a flat amount or a simple ratio of the reward. Each raid type tracks a win streak:
- **Win** (`ratio >= 1`): payout = `baseLoot × lootGrowth^streak`, then the streak increments — chaining repels compounds the reward.
- **Loss**: payout = a flat `baseLoot × 0.5` consolation amount, and the streak resets to zero.

This keeps difficulty climbing forever (via the wave counter, win or lose) while preventing runaway rewards from "farming" failed sieges — losing always pays a small, fixed amount tied to the tier's base, never scaling with how far the difficulty has outrun your defense. Switching raid tiers resets the streak too.

Per-tier loot values (`baseLoot` / `lootGrowth`): Goblin Raid 200,000 / 1.30, Orc Warband 1,000,000 / 1.30, Bandit Horde 5,000,000 / 1.32, Dark Army 25,000,000 / 1.34, Dragon Siege 120,000,000 / 1.36.

**Invasion schedule:** Periodic — once triggered, raids repeat every 5 minutes (300 seconds). Timer only counts down while not under siege.

**Wave naming:** first raid of a tier shows as just the tier name (e.g. "Goblin Raid"); subsequent waves show as "Goblin Raid (Wave 2)", etc.

**Preview:** Left panel always shows next raid name, defense benchmark, and countdown timer. While under siege it shows a live countdown to resolution and an outlook hint ("Defenses holding strong" / "Defenses are not enough — brace for losses").

**Loot display:** Does not count toward `goldEarned` (to avoid immediately triggering the next invasion trigger check). The last raid's outcome persists as "Repelled: ..." or "Survived: ..." in the left panel depending on whether it was a win or a loss.

**Barracks:**
- Unlocks at Village level (one level before first invasion)
- Soldiers generate defense power only — no gold
- Same random roll mechanic as other residents
- Cap tracked in kingdom levels table like other buildings

**Soldiers do not generate gold** — each Barracks is an income sacrifice, making the defense investment a real tradeoff.

## Raid system redesign — active autobattler direction (exploratory)

**Status:** directional ideation plus a standalone prototype only — nothing here is wired into `game.js` yet. The duration-based siege system documented above is the current implementation; this section captures where it's headed next.

**Why a redesign:** the documented siege system resolves passively (compare a number to a benchmark, wait out a timer), which doesn't give the player a reason to look at the screen. The fix isn't faster clicking — that's the Cookie Clicker trap, trivially autoclickable — it's positioning and composition decisions that depend on reading the current state, the way Gnorp Apologue / Wizard Tower / Scritchy Scratchy keep players engaged.

**New direction — heroes vs. raiders autobattler:**
- Town Square splits into two pools: townspeople (gold income) and heroes (defense/combat)
- Combat resolves on a 2x3 grid per side (3 frontline slots targeted first, 3 backline); the player drags hero tiles between slots to set formation, including mid-battle
- Targeting is weighted, not absolute — each unit rolls its own `backlineChance` (most ~15%) to decide whether it goes after the front or back row, so "ranged units skip the frontline" falls naturally out of giving those units a higher chance rather than needing a hard-coded rule
- Units have independent `attack` and `heal` actions, each with its own power/speed/cooldown, so hybrids (e.g. a future Paladin) can do both on staggered timers without special-casing
- Hero rarity mirrors the townspeople rarity system conceptually, but goes further: same role, different *name* and scaled stats per tier (Archer → Sharpshooter → Hunter → Marksman) rather than a generic "Rare Archer" label
- Enemy rosters generate the same way, reskinned per raid family (Goblin Raid, Orc Warband, Bandit Horde, Dark Army, Dragon Siege), so both sides scale on a comparable curve

**Prototype:** `autobattler-prototype.html` — standalone page (not linked from `index.html`) for testing combat feel: drag-and-drop formations, live battle simulation, a hero-tier preview panel, and a raid-theme selector for difficulty testing. Early playtesting: a default Common-tier hero roster comfortably beats Goblin Raid, struggles through Orc Warband, and gets crushed by Bandit Horde — a believable ramp, though the placeholder enemy `powerMult` curve and hero rarity multipliers haven't been tuned against each other yet.

**The bigger picture — losing as the core progression loop:** the vision has shifted from "prestige is an optional late-game milestone" (the Realm-level gate described in the Prestige section below) toward a Hades/Rogue Legacy model: **the kingdom has an HP bar and is expected to eventually fall** — not a failure state, but the intended rhythm that drives meta-progression. Losing heroes damages the kingdom; the kingdom falling triggers a reset into the Legacy Points system. A manual "pull the cord early" reset would sit alongside the forced one, both feeding the same meta-currency — the existing `floor(sqrt(goldEarned / 100,000))` formula already works for either trigger, since it only cares about lifetime earnings, not how the run ended. This would likely replace the Realm-level prestige gate entirely, since the raid difficulty curve does that gating naturally (a fresh kingdom could fall to a Goblin Raid long before reaching Realm, and that's fine).

**Open questions before building for real:** how hero-rarity scaling and raid-tier scaling should track each other (so the loop stays fair as both climb); how kingdom HP loss should be calculated from lost heroes; whether the manual and forced reset paths should reward identically or differently; what meta-progression upgrades should do beyond the already-planned +5%/point income & defense bonuses.

## Prestige system (planned — not yet built)

**Theme:** "Found a New Age" — the kingdom falls but its legend persists, granting bonuses to the rebuild.

**Trigger:** Manual. Player can prestige any time after reaching Realm level (7). A prominent button appears once eligible.

**What resets:**
- Gold, buildings, residents, kingdom level — back to Hamlet with starting gold

**What persists:**
- Legacy Points (the prestige currency)
- Auto-recruit setting
- Dev speed setting

**Legacy Points formula:**
```
Legacy Points earned = floor( sqrt( goldEarned / 100,000 ) )
Total Legacy Points = sum across all runs
```
Based on lifetime earnings model (always gain something, even from suboptimal runs).

**What Legacy Points do:**
- Each point = +5% gold income permanently
- Each point = +5% defense power permanently
- Both scale together so the soft cap (raids outpacing defense) moves further out each run

**The soft cap mechanic:**
Raid difficulty scales indefinitely per tier (each tier's defense requirement grows ~1.15x per wave, forever — see *Invasion / defense system*). Eventually defense capacity (capped by Barracks slots × max roll) falls behind, win streaks stop forming, and sieges spend more time at 25% income. This is the signal to prestige — not a hard failure, just a nudge. After prestiging, the income/defense multipliers push that ceiling further out.

**UI:**
- Left panel shows "Legacy: X points (+Y%)" once first prestige has happened
- "Found a New Age" button appears at Realm level, shows how many Legacy Points the current run would earn
- Confirmation screen before resetting (same in-page pattern as reset button)

**Balance notes:**
- At 1,000,000 goldEarned: 3 points (+15% income/defense)
- At 100,000,000 goldEarned: 31 points (+155%)
- Numbers tunable — the formula shape matters more than exact values

## Milestone tracker
- [x] Milestone 1: Gold counter ticking automatically
- [x] Milestone 2: Cottage building — buy to earn gold/sec
- [x] Milestone 3: Residents with random rolls, hire/fire system
- [x] Milestone 4: Multiple building types with different residents; dynamic rendering
- [x] Milestone 5: Kingdom level system — building caps + unlock gates unified
- [x] Milestone 6: Barracks + defense meter + invasion system

## Starting state
- Player begins with 50 gold (enough to buy first Cottage at 10g + hire first Villager at 25g)
- No base income — gold only accrues from hired residents
