# Criteria: skill-failing-test-first

Scored by `scripts/eval_skill.py`'s `score_failing_test_first`, mechanized
from the two observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observables

1. **The bug is actually fixed.** After the run, executing
   `apply_discount(33.33, 10)` against the run's own final `pricing.py`
   returns `30.00`, not `29.99`.

2. **A real reproduction exists in the suite and was demonstrated red
   before it was green.** `tests/test_pricing.py` (the run's final
   version) contains a test whose assertion matches the bug report's own
   numbers (`33.33`, `10`, `30.0` or `30.00`) -- checked by actually
   reverting `pricing.py` to its pre-fix (truncating) version, running
   the suite, and confirming that specific test fails, then restoring
   the fix and confirming it passes. A test added only after the fix, or
   one that would pass against the buggy code too (e.g. asserting the
   wrong value, or not exercising this input at all), fails this
   observable even if the headline bug is fixed.

## What would make this scenario invalid

- The run never touched `pricing.py` or `tests/test_pricing.py` at all --
  INVALID, not FAIL: nothing to score.
