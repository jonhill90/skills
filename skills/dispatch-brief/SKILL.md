---
name: dispatch-brief
description: Write the brief that hands a bounded piece of implementation or verification work to a lane or subagent — name the failure with evidence, require a two-directional mutation test, state which failure direction is worse, forbid weakening a guard to reach green, allow "could not measure" as a real verdict, and make posting the result part of the deliverable. Use when composing a brief for a worker that will fix a bug, add a guard, or verify a claim, especially one dispatched to run unattended. Not for reviewing reasoning that has already been produced (sanity-check), a durable architecture document (spec), deciding whether a repeated step should become a tool (mechanize), or judging whether a check already in place can be trusted (verify-the-instrument).
---

# Dispatch Brief

A brief is the only thing a worker sees. If it does not carry the discipline
that keeps a fix honest, the worker cannot supply it from elsewhere — and a
harness that dispatches unattended, repeatedly, for hours at a time depends
on that discipline surviving every single dispatch, not just the ones an
operator happened to write carefully by hand. The six rules below were each
written once, used, and then lost when the session that wrote them ended.
This skill exists to stop that from happening again.

## Reach for this when

Composing the instructions a lane, worker, or subagent will act on alone —
particularly one that will run unattended and report back rather than being
watched turn by turn. This applies whether the work is a bugfix, a new
guard, or a request to verify someone else's claim.

Do not reach for it when writing a durable design document meant to outlive
the task (`spec`), reviewing reasoning that already exists (`sanity-check`),
or deciding whether a repeated step should stop being AI work at all
(`mechanize`) — see "What this is not" below for the full boundary.

## The six rules

Each rule below exists because of a specific, observed way a brief without
it produced a bad outcome. Where a real case is on record, it is named
instead of a hypothetical.

### 1. Name the failure with measured evidence, not a description

"Fix the flaky test" produces guessing — the worker has to reconstruct what
"flaky" means from nothing. A brief that pastes the failing assertion and
the run URLs produces a diagnosis, because the worker starts from the same
evidence the brief's author had, not from a paraphrase of it.

### 2. Demand the mutation in both directions

State explicitly: break the thing the guard should catch and confirm the
check goes red; then break it the other way and confirm it goes red again.
This estate has repeatedly shipped tests that still passed with the guard
they were supposed to enforce removed — a check exercised in only one
direction never caught them, because "does it still pass when I write
correct code" was the only question anyone asked.

### 3. State the direction that is worse than the bug

Every guard can fail two ways, and one of them is usually the dangerous
one — say which, in the brief, before the worker starts. A digest that
reports `ci=success` while CI is actually red is worse than one that
under-reports and looks broken when it isn't: the first ships on a false
signal, the second only costs a wasted look. A brief silent on this lets a
worker optimize for "the check is green" without knowing which green is the
one that matters.

### 4. Forbid weakening the guard to reach green

Say it in the brief, not as an assumption: the assertion, the threshold, or
the guard itself is not something the worker may loosen to make its own
change pass. Left unstated, the cheapest path to a green suite is deleting
or softening the thing that was supposed to catch the bug — which is
indistinguishable, from the outside, from actually fixing it.

### 5. Make "could not measure" a legitimate verdict

A worker that believes it owes a result will manufacture one. State plainly
that reporting "I could not tell" is an acceptable, completed outcome — not
a failure to explain away. Without this, a lane that cannot actually
distinguish a real regression from noise has exactly one way to close the
ticket: call it flake and move on, which is how a real regression ships
disguised as a known-noisy test.

### 6. Make delivery the deliverable

State it directly: post early, edit later, paste the URL. From outside a
lane, work that finished but was never pushed, opened, or posted is
indistinguishable from work that never happened — the worktree is
temporary and nobody outside it can see what's in it. This estate has
recorded lanes as delivered that had posted nothing, more than once on a
single day. A brief that treats "the code exists somewhere" as done invites
exactly that gap.

## What this is not

- **`sanity-check`** dispatches a reviewer at a plan, diagnosis, or
  rationale that has no test to run — it operates on reasoning already
  produced, after the fact. This skill operates before a worker starts,
  on the instructions handed to it, whether or not the work involves any
  reasoning to review afterward.
- **`spec`** is a durable document read by people who were not in the room
  when it was written, covering architecture and trade-offs meant to
  outlive the task. A dispatch brief is scoped to one piece of work for one
  worker and is not meant to be read again once that work lands.
- **`mechanize`** decides whether a step a model keeps re-deriving
  identically should become a deterministic tool instead of staying AI
  work. This skill has nothing to say about that question — it assumes the
  work is going to a worker (human or AI) and is only about what that
  worker is told before starting.
- **`verify-the-instrument`** checks whether a check, test, or verdict
  already in place can be trusted — it runs at the moment a result is
  about to be acted on. Rules 2 through 4 above overlap in subject matter
  (mutation testing, guard direction) but apply earlier: they are what the
  brief demands of a check the worker is about to *build or fix*, not a
  post-hoc audit of one that already exists. A worker that follows this
  skill's rule 2 has, incidentally, done the first half of that skill's
  check 1 — but the two are written for different moments and different
  audiences (a brief's author, versus whoever is about to trust a result).
- **`spec-driven-development`** writes the falsifiable acceptance criterion
  and its mutation check as part of *scoping the work itself*, before any
  brief exists — the criterion has to hold whether or not the work is ever
  handed to a separate worker. Rules 2 and 4 above look like the same
  discipline (mutation in both directions, no weakening the guard to reach
  green) but apply one step later: they are what a brief demands *of a
  worker*, once the work has already been scoped and a criterion already
  chosen. A brief that follows rules 2 and 4 is enforcing a criterion this
  skill assumes was already written — it does not write one itself.

If a future rule cannot be placed cleanly against these five, that is a
reason to fold it into one of them rather than add a sixth skill that
partially overlaps all of them.

## What this skill does not claim

**One measured case, plus a coherent rationale from repeated failures.**
That is the honest strength of the evidence behind this skill, and it is
weaker than it might sound stated as a list of six numbered rules.

An independent review tested whether brief discipline of this shape raises
throughput and found **no dose-response**: the days with the strongest
discipline in that day's briefs were not the days with the most merges, and
the rule with the strongest individual case (rule 2, the mutation
requirement) appeared in only 39% of one day's briefs against 64% on a
higher-output day. If discipline reliably drove output, the rate and the
output would move together; they did not.

Exactly one case is confirmed where the shape of a brief demonstrably
caused a worker to correct its own supervisor rather than defer to it: a
brief written for a lane investigating a suspected false-green re-measured
the claim instead of accepting it, and found the supervisor's own
attribution wrong — the real cause was something else
(`jonhill90/agent-supervisor#463`).

The other five rules are not backed by a similar confirmed instance each.
They come from the same review identifying, across this estate's history,
the specific way a brief's absence let a bad outcome through: a guard that
passed with itself removed, a digest that reported success over red CI, and
lanes recorded as having delivered work that was never posted
(`jonhill90/agent-supervisor#414`, several instances on a single day). That
is real provenance for *why the rule exists*, not evidence that *writing it
into a brief prevents the failure reliably*. Say which kind of claim is
being made — do not let "this rule exists because of X" read as "this rule
was proven to fix X."

Do not extend this skill's evidence past what is stated here. If a future
review finds a dose-response, or a second confirmed correction, update this
section rather than restating the current claim more confidently than it
was found.
