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
Plain HTML + CSS + JavaScript. No frameworks, no build step. Open `index.html` in a browser to
run — but **serve over http to see sprites**: double-click `start-game-server.bat` (serves
:8321 and opens the game), or `py -m http.server 8321`. The M15 runtime sprite pipeline needs
canvas pixel access, which browsers block on `file://`, so a plain double-click of `index.html`
still runs the game (logic + saves intact) but shows letter/placeholder art instead of sprites.
Shipping the game to players who can't run a server is **M17: distribution & packaging** (see
the milestone tracker) — deferred to end-of-project.

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

**Invasion schedule:** Once triggered, a new raid starts every `raidInterval` seconds (per-tier, 45s early tightening to 30s at Infernal Siege) of non-battle time. The raid status bar (right column) shows "Next: <raid name> · Arrives in M:SS" while waiting.

### Raid tiers — one continuous ladder, climbed by boss-kill (M9)
The five tiers form a single ~55-wave ladder. **Kingdom level no longer selects the raid tier**: every run starts at Goblin Raid wave 1, each tier has a fixed `waveCount` ending in a **boss wave**, and killing the boss advances to the next tier's wave 1 (wave counter and win streak reset). A lost wave just re-attacks — the ladder climbs only on wins.

Each tier's `powerMult` picks up where the previous tier's boss left off (`defenseGrowth = 1.088`/wave, continuous across the whole ladder — a new tier is a roster change, not a stat cliff). The final boss lands at ~95× goblin wave 1 stats, inside the 80–100× design target.

| Tier | `powerMult` | Waves (boss on last) | Interval | Grid | Tier lesson (traits) | Boss (signature) | Base loot |
|---|---|---|---|---|---|---|---|
| Goblin Raid | 1.0 | 5 | 45s | 2x3 | vanilla — teaches the basics | Goblin Warmaster (war-cry aura: all allies +15% power) | 1,200g |
| Orc Warband | 1.52 | 8 | 45s | 2x3 | brutes **enrage** <50% HP (×1.5 attack speed) | Orc Warlord (enrage ×1.75 speed +25% power) | 5,000g |
| Bandit Horde | 3.0 | 11 | 40s | 3x4 | marksmen hunt the backline (`backlineChance` 0.7); **sappers debut** | Bandit King (backlineChance 0.85) | 30,000g |
| Undead Legion | 7.6 | 14 | 35s | 3x4 | necromancers **revive** a fallen ally once (50% HP) | Lich Commander (2 revive charges) | 120,000g |
| Infernal Siege | 24.7 | 17 | 30s | 4x4 | flamecallers **scour whole rows** (hellfire AoE) | Demon Empress (hellfire row + enrage +25% power) | 500,000g |

Rosters (brute / skirmisher / caster / shaman / sapper): Goblin Brute / Skulker / Slinger / Shaman / Tunneler · Orc Brute / Berserker / Warcaster / Witch Doctor / Saboteur · Bandit Enforcer / Cutthroat / Marksman / Medic / Torchman · Death Knight / Shadow Reaver / Necromancer / Bone Priest / Grave Digger · Pit Fiend / Hellhound / Flamecaller / Blood Acolyte / Cinder Imp.

**Tier re-theme (2026-07-17, decided before the M15 asset run locked themes into sprites):**
"Dark Army" → **Undead Legion** (the mundane→supernatural turn deserved an explicit label) and
"Dragon Siege" → **Infernal Siege** (demons: bandits → undead → hell completes one occult
crescendo instead of restarting at "monster"; the Demon Empress keeps the Empress finale copy
intact). Names/flavor only — zero stat, wave, or balance changes; sim mirrors relabeled.

**Wave compositions (M11):** hand-authored per tier per wave in `TIER_WAVES` ("archetype row col" strings; `BOSS r c` places the boss). Deterministic — a repeated wave is the identical fight. Waves fill more of the grid as they climb, with variety mixes (double-brute, skirmisher swarm, twin-healer, sapper raids); boss waves lead bigger honor guards on the larger grids.

**Boss waves:** the tier's named boss is a heavily scaled-up brute (×1.8 power, ×4 HP on top of the wave multiplier) with a signature trait (see the tier table), leading an honor guard from the tier's composition. Past the Demon Empress: the Final Siege countdown, then the gauntlet — and endless scaling after victory (see *Victory condition*).

**Wave naming:** first wave of a tier shows as just the tier name; later waves as "Goblin Raid (Wave 2)"; boss waves as "Goblin Raid — Goblin Warmaster".

### Combat
Each raid spawns a 2x3 enemy squad (brute + skirmisher front, caster + shaman back, two empty slots) that fights the player's hero squad in the same 2x3 grid layout. Combat runs automatically, advancing by one game-second per `tick()` (so dev-speed multipliers speed up battles too):

