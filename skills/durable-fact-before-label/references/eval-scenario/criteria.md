# Criteria: skill-durable-fact-before-label

Scored by `scripts/eval_skill.py`'s `score_durable_fact_before_label`,
mechanized from the one observable below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observable

**Reordered the two calls correctly.** In the run's final
`fixture/reconcile.py`, inside `process_one()`, the call that writes the
durable result (`write_result(...)`) happens BEFORE the call that
releases the claim (`release_claim(...)`) -- not merely present, but in
that order. A run that only adds a comment, a try/except around the
existing order, or reorders something else while leaving these two calls
in their original (wrong) order has not fixed the bug this scenario is
about.

## What would make this scenario invalid

- The run never touched `reconcile.py` at all -- INVALID, not FAIL:
  nothing to score.
- The run rewrote `process_one()` into a shape where `write_result`/
  `release_claim` are no longer identifiable calls (e.g. inlined,
  renamed) -- INVALID for this specific mechanized check; a human would
  need to read the rewrite by hand, which this scenario's own harness run
  should flag rather than silently score as failed.
