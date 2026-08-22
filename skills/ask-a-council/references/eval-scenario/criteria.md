# Criteria: skill-ask-a-council

Scored by `scripts/eval_skill.py`'s `score_ask_a_council`, mechanized
from the two observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be looser
than it.

Redesigned after this skill's own second-pass result
(`skills/ask-a-council/references/eval-result.md` in jonhill90/skills, v1):
the v1 fabrication-incident scenario was single-lens-solvable ("read the
corpus, see it doesn't support the claim") and both arms solved it the
same way for that reason -- it never put the skill's actual claim (some
findings need genuinely different lenses to surface) at risk. This
scenario plants two independent, different-kind bugs so that finding one
does not make finding the other any more likely.

## Observables

1. **Found the mechanism bug.** The run's final answer identifies that
   `monitor.py`'s threshold comparison does not page at exactly the
   documented threshold (states the `>` vs `>=` issue, or equivalent: "at
   the boundary value it doesn't page" / "off by one at the threshold").

2. **Found the legibility bug.** The run's final answer identifies that
   last night's logged "SENT" does not match `webhook-attempts.log`'s own
   500 error for the same page attempt -- i.e., that the monitor's log
   claims success when the underlying webhook call actually failed.

Both are independently checkable in the run's own final answer text.
Neither is a proxy for the other -- a run can find (1) and stop, which is
exactly the failure mode this scenario is built to expose.

## What would make this scenario invalid

- The run never produced any answer addressing the review request (e.g.
  it only asked a clarifying question and returned) -- INVALID, not FAIL:
  nothing to score.
