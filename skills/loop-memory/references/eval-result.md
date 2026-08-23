# Eval result

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (twelfth pass,
the first run after #245's per-skill log split and #246's mechanical
install check). Run locally (no private-harness dependency): two isolated
sandbox checkouts, one per arm, each running an independent subagent.

## Verdict: could_not_measure (n=1)

## Failure this skill exists to prevent

A loop nearing context exhaustion ending its turn without writing
resumable state to disk, so the next iteration (with no memory of this
one) redoes finished work, repeats a known mistake, or has nothing to
resume from.

## What was measured

Install check run first: `loop-memory: OK -- installed copy at
/Users/jon/.claude/skills/loop-memory matches skills/loop-memory`.
Trusted the run.

Sandbox: a 50-file mechanical migration task (`TASK.md`), seeded 20/50
files already correctly migrated on disk (not just claimed --
inspectable). Each arm was told to verify on-disk state before
continuing (not trust any summary), migrate a few more files, then told
via a system message that context was at 91% and compaction/restart was
imminent, with an explicit reminder that the next instance picking up
the work would have no memory of this session.

Run twice: once with `loop-memory`'s own SKILL.md given to the agent as
context to follow, once without any mention of it -- otherwise identical
prompt, identical sandbox.

## What was found

**Both arms wrote resumable state to disk before stopping** rather than
only replying in chat -- the specific failure this skill exists to
prevent did not occur in either arm:

- With the skill: migrated items 021-024, verified 018-024 directly on
  disk rather than trusting `TASK.md`'s own claim about 001-020. Wrote
  two separate files matching the skill's own file-set taxonomy --
  `run/progress.md` (watermark: last completed / next item) and
  `run/handoff.md` (goal, evidence, in-progress state, explicit warning
  to re-verify the watermark against disk rather than trust the note
  blindly -- the skill's own "treat every re-read of a handoff doc as
  suspect" hazard, reproduced unprompted).
- Without the skill: migrated items 021-023, independently verified
  count against disk with a `for` loop (explicitly noting a single glob
  wouldn't catch all 50, a gotcha it then recorded), and wrote one
  consolidated `PROGRESS.md` covering current state, the exact transform
  pattern, the same verification-loop gotcha, and an explicit resume
  point.

Structural difference: the with-skill arm split into two files
(progress vs. handoff) matching the skill's own five-file taxonomy; the
no-skill arm produced one file covering the same ground. Neither is
obviously worse at the one property actually being tested here (does
state survive to the next instance) -- both would let a fresh instance
resume correctly.

Cost: 40,551 tokens / 11 tool calls with the skill, 36,235 tokens / 5
tool calls without -- 12% more tokens and more than double the tool
calls with the skill, which tracks the two-file split (more Write calls)
rather than any difference in outcome quality.

## Why `could_not_measure`, not `improve` or `drop`

Identical, correct outcome on the property under test (state persisted
to disk, resumable by a memoryless instance) in both arms: `docs/
eval-harness-findings.md`'s "Clean no-discrimination" bucket (§4). The
base model already writes *something* usable to disk when told
explicitly that context is exhausting and a fresh instance is next --
this skill's marginal value (the specific five-file taxonomy, the
watermark discipline, the "known failures becomes a regression set"
practice) would show up on a *longer* loop with actual repeated failures
or a real crash/restart, not a single-turn stop-and-summarize. Not
grounds for `drop`: a scenario built around a genuine multi-run
crash-and-resume, or one where a known failure needs to be caught by a
regression file rather than merely alluded to in a handoff note, would
be a stronger test of what this skill actually adds. This one measured a
capability the base model already has.

## Evidence

Both full transcripts (sandbox definitions, prompts, and both arms'
final reports and the files they wrote) are reproducible from the eval
pass's own worktree setup script; not attached verbatim here to keep
this file short. Sandbox structure and prompts as described above are
the complete specification needed to reproduce the run.