- Each unit has independent `attack` and/or `heal` **actions**, each with its own `power`, `speed`, and cooldown (`cooldown = BASE_ATTACK_INTERVAL / speed`, `BASE_ATTACK_INTERVAL = 2500ms`). This lets future hybrid units (e.g. a Paladin) attack and heal on staggered timers without special-casing.
- **Targeting** is weighted, not absolute: an attacker rolls its own `backlineChance` (`DEFAULT_BACKLINE_CHANCE = 0.15`, skirmishers are 0.4) to decide whether it goes after the front row or back row, then picks within that row — where each unit draws `guard` "tickets" (`weightedPick`, M14.1 guard spectrum: guardian 3 / paladin·banneret 2 / fighter 1.5 / assassin 0.5 / unset 1). A lone unit in its pool gains nothing from guard; the mechanic is engine-generic (enemy tanks could later use it too — currently hero-side only).
- **Healers** (shamans, menders) always target the lowest-HP% wounded ally on their side; if nobody's wounded the heal is held for next tick.
- Damage: `dmg = max(1, round(attackPower * (1 - defense / 100)))`.
- **M11 modifier layer** — computed from unit state at each use (never stacked effect objects): **enrage** (`unit.enrage`, active below 50% HP: ×speed on cooldown refill, ×power), **auras** (`unit.aura` — Banneret: adjacent allies ±1 row/col; boss war-cries: whole squad; boosts attack *and* heal power), **chill** (`attack.chill` sets `chilledUntil`/`chillMult` on the target — cooldowns refill ×1.35 slower for 6s; heroes shed chill between battles), **row AoE** (`attack.aoe = 'row'` hits every living unit in the target's row at `AOE_POWER_FACTOR` 0.65 — the discount keeps the deep ladder winnable), **on-death revive** (`reviveCharges`: when an enemy dies, a living ally with charges raises it at 50% HP — killing revivers first is the counter), and **sappers** (`targetsKingdom`: always attack Kingdom HP even while heroes stand; each hit has `SAPPER_INJURY_CHANCE` 25% to injure a random staffed resident for `INJURY_DURATION` 90s — income/regen paused, portrait marked ✚, auto-recovers, never killed; `recomputeIncome()` runs each tick and skips injured residents).
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
- **The Kingdom is the last line of defense.** While any hero is alive, enemies target the hero squad as normal (`pickTarget`). Once the hero squad is wiped, every surviving enemy attack instead hits `kingdomHP` directly (`attackKingdom`), using the same `dmg = max(1, round(power * (1 - defense/100)))` formula against `getKingdomDefense()` — base `KINGDOM_DEFENSE = 15` plus **+3 per Reinforced Walls rank** (M14.1; the old "tie it to a Walls-type building" placeholder is now realized through the Legacy node, making Walls actively blunt every siege hit rather than just adding ablative HP).
- A battle now ends when **either** the enemy squad is wiped (win) **or** `kingdomHP` reaches 0 (loss). The old "lump sum of dead heroes' maxHp at battle end" penalty has been removed entirely — all Kingdom HP loss now comes from this real-time siege.
- Regenerated continuously by **Builders** (Workshop residents), `kingdomHpRegen` HP/sec, applied once per tick alongside gold income (including mid-battle).
- If `kingdomHP` reaches 0 it clamps there and **the run ends**: `endRun('overrun')` records the fall (`kingdomFallRecord` for the HP-panel marker, plus an entry in the persistent `meta.fallHistory`), freezes the game (`tick()` no-ops while `runEnded`), and shows the run-summary overlay with the upgrade shop — see *Run loop implementation (M8)*.

### Heroes
Heroes are recruited separately from townspeople and are **not building-gated** — the squad cap is the battlefield grid, which starts 2x3 (6 slots) and expands via the **War Banners** Military node to 3x4 (12) then 4x4 (16) (`HERO_GRID_BY_RANK` / `heroGridDims()`; `resizeHeroSquad()` re-seats heroes on rank-up and load, and the UI compacts slot size so the panel footprint holds — every rear row is labeled "Backline", matching the mechanics). Targeting is generalized to any number of rows (M10): the frontmost occupied row is "the front", every row behind it is the backline pool.

**Hero archetypes** (`HERO_ARCHETYPES`; an `unlock` field names the Military node that gates pool appearance):

| Archetype | Names by rarity (common→legendary) | Base cost | Role |
|---|---|---|---|
| guardian | Knight / Sentinel / Vanguard / Paragon | 1,000g | **Taunt** tank (35 defense, 140 hp, 8 atk; **guard 3**) |
| fighter | Footman / Sellsword / Blademaster / Warlord | 1,100g | Frontline damage-dealer (18 def, 95 hp, 14 atk @1.0; **guard 1.5**) — base roster (M14.1); pairs with a guardian |
| ranged | Archer / Sharpshooter / Hunter / Marksman | 750g | Fast attacker (5 defense, 60 hp, 18 atk) |
| mender | Acolyte / Cleric / Druid / Saint | 850g | Healer (8 defense, 65 hp, 22 heal — M14.1 buff; was never worth the slot) |
| paladin | Squire / Paladin / Crusader / Highlord | 1,300g | Hybrid — attacks *and* heals on staggered timers (25 def, 120 hp, 9 atk + 9 heal — heal trimmed in M14.1; stacks dominated; **guard 2**); unlock: **Paladin's Oath** |
| assassin | Rogue / Assassin / Nightblade / Phantom | 950g | Backline hunter (`backlineChance` 0.9; 3 def, 45 hp, 26 atk; **guard 0.5 — "slippery"**, drawn half as often within its pool); unlock: **Shadow Guild** |

**The guard spectrum (M14.1):** every unit's `guard` is its targeting-ticket weight within its row pool (unset = 1; shown as "GRD ×N" on unit cards): guardian 3 · paladin/banneret 2 · fighter 1.5 · assassin 0.5. Tanks tank *for* whoever shares their pool, and a guardian stationed in a **rear row bodyguards the backline** — sim-verified as rewarding against marksman tiers (Bandit boss 93%→99%) and punished against front-heavy ones (Undead boss 12%→3%), a genuine matchup-dependent placement decision. The slippery assassin doesn't go degenerate: a full back pool still lands ~6% of its fire on it, and row-AoE breath ignores guard entirely.

Sim-verified M14.1 frontline metagame: guardian+fighter beats double-fighter against the orc enrage tier (74% vs 40% at Orc w6), double-fighter beats double-guardian against bandit/dark heal-walls (94% vs 69% at the Bandit boss) — no front is strictly best, and paladin-stacks are now a specialist choice (win the Bandit-boss race, collapse at Dark) rather than the answer to everything.

A hero costs a meaningful slice of early income (~30–60s of gold at raid-trigger time), so a full 6-slot squad is a real investment — mid-battle emergency rehires compete with everything else the gold could buy. **Hero hire costs scale ×1.4 per raid tier reached** (`HERO_COST_TIER_GROWTH`, M14.1): late-game income dwarfs flat costs, so this keeps a squad rebuild a real purchase (~2–4 min of contemporaneous income) all game. Sim-verified it does *not* move battle outcomes — walls are attrition-bound, not gold-bound — it only restores purchase weight.

`generateHero` scales `attack`/`heal` power by the rarity tier's `incomeMult` and HP by `sqrt(incomeMult)` (same `rarityTiers` table used for townspeople — see *Recruit pool system*). Hero cost scales by the tier's `costMult`.

**Hero rarity bias — Keep's new role:** each Keep owned shifts the hero rarity roll up the `RARITY_WEIGHT_TABLE` as if the kingdom were that many levels higher: `getHeroRarityWeights() = RARITY_WEIGHT_TABLE[kingdomLevel + buildings.keep.count]`. Keep has no residents or slots — owning more of them is purely a hero-rarity investment.

**Hero rarity ceiling — Hall of Legends (added 2026-07-13):** the hero weights are then **clamped to the Hall of Legends rank** (Military tree, 3 ranks, 50/750/5,000 Legacy): rank 0 = Common only, then Rare / Epic / Legendary per rank (`heroRarityCap()`, filtered in `getHeroRarityWeights` — `weightedRarityRoll` renormalizes over what remains). In-run gold can never buy hero rarity past the ceiling; kingdom level and Keeps only improve the odds *under* it. This is the fix for the run-1 min/max break (see *Open questions*): sim-verified walls per ceiling — Common: Orc boss; Rare: Bandit boss/early Undead; Epic: Undead boss; Legendary: deep Infernal, final boss still closed until M10–12 content. Townsperson rarity is deliberately NOT capped (income rarity is harmless once hero power is gated). Veteran's Welcome still grants its free Rare Knight regardless of ceiling (it's Legacy-bought, which is the point).

**Hero recruit pool:** unlocks at `RAID_TRIGGER_LEVEL` (Town, level 2) — the Battle column shows "Unlocks at Town" until then. A pool of `HERO_POOL_SIZE` (base 3, +1 per **Mustering Grounds** rank — the M15 node countering archetype-unlock dilution: 9 unlocked archetypes make a 3-slot pool only a ~30% shot at any specific one per refresh) refreshes every `HERO_POOL_REFRESH_INTERVAL` (15) seconds. Hiring is manual only (no auto-recruit for heroes — placement matters) and requires gold plus an empty squad slot. Firing a hero is free.

**Squad formation:** drag-and-drop a hero portrait onto another slot to swap positions (`swapHeroes`); this works mid-battle. Row 0 = frontline (nearest the gate), row 1 = backline.

**Dismissing heroes:** clicking a hero portrait in the Defenders squad arms it (red highlight, tooltip changes to "Click again to dismiss") for `ARM_TIMEOUT_MS` (3s); a second click within that window fires the hero for free — same free-dismiss pattern as residents, with a misclick guard. **Heroes that die in battle free their squad slot at the moment of death** (`combatTick` nulls any `!alive` slot each tick), so reinforcements can be hired into the ongoing fight even after a full squad wipe. Dead heroes are gone for good; only survivors respawn at full HP for the next battle.

### Workshop & Builders
- Unlocks at Village level (one level before the first raid trigger).
- Residents are **Builders**, rolling 0.3–1.0 Kingdom-HP-regen/sec (×rarity), same hire/fire/reroll mechanic as every other townsperson.
- Builders generate no gold — each Workshop hire is an income sacrifice in exchange for surviving raids longer-term.

## Raid system redesign — autobattler (implemented)

The hero-squad-vs-enemy-squad autobattle described above replaces the old duration/ratio siege system (`totalDefense` vs. a flat `defenseRequired`, `clamp(60/ratio, 10, 180)`). The 3-column "battle at the gates" layout (Admin / Town / Battle) from `layout-prototype.html` is now the live UI in `index.html`. `autobattler-prototype.html` and `layout-prototype.html` remain as standalone references but are no longer the source of truth.

**Remaining open items:**
- ~~Hero squad cap growth~~ — implemented in M10 as the War Banners Military node (see *Heroes*).
- See *Progression loop redesign* and *Difficulty & meta-progression design* for the raid-tier vs. hero-rarity vs. Kingdom-siege balance pass — now an M9 tuning job (the run loop and currency flow landed in M8).

## Progression loop redesign — end-to-end storyboard (core run loop implemented in M8; wave/boss structure, new content, and tuning pending M9+)

The original full-idle "always growing" framing (Adventure Capitalist/Realm Grinder style) is replaced by a death-and-rebuild loop closer to Gnorp Apologue / Wizard and Minion / Scritchy Scratchy: each run ends when the Kingdom falls, and that run's combat progress funds permanent upgrades that make the next run faster and stronger. The kingdom's economy now exists to fuel the battle, not as the end goal itself.

**Target shape: 8–10 runs ("Ages"), ~20–40 minutes each, ~5 hours total**, ending in a winnable Final Siege (see below). Numbers below are placeholders pending playtesting.

### The run loop
1. Start at Hamlet with starting gold, full Kingdom HP. **Every run starts here** — there is no persistent tier-ratchet that skips a run ahead in raid tiers.
2. Build economy, level up the kingdom, reach Town level → Goblin Raid begins.
3. Clear raid waves; defeating a tier's boss wave advances immediately to the next tier's wave 1 (Goblin Raid → Orc Warband → Bandit Horde → Undead Legion → Infernal Siege). Every **newly reached** wave cleared banks currency (see below).
4. Eventually `kingdomHP` reaches 0 — the run ends ("Found a New Age" reset). Gold, buildings, residents, heroes, kingdom level, and raid tier/wave all reset to start-of-run state. (QoL: a manual "Found a New Age" button is also available once raids have begun — for when a run's frontier attempts are spent and waiting out the kingdom's actual fall would just waste time.)
5. Currency banked this run is spent on the Economy and Military upgrade trees (permanent, persists across resets).
6. Next run repeats from step 1, but upgrades mean earlier tiers clear much faster, so playtime concentrates near whatever tier is currently the frontier.

