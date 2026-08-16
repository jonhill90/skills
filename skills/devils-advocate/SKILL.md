---
name: devils-advocate
description: Argue the strongest honest case against a plan or decision before it is committed, not after. Use before a hard-to-reverse choice is finalized — a build-vs-adopt call, an architecture pick, a plan about to be executed — while the decision can still change. Distinct from sanity-check, which tests whether existing reasoning holds; devils-advocate assumes the conclusion is wrong and builds the opposing case from scratch. Distinct from keep-me-honest, which challenges a claim already stated to the user; devils-advocate runs before anything is said or done. Distinct from ask-a-council, which assigns several non-overlapping lenses to one artifact; devils-advocate is one deliberate opposing pass, not a multi-lens convening.
---

# Devils' Advocate

Opposition is not verification. A verifier takes a conclusion and checks
whether the reasoning behind it holds up — it can return "looks right."
A devil's advocate assumes the conclusion is wrong and builds the
strongest honest case for why, on purpose, before the decision is made.
Those are different jobs with different failure modes: a verifier that
finds nothing wrong tells you the reasoning survived scrutiny; an
opponent that cannot build a case tells you the decision survived an
attack. Only the second is evidence the decision is robust, because only
the second was trying to break it.

## Reach for this when

- A decision is about to be made and is expensive or slow to reverse —
  a build-vs-adopt call, an architecture choice, a plan about to be
  executed, a skill or process about to be adopted.
- The decision has had exactly one perspective on it so far — yours, or
  yours plus one agreement. No one has yet tried to argue against it.
- The cost of running one opposing pass is small next to the cost of
  committing to the wrong choice.

Do not reach for this when the decision is already made and the question
is whether a stated claim holds — that is `keep-me-honest`. Do not reach
for it to test whether your own reasoning is internally consistent —
that is `sanity-check`. Do not reach for it when the failure modes worth
covering are genuinely plural in kind (correctness, legitimacy,
portability, cost) and need several distinct lenses at once — that is
`ask-a-council`, and a devils-advocate pass can be one of its lenses
without being a substitute for the whole convening.

## Build the case with intent

1. **State the decision plainly before opposing it.** Write down what is
   about to be committed to, in one or two sentences, so the case against
   it has a fixed target rather than a moving one.
2. **Assume it is wrong and argue from there.** The opening stance is not
   "let me check this" but "this is the wrong call — why." Starting from
   agreement and working backward to objections produces hedges, not a
   case.
3. **Require the opposition to be evidence-bearing.** An objection with
   no evidence behind it is noise. Cite what supports it — a file, a
   number, a prior run, a documented constraint — and say whether that
   number is measured or inferred if it is a number at all. An objection
   you cannot back is a suspicion, not a finding; say so rather than
   dressing it up.
4. **No strawmen, no hedging into neutrality.** Argue the strongest
   version of the opposing case, not the easiest one to knock down, and
   do not soften the conclusion into "it depends" to avoid taking a
   position. A devils-advocate pass that ends up neutral did not do the job.
5. **Name what would have to be true for the objection to win.** Not
   just "this could fail" but the condition that would make it fail, so
   the decision-maker can go check whether that condition holds. An
   objection with no checkable condition attached cannot be acted on.
6. **Let "I could not build a case" stand as a real result.** If the
   honest opposing case is weak, say that plainly instead of manufacturing
   objections to look thorough. A weak opposing case is itself
   information — it means the decision held up under an attempt to break
   it, not that the attempt was half-hearted.

## Read the result honestly

- A strong opposing case is not a verdict to overturn the decision by
  itself — it is one input the decision-maker weighs, the same way a
  `sanity-check` finding is a lead that still needs to be checked before
  being acted on.
- A weak opposing case is not proof the decision is right — it means this
  particular attempt to break it failed. It does not substitute for
  running a command that would settle a factual question directly; oppose
  what is actually a judgment call, not something a test could answer.
- Report which of the two happened, and why, rather than folding the
  result into "reviewed, looks good." A devils-advocate pass that isn't
  distinguishable afterward from a rubber stamp did not do its job on the
  page even if it did it in the room.

## What this is not

- **Not `sanity-check`.** That skill dispatches a reviewer to test
  whether reasoning already produced holds up, built fresh per question
  with a lens the reviewer can fail on. This skill does not test
  reasoning — it builds the opposing case before any conclusion is acted
  on, assuming from the start that the conclusion is wrong.
- **Not `keep-me-honest`.** That skill governs what you tell the user once
  you already know something contradicts a claim already made. This skill
  runs earlier, before anything is said or committed — there is no claim
  yet to hold anyone to.
- **Not `ask-a-council`.** That skill convenes several reviewers, each
  given a distinct, non-overlapping lens, because the candidate failure
  modes are plural in kind. This skill is one lens — opposition — run as
  a single deliberate pass. It can be one of a council's lenses; it is
  not a replacement for convening one when the artifact's failure surface
  genuinely needs more than opposition alone.
- **Not dispatch mechanics.** How to actually launch and isolate the
  agent building the opposing case, and what model tier it runs on, is
  `dispatching-subagents`'s job, not restated here.

## Where this came from

A council run on 2026-08-16 assigned two agents opposite sides of a
build-vs-adopt question. They disagreed on nearly every fact — including
what a named product even was — and the disagreement is what forced
verification against the GitHub API, which corrected the record
(jonhill90/skills#192). A single agent, or two agents given the same
prompt, would have produced a confident wrong answer instead. This skill
generalizes that one run's mechanism — assign the opposing side on
purpose, before the decision is made — rather than reporting it as a
validated general result; it has been exercised on one artifact.
