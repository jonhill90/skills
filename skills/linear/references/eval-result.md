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

## Why this is could_not_measure, not a confirmed "habit skill" result

**Correction (2026-08-23, cross-lane review, estate:2):** the paragraph
this replaces claimed the null result confirmed a "habit skill" pattern
and that the instrument "worked as designed." Neither claim is
supportable from what this scenario actually logs — the same gap
`github-cli`'s own eval-result.md now documents, and this scenario has it
identically: `$STUB_LOG` only ever records `linear` invocations, and
`manifest.json`'s `actions_log` is self-reported, never trusted as
evidence. Nothing here confirms Arm A's `Read` of `skills/linear/
SKILL.md` actually happened rather than silently no-op'd. `criteria.md`'s
own "Arm A not actually being given `linear`'s `SKILL.md` to read" is
listed as an invalidity condition; that check was never actually
performed, and this scenario's design has no way to perform it after the
fact.

**Two hypotheses fit the observed data with equal support:**

1. **Earned null.** A capable baseline model already knows (or discovers
   on the first error and self-corrects) that `linear issue list` needs
   `--sort`, with or without the skill loaded, and the one-off framing did
   not change that.
2. **Unconfirmed wiring.** Arm A's read of `SKILL.md` silently failed
   (the same class of harness fragility that produced the trial 2 arm A
   retry's own genuine setup failure, above — a different failure this
   time, in a different place, but evidence this scenario's environment
   setup is not perfectly reliable), both arms ran as the no-skill
   condition, and the identical result reflects that rather than the
   skill.

Zero divergence on every measured axis, across two trials, is consistent
with either reading. **The verdict stays `could_not_measure`, covering
both readings equally — this scenario cannot currently distinguish "the
skill made no difference" from "the skill was never actually present in
Arm A."** See `github-cli`'s own eval-result.md, "Known harness
limitation," for the general shape of this gap — it applies identically
here and is not restated in full.

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
