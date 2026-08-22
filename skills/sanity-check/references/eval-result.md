# Eval result

Recorded 2026-08-22, fourth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## What was measured

This skill's own trigger case: "a number counts as unsupported reasoning
until its origin is named" (jonhill90/skills#186, the real
`agent-supervisor#434` incident — a PR body asserted "65 of 258 passes
discarded" as a measured figure that had actually been inherited and
repeated, never measured). The scenario gives the run a draft PR body
asserting a specific, confident, wrong number ("47 of 312 production
requests ... returned stale cached values") and exactly one file that
could have produced it (`incident-log.txt`, the real sampled data: 340
requests, 9 stale) — then asks whether the draft is ready to publish.

Run twice, live, same task, same fixture, once with `sanity-check`
installed and once with it removed via the harness's `no-skill:<name>`
arm:

- **With the skill:** read `incident-log.txt`, caught the mismatch,
  answered "Needs a correction before publishing" with a table comparing
  the draft's claimed 47/312 against the log's real 9/340. 3 turns,
  61,793 tokens.
- **Without the skill:** same result — read the log, caught the same
  mismatch, answered "Needs a correction before publishing" with the same
  comparison. 3 turns, 65,599 tokens.

Both answers are genuinely correct, not a scorer artifact — quoted in
full in each arm's own transcript, both name the actual log figures (9,
340) against the actual draft figures (47, 312) and state the mismatch in
plain language. Cost was also a wash (65,599 vs 61,793 tokens, ~1.06x;
3 turns each) — well inside the ×1.5 ratio this harness's own `verdict()`
uses before it will call a cost delta real.

## Why `could_not_measure`, not `drop`

The mechanical scorer's own decision table returns `drop` for an
identical-outcome, no-cost-delta pair (both arms "solved it the same
way"). Not passed through, same reasoning as this loop's own prior
results for `durable-fact-before-label` and `determine-signals`
(jonhill90/skills#233): nothing failed. Opus 5 caught this specific,
concrete numeric mismatch without needing the skill's own prompting —
that is a real result about this model on this task, not evidence the
skill is dead. `jonhill90/skills#230`'s own framing is explicit that an
unevaluated (or, per this task, a badly-evaluated) skill is unproven, not
disproven; a single wash does not clear that bar in either direction.

## What is not evidenced

Whether a weaker model, a subtler numeric discrepancy (this scenario's
mismatch is large and immediately visible — 47 vs 9 is not a rounding
error), or a scenario with no single obvious file to check would still
resolve correctly without the skill. This result says only: on this
concrete instance of the skill's own named trigger, at this model tier,
the skill made no observable difference.
