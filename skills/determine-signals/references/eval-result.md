# Eval result

Recorded 2026-08-22, third pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that landed in the agent-evals repository (private evaluation evidence, not published here). Tracked in docs/eval-status.json alongside this
pass's other two results.

## Verdict: could not measure a reliable skill-attributable difference — not dropped

The harness's own mechanical decision table returned `drop` (both arms
solved it identically, cost within tolerance). Not passed through — see
`durable-fact-before-label`'s result file, recorded the same pass, for
the identical reasoning: nothing failed, so `drop` is not warranted.

## What was measured

One scenario, built from this skill's own headline rule ("prefer live
system state over any stored record when they disagree"): a stale
memory-style note claiming a ledger path that a migration had since
changed, and the box's own live config holding the current, correct
path.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm: both
arms read the live config rather than trusting the note, and both
reported the correct, current path. Cost was essentially identical
(tokens 95,055 vs. 95,651; turns 4 vs. 3).

## What is not evidenced

This scenario's live/stale conflict was unambiguous — one file plainly
newer and structurally marked as an authoritative config, the other a
dated note. A scenario where the two sources disagree more subtly (no
migration timestamp, a note that reads as equally current) would be a
harder test of whether this skill's ordering rule changes anything a
capable model wasn't already going to do.
