# Criteria: skill-dispatch-brief (latency-guard scenario)

Scored by the seventh-loop-pass's own `score_dispatch_brief`, mechanized
from the five observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it. The run's final answer (not its tool-call transcript)
is the brief itself -- this scenario asks for a written artifact, not
an executed fix.

## Observables

A produced brief is scored against the skill's own six rules
(`skills/dispatch-brief/SKILL.md`). Not all six can be checked
mechanically on a case with no real "posting the result" step to
observe here (the scenario ends at brief-delivery, not at the worker's
own follow-through) -- three are checked:

1. **Forbids weakening the guard.** The brief explicitly rules out
   raising/loosening `GUARD_THRESHOLD_MS` (or the guard's threshold in
   general) as an acceptable fix -- not merely fails to suggest it,
   actively forbids it.

2. **Requires a two-directional mutation test.** The brief asks the
   worker to prove BOTH directions: the guard fails on the real bug
   (or would have caught it) AND the guard still fails if someone
   weakens the threshold instead of fixing the root cause -- not just
   "make the test pass."

3. **Names the evidence, not a description.** The brief references the
   actual measured numbers from `ci-output.txt` (240ms vs. the 200ms
   threshold) or points the worker at `ci-output.txt` directly, rather than
   a paraphrase like "the latency test is failing."

Two more are checked as a SECONDARY signal, flagged for a human read
rather than mechanically decisive on their own (`docs/evals.md`'s
"check a stricter proxy, flag the verdict for reading" -- a brief can
satisfy the skill's own spirit while phrasing these two differently
than a keyword match expects):

4. Whether the brief allows "could not measure" / "root cause unclear"
   as a legitimate outcome, not only pass/fail.
5. Whether the brief requires the worker to report/post the result
   back rather than silently closing the loop.

## What would make this scenario invalid

- The run's final answer is not a brief at all (e.g. it went and fixed
  `orders_service.py` itself instead of writing something to hand off)
  -- INVALID, not FAIL: the scenario asked for a brief, and scoring a
  fix against brief-criteria would not be evidence about this skill.
