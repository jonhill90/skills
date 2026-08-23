# Eval result

## Verdict: could not measure a reliable skill-attributable difference

Recorded 2026-08-23, jonhill90/skills#269. Closes this skill's prior
`unevaluated` status (`references/eval-blocked.md`) with a real pair of
live trials — not by resolving `eval-blocked.md`'s own concern (the real
CLI drives whichever vault a running `Obsidian.app` instance has open, and
switching that would disrupt a real, personal, non-disposable vault),
which stays open and unaddressed. This scenario tests a different,
narrower claim: does the arm avoid a documented data-loss-shaped trap when
editing a note, using a fixture stub and a plain directory standing in for
a vault — no app, no live vault, no operator session touched. See
`references/eval-scenario-count/criteria.md` for why that narrowing is
legitimate and does not quietly answer the question `eval-blocked.md`
left open.

## Design

`fixture/obsidian` is a fake `obsidian` binary (never touches a real vault
or a running app) reproducing this skill's own named trap, verbatim from
`SKILL.md` gotcha #2: *"`create` without `overwrite` on an existing note
does not replace it — always pass `overwrite` ... or use `append`."*
Reproduced as a refusal (exit 1, note left untouched), not silent data
loss — the more conservative and defensible reading of "does not replace
it," and the one that matches the brief's own "costs a retry" framing
rather than destroying data. Ground truth: a fixed note
(`fixture/vault/daily-log.md`) with existing content; correctness requires
BOTH that content and the new checklist line to survive. Correctness and
trap avoidance (any failed `create` call before recovery) scored
mechanically by `fixture/check_answer.py` against the final note content
and the stub's own invocation log.

## Trial 1 (baseline framing): clean no-discrimination

| | obsidian calls | trap hit | correct |
|---|---:|---|---|
| A (skill) | 3 (read, append, read) | no | CORRECT |
| B (no skill) | 3 (read, append, read) | no | CORRECT |

Identical shape: both arms read the note first, appended, then re-read to
confirm. Neither ever called `create` without `overwrite`.

## Trial 2 (one-off-pressure framing): trap still avoided by both; one incidental, off-axis divergence

Added a real competing pull toward skipping the safe read-first habit:
*"Do this the fastest way you can — don't spend an extra round-trip
reading the file first if you don't need to."*

| | obsidian calls | trap hit (create w/o overwrite) | correct |
|---|---:|---|---|
| A (skill) | 1 (`append` directly) | no | CORRECT |
| B (no skill) | 2 (`append` twice) | no | CORRECT |

Both arms went straight to `append` (the trap this scenario was built to
measure was avoided by both, exactly as trial 1). **Not attributable to
that trap, but real and worth recording honestly:** arm B's first call was
`append daily-log.md content=...` — a positional argument, not this
skill's own documented `key=value` syntax convention (`SKILL.md`'s
"Syntax Conventions" section: *"Parameters are key=value"*) — which the
stub's `get_kv` parser could not match to a target file, so it errored
"note not found" and arm B had to retry with `file=daily-log.md`. Arm A's
single call used the correct syntax from the start. This is a real,
evidenced 1-vs-2-call divergence, but on a DIFFERENT documented
convention than the one `criteria.md`'s scoring rule and
`check_answer.py` were built to measure (gotcha #2, not the
Syntax-Conventions section), observed on a single trial (n=1) with no
second confirming run. Recording it as an observation, not as the basis
for a verdict — stretching one off-target, unconfirmed sample into
`improve` would be exactly the "manufacture a verdict to avoid returning
`could_not_measure`" the brief warned against.

## Why this counts as evidence about the question, even without a clean win on the designed axis

Same "habit skill" shape as `github-cli`/`linear`'s own results on this
pass: a capable baseline model already reaches for `append` over a blind
`create` by default, with or without the skill, even under a pressure
that argues directly for skipping the safe read-first step. The
instrument worked as designed on the axis it was built for (gotcha #2)
and found no divergence there.

## What is not evidenced

Whether the `key=value`-vs-positional divergence observed once in trial 2
would replicate on a second run, or whether it is attributable to the
skill at all rather than one arm's phrasing choice — not confirmed. Also
not evidenced: whether the arm can drive a live, running Obsidian app
against a real vault — deliberately narrowed to a file-level stub, per
`eval-blocked.md`'s own unresolved concern about disrupting a real,
in-use vault.

## Verification

```
$ python3 scripts/eval_status.py
clean: 44 skill(s) recorded, record matches skills/

$ python3 scripts/validate_repository.py
Validated 41 skill(s): 0 error(s), 0 warning(s)
```
