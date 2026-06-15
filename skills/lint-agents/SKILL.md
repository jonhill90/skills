---
name: lint-agents
description: Validate agent definition files for correct YAML frontmatter syntax. Use when creating, editing, or reviewing agent .md files to catch common errors before they cause runtime failures.
---

Validate all canonical agent definition files in `agents/`.

## Steps

1. Find all agent files:
   ```
   Glob: agents/**/*.md
   Glob: .claude/agents/**/*.md
   ```

2. For each agent file, read it and validate the YAML frontmatter against these rules:

### Required Fields
- `name` — must be present, lowercase with hyphens only
- `description` — must be present, non-empty string

### Array Fields (MUST be YAML arrays, NOT comma-separated strings)
- `tools` — if present, must be a YAML array (each item on its own `- item` line)
- `disallowedTools` — if present, must be a YAML array
- `skills` — if present, must be a YAML array

Common **wrong** pattern to detect:
```yaml
tools: Read, Grep, Glob        # WRONG - comma-separated string
disallowedTools: Write, Edit    # WRONG - comma-separated string
```

Correct pattern:
```yaml
tools:                          # CORRECT - YAML array
  - Read
  - Grep
  - Glob
```

### Valid Values
- `model` — if present, must be one of: `sonnet`, `opus`, `haiku`, `inherit`
- `permissionMode` — if present, must be one of: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`

### Body
- Must have content after the closing `---` (the system prompt)

## Output

Report results per file:
- **Pass**: file is valid
- **Fail**: list each error with line number and description

Only apply automatic fixes when the user explicitly requests them. Convert
comma-separated tool fields to the YAML structure required by the target
harness.

## Also Check Documentation

Scan reference and documentation files for incorrect agent examples:

```
Grep pattern: ^tools: \w.*, \w
Grep pattern: ^disallowedTools: \w.*, \w
```

Report any doc files that contain wrong comma-separated syntax in code examples (exclude lines explicitly labeled as "Wrong" examples).
