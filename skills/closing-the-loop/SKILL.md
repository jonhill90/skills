---
name: closing-the-loop
description: Closed-loop planning discipline for non-trivial changes. Use when creating implementation plans, reviewing plan completeness, or preparing PRs that require structured planning evidence.
---

# Closed-Loop Planning

Formalize implementation plans so every non-trivial change has a clear contract between planning and verification. The 9 required sections close the loop between "what we plan" and "what we enforce."

## When to Use

- Before implementing any non-trivial change (3+ files, new features, policy work)
- When creating or reviewing implementation plans in plan mode
- When preparing PR bodies that need structured planning evidence
- Skip for trivial changes (< 3 files, docs-only, single-line fixes)

## Required Plan Sections

Every non-trivial plan must include all 9 sections. Order is flexible; names accept alternatives.

### 1. Goal / Signal

What does success look like? What observable signal confirms this work landed correctly?

```markdown
## Goal / Signal

After this lands:
- Observable signal: <what changes in the system>
- User-facing impact: <what users see differently>
```

**Alternatives:** `Objective`

### 2. Scope

What is in scope and what is explicitly out of scope for this change?

```markdown
## Scope

**In scope:**
- Item A
- Item B

**Out of scope:**
- Item C (future PR)
```

### 3. TDD Matrix

Map each requirement to its test. This is the contract between what we build and how we verify it.

```markdown
## TDD Matrix

| Requirement | Test | Type |
|---|---|---|
| Feature X works | `test_feature_x` | unit |
| API returns 200 | `test_api_returns_200` | integration |
```

**Alternatives:** `Test Matrix`

### 4. Implementation Steps

Ordered steps with enough detail that another agent could execute them. Group by TDD phase (Red/Green/Refactor) when applicable.

```markdown
## Implementation Steps

### Phase 1: Red
1. Write failing test for X

### Phase 2: Green
2. Implement X to pass test

### Phase 3: Refactor
3. Clean up implementation
```

**Alternatives:** `Approach`

### 5. Verification Matrix

Concrete commands and expected results. Every claim in the plan maps to a verification step.

```markdown
## Verification Matrix

| Check | Command | Expected Result |
|---|---|---|
| Tests pass | `pytest tests/ -v` | All green |
| Lint clean | `shellcheck scripts/*.sh` | No errors |
```

**Alternatives:** `Verification Checklist`

> **Manual workaround rule:** Treat undocumented manual workarounds as blockers
> by default. Identify the root cause and durable fix, then state one disposition:
> `patch first`; `split follow-up` only when the current change is independently
> safe, does not weaken security, and survives redeploy; or `merge now` only when
> the workaround was unnecessary or the durable fix is already included.

### 6. CI / Drift Gates

What CI checks enforce this change? What drift could occur and how is it caught?

```markdown
## CI / Drift Gates

- **New gate:** `check_foo.py` runs on PRs
- **Existing gates preserved:** bats, compose, shellcheck
- **Drift risk:** If X changes, Y catches it
```

**Alternatives:** `CI Gates`, `Drift Gates`

### 7. Risks & Mitigations

What could go wrong and how do we prevent or handle it?

```markdown
## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| X breaks Y | Low | High | Guard with Z |
```

### 8. Definition of Done

Checkbox list of all conditions that must be true before this work is complete.

```markdown
## Definition of Done

- [ ] All tests pass
- [ ] CI green
- [ ] Docs updated
- [ ] Line count constraints met
```

**Alternatives:** `Done Criteria`

### 9. Stop Conditions / Out-of-Scope

When should work stop? What explicit boundaries prevent scope creep?

```markdown
## Stop Conditions

**Stop if:**
- X exceeds threshold Y
- Approach Z proves unviable

**Out of scope:**
- Future enhancement A
- Unrelated refactor B
```

**Alternatives:** `Out of Scope`, `Out-of-Scope`

## Plan Checklist

Copy into your plan and check off as you complete each section:

```markdown
- [ ] Goal / Signal
- [ ] Scope
- [ ] TDD Matrix
- [ ] Implementation Steps
- [ ] Verification Matrix
- [ ] CI / Drift Gates
- [ ] Risks & Mitigations
- [ ] Definition of Done
- [ ] Stop Conditions
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Vague goal ("improve things") | No observable signal to verify | State concrete before/after |
| TDD matrix without test names | Can't verify tests were written | Name every test function |
| Steps without phase grouping | Unclear when to test vs. implement | Group by Red/Green/Refactor |
| Missing stop conditions | Scope creep goes unchecked | Define explicit boundaries |
| Verification without commands | "It works" isn't evidence | Include exact commands + expected output |
| Risks without mitigations | Identified but unaddressed | Every risk needs a mitigation |
| DoD without checkboxes | Can't track completion | Use `- [ ]` for each condition |
| Scope without "out of scope" | Boundaries are implicit | Explicitly list what you won't do |
| CI section says "existing" only | Doesn't explain new enforcement | Document new gates + drift risks |
| Verification via ad-hoc manual workaround | Root cause unknown, fix isn't durable, breaks on redeploy | Identify root cause, determine least-privilege fix, state merge recommendation: `patch first` (default), `split follow-up` (only if safe to ship independently, no security regression, no redeploy breakage), or `merge now` (only if no real workaround needed or durable fix already in PR) |

## Integration

Use `primer` before planning unfamiliar work. Use
`test-driven-development` when implementation changes behavior. Execute the
commands from the verification matrix before reporting completion.
