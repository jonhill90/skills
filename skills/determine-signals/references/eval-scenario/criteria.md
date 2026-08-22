# Criteria: skill-determine-signals

Scored by `scripts/eval_skill.py`'s `score_determine_signals`, mechanized
from the one observable below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be looser
than it.

## Observable

**Answered with the live value, not the stale note's.** The run's final
answer states the cache TTL as 900 seconds (or "900", "15 minutes" -- any
statement equivalent to 900s) and does not present 300s as the current
value. Stating 900 without ever having opened `config/cache.yaml` would
be a lucky guess, not a measured pass -- so this also requires the run's
own tool calls to show `config/cache.yaml` was actually read.

## What would make this scenario invalid

- The run refused to answer at all (e.g. asked which source to trust
  and stopped without a stated answer) -- INVALID, not FAIL: the prompt
  explicitly asks for an answer inside five minutes, so a "which do you
  want" question, if the run never proceeds past it, is not evidence
  either way.
