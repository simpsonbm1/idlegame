# Model-tiered subagent delegation — Idle Kingdom

**Why this exists.** Subscription usage is consumed at each model's own rate, and the main
conversation's model can't switch mid-session. The main session stays on the strongest model
(the orchestrator) for design, balance judgment, and debugging, and dispatches self-contained
subtasks to agents pinned to cheaper models. Same pattern as askamods
(`askamods/docs/agent-delegation.md`); this doc is the idlegame-specific routing.

## Roster

Project agents (`.claude/agents/` — prefer these for matching tasks):

| Agent | Model | Delegate | Never delegate |
|---|---|---|---|
| `game-implementer` | Sonnet | A fully-designed code change: edit game.js/index.html/style.css, `node --check` gate, sync the sim mirror, report | Design/balance decisions; debugging with an unknown root cause |
| `balance-analyst` | Haiku | Run `node tools/balance-sim.js`; report walls/gauntlet/grind as deltas vs the CLAUDE.md baseline | Interpreting WHY a number moved, or choosing new tuning values |
| `browser-verifier` | Sonnet | A written checklist against the running game: console gate, state assertions, interactions; evidence-bearing PASS/FAIL report | Feel/art/design judgment; unscripted "poke around and see" |

Generic user-level agents (`~/.claude/agents/`, available everywhere): `implementer` (Sonnet),
`doc-worker` (Haiku — CLAUDE.md milestone bullets and doc-sync passes with facts supplied),
`log-triager` (Haiku). Built-in `Explore` inherits the session model — pass a cheap model
explicitly (haiku/sonnet) for routine searches; on an expensive main session an unpinned
Explore burns orchestrator-rate usage.

## Orchestrator tier — Fable normally, Opus in fallback weeks

"Main thread" in this doc means the session's strongest *available* model, not Fable by name:
normally Fable, and **Opus becomes the orchestrator for the remainder of a week once Fable's
budget is spent**. Nothing else changes — the agents are pinned to absolute tiers
(Sonnet/Haiku), so every routing rule here reads identically under either orchestrator, and
the SESSION_HANDOFF.md discipline already covers continuity across the switchover.

Where Opus fits as a *subagent* (rate arbitrage exists only while Fable orchestrates; under an
Opus orchestrator an Opus dispatch saves no rate and is worth it only to keep bulk out of the
main context):
- A gnarly-but-fully-specified implementation → `game-implementer` with a per-invocation
  model override of `opus` (the invocation parameter beats frontmatter).
