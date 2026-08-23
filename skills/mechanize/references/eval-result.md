# Eval result

Recorded 2026-08-22, closing one skill of jonhill90/skills#230's "26 of 35
never evaluated" gap, run against the keep/improve/rename/drop harness
that landed in the agent-evals repository (not published here; see
"Scope" above). This is a second file alongside `eval-case.md` (the test
case definition) — this one states the verdict and what was measured, not
the scenario itself.

## Verdict: could not measure a reliable skill-attributable difference

Not "keep," not "drop" — the harness's own automated scorer returned
`keep`, and this file explains why that number is not trusted as
reported, per this skill's own neighbor `verify-the-instrument`'s
discipline: a verdict from a check is a claim about the checker too.

## What was measured, and what went wrong with measuring it

One scenario, `eval-case.md`'s own reference case turned into a runnable
fixture: eleven ticks of one lane's pane output, ten of which reach the
same stalled/not-stalled answer from a fixed three-fact rule, and an
eleventh that looks identical to a stalled tick by those three facts but
is actually a shell waiting on a human (a `git rebase -i` editor). The
task asked for a decision on how the check should be implemented going
forward, written to a file.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm. Reading
the two written decisions by hand (not the automated scorer) found them
close to equivalent in substance: both independently identified that one
of the three input facts was actively wrong at the failing tick, both
proposed a deterministic classifier to replace the three-fact rule, and
both reserved some residual judgement for cases their own rule could not
place. The run without the skill used the words "classifier"/"detector"/
"design" throughout and never used the words "script"/"tool"/"mechanize"/
"automate" even once — which is what actually produced the scorer's
`keep` reading: its keyword match for "did this recommend mechanizing
anything" only recognized one vocabulary and missed an equivalent
proposal phrased in different, still entirely reasonable, words.

## Why this is reported as "could not measure," not "drop"

Two independent problems compound here, and neither alone would justify
stopping:

1. The scenario itself did not discriminate — a sufficiently capable
   model reached a materially similar, sophisticated engineering answer
   whether or not the skill was present, on this fixture.
2. The scorer built to read the difference has a demonstrated blind spot
   (natural-language paraphrase of "mechanize") that a hand read caught.

Reporting `keep` off a demonstrably blind scorer would repeat exactly the
failure this skill's own neighbor exists to catch. Reporting `drop` would
go the other way on the same bad instrument. Neither is warranted; a
rerun needs either a harder scenario (one where an unaided model is
plausibly worse) or a scorer that reads intent rather than a fixed
keyword list before this skill gets a verdict that means anything.

## What is not evidenced

Whether `mechanize` changes behavior on ANY task remains untested — this
is a report that one attempt did not produce a trustworthy answer, not
that the skill has no effect.

---

## Counting-measurement re-run (jonhill90/skills#266, second scenario)

Recorded 2026-08-23, a from-scratch scenario built the way
`progressive-disclosure`'s `eval-scenario/` was (skills#265/#229): a real
countable quantity, not a scored write-up. Full design and scoring rule:
`references/eval-scenario-count/criteria.md`. Chosen for #266 because
`mechanize`'s own "smell" section names a directly countable target —
*"any answer a model re-derives identically every time it runs"* — and
this skill's own worked examples are about literal tool-call counts, not
prose quality.

### Design

`fixture/ticks/`: 30 tick files, 4 given as worked healthy/unhealthy
examples, 26 to classify by the rule those examples imply
(`error_rate < 0.05 AND latency_ms < 200` → healthy). Real Agent-tool
invocations, one per arm, `manifest.json` self-reports `script_written`
and a literal `actions_log`, scored against a ground truth fixed at
fixture-generation time (`fixture/check_answer.py`), not either arm's own
report. `subagent_tokens`/`tool_uses` are the Agent-tool infrastructure's
own real counters (visible directly on each dispatch in this pass, unlike
the private-harness numbers cited elsewhere in this repository).

### Trial 1 (baseline framing): clean no-discrimination

