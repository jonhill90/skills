# AGENTS.md

## Project

`skills` is a personal, multi-harness workflow layer for AI coding agents.
Portable Agent Skills are the primary product. Agents, instructions, hooks, MCP
configuration, and future package profiles are optional layers.

This file is the shared repository policy. `CLAUDE.md` and
`.github/copilot-instructions.md` point here for harness compatibility.

## Product Boundaries

- Keep `skills/` portable and independently installable.
- Keep canonical content out of harness-owned directories.
- Treat `.agents/`, `.claude/`, `.codex/`, and `.github/` as adapters,
  configuration, or repository automation.
- Do not make installation of one skill inherit the complete personal workflow.
- Keep project-specific and employer-specific material out of this repository.

## Canonical Layout

```text
skills/
  <skill-name>/
    SKILL.md
    scripts/
    references/
    assets/
agents/
docs/
scripts/
tests/
```

Compatibility projections:

- `.agents/skills -> ../skills`
- `.claude/skills -> ../skills`
- `.codex/skills -> ../skills`
- `.claude/agents -> ../agents`
- `.codex/agents -> ../agents`
- `.github/agents -> ../agents`

## Skill Authoring

- Use `skills/<name>/SKILL.md`.
- Match the directory name and frontmatter `name`.
- Use lowercase letters, digits, and hyphens; maximum 64 characters.
- Include what the skill does and when it should trigger in `description`.
- Keep portable frontmatter to `name` and `description` by default.
- Use imperative instructions.
- Keep `SKILL.md` under 500 lines.
- Move detailed material to `references/` and link it directly from `SKILL.md`.
- Put deterministic, repeated operations in tested scripts.
- Do not add a README inside a skill directory.
- Avoid harness-specific preprocessing syntax in portable skills.

Harness-specific extensions require an explicit compatibility note and must not
replace the portable workflow.

## Agent Authoring

- Store reusable agent definitions in `agents/<name>.md`.
- Use kebab-case filenames.
- Keep harness-specific projections or schemas in adapter directories.
- Validate tool lists as YAML arrays where the target format requires arrays.

## Workflow

1. Orient in the repository and inspect current changes.
2. Define observable success criteria.
3. For behavioral code, use red-green-refactor.
4. Make the smallest coherent change.
5. Run repository validation and relevant script tests.
6. Review the diff for generated files, broken links, and source duplication.

## Required Verification

Run before considering repository changes complete:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Run language-specific tests when changing bundled scripts or tools.

## Distribution

- Use `npx skills` for individual skill discovery and installation.
- Use APM for future reproducible workflow packages.
- Do not hand-maintain a growing matrix of harness skill copies.
- Generated package or harness output must identify its canonical source.

## Guardrails

Do:

- use current primary documentation for changing formats and tools;
- install skills selectively;
- preserve progressive disclosure;
- keep generic improvements upstream here;
- document compatibility assumptions.

Do not:

- copy employer-owned content into this repository;
- add duplicate skill identities;
- encode one harness as the portable source model;
- load every skill into every workflow by default;
- claim validation without running the commands above.
