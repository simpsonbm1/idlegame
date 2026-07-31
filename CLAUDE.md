# Idle Kingdom — Project Context

## What this is
A medieval fantasy **incremental kingdom-defense game**: the passive town-building and gold
generation of a Realm Grinder feeds an active Legionbound-style autobattler at the town gates —
and the autobattler is the *primary* mechanic. Deliberately a **finite experience** (~5-hour
arc of 8–10 death-and-rebuild runs) ending in a winnable Final Siege, with an optional endless
mode after victory. No click-to-earn; the economy is fully idle once set up.

This is the developer's first coding project. Keep explanations clear, define new terms, and
prefer small working milestones over large upfront designs.

## Where things live
- **`DESIGN.md` — the design spec and source of truth.** Design-first, not code-first: the code
  gets redesigned around the spec. Don't treat what the code currently does as a design
  constraint or authority — read it to estimate implementation cost or find gaps, not to
  justify design choices. Read the relevant DESIGN.md sections before any design, balance, or
  mechanics change (a PreToolUse gate delivers this reminder on the session's first `game.js`
  edit).
- **`MILESTONES.md`** — the milestone tracker: closed history (M1–M14.1) and current scope
  (M15–M17).
- **`ENDGAME_REWORK.md`** — the locked endgame redesign, audited, not yet built (tracker #0069).
- **`M15_SCOPE.md` / `M15_ASSET_SPECS.md` / `M15_ART_PILOT.md`** — game-feel scope, asset
  prompts, art pipeline and generator routing.
- **`AGENT_DELEGATION.md`** — delegation routing, prompt checklist, verifier conventions.
- **`SESSION_HANDOFF.md`** — in-flight session state (gitignored; hook-mirrored).

## Current focus
**The art has moved in-house to Blender** (user decision 2026-07-31): the AI-generated
sprites and the rendered ones do not sit together, so the roster was rebuilt in
`tools/blender/` rather than added to. **It is complete**: 83 assets covering every
character and building the game needs, rebuilt from source in about three minutes by
`python tools/blender/render_all.py`. None of it is wired into the game yet, and no
human has judged it. Animation is a later pass.

Also live: M15 (game feel) in progress; M16 tutorialization phases 1–2 built, pending the
user's playtest; the endgame rework is designed and audited, not started. Detail:
`MILESTONES.md` and `SESSION_HANDOFF.md`.

## Keeping docs current
**Before committing or pushing, update CLAUDE.md, DESIGN.md, and MILESTONES.md to match what is
actually implemented** — these files are the map other sessions (and the developer) use to
understand the game without re-reading all the code. Mechanics, formulas, balance values, and
design decisions in DESIGN.md must match `game.js`.

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

## Model-tiered subagent delegation
This project has its own agent roster in `.claude/agents/` — **game-implementer** (Sonnet:
fully-designed code changes, `node --check` gate, sim-mirror sync), **balance-analyst** (Haiku:
sim runs reported as deltas vs the documented baseline), **browser-verifier** (Sonnet:
checklist-driven browser passes with evidence) — plus the generic user-level roster
(`implementer`/`doc-worker`/`log-triager`; routing table in `~/.claude/CLAUDE.md`). Full
routing rules, the delegation-prompt checklist, and how verifier reports interact with the
browser-verified convention: **`AGENT_DELEGATION.md`**. Division of labor: the main thread
plans, decides, and diagnoses; agents execute and report — delegate proactively (standing
authorization). Doc passes on this file route to `doc-worker` with surgical prompts.

## Tech stack
Plain HTML + CSS + JavaScript. No frameworks, no build step. Open `index.html` in a browser to
run — but **serve over http to see sprites**: double-click `start-game-server.bat` (serves
:8321 and opens the game), or `py -m http.server 8321`. The M15 runtime sprite pipeline needs
canvas pixel access, which browsers block on `file://`, so a plain double-click of `index.html`
still runs the game (logic + saves intact) but shows letter/placeholder art instead of sprites.
Shipping the game to players who can't run a server is **M17: distribution & packaging** (see
`MILESTONES.md`) — deferred to end-of-project. **Players must never run a server.**

## File structure
- `index.html` — page structure and UI elements
- `style.css` — medieval dark theme styling
- `game.js` — all game logic
- `tools/balance-sim.js` — Node balance simulator (`node tools/balance-sim.js`): models a
  greedy player at 1× with a mirror of game.js constants and a port of the combat engine.
  Rerun for any balance change. **Keep its constant tables in sync with game.js.**
- `tools/process-art.html` / `tools/plot-placer.html` / `tools/scene-prototype.html` — art
  pipeline and layout tools
- `tools/blender/` — **the art pipeline going forward** (user decision 2026-07-31). Python
  that models and renders sprites, buildings and the backdrop as 3D pixel art, driven over
  the Blender MCP connection with no manual modelling. Renders go to the gitignored
  `tools/blender/out/`. **Read `tools/blender/README.md` before touching it** — it carries a
  dozen rules that each cost a real debugging round, and most of them are counter-intuitive
  (ramp stops go on a measured histogram, not evenly; terrain must be smooth-shaded; light
  azimuth differs per camera). Nothing here is wired into the game yet.
- `assets/` — sprites and audio; every committed asset file must be covered by a
  `assets/CREDITS.md` line (pre-commit enforced; run `git config core.hooksPath .githooks`
  once per machine)

## Engine gotchas (violations caused real, expensive bugs)
- `tick()` is pure simulation — never touch the DOM from the tick path; painting lives in the
  requestAnimationFrame loop (`renderFrame`/`renderAll`).
- Memoized panel strings must contain NO per-second-changing values (countdowns, live costs,
  affordability states) — those live in fixed child elements updated in place by
  `refreshVolatileUI()`. Baking a ticking value into a panel string forces per-second innerHTML
  rebuilds that destroy buttons mid-click.
- Generated panels use `data-action="name:arg"` with the delegated dispatch registry, never
  inline `onclick` — a press must survive a rebuild between pointerdown and pointerup.
- Player-facing strings avoid em dashes (hard max one per text block) — standing user rule.
- No pipeline pixel-surgery on generated art: an image either works as delivered or gets
  regenerated (whole-image CSS cropping/positioning is fine) — standing user rule 2026-07-18,
  full art workflow in `M15_ASSET_SPECS.md`.
