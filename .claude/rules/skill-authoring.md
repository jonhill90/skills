---
paths:
  - "skills/**/*.md"
---

# Skill Authoring Rules

When writing or editing SKILL.md files:

## Structure
- Keep SKILL.md under 500 lines
- Move detailed content to reference files
- Reference supporting files with relative links

## Frontmatter
- `name` and `description` are the only required fields
- Description is the PRIMARY triggering mechanism - be clear and comprehensive
- Include "when to use" context in description, not in body

## Content
- Use imperative/infinitive form ("Run tests" not "Running tests")
- Prefer concise examples over verbose explanations
- Only include what the agent doesn't already know

## Progressive Disclosure
- Core workflow in SKILL.md
- Detailed reference material in separate files
- Agent reads reference files on demand

## Portability
- Keep portable frontmatter to `name` and `description` by default
- Avoid harness-specific preprocessing syntax
- Document reduced compatibility before using harness extensions
