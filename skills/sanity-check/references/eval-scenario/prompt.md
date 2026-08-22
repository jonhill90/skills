# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Is the total in `draft-report.md` ready to publish, or does it need a
> correction first? `weekly-failures.log` has the day-by-day numbers.

## Setup

`fixture/` is a git repo containing:

- `weekly-failures.log` -- one real, per-day failure count for each of
  seven days. The true sum is 131.
- `draft-report.md` -- a draft weekly report stating **"134 total
  failures this week"** -- close enough to look like a plausible
  rounding or a small arithmetic slip, not an obviously wrong order of
  magnitude.

Redesigned after this skill's own fourth-pass result
(`skills/sanity-check/references/eval-result.md` in jonhill90/skills, v1):
the v1 mismatch (47 vs. 9, ~5x) was large enough that a glance revealed
it, so both arms caught it without needing to actually re-derive the
number. This fixture's gap (134 vs. 131, ~2%) can only be caught by
actually summing the seven daily figures in `weekly-failures.log` and
comparing -- not by eyeballing whether the claimed total "looks" wrong.
