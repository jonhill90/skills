# Eval result

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (seventh pass).
Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other
three results.

## Verdict: could_not_measure (n=1)

## What was measured

Three files (`stage-b.txt`, `stage-c.txt`, `stage-d.txt`) that must be
updated in a strict dependency chain -- each stage's correct value is
the PREVIOUS stage's newly-written value plus 10 (`stage-a.txt` given as
5; correct answers 15/25/35). On its surface this reads as "three
independent small edits," the shape that makes fanning out to parallel
subagents tempting on reflex; it is not independent -- the skill's own
"Decide first" section names this exact trap ("Do not delegate when:
the subtasks are sequential and each needs the previous one's output").
Three subagents dispatched in parallel would each read a stale value
before an earlier stage's write landed, and the final files would not
read 15/25/35.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm
(scoped real-path swap against `~/.claude/skills/`, restored
immediately after each run -- see `skills/dispatch-brief/references/
eval-result.md`'s own "A harness defect found and fixed" section for why
the safer isolated-shadow mechanism could not be used this pass, and
what was verified before falling back).

## What was found

**Both arms got every value correct**: `stage-b.txt` = 15,
`stage-c.txt` = 25, `stage-d.txt` = 35, in both runs. Read both
transcripts in full, not just the file diffs -- both explicitly named
the sequential dependency in their own final answer and explained why
they did the work inline rather than delegating:

- With the skill: "The chain is strictly sequential — each value
  depends on the one written before it — so I did it inline rather than
  fanning out; parallel agents would have read stale `TBD` values."
- Without the skill: "The chain is strictly sequential — each stage's
  input is the previous stage's *new* value — so I did this inline
  rather than fanning out, since no two steps could run concurrently."

Neither run's own tool calls include a `Task`-type subagent dispatch
(checked directly, not inferred from the prose) -- both did the work
inline, correctly, unprompted.

## Why `could_not_measure`, not `improve` or `drop`

Cost: 201,659 tokens / 6 turns with the skill, 235,785 tokens / 9 turns
without (1.2x tokens, 1.5x turns -- turns sit exactly at this harness's
own efficiency-flag threshold, `docs/eval-harness-findings.md`'s own
documented tolerance). Identical, correct outcome in both arms and a
cost delta right at the tolerance boundary is exactly Cause A from that
same file: "both arms solved the scenario correctly, and the cost delta
... fell inside the harness's own tolerance." The mechanical harness
would print `drop` for this shape; not passed through here for the same
reason it wasn't for any of #236's four results -- there is no separate
outcome in the tool itself for "this particular scenario did not
distinguish the two arms" versus "this skill measurably does nothing,"
and this pass's own base model already avoids the reflexive-parallel-
dispatch trap on this scenario without needing the skill's prompting.
That is a real result about this model on this task, not evidence the
skill is dead.

## What is not evidenced

Whether a harder version of this scenario -- more stages, or a
dependency chain less obviously stated in the prompt's own wording ("the
PREVIOUS stage file's value") -- would still be solved correctly without
the skill. This prompt states the sequential shape almost as directly as
the skill's own "Decide first" section does; a model reaching the same
conclusion from a vaguer prompt would be stronger evidence either way.
