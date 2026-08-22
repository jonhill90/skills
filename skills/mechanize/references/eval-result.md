# Eval result

Recorded 2026-08-22, closing one skill of jonhill90/skills#230's "26 of 35
never evaluated" gap, run against the keep/improve/rename/drop harness
that landed in the agent-evals repository (not published here; see
"Scope" above). This is a second file alongside `eval-case.md` (the test
case definition) — this one states the verdict and what was measured, not
the scenario itself.

## Verdict: could not measure a reliable skill-attributable difference

Not "keep," not "drop" — the harness's own automated scorer returned
`keep`, and this file explains why that number is not trusted as
reported, per this skill's own neighbor `verify-the-instrument`'s
discipline: a verdict from a check is a claim about the checker too.

## What was measured, and what went wrong with measuring it

One scenario, `eval-case.md`'s own reference case turned into a runnable
fixture: eleven ticks of one lane's pane output, ten of which reach the
same stalled/not-stalled answer from a fixed three-fact rule, and an
eleventh that looks identical to a stalled tick by those three facts but
is actually a shell waiting on a human (a `git rebase -i` editor). The
task asked for a decision on how the check should be implemented going
forward, written to a file.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm. Reading
the two written decisions by hand (not the automated scorer) found them
close to equivalent in substance: both independently identified that one
of the three input facts was actively wrong at the failing tick, both
proposed a deterministic classifier to replace the three-fact rule, and
both reserved some residual judgement for cases their own rule could not
place. The run without the skill used the words "classifier"/"detector"/
"design" throughout and never used the words "script"/"tool"/"mechanize"/
"automate" even once — which is what actually produced the scorer's
`keep` reading: its keyword match for "did this recommend mechanizing
anything" only recognized one vocabulary and missed an equivalent
proposal phrased in different, still entirely reasonable, words.

## Why this is reported as "could not measure," not "drop"

Two independent problems compound here, and neither alone would justify
stopping:

1. The scenario itself did not discriminate — a sufficiently capable
   model reached a materially similar, sophisticated engineering answer
   whether or not the skill was present, on this fixture.
2. The scorer built to read the difference has a demonstrated blind spot
   (natural-language paraphrase of "mechanize") that a hand read caught.

Reporting `keep` off a demonstrably blind scorer would repeat exactly the
failure this skill's own neighbor exists to catch. Reporting `drop` would
go the other way on the same bad instrument. Neither is warranted; a
rerun needs either a harder scenario (one where an unaided model is
plausibly worse) or a scorer that reads intent rather than a fixed
keyword list before this skill gets a verdict that means anything.

## What is not evidenced

Whether `mechanize` changes behavior on ANY task remains untested — this
is a report that one attempt did not produce a trustworthy answer, not
that the skill has no effect.
