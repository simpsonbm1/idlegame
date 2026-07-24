# Endgame Rework — The Cathedral's Miracle

**Status:** design locked 2026-07-24 (user-directed), audited against live `game.js` the same
day and revised. Supersedes the M13 Final Siege *flow* (the 3-phase gauntlet content stays; how
you reach and survive it changes). Not yet implemented. Doc-rot corrections (below) ride along in
the same pass. Changelog at the end.

## The problems this fixes

1. **Economy bug (root cause).** The base trees cost ~93k Legacy total. First-clear credit
   banks ~113k just reaching the w15 wall (Infernal w1-14 @6,250 = 87.5k, plus ~25k from
   the earlier tiers). So you **fully fund both trees around Infernal w10-14 — before the
   Final Siege even unlocks** (it needs the Infernal boss at w17). You max out, wall, and
   have nothing left to buy. The 25k Lessons-of-the-Last-Siege bonus lands on a player with
   nothing to spend it on. The intended "reach the siege → lose → upgrade → win" beat is
   structurally impossible.

2. **Compounding.** Reaching *and* winning the siege is ~7 sequential win-or-Age-ends gates
   (w15 → w16 → w17-boss → 3 post-boss countdown raids → the 3-phase gauntlet). An Overrun at
   any gate restarts from Goblin w1 (no tier ratchet). These genuinely multiply — per-gate rates
   in the 24-40% range make the true end-to-end rate a fraction of a percent. No per-gate tuning
   fixes a chain that long.

3. **Design intent (user).** A maxed kit with a non-degenerate comp should **win** — comfortably.
   The gauntlet losses that happen are *scripted, guaranteed* pacing beats, not RNG. The moment
   there's nothing left to upgrade, a loss is RNG theater, not a decision — so the win, once
   earned, must be certain.

## The locked design — three visits, two upgrade sub-tiers

