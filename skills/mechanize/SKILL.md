---
name: mechanize
description: Decide whether a step currently done by AI inference should become a deterministic tool instead - check whether the output is a FUNCTION of the input (mechanize it) or requires judgement (keep AI on it), then run the counter-test before committing. Use when a model has computed, checked, or classified the same thing identically across several turns or ticks, or before scripting a step an agent currently performs by reasoning. Not for checking whether a tool can be trusted once built (verify-the-instrument), whether existing reasoning holds (sanity-check), or whether to adopt someone else's code versus write your own (adopt-or-build) - this decides whether a tool should exist here at all.
---

# Mechanize

A harness is a multiplier, not a substitute. Mechanizing a deterministic
step does not save money by swapping a cheap thing in for an expensive one
— it stops a capable model being **wasted** on work a script should do, so
the model's judgement is spent where judgement is actually needed. That is
the correct reading of the 10/90 claim: the score jumps behind it came from
scaffolding **with a fixed model**, never from replacing the model.

This is the decision procedure for stage 4 of the AI-to-tool lifecycle: AI
does it while the shape is unknown → AI watches until it works → AI thinks
about how it breaks → **a tool does it**, with AI kept on only for new
failure modes the tool cannot see.

## The test

> **Is the output a FUNCTION of the input, or does it require judgement?**

Reading a number and comparing it to a threshold is a function. Deciding
whether a stale fact is still true is judgement.

Detection is mechanical. Judgement is not. If two runs over the same input
must reach the same answer by rule alone, mechanize. If reaching the answer
requires weighing context a rule cannot enumerate, it stays AI.

## The counter-test

Before mechanizing, ask the question that keeps stage 4 from overreaching:

> **What NEW failure mode would a tool be blind to?**

A tool encodes the failure modes already known when it was written; it
cannot notice one it was never shaped around. If the honest answer is "a
novel one we have not seen yet," AI stays on top of the tool rather than
being replaced by it — the tool still does the mechanical part, but AI
keeps watching its output for the case the tool cannot recognize as wrong.

If the answer is "none - the failure modes are closed, we've watched this
break enough times to enumerate how," mechanize with confidence.

## The smell

> **Any answer a model re-derives identically every time it runs.**

This is the signal that a step has quietly outgrown stage 1-3 without
anyone noticing: the shape is no longer unknown, watching has already
happened, and the model is now paying inference cost for a lookup. The
canonical instance cited in this estate: a watchdog re-derived six
mechanical facts every tick across roughly twenty ticks before anyone
caught it and wrote a fix (could not measure — no matching issue, PR, or
commit found in jonhill90/agent-supervisor or jonhill90/agent-dotfiles to
check the specific counts against).

Catching the smell is itself an application of the test above — the fact
that the answer is identical every time is direct evidence it was never
judgement in the first place.

## Worked examples

**Mechanized, correctly** — the output was a function of the input, and the
failure modes were already known:

- **Quota checking.** Was eyeballing usage; now a script with bounded
  timeouts and a defined exit contract.
- **Transcript extraction.** Was grepping by hand; now a script with typed
  flags for the recurring queries (only-typed, JSON output, since a date,
  grep a pattern).
- **Pane/state classification.** A fixed rule over visible state, now a
  script rather than a per-tick judgement call.
- **Completion verification.** A defined verify loop a script runs after
  dispatch, rather than an agent re-reading output each time to decide if
  a task finished.

**Still AI, and must not be mechanized** — the output required judgement,
or the failure mode was novel:

- **Deciding whether a stranded prompt is safe to submit.** A stranded
  "merge the PR" once sat in the queue of the very lane that had authored
  the unreviewed PR it named. A tool that auto-submits stranded text would
  have merged it. Safety here depends on context a rule cannot enumerate in
  advance — who authored what, what state the PR is actually in — which is
  exactly the shape of judgement, not detection.
- **Judging whether a merged fix actually fixed the symptom.** This estate
  has closed issues while their symptoms continued, repeatedly. Confirming
  a fix worked means checking the original complaint against current
  reality, not checking that a diff merged.
- **Sequencing.** Deciding what should happen next among competing,
  partially-observed pieces of work is judgement about priority and risk,
  not a lookup.

## What this is not

- **`verify-the-instrument`** asks *can this tool be trusted?* — it runs
  after a tool exists, to check the tool's verdicts are load-bearing. This
  skill asks *should there be a tool here at all?* — it runs before one is
  built.
- **`sanity-check`** asks *does my reasoning hold?* about a specific
  conclusion. This skill asks whether a whole class of repeated reasoning
  should stop being reasoning.
- **`adopt-or-build`** asks *should we take someone else's code, or write
  our own?* once the decision to build something is already made. This
  skill decides whether anything should be built at all, versus staying on
  AI.

## Eval case

`references/eval-case.md` has a worked scenario with an expected verdict,
usable as a fixture to check this skill actually changes the answer rather
than restating the input.
