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
root, 25 skills at `skills/<name>/SKILL.md` (measured `ls -d skills/*/ | wc -l`,
verified 2026-08-16T02:15Z), which is the standard's own discovery convention.
Any conformant client can consume the collection whole, with no bespoke
tooling.

That is a portability claim, not a local one. Claude Code reads its own
manifest at `.claude-plugin/plugin.json` and does not look for this file, so
adding it changed nothing for Claude Code users today. `npx skills` above
remains the way to install individual skills, and nothing here replaces it.

## Skills in this collection

All 25, flat and alphabetical — matching `skills/`'s own layout (see
[Where a skill belongs](#where-a-skill-belongs) for why this repository does
not bucket by category). Measured `ls -d skills/*/`, verified
2026-08-16T02:15Z; this table previously listed 13 and was 12 skills short of
the tree for five days (`069e2c4`, 2026-08-09, through this correction).

| Skill | Purpose |
|---|---|
| [`ask-a-council`](skills/ask-a-council/) | Convene several harnesses or models against one question, each given a distinct lens it can fail on |
| [`close-the-loop`](skills/close-the-loop/) | Confirm you have everything needed to finish a change before starting it |
| [`create-skill`](skills/create-skill/) | Design, create, and validate portable Agent Skills |
| [`dispatching-subagents`](skills/dispatching-subagents/) | Decide whether to delegate to subagents and verify their output with external evidence |
| [`distill`](skills/distill/) | Reduce a large body of source material to the smallest thing a reader can act on |
| [`failing-test-first`](skills/failing-test-first/) | Reproduce a bug with a failing test before fixing it |
| [`github-cli`](skills/github-cli/) | Manage GitHub PRs, issues, workflows, actions, and releases via `gh` |
| [`keep-me-honest`](skills/keep-me-honest/) | Push back when the user's stated belief conflicts with what you actually observed |
| [`linear`](skills/linear/) | Manage Linear issues, teams, and projects via the Linear CLI |
| [`loop-contract`](skills/loop-contract/) | Design a loop before running one — trigger, verification, stop conditions, terminal states |
| [`loop-memory`](skills/loop-memory/) | Keep the run state a repeating or long-running loop needs between iterations on disk |
| [`memory-conventions`](skills/memory-conventions/) | Read and write durable agent memory in a personal Obsidian vault |
| [`mine-transcripts`](skills/mine-transcripts/) | Mine your own agent transcripts for vocabulary that's a candidate for the next skill |
| [`notify`](skills/notify/) | Send a short message to a human on a configured outbound channel from the terminal |
| [`obsidian`](skills/obsidian/) | Read, write, search, and manage notes in Obsidian vaults |
| [`prd`](skills/prd/) | Author or review a Product Requirements Document |
| [`primer`](skills/primer/) | Orient in an unfamiliar codebase before starting work |
| [`research-the-limit`](skills/research-the-limit/) | Check a primary source before asserting a tool or system cannot do something |
| [`safe-deletion`](skills/safe-deletion/) | Verify contents or state match their described purpose before deleting or killing anything |
| [`sanity-check`](skills/sanity-check/) | Build a second-opinion reviewer prompt for high-cost reasoning |
| [`spec`](skills/spec/) | Author or review a technical specification — architecture, interfaces, trade-offs |
| [`supervised-lane-loop`](skills/supervised-lane-loop/) | Run a long-lived supervisor loop over one or more worker-agent lanes |
| [`tdd`](skills/tdd/) | Red-green-refactor for code that has never worked yet |
| [`tmux`](skills/tmux/) | Operate tmux safely from an agent: pane targeting, verified input, recovery |
| [`verify-the-instrument`](skills/verify-the-instrument/) | Check the measuring device before trusting what it reports |

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
