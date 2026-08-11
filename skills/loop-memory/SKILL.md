---
name: loop-memory
description: Keep the run state a repeating or long-running loop needs between iterations — a progress file, decision log, known-failures list, run receipts, and a handoff note — on disk instead of in context. Use when work spans sessions or scheduled runs, a run must not redo what a prior run did, or context is filling before a handoff. Not for durable facts about the user (memory-conventions) or a one-off single-session handoff with no recurring loop behind it.
---

# Loop Memory

A loop's agent is wiped at the end of every shift. Whatever the next
iteration needs to avoid redoing work, repeating a mistake, or starting
blind has to be written down before the shift ends — not held in context,
because context does not survive. Files on disk that nobody re-reads are
not memory, they are archaeology: writing them once and never reading them
back is worse than not writing them, because the next run trusts a file
it never opens.

This is *loop* memory, not personal memory. `memory-conventions` owns
durable facts about the user, in the Obsidian vault, across every
project — preferences, decisions about how to work together, history that
outlives any one piece of work. This skill owns run state for one loop, in
one repo: progress, receipts, failures, and handoff, scoped to the work
and pruned as it ages.

| | `memory-conventions` | `loop-memory` |
|---|---|---|
| Scope | The user, across every project | One loop, in one repo |
| Lifetime | Durable — outlives the work | Per-run and per-work-item |
| Home | `$AGENT_MEMORY_VAULT/agent/facts/` | The repo, or a run directory beside it |
| Content | Preferences, decisions, history | Progress, receipts, failures, handoff |
| Volume | One fact per note, capped index | Grows every run; needs pruning |

Putting run state in the vault swamps an index that global rules require
reading every session, and it outlives its own relevance. Putting durable
preferences in a run log loses them the moment the log gets pruned. State
the boundary explicitly whichever direction a request comes from.

## Reach for this when

- Work spans more than one session, context window, or scheduled run.
- A run must not redo what an earlier run already did.
- Context is filling and a handoff or compaction is coming — if a task
  will need more than about 60% of the context window, start the handoff
  now, not when the window runs out.
- Someone needs to reconstruct what a loop did, and why, after the fact.

**Do not reach for it when:**

- The fact is about the user, not the work — hand off to
  `memory-conventions`; it belongs in the vault, not a run file.
- The task is a single session that finishes in one context. Creating
  progress files, receipts, or a handoff note for one-shot work is the
  over-trigger to guard against — it produces files nobody will ever
  re-read.
- The content is already recorded elsewhere: code structure, git history,
  and existing project docs are not memory. Copying them into a progress
  file creates a second source of truth that drifts from the first.
- The need is a one-off session handoff with no recurring loop behind
  it — write the handoff note (§ below) without standing up the other
  four files; it is not, by itself, reason to adopt this skill's whole
  file set.

## The file set

Five files, each with one job. Resist inventing a sixth; resist merging
two into one. Templates and field lists: [references/files.md](references/files.md).

| File | Holds | Written |
|---|---|---|
| Progress / plan | The work queue and current status | Every iteration |
| Decisions | Choices made, and why | On any non-obvious choice |
| Known failures | What has failed before, and the symptom that identifies it | On every failure |
| Run receipts | Per-run cost, terminal state, evidence, artifacts | Every run, including crashed ones |
| Handoff note | State, known issues, next action | Before compaction, model switch, or a long pause |

Keep conventions out of these files. "This project uses X for Y" is a
convention and belongs in the repo's own agent instructions, read once and
assumed stable. "We tried Redis Streams for the event bus and switched to
NATS over backpressure" is experience — a decision this skill's log
exists to hold. Conflating the two grows a file every iteration has to
re-read.

## Re-injection and watermarks

**Re-inject the plan every turn.** A plan written once at the start and
never re-read is gone by the third iteration — this is what makes file
memory survive context loss, compaction, and crashes: the loop's driving
prompt says "read the progress file, act," not "here is the plan" spelled
out inline.

**Carry an intake watermark** — the last-processed timestamp or item id,
written back after each item completes. Without one, a scheduled loop
reprocesses its whole backlog on every run. This is the most common silent
defect in scheduled work.

## Receipts

