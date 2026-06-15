---
name: validate-skill
description: Validate an Agent Skill's structure, portable frontmatter, links, and bundled scripts. Use when creating, editing, reviewing, or troubleshooting a SKILL.md directory.
---

# Validate a Skill

Use deterministic validation before qualitative review.

## Workflow

1. Identify the skill directory from the user's request.
2. Run the repository validator against that directory.
3. Fix structural errors before reviewing instruction quality.
4. Run or test bundled scripts when behavior changed.
5. Report errors, warnings, and executed verification.

```bash
python3 scripts/validate_repository.py skills/<name>
```

## Structural Contract

Verify:

- the directory contains `SKILL.md`;
- YAML frontmatter parses successfully;
- `name` and `description` are present;
- `name` matches the directory;
- the body is non-empty and under 500 lines;
- relative Markdown links resolve;
- scripts are executable where appropriate;
- no skill-level README exists;
- the repository has no duplicate skill names.

Portable skills should use only `name` and `description` frontmatter unless a
documented compatibility requirement justifies a standard optional field.

## Qualitative Review

After structural validation, check that:

- the description distinguishes triggering from nearby non-triggering requests;
- instructions are actionable and imperative;
- general knowledge is not repeated unnecessarily;
- detailed or variant-specific material uses progressive disclosure;
- scripts replace fragile repeated command generation where appropriate;
- references are linked with clear guidance for when to read them.

## Report

Return:

- status: valid, warnings, or invalid;
- structural findings with paths;
- qualitative findings;
- commands run and their outcomes.
