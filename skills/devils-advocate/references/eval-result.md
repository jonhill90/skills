# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=2)

## What was measured

This skill's own trigger case (jonhill90/skills#192, the `loom`
naming-collision incident: two agents assigned opposite sides of a
build-vs-adopt question disagreed on nearly every fact, and the
disagreement forced verification that corrected the record). The
scenario proposes skipping a migration rollback script, reasoning "every
prior additive migration has shipped clean" — a claim `MIGRATION-
HISTORY.md`, given alongside the proposal, directly refutes: one prior
migration that looked identical at proposal time (a single nullable
additive column, same table) silently broke a downstream materialized
view and needed an emergency rollback.

## Two independent live pairs — not one

Run twice, live, same task, same fixture, once with `devils-advocate`
installed and once with it removed via the harness's `no-skill:<name>`
arm — twice, because the first pair's own cost ratio (turns 6 vs 4,
1.5x) sat exactly on this harness's efficiency-flag threshold and a
second pair was run to see whether it held:

| Pair | With: tokens/turns | Without: tokens/turns | Token ratio | Turn ratio |
|---|---|---|---|---|
| 1 | 102,817 / 6 | 94,785 / 4 | 1.08x | 1.50x |
| 2 | 95,729 / 4 | 100,144 / 5 | 1.05x | 0.80x (with used FEWER turns) |

**Outcome, both pairs, both arms: correct and specific.** All four runs
named `MIGRATION-HISTORY.md`'s 2026-05-19 incident by date, quoted the
"looked identical to the other four at proposal time" line, and
concluded the decision was not ready to proceed as written — read by
hand from each run's own transcript, not taken from the scorer's summary
(`.transcript.jsonl` kept alongside each run for this pass; not
published, per this repository's own scope).

## Why `could_not_measure`, not `improve` or `drop`

The FIRST pair alone would have read as `improve` (turn ratio at this
harness's 1.5x flag threshold). The SECOND pair inverts the direction
entirely — the skill-installed arm used *fewer* turns than the
skill-absent one. Two samples pointing opposite ways is exactly what
`docs/evals.md`'s ×2/×3-repetitions bar (that file was removed from this
repo 2026-08-09, before this pass ran -- could not be re-checked against
the current tree) exists to catch: n=1 would have
shipped a false `improve`. The outcome axis never moved across either
pair — every one of the four runs solved the task the same, correct way
— so this is a wash on both axes once measured properly, not a skill
that changed anything observable on this task.

Recorded as `could_not_measure`, not the harness's own mechanical `drop`
for an identical-outcome pair (`docs/eval-harness-findings.md`, filed in
this loop's fifth pass: that branch has no separate outcome for "the
scenario didn't discriminate" versus "the skill measurably does
nothing," and every prior `could_not_measure` in this record needed
exactly this override). Same reasoning as this loop's own prior
`sanity-check`/`determine-intent` results (jonhill90/skills#234): nothing
failed, and this skill's own incident (jonhill90/skills#192) is real
enough that two clean passes on one scenario, by one model, does not
settle whether the skill matters on a harder case.

## What is not evidenced

Whether a scenario with a more subtle counter-example (this one names
the same table and the same column shape as the incident-in-question,
which may be an unusually easy "reference class" match for Opus 5 to
notice on its own) would still be caught without the skill, and whether
the noisy, direction-flipping cost delta across two pairs would settle
in either direction with a third.
