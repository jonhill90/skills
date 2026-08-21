# skills

Jon Hill's public collection of portable [Agent
Skills](https://agentskills.io/specification) — self-contained,
model- and harness-agnostic instructions an AI coding agent loads on
demand. Every skill here is individually installable; nothing in this
repository is specific to any one harness, and nothing here depends on
private tooling or evidence.

## Install

Browse the collection:

```bash
npx skills add jonhill90/skills --list
```

Install one or more specific skills into the current project:

```bash
npx skills add jonhill90/skills --skill tmux --skill github-cli
```

`npx skills` pins installs by content hash in `skills-lock.json`, so a
project's skill set stays reproducible. See the [skills
CLI](https://www.npmjs.com/package/skills) for the full command
reference.

### As an Agent Plugin

This repository is also an [Agent Plugins
1.0.0](https://agent-plugins.org/specification) plugin: `plugin.json` at the
root, 38 skills at `skills/<name>/SKILL.md` (measured `ls -d skills/*/ | wc -l`,
verified 2026-08-21), which is the standard's own discovery convention.
Any conformant client can consume the collection whole, with no bespoke
tooling.

That is a portability claim, not a local one. Claude Code reads its own
manifest at `.claude-plugin/plugin.json` and does not look for this file, so
adding it changed nothing for Claude Code users today. `npx skills` above
remains the way to install individual skills, and nothing here replaces it.

## Skills in this collection

All 38, flat and alphabetical — matching `skills/`'s own layout (see
[Where a skill belongs](#where-a-skill-belongs) for why this repository does
not bucket by category). Measured `ls -d skills/*/`, verified 2026-08-21.
This table has drifted from the tree twice: 12 skills short for five days
(`069e2c4`, 2026-08-09) and, a second time, 13 skills short until this
correction (skills#224) — `scripts/validate_repository.py`'s
`validate_readme_table` check now fails CI when the table and `skills/`
disagree, so a hand-edit that drops or misnames a row is caught before it
reaches the public repository.

| Skill | Purpose |
|---|---|
| [`adopt-or-build`](skills/adopt-or-build/) | Decide, per component, whether to adopt an existing dependency or build it in-house, weighing blast radius over convenience |
| [`ask-a-council`](skills/ask-a-council/) | Convene several harnesses or models against one question, each given a distinct lens it can fail on |
| [`close-the-loop`](skills/close-the-loop/) | Confirm you have everything needed to finish a change before starting it |
| [`create-skill`](skills/create-skill/) | Design, create, and validate portable Agent Skills |
| [`decide-by-variant`](skills/decide-by-variant/) | Build several genuinely different real artifacts with fake data and let the human pick by looking |
| [`derive-independently-then-compare`](skills/derive-independently-then-compare/) | Derive an answer from the source corpus a second time, blind to the first derivation, then compare |
| [`determine-intent`](skills/determine-intent/) | Work out what the user actually wants before starting the work, and state that reading so it can be corrected |
| [`determine-signals`](skills/determine-signals/) | Find out what has already been said before asking a question or restating a fact as current |
| [`devils-advocate`](skills/devils-advocate/) | Argue the strongest honest case against a plan or decision before it is committed |
| [`dispatch-brief`](skills/dispatch-brief/) | Write the brief that hands work to a lane or subagent — name the failure, demand two-directional mutation, forbid weakening the guard |
| [`dispatching-subagents`](skills/dispatching-subagents/) | Decide whether to delegate to subagents and verify their output with external evidence |
| [`distill`](skills/distill/) | Reduce a large body of source material to the smallest thing a reader can act on |
| [`durable-fact-before-label`](skills/durable-fact-before-label/) | Write the durable record before the label that points at it, so a crash leaves a stale label, not a broken record |
| [`failing-test-first`](skills/failing-test-first/) | Reproduce a bug with a failing test before fixing it |
| [`github-cli`](skills/github-cli/) | Manage GitHub PRs, issues, workflows, actions, and releases via `gh` |
| [`keep-me-honest`](skills/keep-me-honest/) | Push back when the user's stated belief conflicts with what you actually observed |
| [`linear`](skills/linear/) | Manage Linear issues, teams, and projects via the Linear CLI |
| [`loop-contract`](skills/loop-contract/) | Design a loop before running one — trigger, verification, stop conditions, terminal states |
| [`loop-memory`](skills/loop-memory/) | Keep the run state a repeating or long-running loop needs between iterations on disk |
| [`mechanize`](skills/mechanize/) | Decide whether a step done by AI inference should become a deterministic tool instead |
| [`memory-conventions`](skills/memory-conventions/) | Read and write durable agent memory in a personal Obsidian vault |
| [`mine-transcripts`](skills/mine-transcripts/) | Mine your own agent transcripts for vocabulary that's a candidate for the next skill, judging what an extractor tool hands back |
| [`notify`](skills/notify/) | Send a short message to a human on a configured outbound channel from the terminal |
| [`obsidian`](skills/obsidian/) | Read, write, search, and manage notes in Obsidian vaults |
| [`plan-parallel-execution`](skills/plan-parallel-execution/) | Turn a task list into groups several agents can execute concurrently without colliding |
| [`prd`](skills/prd/) | Author or review a Product Requirements Document |
| [`primer`](skills/primer/) | Orient in an unfamiliar codebase before starting work |
| [`prompt-corpus`](skills/prompt-corpus/) | Turn a transcript history into a queryable record of decisions |
| [`refuse-invented-identity`](skills/refuse-invented-identity/) | Refuse and report unrecoverable when a recovery path cannot positively confirm the prior identity it is restoring |
| [`research-the-limit`](skills/research-the-limit/) | Check a primary source before asserting a tool or system cannot do something |
| [`safe-deletion`](skills/safe-deletion/) | Verify contents or state match their described purpose before deleting or killing anything |
| [`sanity-check`](skills/sanity-check/) | Build a second-opinion reviewer prompt for high-cost reasoning |
| [`spec`](skills/spec/) | Author or review a technical specification — architecture, interfaces, trade-offs |
| [`supervised-lane-loop`](skills/supervised-lane-loop/) | Run a long-lived supervisor loop over one or more worker-agent lanes |
| [`tdd`](skills/tdd/) | Red-green-refactor for code that has never worked yet |
| [`test-in-the-consumer-context`](skills/test-in-the-consumer-context/) | Run a check where the thing that depends on it runs, before believing its verdict |
| [`tmux`](skills/tmux/) | Operate tmux safely from an agent: pane targeting, verified input, recovery |
| [`verify-the-instrument`](skills/verify-the-instrument/) | Check the measuring device before trusting what it reports |
| [`wire-it-when-you-write-it`](skills/wire-it-when-you-write-it/) | Ship a mechanism and its caller in the same change, and add the check that fails when the caller disappears |

Each skill's `description` frontmatter is the actual trigger contract —
read the skill itself for exact wording and preconditions. This repository
does not yet distinguish user-invoked from model-invoked skills anywhere a
reader sees before opening `SKILL.md` — tracked as open in
[`docs/skills-docs-proposal-161.md`](docs/skills-docs-proposal-161.md).

## Where a skill belongs

Most skills should **not** live in this repository. Decide placement
first:

| Situation | Where it goes |
|---|---|
| Useful across many unrelated projects, every day | a public collection like this one |
| Only true in one repository | that repo's own `.claude/skills/` or `.agents/skills/` |
| Needed once, or maintained by someone else | nothing installed — `npx skills use <package>@<skill>` |

## Authoring contract

Each skill lives at `skills/<name>/SKILL.md`:

```text
skills/example-skill/
├── SKILL.md
├── scripts/       Optional deterministic, tested helpers
├── references/    Optional detail loaded on demand
└── assets/        Optional output resources
```

Portable frontmatter is `name` and `description` (plus optional
`license`, `compatibility`, `metadata`, `allowed-tools`). The directory
name must match `name`. Keep `SKILL.md` under 500 lines and move detail
into directly linked `references/`. Full conventions: [AGENTS.md](AGENTS.md).

## Validate

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
```

CI runs both on every pull request and on pushes to `main`.

## Content boundaries

- This repository holds only portable skill content and the minimal
  validation/tests/CI needed to keep it correct.
- Personal harness configuration — canonical instructions, hooks,
  agents, settings, MCP declarations, install/sync tooling — lives in a
  separate personal harness repository that consumes this collection; it
  is not vendored here.
- Behavioral evaluation methodology, scenarios, transcripts, and results
  are private and are not published in this repository. Where a skill
  references past evidence, it states what happened and when without a
  link to private material.
- Employer-owned or project-specific material is never copied here.

See [AGENTS.md](AGENTS.md) for contribution rules.
