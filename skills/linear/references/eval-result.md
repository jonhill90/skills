# Eval result

## Verdict: could not measure a reliable skill-attributable difference

Recorded 2026-08-23, jonhill90/skills#269. Closes this skill's prior
`unevaluated` status (`references/eval-blocked.md`) with a real pair of
live trials — not by resolving `eval-blocked.md`'s own concern (no Linear
workspace exists in this estate to run a live check against), which stays
open and unaddressed. This scenario tests a different, narrower claim:
does the arm pass the one flag this skill's own `SKILL.md` calls out as
required, using a fixture stub that never contacts Linear at all. See
`references/eval-scenario-count/criteria.md` for why that narrowing is
legitimate and does not quietly answer the question `eval-blocked.md`
left open.

## Design

`fixture/linear` is a fake `linear` binary (never touches a real
workspace) reproducing this skill's own named trap, verbatim from
`SKILL.md`: *"IMPORTANT: --sort is required (values: priority, manual)."*
Ground truth, fixed in the stub before either arm ran: `linear issue list`
without `--sort` is a hard usage error (exit 2); with it, returns two
fixed issues (`ENG-401`, `ENG-388`). Correctness and trap avoidance
(`--sort` present on the first `issue list` call, and whether a second
call was needed after an error) scored mechanically by
`fixture/check_answer.py` against the stub's own invocation log.

## Trial 1 (baseline framing): clean no-discrimination

| | linear calls | first `issue list` call | correct |
|---|---:|---|---|
| A (skill) | 1 | `issue list --sort priority --state started` | CORRECT |
| B (no skill) | 1 | `issue list --sort priority --state started` | CORRECT |

Both arms included `--sort` on the first call unprompted; identical
invocation shape.

## Trial 2 (one-off-pressure framing): still no discrimination

Added a real competing pull against careful flag construction: *"Don't
overthink the exact flags — this is a quick, throwaway look, just get the
list as fast as possible."* Arm A's first run hit a harness setup defect
(environment variables set in one Bash call did not persist to the next,
so its early `linear` calls never reached the fixture stub at all —
confirmed by the stub's own invocation log being entirely absent; scored
INVALID per this scenario's own criteria and re-run, not recorded) — the
re-run below is the one counted.

| | linear calls | first `issue list` call | correct |
|---|---:|---|---|
| A (skill, re-run) | 1 | `issue list --sort priority --state started` | CORRECT |
| B (no skill) | 1 | `issue list --sort priority --state started` | CORRECT |

Both arms still included `--sort` even when told explicitly not to
overthink the flags. No discrimination.

## Why this counts as evidence about the question, even without a clean win

Same "habit skill" shape as `github-cli`'s own result on this pass: a
capable baseline model already knows (or discovers on the first error and
would have corrected, had it made one) that `linear issue list` needs
`--sort`, with or without the skill loaded, and the one-off framing did
not change that. The instrument worked as designed — a real pair, a real
mechanical scorer, a real invocation log — and found no divergence on
this axis.

## What is not evidenced

Whether `linear` changes behavior on the skill's other named traps or on
its more complex surface (`linear issue start`, `linear issue pr`'s
`gh`-under-the-hood behavior, cross-team leakage) — not tried here. Also
not evidenced: whether the arm can drive a real Linear workspace end to
end — deliberately narrowed to invocation-shape recognition against a
stub, per `eval-blocked.md`'s own unresolved infrastructure question
(no disposable workspace exists to test that).

## Verification

```
$ python3 scripts/eval_status.py
clean: 44 skill(s) recorded, record matches skills/

$ python3 scripts/validate_repository.py
Validated 41 skill(s): 0 error(s), 0 warning(s)
```
