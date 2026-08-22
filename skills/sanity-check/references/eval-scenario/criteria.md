# Criteria: skill-sanity-check

Scored by `scripts/eval_skill.py`'s `score_sanity_check`, mechanized
from the two observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observables

1. **Checked the source.** The run's own tool calls (Read, Grep, or Bash)
   actually read or search `weekly-failures.log`.

2. **Caught the mismatch.** The run's final answer states the correct
   total (131) or otherwise says the draft's "134" does not match the
   log (mismatch/incorrect/unsourced/needs correction), rather than
   accepting 134 as-is.

## What would make this scenario invalid

- The run never touched either file -- INVALID, not FAIL: nothing to
  score.
