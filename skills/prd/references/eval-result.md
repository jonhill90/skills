# Eval result

Two independent evaluations, different scenarios, different verdicts.
This file preserves both write-ups, each attributed to its own pass, per
`docs/eval-status.json`'s "one entry per skill" record and the
convention this loop uses when a second pass lands on a skill a prior
pass already covered: neither overwrites the other.

## Agreement

**The two passes do not agree on the verdict** (`could_not_measure` at
pass 13 vs. `improve` at pass 14) **but they are not in real tension** —
different fixtures, testing different halves of `prd`'s own boundary.
Pass 13's "Redis caching" scenario tests whether a named solution
contaminates the *problem statement*; both arms kept the technology out
of Problem/Goals/Non-goals/Success-criteria, and the one real difference
found (a title mentioning Redis) fell outside what that scenario's own
criteria set out to measure — a clean `could_not_measure`. Pass 14's
"export to CSV" scenario tests the adjacent, sharper case where the
request itself names its own output format, and finds both arms produce
an equally complete, non-leaking PRD but at a real, unreplicated cost
delta (`improve`, not `drop`, precisely because that delta hasn't been
confirmed against a second sample). Read together: across two
independently-designed traps for the same boundary, this model has not
yet been caught crossing it — the open question both write-ups leave is
about cost and title-level framing, not about the substantive line `prd`
draws.

---

## Pass 13 (2026-08-23)

Recorded 2026-08-23, thirteenth pass of jonhill90/skills#230's
evaluation loop, run against the keep/improve/rename/drop harness that
lives in the agent-evals repository (private evaluation evidence, not
published here). Recorded via `scripts/eval_status.py --record` — the
one supported write path since #245's per-skill append-only logs.

### Verdict: could_not_measure (n=1)

### Selection

By this pass, `scripts/eval_status.py --unevaluated` returned only six
skills: `github-cli`, `linear`, `obsidian`, `prd`, `primer`, `tmux`.
None carries a documented incident (the bar retired at pass 9). `prd`
was picked for its own precise, dual-pronged boundary: "If there's no
problem, there's no PRD; say so instead of inventing one to justify a
solution already chosen" and "Not a technical design. If you find
yourself naming a database, an API shape, or a library while writing
this, that content belongs in the corresponding spec."

### What was measured

A short Slack thread: a teammate reports a real, measured regression
(checkout p95 latency 900ms → 2.4s, three support tickets), a second
proposes a specific fix ("add Redis caching... that's the fix"), a
third asks for "a PRD for adding Redis caching." The trap: a real
problem does exist (unlike the skill's "no problem, no PRD" case), but
it's buried one message before a named technology — testing whether the
written PRD states the actual problem (the regression) as the
Problem/Goals content, or lets the proposed solution (Redis) become the
requirement itself.

### Read the actual written PRD files, not just the chat reply

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

### Why `could_not_measure`, not `drop`

Nothing failed. Both arms produced a real problem statement and both
correctly kept the proposed technology out of the document's own
requirements, differing only in a title-level framing choice that the
scenario's own criteria did not set out to measure. Per
`docs/eval-harness-findings.md`, an identical-outcome pair reads as
`could_not_measure`, not the mechanical `drop`.

### What is not evidenced

Whether the title-level difference found here (technology named in the
title vs. kept out entirely) is a real, repeatable effect of the skill
or noise from one run each — a criteria revision that specifically
scores document *titles*, not just section content, would be needed to
test that difference on its own terms rather than as an incidental
observation.

---

## Pass 14 (2026-08-23)

Recorded 2026-08-23, fourteenth pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at `skills/prd/references/eval-scenario/`
so it can be re-run.

### Verdict: improve (n=1, not replicated)

### Why this skill, with no documented incident

None of this pass's six candidates (`github-cli`, `linear`, `obsidian`,
`prd`, `primer`, `tmux`) carries a documented incident. Picked by
trigger/caveat specificity — `prd`'s own SKILL.md draws an unusually
sharp, explicit exclusion: "Not a technical design. If you find yourself
naming a database, an API shape, or a library while writing this, that
content belongs in the corresponding spec — move it there."

### The scenario

"Write a PRD for a new feature: letting a user export their account data
to a CSV file." The trap: "export to CSV" names its own output format,
making it unusually easy to drift into describing *how* the export would
be built (an endpoint, a background job, a storage system) while writing
what is nominally a requirements document. Scored on two observables:
(1) all four required sections present in substance (problem, goals,
non-goals, an observable success criterion) and (2) no implementation
leak — a concrete technical mechanism invented in the answer and not
present in the prompt, phrased in a sentence that isn't itself excluding
that mechanism as a non-goal.

### A real scorer bug, caught by hand-reading the actual output

The first run scored the with-arm as leaking on the word "API" — reading
the actual response showed this was wrong twice over. First, the
scorer's own regex required the literal phrase "success criteria";
the without-arm's real section was headed "How we would know it is
actually done", a semantically equivalent success-criteria section
under different words that a literal-phrase match doesn't recognize.
Second, the scorer flagged "API" as a leak in both arms — both actual
uses were inside an explicit non-goal ("Not an API. Programmatic access
for integrations is a different audience...", and its without-arm
equivalent) correctly *excluding* an API rather than committing to one.
The scorer's first pass checked negation only within the same sentence
as the match; the real negation sat in an earlier sentence of the same
bullet. Fixed by (1) broadening the required-section patterns to match
the concept, not one fixed phrase, and (2) checking negation at
paragraph/bullet granularity instead of sentence granularity — the unit
a reader actually parses "in scope or excluded" from. Re-scored the same
saved transcripts against the fixed scorer and both flipped to
`solved=True, used_builtin=True` (no leak), matching what hand-reading
already showed. Mutation-checked afterward: a synthetic PRD that
actually commits to "a new `/export` endpoint backed by Postgres... with
pandas" still correctly flags as a leak, and a synthetic PRD missing
non-goals/success-criteria still correctly fails `solved` — the fix
widened the true-negative case without losing the true-positive one.

### What was measured (corrected)

Both arms wrote a complete, well-structured, non-leaking PRD — real
documents, not abbreviated ones (both had six-plus substantive
sections). Both `solved=True`, both `used_builtin=True` (no leak). Cost
differed outside the harness's own ×1.5 tolerance: with the skill, 5
turns / 136,105 tokens; without, 3 turns / 101,563 tokens (1.7x turns,
1.3x tokens) — the skill's own run did more work to reach an equally
good result.

### Why improve, not drop or keep

Both arms solved it identically, which alone would read as `drop` — but
the cost delta is real and outside tolerance, which `eval_skill.py`'s
own `verdict()` treats as a signal to replicate before trusting either
reading, not as license to call it settled at n=1 in either direction.
Recorded `improve` with both numbers attached rather than picking a
verdict the single sample doesn't support.

### What is not evidenced

Whether the cost delta replicates, and if so, whether it traces to the
skill's own five required sections (problem/goals/non-goals/success-
criteria/audience) prompting more structure than the task's own bare
request would otherwise produce, or to something else entirely. Not
replicated this pass — flagged for whoever picks this back up.
