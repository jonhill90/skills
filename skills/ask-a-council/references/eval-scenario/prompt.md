# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Before we trust this monitor going forward, review `monitor.py` and last
> night's logs (`last-night.log`, `webhook-attempts.log`). Anything wrong?

## Setup

`fixture/` is a git repo containing:

- `monitor.py` -- a queue-backlog monitor. Pages on-call when the backlog
  crosses a threshold. Has a real, findable **mechanism** bug: the
  threshold comparison is `>` where the code's own docstring says
  "page at or above 100," so a backlog of exactly 100 never pages.
- `last-night.log` -- last night's real run output, ending with
  `queue backlog 118 -- paging on-call: SENT`.
- `webhook-attempts.log` -- the actual outbound HTTP log for that same
  page attempt: `POST /page -> 500 Internal Server Error`. The page never
  went out. `monitor.py`'s own exception handler logs "SENT" regardless
  of whether the send actually succeeded -- a separate, **legibility**
  bug: the log is not telling the truth about what happened.

This scenario is `ask-a-council`'s own trigger case, engineered so it is
NOT single-lens-solvable (unlike this skill's second-pass attempt, which
a single review closed with one grep-shaped step): there are two
genuinely different-kind issues here, findable only by two different
questions. "Read the code for bugs" surfaces the mechanism bug and stops
-- there is no reason for that pass to ALSO cross-reference a separate log
file against the main log's own claim of success. Only a reviewer
specifically asking "does the log's story match what actually happened"
(the legibility lens) finds the second one, and finding the first does
not make a reviewer more likely to look for the second -- they are
independent questions about independent parts of the artifact, exactly
the shape the skill's own worked example (`watchdog.sh`, jonhill90/skills#147)
describes.
