# Eval result

Two independent evaluations, both landing on `could_not_measure`. This
file preserves both write-ups, each attributed to its own pass, per
`docs/eval-status.json`'s own "one entry per skill" record and the
convention this loop uses when a second pass lands on a skill a prior
pass already covered: neither overwrites the other.

## Agreement

**The two passes agree on the verdict** (`could_not_measure`, n=1 each)
**but tested genuinely different fixtures and each independently caught
a defect before trusting its own result** -- pass 10 a scorer bug
(a path-matching regex that also matched the test file's own name), this
pass a live confirmation of a real red-then-green reproduction via
mutation (reverting the fix and confirming the new test actually goes
red). Two different bugs, two different scenarios, same honest outcome:
neither arm needed the skill's own prompting to write the reproduction
before the fix, on either fixture. That is stronger evidence toward
"this model does this by default on small, well-specified bugfixes" than
either result alone would be.

---

## Pass 10 (2026-08-23)

Recorded 2026-08-23, tenth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

### Verdict: could_not_measure (n=1, scorer bug found and fixed)

### Criterion update for this pass

As with this pass's other two picks, no remaining unevaluated candidate
had a documented incident in its own SKILL.md text (the bar retired
after nine passes of confirming this by reading, per this pass's own
brief). `failing-test-first` was picked for its own precise sequence
and completion gate instead (`SKILL.md`: "do not fix first and backfill
the test"; "The fix is not complete until a test that failed before the
fix passes after it. Report both runs (red, then green) as evidence.").

### What was measured

A one-line off-by-one bug (`is_free_shipping` uses `>` where the stated
policy needs `>=`, so an order of exactly $50.00 doesn't get free
shipping) with no existing test suite in the fixture. Scored on:
whether the test file was created before the source fix, whether a
failing run was actually executed before the fix landed, and whether
both the red and green results were reported.

### A real scorer bug, caught by hand-reading a run that looked wrong

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

### Why `could_not_measure`, not `keep`/`improve`/`drop`

Once corrected, this is an identical-outcome pair — both arms followed
the skill's own sequence exactly, with or without it installed.
Recorded `could_not_measure` per docs/eval-harness-findings.md rather
than the mechanical `drop` an identical-outcome pair would otherwise
produce.

### What is not evidenced

Whether a bug that more plausibly tempts a direct fix-then-test
shortcut — this one is a single comparison operator, about as easy a
case as exists for writing the fix first and the test as an
afterthought — would still be caught correctly without the skill. This
scenario's bug may have been too small to create real pressure toward
the shortcut this skill exists to prevent.

---

## Pass 11 (2026-08-22)

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (eleventh
pass). Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/failing-test-first/references/eval-scenario/` so it can be
re-run.

### Verdict: could_not_measure (n=1)

### Why this skill, with no documented incident

Per pass 9's own finding (confirmed again here): none of the remaining
unevaluated skills carry a documented incident. Picked by trigger/caveat
specificity instead -- `failing-test-first`'s own completion gate is
unusually precise and mechanically checkable: "The fix is not complete
until a test that failed before the fix passes after it."

### The scenario

A currency-rounding bug (`apply_discount(33.33, 10)` truncates to
`29.99` instead of rounding to `30.00`), phrased as a real bug report
(the input and both amounts named, the way a support ticket reads) with
a pre-existing test suite that passes cleanly against the bug (none of
its inputs cross the rounding boundary). Scored two ways: (1) is the bug
actually fixed, and (2) does the final test suite contain a real
reproduction -- checked mechanically by reverting the run's own
`pricing.py` to the pre-fix version, running the suite, confirming that
specific test goes red, then restoring the fix and confirming green. A
test added only after the fix, or one that doesn't actually exercise
this input, fails observable (2) even if the headline bug is fixed.

### What was measured

Run once, same task, same fixture, once with `failing-test-first`
installed and once with it removed via the harness's `no-skill:<name>`
arm: both arms fixed the rounding bug correctly and both added a test
matching the bug report's own numbers that mechanically verified red
before the fix and green after. Cost was close (288,249 vs. 279,843
tokens, ~1.03x; 10 vs. 9 turns) -- inside the harness's own ×1.5
tolerance, not a signal worth replicating per this pass's own
instruction to replicate only a strong-looking first result.

### Why could_not_measure, not drop

Nothing failed; both arms produced a real, mechanically-verified
red-then-green reproduction, not just a fixed function. Opus 5 at this
model tier already writes the reproduction before the fix on a task this
size without the skill's own prompting -- a real result about this model
on this task, not evidence the skill does nothing on a harder one.

### What is not evidenced

Whether the same holds under time pressure or a more insistent framing
("just fix it fast, this is blocking a release") that might tempt a
model to skip the reproduction step it took unprompted here. This
scenario's own prompt has no such pressure in it.
