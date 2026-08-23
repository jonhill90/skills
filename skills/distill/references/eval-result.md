# Eval result

Recorded 2026-08-22, ninth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## No documented incident for this candidate

As with this pass's other two picks, no remaining unevaluated skill had
a genuine documented incident in its own SKILL.md text. `distill` was
picked for its own named failure mode instead (`SKILL.md`: "an inferred
figure that reads as measured... makes the corpus look more settled than
it is"; "record disagreement instead of smoothing it over").

## What was measured

Three short research documents: two agree a cache change measured a 40%
latency reduction, a third (`followup-analysis.md`) re-aggregates the
same underlying load-test run and shows the 40% figure only covered the
warm-cache subset (~30% of traffic) — the real reduction across the full
mix is 12%. Scored on: did the run read all three files, did it surface
the 40%-vs-12% disagreement by name (not just cite the corrected number
without saying it contradicts the other two), and did its own working
recommendation avoid repeating 40% as the settled figure.

## Outcome: both arms solved it, correctly and thoroughly

Both the skill-installed and skill-absent runs read all three documents,
led with "the 40% figure is retracted/wrong, here's the 12% figure and
why," named the same-underlying-data relationship between the two
numbers explicitly, and both went further than the minimum bar — flagging
the un-analyzed cold-miss path (70% of traffic) and the missing p95/p99
tail latency as gaps the corpus doesn't cover. Hand-read both full
`.transcript.jsonl` texts; no scorer bug found this time — the
`surfaced`/`led_with_40` regexes matched real, correctly-attributed
text in both arms.

Cost: with-skill used more (132,844 tokens / 7 turns) than without
(95,495 tokens / 5 turns) — a 1.39x token ratio and 1.4x turn ratio,
both under this harness's 1.5x efficiency-flag threshold, so no
`improve` flag triggered.

## Why `could_not_measure`, not `drop`

Identical outcome, both arms correct and equally thorough. Per
docs/eval-harness-findings.md, an identical-outcome pair is not evidence
the skill does nothing — this scenario, at 23 lines of source material
across three short files, may simply be too small to need the skill's
own stated cost-justification threshold ("distillation earns its cost
against a corpus, not a paragraph" — a line the skill-installed arm's own
opening sentence quoted almost verbatim, correctly declining to treat
this size of input as needing real distillation work). Recorded
`could_not_measure`, not `drop`.

## What is not evidenced

Whether a larger corpus — enough source material that a model would
actually need to sample/skip material rather than read all of it in one
pass — would show a real difference. This scenario's small size may have
made both arms converge on "just read everything," which sidesteps the
skill's actual value proposition rather than testing it.
