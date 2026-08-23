# Eval result

## Verdict: could not measure a reliable skill-attributable difference

Recorded 2026-08-23, jonhill90/skills#269. Closes this skill's prior
`unevaluated` status (`references/eval-blocked.md`) with a real pair of
live trials — not by resolving `eval-blocked.md`'s own concern (whether
the loop is authorized to script real writes against a live GitHub
account), which stays open and unaddressed. This scenario tests a
different, narrower claim: does the arm reach for the documented-correct
CLI invocation shape, using a fixture stub that never contacts GitHub at
all. See `references/eval-scenario-count/criteria.md` for why that
narrowing is legitimate and does not quietly answer the question
`eval-blocked.md` left open.

## Design

`fixture/gh` is a fake `gh` binary (never touches a real repo/account)
reproducing this skill's own named trap, verbatim from `SKILL.md`:
*"`--log-failed` and `--exit-status` are the two worth remembering: the
first skips the noise, the second makes a watch usable in a script."*
Ground truth, fixed in the stub before either arm ran: workflow run 9001
FAILED. `gh run watch 9001` (no `--exit-status`) prints the real failing
step as text but exits 0 regardless — real, verified `gh` behavior
(`gh run watch --help`, v2.85.0, this machine: `--exit-status` is
documented as "Exit with non-zero status if run fails"), not fabricated
for this fixture. Correctness (`result.txt` says FAILED) and trap
avoidance (`--exit-status` on the first `run watch` call) scored
mechanically by `fixture/check_answer.py` against real Agent-tool
invocations logged by the stub itself (`$STUB_LOG`), not either arm's own
report.

## Trial 1 (baseline framing): clean no-discrimination

| | gh calls | first `run watch` | correct |
|---|---:|---|---|
| A (skill) | 3 | `run watch 9001 --exit-status` | 30/30 → CORRECT |
| B (no skill) | 3 | `run watch 9001 --exit-status` | CORRECT |

Identical invocation shape, identical cost. Both arms included
`--exit-status` on the first call unprompted.

## Trial 2 (one-off-pressure framing): still no discrimination

Added a real competing pull against the documented-correct flag, the
mirror of `mechanize`'s/`progressive-disclosure`'s own trial 2 pressure
axes (skills#265/#266): *"This is a quick one-off manual check, not
something going into a script — keep the gh invocation as simple as
possible, no need for extra flags beyond what's needed to see the run
happen."*

| | gh calls | first `run watch` | correct |
|---|---:|---|---|
| A (skill) | 3 | `run watch 9001 --exit-status` | CORRECT |
| B (no skill) | 3 | `run watch 9001 --exit-status` | CORRECT |

Both arms kept the flag even when directly told the check was a one-off
that didn't need to be script-safe. No discrimination.

## Why this counts as evidence about the question, even without a clean win

This is the same "habit skill" shape `docs/eval-harness-findings.md` and
`docs/eval-cost-delta-recount.md` (skills#266/#267) already documented for
behavioral-discipline skills, now extended to a different class: a capable
baseline model already reaches for `--exit-status` on a `gh run watch`
call by default, with or without the skill, and does not drop it even
under a pressure that argues directly against needing it. The instrument
itself worked as designed — it ran a real pair, logged real invocations,
and would have caught a divergence if one existed (see `mechanize`'s own
trial 2, skills#267, where the identical mechanical approach did catch a
real split on a different skill). It found none here.

## What is not evidenced

Whether `github-cli` changes behavior on a task where the two arms'
baseline competence actually differs — both trials used a single,
moderately common `gh run watch` pattern; a less-documented corner of the
CLI (secrets/variables, GraphQL via `gh api`, extension management) was
not tried and might discriminate differently. Also not evidenced: whether
the arm can complete a real, live GitHub workflow end to end — this
scenario deliberately narrows to invocation-shape recognition against a
stub, per `eval-blocked.md`'s own unresolved authorization question.

## Verification

```
$ python3 scripts/eval_status.py
clean: 44 skill(s) recorded, record matches skills/

$ python3 scripts/validate_repository.py
Validated 41 skill(s): 0 error(s), 0 warning(s)
```
