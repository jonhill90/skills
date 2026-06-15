---
name: dispatching-parallel-agents
description: Dispatch parallel subagents for independent tasks without shared state. Use when facing 2+ independent failures, debugging unrelated subsystems, or researching separate topics concurrently.
---

# dispatching-parallel-agents

Dispatch parallel subagents when you have multiple independent tasks that don't share state. This skill provides the decision framework and prompt structure for effective parallelization.

## When to Use

Parallel dispatch is appropriate when:

- **Independent domains** — Tasks touch different files, services, or subsystems with no overlap
- **No shared state** — No task depends on the output of another
- **Clear boundaries** — Each task has a well-defined scope and expected output
- **Time savings** — Running sequentially would be noticeably slower

## When NOT to Use

Stay sequential when:

- Tasks depend on each other's output (chain, don't parallelize)
- Tasks modify the same files (merge conflicts are likely)
- The problem is not yet understood (investigate first, parallelize second)
- A single task is fast enough that parallelization adds overhead without benefit

## The Pattern

### Step 1: Identify Independent Tasks

Break the work into units that have no dependencies on each other. Each unit should be completable without knowledge of the others' results.

Questions to validate independence:
- Can task A complete without task B's output? (If no, they're dependent)
- Do tasks A and B modify the same files? (If yes, they'll conflict)
- Does the order matter? (If yes, they're sequential)

### Step 2: Create Task Descriptions

Write a focused, self-contained prompt for each agent. Every prompt must include:

1. **Context** — What the agent needs to know about the codebase
2. **Scope** — Exactly what files/areas to work in
3. **Objective** — What to accomplish, stated precisely
4. **Constraints** — What NOT to touch or change
5. **Expected output** — What to report back

### Step 3: Dispatch Agents

Use the harness's subagent or task tool to dispatch agents in one parallel
operation. If the harness has no subagent capability, keep the work sequential.

```
Task 1: "Fix SMTP timeout in services/email/..."
Task 2: "Fix auth token refresh in services/auth/..."
Task 3: "Update deploy script error handling in scripts/..."
```

Choose the right agent type for each task:

**Platform built-ins** (available in Claude Code regardless of repo config):
- `Bash` — Command execution, git operations
- `general-purpose` — Multi-step tasks requiring multiple tools
- `Explore` — Codebase investigation and search

**Repository agents** may be available in `agents/`. Read their metadata before
selecting one and do not assume every harness supports the same agent schema.

### Step 4: Review Results

After all agents return:

1. **Read each summary** — Verify the agent accomplished its objective
2. **Check for conflicts** — Ensure no agent modified files outside its scope
3. **Run the full test suite** — Confirm no regressions from combined changes
4. **Integrate** — If agents worked in worktrees, merge branches

## Agent Prompt Structure

A well-structured agent prompt follows this template:

```
You are working on [project context].

## Task
[Precise objective — what to accomplish]

## Scope
- Files to modify: [specific paths]
- Files to read for context: [specific paths]

## Constraints
- Do NOT modify [specific files/areas]
- Do NOT [specific anti-patterns]

## Expected Output
Return:
- [What was changed and why]
- [Any issues encountered]
- [Test results if applicable]
```

### Example: Debugging Multiple BATS Test Files

```
Task 1 (general-purpose):
"Fix the failing tests in tests/scripts/deploy.bats.
Read scripts/deploy.sh for context. The tests expect
deploy.sh to validate the service name argument before
proceeding. Only modify scripts/deploy.sh — do not
change the test file. Run the tests after fixing and
report results."

Task 2 (general-purpose):
"Fix the failing tests in tests/scripts/secrets.bats.
Read scripts/secrets.sh for context. The tests expect
secrets.sh to check for sops binary before attempting
decryption. Only modify scripts/secrets.sh — do not
change the test file. Run the tests after fixing and
report results."
```

### Example: Researching Independent Topics

```
Task 1 (Explore):
"Search the codebase for all Traefik configuration.
Find how TLS certificates are managed, what middleware
is configured, and document the routing rules. Return
a summary of the Traefik setup."

Task 2 (Explore):
"Search the codebase for all Keycloak configuration.
Find realm settings, client configurations, and theme
customizations. Return a summary of the auth setup."
```

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Prompt too broad ("fix all the tests") | Agent flounders without focus | Scope to specific files and behaviors |
| Missing context ("fix the bug") | Agent lacks information to start | Include file paths and background |
| No constraints ("make it work") | Agent may modify shared files | Specify what NOT to change |
| Vague output expectation | Can't verify success | Define what the summary must include |
| Parallelizing dependent tasks | Later agents need earlier results | Identify dependencies first, chain those |
| Too many agents at once | Diminishing returns, review burden | 2-4 agents is the sweet spot |

## Verification After Agents Return

After all agents complete, always:

1. **Review each agent's summary** — Did it accomplish the stated objective?
2. **Check for scope violations** — Did any agent modify files outside its designated area?
3. **Look for conflicts** — Did agents make contradictory changes?
4. **Run the full test suite** — Combined changes may interact even if individual tasks were independent
5. **Commit atomically or separately** — If changes are truly independent, separate commits improve history; if they're part of one feature, a single commit is cleaner

## Integration

- **using-git-worktrees skill**: When agents need filesystem isolation, create a worktree per agent before dispatching.
- **using-tmux skill**: For agents running in separate terminal sessions, combine worktrees with tmux session-per-agent orchestration.
- **Agent patterns**: Prefer read-only specialists for research and isolated
  worktrees for agents that edit files.
