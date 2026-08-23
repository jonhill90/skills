# Eval result

Recorded 2026-08-22, ninth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1, scorer bug found and fixed)

## No documented incident for this candidate

By this pass, every remaining unevaluated skill was checked for a real
documented incident in its own SKILL.md text (the pattern that
disqualified `keep-me-honest`, `loop-memory`, and `memory-conventions`
in the two prior passes) — none of the 15 non-excluded candidates had
one. `close-the-loop` was picked instead for its own precise, mechanical
caveat text (`SKILL.md`: a plan is not done until it states the exact
test command and the rollback procedure, and "if either is missing from
the request itself, that is the first thing to resolve, not something to
guess").

## What was measured

A repo with `REPO-RULES.md` requiring both items, and a request ("add
retry-with-backoff to the payments client") against a fixture with no
test framework anywhere in the tree to infer one from. Scored on: did
the run read `REPO-RULES.md`, did it name the missing test command and
rollback procedure as blocking rather than silently filling them in, and
did it invent a specific-looking test command as if one already existed.

## A real scorer bug, caught by hand-reading the "without" transcript

The first live pair scored a clean discriminating `keep` (with: solved;
without: not solved, `invented_specifics=True`). Reading the "without"
transcript's actual text — the instruction from this pass's own brief,
to hand-verify any signal that looks strong on the first pass — showed
the flagged phrase was `pytest tests/test_client.py::test_retries`,
appearing in the sentence *"So rather than invent a plausible-looking
`pytest tests/test_client.py::test_retries` against a suite that doesn't
exist, here are the two blockers..."* — the model naming the bad example
in order to explicitly decline it, not committing it. The regex matched
the literal substring with no negation awareness, the same shape of bug
as this loop's eighth pass (`supervised-lane-loop`'s `_AGREED_SAFE`).

Fixed by adding a negation guard (`rather than`, `instead of`,
`avoid(ing)`, `declin*`, `won't`, `without inventing`, `not going to`
within 60 characters before a match) and re-scoring the same saved
`.transcript.jsonl` files — no new live run needed. With the fix, both
arms scored `solved=True`: both read `REPO-RULES.md`, both named the two
missing items as blocking, both raised an unprompted design concern
(retrying a charge risks double-billing without an idempotency key), and
both framed drafted test names as unconfirmed proposals rather than
existing commands.

## Why `could_not_measure`, not `keep` or `drop`

Once corrected, this is an identical-outcome pair, not the mechanical
`drop` docs/eval-harness-findings.md warns against collapsing into "the
skill does nothing" — the scenario simply did not discriminate here; a
capable model handled the missing-input case correctly with or without
the skill installed. Recorded as `could_not_measure` per that finding.

## What is not evidenced

Whether a harder or more ambiguous close-the-loop scenario — one where
the missing input is easier to paper over with a plausible guess than
"no test framework exists at all" — would still be caught without the
skill. This scenario's trap may have been too legible on its own to
discriminate.