Write receipts from the wrapper or harness driving the loop, not from the
agent's own turn — so a receipt exists even when the run crashes, wedges,
or hits a budget cap mid-task. Each receipt: what the run did in a few
lines, what it chose and why, the evidence (test output, diffs, PR URLs),
and the numbers (tokens, cost, iterations, terminal state, artifacts
produced).

**Distinguish "ran and found nothing" from "did not run."** A green
process exit means the process exited, not that the task succeeded — a
receipt that only records exit code cannot tell those apart, and the next
run needs to.

A receipt does three jobs: it is the next run's watermark, the
postmortem's raw material, and the audit trail for "why did it do that on
Tuesday?"

## Known failures become a regression set

Each entry: the failing input, the wrong behavior, and the check that now
catches it. A body of real, accumulated entries is what stops a loop
re-committing the same mistake weekly — it is an eval substrate in a
different shape, not a new mechanism.

**Circuit breaker, before each retry:** check this file. If the same
failure has repeated, or the attempt cap for this item is hit, stop and
escalate instead of retrying again. The attempt cap itself is a loop-design
question (`loop-contract`, once it exists); the attempt *count* is state,
so it lives in this file.

## Handoff

Trigger a handoff on model switch, agent handoff, context compaction, or a
long pause — proactively at ~60% of the context window, not at the wall.
Contents, in this order (the order matters — later readers stop once
they've read enough):

1. The goal, restated in one sentence.
2. What is done, with evidence (commits, passing tests).
3. What is in progress, and precisely where it stopped.
4. **Known issues and dead ends already ruled out.** The highest-value
   line, because it is what stops the next context re-walking them.
5. The next concrete action.

**Edit the handoff doc in place; do not re-type it each iteration and do
not leave it stale.** A handoff doc that is not updated when state changes
is worse than none, because a successor trusts it. A stale brief read as
current is a known failure mode of this pattern — treat every re-read of a
handoff doc as suspect until you have verified its claims against the
repo's actual state (a named file exists, a test actually passes), not
just against what the doc says.

## Compose with a durable ledger; do not invent a second store

Where a durability layer already exists for a loop — one that survives a
process restart and can carry a payload, as opposed to a plain
one-bit signal — write into that ledger rather than a parallel set of
files. `jonhill90/agent-dotfiles` documents one such layer in `docs/SPEC.md`
§14 and `docs/loop-engineering.md`: a signal (like a `tmux wait-for` call)
is ephemeral and carries one bit, a ledger row survives a restart and can
carry the receipt itself. The five files above are the *content* this
skill says a loop should keep; where a ledger already exists to hold that
content durably, use it as the home instead of a new flat file.

## Hazards

- **Staleness.** A file naming a path, flag, or function records what was
  true when written. Verify against the repo before acting on it, the same
  way `memory-conventions` requires for vault facts.
- **Concurrent writes.** Two agents writing one file produce
  last-write-wins corruption. Partition by owner, or make writes
  append-only with attribution.
- **Growth.** Every file here grows. Name a prune rule per file — see
  [references/files.md](references/files.md) — or the progress file
  becomes the thing nobody reads.
- **Secrets.** State files are often committed. CI logs and alert payloads
  can carry credentials; redact before writing.

## What this skill is not

- Not `memory-conventions` — durable facts about the user go to the vault,
  one fact per note, with an index line. A "remember this about me"
  request hands off there; it does not get a run file here.
- Not `primer` — re-orienting in the codebase each iteration is that
  skill's job. This skill only carries what the codebase does not already
  record.
- Not `loop-contract` — that skill (once written) decides *what* must be
  persisted, as a design question, before a loop starts. This one decides
  *how*, and holds the state once the loop is running.
- Not an excuse to write files nobody reads. If a file is not re-injected
  by the loop or read by the next run, delete it.

## Where this came from

Practice, not a measured result. The corpus this is drawn from names
persistent memory as one of the most underdeveloped fields across the
loops it reviewed, and the file set, re-injection rule, and 60% handoff
threshold above are its recommendations, not this skill's own
measurement — no run has yet compared a loop with this file set against
one without and scored the difference. Provenance:
[references/provenance.md](references/provenance.md).
