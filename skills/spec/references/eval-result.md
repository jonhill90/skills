# Eval result

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop (twelfth pass,
the first run after #245's per-skill log split and #246's mechanical
install check). Run locally (no private-harness dependency): two isolated
sandbox checkouts, one per arm, each running an independent subagent.

## Verdict: could_not_measure (n=1)

## Failure this skill exists to prevent

A requested technical spec turning into PRD-flavored prose -- justifying
*why* a feature matters to users or the business, vague on interfaces
and architecture -- rather than a document an implementing engineer could
build from, with a real alternatives-considered section rather than
decoration.

## What was measured

Install check run first: `spec: OK -- installed copy at
/Users/jon/.claude/skills/spec matches skills/spec`. Trusted the run.

Scenario: "write a technical spec for adding a rate limiter to our API
gateway. We're a Go monolith, and we already use Redis for caching," with
no PRD given and instructions to make and state assumptions rather than
ask. Chosen because the request names no requirements up front -- the
default failure this skill's own doc calls out ("stating why a problem
matters to a user... belongs in the corresponding prd") is likely when
nothing has already settled the *what*, leaving *why* as the easy filler.

Run twice: once with `spec`'s own SKILL.md given to the agent as context
to follow, once without any mention of it -- otherwise identical prompt.
Both wrote to `SPEC-rate-limiter.md`.

## What was found

**Both arms produced a document following the skill's own five-section
structure**, matching heading-for-heading (context and requirements,
approach, alternatives considered and rejected, trade-offs and risks,
verification) without prompting for that shape in the no-skill arm, and
neither contains PRD-flavored "why this matters to users" framing --
both open directly with the stated assumptions and requirements needed
to build, not a justification for building it:

- With the skill (295 lines): sliding-window-counter algorithm via a
  Redis Lua script, a `Limiter` interface with `RedisLimiter`, explicit
  fail-open policy with a bounded fallback and a metric, five
  alternatives named and rejected with reasons (token bucket, fixed
  window, in-process-only, fail-closed, sidecar proxy).
- Without the skill (321 lines): GCRA/token-bucket via Redis Lua, the
  same `Limiter`-interface middleware shape, explicit fail-open policy,
  five alternatives named and rejected (standalone gateway, in-process,
  fixed window, sliding-window log, client-side-only), plus its own
  explicit non-goals section.

Both state assumptions explicitly rather than silently, both include a
real (non-decorative) alternatives section with distinct rejection
reasons per option, and both close with a concrete verification plan
(unit/integration/load tests, a rollout check).

Cost: 38,165 tokens / 2 tool calls with the skill, 39,497 tokens / 2 tool
calls without -- a 3% token delta, inside this harness's own noise
tolerance.

## Why `could_not_measure`, not `improve` or `drop`

Structurally near-identical, correct-shaped output in both arms: `docs/
eval-harness-findings.md`'s "Clean no-discrimination" bucket (§4). The
base model already knows the shape of a good technical spec -- context,
approach, real alternatives, trade-offs, verification -- without this
skill's explicit five-section list; the PRD-flavored failure this skill
names as its reason to exist did not occur in either arm on this
scenario. Not grounds for `drop`: this skill's marginal value more
plausibly shows up on a request that already has PRD-shaped material
mixed into it (e.g. "explain to leadership why we need a rate limiter and
how it'll work"), which pulls toward the conflation this skill exists to
catch, rather than a clean "write a spec" request with no such material
present to begin with.

## Evidence

Both full transcripts (prompts and both arms' final reports and the
documents they wrote) are reproducible from the eval pass's own worktree
setup script; not attached verbatim here to keep this file short. The
scenario as described above is the complete specification needed to
reproduce the run.
