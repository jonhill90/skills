# Criteria: skill-tdd

Scored by `scripts/eval_skill.py`'s `score_tdd`, mechanized from the two
observables below -- this file is authoritative (`docs/evals.md`, "Which
artifact wins"); the scorer must never be looser than it.

## Observables

1. **The function works.** After the run, `humanize_duration` exists in
   `duration.py` and returns the two example strings the prompt itself
   gives: `humanize_duration(90) == "1m 30s"` and
   `humanize_duration(3661) == "1h 1m 1s"` (or an equally readable
   equivalent naming the same units in the same order -- exact
   punctuation is not the point, the two worked examples resolving
   correctly is).

2. **The test came first, by the run's own tool-call order, not just by
   the final diff.** The run's own tool_calls are inspected in sequence:
   the first tool call that WRITES OR EDITS `tests/test_duration.py`
   with a real assertion referencing `humanize_duration` must occur
   BEFORE the first tool call that adds a `def humanize_duration` to
   `duration.py`. A final repo state with both files present proves
   nothing about order -- this is the whole reason `tdd`'s own
   red/green/refactor discipline is a sequence, not a checklist of
   artifacts to have by the end.

## What would make this scenario invalid

- The run never touched either file -- INVALID, not FAIL: nothing to
  score.
- The implementation and the test were written in the SAME tool call
  (one Write containing both, or a single commit-shaped patch with no
  intermediate call boundary) -- INVALID for the order check
  specifically (observable 2 cannot be mechanically ordered), but
  observable 1 still scores normally.
