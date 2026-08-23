# Eval result

Recorded 2026-08-22, seventh pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/dispatch-brief/references/eval-scenario/` so it can be re-run.

## Verdict: keep (n=2, replicated)

## A real environment defect, caught before the first live run counted

`dispatch-brief` was not installed on this machine's shared skills path
at all (`~/.claude/skills/` symlinks 35 of this repo's 40 skills; this
was one of the 5 that weren't -- pre-existing, not something this pass
broke, same class of gap `durable-fact-before-label`'s own eval-result.md
already documented from the prior pass). Discovered before trusting the
first run's own "with" arm: symlinked the skill in for the duration of
this pass's real runs, then **removed the symlink again afterward** --
this PR does not change what's globally installed; that's a separate,
out-of-scope decision for a human to make deliberately.

## The scenario

This skill's own trigger case: composing the brief that hands a bounded
bugfix-plus-guard task to an unattended lane. The fixture is a small,
real bug (`parse_amount("125000.00")` silently truncates to `1250.0` --
a factor-of-100 error, evidenced in `evidence.log`) and a misleading
in-code comment that describes the bug incorrectly. The task: write
`brief.md` for the lane that will fix it -- not fix it directly.

## What was measured, twice, and read in full both times

Run twice (a deliberate second pair, per this task's own instruction not
to trust a strong first-pair signal without replication), same task,
same fixture, once with `dispatch-brief` installed and once with it
removed via the harness's `no-skill:<name>` arm:

- **Pair 1:** WITH -- pasted the exact measured numbers, demanded the
  mutation in both directions explicitly, named silent under-reporting
  as the worse failure direction, forbade six specific ways to fake
  green, and included a section titled `## "Could not measure" is a
  real, complete verdict`. WITHOUT -- pasted the evidence and root-caused
  the bug correctly, but asked for only ONE mutation direction (before/
  after the fix, never "break it the opposite way too") and never once
  said an inconclusive result was an acceptable outcome to report.
- **Pair 2 (replication):** same shape. WITH again included an explicit
  `## 5. "Could not measure" is a complete verdict` section. WITHOUT
  again asked for both directions this time (that specific observable
  did not replicate identically) but again never once permitted "could
  not measure" as an outcome -- grepped the full text by hand both times
  to confirm, not just trusted the scorer's regex.

**The one signal that replicated identically across both independent
pairs**: the skill-installed brief explicitly states that an
inconclusive result is a real, acceptable thing to report; the no-skill
brief never does, in either pair. The other observable this scenario
checks (explicit two-directional mutation language) moved in pair 1 but
not pair 2 -- read as noise on that axis, not part of the verdict.

## Why keep, not improve

Both pairs solved the underlying bug-diagnosis identically well -- the
skill did not change whether the brief was thorough or correct on the
parts both arms got right. It changed something narrower and specific:
whether the brief tells its own future reader that "I could not
determine this" is a real, complete answer rather than a failure to
explain away. That is exactly this skill's own rule 5
("allow 'could not measure' as a real verdict"), and it did not appear
unprompted in either no-skill run. A behavioral difference that
reproduces across two independent pairs, on the exact axis the skill
claims to own, is `keep`, not `improve` -- there is no cost delta to
weigh here; the outcome itself moved.

## What is not evidenced

Whether this specific difference (naming "could not measure" as
acceptable) changes what actually happens downstream -- whether a real
lane given the no-skill brief would in practice force a false pass/fail
rather than genuinely getting stuck and reporting so. This result is
about what the BRIEF says, not about a lane's behavior under it; testing
that would need a second-order scenario (dispatch a lane against each
brief and see what it does when it genuinely cannot measure something),
which this pass did not build.
