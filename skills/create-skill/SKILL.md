---
name: create-skill
description: Design, create, and validate portable Agent Skills with effective triggers, concise instructions, and reusable scripts, references, or assets. Use when adding a new skill, substantially restructuring an existing skill, or validating a skill's structure, frontmatter, links, and bundled scripts.
---

# Create a Skill

Create focused skills that another agent can discover and apply without loading
unrelated context.

## Ask where it belongs first

Before writing anything, settle where the skill will live. Most skills do
not belong in a personal harness repository, and the answer changes what
the skill has to earn.

| Situation | Where | Has to earn its place? |
|---|---|---|
| Every project, every day | personal roster | yes — full evidence bar |
| One repository only | that repo's `.claude/skills/` or `.agents/skills/` | no |
| Occasional domain work | nothing installed — `npx skills use <pkg>@<skill>` | no |

A skill in the personal roster is loaded on every request on every harness,
so it is the only case that needs a failing scenario behind it. A project
skill costs nothing anywhere else — write it, commit it next to the code,
and move on.

If the answer is "one repository" or "someone else already wrote it", stop
here. The rest of this skill is about authoring for the portable case.


## Workflow

1. Gather concrete examples of requests that should trigger the skill.
2. Define the repeated workflow and identify deterministic operations.
3. Create `skills/<name>/SKILL.md`.
4. Add only the resources needed by that workflow.
5. Validate the skill and test its scripts.
6. Exercise it against realistic trigger and non-trigger prompts.

## Structure

```text
skills/<name>/
├── SKILL.md
├── scripts/       Optional deterministic helpers
├── references/    Optional detail loaded on demand
└── assets/        Optional output resources
```

Do not add auxiliary files such as a skill-level README, changelog, or
installation guide.

## Frontmatter

Use portable frontmatter by default:

```yaml
---
name: review-api
description: Review an HTTP API for correctness, compatibility, and security. Use when evaluating route, schema, authentication, or versioning changes.
---
```

Requirements:

- Use lowercase letters, digits, and hyphens.
- Keep the name at 64 characters or fewer.
- Match the directory name exactly.
- Describe both the capability and its trigger conditions.
- Avoid harness-specific fields unless the skill explicitly documents reduced
  portability.

## Body

- Use imperative instructions.
- Assume the agent already knows general software engineering.
- Include procedural or domain knowledge that changes execution.
- Keep the main file under 500 lines.
- Put variant-specific detail in directly linked references.
- Explain when each reference should be read.

## Resource Selection

Use `scripts/` when reliability requires a repeated deterministic operation.
Test every script that is added or changed.

Use `references/` for schemas, detailed procedures, provider-specific guidance,
or material that is only relevant to some requests.

Use `assets/` for templates and files used in produced output rather than loaded
as instructions.

## Validation

Run:

```bash
# inside this repository:
python3 scripts/validate_repository.py skills/<name>
# anywhere else — the portable check:
npx skills add . --list
python3 -m unittest discover -s tests -v
```

Then test at least:

- a request that should activate the skill;
- a nearby request that should not activate it;
- one realistic task using any bundled script or reference.
