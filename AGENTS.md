# AGENTS.md

## Project

`skills` is Jon Hill's public collection of portable [Agent
Skills](https://agentskills.io/specification) — model- and
provider-agnostic instructions an AI coding agent can load on demand.
Each skill is self-contained: a `SKILL.md` plus optional `scripts/`,
`references/`, and `assets/`. Nothing here depends on any particular
harness, personal dotfiles, or private evaluation tooling.

This file is the shared repository policy. `CLAUDE.md` and
`.github/copilot-instructions.md` are committed **symlinks** to it, so
each harness reads its own filename and there is one source. Edit this
file; the other two follow with no sync step.

## Scope

- This repository holds only portable skill content plus the minimal
  validation, tests, and CI needed to keep that content correct.
- Personal harness configuration (instructions, hooks, agents, settings,
  MCP declarations, install/sync tooling) lives in Jon's separate
  `agent-dotfiles` repository, which consumes this collection rather than
  vendoring it.
- Behavioral evaluation methodology, scenarios, transcripts, and results
  live in a private companion repository. None of that is published here.
- Employer-owned or project-specific material is never copied into this
  repository.

## Canonical Layout

```text
skills/
  <skill-name>/
    SKILL.md
    scripts/
    references/
    assets/
scripts/
  validate_repository.py   # structural + link + naming checks
tests/
  test_validate_repository.py
.github/workflows/         # CI: validate + unit tests
```

## Skill Authoring

- Use `skills/<name>/SKILL.md`.
- Match the directory name and frontmatter `name`.
- Use lowercase letters, digits, and hyphens; maximum 64 characters.
- Include what the skill does and when it should trigger in `description`.
- Keep portable frontmatter to `name` and `description` by default;
  `license`, `compatibility`, `metadata`, and `allowed-tools` are also
  accepted.
- Use imperative instructions.
- Keep `SKILL.md` under 500 lines.
- Move detailed material to `references/` and link it directly from `SKILL.md`.
- Put deterministic, repeated operations in tested, executable scripts
  under `scripts/`.
- Do not add a README inside a skill directory.
- Avoid harness-specific preprocessing syntax.
- Classify each skill as *model-invoked* (a reusable discipline the agent
  should reach on its own) or *user-invoked* (a workflow reached
  deliberately). Express the classification in `description` trigger
  wording, not in frontmatter fields.

## Workflow

1. Orient in the repository and inspect current changes.
2. Define observable success criteria.
3. For behavioral code (scripts), use red-green-refactor.
4. Make the smallest coherent change.
5. Run repository validation and relevant script tests.
6. Review the diff for generated files, broken links, and source duplication.

## Work Tracking

GitHub Issues on this repository (`gh issue list`) is the tracking
surface for open work here. Close an issue with `Fixes #N` in the PR
body. Branch with a type prefix (`docs/`, `feat/`, `chore/`); CI gates on
`pull_request`.

## Required Verification

Run before considering repository changes complete:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Run language-specific tests when changing bundled scripts.

## Recording Figures

A number written into this repository's docs is either **measured** — a
command was run and its output read — or **inferred** from a setting, a
prediction, or arithmetic. State which. Do not quote a count for a set
you have not enumerated.

## Distribution

- `npx skills add jonhill90/skills --list` browses the collection.
- `npx skills add jonhill90/skills --skill <name>` installs one skill
  into the current project.
- Do not hand-maintain a growing matrix of harness-specific copies of
  this repository; harness projection is that consumer's job, not this
  repository's.

## Guardrails

Do:

- use current primary documentation for changing formats and tools;
- preserve progressive disclosure;
- document compatibility assumptions.

Do not:

- copy employer-owned or project-specific content into this repository;
- add duplicate skill identities;
- encode one harness as the portable source model;
- claim validation without running the commands above;
- publish private evaluation evidence or link to private repositories
  from this tree — plain provenance statements (what happened, when) are
  fine; clickable links to private material are not.
