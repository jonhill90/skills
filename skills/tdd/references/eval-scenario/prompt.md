# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Add a `humanize_duration(seconds)` function to `duration.py` that turns
> a count of seconds into a short human string, e.g. `90 -> "1m 30s"`,
> `3661 -> "1h 1m 1s"`. No such function exists yet.

## Setup

`fixture/` is a git repo containing:

- `duration.py` -- an empty module (one docstring, no functions). Nothing
  to reproduce a break against; this is greenfield.
- `tests/test_duration.py` -- empty except for the standard import
  boilerplate, so there is somewhere obvious to add a test, but nothing
  written yet.

This is `tdd`'s own trigger case, verbatim from its own SKILL.md:
"building a new function... from scratch and no prior bug is being
reproduced" -- the boundary case this skill itself draws against
`failing-test-first` ("a defect in already-working code" governs the
other skill, not this one). Scored on ORDER, not just presence: did the
test for `humanize_duration` get written (and actually run, failing
because the function doesn't exist yet) before the implementation, or
after.
