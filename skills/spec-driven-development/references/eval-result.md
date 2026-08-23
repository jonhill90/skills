# Eval result

Recorded 2026-08-22, seventh pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/spec-driven-development/references/eval-scenario/` so it can be
re-run.

## Verdict: could_not_measure (n=1)

## A real environment defect, caught before the first live run counted

This skill was not installed on this machine's shared skills path at
all -- one of the 5 skills out of this repo's 40 that `~/.claude/skills/`
doesn't symlink (same class of gap `durable-fact-before-label`'s and
this pass's own `wire-it-when-you-write-it`/`dispatch-brief` results
document). Symlinked it in for this pass's real run, then removed the
symlink again afterward.

## The scenario

This skill's own trigger case: "deciding whether a request duplicates
something already shipped. A criterion written before starting is also
a search: if it already holds against the current system, the work is
done, not begun." The fixture repo already has `utils/slugify.py`'s
`to_slug()`, wired into `routes.py`, doing exactly what the prompt asks
for under a different name ("slugify" appears nowhere in the prompt's
own wording). The prompt is phrased as ordinary new-feature work, with
no hint that it already exists.

## What was measured

Run once, same task, same fixture, once with
`spec-driven-development` installed and once with it removed via the
harness's `no-skill:<name>` arm: both arms searched the codebase for
existing slug-related code, found `to_slug()`, reported that the
functionality already exists rather than writing a duplicate, and left
`utils/slugify.py` unchanged. Cost was essentially identical (132,405 vs.
131,958 tokens, ~1.003x; 4 turns each).

## Why could_not_measure, not drop

Both arms did the right thing -- checked before building, found the
existing implementation, said so. Nothing failed. This is a real result
about Opus 5's own default habit of searching before writing new code on
a task this size, not evidence the skill's actual claim (that the
criterion-as-search discipline changes outcomes) is false.

## What is not evidenced

Whether the same holds on a larger or less obviously-searchable
codebase, where finding the existing implementation requires more than
one grep -- this fixture's `utils/slugify.py` is one small file, three
lines from the entrypoint the prompt already implies (`routes.py`). A
harder version of this scenario, closer to this skill's own stated
"non-trivial work" scope, has not been built.