The endgame is a **three-visit arc** to the gauntlet. The first two visits are **guaranteed
losses by balance** — no build can win them; if the math ever allows a win, that's a balance
bug to fix, not a feature (user ruling: "there is no such thing as a god-tier build that could
win outright; if there is, there shouldn't be"). Each loss unlocks the next tier of preparation.
The **Miracle is a purchased upgrade**, not a scripted deity gift — buying it is what arms the
revival that turns the third visit into the win.

### The arc
1. **Approach = victory lap.** For a maxed kit (all base trees) + non-degenerate comp, reaching
   the gauntlet is a formality. **The whole ladder has to be a formality, not just the last few
   waves** — every visit after the first re-climbs ~55 waves from Goblin w1, and each one is a
   win-or-the-Age-ends gate. Three gates at 95% is 86%; even 99.5% per wave completes the full
   climb only 76% of the time, which would kill one scripted run in four before it reached its
   scripted beat. Two ways to satisfy this; pick one at stage 2:
   - Tune the maxed kit to **effectively 100% per wave across the whole Infernal tier** — the
     lever is the **top base ranks** (Drills/Armor/doctrines/War Banners, the maxed-only nodes),
     so runs 1-8 are unchanged; or
   - **a `finalSiegeSeen`-gated ladder skip** that starts post-siege Ages at a later tier. This
     removes the compounding structurally rather than tuning it down, and it also shortens the
     visit-2 Age (see step 4). CLAUDE.md already floats "start at wave N" as a candidate Economy
     QoL node.

   Either way the countdown collapses to **one non-lethal herald beat**.

2. **Siege-arrival beat.** A severe "oh no, it's the Gauntlet" stakes beat (same machinery as
   the M16 first-boss beat, escalated; fires even post-tutorial, once per campaign). Warns the
   gauntlet is overwhelming — **does NOT say "you can't win."**

3. **Gauntlet visit 1 → guaranteed loss → real reset (the Age falls).** Balance-tuned unwinnable.
   The Age ends normally (re-climb from Goblin w1), **but** the run summary now unlocks **Sub-tier
   A ("Preparation")**, framed *"We know what we're up against now. We must prepare."* The 25k
   Lessons bonus pays here to fund it.

4. **Sub-tier A — Preparation upgrades.** Unlocked by `meta.finalSiegeLost`. A set of moderate
   power upgrades, **a large income node**, and **the Miracle node**. Bought on the run-summary
   shop (banked surplus + Lessons). The stat upgrades get you *further* next visit; the **Miracle**
   is the key purchase that arms the revival.

   - **The income node** exists because the visit-2 Age is bounded by gold and time, not combat
     power: it is a full rebuild from Hamlet to Realm with a 16-slot legendary squad, and no
     amount of hero-power ranking shortens it. Size it in **multiples, not percentages** (5-10x)
     — the goal is turning a ~30-minute rebuild into a short one, and because kingdom-level costs
     are fixed while income scales, a multiplier compresses the level ladder directly. Blast
     radius is nil: it cannot be bought before the first siege, so runs 1-8 never see it. Note it
     makes the re-climb *shorter*, not *safer* — step 1 is still required.
   - **The Miracle must not be missable.** It stays a purchase (that is the point), but upgrades
     are buyable only through the run-summary overlay, so a player who skips it cannot correct
     the mistake mid-run: they re-climb the whole ladder, lose visit 2 for real, and only then
     get another shop. So: **glow it** in the upgrade shop until first interacted with (same idea
     as the scene's new-building-unlock glow, but a different renderer, so it needs its own
     seen-flag rather than reusing `seenPlots`), and **price it at or below the 25k Lessons
     grant** so the payout landing on the same summary always covers it.

5. **Gauntlet visit 2 → get further (maybe to the final boss) → also a guaranteed loss.**
   Balance-tuned so Sub-tier A gets you deeper into the phases but still can't clear.
   - **Miracle owned:** the loss triggers **the Miracle event** instead of a reset — the
     Cathedral raises a fresh defense mid-siege (NOT a reset, no ladder re-climb) and unlocks
     **Sub-tier B**. What the Miracle actually does is in *The Miracle event* below; it **grants**
     a defense rather than reviving one, because by the time the Kingdom falls there is nothing
     left alive to revive.
   - **Miracle NOT owned:** ordinary real reset — go buy the Miracle from Sub-tier A, then climb
     back and try visit 2 again. **The Miracle is the gate to the win path.**

6. **Sub-tier B — the overpowered capstones.** Revealed the moment the Miracle fires. The
   gauntlet pauses, a shop opens; these are the decisive, guaranteed-win buffs. **Free (cost 0)**
   — the guaranteed-win payoff is never Legacy-gated.

7. **Gauntlet visit 3 — a continuation of visit 2, NOT a reset.** The same battle resumes with
   Sub-tier B power, restarting the gauntlet phases from phase 1 (no ladder reset).
   **Guaranteed win** for any non-degenerate comp → campaign victory.

**Net beat:** cruise to the siege → lose, ominous → prepare (buy the Miracle + prep) → reach it
again, get *further*, lose → the Miracle fires, overwhelming power → finish it, win. **One real
reset** (after visit 1), **one mid-siege revival** (after visit 2).

### The Miracle event

Fires on the **visit-2 loss**, not at purchase — the bought Miracle sits inert until the second
defeat. It must **grant** a defense, not revive one: dead heroes are removed from `heroSquad` the
tick they fall, and the Kingdom only takes hits once the squad is wiped, so at `kingdomHP <= 0`
the squad array is all `null`. There is nothing there to raise. Nothing restores Kingdom HP either,
so a revival that only touches the squad re-enters the `kingdomHP <= 0` branch on the very next
tick — with `meta.miracleSpent` already set, which spends the campaign's only win path on nothing.

`triggerMiracle()` therefore:
1. Restores `kingdomHP` to `getKingdomHpMax()`.
2. **Fills the squad** with a full roster of legendary heroes. This also decouples the guaranteed
   win from whatever gold survived the losing visit.
3. Resets `blessingUsed` — `spawnFinalSiegePhase` carries it forward from the previous invasion,
   so visit 3 would otherwise start with the Cathedral Blessing already spent.
4. Sets `meta.miracleSpent`, unlocks Sub-tier B, opens the revival shop, `spawnFinalSiegePhase(1)`.

Revival is **unconditional on ownership** — it fires because the Miracle upgrade is owned, not
because a Cathedral is standing. (Narratively the Cathedral; mechanically the purchase.)

### State machine
- `meta.finalSiegeSeen` — set when the first gauntlet spawns. Drives the **arrival beat only**.
- `meta.finalSiegeLost` — set in `endRun` only when `reason === 'overrun' && currentInvasion.finalSiege`.
  Gates **both** the Sub-tier A unlock and the Lessons payout. Separate from `finalSiegeSeen`
  because `endRun` pays Lessons for *any* reason including `'abandoned'`: without the split, a
  player can hit "Found a New Age" the instant the gauntlet spawns and collect the 25k plus the
  Sub-tier A unlock without fighting, skipping the arrival beat the whole sequence is built around.
- `upgradeRank('miracle') > 0` — the Miracle node is owned (a Sub-tier A purchase).
- `meta.miracleSpent` — the Miracle has fired (once per campaign). Unlocks Sub-tier B.
- **Final Siege overrun routing:**
  - Miracle owned & `!meta.miracleSpent` → **the Miracle event** (above). NOT `endRun`.
  - else → real `endRun('overrun')`. The run summary shows Sub-tier A once `finalSiegeLost` is set.

### Guaranteed-loss enforcement
Visits 1 and 2 are unwinnable **by balance** — stage 2 tunes the phase stats so no-sub-tier
can't clear visit 1 and Sub-tier-A can't clear visit 2. No win-interception script: the loss
(overrun) is the real, tuned outcome; the state machine just routes it. If a comp ever wins a
visit it shouldn't, that's a stage-2 tuning bug.

Two things threaten that guarantee and have to be handled, or "unwinnable" is a claim tuning has
to keep re-defending:
- **Escalation must carry across gauntlet phases.** `spawnFinalSiegePhase` sets `duration: 0`,
  restarting the escalation clock and handing back the 60-second grace every phase. Since nothing
  caps mid-battle hiring except gold, and endgame gold is already over-plentiful (tracker #0054),
  a rich player can rehire their way through phases meant to be unwinnable. Carry the clock across
  phases (or floor it at the previous phase's value) so a stalled gauntlet only ever gets harder.
- **Verify against the sim's reinforcement/grind model, not the fixed-squad win-rate table.** The
  fixed-squad table reports "unwinnable" regardless of how much gold the real player brings, which
  is exactly the failure mode this guarantee cannot afford.

## Consequences / edge cases
- **Two guaranteed losses, one real reset.** Visit 1 falls the Age (fast re-climb with the maxed
  + Sub-tier-A kit); visit 2's loss is caught by the Miracle (no reset) → visit 3 continuation →
  win. Reaching the gauntlet with the Miracle owned = winning the campaign.
- **Revival state must persist.** `currentInvasion` is already in the save payload, so a paused
  gauntlet survives a reload. The revival-mode flag must join it, and must also freeze `tick()`
  the way `runEnded` and `victoryPending` do. Without both, reloading while the revival shop is
  open resumes an unpaused gauntlet with a dead kingdom.
- **Sub-tier A budget.** Roughly 88k is available at the visit-1 loss (~150k campaign first-clear
  + one countdown wave, minus ~93k of base trees, plus 25k Lessons), and `FINAL_SIEGE_COUNTDOWN_RAIDS`
  3 → 1 removes 12,500 of that. No pricing target beyond **every Sub-tier A node must be
  purchasable** (user's call).
- **Endless mode after victory: unchanged.** Free Sub-tier B capstones persist and trivialize it;
  accepted, since endless is undesigned beyond existing.

## Doc-rot corrections (fold into this pass)
The **persistent-siege loss model** is mis-documented as a wave-retry model in several places.
Correct model:
> A battle is a persistent siege with exactly two outcomes: **Repelled** (enemy squad wiped →
> advance one wave) or **Overrun** (Kingdom HP hits 0 → the Age ends). There is **no non-fatal
> loss and no wave re-queue** — a squad wipe continues the siege against Kingdom HP (with
> mid-battle reinforcement) until one of those two happens. The ladder climbs only on Repels;
> an Overrun restarts from Goblin w1.

Purge stale "wave repeats until beaten / re-attacks / re-fights" language:
- CLAUDE.md lines ~102, 159, 200, 280, 420
- game.js `winInvasion` comment (~line 1482)

Preserve the design point that language was carrying (the ladder never skips ahead) while
removing the false mechanic (a lost wave re-queuing). Then rewrite the Final Siege / countdown /
Lessons sections to the new three-visit flow.

## Implementation + verification plan
- **Stage 1 — mechanic (no balance numbers):** `FINAL_SIEGE_COUNTDOWN_RAIDS` 3 → 1; new flags
  (`meta.finalSiegeSeen`, `meta.finalSiegeLost`, `meta.miracleSpent`, additive `?? false` — no
  SAVE_VERSION bump yet); Sub-tier A + Sub-tier B nodes in `UPGRADE_TREES` with `unlock`
  predicates + the Miracle node; siege-arrival beat; Final-Siege overrun routing (Miracle event
  vs `endRun`); `triggerMiracle()` per *The Miracle event*; Lessons gated on `finalSiegeLost`;
  escalation carried across phases; revival shop (reuse the run-summary overlay in a "revival"
  mode: Sub-tier B unlocked, "Return to the fight" resumes the gauntlet) with its flag persisted
  and `tick()` frozen; `buyUpgrade`/`renderUpgradeTree` respect `node.unlock`; Miracle glow flag.
- **Stage 2 — balance (SAVE_VERSION bump here):** make the approach a near-certainty by whichever
  route step 1 of the arc picks (top-rank buff to effectively 100% per wave across Infernal, or
  the ladder skip); tune the phase stats + the two sub-tiers so visit 1 (no sub-tier) and visit 2
  (Sub-tier A) are unwinnable **against the reinforcement/grind model** and visit 3 (Sub-tier B)
  is a guaranteed win for a non-degenerate comp; size the Sub-tier A income node so the visit-2
  Age is short; confirm every Sub-tier A node is purchasable from banked surplus + the 25k
  Lessons (Sub-tier B is free, so no affordability tuning there). Verify runs 1-8 walls unchanged.
  Keep the sim's constant mirror in sync.
- **Stage 3 — docs:** the corrections above + sim mirror.

## Implementation anchors (game.js, verified 2026-07-23/24 — line numbers approximate)
- **Countdown constant:** `FINAL_SIEGE_COUNTDOWN_RAIDS` (~224) 3 → 1. The decrement logic in
  `winInvasion` (~1508-1516) and the spawn in `startInvasion` (~1437-1441) already read it.
- **meta flags:** add to `defaultMeta()` (~326-347) and `loadMeta()` (~358-377) — `finalSiegeSeen`,
  `finalSiegeLost`, `miracleSpent`, all `?? false` (additive, NO SAVE_VERSION bump in stage 1).
- **Set `meta.finalSiegeSeen`** when the first gauntlet spawns — in `spawnFinalSiegePhase(1)`
  (~1455) or where `finalSiegeCountdown === 0` fires in `startInvasion` (~1437). Drives the
  arrival beat only.
- **Overrun routing:** the tick's `kingdomHP <= 0` branch (~1839-1842) calls `endRun('overrun')`.
  Gate it: if `currentInvasion.finalSiege && upgradeRank('miracle') > 0 && !meta.miracleSpent`
  → `triggerMiracle()` instead of `endRun`. Else `endRun` as now.
- **Squad is empty at that point:** `combatTick` (~1203) nulls any dead hero's slot every tick, so
  `triggerMiracle()` must fill `heroSquad`, not revive it. `getKingdomHpMax()` restores the HP.
- **Blessing carry:** `spawnFinalSiegePhase` (~1468) copies `blessingUsed` from the previous
  invasion — reset it in `triggerMiracle()`.
- **Escalation clock:** `spawnFinalSiegePhase` (~1473) sets `duration: 0`. Carry the previous
  phase's value instead (`escalationMult` ~990 reads it via `currentInvasion.duration`).
- **Lessons** (~1531-1539 in `endRun`) pays on `currentInvasion.finalSiege && !meta.lessonsGranted`
  for **any** reason including `'abandoned'`. Gate it on `reason === 'overrun'` and set
  `meta.finalSiegeLost` in the same branch.
- **Capstone gating:** `UPGRADE_TREES` node defs; add an optional `unlock: () => bool` to Sub-tier
  A/B nodes. `buyUpgrade` (~436) must reject a locked node; `renderUpgradeTree` (~3158) must
  hide-or-lock a node whose `unlock` is false. Sub-tier A `unlock: () => meta.finalSiegeLost`;
  Sub-tier B `unlock: () => meta.miracleSpent`, `costs: [0]`.
- **Shop is summary-only:** `buyUpgrade` ends in `renderRunSummary` (~451) — the reason the
  Miracle needs the glow and the low price rather than trusting the player to notice it.
- **Revival shop:** reuse the run-summary overlay (`renderRunSummary` ~3188 / `run-summary-overlay`).
  Add a "revival" mode (distinct title/copy, a **"Return to the fight"** button that resumes the
  paused gauntlet rather than `foundNewAge`). Or a sibling `renderRevivalShop()` that renders
  `renderUpgradeTree` filtered to unlocked capstones. The gauntlet is paused while it's open
  (mirror the `runEnded`/`victoryPending` freeze pattern in `tick()` ~1810), and the flag joins
  the save payload (~1687) alongside `runEnded`/`runSummary`.
- **Siege-arrival beat:** add a severe event-beat like `TUTORIAL_BOSS_BEAT` (~3519-3530); fire it
  in `renderTutorial` (~3601-3614) on the first finalSiege spawn **even when `meta.tutorialDone`**
  (the current early-return gates on `!meta.tutorialDone` — the siege beat needs a path outside
  that gate), guarded to fire once off the `finalSiegeSeen` transition.
- **Sub-tier A/B node placement:** likely a new `UPGRADE_TREES` group or flagged nodes in the
  existing trees; render them in the run-summary/revival shop only when unlocked so pre-endgame
  summaries don't show locked capstones (or show them greyed with an "unlocks at the Final Siege"
  hint — match the building-unlock-hint pattern).

## Changelog
- **2026-07-24 (design):** locked live with the user. Three-visit arc, two upgrade sub-tiers,
  purchasable Miracle, Sub-tier B free.
- **2026-07-24 (audit, Opus 5):** audited against live `game.js`; seven revisions, all
  user-approved, folded into the body above. The two that were corrections rather than
  refinements: the Miracle must **grant** a squad and Kingdom HP (as originally specced it could
  not fire at all — nothing is alive to revive and the next tick re-overruns), and the approach
  target moved from "~95% on w15-17" to a near-certainty across the whole ladder (three gates at
  95% is 86%, and the real exposure is ~55 waves). The other five: a large income node in
  Sub-tier A (the visit-2 Age is gold-bound, not power-bound); the Miracle glows and is priced
  under the Lessons grant (the shop is summary-only, so a miss costs a whole Age); escalation
  carries across gauntlet phases and unwinnability is verified against the reinforcement model
  (gold could otherwise grind the scripted losses); `finalSiegeSeen` split from `finalSiegeLost`
  (closing an abandon-at-spawn Lessons exploit); revival state persisted and `tick()` frozen.
  A mid-run "War Council" shop was floated and dropped — Preparation is bought at the visit-1
  summary, so only ~20k of repeat trickle is ever unspendable.
