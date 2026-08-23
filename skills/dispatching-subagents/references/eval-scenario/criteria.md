# Criteria: skill-dispatching-subagents

Scored by `scripts/eval_skill.py`'s `score_dispatching_subagents`,
mechanized from the observable below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observables

1. **Correctness (primary, mechanical).** After the run, `stage-b.txt`
   contains `15`, `stage-c.txt` contains `25`, and `stage-d.txt`
   contains `35`. This is the decisive check -- a run that dispatched
   three genuinely-parallel subagents against this dependency chain is
   very unlikely to land on all three correct values, since at least
   one subagent would have had to read a stale value before an
   earlier stage's write landed.

2. **Delegation shape (secondary, read from the transcript).** Whether
   the run's own tool calls show a `Task`-type dispatch for this work
   at all, and if so, whether it was sequenced one-at-a-time (each
   `Task` call's own result read before the next one launches) rather
   than fired concurrently. Flagged for a human read per `docs/evals.md`
   ("check a stricter proxy, flag the verdict for reading") --
   correctness alone cannot distinguish "did the work inline" from
   "delegated three subagents but serialized them correctly," and both
   are legitimate skill-following outcomes per the skill's own text
   ("If none of the three conditions holds, do the work inline and say
   so").

## What would make this scenario invalid

- The run touched none of the three target files -- INVALID, not FAIL:
  nothing to score.
