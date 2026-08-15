---
name: dispatching-subagents
description: Decide whether to delegate work to subagents, set each one's isolation boundary, and verify their output with external evidence. Use when considering fanning work out to parallel agents, orchestrating multiple agents, or reviewing whether a multi-agent result can be trusted.
---

# Dispatching Subagents

Delegation is an orchestrator-workers decision, not a reflex. It costs
roughly an order of magnitude more tokens than doing the work inline and
it removes your ability to see what happened. Earn it.

Portability: dispatch mechanisms differ per harness and change often.
This skill is the decision procedure, not the API. Use whatever
mechanism the current harness provides; where none exists, execute the
same plan sequentially in this context. The boundaries and verification
rules below are unchanged either way.

## Decide first

Delegate only when at least one is true:

- The work is **breadth-first**: several independent paths must be
  explored and their results do not depend on each other.
- The material **exceeds one context window** and splitting it loses
  nothing.
- A **verifier must be independent** of the maker to be worth anything.

Do not delegate when: the subtasks are sequential and each needs the
previous one's output; the task is small enough to read directly; you
cannot state the success criterion for a worker in one paragraph; or you
would be unable to check the result yourself.

If none of the three conditions holds, do the work inline and say so.

## Set the isolation boundary

Before dispatching, state for each worker what it knows about the
others. Default to **nothing**: a self-contained task description, the
required output format, and a fresh context. Shared state between
workers is a cost — justify each piece of it.

Write the boundary down in the plan. "Worker A does not see B's
findings" is a design decision, not an omission.

## Tier the models

Put reasoning-heavy planning, decomposition, and final review on the
strongest model. Put well-specified execution on cheaper ones. A worker
whose task cannot be specified tightly enough for a cheaper model is a
sign the decomposition is not finished.

## Verify with external evidence

Agreement between workers is not verification. Several agents on the
same model reading the same flawed context will agree with each other
and be wrong together.

A result is verified only by evidence from outside the agents:

- test or build output, pasted;
- a command's actual return value;
- a file or record that can be read back;
- human review.

The maker never grades its own work. If a verifier is itself an agent,
it must be given the artifact and the criterion, not the maker's
reasoning.

## When independence is not available

Sometimes no genuinely independent reviewer exists — only one reviewing
agent is running, and it also contributed to the change under review.
Three moves are possible and only one is right:

1. **Proceed silently**, saying nothing about the conflict — a hidden
   conflict is a defect.
2. **Stall the queue** until independence returns — this looks safer but
   is a failure too, just a quieter one, when the work is otherwise
   mergeable.
3. **Review anyway, and declare the conflict in the first line of the
   review**: what the reviewer contributed to the change, and why review
   is proceeding without independence regardless.

A hidden conflict is a defect; a declared one is a tradeoff — the record
can be judged either way later, but only if it says so.

Two boundaries keep this from drifting into cover for bad practice:

- **The strictly worse case stays refused.** A reviewer approving its own
  work with no second reader of any kind — no declaration, no evidence,
  no fixup-only pass — is not made acceptable by naming it. Declaring a
  conflict is not a licence for that case.
- **The exception is scoped and expires.** State when independence is
  expected back, and stop taking the exception once it returns. An
  exception with no stated end silently becomes the norm.

When you get to choose which agent reviews, prefer one that only touched
a fixup over one that wrote the substantive change, and say in the review
which it was.

This traces back to a standing independent reviewer becoming unavailable
for a bounded window: rather than stalling a queue of otherwise-mergeable
work indefinitely, a contributing agent reviewed its own queue with the
conflict named explicitly in each review, while still refusing the
strictly-worse case above. The exception was scoped to expire once
independence returned.

## Report honestly

State how many workers ran, what each was asked, what came back, and
which claims are backed by external evidence versus by an agent's
assertion. Unverified worker output is reported as unverified.

## Stop conditions

Stop and consolidate when: workers return contradictory results and no
external evidence settles it; a worker fails twice on the same subtask;
or the dispatch has cost more than doing the work inline would have.
Contradiction is a finding to report, not noise to re-roll away.
