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
root, every skill at `skills/<name>/SKILL.md` (the generated table below is the
count), which is the standard's own discovery convention.
Any conformant client can consume the collection whole, with no bespoke
tooling.

### As a Claude Code plugin

`.claude-plugin/` makes this repository its own Claude Code marketplace with
one plugin, `jonhill90-skills`, that contains every skill:

```bash
claude plugin marketplace add jonhill90/skills
```

```bash
claude plugin install jonhill90-skills@jonhill90
```

The plugin has no pinned version, so each install and update takes the
latest commit on `main`. It loads the whole collection, which adds roughly
5.6k tokens of skill descriptions to every session (measured 2026-09-30 with
`claude plugin details`). To take only a few skills, use `npx skills` above.

## Skills in this collection

<!-- generated-skills:start -->

Generated from 42 skills; do not hand-edit.
Regenerate with `python3 scripts/skills_table.py`; verify with `--check`.
Upload audit PASS = no local-machine or CLI assumptions detected; FAIL = review before using without a shell.

| Skill | Upload audit |
|---|---|
| [`adopt-or-build`](skills/adopt-or-build/) | FAIL |
| [`ask-a-council`](skills/ask-a-council/) | PASS |
| [`close-the-loop`](skills/close-the-loop/) | PASS |
| [`create-skill`](skills/create-skill/) | FAIL |
| [`decide-by-variant`](skills/decide-by-variant/) | PASS |
| [`derive-independently-then-compare`](skills/derive-independently-then-compare/) | PASS |
| [`determine-intent`](skills/determine-intent/) | PASS |
| [`determine-signals`](skills/determine-signals/) | PASS |
| [`devils-advocate`](skills/devils-advocate/) | PASS |
| [`dispatch-brief`](skills/dispatch-brief/) | PASS |
| [`dispatching-subagents`](skills/dispatching-subagents/) | PASS |
| [`distill`](skills/distill/) | PASS |
| [`durable-fact-before-label`](skills/durable-fact-before-label/) | PASS |
| [`failing-test-first`](skills/failing-test-first/) | PASS |
| [`github-cli`](skills/github-cli/) | FAIL |
| [`keep-me-honest`](skills/keep-me-honest/) | PASS |
| [`linear`](skills/linear/) | FAIL |
| [`loop-contract`](skills/loop-contract/) | PASS |
| [`loop-memory`](skills/loop-memory/) | FAIL |
| [`mechanize`](skills/mechanize/) | PASS |
| [`memory-conventions`](skills/memory-conventions/) | FAIL |
| [`mine-transcripts`](skills/mine-transcripts/) | FAIL |
| [`notify`](skills/notify/) | FAIL |
| [`obsidian`](skills/obsidian/) | FAIL |
| [`organize-repository`](skills/organize-repository/) | PASS |
| [`plan-parallel-execution`](skills/plan-parallel-execution/) | PASS |
| [`prd`](skills/prd/) | PASS |
| [`primer`](skills/primer/) | FAIL |
| [`progressive-disclosure`](skills/progressive-disclosure/) | PASS |
| [`prompt-corpus`](skills/prompt-corpus/) | FAIL |
| [`refuse-invented-identity`](skills/refuse-invented-identity/) | PASS |
| [`research-the-limit`](skills/research-the-limit/) | PASS |
| [`safe-deletion`](skills/safe-deletion/) | PASS |
| [`sanity-check`](skills/sanity-check/) | PASS |
| [`spec`](skills/spec/) | PASS |
| [`spec-driven-development`](skills/spec-driven-development/) | PASS |
| [`supervised-lane-loop`](skills/supervised-lane-loop/) | FAIL |
| [`tdd`](skills/tdd/) | PASS |
| [`test-in-the-consumer-context`](skills/test-in-the-consumer-context/) | PASS |
| [`tmux`](skills/tmux/) | FAIL |
| [`verify-the-instrument`](skills/verify-the-instrument/) | PASS |
| [`wire-it-when-you-write-it`](skills/wire-it-when-you-write-it/) | PASS |

<!-- generated-skills:end -->

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
- There is no behavioral eval system here for now; a community-maintained
  replacement is tracked in
  [#309](https://github.com/jonhill90/skills/issues/309). Where a skill
  references past evidence, it states what happened and when without a
  link to private material.
- Employer-owned or project-specific material is never copied here.

See [AGENTS.md](AGENTS.md) for contribution rules.
