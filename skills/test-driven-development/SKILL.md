---
name: test-driven-development
description: Test-driven development discipline for any feature or bugfix. Use when implementing features, fixing bugs, or changing behavior — requires writing failing tests before implementation code.
---

# test-driven-development

Test-driven development is a discipline, not a suggestion. This skill defines
when and how to apply TDD and provides the constraint that prevents tests from
becoming post-hoc confirmation.

## When to Use

- Implementing any new feature or behavior
- Fixing any bug (the fix must be preceded by a test that reproduces it)
- Changing existing behavior (modify tests first to reflect new expectations)
- Refactoring (existing tests must stay green throughout)

## The Iron Law

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

This is not a guideline. It is a hard constraint. If you find yourself writing implementation code without a failing test, stop immediately and write the test first.

The only exception: trivial configuration changes (adding an env var, updating a version number) that have no behavioral impact.

## Red-Green-Refactor

Every change follows this cycle:

### Red: Write a Failing Test

1. Write a test that describes the desired behavior
2. **Verify RED** — Run the test and confirm it fails
3. Confirm it fails for the right reason (missing implementation, not a syntax error)

If the test passes immediately, either:
- The behavior already exists (you're done)
- The test is wrong (it's not testing what you think)

### Green: Write Minimum Implementation

1. Write the simplest code that makes the failing test pass
2. **Verify GREEN** — Run the test and confirm it passes
3. Run the full suite to check for regressions

Do not optimize. Do not add features. Do not refactor. Just make it green.

### Refactor: Improve Structure

1. Clean up the implementation (extract helpers, rename, simplify)
2. Run tests after every change — they must stay green
3. Do not add new behavior during refactoring

Then return to Red for the next requirement.

## Writing Good Tests

### Structure: Arrange-Act-Assert

```bash
# BATS example
@test "deploy.sh rejects unknown service name" {
  # Arrange
  source scripts/deploy.sh

  # Act
  run deploy "nonexistent-service" "prod"

  # Assert
  [[ "$status" -ne 0 ]]
  [[ "$output" =~ "unknown service" ]]
}
```

```typescript
// TypeScript example
test("retryOperation retries on transient failure then succeeds", async () => {
  // Arrange
  let attempts = 0;
  const operation = async () => {
    attempts++;
    if (attempts < 3) throw new Error("transient");
    return "success";
  };

  // Act
  const result = await retryOperation(operation, { maxRetries: 3 });

  // Assert
  expect(result).toBe("success");
  expect(attempts).toBe(3);
});
```

### Good Test Properties

| Property | Meaning | Example |
|----------|---------|---------|
| **Focused** | Tests one behavior | "rejects empty input", not "handles all edge cases" |
| **Descriptive** | Name explains what and why | `deploy rejects unknown service` |
| **Independent** | No reliance on other tests | Each test sets up its own state |
| **Deterministic** | Same result every run | No reliance on timing, network, or random values |
| **Fast** | Runs in milliseconds | Mock external dependencies |

### Triangulation

One test case is not enough. A hardcoded return value can pass a single test. Add multiple examples to force a real implementation:

```bash
@test "slugify converts spaces to hyphens" {
  run slugify "hello world"
  [[ "$output" == "hello-world" ]]
}

@test "slugify converts multiple spaces to single hyphens" {
  run slugify "hello   world"
  [[ "$output" == "hello-world" ]]
}

@test "slugify lowercases uppercase letters" {
  run slugify "Hello World"
  [[ "$output" == "hello-world" ]]
}
```

## Why Order Matters

Writing tests after implementation has fundamental problems:

1. **Confirmation bias** — You test what you built, not what you should have built
2. **Missing edge cases** — You only test the happy path you already know works
3. **Untestable design** — Code written without tests often has hidden dependencies that make testing painful
4. **False confidence** — Tests that pass on first run may not be testing anything meaningful

Writing tests first:

1. **Clarifies requirements** — You must define "done" before you start
2. **Drives simple design** — Testable code is naturally modular
3. **Catches regressions** — Every behavior has a test from the start
4. **Provides documentation** — Tests show how the code is meant to be used

## Common Rationalizations

These are excuses. Recognize them and resist.

| Rationalization | Why It's Wrong |
|----------------|----------------|
| "I'll write the tests after" | You won't. And if you do, they'll be weaker. |
| "This is too simple to test" | Simple code grows. The test takes 30 seconds to write. |
| "I'm just exploring" | Spike in a branch. When you implement for real, TDD. |
| "The tests would be trivial" | Trivial tests catch regressions. Write them anyway. |
| "I need to see the implementation first" | No. Define the behavior first. Implementation follows. |
| "It's just a refactor" | Refactoring means tests stay green. If they don't exist, write them. |
| "This is infrastructure code" | Infrastructure has behavior. Test it. |
| "I'll slow down the team" | Bugs slow down the team more. TDD prevents bugs. |
| "The framework makes it hard to test" | Isolate the framework. Test your logic separately. |
| "It's a one-line change" | One-line changes cause production incidents. Test it. |
| "I know this works" | You don't. The test proves it. |

## Red Flags

Stop and course-correct if you notice:

- Writing implementation code without a failing test in the current cycle
- A test that passed on the first run (investigate — it may not test what you think)
- Modifying a test to make it pass (tests define behavior; implementation satisfies tests)
- Multiple new behaviors in one Red-Green cycle (one behavior per cycle)
- Skipping the Refactor phase ("it works, ship it" leads to debt)
- Tests coupled to implementation details (mock internals, check private state)

## Example: Bug Fix with TDD

A user reports that `deploy.sh` crashes when given an empty service name.

### Red

```bash
@test "deploy.sh exits with error when service name is empty" {
  run bash scripts/deploy.sh "" "prod"
  [[ "$status" -ne 0 ]]
  [[ "$output" =~ "service name required" ]]
}
```

Run the test. It fails because `deploy.sh` doesn't validate the service name. Good — this is the right failure.

### Green

Add validation at the top of `deploy.sh`:

```bash
if [[ -z "$1" ]]; then
  echo "Error: service name required" >&2
  exit 1
fi
```

Run the test. It passes. Run the full suite. No regressions.

### Refactor

The validation is simple enough — no refactoring needed. Move to the next requirement.

## Verification Checklist

Before considering a TDD cycle complete:

- [ ] Test was written before implementation
- [ ] Test failed before implementation (verified RED)
- [ ] Test passes after implementation (verified GREEN)
- [ ] Full test suite passes (no regressions)
- [ ] Test name describes behavior, not implementation
- [ ] Test is independent (can run in isolation)
- [ ] No test-only code paths in production code

## When Stuck

| Situation | Action |
|-----------|--------|
| Don't know what test to write | Describe the behavior in plain English first. The test is that description in code. |
| Test is hard to write | The design needs to change. Hard-to-test code is poorly structured code. |
| Test keeps failing after implementation | Read the failure message carefully. The test and implementation may disagree on the interface. |
| Too many tests to write | Start with the most important behavior. One test at a time. |
| Existing code has no tests | Write tests for the behavior you're about to change. Don't try to backfill everything. |
| Can't isolate dependencies | Use test doubles (stubs, spies). If you can't inject dependencies, refactor to allow it. |
| Not sure if test is meaningful | Ask: "Would this test catch a real bug?" If no, reconsider. |
| Blocked on understanding behavior | Ask the user to clarify expected behavior before writing tests. |

## Debugging Integration

When a bug is found:

1. **Write a failing test that reproduces the bug** — This is the Red step
2. Fix the bug — This is the Green step
3. Refactor if needed
4. The test now permanently guards against regression

Never fix a bug without first writing a test that demonstrates it. The test is proof the bug existed and evidence it's fixed.

## Optional Agent Separation

When the harness supports subagents, separate Red, Green, and Refactor into
distinct tasks only if their file ownership and handoff are explicit. The Red
agent must not edit implementation files; the Green agent must satisfy the
existing failing test; the Refactor agent must preserve green tests.

## Testing Anti-Patterns

See [references/testing-anti-patterns.md](references/testing-anti-patterns.md) for detailed anti-patterns including:

- Testing implementation instead of behavior
- Excessive mocking
- Test-only production code paths
- Asserting on mock behavior
- Snapshot addiction
