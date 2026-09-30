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
- There is no behavioral eval system in this repository for now. A vetted,
  community-maintained replacement is tracked in jonhill90/skills#309. Past
  evaluation evidence is private and is not published here.
- Employer-owned or project-specific material is never copied into this
  repository.

## What "shipped" means

Merging a skill here publishes it (`npx skills add`, or as an Agent
Plugin); it does not install it anywhere. Whether a harness loads it by
default is decided later, in `agent-dotfiles`. `scripts/check_orphan_skills.py`
is an advisory view of that question and never gates CI. Details, including
the plugin manifest and what Claude Code does and does not read:
[docs/reference/distribution.md](docs/reference/distribution.md).

## Canonical Layout

```text
plugin.json                # Agent Plugins 1.0.0 manifest (closed schema)
skills/<skill-name>/       # SKILL.md plus scripts/, references/, assets/ when needed
scripts/                   # repository tooling: validation, docs lint, eval status, merge gate
tests/                     # unit tests for scripts/ and for every bundled skill script
docs/                      # indexed by docs/README.md
  reference/               # maintained explanations that stay true
  decisions/               # numbered decision records; superseded, never deleted
.github/workflows/         # CI: validate, docs lint, skills-table check, unit tests
```

Placement follows `skills/organize-repository`. Investigations and proposals
belong in issues and pull requests, not in `docs/`; this repository carries
no project-level PRD/SPEC material (see "Scope").

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
- Frontmatter fields are flat `key: value` lines — never nested mappings or
  flow collections. Write a colon in a `description` freely (e.g. "runs
  long: repetition, not duration"); the validator quotes such values before
  either parser sees them, so plain YAML's "unquoted `: ` is a mapping
  separator" rule never applies to skill descriptions
  (jonhill90/skills#142).

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

## Merging PRs

Merge only with `python3 scripts/merge_pr.py --repo jonhill90/skills --number <N>`,
never `gh pr merge`. It merges only when CI is green and a different lane
has posted a `Verdict: APPROVE` comment for the PR's current head. The PR
body must carry `Author-Lane: <name>`. Comment format, exit codes, and why
the gate is not a CI job: [docs/reference/merge-gate.md](docs/reference/merge-gate.md).

## Required Verification

Run before considering repository changes complete:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Run language-specific tests when changing bundled scripts.

## Spec Conformance

CI independently validates every skill with the specification's reference
validator (`skills-ref`) and `plugin.json` against the published Agent
Plugins schema. `scripts/validate_repository.py` is deliberately stricter
than the reference. The differences and the reasons:
[docs/reference/validation.md](docs/reference/validation.md).

## Recording Figures

A number written into this repository's docs is either **measured** — a
command was run and its output read — or **inferred** from a setting, a
prediction, or arithmetic. State which. Do not quote a count for a set
you have not enumerated.

## Distribution

- Do not add harness-specific copies of this repository or an `mcp.json`;
  see [docs/reference/distribution.md](docs/reference/distribution.md).

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
  fine; clickable links to private material are not. This repository is
  public deliberately; a relative Markdown link or `https://` link into a
  private repository (the former evaluation repository
  `jonhill90/agent-evals`, or any repository named
  by convention with a `-private` suffix) is simply broken for every
  public reader. Name the private source in plain text instead — a repo
  name and issue number a reader cannot click through to is provenance,
  not a leak. `scripts/validate_repository.py`'s `validate_no_private_links`
  check (jonhill90/skills#201) enforces this in CI so the convention does
  not depend on anyone remembering it.
