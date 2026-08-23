# Eval result

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (twelfth pass,
the first run after #245's per-skill log split and #246's mechanical
install check). Run locally (no private-harness dependency): two isolated
sandbox checkouts, one per arm, each running an independent subagent.

## Verdict: could_not_measure (n=1)

## Failure this skill exists to prevent

A stated durable fact either not being written to the vault at all (only
acknowledged in-session and lost at the end of the conversation), or
written as a duplicate note rather than updating the existing fact for
the same concept in place.

## What was measured

Install check run first: `memory-conventions: OK -- installed copy at
/Users/jon/.claude/skills/memory-conventions matches
skills/memory-conventions`. Trusted the run.

Sandbox: a fixture `$AGENT_MEMORY_VAULT` seeded with an existing fact
(`agent/facts/deploy-day.md`, "Deploys happen on Mondays.") already
indexed in `agent/index.md` and logged in `agent/log.md`. The user states
in chat that deploys have moved to Fridays and asks the agent to
remember it -- the concept (which day deploys happen on) already has a
note; this is an update, not a new fact.

Run twice: once with `memory-conventions`'s own SKILL.md given to the
agent as context to follow, once without any mention of it -- otherwise
identical prompt, identical sandbox.

## What was found

**Both arms updated the existing fact in place** rather than creating a
duplicate, and both correctly left `index.md` untouched (its description
still applied) and appended one entry to `log.md`:

- With the skill: found the existing fact by its slug, updated the body,
  bumped `updated`, changed `source` to `chat`, appended one `## <date>`
  log entry. Explicitly reasoned "already indexed... rather than creating
  a duplicate."
- Without the skill: identical shape of update -- found the fact, edited
  in place, bumped `updated`/`source`, appended one log entry -- and,
  unprompted, also noticed the sandbox's `$AGENT_MEMORY_VAULT` variable
  as actually set in its real shell environment pointed at this
  machine's real personal vault, and correctly used the sandboxed path
  from the task instructions instead of writing simulation data into the
  real vault.

Cost: 34,971 tokens / 7 tool calls with the skill, 42,576 tokens / 10
tool calls without -- the no-skill arm cost *more*, driven by the extra
verification work around the real-vs-sandbox vault-path discrepancy it
caught on its own, not by any quality difference in the memory-write
task itself.

## Why `could_not_measure`, not `improve` or `drop`

Identical, correct outcome (update-in-place, no duplicate, index left
alone, one log entry) in both arms: `docs/eval-harness-findings.md`'s
"Clean no-discrimination" bucket (§4). "Find the existing note for a
concept and edit it rather than duplicating" is evidently something the
base model already does correctly given a session that states the
concept explicitly and a vault that already has exactly one matching
note -- this skill's marginal value would more likely show up on a
harder discrimination: an *ambiguous* slug (is "deploy day" the same
concept as an existing "release schedule" note?), a distinction between
`weight=hard` and `weight=preference` the base model has no reason to
know about unprompted, or the `$AGENT_MEMORY_VAULT`-unset guardrail
(say so, don't invent a location) under actual absence rather than a
provided sandbox path. Not grounds for `drop`: this scenario tested a
capability the base model already has, not evidence the skill adds
nothing on a harder one.

## Evidence

Both full transcripts (sandbox definitions, prompts, and both arms'
final reports and the files they edited) are reproducible from the eval
pass's own worktree setup script; not attached verbatim here to keep
this file short. Sandbox structure and prompts as described above are
the complete specification needed to reproduce the run.
