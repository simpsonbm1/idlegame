# AGENTS.md — non-Claude agent bootstrap

**Read `CLAUDE.md` first — it is the canonical project context** (orientation, tech stack,
engine gotchas, doc map). The design spec and source of truth is `DESIGN.md`; the milestone
tracker is `MILESTONES.md`; delegation conventions are `AGENT_DELEGATION.md`. This stub exists
so non-Claude agents get the non-negotiables without a second full copy drifting out of date.

Non-negotiables for any agent working here:

- **Nothing is "fixed", "resolved", or COMPLETE until the developer confirms it in-game.**
  Until then it is FIX ATTEMPTED / ⚠️ pending confirmation.
- **Ask before you commit or push — never automatic.** The developer decides when history is
  written.
- Design authority is `DESIGN.md`, never the current behavior of `game.js` — the code is a
  prototype being redesigned around the spec.
- `tick()` is pure simulation: no DOM access from the tick path. Painting happens only in the
  requestAnimationFrame loop.
- Player-facing strings avoid em dashes (hard max one per text block).
- Balance changes rerun `node tools/balance-sim.js` and keep its mirrored constant tables in
  sync with `game.js`.
