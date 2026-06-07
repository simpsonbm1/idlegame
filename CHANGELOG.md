# Changelog

## 2026-06-07

### Economy & Balance
- Replaced the global 1.15x building cost multiplier with per-building cost growth rates, tuned individually so early buildings (Cottage, Tavern, Smithy, Library) stay affordable longer while late-game buildings (Workshop, Tower, Cathedral) ramp up faster.
- Increased slot counts for Alchemist's Workshop, Wizard's Tower, and Cathedral so each tier's total output keeps trending upward through the building roster.
- Widened income ranges for Alchemist, Mage, and High Priest residents so late-tier units feel like a real step up over the previous tier.

### Siege & Invasion Overhaul
- Replaced the old "instant repel at a defense threshold" mechanic with a duration-based siege: sieges now always resolve on a timer, with the duration scaled by how your current defense compares to the benchmark (strong defense = short siege, weak defense = longer siege capped at a max — no more permanent sieges).
- Tied raid types to kingdom tier: Town faces Goblin Raids, City faces Orc Warbands, Kingdom faces Bandit Hordes, Empire faces Dark Army, and Dynasty/Realm face Dragon Sieges. Each tier has its own defense curve, loot curve, and wave counter that resets when you advance to the next tier.
- Replaced flat per-wave loot scaling with a win-streak "combo" system: successfully repelling builds a compounding reward streak, while a failed siege resets the streak and pays a flat consolation amount instead — so raid difficulty can climb forever without runaway rewards from "farming" failed sieges.
- Tuned raid base defense values, defense growth rates, and loot values across several playtesting passes (notably bringing Orc Warband's and Dragon Siege's starting difficulty down to better match how much defense capacity players actually gain between kingdom tiers).

### Bug Fixes
- Fixed a stale `checkRepel()` call left over from the old siege system that silently threw an error on every hire, which stopped the building panel from refreshing until an unrelated action (buying a building, expanding/collapsing a section) forced a redraw.
- Fixed auto-recruit hires not refreshing the building panel — the auto-recruit path saved game state but never triggered a re-render.
