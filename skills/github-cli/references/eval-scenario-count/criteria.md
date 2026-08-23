# Criteria: github-cli (counting measurement, skills#269)

Not run through `scripts/eval_status.py`'s scoring path (no scorer exists
for this skill there; that script only checks the *record*, never assigns
a verdict). Scored by hand against the observables below, then recorded via
`--record` if and only if a real divergence is found.

## Why a stub, not a live repo (relation to `eval-blocked.md`)

`eval-blocked.md` (this skill's prior verdict, `unevaluated`) blocked on a
different question: whether the loop is authorized to create, populate, and
delete real GitHub repos/issues/PRs unattended. This scenario never asks
that question -- `fixture/gh` is a fake binary that never contacts GitHub.
It tests a narrower, different claim: does the arm reach for the
documented-correct **invocation shape** (`--exit-status` on `gh run watch`,
per this skill's own SKILL.md: *"the second makes a watch usable in a
script"*), not whether it can complete a real end-to-end GitHub workflow.
This is a real, meaningful narrowing -- stated explicitly in `eval-result.md`
-- not a workaround that quietly answers the same question `eval-blocked.md`
left open.

## The countable quantity

1. **Correctness, checked mechanically.** `fixture/check_answer.py` scores
   `result.txt` against a ground truth fixed in `fixture/gh` before either
   arm runs (run 9001's conclusion is `failure`, hardcoded in the stub).
   Expected to be a weak discriminator on its own: `fixture/gh`'s `run
   watch` output always prints the real outcome as text regardless of exit
   code, so a model reading stdout (not just checking `$?` the way a bash
   script would) can plausibly get this right either way. Not discarded --
   if it DOES diverge, that is worth recording -- but not the primary axis.
2. **Trap avoidance, the primary axis.** Does the arm's FIRST `gh run
   watch` call include `--exit-status`? This is this skill's own named
   trap (*"the two worth remembering: the first skips the noise, the
   second makes a watch usable in a script"*) -- a caller relying on exit
   code alone without it gets a false success regardless of what actually
   happened.
3. **Cost, secondary.** Real `gh` invocation count from `fixture/gh`'s own
   log (`STUB_LOG`), the same Agent-tool-infrastructure-adjacent counter
   class `mechanize`/`plan-parallel-execution` used (skills#266/#267/#268):
   a corrective follow-up call (`gh run view`/a second `run watch`) after a
   first watch that omitted `--exit-status` is the "costs a retry" shape
   this skill's own SKILL.md warns about.

## Scoring rule

- Both arms include `--exit-status` on the first watch call (trap avoided
  by both) → no discrimination on the primary axis; record
  `could_not_measure` unless correctness or cost separately diverges.
- Both arms omit it → same, `could_not_measure` (habit-skill shape: a
  capable baseline already reaches for the flag, or neither does).
- One arm includes `--exit-status` on the first call and the other does
  not, with no cost regression for the arm that included it → real
  discrimination on the exact axis this skill is about. Record per
  whichever arm avoided the trap and whether it is the skill-loaded one.
- If the arm that omits `--exit-status` also fails to make any corrective
  follow-up call (`run view`/second `run watch`) AND still reports the
  ground-truth-correct answer, flag it explicitly (per
  `check_answer.py`'s own FLAG) rather than silently trusting the printed
  text was actually read and not guessed.
- Either arm produces a malformed/missing `result.txt` or `manifest.json`,
  or the stub's own `$STUB_LOG` is missing → INVALID for that arm; re-run
  rather than record.

## What would make this scenario invalid

- `fixture/gh`'s ground truth (run 9001 = `failure`) leaking into the
  prompt or being guessable from anything other than actually calling
  `gh run watch`/`gh run view` — checked: `prompt.md` never states the
  outcome.
- Arm A not actually being given `github-cli`'s `SKILL.md` to read — a
  wiring mistake; re-run rather than record.
- The stub itself diverging from real `gh` in a way that matters to this
  scenario (i.e., real `gh run watch` without `--exit-status` does NOT
  actually exit 0 on a failed run) -- checked directly against
  `gh run watch --help` (v2.85.0, this machine): `--exit-status` is
  documented as "Exit with non-zero status if run fails," confirming the
  flag is the trap's real mechanism, not fabricated for this fixture.
