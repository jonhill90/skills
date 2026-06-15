# Skills

Personal skills and workflow components for AI coding agents.

This repository is a portable, multi-harness workflow layer: skills form the
common core, while agents, hooks, instructions, MCP configuration, and package
profiles can extend that core without being required for every installation.

## Install Skills

Browse the collection and select individual skills:

```bash
npx skills add jonhill90/skills
```

Install a specific skill:

```bash
npx skills add jonhill90/skills --skill primer
```

The repository currently targets Codex, Claude Code, and GitHub Copilot. Other
Agent Skills-compatible harnesses may work through the same installer.

## Repository Model

```text
skills/          Portable Agent Skills source
agents/          Reusable agent definitions
docs/            Platform-agnostic reference material
.agents/         Codex and cross-harness compatibility projection
.claude/         Claude-specific configuration and development hooks
.codex/          Codex-specific configuration and policy
.github/         GitHub Copilot instructions and repository automation
tools/           Standalone tools used by selected skills
```

`skills/` is canonical. Harness directories contain configuration or symlinks
back to canonical source; they are not independent copies.

## Core Workflow Skills

| Skill | Purpose |
|---|---|
| `primer` | Orient in an unfamiliar codebase |
| `using-tmux` | Operate persistent interactive terminal sessions safely |
| `closing-the-loop` | Produce implementation plans tied to verification |
| `create-skill` | Design portable skills with progressive disclosure |
| `validate-skill` | Validate skills against this repository's portable contract |

Additional skills integrate with GitHub, Azure DevOps, Linear, Microsoft Learn,
Context7, Obsidian, and YouTube transcripts. Install them selectively to avoid
overlapping triggers and unnecessary context.

General software-development methodology skills such as TDD, Git worktrees,
and parallel-agent dispatch are provided by
[Superpowers](https://github.com/obra/superpowers) and are intentionally not
duplicated here.

## Authoring Contract

Each skill lives at `skills/<name>/SKILL.md`:

```text
skills/example-skill/
├── SKILL.md
├── scripts/       Optional deterministic helpers
├── references/    Optional detail loaded on demand
└── assets/        Optional output resources
```

Portable skills use `name` and `description` frontmatter. The directory name
must match `name`. Keep the core instructions concise and move detail into
directly linked references.

Validate the repository:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
```

## Distribution Direction

Two installation layers are intentional:

- `npx skills` installs independent public skills.
- APM packages will reproduce opinionated workflow profiles containing skills
  plus agents, instructions, hooks, and MCP dependencies.

APM packaging will be added after the portable source layout and installer
behavior are stable.

## Content Boundaries

- Generic personal workflow improvements should originate here.
- Project-specific deployment and operational policy remains in its project.
- Employer repository material is research input only and is not copied,
  migrated, or adapted into this repository.

See [docs/migration-audit.md](docs/migration-audit.md) for the source and
selection decision behind each migrated skill.

See [AGENTS.md](AGENTS.md) for contribution rules.
