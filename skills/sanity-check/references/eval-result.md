# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop (estate-loop/agent-b2.md), superseding this file's own fourth-pass
result. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario itself is committed at
`skills/sanity-check/references/eval-scenario/` so it can be re-run.

## Verdict: could_not_measure (still)

## The new scenario

`docs/eval-harness-findings.md`'s Cause A named this skill's own
fourth-pass scenario as too easy: the planted mismatch (47 vs. 9, ~5x)
was large enough that a glance revealed it, without needing to actually
re-derive the number. This pass's fixture narrows the gap to 134
(claimed) vs. 131 (the real sum of seven daily figures in
`weekly-failures.log`) -- a ~2% difference, plausible as a rounding slip
or a small arithmetic error, not visible without actually adding the
seven numbers.

## What was measured

Run twice, live, same task, same fixture, once with `sanity-check`
installed and once with it removed via the harness's `no-skill:<name>`
arm:

- **With the skill:** read `weekly-failures.log`, ran
  `awk '{s+=$4} END {print "sum:", s, "days:", NR}'`, got 131, stated
  the draft needs correction with the arithmetic shown. 5 turns,
  132,443 tokens.
- **Without the skill:** same -- read the log, summed it (`18 + 22 + 15
  + 19 + 24 + 17 + 16 = 131`), same correction, same evidence shown.
  5 turns, 129,903 tokens (1.02x -- inside the harness's own ×1.5
  tolerance).

## Why this is still could_not_measure

Even at a 2% gap requiring an actual sum rather than a glance, both arms
did the arithmetic and caught it. This is a real result about Opus 5 at
this model tier on this specific kind of check (summing seven small
integers from a log) -- not evidence the skill's actual target (an
inherited, unsourced FIGURE with no source at all to check, this skill's
own TRIGGER clause) doesn't matter. This scenario, even narrowed, is
still fundamentally "there is a source, and checking it is a single
`awk` call" -- exactly the kind of check the skill's own text says NOT
to reach for it for ("if a command would settle the question... run the
check"). The skill's own hardest case -- a number with NO command that
could settle it, only a search that may fail to turn one up -- has not
been built as a fixture yet.

## Why could_not_measure, not drop

Nothing failed in either arm; both produced the correct, evidenced
correction. Matches this skill's own prior result and
`docs/eval-harness-findings.md`'s Cause A.

## What is not evidenced

Whether this skill changes behavior on its own actual hardest case: a
number with no single source to check at all -- where the correct move
is naming the absence of provenance as the finding itself, not running
one more command. That is a harder, and more faithful, fixture than
either this pass's or the prior pass's own scenario, and has not been
built yet.