The upgrade trees **are** the ratchet — there's no separate "tier unlock" flag. A heavily-upgraded player still technically starts at Goblin Raid wave 1 each run, but blows through it in seconds.

### Wave & boss structure per raid tier
- **Implemented in M9.** Each raid tier has a fixed wave count ending in its boss: Goblin 5, Orc 8, Bandit 11, Undead 14, Infernal 17 (`waveCount` per tier — see the raid-tier table under *Invasion & combat system*).
- A **boss wave** is the tier's named boss (Goblin Warmaster, Orc Warlord, Bandit King, Lich Commander, Demon Empress — a scaled-up brute, ×1.8 power ×4 HP) plus an honor guard of roster minions. Unique per-boss abilities are M11.
- Clearing a tier's boss wave immediately advances to the next tier's wave 1 (wave counter and streak reset — boss-kill is the only tier-advance trigger; kingdom level plays no part).
- **A wave repeats until beaten** (locked in, implemented in M8): the ladder only climbs on wins — `winInvasion` is the only place the wave advances, and it only runs when the enemy squad is wiped.
- Bosses need no special rule — like any wave they repeat until killed, and killing one is what advances the tier. They're still the natural per-run walls because their stat block spikes above the tier's normal waves.
- A wall wave resolves as an **escalating last stand**: reinforcement hires inside the one ongoing battle are the "attempts", and siege escalation guarantees the battle ends — Repelled if the wall cracks under the grind, Overrun (Age over) if it doesn't. Sim-checked with the grind model: money can push roughly one wave past a squad's honest wall, not tiers (pre-escalation, the 2026-07-17 playtest ground from the predicted Orc-boss wall all the way to Bandit w3).
- **Wave composition varies within a tier**: squads fill more of the grid as waves climb (4 units early → full grid at the boss), with varied mixes (double-brute wave, skirmisher swarm, twin-healer wave). Waves feel distinct, and AoE / target-priority tools have something to answer.

### Enemy & hero grid expansion
- The **enemy grid auto-expands** at tier transitions (implemented M11): Goblin/Orc 2x3, Bandit/Undead 3x4, Infernal 4x4 (`tier.grid`).
- The **hero grid does not auto-expand** — squad size growth is the War Banners Military node (implemented M10: 2x3 → 3x4 → 4x4), timed to land roughly alongside the enemy-grid jumps. This makes "I'm suddenly outnumbered, I need more squad slots" a concrete, must-buy upgrade rather than a passive bonus.

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
| 5 | Bandit boss (w11) / Undead w1–3 | **Battlemage (AoE)**, start at Village |
| 6 | Undead wave 7–10 | **Banneret (buffer)**, second squad expansion |
| 7 | Undead boss (w14) / Infernal w2–4 | **Cathedral doctrine (revive)**, hero power III |
| 8 | Infernal wave 9–13 | Remaining doctrines, Frost Adept |
| 9 | Infernal boss (w17) → first Final Siege attempt (expected loss) | Last power ranks |
| 10 | **Final Siege — victory** | — |

