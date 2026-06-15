---
name: primer
description: Orient in an unfamiliar codebase by inspecting repository instructions, structure, documentation, manifests, key files, Git state, and recent work. Use when starting work, switching repositories, or needing a concise architecture overview.
---

# Codebase Primer

Build enough context to work safely without reading the repository exhaustively.

## Phase 1: Inspect Current State

Read repository instructions in scope, then inspect:

```bash
git status --short --branch
git log --oneline -20
git remote -v
rg --files
```

Use a shallow tree when available and exclude generated dependency, cache, and
build directories. If the request names a subdirectory, focus there while noting
its relationship to the broader repository.

## Phase 2: Read Documentation

Read in this order, stopping when sufficient context is available:

1. Agent instructions such as `AGENTS.md`, `CLAUDE.md`, and scoped equivalents.
2. `README.md`, contribution guides, and architecture documentation.
3. Dependency and build manifests such as `package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, and `Makefile`.

Read instruction files fully. Scan manifests for commands and important
dependencies rather than reading lockfiles or generated output.

## Phase 3: Identify Architecture

Identify:

- project type and primary languages;
- major directories and ownership boundaries;
- entry points and important data flows;
- build, test, lint, and CI systems;
- schemas, shared types, and configuration;
- the smallest set of core implementation files needed to explain the system.

Prefer targeted reads. Note large files without loading them completely unless
the active task requires it.

## Phase 4: Assess Active Work

If the working tree is dirty, inspect `git diff --stat` and the relevant diffs
without reverting them. Use recent commits to identify the current development
focus. Surface uncertainty and repository risks instead of guessing.

## Output

```markdown
## Primer Report: <project>

### Overview
- Type, purpose, languages, and frameworks

### Architecture
- Major directories, boundaries, entry points, and data flows

### Development
- Runtime, dependencies, build, test, lint, and CI commands
- Repository rules that affect the requested work

### Key Files
| File | Purpose |
|---|---|

### Current State
- Branch and working tree
- Recent development focus
- Risks, unknowns, and likely next investigation
```

Keep the report concise and evidence-based. Do not infer unsupported commands or
architecture.
