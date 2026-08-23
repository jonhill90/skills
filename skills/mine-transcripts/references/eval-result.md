# Eval result

Recorded 2026-08-22, eighth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1) — the scenario, not just the harness, needs rework

## A scenario defect found by reading the transcripts, not a scorer bug

The harness's mechanical table returned `improve` here for the wrong
reason ("neither arm solved it" — its own catch-all for a pair that
doesn't fit the keep/drop shape), and reading both transcripts by hand
found why: **this scenario's own prompt inadvertently prevented the test
it was meant to run.** `prompt.md` said "Search `transcripts/` for
whether the user ever said..." — a literal scope that both arms
respected. The `without`-skill transcript says so explicitly: *"There's
also a `vault/` directory alongside `transcripts/`; I didn't search it
since you scoped the question to transcript[s]."* Neither arm checked
the vault note that actually contains the instruction
(`vault/facts/checkout-retry.md`) — not because either model failed to
notice it existed, but because the prompt told them where to look.

## What was measured, and what actually happened

Both arms handled the residual honestly, which is worth recording on its
own: neither concluded "the user never said this." Both hedged
correctly — "absence here is weak evidence," "I would not treat 'drop
the retry logic' as an authorized change on this basis" — which is
exactly the caution this skill's own incident (a measured phrase with no
matching transcript turn, found only in a personal vault) argues for.
The scenario just never forced the harder step (going and checking the
other record) because its own wording pre-empted it.

Cost, for what it's worth given neither arm reached the intended
observable: 133,142 tokens / 4 turns with the skill, 129,675 / 4 turns
without — a wash (1.03x).

## Why `could_not_measure`, not `improve` or `drop`

Neither the harness's mechanical `improve`-by-default nor a forced
keep/drop reading would be honest here — the scenario didn't discriminate
because it wasn't built to give the skill a chance to fire, not because
the skill made no difference on a fair test. Recording this as
`could_not_measure` and naming the actual cause (a fixture design defect,
not a harness defect this time) rather than either quietly re-running with
a rewritten prompt mid-pass or reporting a verdict the evidence doesn't
support.

## What is not evidenced

Whether either arm would have checked `vault/` unprompted, and whether
the skill changes that, on a version of this scenario that asks the
underlying question ("did the user ever ask for this") without
naming `transcripts/` as the search surface. That scenario has not been
built.
