# Eval result

Recorded 2026-08-22, third pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that landed in the agent-evals repository (private evaluation evidence, not published here). Tracked in docs/eval-status.json alongside this
pass's other two results.

## Verdict: improve (n=1 — rerun before trusting further)

## A scorer defect found and fixed before trusting this number

The harness's own scorer initially returned `neither arm solved it` for
BOTH arms — a false reading. It checked `intake_watermark` and
`stop_conditions` for non-placeholder *string* content, and both real
runs answered with rich, structured objects (a keyed ledger design, a
list of named stop conditions with terminal states) rather than plain
strings — content the scorer's own first version silently treated as
empty because it never recursed into a dict. Read by hand, both answers
were genuinely excellent and complete. The scorer was fixed to recurse
into nested objects/arrays before this verdict was trusted, and both
saved transcripts were rescored from the already-run artifacts — no
second live run was needed. This is recorded here rather than smoothed
over, the same discipline `verify-the-instrument`'s own result file (this
pass's predecessor) used.

## What was measured

One scenario testing the two fields this skill's own SKILL.md names as
causing "the most damage when left blank": a request to design an
unattended file-watching loop, phrased with no mention of deduplication
or stopping — asking only for `design.json` with named fields including
`intake_watermark` and `stop_conditions`.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm, after
the scorer fix: both arms produced a real, non-placeholder watermark
(a content-hash ledger keyed by file identity, explicitly rejecting a
bare mtime watermark for the exact reasons this skill's own text gives)
and multiple real stop conditions (operator stop, consecutive-failure
circuit breaker, poison-item quarantine, budget ceilings, a no-progress
watchdog). Outcome was a wash. Cost was not: the skill-installed run used
about 1.6x the turns of the run without it (8 vs. 5; tokens close, 1.1x).

## Why "improve," not "keep" or "drop"

Same reasoning as this pass's other two results: identical correct
outcome plus a real turn-count delta is `improve`, not `keep` (nothing
changed about whether the design was complete) and not `drop` (nothing
failed — quite the opposite, both answers were unusually thorough).

## What is not evidenced

Whether Opus 5 names a real watermark and real stop conditions by
default on this kind of request regardless of the skill — the outcome
axis did not move here, matching this pass's other two results. A
weaker model, or a request phrased to more strongly invite skipping
these fields (e.g. one that explicitly asks only for the parts it
mentioned), would be a harder test of whether the skill's own naming of
"the two fields that cause the most damage when left blank" changes
anything.

## Follow-up (same day): closing the loop — improve, re-run, re-verify

This "improve" verdict, alone, is a note. Acted on it: SKILL.md's own
"Two stop conditions, never one" section named the terminal-state
vocabulary but gave no structural template for stating a condition — a
real gap, since both recorded runs spent extra turns working out HOW to
lay one out before filling it in. Added a compact per-condition row
template (`{type, name, check/limit, terminal_state}`) directly after
the "Name terminal states" rule, aimed at the actual overhead the eval
found (structuring the answer), not at this eval's own literal JSON key
names — a fix keyed to this scenario's private schema would be teaching
to the test, not a real improvement.

Re-ran the identical scenario against the changed skill (same fixture,
same `no-skill:loop-contract` arm), plus a second baseline re-run against
the *unchanged* skill first, to have a same-day noise estimate rather
than compare a single new sample against the single old one:

| Run | Skill state | with tokens/turns | without tokens/turns | token ratio | turn ratio |
|---|---|---|---|---|---|
| Original (recorded above) | unchanged | 196,945 / 8 | 177,776 / 5 | 1.11x | 1.6x |
| Baseline re-run | unchanged | 191,558 / 7 | 174,992 / 5 | 1.09x | 1.4x |
| **After the fix** | **changed** | 185,418 / 7 | 182,450 / 5 | **1.02x** | 1.4x |

Both arms still solved it correctly in every run — outcome never moved,
consistent with this scenario's own pattern. The turn ratio (1.4x) is
identical between the baseline re-run and the after-the-fix run, so
turns alone do not show a clean before/after signal on n=1 — the
baseline's own two samples (1.6x, then 1.4x) already show this
scenario's turn-count noise floor is wide. The token ratio is the
cleaner signal: 1.11x and 1.09x on the two unchanged-skill samples, 1.02x
(near-parity) on the one after-the-fix sample — the direction docs/evals.md's own ×2/×3
bar exists to confirm before trusting, not proof from one sample.

**The harness's own mechanical table calls all three of these runs
`drop`** (outcome converged, cost inside its ×1.5 tolerance the two
times it was — and, tellingly, also on the ORIGINAL 1.6x-turn run once a
FRESH baseline sample showed that same ratio isn't reliably outside
tolerance either). None of the three is reported as `drop` here, for the
same reason recorded on every other `could_not_measure` result this
pass: nothing failed. This is the identical harness gap named in this
pass's own top-level finding — see the pass's own summary (not
published here in full; recorded in the PR that carries this entry).

**Verdict left as `improve`**, not upgraded to `keep`: one favorable
token-ratio sample after a real change is suggestive, not confirmed to
the ×2/×3 bar this same file already invokes for the pre-fix numbers.
