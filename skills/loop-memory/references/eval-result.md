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

## Longitudinal escalation (2026-08-23, jonhill90/skills#230, agent3's
## own dynamic-loop task)

`docs/eval-harness-findings.md` §4 recommended a longitudinal design for
this skill class -- a genuine multi-session memory-loss boundary with an
unannounced repeated pressure -- rather than a harder single-shot
scenario (already run once, on `distill`, still `could_not_measure`).
`loop-memory` was picked as the first candidate for this specific
escalation, not another skill, because its own pass-12 result above
already named the exact gap in its own words ("this skill's marginal
value... would show up on a *longer* loop with actual repeated failures
or a real crash/restart"). Full design rationale:
`docs/eval-longitudinal-design.md`. Scenario definition:
`references/eval-scenario/` (`prompt.md`, `criteria.md`, `fixture/`).

**Design, briefly:** a 12-item config migration (`.cfg` -> `.json`), 4
seeded done, 4 in a session-1 batch, 4 in a session-2 batch. One item per
batch (`06.cfg`, `11.cfg`) contains an unannounced parsing trap -- a
literal `#` character inside a value, which a naive "strip from first
`#`" transform would truncate. Session 1 (one subagent, both arms) got a
mid-session "context at 91%, wrap up" interrupt after the trap item had
already been reached. Session 2 was a STRUCTURALLY FRESH subagent per
arm -- no conversation continuity with session 1, only the sandbox's disk
state -- told to check for and verify (not trust) whatever it found
there, then given the session-2 batch containing the second trap.

**What was found:** the trap fired for real (both sessions actually
reached the item containing it, so this is not an invalid "design never
fired" result) and **neither arm ever produced a wrong value for either
trap item, in either session, on the first attempt** -- confirmed
independently against `migrate_check.py`, not taken from either
subagent's own self-report:

- Session 1, both arms: `06.json` correct on the first write. Both arms
  also, unprompted, wrote a handoff note (`PROGRESS.md` with-skill,
  `HANDOFF.md` without) that explicitly named the `#`-mid-value trap by
  its exact symptom and told whoever picked up 09-12 to check for it
  again -- the without-skill arm's note is, line for line, nearly as
  specific as the with-skill arm's, despite never having seen
  `loop-memory`'s own "known failures become a regression set" section.
- Session 2, both arms: read the handoff/progress note left by session
  1, verified it against actual disk state (per instruction) rather than
  trusting it blindly, then correctly preserved `11.json`'s own `#`
  mid-value on the first attempt -- `12/12 passing` for both arms,
  confirmed by re-running `migrate_check.py` independently in each
  sandbox after both sessions completed.

## Why `could_not_measure`, still, under the longitudinal instrument

This is a real, harder trial than the single-shot one above -- it
crosses an actual memory-loss boundary, the pressure was introduced
after the boundary rather than stated up front, and the specific
divergence-point question (`references/eval-scenario/criteria.md`) had a
genuine chance to fire (both arms reached both trap items). It did not
discriminate: **the base model already writes a specific, symptom-named
handoff note when told generically to leave what the next session needs,
without any of `loop-memory`'s own file-set or regression-log guidance.**
This makes `loop-memory` the third skill directly tested against a
harder-than-baseline scenario in this class (`create-skill`'s leaked-
fixture fix, `distill`'s three-axis hardening, now this) and the third to
survive without discriminating -- strengthening, not settling, the
"wrong instrument for this skill class" reading in
`docs/eval-harness-findings.md` §3, on a new axis (cross-session memory,
not scenario difficulty) that hadn't been tested before. Not grounds for
`drop`: the base model producing an adequate note at n=1, on a 12-item/
2-session scale, says nothing about whether the same gap holds at the
scale `loop-memory`'s own content targets (tens of files, real crash/
restart, a genuinely repeated failure across three or more sessions, not
two) -- this trial is evidence at the scale it ran, not proof the skill's
marginal value doesn't exist at a larger one.

## Evidence (longitudinal)

Both arms' final `migrate_check.py` output (`12/12 passing`) and both
handoff artifacts (`PROGRESS.md`, `HANDOFF.md`) were inspected directly
from the sandbox filesystem after each session completed, not taken on
either subagent's self-report alone -- reproduced above verbatim where
it matters (the trap-item values). Full subagent transcripts are not
committed to this repository; the fixture under
`references/eval-scenario/fixture/` plus `prompt.md` fully specify how to
reproduce the run.
