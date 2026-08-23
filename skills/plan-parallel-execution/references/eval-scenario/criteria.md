# Criteria: skill-plan-parallel-execution

Scored by `scripts/eval_skill.py`'s `score_plan_parallel_execution`,
mechanized from the observable below where possible, flagged for a
human read where it cannot be -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it. This scenario produces a written grouping, not an
executed change -- the run's final answer is what is scored, not its
tool-call transcript.

## Observables

1. **Both collisions caught (primary).** The final grouping keeps task
   1 and task 3 in DIFFERENT concurrent batches (or explicitly marks
   them as a deliberate serialization within one batch, per the
   skill's own "unless it is a deliberate serialization" allowance),
   AND keeps task 2 and task 4 in different batches (or explicitly
   serialized) -- both collisions, not just one. Task 5 has no
   constraint; it may share a batch with anything.

   This is checked by a human read of the run's final answer
   (`docs/evals.md`, "Which artifact wins": a criterion this specific
   about which task NUMBERS land in which named batch is a statement
   about the plan's own structure, not a fixed string a keyword match
   can safely resolve without risking a false PASS on a differently
   -worded but still-correct answer, or a false FAIL on a correct
   answer that groups batches in a different order than expected).

2. **Reasoning references the real files, not just the prompt's own
   words.** The run's tool calls show it actually read
   `billing/pricing.py` and/or `auth/login.py` before producing the
   grouping (Read/Grep/Bash tool calls touching those paths) -- a
   grouping produced without ever opening the fixture would be
   guessing at the collision from the prompt's own repeated phrasing,
   not deriving it mechanically the way the skill's own "Mechanize
   first" section requires.

## What would make this scenario invalid

- The run's final answer does not group the five tasks into batches at
  all (e.g. it just restates the task list) -- INVALID, not FAIL:
  nothing to score against observable 1.
