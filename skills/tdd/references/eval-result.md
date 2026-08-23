# Eval result

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (eleventh
pass). Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at `skills/tdd/references/eval-scenario/`
so it can be re-run.

## Verdict: could_not_measure (n=1)

## The scenario

`tdd`'s own trigger case verbatim: "building a new function... from
scratch and no prior bug is being reproduced" -- the boundary this skill
itself draws against `failing-test-first`. Fixture: an empty
`duration.py` and an empty test file, prompt asks for a new
`humanize_duration(seconds)` function with two worked examples. Scored
on ORDER, not just presence: the run's own tool_calls are inspected to
find the first call that writes a real assertion referencing
`humanize_duration` into the test file, and the first call that adds
`def humanize_duration` to the implementation file, and checks the test
came first.

## What was measured

Run once, same task, same fixture, once with `tdd` installed and once
with it removed via the harness's `no-skill:<name>` arm: both arms wrote
the function correctly (both worked examples resolve to the expected
strings) and both wrote the test before the implementation, by actual
tool-call order -- with-skill: test at call 5, implementation at call 7;
without-skill: test at call 3, implementation at call 5. Cost was close
(256,252 vs. 269,998 tokens, ~1.05x; 11 vs. 8 turns, ~1.38x) -- inside
the harness's own ×1.5 tolerance on both axes, not close enough to the
flag to warrant a replication per this pass's own instruction to
replicate only a strong-looking signal.

## Why could_not_measure, not drop

Both arms independently chose to write the test first, unprompted by
the skill in the without arm's case -- a real result about Opus 5's own
default habit on a small, clearly-scoped greenfield function, not
evidence the skill changes nothing. Nothing failed in either arm.

## What is not evidenced

Whether the same test-first ordering holds on a larger or more
ambiguous greenfield task -- one with several interacting new functions,
or a request phrased to invite jumping straight to an implementation
(e.g. "just write me a working `humanize_duration`"). This scenario's
own two-worked-examples framing may itself invite writing assertions
first regardless of the skill.
