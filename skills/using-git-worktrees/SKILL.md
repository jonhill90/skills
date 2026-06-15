---
name: using-git-worktrees
description: Create isolated git worktrees for feature work with safety verification. Use when starting feature branches that need isolation, running parallel agents in separate workspaces, or before executing implementation plans.
---

# using-git-worktrees

Create isolated worktrees for feature work so each branch gets its own working directory without cloning the entire repository.

## When to Use

- Starting a feature branch that needs filesystem isolation from the main worktree
- Running parallel agents that each need their own working directory
- Working on multiple branches simultaneously without stashing
- Before executing an implementation plan that modifies many files

## Directory Selection

Check for a worktree directory in this order:

1. `.worktrees/` — project-local, preferred
2. `worktrees/` — alternative project-local
3. Ask the user — if neither directory exists

```bash
if [[ -d ".worktrees" ]]; then
  WORKTREE_DIR=".worktrees"
elif [[ -d "worktrees" ]]; then
  WORKTREE_DIR="worktrees"
else
  # Ask the user where to create worktrees
  echo "No worktree directory found. Where should worktrees be created?"
  echo "  1. .worktrees/ (recommended — hidden, project-local)"
  echo "  2. worktrees/"
  echo "  3. Custom path"
fi
```

## Safety Verification

Before creating a project-local worktree directory, verify it is gitignored. An unignored worktree directory will pollute `git status` with thousands of untracked files.

```bash
# Check if the directory is gitignored
if ! git check-ignore -q "$WORKTREE_DIR" 2>/dev/null; then
  echo "WARNING: $WORKTREE_DIR is not in .gitignore"
  echo "Add it to .gitignore and commit before proceeding."

  # Add to .gitignore and stage (let user commit when ready)
  echo "$WORKTREE_DIR/" >> .gitignore
  git add .gitignore
  echo "Staged .gitignore — commit when ready before creating the worktree."
fi
```

Never skip this check. Creating a worktree in an unignored directory is a common mistake that is tedious to clean up.

## Creation Steps

### 1. Choose a Branch Name

Use the repository's branch naming conventions. If none are documented, prefer:

| Type | Prefix | Example |
|------|--------|---------|
| Feature | `feat/` | `feat/add-auth-flow` |
| Bug fix | `fix/` | `fix/smtp-timeout` |
| Refactor | `refactor/` | `refactor/deploy-script` |
| Docs | `docs/` | `docs/api-reference` |
| Enhancement | `enhance/` | `enhance/logging` |

### 2. Create the Worktree

```bash
BRANCH="feat/my-feature"
git worktree add "$WORKTREE_DIR/$BRANCH" -b "$BRANCH"
```

To create from an existing branch:

```bash
git worktree add "$WORKTREE_DIR/$BRANCH" "$BRANCH"
```

### 3. Set Up the Worktree

After creation, the worktree needs project dependencies. Detect and run the appropriate setup:

```bash
cd "$WORKTREE_DIR/$BRANCH"

# Node.js
[[ -f package-lock.json ]] && npm ci
[[ -f pnpm-lock.yaml ]] && pnpm install --frozen-lockfile
[[ -f yarn.lock ]] && yarn install --frozen-lockfile

# Python
[[ -f requirements.txt ]] && pip install -r requirements.txt
[[ -f pyproject.toml ]] && pip install -e .

# Rust
[[ -f Cargo.toml ]] && cargo build

# Go
[[ -f go.mod ]] && go mod download

# BATS
compgen -G 'tests/scripts/*.bats' >/dev/null 2>&1 && echo "BATS tests available"
```

### 4. Verify

```bash
# Confirm the worktree exists
git worktree list

# Confirm the branch is correct
cd "$WORKTREE_DIR/$BRANCH"
git branch --show-current
```

## Quick Reference

```bash
# List all worktrees
git worktree list

# Remove a worktree (after merging)
git worktree remove "$WORKTREE_DIR/$BRANCH"

# Prune stale worktree references
git worktree prune

# Lock a worktree (prevent accidental removal)
git worktree lock "$WORKTREE_DIR/$BRANCH"
```

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Worktree dir not in `.gitignore` | Thousands of untracked files in `git status` | Always run `git check-ignore` first |
| Same branch in multiple worktrees | Git refuses — a branch can only be checked out in one worktree | Use `git worktree list` to check |
| Deleting worktree directory manually | Stale reference in `.git/worktrees/` | Always use `git worktree remove` |
| Forgetting dependency install | Build/test failures in the worktree | Run setup detection after creation |
| Creating worktree from dirty state | Uncommitted changes don't transfer | Commit or stash before creating |

## Integration

- **using-tmux skill**: Use the `using-tmux` skill for session-per-worktree orchestration. This skill handles worktree creation; tmux handles running agents in separate terminal sessions within those worktrees.
- **Branch naming**: Follow AGENTS.md conventions (`feat/`, `fix/`, `refactor/`, `docs/`, `enhance/`).
- **Parallel agents**: Combine with the `dispatching-parallel-agents` skill when multiple agents need isolated workspaces.
