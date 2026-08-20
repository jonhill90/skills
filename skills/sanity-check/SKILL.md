---
name: sanity-check
description: "Check reasoning with a second mind — dispatch a reviewer whose prompt is built for the specific question, with a lens it can fail on and evidence required for every finding. Use before acting on a plan, decision, diagnosis, or rationale whose cost of being wrong is high and whose only support so far is your own reasoning. TRIGGER, even when the surrounding work otherwise reads as routine: a number, count, or ratio about to be stated (in a report, a PR body, a closing comment) that you cannot point to a command, log line, or fixture for — an inherited figure is exactly this, not an exception to it."
---

# Sanity Check

A sanity check is a second mind, not a second look. When a plan, decision,
diagnosis, or rationale is supported only by your own reasoning, dispatch a
reviewer whose single job is to find out whether that reasoning holds — and
build its prompt for this specific question, from scratch, every time. The
prompt is the whole of the technique. A reviewer handed your conclusion and
asked "does this look right?" will tell you it does; a reviewer handed the
artifact, a stated lens it can fail on, and permission to come back
empty-handed will tell you what you missed. Re-asking yourself, or asking
three reviewers the same question, buys agreement rather than verification.

## Reach for this when

- The conclusion is reasoning, not output: a plan, a diagnosis, a chosen
  approach, a rationale for a decision.
- Being wrong is expensive — the work proceeds on this, or the record keeps
  it.
- Nothing outside your own reasoning currently supports it. **A number
  counts as unsupported reasoning, not as evidence, until you can name what
  produced it.** A figure that arrived already-written — copied from an
  earlier report, a prior PR, a teammate's summary — reads as settled and
  is exactly the case this rule means to catch, not an exception carved out
  of it. Before repeating it, name the counter, log line, or fixture behind
  it; if you cannot, that gap is itself the finding to hand a reviewer, not
  a detail to smooth over.

Do not reach for it when a command would settle the question. If the doubt
is "does this file exist on `main`", "does this test pass", "did the write
apply" — run the check. That is a test, not a reviewer, and a reviewer asked
to reason about it will guess. A number is different: there is no command to
run when the number's origin is simply unknown, only a search that may
itself fail to turn one up — that failure is what the reviewer above exists
to press on.

## Build the prompt with intent

Eight properties. Write them fresh into each prompt; do not carry wording
forward.

1. **Give the reviewer a lens it can fail on.** Name the specific angle, and
   confirm a real "no" is reachable from it. *"Does this document belong at
   this path, given what the repository already treats as canonical?"* has a
   negative answer available. *"Review this plan"* does not.
2. **Hand over the artifact, not your conclusion.** Where the review is *of*
   reasoning, the rationale has to be shown — label it as the thing to
   attack, not as context to build on.
3. **Forbid deference explicitly.** State in the prompt that the requester's
   conclusion may be wrong, and that confirming it is not the deliverable.
   Without the sentence, the reviewer treats your framing as given and
   audits only what you left inside it.
4. **Require evidence per finding, and name what counts.** A file and line,
   a command's actual output, the ref the consumer will read. Say that a
   finding you cannot evidence is dropped — or moved to the list in rule 6.
5. **Say that finding nothing is an acceptable result.** A reviewer that
   believes it owes you findings will manufacture them, and manufactured
   findings cost more than they save, because they read as real and get
   acted on. Require that "nothing found" name what was checked and how, so
   an empty review is distinguishable from a review that never ran.
6. **Ask for the arguments it dropped for lack of evidence.** A short list
   of objections considered and not substantiated. This is where a suspicion
   too weak to assert still reaches you, without pressuring the reviewer to
   inflate it into a finding.
7. **Allow "could not check" as a distinct return.** Separate from both a
   finding and a clean result. A reviewer that could not reach the artifact
   must say so rather than reason about it.
8. **Name the output shape.** Findings with evidence; dropped arguments;
   what could not be checked. Shape is not the technique, but an unnamed
   shape returns prose you have to re-read to score.

Then: **vary the question, not the reviewer count.** Three reviewers asked
the same question produce one answer with three votes. If you want more
coverage, add a lens — a second reviewer pointed at a different failure
mode — not a clone.

## Why not a template

The lens is what does the work, and a lens carried over from a previous
prompt is one this reasoning has already survived. A template also fixes the
question before you have looked at the material, which is backwards: you
choose the angle *because* of what you found while reasoning, and the angle
you would not have thought to write down in advance is usually the one worth
asking.

