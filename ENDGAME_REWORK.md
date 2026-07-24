# Endgame Rework — The Cathedral's Miracle

**Status:** design locked 2026-07-24 (user-directed this session). Supersedes the M13
Final Siege *flow* (the 3-phase gauntlet content stays; how you reach/survive it changes).
Not yet implemented. Doc-rot corrections (below) ride along in the same pass.

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

3. **Design intent (user, this session).** A maxed kit with a non-degenerate comp should
   **win** — comfortably. The gauntlet losses that happen are *scripted, guaranteed* pacing
   beats, not RNG. The moment there's nothing left to upgrade, a loss is RNG theater, not a
   decision — so the win, once earned, must be certain.

## The locked design — three visits, two upgrade sub-tiers

The endgame is a **three-visit arc** to the gauntlet. The first two visits are **guaranteed
losses by balance** — no build can win them; if the math ever allows a win, that's a balance
bug to fix, not a feature (user ruling: "there is no such thing as a god-tier build that could
win outright; if there is, there shouldn't be"). Each loss unlocks the next tier of preparation.
The **Miracle is a purchased upgrade**, not a scripted deity gift — buying it is what arms the
revival that turns the third visit into the win.

### The arc
1. **Approach = victory lap.** For a maxed kit (all base trees) + non-degenerate comp, Infernal
   w15 → w16 → w17-boss each **~95%+**; the countdown collapses to **one non-lethal herald beat**.
   Reaching the gauntlet is a formality. *Lever:* buff the **top base ranks** (Drills/Armor/
   doctrines/War Banners — the maxed-only nodes), so runs 1-8 are unchanged but the near-maxed
   endgame kit sails w15-17.

2. **Siege-arrival beat.** A severe "oh no, it's the Gauntlet" stakes beat (same machinery as
   the M16 first-boss beat, escalated; fires even post-tutorial, once per campaign). Warns the
   gauntlet is overwhelming — **does NOT say "you can't win."**

3. **Gauntlet visit 1 → guaranteed loss → real reset (the Age falls).** Balance-tuned unwinnable.
   The Age ends normally (re-climb from Goblin w1), **but** the run summary now unlocks **Sub-tier
   A ("Preparation")**, framed *"We know what we're up against now. We must prepare."* The 25k
   Lessons bonus pays here to fund it.

4. **Sub-tier A — Preparation upgrades.** Unlocked by `meta.finalSiegeSeen`. A set of moderate
   power upgrades **plus the Miracle node**. Bought on the run-summary shop (banked surplus +
   Lessons). The stat upgrades get you *further* next visit; the **Miracle** is the key purchase
   that arms the revival.

5. **Gauntlet visit 2 → get further (maybe to the final boss) → also a guaranteed loss.**
   Balance-tuned so Sub-tier A gets you deeper into the phases but still can't clear.
   - **Miracle owned:** the loss triggers **the Miracle event** instead of a reset — the
     Cathedral revives the party mid-siege (NOT a reset, no ladder re-climb) and unlocks
     **Sub-tier B**.
   - **Miracle NOT owned:** ordinary real reset — go buy the Miracle from Sub-tier A, then climb
     back and try visit 2 again. **The Miracle is the gate to the win path.**

6. **Sub-tier B — the overpowered capstones.** Revealed the moment the Miracle fires. The
   gauntlet pauses, the party is revived, a shop opens; these are the decisive, guaranteed-win
   buffs.

7. **Gauntlet visit 3 — a continuation of visit 2, NOT a reset.** The same battle resumes with
   Sub-tier B power. **Guaranteed win** for any non-degenerate comp → campaign victory.

**Net beat:** cruise to the siege → lose, ominous → prepare (buy the Miracle + prep) → reach it
again, get *further*, lose → the Miracle fires, overwhelming power → finish it, win. **One real
reset** (after visit 1), **one mid-siege revival** (after visit 2).

### State machine
- `meta.finalSiegeSeen` — set when the first gauntlet spawns. Unlocks Sub-tier A; gates the
  arrival beat (fires once).
- `upgradeRank('miracle') > 0` — the Miracle node is owned (a Sub-tier A purchase).
- `meta.miracleSpent` — the Miracle revival has fired (once per campaign). Unlocks Sub-tier B.
- **Final Siege overrun routing:**
  - Miracle owned & `!meta.miracleSpent` → **Miracle revival**: set `meta.miracleSpent`, unlock
    Sub-tier B, revive the squad, open the Sub-tier B shop, resume the gauntlet (visit 3). NOT
    `endRun`.
  - else → real `endRun('overrun')`. The run summary shows Sub-tier A once `finalSiegeSeen` is
    set. Lessons pays on the first such loss.

### Guaranteed-loss enforcement
Visits 1 and 2 are unwinnable **by balance** — stage 2 tunes the phase stats so no-sub-tier
can't clear visit 1 and Sub-tier-A can't clear visit 2. No win-interception script: the loss
(overrun) is the real, tuned outcome; the state machine just routes it. If a comp ever wins a
visit it shouldn't, that's a stage-2 tuning bug.

## Consequences / edge cases
- **Two guaranteed losses, one real reset.** Visit 1 falls the Age (fast re-climb with the maxed
  + Sub-tier-A kit); visit 2's loss is caught by the Miracle (no reset) → visit 3 continuation →
  win. Reaching the gauntlet with the Miracle owned = winning the campaign.
- **Revival is unconditional on ownership** — it fires because the Miracle upgrade is owned, not
  gated on a standing Cathedral. (Narratively the Cathedral; mechanically the purchase.)
- Endless mode after victory: unchanged.

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
Then rewrite the Final Siege / countdown / Lessons sections to the new three-visit flow.

## Implementation + verification plan
- **Stage 1 — mechanic (no balance numbers):** `FINAL_SIEGE_COUNTDOWN_RAIDS` 3 → 1; new flags
  (`meta.finalSiegeSeen`, `meta.miracleSpent`, additive `?? false` — no SAVE_VERSION bump yet);
  Sub-tier A + Sub-tier B nodes in `UPGRADE_TREES` with `unlock` predicates + the Miracle node;
  siege-arrival beat; Final-Siege overrun routing (revival vs endRun); revival shop (reuse the
  run-summary overlay in a "revival" mode: Sub-tier B unlocked, "Return to the fight" resumes the
  gauntlet); `buyUpgrade`/`renderUpgradeTree` respect `node.unlock`.
- **Stage 2 — balance (SAVE_VERSION bump here):** tune the top-rank approach buff (w15-17 → ~95%),
  and the phase stats + the two sub-tiers so visit 1 (no sub-tier) and visit 2 (Sub-tier A) are
  unwinnable and visit 3 (Sub-tier B) is a guaranteed win for a non-degenerate comp. Sub-tier A
  must be affordable from banked surplus + the 25k Lessons; Sub-tier B is free (cost 0), so no
  affordability tuning there. Verify runs 1-8 walls unchanged. Keep the sim's constant mirror in
  sync.
- **Stage 3 — docs:** the corrections above + sim mirror.

## Resolved mechanical details (user, 2026-07-24)
- **Visit 3 continuation point:** on the Miracle, revive the squad to full and **restart the
  gauntlet phases from phase 1** within the same battle (no ladder reset). Sub-tier B makes it a
  quick win.
- **Sub-tier B pricing:** **free (cost 0).** The guaranteed-win payoff, never Legacy-gated.
- **Miracle "event" timing:** the bought Miracle sits inert; its revival + the Sub-tier B reveal
  fire on the **visit-2 loss** (not at purchase) — the trigger is the second defeat.

## Implementation anchors (game.js, verified 2026-07-23/24 — line numbers approximate)
- **Countdown constant:** `FINAL_SIEGE_COUNTDOWN_RAIDS` (~224) 3 → 1. The decrement logic in
  `winInvasion` (~1508-1516) and the spawn in `startInvasion` (~1437-1441) already read it.
- **meta flags:** add to `defaultMeta()` (~326-347) and `loadMeta()` (~358-377) — `finalSiegeSeen:
  false`, `miracleSpent: false`, both `?? false` (additive, NO SAVE_VERSION bump in stage 1).
- **Set `meta.finalSiegeSeen`** when the first gauntlet spawns — in `spawnFinalSiegePhase(1)`
  (~1455) or where `finalSiegeCountdown === 0` fires in `startInvasion` (~1437). Also drives the
  arrival beat + Sub-tier A unlock.
- **Overrun routing:** the tick's `kingdomHP <= 0` branch (~1839-1842) calls `endRun('overrun')`.
  Gate it: if `currentInvasion.finalSiege && upgradeRank('miracle') > 0 && !meta.miracleSpent`
  → new `triggerMiracle()` (set `meta.miracleSpent`, revive squad to full/alive, `spawnFinalSiegePhase(1)`,
  open the revival shop) instead of `endRun`. Else `endRun` as now.
- **Lessons** (~1531-1539 in `endRun`) already pays once on a lost finalSiege via
  `!meta.lessonsGranted` — pays on the visit-1 real-reset loss, which funds Sub-tier A. Good as-is.
- **Capstone gating:** `UPGRADE_TREES` node defs; add an optional `unlock: () => bool` to Sub-tier
  A/B nodes. `buyUpgrade` (~436) must reject a locked node; `renderUpgradeTree` (~3158) must
  hide-or-lock a node whose `unlock` is false. Sub-tier A `unlock: () => meta.finalSiegeSeen`;
  Sub-tier B `unlock: () => meta.miracleSpent`, `costs: [0]`.
- **Revival shop:** reuse the run-summary overlay (`renderRunSummary` ~3188 / `run-summary-overlay`).
  Add a "revival" mode (distinct title/copy, a **"Return to the fight"** button that resumes the
  paused gauntlet rather than `foundNewAge`). Or a sibling `renderRevivalShop()` that renders
  `renderUpgradeTree` filtered to unlocked capstones. The gauntlet is paused while it's open
  (mirror the `runEnded`/`victoryPending` freeze pattern in `tick()`).
- **Siege-arrival beat:** add a severe event-beat like `TUTORIAL_BOSS_BEAT` (~3519-3530); fire it
  in `renderTutorial` (~3601-3614) on the first finalSiege spawn **even when `meta.tutorialDone`**
  (the current early-return gates on `!meta.tutorialDone` — the siege beat needs a path outside
  that gate), guarded to fire once (its own seen-flag or `finalSiegeSeen` transition).
- **Sub-tier A/B node placement:** likely a new `UPGRADE_TREES` group or flagged nodes in the
  existing trees; render them in the run-summary/revival shop only when unlocked so pre-endgame
  summaries don't show locked capstones (or show them greyed with an "unlocks at the Final Siege"
  hint — match the building-unlock-hint pattern).
