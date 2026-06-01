# Idle Kingdom — Project Context

## What this is
A medieval fantasy idle game. The player builds a town by constructing buildings and hiring residents, who generate passive gold income. No click-to-earn mechanic — everything is fully idle once set up.

This is the developer's first coding project. Keep explanations clear, define new terms, and prefer small working milestones over large upfront designs.

## Tech stack
Plain HTML + CSS + JavaScript. No frameworks, no build step. Open `index.html` in a browser to run.

## File structure
- `index.html` — page structure and UI elements
- `style.css` — medieval dark theme styling
- `game.js` — all game logic

## Core mechanics

### Buildings
Buildings are slot containers — they don't generate income directly. Each building purchased opens a fixed number of resident slots. Buildings scale in cost by 1.15x per purchase.

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
- Cost scaling: 1.15x per building purchase
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

**Trigger:** Kingdom level threshold + total gold *earned* (a counter that only goes up, separate from current gold — spending down can't delay an invasion).

**Siege effect:** While under siege, gold income drops to 25% of normal.

**Resolution:** When total defense power >= invasion's required defense, the invasion is instantly repelled. Defense power is the sum of all soldiers' rolled stats — same mechanic as residents generating gold.

**Loot bonus:** Repelling an invasion awards a one-time gold bonus (soldiers brought back loot). Fixed amount per invasion.

**Invasion schedule:** Periodic — once triggered, raids repeat every 5 minutes (300 seconds). Timer only counts down while not under siege.

**Trigger:** Town level (2) + 12,000 total gold earned. After that, raids repeat indefinitely.

**Scaling per wave:**
- Defense required: `500 × 1.5^waveNumber` (wave 0=500, 1=750, 2=1125, ...)
- Loot reward: `4000 × 1.3^waveNumber` (wave 0=4000, 1=5200, 2=6760, ...)

**Wave names:** Goblin Raid → Orc Warband → Bandit Horde → Dark Army → Dragon Siege (then "Dragon Siege Wave N")

**Preview:** Left panel always shows next raid name, defense needed, and countdown timer.

**Loot:** Fixed gold reward on repelling. Does not count toward `goldEarned` (to avoid immediately triggering the next invasion). Persists as "Last Victory" in the left panel.

**Barracks:**
- Unlocks at Village level (one level before first invasion)
- Soldiers generate defense power only — no gold
- Same random roll mechanic as other residents
- Cap tracked in kingdom levels table like other buildings

**Soldiers do not generate gold** — each Barracks is an income sacrifice, making the defense investment a real tradeoff.

## Milestone tracker
- [x] Milestone 1: Gold counter ticking automatically
- [x] Milestone 2: Cottage building — buy to earn gold/sec
- [x] Milestone 3: Residents with random rolls, hire/fire system
- [x] Milestone 4: Multiple building types with different residents; dynamic rendering
- [ ] Milestone 5: Kingdom level system — building caps + unlock gates unified
- [x] Milestone 6: Barracks + defense meter + invasion system

## Starting state
- Player begins with 50 gold (enough to buy first Cottage at 10g + hire first Villager at 25g)
- No base income — gold only accrues from hired residents
