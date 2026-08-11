# Mechanisms — the ring model

Loop mechanisms sort by **who holds the restart button**. Anthropic's public
four-type vocabulary (turn-based, goal-based, time-based, proactive) is the
naming layer; the rings below are the mechanism underneath it. This file is
expected to rot faster than the contract in `SKILL.md` — that is why it is
kept separate. Verify current harness support before relying on any of it.

| Ring | Mechanism | Restart held by | Survives session close? |
|---|---|---|---|
| 0 | Inner agentic loop | The model | No |
| 1 | A model-evaluated goal check | A separate small evaluator | No (restored on resume) |
| 2 | Stop hooks / exit-code gates | The hook script's exit code | No |
| 3 | A user-facing "run every N minutes" loop command | A timer | No — commonly a fixed expiry (e.g. 7 days) |
| 4 | Headless / unattended run | The shell | Yes, no session at all |
| 5 | Cron / a managed scheduler | The OS or a hosted scheduler | Yes |

## When each ring is the right choice

| If | Then |
|---|---|
| Must survive the machine being off | Ring 5 — managed/cloud scheduling |
| Needs local files and the machine stays on | Local scheduled task (ring 4 or 5) |
| Long unattended grind | Ring 4 — headless, fresh context per pass, sandboxed |
| Condition is deterministic and repo-wide | Ring 2 — a code-enforced stop gate |
| Condition is judgeable from the transcript | Ring 1 — a model-evaluated goal |
| Watching something during a live session | Ring 3, or better, a push/event channel |

## Layering, not replacement

A production loop is usually several rings stacked by failure mode, not one
ring chosen and the rest discarded:

- **Fast path** — the normal-case mechanism (e.g. a backgrounded wait for
  the next signal), so the common case stays cheap and non-blocking.
- **Failure path** — something that fires when the fast path's signal never
  arrives: a crash, a wedge, a usage limit hit mid-run. A hook or an
  external watcher, not a blind retry.
- **Durability and payload** — state that survives a process restart and
  can carry more than one bit (a verdict, counts, a URL), because a
  transient signal can arrive lossy or racy.
- **Backstop only** — ring 5, restricted to noticing a lane has been in the
  same state too long and escalating to a human. Not the driver.

`jonhill90/agent-dotfiles` `docs/SPEC.md` §14 is one worked, measured
instance of this layering for a tmux-based supervisor/worker pattern, and
its constraint on cron's role (stall detector only, never the driver) is
carried in the body of `SKILL.md` rather than here, because it is a rule,
not a lookup fact.

## Per-harness scheduling entry points

Check these against current documentation before use — names, flags, and
availability change:

- **Claude Code**: a user-facing recurring-loop command with self-pacing or
  fixed-interval modes; cron-backed scheduled/routine agents for durable,
  machine-off survival; Stop hooks for failure-path detection.
- **Codex / other CLI agents**: headless/exec modes for unattended runs;
  check for an equivalent scheduled-agent or app-server mode before
  reaching for OS-level cron directly.
- **OS-level**: `cron`, `launchd` (macOS), `systemd` timers (Linux), or a
  hosted scheduler — use only as the ring-5 layer in the stack above, not
  as a substitute for the fast/failure/durability layers underneath it.
