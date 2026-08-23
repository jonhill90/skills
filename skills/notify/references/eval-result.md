# Eval result

Recorded 2026-08-23, tenth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=2, scenario design defect found, not a scorer bug)

## Criterion update for this pass

As with this pass's other two picks, no remaining unevaluated candidate
had a documented incident in its own SKILL.md text. `notify` was picked
for institutional knowledge that lives only in its own text and is not
inferable from a repo: `SKILL.md`'s Channel priority section says "5.
Slack — deferred indefinitely, unused since 2019. Do not build it."

## What was measured

A trimmed, standalone copy of the real `notify.py` (Telegram + iMessage
implemented) with a request to "add Slack support... since our team
just moved to Slack." Scored on: did the run avoid implementing Slack
support, and did it name the actual deferred-since-2019 reason rather
than a generic hedge.

## The scenario did not exercise the skill at all — in either arm

Both live pairs (four runs total) built Slack support, with or without
the skill installed. Hand-reading the tool-call sequence explained why:
in every OTHER scenario this pass and the prior one, the skill-installed
arm's very first or near-first tool call is `Skill` naming the matching
skill (`{"skill": "keep-me-honest"}`, `{"skill": "failing-test-first"}`)
— the model recognizing the task as this skill's own trigger and pulling
in its text. For `notify`, across both independent pairs, the
skill-installed arm never once called the `Skill` tool. One run got as
far as `ls -R ~/.claude/skills/notify` (discovering the directory
exists) but never read `SKILL.md` itself; the other didn't look at
`~/.claude/skills/` at all. The skill's own "do not build it" line
never entered context in any of the four runs — not because the skill
lacks the knowledge, but because "modify this skill's own script to add
a feature" doesn't read, to the model's own skill-selection judgement,
as the kind of task `notify`'s own trigger conditions describe ("a
caller has already decided a human needs to know something now").

This is not a scorer bug — `_ADDED_SLACK`/`_DECLINED_SPECIFIC` correctly
identified that Slack was built and that no specific reason was named,
in every run, confirmed by hand-reading all four result texts. It is a
scenario design defect: framing the request as an engineering change to
the skill's own script, rather than as a request to *use* the skill for
its actual purpose (sending a message), does not reliably cause the
skill to be consulted at all, so the with/without conditions never
actually differed on the axis this scenario meant to test. Same root-cause
category as this loop's eighth-pass `mine-transcripts` finding (a
scenario bug, not a skill or harness bug) — reported here rather than
silently rewriting the prompt mid-pass.

## Why `could_not_measure`, not `drop`

A skill whose text is never read cannot be credited with having "no
effect" — that would misrepresent a scenario-design failure as evidence
about the skill. Recorded `could_not_measure`.

## What is not evidenced

Whether `notify`'s Slack caveat changes behavior when the skill is
actually consulted for this task — e.g. if the prompt were framed as
"a caller decided to notify about X, but Slack was requested as the
channel" (matching the skill's own stated trigger) rather than "add a
feature to this script." That reframed version was not built or run
this pass; it is the natural next attempt if this skill comes up again.
