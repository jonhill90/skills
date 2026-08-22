# Eval result

Recorded 2026-08-22, second pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that landed in the
agent-evals repository (not published here; see "Scope" above). This
file states the verdict and what was measured, not the scenario or
transcript.

## Verdict: could not measure a reliable skill-attributable difference on this scenario — not dropped

The harness's own mechanical decision table returned `drop` for this run
(its rule: both arms solved the task the same way, within its cost-delta
tolerance, so the skill made no observable difference). That number is
reported here, but not passed through as this skill's verdict: a `drop`
verdict must rest on an eval that ran and *failed*, and nothing failed
here — both arms independently caught the fabrication correctly. "Neither
arm needed the skill for this one task" is a real result about this
scenario's discriminating power, not a finding about the skill's value.

## What was measured

This skill's own SKILL.md ships a written eval case ("the fabrication
incident"): an agent write-up confidently attributes a specific,
invented requirement to "prior instructions," and the acceptance test is
whether a review catches that the cited source doesn't actually support
the claim. Turned into a fixture: a write-up citing a corpus, and the
corpus itself containing nothing that supports the claim.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm:

- **Without the skill:** the run read the corpus itself, found no support
  for the claim, and correctly flagged it as unsupported.
- **With the skill:** the same — corpus checked, same correct verdict,
  similar cost (tokens/turns within the harness's own no-flag tolerance).

## Why this scenario didn't discriminate, and what would

This skill's own framing is explicit that a council earns its cost when
"the failure modes genuinely differ in kind — a single reviewer's prompt
would only catch what its own lens looks for." The fabrication-incident
scenario, as written and as fixtured here, is catchable by a single
check: read the cited corpus, see it doesn't contain the claim. That is
exactly the kind of task a capable model does not need multiple lenses
or evidence-partitioned reviewers to get right — it needed one grep-shaped
step, which both arms took unprompted. This scenario proves the
mechanism's own worked example is *sound* (an evidence-blind, persona-only
review would have missed it, per the skill's own text) without proving
the *skill* changes behavior on a task that only needs one lens to solve.

A scenario that would actually discriminate needs a task where the
failure modes genuinely differ in kind — e.g. one requiring a
mechanism-level read AND a legitimacy-level read AND a portability-level
read to converge, where a single-lens review plausibly stops after
finding the first thing and never looks for the others. That is a
harder fixture to build than this pass had time for.

## What is not evidenced

Whether `ask-a-council` changes behavior on a task that genuinely needs
multiple distinct lenses remains untested. This result is specific to a
single-lens-solvable case; it does not generalize to the skill's actual
target use case.
