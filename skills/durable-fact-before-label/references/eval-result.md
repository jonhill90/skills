# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop (estate-loop/agent-b2.md), superseding this file's own third-pass
result. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario itself is committed at
`skills/durable-fact-before-label/references/eval-scenario/` so it can
be re-run.

## Verdict: could_not_measure (still)

## A real environment defect found and fixed before trusting the first
## attempt at all

The first attempt at this pass produced a broken pair: the "without"
arm returned after 1 turn and 0 tokens -- a harness-level failure, not a
real run. Investigating by hand (per this task's own instruction: read
the actual transcripts/evidence before trusting a printed number) found
the cause was upstream of the harness entirely: **`durable-fact-before-
label` was never installed on this machine's shared skills path at all**
(`~/.claude/skills/` symlinks 35 of this repo's 40 skills; this is one
of the 5 that isn't, confirmed by `comm` against the real skills/
directory -- a pre-existing gap, not something this pass's own eval run
broke). The "with" arm in that first attempt was silently *also* a
without-the-skill run; the whole first pair was invalid and is not
recorded as evidence for or against this skill.

Fixed by symlinking the skill in for the duration of a real run,
re-running both arms properly, then **removing the symlink again
afterward** -- this pass does not change what is globally installed on
this machine; that is a separate, out-of-scope gap worth a human
decision, not something to silently fix as a byproduct of an eval run.
Confirmed restored: `~/.claude/skills` symlinks the same 35 skills after
this pass as before it.

## The new scenario

`docs/eval-harness-findings.md`'s Cause A named this skill's own
third-pass scenario as too easy: the bug was two adjacent lines to swap
in an otherwise-empty `finalize.py`, legible from the code alone with no
investigation. This pass's fixture (`reconcile.py`, ~100 lines) buries
the same mistake -- `release_claim()` called before `write_result()` --
inside `process_one()`, itself called from a realistic sweep with
argument handling, retry/backoff, and logging around it. A
`crash-report.txt` describes the symptom the way an operator would (a
released claim, a missing result file) without pointing at a line.

## What was measured

Run twice, live, same task, same fixture, once with the skill genuinely
installed (see above) and once with it removed via the harness's
`no-skill:<name>` arm:

- **With the skill:** reordered the two calls correctly --
  `write_result()` then `release_claim()`. 13 turns, 344,343 tokens.
- **Without the skill:** same correct reorder. 9 turns, 249,512 tokens.

Token ratio 1.38x, turn ratio 1.44x -- both inside the harness's own
×1.5 tolerance. Both arms actually found and fixed the real bug (checked
via `ast`, not a text search -- `write_result`/`release_claim` are also
function DEFINITIONS earlier in the file, so a plain string search would
find those instead of the calls inside `process_one()` specifically; the
scorer parses the function body and compares the two calls' line
numbers).

## Why could_not_measure, not drop

Both arms correctly diagnosed and fixed a bug buried in a realistic
reconciler, with no adjacent-lines shortcut available this time. Nothing
failed. The cost delta is real but inside tolerance, so the mechanical
scorer's own "solved identically" branch applies -- and per this
skill's own second-pass result and `docs/eval-harness-findings.md`'s
Cause A, that reads as `could_not_measure`, never `drop`: a drop verdict
requires an eval that ran and failed, and this one didn't.

## What is not evidenced

Whether a model finds this ordering bug reliably in a LARGER reconciler
closer to this skill's own second cited incident
(`reconcile-lane-completions` overwriting 133 result files) -- ~100
lines with one obvious sweep function may still be within reach of
careful, unassisted reading. A multi-file reconciler with the ordering
bug several calls deep across module boundaries would be a harder test.
