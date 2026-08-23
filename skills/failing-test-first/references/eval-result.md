# Eval result

Recorded 2026-08-23, tenth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1, scorer bug found and fixed)

## Criterion update for this pass

As with this pass's other two picks, no remaining unevaluated candidate
had a documented incident in its own SKILL.md text (the bar retired
after nine passes of confirming this by reading, per this pass's own
brief). `failing-test-first` was picked for its own precise sequence
and completion gate instead (`SKILL.md`: "do not fix first and backfill
the test"; "The fix is not complete until a test that failed before the
fix passes after it. Report both runs (red, then green) as evidence.").

## What was measured

A one-line off-by-one bug (`is_free_shipping` uses `>` where the stated
policy needs `>=`, so an order of exactly $50.00 doesn't get free
shipping) with no existing test suite in the fixture. Scored on:
whether the test file was created before the source fix, whether a
failing run was actually executed before the fix landed, and whether
both the red and green results were reported.

## A real scorer bug, caught by hand-reading a run that looked wrong

Both arms scored `test_before_source=False` on the first run —
surprising, since a scenario this precisely specified should be easy
for a capable model to get right. Hand-reading the actual tool-call
sequence (this pass's own standing instruction: check any signal that
looks strong or surprising against the raw transcript) showed both runs
did the textbook-correct sequence exactly: write `test_shipping.py`,
run pytest (fails), edit `shipping.py`, run pytest again (passes). The
scorer's own path-matching regex was the bug: `_SOURCE_PATH` was
`shipping\.py$`, which also matches `test_shipping.py` — the test file's
own name ends in "shipping.py" too — so `_first_index` returned the test
file's index as the "source file" index, making `test_before_source`
compute `False` on every correctly-ordered run.

Fixed with a negative lookbehind (`(?<!test_)shipping\.py$`) and
re-scored the same saved transcripts — both arms flipped to
`solved=True`, matching what hand-reading the tool-call list already
showed.

## Why `could_not_measure`, not `keep`/`improve`/`drop`

Once corrected, this is an identical-outcome pair — both arms followed
the skill's own sequence exactly, with or without it installed.
Recorded `could_not_measure` per docs/eval-harness-findings.md rather
than the mechanical `drop` an identical-outcome pair would otherwise
produce.

## What is not evidenced

Whether a bug that more plausibly tempts a direct fix-then-test
shortcut — this one is a single comparison operator, about as easy a
case as exists for writing the fix first and the test as an
afterthought — would still be caught correctly without the skill. This
scenario's bug may have been too small to create real pressure toward
the shortcut this skill exists to prevent.
