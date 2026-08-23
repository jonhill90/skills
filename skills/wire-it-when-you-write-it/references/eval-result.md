# Eval result

Recorded 2026-08-22, seventh pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/wire-it-when-you-write-it/references/eval-scenario/` so it can
be re-run.

## Verdict: could_not_measure (n=1)

## A real environment defect, caught before the first live run counted

This skill was not installed on this machine's shared skills path at
all (one of 5 skills out of this repo's 40 that `~/.claude/skills/`
doesn't symlink -- pre-existing, same class of gap
`durable-fact-before-label`'s own eval-result.md documents from the
prior pass). The first live attempt was discarded entirely once this
was found -- both arms had silently run without the skill either way.
Symlinked the skill in for one real pair, then removed the symlink
again afterward.

## The scenario

This skill's own trigger case, reproduced directly from its own incident
list (`acp_transport.py`: 302 lines, ~15 test classes, 0 lanes ever used
it): a fixture repo has `deploy.sh` (the real entrypoint, does nothing
about uncommitted changes yet) and `check_clean.sh` (a fully-written,
already-tested guard that nothing calls). The prompt asks to make
`deploy.sh` refuse on a dirty tree and says to look around first. Scored
by actually RUNNING the run's own final `deploy.sh` against a dirtied
fixture repo and checking it refuses -- not by grepping the source for
whether it mentions `check_clean`, which a call that's present but
unreached would also pass.

## What was measured

Run once (properly, with the skill genuinely installed), same task,
same fixture, once with `wire-it-when-you-write-it` installed and once
with it removed via the harness's `no-skill:<name>` arm: both arms found
`check_clean.sh`, wired it into `deploy.sh`'s real execution path, and
the resulting `deploy.sh` genuinely refused when run against a dirty
tree. Cost was a wash (335,178 vs. 329,311 tokens, ~1.02x; 13 turns
each) -- inside the harness's own ×1.5 tolerance.

## Why could_not_measure, not drop

Nothing failed; both arms produced a real, demonstrated fix, not just
code that looks wired. This scenario's own trap (an already-tested,
unwired mechanism sitting next to the entrypoint that should call it) is
real and specific to this skill's own incident, but Opus 5 at this
model tier finds and wires it without needing the skill's own
prompting on this particular task shape.

## What is not evidenced

Whether the same holds on a task where the unwired mechanism is farther
from the entrypoint the prompt names directly -- e.g. requiring a search
across several files or a less obviously-related directory before the
existing, unwired mechanism is even found, rather than sitting one
`ls` away in the same small repo this scenario used.
