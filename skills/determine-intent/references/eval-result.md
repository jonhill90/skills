# Eval result

Recorded 2026-08-22, fourth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## A scorer defect found and fixed before trusting this number

The harness's own scorer initially returned "neither arm solved it" for
BOTH arms, flagging `invented_constraint=True` on runs whose actual
deliverable added nothing of the kind. The check matched a set of
rendering-related keywords ("static export", "hydrat[ion]", ...) against
the run's own prose, and both runs' prose mentioned these concepts —
correctly, to explain that the phantom constraint had been noticed and
declined, not because either run had built it. A bare keyword match
cannot tell "discussed and declined" apart from "built"; checked by
hand against the actual artifact (`widgets/active-lanes.js` in each
arm's own fixture directory) and confirmed neither file contains
anything resembling static-export or hydration handling — both are a
plain `render`/`poll`/`module.exports` mirror of the existing
`queue-depth.js`, nothing more. The scorer was fixed to check only the
artifact (this skill's own criteria.md already names the artifact as the
load-bearing evidence for this observable; the prose check was an
over-reach beyond what criteria.md itself specifies) — no second live run
was needed, since `asked_settled_question` and the task-solved fields
were already correctly computed and recorded from the original run's own
output.

## What was measured

Two of `determine-intent`'s own named failure modes from its documented
incident (jonhill90/skills#213): asking a question the corpus already
settles, and treating an uncited, soft aside as a binding requirement.
The scenario asks the run to add a dashboard widget with no mention of
rendering at all; `notes/decisions.md` already settles that the dashboard
is SSR-only (a standing 2026-06-01 decision), and the widget file being
mirrored (`queue-depth.js`) carries a stray, explicitly-non-binding aside
comment ("would be nice if this could someday also run in a static
export, but nobody's asked for that").

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm, after
the scorer fix: both arms added the widget correctly (new
`widgets/active-lanes.js` mirroring the existing pattern, a new
`widgets/registry.json` entry), neither asked about rendering mode, and
neither added any static-export/hydration handling. Cost: with the
skill, 8 turns / 165,986 tokens; without, 8 turns / 197,318 tokens — a
1.19x token ratio and 1.0x turn ratio, both inside the ×1.5 threshold
this harness's own `verdict()` treats as noise.

## Why `could_not_measure`, not `drop`

Both of this skill's own named failure modes were avoided in both arms —
neither run asked the settled question, neither run built the phantom
constraint. The outcome axis did not move, and (once the scorer's false
positive was corrected) neither did cost by a meaningful margin. Same
reasoning as this loop's own `durable-fact-before-label`/
`determine-signals` results (jonhill90/skills#233): a wash is not a
`drop` — nothing failed, and this skill's own incident
(jonhill90/skills#213) is real and specific enough that one clean pass
by a strong model does not settle whether it matters on a harder case.

## What is not evidenced

Whether Opus 5 avoids both failure modes on this kind of request by
default regardless of the skill, or whether a request phrased closer to
the real incident's own shape (a watchdog-style loop under time
pressure, rather than a single clean headless turn) would surface either
failure mode where this scenario did not. The outcome axis did not move
here, matching this pass's other two results — a genuinely harder
version of this scenario has not been built.