| | tokens | tool_uses | script_written | actions_log | correct |
|---|---:|---:|---|---:|---|
| A (skill) | 40,407 | 6 | true (`classify.py`) | 6 | 30/30 |
| B (no skill) | 36,075 | 4 | true (`classify.py`) | 5 | 30/30 |

Both arms independently wrote an equivalent threshold-rule script and ran
it once — the mechanized answer both this skill and a capable baseline
model already reach by default on a task this clean. B was marginally
cheaper on both axes. No discrimination.

### Trial 2 (one-off-pressure framing): still no clean discrimination, but a real qualitative split the manifest schema didn't capture

Same fixture, same question. Added one line, an explicit competing pull
against mechanizing, the mirror of `distill`'s escalation axis and
`progressive-disclosure`'s trial 2 (skills#265): *"This is a one-off
check — we will not run this classification again after today, so don't
over-invest in tooling for a single pass."*

| | tokens | tool_uses | script_written | actions_log | correct |
|---|---:|---:|---|---:|---|
| A (skill) | 40,068 | 5 | **false** (self-reported) | 6 | 30/30 |
| B (no skill) | 37,880 | 3 | false | 3 | 30/30 |

Both arms backed off a *persisted* script under the pressure — but
reading the actual transcripts (`actions_log` entries, quoted verbatim
above) shows they did NOT do the same thing. Arm A ran a single inline
`python3 -c` command that mechanically applied the derived rule to all 30
records in one deterministic pass — the substance of "mechanize," just
without writing a reusable file, which is a reasonable reading of "don't
over-invest in tooling for a one-off." Arm B `cat`-viewed all 30 records
and generated the 26 verdicts by its own inference, record by record, with
no programmatic check — the model's own token-by-token judgement, the
thing this skill exists to move off of, even though it happened to be
100% correct this run.

**This is a real, evidenced divergence in HOW the task was done, on the
exact axis `mechanize` is about — but it is not the divergence this
scenario's own manifest schema was built to detect.** `script_written`
is a boolean about a persisted file; it returned `false` for both arms
here and therefore reads as "no discrimination" if read at face value.
The actual discriminating fact — code execution against all inputs at
once (A) versus per-record model inference (B) — only shows up by
reading `actions_log`'s literal content, the same "read the actual
transcript" discipline `docs/eval-harness-findings.md` names as the fix
for scorer/regex misreads (§1). Per this scenario's own `criteria.md`
scoring rule (cost-and-correctness only), this does not clear the bar for
`improve`: B was cheaper (3 vs 5 tool_uses) and equally correct, so the
conjunctive test fails for A. Recorded `could_not_measure`, not `improve`
— the qualitative split is real and worth naming, but the instrument as
built does not mechanically score it as a win for the skill.

### Why this counts as evidence about the QUESTION, even without a clean win

`progressive-disclosure`'s trial 2 (skills#265) discriminated because its
added pressure ("be thorough") argued directly FOR the specific behavior
the skill argues against (reading everything instead of the index) —
the pressure targeted the skill's own claimed axis precisely. This
scenario's trial 2 pressure ("don't over-invest in tooling for a
one-off") argues against building a REUSABLE tool, which is a real and
separate engineering judgement from whether to apply the rule
mechanically at all — and a capable baseline model already makes a
similar call in both arms (neither persisted a script), leaving no room
for the skill to move behavior on the axis the manifest was built to
measure. The single-shot execution (A's inline command) versus
per-record inference (B) split IS the discrimination `mechanize`'s own
claim predicts, just not the one this scenario's schema was designed to
catch — a design gap in this scenario, not evidence the skill has no
effect.

### What would close this gap

A `manifest.json` field asking each arm to self-report, honestly, whether
the 26 verdicts were produced by ONE programmatic pass over all inputs or
by per-record model judgement, independent of whether a file was
persisted — re-run with that field, or a scorer that reads `actions_log`
for "one command covering N inputs" versus "N per-input actions," rather
than trusting the coarser boolean. Not built here; left as the concrete
next step for whoever re-runs this scenario.
