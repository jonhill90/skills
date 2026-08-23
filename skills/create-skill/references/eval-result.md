# Eval result

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (twelfth pass,
the first run after #245's per-skill log split and #246's mechanical
install check). Run locally (no private-harness dependency): two isolated
sandbox checkouts, one per arm, each running an independent subagent.

## Verdict: could_not_measure (n=1)

## Failure this skill exists to prevent

Installing a repo-specific skill into a shared, cross-project roster
without first checking whether it actually needs to be there -- the
skill's own "Ask where it belongs first" table exists because a
single-repository need does not earn a place in a roster loaded on every
session everywhere.

## What was measured

Install check run first (jonhill90/skills#230, #246): `create-skill: OK
-- installed copy at /Users/jon/.claude/skills/create-skill matches
skills/create-skill`. Trusted the run.

Sandbox: a minimal git repo styled as a shared, cross-project skills
collection (its own `AGENTS.md` describes it as "a collection of reusable
Agent Skills used across this team's projects", deliberately without
spelling out a placement rule -- see "A scenario-design defect caught and
fixed" below for why that mattered). A teammate message asks for a skill
to be added for a `widgets-service`-only deploy checklist, explicitly
"we only use it in that one repo," with the stated reason for wanting it
in the shared collection being setup friction ("I don't have another
skills folder set up there yet").

Run twice: once with `create-skill`'s own SKILL.md given to the agent as
context to follow, once without any mention of it -- otherwise identical
prompt, identical sandbox.

## What was found

**Both arms declined to add the skill to the shared repo**, independently
reaching the same conclusion by the same basic reasoning: a single-repo
need does not belong in a cross-project roster, "I don't have a folder
there yet" is a setup-friction reason rather than a placement reason, and
the correct fix is `widgets-service/.claude/skills/deploy-checklist/
SKILL.md` in the other repo. Neither arm created any file in the sandbox.

- With the skill: cited create-skill's own placement table directly
  ("One repository only → that repo's own `.claude/skills/`... no
  evidence bar, just write it") and the teammate's own words as a
  textbook match for that row.
- Without the skill: reasoned from the sandbox's own `AGENTS.md`
  description alone ("a shared, cross-project library... your ask is for
  a checklist that's specific to widgets-service") to the identical
  conclusion, plus confirmed via `git remote -v` that no `widgets-service`
  checkout exists in the sandbox.

Cost: 35,539 tokens / 4 tool calls with the skill, 33,449 tokens / 3 tool
calls without -- a 6% token delta, inside this harness's own noise
tolerance (`docs/eval-harness-findings.md`).

## A scenario-design defect caught and fixed mid-pass

The first version of this sandbox's `AGENTS.md` stated the placement rule
explicitly ("single-repository skills belong in their own repositories,
not here"), copied from this real repo's own `AGENTS.md`. Both arms
declined identically on that draft too, for the same reason `docs/
eval-harness-findings.md`'s "Scenario design defect" bucket names: the
fixture itself carried the answer, so nothing about the create-skill
skill was actually under test -- the base model just had to read one
sentence in the repo it was already told to read. Caught before
recording anything, by noticing both arms cited the exact same sentence
verbatim rather than reasoning toward it. Rewritten to a neutral
`AGENTS.md` (states what the repo is, not where things do or don't
belong) and re-run from scratch on both arms -- the result above is the
re-run, not the original draft.

## Why `could_not_measure`, not `improve` or `drop`

Identical, correct outcome in both arms, and a cost delta inside
tolerance: this is `docs/eval-harness-findings.md`'s "Clean
no-discrimination" bucket (§4) -- the scenario didn't fail to run, it
ran cleanly and simply didn't separate the arms, because the base model
already reasons about cross-project-roster placement correctly without
this skill's explicit table. That is a real property of the current base
model on this exact scenario, not a defect in the skill, and not grounds
for `drop` -- a differently-shaped scenario (a repo whose own
`AGENTS.md` says nothing at all about scope, or a request where the
"it's more convenient here" pressure is stronger) might still
discriminate; this one didn't.

## Evidence

Both full transcripts (sandbox definitions, prompts, and both arms' final
reports) are reproducible from the eval pass's own worktree setup script;
not attached verbatim here to keep this file short. Sandbox structure and
prompts as described above are the complete specification needed to
reproduce the run.
