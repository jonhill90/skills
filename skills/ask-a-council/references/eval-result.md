# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop (estate-loop/agent-b2.md), superseding this file's own second-pass
result. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario itself is committed at
`skills/ask-a-council/references/eval-scenario/` so it can be re-run.

## Verdict: could_not_measure (still)

## Why this pass exists

`docs/eval-harness-findings.md`'s Cause A named this skill's own second-
pass scenario as single-lens-solvable by design: a fabrication citing a
corpus that plainly didn't support it, catchable by one grep-shaped step.
Both arms took that one step and the scenario never put the skill's own
actual claim -- that some artifacts need genuinely different lenses to
surface everything wrong with them -- at any real risk.

## The new scenario

`monitor.py` plus two real logs, engineered with two INDEPENDENT,
different-kind defects instead of one single-lens-solvable one:

1. **Mechanism**: `check_backlog()`'s `n > THRESHOLD` never pages at
   exactly the documented threshold (100) -- a real off-by-one, findable
   by reading the code, and directly evidenced in `last-night.log`
   itself ("queue backlog 100 -- within limits").
2. **Legibility**: `page_oncall()`'s exception handler logs "SENT" even
   when the outbound call fails -- `last-night.log` claims a page went
   out; `webhook-attempts.log` (a separate file) shows that same request
   actually returned `500`. Reading the code alone does not surface this;
   only cross-referencing the log's own claim against a second source
   does.

Finding one does not make finding the other more likely -- they are
independent questions about independent parts of the same artifact,
matching the shape of this skill's own worked example (`watchdog.sh`,
jonhill90/skills#147: the highest-value finding came from the legibility
lens, not from either bug-hunter).

## What was measured

Run twice, live, same task, same fixture, once with `ask-a-council`
installed and once with it removed via the harness's `no-skill:<name>`
arm:

- **With the skill:** found both defects. Its own answer states it
  "settled both with direct runs rather than a review panel, since the
  boundary and the failure path are both cheaply testable" -- i.e., it
  read `ask-a-council`'s own text, correctly applied the skill's OWN
  "check the frame before convening" rule (RULE B2), and concluded a
  council was not warranted for this specific case. 7 turns, 171,296
  tokens.
- **Without the skill:** found both defects independently, same
  reasoning depth, no council convened (there was nothing to convene
  with the skill absent). 7 turns, 165,181 tokens (1.04x -- inside the
  harness's ×1.5 tolerance).

## Why this is still could_not_measure, and what it actually shows

Both arms found both defects unassisted. This is a genuinely different,
and more interesting, non-result than the first pass's: it is not that
the scenario was single-lens-solvable -- it has two real, independent,
different-kind issues -- it is that **a single capable model, given
enough turns to actually read both logs carefully, does not need to
literally dispatch separate reviewers to check two different things**.
The skill's own text already anticipates this ("run cheap deterministic
checks before convening anyone... convene only once cheap checks are
exhausted") -- and the WITH arm's own transcript shows it correctly
choosing NOT to convene, for exactly the reason the skill gives. That is
the skill working as designed on this task, not the skill failing to
matter: a well-applied `ask-a-council` on a two-defect, both-cheaply-
checkable artifact is supposed to conclude "no council needed" -- which
means this scenario, even redesigned around the skill's own documented
gap, still cannot show what a GENUINE multi-agent convening changes,
because the artifact was never one this skill's own rules would dispatch
a council against in the first place.

## What is not evidenced

Whether `ask-a-council` changes behavior on an artifact large or complex
enough that ONE context window cannot hold everything needed to check
both a mechanism-level and a legibility-level question thoroughly in one
continuous pass -- e.g. a real multi-file service where the log
cross-reference requires following state across several systems, not two
small files in one directory. That is a harder fixture to build than
this pass had time for, and per this skill's own step 5, may be the only
kind of case where a council is genuinely warranted over one careful
pass.