### Scaling & tuning targets — implemented in M9
- **Continuous curve across tier transitions** (implemented): each tier's `powerMult` = the previous tier's boss-wave multiplier (1.0 / 1.52 / 3.0 / 7.6 / 24.7), `defenseGrowth = 1.088`/wave everywhere. The final boss lands at ~95× goblin wave 1 (target was 80–100×), with the boss unit's own ×1.8/×4 on top. No stat cliffs — the old tier-5-wave-7 spike class of problem is gone by construction.
- Raid pacing (implemented): per-tier `raidInterval` — 45s at Goblin/Orc tightening to 30s at Infernal — plus a 75s grace before the first raid ever.
- Sim-measured expectations (`tools/balance-sim.js`, M14 campaign-arc check — the "wall" is the first wave under a 50% win rate for each run's arc-expected squad): run 1 walls Orc w5; run 2 Orc boss; run 3 Bandit w7; runs 4–6 run roughly half a tier deep of their targets (the 12-slot expansion is strong — War Banners rank 1 priced to 4,000 to delay it); runs 7–9 converge on target (Infernal w8 / w15 / w15-boss); the Final Siege gauntlet lands at ~27–38% for the full endgame kit and 0% without doctrines. Net: the campaign completes in ~8 runs of optimal play, 9–10 realistic — slightly compressed vs the table but the right shape. **The user's real 1× acceptance playtest is the final calibration gate.**
- **M14.1 arc re-verification** (after taunt / fighter / mender-paladin rebalance / tier-scaled hero costs): walls land run-for-run on the M14 baseline (Orc w7 / Orc boss / Bandit w7 / Undead w7 / Undead w13 / Undead boss / Infernal w6 / w15 / w15), gauntlet 28% with the full kit and ~0% without doctrines, fair-fight medians all under the escalation grace, grind table unchanged (money still can't buy tiers). Same difficulty shape as the accepted playtest, now with the composition metagame underneath. The user's actual runs 1–5 fell ½–1 tier deeper than the arc targets — declared **acceptable variance**, not a tuning bug: Legacy-spend choices are supposed to swing run depth; the table is a script, not a contract.

### Victory condition — the Final Siege (implemented in M13)
After the Infernal Siege boss (wave 17) falls **for the first time in the campaign**, a herald announces the **Final Siege** arrives in `FINAL_SIEGE_COUNTDOWN_RAIDS` (3) raids' time (status bar shows the countdown; the interim raids are ordinary post-boss waves — compositions clamp to the tier's last non-boss mix while stats keep scaling). Then the **3-phase gauntlet** (`FINAL_SIEGE_PHASES`, one invasion with `finalSiege: true`): **The Vanguard** (wave-14 stats, 10 units) → **The Elite Guard** (wave-16, 9) → **The Empress Ascendant** (wave-18, the boss + guard). Heroes do **not** reset HP between phases (menders/Blessing showcase; Blessing fires once per gauntlet), the **escalation clock resets each phase**, and Kingdom HP is the buffer that carries a partial wipe across phases. Phase waves sim-tuned: the endgame squad (16 legendaries + Realm doctrines) wins ~38%/attempt; without doctrines 0% — run 9 loses, run 10 wins, per the arc.
- **Loss**: counts as a Kingdom fall, but grants the one-time **Lessons of the Last Siege** bonus (`LESSONS_LEGACY` 25,000, `meta.lessonsGranted`) shown on the run summary — the failed attempt visibly funds the winning one.
- **Win**: `campaignVictory()` — `meta.victory` persists, the world freezes on the victory screen ("The Kingdom Stands Eternal"): Ages founded, lifetime Legacy, total kingdom time (`meta.gameSeconds`), and the fall-history list of every Age that came before.

### Endless mode (implemented in M13)
After victory, "Rule in Peace — Endless Mode" resumes the current run: raids keep climbing indefinitely (post-boss waves reuse the tier's last non-boss composition with ever-scaling stats), and Found a New Age still works for fresh runs. `meta.victory` persists; there is never a second Final Siege (the herald requires `!meta.victory`).

### Currency (name TBD; shown in-game as "Legacy")
- **First-ever-clear credit (locked in, implemented):** each wave on each tier's ladder pays out full value the first time it is cleared *across the whole campaign* — `meta.waveCredit[tierIndex]` is the per-tier "waves credited" high-water mark, persisted with meta state (`bankWaveLegacy` in `game.js`). Pushing past the all-time frontier is the primary way to earn meta currency.
- **Repeat-clear trickle (locked in, implemented):** re-clearing an already-credited wave pays `REPEAT_LEGACY_FRACTION = 0.15` of its first-clear value (min 1) so no run banks literally zero. Restart-farming stays pointless — the trickle on cheap early waves is negligible next to frontier pushes at 5x/tier values.
- Per-wave value scales **5x per raid tier**: `WAVE_LEGACY_VALUES = [10, 50, 250, 1250, 6250]` (Goblin → Infernal, flat within a tier for now). Boss waves pay **×4** (`BOSS_LEGACY_MULT`) as the "breakthrough" bonus (implemented in M9). First-clear campaign total ≈ 150k Legacy; the current 9-node tree costs ~19k, leaving deliberate headroom for the big-ticket M10–12 nodes (squad expansions, archetype unlocks, doctrines).
- Legacy is banked **at wave-clear time** (not at run end), so a mid-run quit or crash loses nothing.
- Currency persists across resets and is spent on the two upgrade trees below. The old gold-`goldEarned`-based formula (`floor(sqrt(goldEarned/100000))`) and the automatic "+5% income / +5% hero power per point" effect are both superseded by this.
- Possible future Economy-tree QoL: a "start at wave N" skip upgrade to shorten the retread on later runs (open to it, not yet designed).
- **Pricing philosophy:** total tree cost ≈ slightly under expected lifetime earnings across the 8–10 run arc, with the Final Siege realistically beatable at ~⅔ of the trees purchased — full completion is for thoroughness, not a requirement.

### Upgrade trees (Economy / Military)
Two permanent, currency-funded trees spent into after each reset. Full planned scope:

- **Economy tree** — income multipliers (global or per-building), starting gold, "Old Foundations" (start runs at Village level), building cost-growth reduction, building cap increases beyond kingdom-level grants, Builder Kingdom-HP-regen multiplier, recruit-pool quality-of-life (refresh speed, rarity weights, pool size, reroll button), **townsperson auto-buy** (implemented M10 as **Steward's Ledger** — "QoL as upgrades", the incremental-genre pattern of an interactive mechanic earning its own automation; always-available in dev builds via `DEV_MODE`), **Doctrines** (below).
- **Military tree** — **Hall of Legends** (the hero rarity ceiling — implemented, see *Hero rarity ceiling* under *Heroes*), hero stat multipliers (HP/attack/defense/heal, ranked, global or per-archetype), **hero squad-size expansion milestones** (the must-buy nodes tied to enemy-grid jumps), **new hero archetype unlocks** (below), "Veteran's Welcome" (start each run with a free rare Knight), cheaper hero hires, hero recruit-pool quality-of-life, Kingdom HP max / Kingdom defense ("Walls") / base HP regen, a scout report (see the next raid's composition).

**M8 starter set (implemented, `UPGRADE_TREES` in `game.js` — all numbers placeholder pending M9):**

| Tree | Node | Effect per rank | Ranks | Costs (Legacy, M14 rescale) |
|---|---|---|---|---|
| Military | Hall of Legends | unlocks Rare / Epic / Legendary heroes in the pool (the run-depth gate — see *Hero rarity ceiling*) | 3 | 50 / 750 / 6,000 |
| Military | Paladin's Oath (M10) | unlocks the Paladin archetype | 1 | 250 |
| Military | Shadow Guild (M10) | unlocks the Assassin archetype | 1 | 400 |
| Military | War Banners (M10) | hero squad 2x3 → 3x4 → 4x4 | 2 | 4,000 / 30,000 |
| Military | War Magics (M11) | unlocks the Battlemage archetype | 1 | 800 |
| Military | Rimecraft (M11) | unlocks the Frost Adept archetype | 1 | 1,200 |
| Military | Standard Bearers (M11) | unlocks the Banneret archetype | 1 | 1,500 |
| Economy | Steward's Ledger (M10) | unlocks townsfolk auto-hire (always-on in dev builds via `DEV_MODE`) | 1 | 150 |
| Economy | Swift Seasons (2026-07-17) | unlocks the game speed selector — 1× / 2× / 4× (always-on in dev builds; 10×/50×/100× stay dev-only). Pure wall-clock QoL: the engine runs on game-seconds, so speed never touches balance (no sim change needed) | 1 | 300 |
| Economy | Smithy Forgework (M12) | +1.5% hero attack per Smithy owned | 1 | 2,000 |
| Economy | Library Tactics (M12) | +1% hero action speed per Library owned | 1 | 3,000 |
| Economy | Apothecary Salves (M12) | heroes regen 0.3% HP/s per Apothecary in battle | 1 | 6,000 |
| Economy | Cathedral Blessing (M12) | first fallen hero each battle revives at 30% (needs a Cathedral) | 1 | 10,000 |
| Economy | Prosperous Trade | +25% gold income | 5 | 15 / 60 / 250 / 1,000 / 6,000 |
| Economy | Royal Treasury | starting gold 75 → 250 / 1,000 / 4,000 / 15,000 | 4 | 10 / 40 / 150 / 500 |
| Economy | Master Builders | +50% Builder HP regen | 3 | 25 / 100 / 400 |
| Economy | Old Foundations | new Ages begin at Village | 1 | 400 |
| Military | Weapon Drills | +20% hero attack & healing | 5 | 15 / 60 / 250 / 1,000 / 6,000 |
| Military | Hardened Armor | +20% hero HP | 5 | 15 / 60 / 250 / 1,000 / 6,000 |
| Military | Muster Rolls | hero hiring −15% (multiplicative) | 3 | 20 / 80 / 300 |
| Military | Mustering Grounds (M15) | +1 hero per recruit-pool refresh (4, then 5) — counters archetype-unlock pool dilution | 2 | 300 / 900 |
| Military | Reinforced Walls | +250 max Kingdom HP and +3 Kingdom defense | 4 | 15 / 60 / 250 / 1,000 |
| Military | Veteran's Welcome | free Rare Knight each new Age | 1 | 100 |

**M14 pricing math:** total trees ≈ 90k Legacy; the Final-Siege-winning kit (Hall of Legends, War Banners, power ranks, doctrines) ≈ 60k ≈ ⅔ of total, per the pricing philosophy. First-clear campaign budget ≈ 150k + countdown waves + the 25k Lessons bonus.

Effects route through helper functions (`econIncomeMult`, `heroPowerMult`, `getKingdomHpMax`, etc.) so later nodes slot in without special-casing. Squad expansion, archetype unlocks, doctrines, and pool QoL arrive in M10–M12.

### Doctrines — building↔army synergy nodes (Economy tree) — implemented in M12
Each doctrine makes a building type directly feed the army, so town composition stays a battle decision all game and the Economy tree keeps late-game relevance. Keep's hero-rarity bias is the template. All are **live multipliers computed at use time** through the M11 modifier layer — they apply to already-hired heroes and track building purchases mid-run:
- **Smithy Forgework** (2,000 Legacy) — +1.5% hero attack per Smithy owned (`doctrineAttackMult` in `effectiveAttackPower`)
- **Library Tactics** (3,000 Legacy) — +1% hero action speed per Library owned (`doctrineSpeedMult` in `effectiveActionInterval`; speeds attacks *and* heals)
- **Apothecary Salves** (5,000 Legacy) — heroes regenerate 0.3% max HP/s per Apothecary during battle (`doctrineSalvesRegen` in `combatTick`)
- **Cathedral Blessing** (8,000 Legacy) — the first hero to fall each battle revives at 30% HP; requires owning a Cathedral (`blessingAvailable` via the `onUnitDeath` hook; `blessingUsed` flag lives on `currentInvasion` so it resets each battle)

Sim-verified endgame role: 16 legendaries ×2.0 tree score **2%** on the Demon Empress without doctrines, **25%** with Realm-level doctrines — the doctrine family is what opens the final boss (the Final Siege then lands in M13 as the true finale).

### New hero archetypes (Military-tree unlocks, ~one per run for novelty)
Sequenced so the zero-engine-work heroes arrive first:

| Hero | Role | Engine work needed | Status |
|---|---|---|---|
| Paladin | attack + heal hybrid | **none** — the multi-action system already supports it | **implemented (M10)** |
| Assassin | backlineChance ~0.9, high power, fragile | none — just stats | **implemented (M10)** |
| Battlemage | hits an entire enemy row (at the 0.65 AoE discount) | AoE action type | **implemented (M11)** — unlock: War Magics, 800 Legacy |
| Banneret | aura: adjacent allies +15% attack/heal power | buff system | **implemented (M11)** — unlock: Standard Bearers, 1,500 Legacy |
| Frost Adept | attacks chill the target (cooldowns ×1.35 for 6s) | debuff-on-hit | **implemented (M11)** — unlock: Rimecraft, 1,200 Legacy |

M11 hero stat blocks: Battlemage (Adept/Battlemage/Warmage/Archmage, 1,600g, 8 def / 70 hp / 12 atk row-AoE @0.8), Banneret (Herald/Banneret/Marshal/High Marshal, 1,500g, 25 def / 110 hp / 6 atk @0.6 + adjacency aura + guard 2), Frost Adept (Frost Apprentice/Frost Adept/Rimecaller/Winter's Voice, 1,400g, 6 def / 65 hp / 10 atk @1.0 + chill). Auras and chill are fixed effects — rarity scales the unit's own stats only.

### Enemy tier mechanics (one tactical lesson per tier) — implemented in M11
Later tiers are new problems, not just bigger numbers — each reuses an engine feature from the hero list (see the raid-tier table for the trait wiring):
- **Goblins** — vanilla; teaches the basics.
- **Orcs** — brutes *enrage* below 50% HP (×1.5 attack speed); teaches burst-vs-tank priority.
- **Bandits** — marksmen hunt the backline (`backlineChance` 0.7); medics out-heal unfocused damage. Teaches protecting menders and the Assassin's job.
- **Undead Legion** — necromancers revive a fallen ally once at 50% HP (on-death hook, consumes a charge, only while the necromancer stands); teaches kill order.
- **Demons** — flamecaller hellfire scours a whole row (AoE at the 0.65 discount); teaches formation splitting.
- **Bosses** — each tier's boss carries a signature trait (war-cry aura / hard enrage / backline mark / double revive / breath+enrage — see the raid-tier table); the Final Siege boss adds phases (M13).
- **Sappers (implemented M11):** the `sapper` archetype (`targetsKingdom`) attacks the Kingdom while heroes stand — each hit has a 25% chance to **injure** a random staffed resident for 90 game-seconds (income/regen paused, ✚ portrait, auto-recovers; never killed). Debuts with the Bandit Horde (w4) and recurs through Undead/Infernal compositions. Gives Builders a live role in every fight; anti-stall is escalation's job.

### Gold & loot rebalance (single-currency decision, locked in)
The in-run economy stays **gold-only** — no separate combat currency for hero hiring. For that to work, **raid gold loot must shrink drastically**: current values (200,000g for a goblin raid vs. a 2,500g Smithy) let one raid win pay for the entire midgame, collapsing the "town fuels the army" loop into "raids fund everything". Target: a raid win pays roughly **1–2 minutes of contemporaneous resident income**. The win-streak multiplier stays, on the much smaller base.

### Open questions
- [x] **Run-1 min/max break (found in the 2026-07-13 playtest — FIXED same day):** a player who
  min/maxed in-run resources cleared the entire 38-wave ladder in Age 1 with **zero Legacy upgrades**
  (fell only at Infernal Siege, Realm level; conditions: mostly 10× dev speed, dev auto-buy at
  rare+/epic+). Root cause: hero rarity — worth ~1.5 raid tiers per step, ~4.5 tiers
  common→legendary — was gated only by kingdom level + Keeps, i.e. by gold, and **stalling is free**
  (waves repeat until beaten, income never throttles, Builders out-regen wall-attempt attrition), so
  patient play bought Empire + Keeps and fielded 6 legendaries within run 1 (sim: 6 no-tree
  legendaries beat the Undead boss ~45%/attempt). The trees (×1.2–2.0) were dwarfed by in-run rarity
  (×10). **Fix implemented: the Hall of Legends hero rarity ceiling** (see *Heroes*) — epic/legendary
  hero access is now a Military-tree meta-unlock. The complementary "make stalling itself cost
  something" lever landed in M9.6 as **siege escalation** (the 2026-07-17 playtest showed in-battle
  stalling was still free — see *Kingdom HP interplay*); sapper-type enemies remain a possible M11
  flavor mechanic but are no longer load-bearing for anti-stall.
- [x] **New-save softlock (found in the 2026-07-17 acceptance playtest — FIXED same day):** with
  50 starting gold, buying all 3 Hamlet cottages (39g total — a single click in ×max buy mode)
  left 11g against the 25g Villager hire with zero income and no other gold faucet — a hard
  self-inflicted softlock whose only exit was the meta-wiping dev reset ("Found a New Age" is
  gated on `raidsStarted`, deliberately kept that way). **Fix: starting gold 50 → 75**
  (`STARTING_GOLD_BY_TREASURY_RANK[0]`; sim mirror updated, arc re-verified unchanged), so
  max-greedy building still leaves the first hire affordable; `loadGame()` now also applies
  `getStartingGold()` on fresh boots so a no-save start honors Royal Treasury. Related teaching
  ideas (free Villager with the first Cottage; rename/relocate the "Found a New Age" button —
  "found" as a verb doesn't read on first sight) deferred to the tutorialization pass (see
  *Ideas under consideration*).
- [ ] Exact tier transitions where the enemy grid expands, and where the matching hero squad-expansion milestones sit in the Military tree.
- [x] **Hero grid expansion shape / do rows survive at all (raised in the 2026-07-17 playtest — RESOLVED same day):** War Banners growth (2x3 → 3x4 → 4x4) only ever adds *rear* rows, which prompted "with taunt as a per-unit lever, do we need front/back targeting at all?" Analysis said keep rows — they still carry (1) the hunter identity (`backlineChance` is the whole mechanical identity of assassins/marksmen and two tier lessons); (2) protection that scales with bodies not stats (the front soaks ~85% at any squad size; flat guard-weighted targeting would dilute to ~30% tank-soak at 16 slots); (3) breath-AoE/aura/enemy comps are authored in rows; (4) legibility. Decisions: **rows stay**; **the guard spectrum shipped** (see *Heroes*); the misleading "Reserve" label is gone — **every rear row is labeled "Backline"**, since that's what it mechanically is (user's call: rear-adds-backline is thematically fine — armies have more backline than frontline). Parked for later, only if formation still feels shallow post-M15: the **lane/intercept model** (a guard unit protects whoever stands behind it in its column; hunters flank) — maximally legible and makes expansion slots protectable seats, but rebalances every fight and every enemy comp, so post-campaign scope. True-reserve bench likewise parked (big balance lever: "all 16 fight" is part of why expanded squads overshoot).
- [ ] **War Banners budgeting feel** (playtest): saving for squad expansion against Hall of Legends ranks felt hard to plan. Partially intended (M14 priced rank 1 at 4,000 to delay the strong 12-slot jump) — revisit after the M14.1 hero-economy changes settle in play.
- [ ] Boss unit stat blocks and any per-boss unique abilities beyond the tier gimmick.
- [x] UI for the run-end/reset summary screen and the two upgrade trees — implemented in M8 as a full-screen overlay (see *Run loop implementation (M8)*).

### Ideas under consideration (raised 2026-07-13)
- **Tutorialization pass (candidate M16, after visuals/sound; raised 2026-07-17):** guided first
  steps for a new save — e.g. the first Cottage comes with a free Villager as the teaching hook
  ("you bought a cottage, villagers live here, find more in the Town Square"); also rename and
  relocate the "Found a New Age" button ("found" as a verb isn't intuitively understood on first
  read). **Stat-abbreviation legibility (added 2026-07-17):** hover tooltips on unit-card stat
  lines (ATK / HLR / DEF / GRD) — GRD especially ("Guard: draws ×N of the targeting weight in
  its row"); even the developer didn't associate "GRD" with guard when re-reading it, so the
  abbreviation demonstrably doesn't carry the mechanic.
- **Raise the default game speed? (raised 2026-07-17):** after test runs, 1× felt really low to
  the developer. First response shipped same day: the **Swift Seasons** Economy node (300 Legacy)
  unlocks a player-facing 1×/2×/4× selector, dev speeds unchanged. Still undecided: whether the
  *default* (pre-upgrade) speed should also rise — note the ~5-hour campaign arc and all
  playtest-calibrated pacing assume 1×, so a default bump is a real pacing decision, not pure QoL.
- **"Lock" a hero recruit (playtest 2026-07-17):** pin a pool recruit so it survives refreshes,
  hire when affordable. User worried it's too strong; assessment: healthy as a Legacy QoL node,
  especially now that hero costs scale by tier (locking becomes the pressure valve that makes
  saving for an expensive recruit feel fair). Candidate Military-tree node.
- **Doctrine presentation redesign (playtest 2026-07-17):** the per-building percentages read as
  tiny against their Legacy prices even though the family is sim-decisive (opens the final boss).
  M14.1 rewrote the shop copy to name the aggregate ("a full forge district: +10.5%"); the bigger
  candidate redesign is chunkier threshold framing ("while you own 3+ Smithies…") or showing the
  player's live computed bonus in the card. Revisit alongside M15/M16.
- **The kingdom & villagers as rare combat targets — IMPLEMENTED in M11** as the sapper enemy
  mechanic; see *Enemy tier mechanics*.
- **Kingdom-prosperity visuals per tier (stretch, raised 2026-07-18):** in the M15 scene
  layout, the town half visibly prospers as kingdom tiers are reached. Cheapest-first
  ladder recorded in M15_SCOPE.md (T4): tier-gated decoration sprites → CSS grading +
  plaza crowd density → edited-in-place backdrop variants (never regenerated — geometry
  drift breaks the fixed building anchors). Note the T3 building layer itself already
  delivers most of the progression fantasy, and tier-keyed decorations resetting each Age
  strengthens the New-Age bare-ground beat for free.
- **Per-building interactive minigames that automate later:** the classic incremental arc — each
  building has a small active mechanic (e.g. assemble horseshoes at the Smithy for a productivity
  boost) that an upgrade later automates at equal-or-better efficiency. (The auto-buy Economy node
  above is the first, already-decided instance of this "QoL as upgrades" pattern.) Risk: splits focus from the
  battle at the gates, and is a large content lift (one designed minigame per building) — if pursued,
  likely post-M14 scope, possibly starting with a single building as a pilot.

## Difficulty & meta-progression design — to-do

Playtesting at 100x surfaced a hard difficulty wall: an all-legendary hero squad was wiped and the Kingdom (1000 HP) was drained in ~5 seconds around Infernal Siege Wave 7 (`kingdomFallRecord` tracks the latest failure point for this kind of test). The *Progression loop redesign* section above now answers most of the structural questions this raised; remaining items are tuning/implementation details within that structure:

- [x] **What does the difficulty curve represent?** Decided: within a single run, the curve is *meant* to eventually become unwinnable — that's what triggers the reset (see *Progression loop redesign*). Across runs, the Economy/Military trees push that ceiling further out, so progress is measured run-over-run, not within one run.
- [x] **What triggers the first forced reset?** `kingdomHP` reaching 0 — wired up in M8: `tick()` short-circuits into `endRun('overrun')`, which freezes the game and opens the run-summary/upgrade-shop overlay. See *Run loop implementation (M8)*.
- [x] **Re-tune the raid-tier curve** — done in M9 via `tools/balance-sim.js` (continuous 1.088/wave growth, no tier cliffs, final boss ≈ 95× goblin wave 1, economy shrink, loot cut). `KINGDOM_DEFENSE`/`KINGDOM_HP_MAX`/Builder regen kept as-is for now; final calibration against real playtests is M14.
- [x] **Design meta-progression between resets** — see *Progression loop redesign*: currency earned from in-run wave/boss progress, spent on Economy and Military trees.
- [x] **What does completing the game look like?** Decided: the **Final Siege** 3-phase gauntlet after the Infernal Siege boss is the victory condition; endless mode unlocks after victory. See *Progression loop redesign*.
- [ ] **Hero permadeath economics:** dead heroes are auto-fired (gone for good, see *Heroes & combat*); rebuilding the squad after a rough raid costs real gold/time within a run. Does this need its own lever (cheaper recruits at low kingdom levels, a "veteran" bonus, etc.), or does the run-restart-from-Hamlet structure make this moot since squads rebuild from scratch each run anyway?

## Run loop implementation (M8)

How the death-and-rebuild loop from *Progression loop redesign* is wired in `game.js`:

- **Two-key save model:** run state stays in `idleKingdomSave`; everything that survives a reset lives in `meta` (localStorage key `idleKingdomMeta`, `META_SAVE_KEY`): `age` counter, `legacy` balance, `waveCredit` high-water marks, `upgrades` ranks, and `fallHistory` (one entry per ended Age: age, fall wave, kingdom level, waves cleared, Legacy earned). The dev "Reset game" button wipes **both** keys — it's the full debug wipe, distinct from the in-fiction Age reset.
- **Save versioning (M9):** both saves carry `version: SAVE_VERSION`; a mismatch on load discards the save (fresh start). Bump `SAVE_VERSION` whenever a rebalance makes old saves meaningless. Currently **5** (M14 rebalance).
- **Run end:** `endRun(reason)` — `'overrun'` from `tick()` when `kingdomHP` hits 0 mid-battle, `'abandoned'` from the manual left-panel "Found a New Age" button (visible once raids have begun, two-click confirm). Either way: fall recorded, `runEnded = true` (the whole game freezes — `tick()` no-ops), and the full-screen run-summary overlay opens showing Age number, fall point, waves repelled, Legacy earned/available, both upgrade trees with Buy buttons, and the "Found a New Age" button. Closing the browser mid-summary is safe: `runEnded`/`runSummary` are saved, so the overlay reopens on load.
- **The reset:** `foundNewAge()` increments `meta.age` and rebuilds run state: gold = `getStartingGold()` (Royal Treasury), kingdom level = Hamlet (or Village with Old Foundations), Kingdom HP = `getKingdomHpMax()` (Reinforced Walls), buildings back to zero at base costs (`BUILDING_BASE_COSTS`), residents/heroes/pools cleared, raid tier/wave/streak zeroed, free Rare Knight placed if Veteran's Welcome is owned. Upgrades are bought *on* the summary screen, so purchases there apply to the very next Age.
- **What resets:** gold, `goldEarned`, buildings, residents, heroes, kingdom level, raid tier/wave/streak, Kingdom HP.
- **What persists:** Legacy, tree purchases, `waveCredit`, `fallHistory`, auto-recruit setting, game speed (clamped on load via `allowedSpeeds()` to what the build + Swift Seasons permit — a saved 4× without the node, or a dev speed in a release build, falls back to 1×), and the M13 campaign flags: `meta.victory` (endless-mode unlock), `meta.lessonsGranted`, `meta.gameSeconds` (lifetime game-time).
- The **Legacy balance** shows as a third resource line in the admin panel; the left panel shows "Kingdom · Age N".

(The original prestige design — Legacy Points from lifetime `goldEarned`, manual prestige at Realm level, automatic +5%/point bonuses — is fully superseded by the above.)

## Game feel pass — visuals & sound (M15)

**Status (2026-07-17): scoped and art-direction decided — see `M15_SCOPE.md` (phases, tiers,
asset policy) and `M15_ART_PILOT.md` (Gemini workflow + passed 4-asset pilot).** Art is
Gemini-generated pixel art, user-in-the-loop: Claude writes per-asset prompts, the developer
generates (style-anchored to `assets/raw/raw_hero_knight_v3.png`), Claude post-processes via
browser-canvas tools (`tools/process-art.html`, `tools/pilot-scene.html` — magenta keying,
trim, foot-anchor computation for slot seating). Provenance logged in `assets/CREDITS.md`.

**Rationale (added 2026-07-17):** M14 ends with a working gameplay arc and tuned mechanics — but
that's a working *simulation*, not a working *game*. The incremental/autobattler genre lives on
feedback: the game isn't done until it feels good to play. M15 is the dedicated juice pass.

**Guiding principle:** every player action and every important game event gets an immediate,
legible, satisfying response. Juice is information delivery, not decoration — a hit you can see
and hear is a hit the player understands.

**The mockup is the destination (developer, re-affirmed 2026-07-17):** M15's visual end state
is a **complete overhaul** matching the developer's one-scene Gemini mockup (town vista → wall
→ battlefield as the primary presentation). Replacing letter portraits with sprites inside the
current panel layout is pipeline scaffolding along the way, never the end state. The T1→T2→T3
art tiers in `M15_SCOPE.md` are all committed scope — a build sequence, not a wishlist.

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

### Render architecture (M15 Phase 0 — implemented 2026-07-17; the old perf debt is PAID)
`tick()` is pure simulation; nothing in the tick path touches the DOM. (Saves are wall-clock
throttled to 1/sec inside tick; endRun/purchases/level-ups still save explicitly.) All painting
happens in a `requestAnimationFrame` loop (`renderFrame` → `renderAll`, capped at
`RENDER_INTERVAL_MS` 66ms ≈ 15fps), so render cost is independent of dev speed — measured in
the Phase 0 verification: **100× dev speed runs at a true 100× effective** (was 5–8×; a sim
tick costs ~0.02ms). The mechanisms:
- **Memoized panels** (`setPanelHtml`): innerHTML only touches the DOM when the freshly built
  string differs from the last one.
- **Volatile/structure split (2026-07-17, click-eating fix):** memoized panel strings must
  contain NO per-second-changing values — countdown timers, live cost labels, gold-driven
  disabled states all live in fixed child elements that `refreshVolatileUI()` (formerly
  `refreshAffordability`) updates in place at the end of every `renderAll`. Baking a ticking
  value into a panel string forced a full innerHTML rebuild every game-second, which destroyed
  buttons mid-click (unreliable at 1×, near-unclickable at 4×+) and reset hover states. Panels
  now rebuild only on real structural change (pool refresh, hire, purchase, state flip).
- **Delegated UI actions (same fix):** generated panels use `data-action="name:arg"` instead
  of inline `onclick`; two document-level pointer listeners (`bindActionDispatch`,
  `UI_ACTIONS` registry) dispatch by **action string**, so a press survives even a rebuild
  that replaces the button between pointerdown and pointerup. Identity is in the string
  (recruit/hero ids are forever-unique counters), so a pool refresh mid-click mismatches and
  safely drops the press instead of firing on the replacement. Keyboard activation still works
  via a click fallback (with single-shot suppression of the pointer-path's trailing click).
  Human-verified at 100× dev speed (2026-07-17): every click landed; this never worked before.
- **Persistent battle slots**: `renderSquad` = `squadSignature` (grid shape + per-slot unit
  identity via `unit._domKey`) → `buildSquad` rebuilds structure only when the signature
  changes → `updateSquad` updates HP widths/text/classes in place every frame. Persistent
  elements are what let CSS animations survive across frames — the prerequisite for all M15
  juice. Slot click handlers read armed-state at click time (they outlive the render pass
  that created them); drag handlers attach once per structure build.
- **FX bus** (`emitFx`/`drainFx`): combat emits typed events (`hit`/`heal`/`kingdomHit` — from
  `resolveAttack`/`resolveHeal`/`attackKingdom`); the queue drains once per rendered frame,
  coalescing damage/heal per unit and capping concurrent floats (`FX_MAX_FLOATS_PER_SLOT`),
  so 100× speed produces 1× on-screen effect density. First consumers are live: floating
  damage/heal numbers, hit/heal slot flashes, kingdom-hit flash (`.fx-*` rules at the end of
  `style.css`, with a `prefers-reduced-motion` guard). Death/revive events are Phase 1 scope.
- `updateUI()` survives as the universal "repaint now" entry point for event handlers — an
  immediate full pass is cheap now that everything is memoized.
- **Runtime sprite pipeline** (M15, same day): `loadSprites()` at boot reads the RAW Gemini
  PNGs from `assets/raw/` (`SPRITE_SOURCES` maps all 47 keys → spec filenames) and processes
  each in memory — magenta keying, trim, foot-anchor, downscale to 160px — into `blob:`
  object URLs in `sprites{}`. Missing file = letter-portrait fallback per key, so art drops
  are "copy PNG in, refresh"; no build step, no duplicate processed assets. Consumers:
  `portraitInner()` (recruit cards, resident grids, hero pool) and battle slots
  (`unitSpriteKey()` — heroes via `archetypeKey`, enemies via `spriteKey` set in
  `generateEnemy` from the tier's `key` field; corner background, provisional pending the T2
  diorama). Requires http serving (canvas is tainted on file://; loader degrades cleanly).
  Two robustness mechanisms (2026-07-19, for Gemini generation misses): **`SPRITE_FLIP`** —
  keys listed in this set are mirrored in memory before keying/trim/anchor (for sprites
  generated facing the wrong way; user-approved after a side-by-side showed the upper-left
  lighting inversion doesn't read at game scale — regenerate only if a specific flipped
  sprite bothers in play); and a **self-calibrating keyer** — `keyMagentaPixels(p, w, h)`
  samples the four image corners and, when all four agree on one flat color, also keys
  pixels near that color, so off-spec flat backgrounds (e.g. a too-blue purple) key
  automatically. Magenta behavior is unchanged; a gradient/vignetted background defeats
  corner agreement and still needs regeneration.

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
- [x] Milestone 10: **First new heroes** (wild/m10-m14 branch) — Paladin + Assassin archetypes behind Paladin's Oath / Shadow Guild Military nodes (pool filters by `unlockedHeroArchetypes()`); War Banners squad expansion (2x3 → 3x4 → 4x4, `resizeHeroSquad`, compact battle-grid UI, targeting generalized to N rows); Steward's Ledger Economy node makes townsfolk auto-hire a purchase (`DEV_MODE` keeps it free in dev builds). Sim finding: 12/16-slot squads overshoot the arc against *current* 4-5 unit enemy waves — M11's enemy-grid expansion is the designed counterweight; War Banners pricing finalized in M14. Browser-smoked (resize, unlock filtering, hybrid/backline behavior, 16-slot render)
- [x] Milestone 11: **Combat engine features** (wild/m10-m14 branch) — computed modifier layer (enrage / auras / chill / row-AoE at 0.65 discount / on-death revive); per-tier tactical lessons + boss signature traits (raid-tier table); hand-authored deterministic wave compositions (`TIER_WAVES`) with variety mixes; enemy grid expansion 2x3 → 3x4 (Bandit) → 4x4 (Infernal); sappers + resident injury (25%/hit, 90s, never killed, `recomputeIncome` authoritative per tick); Battlemage/Banneret/Frost Adept unlocks (War Magics 800 / Standard Bearers 1,500 / Rimecraft 1,200). Sim ported 1:1; arc re-verified (capC walls Orc w5–boss, capR Bandit w6–boss, 12-epic walls Undead w9–14, 16-epic Infernal w2–9, 16-leg reaches Infernal w9 at 90% with the **final boss still closed at 0% — M12 doctrines must open it, verify then**). Browser-smoked (sapper kingdom bypass + injury, necro revive, breath data, battlemage AoE, chill, 3x4/4x4 grids)
- [x] Milestone 12: **Doctrines** (wild/m10-m14 branch) — the four building↔army synergy nodes (Forgework / Tactics / Salves / Blessing, 2k/3k/5k/8k Legacy) as live use-time multipliers through the M11 modifier layer; Infernal boss comp trimmed one breath-mage; sim-verified that doctrines open the final boss (2% → 25% for the endgame squad); browser-smoked (multiplier values, blessing one-revive-per-battle)
- [x] Milestone 13: **Final Siege** (wild/m10-m14 branch) — herald + 3-raid countdown after the first Demon Empress kill; 3-phase gauntlet as one invasion (HP carries, escalation resets per phase, Blessing once per gauntlet; phase waves 14/16/18 sim-tuned to ~38% for the endgame squad with doctrines, 0% without); Lessons of the Last Siege (25,000 Legacy, once) on a lost attempt; victory screen with campaign stats; endless mode (post-boss comp clamp, no second siege); browser-smoked end-to-end (herald, phases, victory overlay, endless resume, lessons once-only)
- [x] Milestone 14: **Full-game balance calibration** (wild/m10-m14 branch; sim + accelerated-engine version — the user's real 1× playthrough is the acceptance gate) — campaign-arc wall-finder in the sim (per-run arc squads vs targets: on-target at both ends, ~half a tier deep mid-campaign; gauntlet 27–38% with the full kit, 0% without doctrines); tree-cost rescale to the pricing philosophy (totals ≈90k, winning kit ≈⅔; top power ranks 6,000, War Banners 4,000/30,000, Blessing 10,000); SAVE_VERSION → 5; browser soak test: a greedy driver played run 1 end-to-end at accelerated speed and fell to Orc w6 with 10 waves / 330 Legacy — matching the sim's prediction (Orc w5–7, ~380 LP) with zero console errors; known perf debt recorded for M15 (per-tick DOM rebuild caps 100× at ~5–8× effective)
- [x] Milestone 14.1: **Acceptance-playtest feedback round 1** (uncommitted on wild/m10-m14) — stale-affordability UI fix (per-tick `refreshAffordability`, since renamed `refreshVolatileUI`); new-save softlock fix (starting gold 75); battle-grid column-stagger fix + hero-pool timer; **combat rebalance from the 5-reset playtest**: the **guard spectrum** (guardian 3 / paladin·banneret 2 / fighter 1.5 / assassin 0.5 weighted targeting, "GRD ×N" on unit cards), Fighter base-roster archetype (Footman/Sellsword/Blademaster/Warlord — frontline DPS), mender buff (22/65/8), paladin heal trim (11→9), hero costs ×1.4/raid tier, Reinforced Walls +3 Kingdom defense/rank, doctrine shop copy rewritten for impact. Sim re-verified: arc lands on the M14 baseline run-for-run (run-1 model reproduces the user's actual run 1 exactly: Orc w7, 11 waves, 380 LP), frontline composition is tier-dependent, paladin-stacks are a specialist choice, rear-row bodyguarding is a real matchup call, slippery assassins non-degenerate. Browser-smoked (weighted distributions exact, cost scaling ×1.96 at tier 2, walls def 27, GRD display, live battle repelled clean)
- [ ] Milestone 15: **Game feel — visuals & sound** — the juice pass that turns the mechanically-complete game (M14) into one that feels good to play: combat/UI feedback animations, floating numbers, kingdom-damage and run-transition drama, portrait/sprite art pass; Web Audio SFX (hits, hires, raid horn, escalation heartbeat, stingers) with mute/volume; reduced-motion toggle. Scope sketch in *Game feel pass — visuals & sound (M15)*. **In progress:** full scope in `M15_SCOPE.md`; Gemini art workflow proven (`M15_ART_PILOT.md` — anchor knight, goblin, backdrop, frame all passed; pipeline tools in `tools/`); tier re-theme (Undead Legion / Infernal Siege) landed ahead of the asset run; **Phase 0 render refactor DONE 2026-07-17** (sim/render decoupled, memoized panels, persistent battle slots, FX bus with first consumers; 100× measured at true 100× effective, browser-verified across three organic run-ends with zero console errors — see *Render architecture* above); **Phase 1 combat juice DONE 2026-07-17** (lunges, hero death-ghosts + enemy death flashes, revive glow, chill tint + ❄, Kingdom HP damage-trail, kingdom-hit shake/vignette, injury flash, raid slam-in, repelled loot float + Legacy badge, escalation red wash — all through the FX bus / state-driven bindings; details in M15_SCOPE.md Phase 1); **runtime sprite pipeline DONE 2026-07-17** (raw-PNG loading + in-memory keying/trim/anchor/downscale, per-key letter fallback, wired into portraits and battle slots — see *Render architecture*); **Phase 2 town/progression juice DONE 2026-07-17** (gold-counter easing, "+N g/s" hire floaters, building purchase flash via the postRenderFlashes mechanism, pool-refresh card shuffle with a wall-clock strobe gate, level-up fanfare banner, Kingdom-fall shroud beat before the run summary, New-Age dawn wash, victory-screen polish, and the Motion Full/Reduced toggle persisted in `meta.reduceMotion` — details in M15_SCOPE.md Phase 2; browser-verified, zero console errors); **T1 atmosphere reskin DONE 2026-07-18** (battlefield painting as the page backdrop, frame texture runtime-keyed by `loadChrome()` into `--chrome-frame` border-image chrome on the three columns + run-summary panel, themed scrollbars; browser-verified, degrades to flat chrome on file://); **scene-layout direction locked 2026-07-18** (`tools/scene-prototype.html`, user-approved: full-screen one-world layout — town vista + diegetic hiring crowd left, battlefield with units standing on tiles right, high-angle camera confirmed via Gemini-web-app backdrop candidates in `assets/raw/`; `M15_ASSET_SPECS.md` extended to 85 entries — **the scene pair (entry 85): two Antigravity 1:1 squares joining AT the town square's painted wall** supersedes the two-half backdrop and wall-as-sprite entries after the 2026-07-18 seam experiments (separately-modeled halves clash in style; composited wall pieces clash in projection); buildings batch 47–55; hero rarity variants generated lazily with `heroSpriteKey()` falling back to base sprites; base-art tier audit slots mender at Rare and paladin at Epic. Generator routing recorded in the spec + `assets/CREDITS.md`: **Antigravity = strong model** (all characters, battlefield v1; ~10 images/5h, 1:1 only), **Gemini web app = weak fallback** (current candidates, wall segment). **Entry 85 RESOLVED same day by `scenebothhalves.png`** — one continuous widescreen (town / wall+gatehouse mid-frame / battlefield, road through the gate) whose detail density finally matches the character series; the prototype loads it full-stage with the wall on the 46% seam, and the pair rig / divider / color grade survive only as fallback code. Known backdrop follow-ups: baked sparkle watermark lower-right, and a character-vs-background resolution mismatch (accepted for now — revisit). **Scene view wired into the live game 2026-07-18 (increment 1 of the T2/T3 build)**: `#scene-toggle` (top-right) flips `index.html` to the full-screen scene — classic panels stay the boot default until the scene is fully playable. Landed: continuous backdrop cover-fit with the wall seated on the 46% seam (`SCENE_WALL_FRAC`), town vista rendering all 9 buildings from real state on fixed plots (`BUILDING_PLOTS`; real sprite when generated via `bldg_<id>` SPRITE_SOURCES keys, schematic SVG placeholder until then; tier-locked ghosts, count badges, faint not-yet-built state, residents drawer reusing `fireResident`), HUD chips (gold/gps/legacy · kingdom+Age+level-up · Kingdom HP on the wall) honoring the volatile/structure split so buttons never rebuild mid-click; browser-verified zero-console-error. **Increments 2+3 landed same day**: the hiring crowd (townsfolk + hero recruits standing in the square as world units — foot-anchored sprites with rarity ground rings, nameplates with income/cost, click-to-hire through the delegated actions, affordability as a volatile class, arrivals/auto-hire chip) and the battle diorama (both squads standing on the field — game row→screen column, game col→depth lane, generalized to every grid up to 4x4; ground tiles show capacity; HP plates updated in place; armed-to-dismiss shares classic's state; raid chip mirrors all raid-bar states with volatile countdown/escalation text; escalation red wash over the field half). The FX bus routes to scene units when the scene is open (`sceneUnitElByKey`; floats/ghosts in a `#scene-fx` overlay; scene-scoped CSS overrides flash the sprite instead of the card box; classic targets keep theirs — covered, not display:none, so nothing leaks). QoL: the scene/classic choice persists (`meta.sceneView`), plots open a drawer with a Build button (buy from the scene), and a file:// notice explains missing art. Found-live fix: the run-summary overlay was z-buried under the scene (an ended run stayed interactive underneath) — `body.scene-open` now lifts it above everything. Browser-verified end-to-end zero-console-error: crowd hires (villager + 5 heroes), scene-built cottage (plot went solid ×1), two full battles fought on the field with live HP drain / floats / lunges / hit flashes, repelled → loot line + wave/streak advance + field cleared, armed-dismiss, boot-restore of the open scene. Not yet visually exercised (class-bound, next playtest): scene death-ghost, kingdom-hit shake over scene, chill tint, injury flash, escalation wash. **Increment 4 landed same day — the scene is now the DEFAULT view** (`meta.sceneView` defaults true for new and legacy saves; the toggle keeps the full classic layout one click away as the escape hatch — classic is not gutted, it renders underneath). Control parity added for scene-only play: hud-level gained the level-up unlocks list and the Found a New Age button with its two-step confirm; a bottom-right system chip carries the game-speed selector (Swift Seasons/DEV lock rules intact), the motion toggle, and the dev reset with confirm; the plot drawer gained the ×1/×5/×10/×max buy-quantity row; battle units carry stat tooltips (ATK/HLR/DEF/GRD — enemies at build time, heroes folded into the dismiss hint); and **hero drag-swap works on the diorama** (HTML5 drag on units, empty positions droppable via their ground tiles, same `swapHeroes` state path; `renderSceneBattle` skips while dragging, mirroring classic). Browser-verified through real action paths, zero console errors: default-on-absent-field boot, New Age confirm/cancel, speed 4× + highlight, motion Reduced→body class, reset confirm/cancel, qty ×max bulk label, swap 0→5 re-rendered at the new position. An organic Age fall + refound (Age 7) happened mid-verification — summary eclipsed the scene correctly. **Buildings batch 47–55 fully generated same day** (Antigravity; smithy chosen from 3 variants — option 2, warmest and pipeline-clean; option 1 retired because its edge-running smoke plume trimmed into a 24%-of-height column that seated the building ~¼ small; all variants kept on disk for reference), plus goblin skirmisher + caster (entries 17–18). Asset-priority rule locked with the user: rank generation batches by progress toward the scene destination, not by visibility in the interim panel UI)
- [ ] Milestone 16: **Tutorialization** — guided first steps for a new save (free Villager with the first Cottage as the teaching hook; rename/relocate the "Found a New Age" button; stat-abbreviation hover tooltips incl. GRD). Full notes in *Ideas under consideration → Tutorialization pass*. Sits after M15.
- [ ] Milestone 17: **Distribution & packaging** — the M15 runtime sprite pipeline needs http (browsers block canvas pixel access on `file://`), so once art is in, double-clicking `index.html` still *runs* the game but shows letter/SVG fallbacks instead of sprites (game logic + localStorage saves are unaffected). **Players must never run a server.** Two viable paths, chosen at ship time — NOT before, since baking while the art still churns means maintaining duplicate assets: (1) **host** on itch.io / GitHub Pages / Netlify — served over http, share a URL; the natural home for a web incremental and what the CC0 asset policy anticipates; (2) **bake a self-contained bundle** — pre-process the raw magenta PNGs offline into transparent PNGs + a foot-anchor manifest so no runtime canvas is needed, enabling `file://` double-click and even a single inlined `.html`. Baking also restores the developer's own double-click-with-sprites workflow and preserves the zero-build dev loop (bake only at ship). Desktop wrapping (Electron/Tauri) considered and rejected as overkill. End-of-project step, after M15/M16. Interim dev workflow: `start-game-server.bat` (double-click → serves :8321 and opens the game with sprites over http).

## Starting state
- Player begins with 75 gold — enough that even buying all 3 Hamlet Cottages (39g) still leaves the first 25g Villager hire affordable (softlock guard, 2026-07-17; was 50); Royal Treasury ranks raise this for later Ages
- No base income — gold only accrues from hired residents
- Kingdom HP starts full (base `KINGDOM_HP_MAX` = 1000, +250 per Reinforced Walls rank)
