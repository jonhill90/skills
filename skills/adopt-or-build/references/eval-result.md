# Eval result

Recorded 2026-08-22, fourth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: improve (n=1 — rerun before trusting further)

## What was measured

This skill's own trigger case, step 1: "Check availability and prior
art... before recommending anything... A name check that stops at 'I
don't recall one' is not a check" (jonhill90/skills#202 — the real `loom`
incident, proposed as a product name and only later found to collide
with three existing agent orchestrators). The scenario proposes naming a
new internal package `loom` and asks whether that's a good name to go
with; a local `NAMING-REGISTRY.md` in the fixture repo records that
`loom` is already in use internally, one `grep` away, matching the real
incident's own missed check.

Run twice, live, same task, same fixture, once with `adopt-or-build`
installed and once with it removed via the harness's `no-skill:<name>`
arm:

- **With the skill:** checked `NAMING-REGISTRY.md`, correctly refused the
  name ("No — pick something else. `loom` is already taken inside your
  own org."), cited the registry line and its own "check here before
  proposing a new one" header. 13 turns, 330,160 tokens.
- **Without the skill:** same correct refusal, same registry citation,
  same reasoning. 5 turns, 95,867 tokens.

Both answers are correct — both checked the registry, both named the
collision by file and line. The outcome axis did not move. The cost axis
did, by a wide and *reproduced* margin: **a second pair, run by accident**
(re-invoking the harness to re-print the first pair's own evidence, not a
deliberate ×2-confidence rerun) **showed the same shape again** — with:
13 turns / 223,303 tokens, without: 4 turns / 94,884 tokens. Both pairs:
same correct outcome, ~2.4–3.4x more tokens and ~2.6–3.2x more turns with
the skill installed than without.

## Why `improve`, not `keep`

Same reasoning as this loop's own prior `loop-contract`/`safe-deletion`/
`research-the-limit` results (jonhill90/skills#232/#233 -- `safe-deletion`
was recorded in #232, not #231; #231 covered `verify-the-instrument`,
`prompt-corpus`, and `mechanize` instead): identical
correct outcome plus a real turn/token delta is `improve`, not `keep`
(nothing changed about whether the collision was caught) — and, per
`docs/evals.md`'s own ×2/×3-repetitions bar (that file was removed from
this repo 2026-08-09, before this pass ran -- could not be re-checked
against the current tree; the same ×2/×3 threshold is described, without
a specific file citation, in `docs/eval-harness-findings.md`), one accidental extra pair
landing in the same direction is suggestive, not confirmatory; this is
still recorded as an n=1 result per this task's own instruction not to
deliberately chase a ×2/×3 pass, with the second pair noted as
corroborating context rather than folded into the headline numbers.

## What was NOT hand-waved

Did not trust the mechanical `improve` label without reading both
transcripts' own quoted text first — both genuinely name
`NAMING-REGISTRY.md:6` and the batch-job-scheduler collision specifically,
not a vague "sounds taken" guess. The cost delta is not a scorer artifact
either: turn/token counts come straight from the CLI's own `stream-json`
usage accounting, not from anything this pass's scorer computed.

## What is not evidenced

*Why* the skill-installed run cost more — this result reports the
measured delta, not its cause. A plausible read is the skill's own later
steps (blast-radius classification, the mandatory `devils-advocate` pass)
running in full even though step 1 alone already settled this
particular, simple case; that is a hypothesis this result does not test.
