# Eval result

Recorded 2026-08-22, third pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that landed in the agent-evals repository (private evaluation evidence, not published here). Tracked in docs/eval-status.json alongside this
pass's other two results.

## Verdict: improve (n=1 — rerun before trusting further)

## A scorer defect found and fixed before trusting this number

The harness's own scorer initially returned `neither arm solved it` for
BOTH arms — a false reading. It checked `intake_watermark` and
`stop_conditions` for non-placeholder *string* content, and both real
runs answered with rich, structured objects (a keyed ledger design, a
list of named stop conditions with terminal states) rather than plain
strings — content the scorer's own first version silently treated as
empty because it never recursed into a dict. Read by hand, both answers
were genuinely excellent and complete. The scorer was fixed to recurse
into nested objects/arrays before this verdict was trusted, and both
saved transcripts were rescored from the already-run artifacts — no
second live run was needed. This is recorded here rather than smoothed
over, the same discipline `verify-the-instrument`'s own result file (this
pass's predecessor) used.

## What was measured

One scenario testing the two fields this skill's own SKILL.md names as
causing "the most damage when left blank": a request to design an
unattended file-watching loop, phrased with no mention of deduplication
or stopping — asking only for `design.json` with named fields including
`intake_watermark` and `stop_conditions`.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm, after
the scorer fix: both arms produced a real, non-placeholder watermark
(a content-hash ledger keyed by file identity, explicitly rejecting a
bare mtime watermark for the exact reasons this skill's own text gives)
and multiple real stop conditions (operator stop, consecutive-failure
circuit breaker, poison-item quarantine, budget ceilings, a no-progress
watchdog). Outcome was a wash. Cost was not: the skill-installed run used
about 1.6x the turns of the run without it (8 vs. 5; tokens close, 1.1x).

## Why "improve," not "keep" or "drop"

Same reasoning as this pass's other two results: identical correct
outcome plus a real turn-count delta is `improve`, not `keep` (nothing
changed about whether the design was complete) and not `drop` (nothing
failed — quite the opposite, both answers were unusually thorough).

## What is not evidenced

Whether Opus 5 names a real watermark and real stop conditions by
default on this kind of request regardless of the skill — the outcome
axis did not move here, matching this pass's other two results. A
weaker model, or a request phrased to more strongly invite skipping
these fields (e.g. one that explicitly asks only for the parts it
mentioned), would be a harder test of whether the skill's own naming of
"the two fields that cause the most damage when left blank" changes
anything.