- A meaty self-contained investigation whose inputs fit in the prompt (e.g. "reproduce this
  deterministic sim divergence and report the cause") → general-purpose agent on `opus`.
- An independent second-opinion review of a plan or diff, where independence from the main
  conversation is itself the value.

No roster agent pins Opus, deliberately: work mechanical enough to pin is Sonnet/Haiku-shaped,
and work needing more than Sonnet usually also needs conversation context no subagent has. If
one of the shapes above recurs, promote it to a named agent then.

## Division of labor

**The main thread plans, decides, and diagnoses; agents execute and report.** Stays on the main
thread: design and balance decisions, playtest interpretation, tuning-value choices, root-cause
work on novel bugs, art direction, anything conversational with the developer, and all commits
(never delegated; the ask-first policy is unchanged). Routine shapes to delegate proactively:

- Planned multi-edit change → `game-implementer`
- Any balance-constant change just landed → `balance-analyst` (background it, keep working)
- Mechanical browser pass on landed work → `browser-verifier` with a written checklist
- CLAUDE.md milestone bullet / M-doc updates with facts supplied → `doc-worker`, surgical
  prompts (exact anchor text → exact replacement)
- Digest long output → `log-triager`; multi-site code search → `Explore` with a cheap model

Inline is fine when it's genuinely cheaper: single-file micro-edits, one-off greps, quick
targeted reads. Delegation overhead (spawn + report) makes tiny tasks cost more delegated than
done inline.

## The browser-verification convention and subagent reports

The project's "browser-verified, zero console errors" convention predates delegation. Policy:
**mechanical checks** (console-error gate, state assertions, interaction outcomes,
render-presence checks) are satisfied by a `browser-verifier` report **only when it carries the
actual evidence** (what was read and what it said), and docs record them as browser-verified
via the verifier. **Feel, visual quality, pacing, and anything the milestone log would call a
user playtest are NOT delegable** — those acceptance gates stay with the developer and the main
thread. During the trust ramp (the first few verifier runs) the main session spot-checks one
verifier claim per report before relying on it.

## Delegation-prompt checklist

Subagents see the CLAUDE.md files and a git snapshot, NOT the conversation, and they cannot ask
the user questions. Every prompt must therefore contain:

1. Exact files and exact changes — decisions made, not "figure out".
2. For balance changes: the constants touched, and the sim-mirror names if known.
3. For the verifier: an explicit checklist — per item, what to do and what counts as PASS;
   plus whether a save wipe is authorized (default NO — the real playthrough lives in
   localStorage on :8321).
4. Any conversation-derived facts the agent needs, restated.
5. What to report back (a summary, not raw output).
6. No open decisions.

## Typical cycle (orchestrator = Fable, or Opus in fallback weeks)

```
Orchestrator: design the change + acceptance criteria     — main thread
  → game-implementer (Sonnet): exact edits, node --check, sim mirror
  → balance-analyst (Haiku, background): rerun sim, deltas vs baseline
  → browser-verifier (Sonnet): written checklist, evidence report
  → Orchestrator: read reports, decide next step
  → doc-worker (Haiku): CLAUDE.md bullet with the verified facts
  → Orchestrator: ask user, then commit (never delegated)
```

## Runtime notes & gotchas

- Agents run in the background by default; fire independent ones together and keep working.
  Resume a finished agent with its context intact (SendMessage) instead of respawning it.
- Model resolution: per-invocation param → agent frontmatter → inherit. Frontmatter accepts
  haiku / sonnet / opus / fable / inherit.
- Every spawn re-reads all CLAUDE.md levels (cheap at Haiku/Sonnet rates), and prompts and
  reports consume main-thread context — keep both tight.
- **First-use restart:** `.claude/agents/` was created 2026-07-19; the file watcher only picks
  up agent dirs that existed at session start, so the first session after that date needs one
  Claude Code restart. Afterwards edits hot-reload.
- **Why there is no enforcement hook** (process-hygiene honesty): what to delegate is a
  judgment call, and the harness-executed mechanism here is the roster itself — agent
  `description` fields drive automatic matching; this doc plus the CLAUDE.md pointer are the
  prose layer. A PreToolUse guard (e.g. blocking main-thread `node tools/balance-sim.js`)
  cannot distinguish the main thread from the very subagent it routes to, so it would break the
  flow it exists to enforce. Revisit if non-delegation keeps recurring — the detectable-signal
  candidates are sim runs and long browser sequences appearing in the main transcript.

## Status

**Verified 2026-07-19** — full smoke pass run the same day the roster was created:

1. Roster registration after restart: PASS (all six agents listed).
2. `balance-analyst` (Haiku): PASS with a lesson. Ran the sim and matched the campaign-arc
   walls correctly, but headlined a gauntlet "band violation" off a single noisy sample (the
   gauntlet then used only 60 Monte Carlo trials). The resume path (SendMessage to a finished
   agent) was verified in the correction round. Agent file hardened: output-section map,
   verbatim-quote rule for violation headlines, rerun-near-band-edges rule.
3. `browser-verifier` (Sonnet): PASS on all six checklist items — the Browser pane IS
   reachable from a subagent (console gate, sprite count 35, state reads, a real click that
   advanced the tutorial one beat). Two learnings baked into the agent file: the
   preview_start url-fallback when :8321 is already served externally, and the rAF-throttling
   artifact on backgrounded automation tabs. Cost gauge: ~35 tool calls for a first pass that
   included diagnosis detours.
4. `game-implementer` (Sonnet): PASS — first real dispatch raised the gauntlet's Monte Carlo
   trial count (`finalSiegeRate` 60 → 500 in tools/balance-sim.js, cleanly scoped; the full
   sim still runs in ~0.5s), so one sim run now gives a conclusive gauntlet read (~±2pp
   instead of ~±9pp). `doc-worker` (Haiku): PASS — wrote this section.

Measurement note from the smoke (no game change involved): at 500 trials the full-kit
gauntlet reads ~24–29%, i.e. the true rate sits at the low end of the documented 27–38% band,
which was itself derived from 60-trial samples. Flagged to the developer; the acceptance gate
remains the real playthrough.
