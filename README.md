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

## Skills in this collection

| Skill | Purpose |
|---|---|
| [`close-the-loop`](skills/close-the-loop/) | Confirm you have everything needed to finish a change before starting it |
| [`create-skill`](skills/create-skill/) | Design, create, and validate portable Agent Skills |
| [`dispatching-subagents`](skills/dispatching-subagents/) | Decide whether to delegate to subagents and verify their output with external evidence |
| [`failing-test-first`](skills/failing-test-first/) | Reproduce a bug with a failing test before fixing it |
| [`github-cli`](skills/github-cli/) | Manage GitHub PRs, issues, workflows, actions, and releases via `gh` |
| [`linear`](skills/linear/) | Manage Linear issues, teams, and projects via the Linear CLI |
| [`memory-conventions`](skills/memory-conventions/) | Read and write durable agent memory in a personal Obsidian vault |
| [`obsidian`](skills/obsidian/) | Read, write, search, and manage notes in Obsidian vaults |
| [`primer`](skills/primer/) | Orient in an unfamiliar codebase before starting work |
| [`safe-deletion`](skills/safe-deletion/) | Verify contents match their described purpose before deleting anything |
| [`sanity-check`](skills/sanity-check/) | Build a second-opinion reviewer prompt for high-cost reasoning |
| [`supervised-lane-loop`](skills/supervised-lane-loop/) | Run a long-lived supervisor loop over one or more worker-agent lanes |
| [`tmux`](skills/tmux/) | Operate tmux safely from an agent: pane targeting, verified input, recovery |

Each skill's `description` frontmatter is the actual trigger contract —
read the skill itself for exact wording and preconditions.

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
