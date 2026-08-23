# Eval result

Recorded 2026-08-23, thirteenth pass of jonhill90/skills#230's
evaluation loop, run against the keep/improve/rename/drop harness that
lives in the agent-evals repository (private evaluation evidence, not
published here). Recorded via `scripts/eval_status.py --record` — the
one supported write path since #245's per-skill append-only logs.

## Verdict: could_not_measure (n=1)

## Selection

By this pass, `scripts/eval_status.py --unevaluated` returned only six
skills: `github-cli`, `linear`, `obsidian`, `prd`, `primer`, `tmux`.
None carries a documented incident (the bar retired at pass 9). `prd`
was picked for its own precise, dual-pronged boundary: "If there's no
problem, there's no PRD; say so instead of inventing one to justify a
solution already chosen" and "Not a technical design. If you find
yourself naming a database, an API shape, or a library while writing
this, that content belongs in the corresponding spec."

## What was measured

A short Slack thread: a teammate reports a real, measured regression
(checkout p95 latency 900ms → 2.4s, three support tickets), a second
proposes a specific fix ("add Redis caching... that's the fix"), a
third asks for "a PRD for adding Redis caching." The trap: a real
problem does exist (unlike the skill's "no problem, no PRD" case), but
it's buried one message before a named technology — testing whether the
written PRD states the actual problem (the regression) as the
Problem/Goals content, or lets the proposed solution (Redis) become the
requirement itself.

## Read the actual written PRD files, not just the chat reply

Both runs wrote a real PRD file to disk (`checkout-latency-prd.md`,
`PRD-checkout-latency-redis-caching.md`) — the scorer checks the CLI's
chat-reply text, but the actual deliverable is the file. Read both
files in full by hand rather than trusting the reply summary. Both are
genuinely excellent: both correctly scope the Problem section to the
latency regression, not "we need a cache"; both explicitly refuse to
treat Redis as a settled requirement (the WITH arm's non-goals: "Not
committing to caching, Redis, or any named technology... Approach
selection belongs to the spec"; the WITHOUT arm's proposed-approach
section gates any caching work behind a diagnostic Phase 0 with an
explicit "Do not implement the cache anyway" if the hypothesis isn't
confirmed); both name real, well-reasoned open questions (abandonment
rate, whether the regression is a step change vs. gradual) rather than
inventing numbers.

One real, subtle difference exists at the margin: the WITHOUT arm's own
document title is "PRD: Reduce checkout latency (proposed approach:
Redis caching of pricing lookups)" — naming the candidate technology in
the title itself, even though the technology never appears inside the
Goals/Non-goals/Success-criteria sections the scenario's own criteria
check. The WITH arm's title omits any technology name entirely ("PRD:
Checkout latency regression") and its own opening framing note states
outright: "Redis caching is a proposed *solution*..., not the problem."
This is a real stylistic difference favoring the WITH arm's discipline,
but it does not rise to the criteria's own bar (naming a technology
*as a requirement* inside Problem/Goals/Non-goals/Success-criteria) —
both PRDs are substantively equivalent on the actual observables
scored.

Cost: 141,428 tokens / 6 turns (with) vs. 174,275 / 5 turns (without) —
1.23x token ratio, 1.2x turn ratio, both under this harness's own 1.5x
efficiency-flag threshold. No second pair run — no signal near the
threshold to check, consistent with this loop's own practice of
reserving replication for results close to or across that line.

## Why `could_not_measure`, not `drop`

Nothing failed. Both arms produced a real problem statement and both
correctly kept the proposed technology out of the document's own
requirements, differing only in a title-level framing choice that the
scenario's own criteria did not set out to measure. Per
`docs/eval-harness-findings.md`, an identical-outcome pair reads as
`could_not_measure`, not the mechanical `drop`.

## What is not evidenced

Whether the title-level difference found here (technology named in the
title vs. kept out entirely) is a real, repeatable effect of the skill
or noise from one run each — a criteria revision that specifically
scores document *titles*, not just section content, would be needed to
test that difference on its own terms rather than as an incidental
observation.
