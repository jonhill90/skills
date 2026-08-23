# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Write the brief for the next lane. It needs to add a guard so
> `parse_amount()` stops silently truncating large refund amounts --
> `evidence.log` has the failing case. Write the brief to `brief.md`.

## Setup

`fixture/` is a git repo containing:

- `evidence.log` -- a concrete, measured failure: `parse_amount("125000.00")`
  returned `1250.0` (truncated at the decimal, silently, no error) in a
  real run, with the exact input/output/timestamp.
- `parse_amount.py` -- the function in question, small enough that the
  bug is visible on inspection once you look, but the prompt does not
  point at the file directly.

This is `dispatch-brief`'s own trigger case: composing the instructions
a lane will act on alone, unattended, for a bugfix-plus-guard task -- the
exact shape its own six rules exist for. The scenario does not ask
whether the run can fix the bug; it asks whether the BRIEF it writes
carries the discipline that survives the fix being handed to someone
else, per this skill's own text: "the six rules below were each written
once, used, and then lost when the session that wrote them ended."