What is reusable is the list above — the properties a working prompt has.
The wording is not.

## Read the result honestly

- **Agreement is not verification.** Several agents on the same model
  reading the same flawed context agree with each other and are wrong
  together; see `dispatching-subagents` for the general rule and for what
  external evidence means.
- **Check the instrument before believing the verdict.** An empty review may
  mean the reviewer found nothing, or that it was handed nothing to review.
  Rules 5 and 7 exist so those two look different on the page.
- **A finding without evidence is a lead, not a fact.** Check it yourself
  before acting; do not propagate it as the reviewer's conclusion.
- **Two reviewers contradicting each other is a finding to report**, not a
  tie to break with a third.
- **Report what the review changed.** If it changed nothing, say that — a
  review that found nothing is a result, and stating it is what keeps the
  next one honest.

## What this skill is not

This skill owns one thing: the content of a single reviewer's prompt, when
what is under review is reasoning rather than something a command can check.

It is a caller of `dispatching-subagents`, not a substitute. That skill
decides whether a second agent is warranted at all, what each worker may see
about the others, which model tier the work belongs on, what counts as
external evidence, and when to stop. None of that is restated here — read it
there.

It also carries no dispatch mechanism. Mechanisms differ per harness and
change often; where none exists, ask the same question of a fresh context
and apply the same rules to the answer.

## Where this came from

**Read this section as the author's practice, not as measured results.** An
earlier version cited a provenance manifest and results files for the three
anecdotes below. Two of those citations did not hold up when checked: the
three-reviewer migration-plan review is recorded only in a commit message,
and the trigger probe is recorded as **one** phrasing loading the wrong
skill, not as two-right-and-one-wrong. The corrected status is below, and
the claim each anecdote was supporting is marked accordingly.

- **A reviewer handed a conclusion confirms it.** *Evidenced.* Copilot
  sought a second opinion exactly as instructed, handed over its diagnosis,
  the reviewer agreed, and it edited the wrong skill (2026-07-27, ladder
  run; recorded in the private jonhill90/agent-evals repository, not
  publicly available). The same fixture, given raw to a reviewer on
  another harness, produced a falsified hypothesis instead (2026-07-26,
  sentence-rung run; recorded in the private jonhill90/agent-evals
  repository, not publicly available).
- **Agreement is not verification.** *Evidenced.* Copilot delegated to three
  reviewers, they agreed, and it acted on the vote without running the test
  that settled the question — FAIL ×2 (2026-07-27, column run; recorded in
  the private jonhill90/agent-evals repository, not publicly available).
- **Check the instrument before believing the verdict.** *Evidenced, and the
  best-supported claim here.* Twenty-plus false verdicts across
  2026-07-26/29, none from a skill; one was an arm that reported a skill
  absent while a harness still listed it (2026-07-28, counter-scenario run;
  recorded in the private jonhill90/agent-evals repository, not publicly
  available).
- **Vary the question, not the reviewer count.** *Not evidenced.* Reasoning
  from the two entries above, not from a run that varied it.
- **The eight prompt properties.** *Not evidenced individually.* Rules 3, 5,
  6 and 8 have no recorded instance behind them. They are practice.
- **A number counts as unsupported reasoning until its origin is named.**
  *Evidenced.* `jonhill90/agent-supervisor#434`'s PR body asserted "65 of
  258 passes discarded" as the measured scale of a bug. A council seat
  given the mechanism lens searched `git log -S`, `git grep`, fixtures, and
  live supervisor state for anything the figure could have come from and
  found none — no counter, no log, no fixture. The number had been
  inherited and repeated, not measured, and was removed; the defect stood
  on its own without it (two smoke-test durations that provably exceed the
  window). This is the evidence behind the TRIGGER clause added to this
  skill's description and the explicit bullet above
  (`jonhill90/skills#186`). **Untested here:** whether "a conclusion that
  reverses a previously-recorded fact" is a distinct trigger condition
  worth naming the same way — no measured case for it was found during
  that same research pass, so it is not added as a claim this skill makes.

The technique as a whole has never been measured: the sentence-rung scenario
scores whether an outside check was **sought**, not whether the way it was
asked improved the answer. That is why this skill is public opt-in rather
than in the default roster. The scenario that would settle it — a fixture
where a well-built prompt and a naive one reach different answers — has not
been written; the first attempt exercised the mechanism in 3 of 16 runs. The
underlying transcripts are private evaluation evidence, not published here.
