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

## Why this is could_not_measure, not a confirmed "habit skill" result

**Correction (2026-08-23, cross-lane review, estate:2):** the paragraph
this replaces claimed the null result confirmed a "habit skill" pattern
and that the instrument "worked as designed." Neither claim is
supportable from what this scenario actually logs, and stating them was
an overclaim in the record itself, which is the artifact that matters
here.

`criteria.md`'s own "What would make this scenario invalid" section names
exactly this failure mode: *"Arm A not actually being given `github-cli`'s
`SKILL.md` to read — a wiring mistake; re-run rather than record."* That
check was never actually performed, and nothing in this scenario's design
CAN perform it after the fact: `$STUB_LOG` records only `gh` invocations,
and `manifest.json`'s `actions_log` is self-reported by the arm — this
scenario's own convention (matching `mechanize`'s, skills#266/#267)
treats self-reported logs as informational, never as evidence a scored
axis can rely on. There is no independent record anywhere of whether Arm
A's `Read` of `skills/github-cli/SKILL.md` actually happened or silently
no-op'd (a missing file, a permissions issue, a harness that swallowed
the tool call) before the arm proceeded to solve the task unprompted.

**Two hypotheses fit the observed data with equal support:**

1. **Earned null.** A capable baseline model already reaches for
   `--exit-status` on a `gh run watch` call by default, with or without
   the skill, matching the "habit skill" pattern `docs/eval-harness-
   findings.md`/`docs/eval-cost-delta-recount.md` (skills#266/#267)
   documented for other skills.
2. **Unconfirmed wiring.** Arm A's read of `SKILL.md` silently failed,
   both arms ran as the no-skill condition, and the identical result is
   an artifact of that failure rather than evidence about the skill at
   all.

Both trials (baseline and one-off-pressure framing) produced zero
divergence on every axis this scenario measures, which is exactly the
signature either hypothesis predicts — the data does not choose between
them. **The verdict stays `could_not_measure`, and that label now covers
both readings equally: this scenario cannot currently tell "the skill
made no difference" apart from "the skill was never actually present in
the arm meant to have it."** Closing that gap needs an independent
confirmation that Arm A's read happened — e.g., a manifest field the arm
cannot skip, or a scored assertion the arm must make about SKILL.md's own
content — not present in this design and not something this correction
adds retroactively. See "Known harness limitation" below.

## Known harness limitation: an unlogged prompt-delivered read

Distinct from skills#270's install-symlink audit (whether `~/.claude/
skills/` has a current copy of the skill) — this is a different
blindness. Every counting-measurement scenario built so far (this one,
`linear`'s, `obsidian`'s, and `progressive-disclosure`/`mechanize`/
`plan-parallel-execution`'s, skills#265/#266/#267) delivers the skill to
Arm A via a `Read` tool call on an explicit path, instructed in
`prompt.md`, never through `~/.claude/skills` — which is exactly what
makes them immune to the install-symlink failure skills#270 audited.
**But nothing in any of these scenarios' own fixtures logs whether that
`Read` call actually happened and actually returned real content.**
`#246`'s install check has no visibility into this either — it verifies
repo-vs-installed file parity, not which tool calls a subagent made
mid-run. A future scenario that wants "clean tie" to mean "confirmed
earned null" rather than "confirmed earned null OR unconfirmed wiring
failure" needs a mechanism that makes this read observable to the
scorer, independent of the arm's own self-report.

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
