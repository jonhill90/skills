# Criteria: linear (counting measurement, skills#269)

Not run through `scripts/eval_status.py`'s scoring path. Scored by hand
against the observables below, then recorded via `--record` if and only if
a real divergence is found.

## Why a stub, not a real workspace (relation to `eval-blocked.md`)

`eval-blocked.md` (this skill's prior verdict, `unevaluated`) blocked
because this estate has no Linear workspace to run a live check against,
and provisioning one is an infrastructure decision outside any single
pass's scope. This scenario does not need one: `fixture/linear` is a fake
binary that never contacts Linear. It tests a narrower claim -- does the
arm pass the flag this skill's own SKILL.md calls out explicitly
(*"IMPORTANT: --sort is required"*) on the first attempt -- not whether it
can drive a real workspace end to end. Stated explicitly so this is not
mistaken for quietly answering the question `eval-blocked.md` left open.

## The countable quantity

1. **Correctness, checked mechanically.** `fixture/check_answer.py` checks
   that both fixed issue ids (`ENG-401`, `ENG-388`) appear in `result.txt`,
   against a ground truth set in `fixture/linear` before either arm runs.
2. **Trap avoidance, the primary axis.** Does the arm's FIRST `linear
   issue list` call include `--sort`? Real `schpet/linear-cli` behavior
   (reproduced in the stub) is a hard usage error without it -- this
   skill's own SKILL.md flags it as the one flag worth remembering.
3. **Cost.** Real `linear` invocation count from the stub's own log. A
   retry (`issue list` called more than once) is the literal "costs a
   retry" shape from the brief -- the first call failed and the arm had to
   notice the error and correct it.

## Scoring rule

- Both arms include `--sort` on the first call → no discrimination;
  record `could_not_measure` unless correctness diverges.
- Both arms omit it and both retry successfully after the error → same,
  `could_not_measure` (a capable baseline reads the CLI's own error
  message and self-corrects regardless of the skill).
- One arm includes `--sort` on the first call (0 wasted calls) and the
  other does not (1+ wasted call before correcting) → real discrimination
  on cost, the `progressive-disclosure`-shaped result. Record per whichever
  arm avoided the trap and whether it is the skill-loaded one.
- Either arm produces a malformed/missing `result.txt`/`manifest.json`, or
  the stub's own log is missing → INVALID for that arm; re-run rather than
  record.

## What would make this scenario invalid

- The required-flag behavior not matching the real CLI -- this is stated
  directly in the skill's own SKILL.md ("IMPORTANT: --sort is required
  ... Set LINEAR_ISSUE_SORT to avoid passing it every time"), which is
  itself evidence this is a real, previously-encountered trap, not one
  invented for this fixture.
- Arm A not actually being given `linear`'s `SKILL.md` to read -- a wiring
  mistake; re-run rather than record.
- `LINEAR_ISSUE_SORT` being set in either arm's environment (would make
  the flag unnecessary and collapse the scenario to no-discrimination for
  an unrelated reason) -- checked: not set by the harness for either arm.
