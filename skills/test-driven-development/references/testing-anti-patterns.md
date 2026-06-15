# Testing Anti-Patterns

Common testing mistakes that undermine test value. Each anti-pattern includes what it looks like, why it's harmful, and how to fix it.

## 1. Testing Implementation Instead of Behavior

### What It Looks Like

Tests that verify internal mechanics rather than observable outcomes:

```typescript
// Anti-pattern: testing how, not what
test("login calls hashPassword then queries database", async () => {
  const hashSpy = jest.spyOn(crypto, "hashPassword");
  const dbSpy = jest.spyOn(db, "query");

  await login("user", "pass");

  expect(hashSpy).toHaveBeenCalledWith("pass");
  expect(dbSpy).toHaveBeenCalledWith("SELECT * FROM users WHERE ...");
});
```

### Why It's Harmful

- **Brittle** — Refactoring internals breaks the test, even when behavior is unchanged
- **False confidence** — The test passes even if login doesn't actually authenticate anyone
- **Maintenance burden** — Every internal change requires test updates

### The Fix

Test the behavior the user cares about:

```typescript
// Correct: testing behavior
test("login succeeds with valid credentials", async () => {
  await createUser("user", "pass");

  const result = await login("user", "pass");

  expect(result.authenticated).toBe(true);
  expect(result.token).toBeDefined();
});

test("login fails with wrong password", async () => {
  await createUser("user", "pass");

  const result = await login("user", "wrong");

  expect(result.authenticated).toBe(false);
});
```

**Question to ask:** "If I completely rewrote the implementation but kept the same behavior, would this test still pass?"

## 2. Excessive Mocking

### What It Looks Like

Tests where most of the code is mock setup, and the actual assertion is trivial:

```typescript
// Anti-pattern: more mocking than testing
test("processOrder works", async () => {
  const mockDb = { save: jest.fn().mockResolvedValue({ id: 1 }) };
  const mockEmail = { send: jest.fn().mockResolvedValue(true) };
  const mockPayment = { charge: jest.fn().mockResolvedValue({ ok: true }) };
  const mockInventory = { reserve: jest.fn().mockResolvedValue(true) };
  const mockLogger = { info: jest.fn(), error: jest.fn() };

  const order = new Order(mockDb, mockEmail, mockPayment, mockInventory, mockLogger);
  await order.process({ item: "widget", qty: 1 });

  expect(mockPayment.charge).toHaveBeenCalled();
  expect(mockDb.save).toHaveBeenCalled();
  expect(mockEmail.send).toHaveBeenCalled();
});
```

### Why It's Harmful

- **Tests the mocks, not the code** — You're verifying that mocks were called, not that orders are processed correctly
- **Hides design problems** — If a function needs 5 mocks, it has too many responsibilities
- **Fragile** — Changing any dependency signature breaks the test

### The Fix

Use real dependencies where possible. Mock only at system boundaries (network, filesystem, external APIs). If you need many mocks, refactor the code:

```typescript
// Correct: fewer, more meaningful mocks
test("processOrder charges payment and confirms", async () => {
  const paymentGateway = new FakePaymentGateway(); // in-memory fake
  const orderService = new OrderService(paymentGateway);

  const result = await orderService.process({
    item: "widget",
    qty: 1,
    price: 9.99,
  });

  expect(result.status).toBe("confirmed");
  expect(paymentGateway.charges).toHaveLength(1);
  expect(paymentGateway.charges[0].amount).toBe(9.99);
});
```

**Question to ask:** "Am I testing my code or testing that `jest.fn()` works?"

## 3. Test-Only Production Code Paths

### What It Looks Like

Adding code to production that only exists to make testing easier:

```typescript
// Anti-pattern: test-only code in production
class SessionManager {
  private sessions: Map<string, Session> = new Map();

  // Added only for testing — never called in production
  _resetForTesting() {
    this.sessions.clear();
  }

  // Test-only flag
  _skipValidation = false;

  createSession(user: User) {
    if (!this._skipValidation) {
      this.validateUser(user);
    }
    // ...
  }
}
```

### Why It's Harmful

- **Security risk** — Test backdoors can be exploited in production
- **Coupling** — Production code depends on test infrastructure
- **Confusion** — Future developers don't know if `_resetForTesting` is safe to remove

### The Fix

Design for testability through proper dependency injection, not through test backdoors:

```typescript
// Correct: dependency injection
class SessionManager {
  constructor(
    private store: SessionStore,
    private validator: UserValidator
  ) {}

  createSession(user: User) {
    this.validator.validate(user);
    return this.store.create(user);
  }
}

// In tests: inject test doubles
const manager = new SessionManager(
  new InMemorySessionStore(),
  new AlwaysValidValidator()
);
```

**Question to ask:** "Would I be comfortable if this code ran in production exactly as written?"

## 4. Asserting on Mock Behavior

### What It Looks Like

Tests that only verify mocks were called without checking real outcomes:

```typescript
// Anti-pattern: testing the mock, not the outcome
test("saveUser persists the user", async () => {
  const mockRepo = { save: jest.fn() };
  const service = new UserService(mockRepo);

  await service.createUser({ name: "Alice" });

  expect(mockRepo.save).toHaveBeenCalledWith(
    expect.objectContaining({ name: "Alice" })
  );
});
```

### Why It's Harmful

This test verifies that `save` was called, not that the user was actually persisted. The implementation could call `save` and then immediately delete the record — the test would still pass.

### The Fix

Verify the observable outcome, not the mechanism:

```typescript
// Correct: verify the outcome
test("saveUser persists the user", async () => {
  const repo = new InMemoryUserRepository();
  const service = new UserService(repo);

  await service.createUser({ name: "Alice" });

  const users = await repo.findAll();
  expect(users).toHaveLength(1);
  expect(users[0].name).toBe("Alice");
});
```

**Question to ask:** "Does this test prove the feature works, or just that some functions were called?"

## 5. Snapshot Addiction

### What It Looks Like

Using snapshots as the primary assertion strategy:

```typescript
// Anti-pattern: snapshot everything
test("renders user profile", () => {
  const component = render(<UserProfile user={testUser} />);
  expect(component).toMatchSnapshot();
});

test("API response format", async () => {
  const response = await getUser(1);
  expect(response).toMatchSnapshot();
});
```

### Why It's Harmful

- **Meaningless diffs** — Reviewers blindly approve snapshot updates without understanding what changed
- **False positives** — Any change (even intentional) breaks the snapshot
- **No intent** — The test doesn't communicate what matters about the output
- **Lazy validation** — Developers use snapshots to avoid thinking about what to assert

### The Fix

Assert on specific, meaningful properties:

```typescript
// Correct: targeted assertions
test("renders user profile with name and role", () => {
  const { getByText, getByRole } = render(
    <UserProfile user={testUser} />
  );

  expect(getByText("Alice")).toBeInTheDocument();
  expect(getByRole("heading")).toHaveTextContent("Admin");
});

test("API response includes user fields", async () => {
  const response = await getUser(1);

  expect(response.name).toBe("Alice");
  expect(response.email).toMatch(/@/);
  expect(response.createdAt).toBeInstanceOf(Date);
});
```

Snapshots are acceptable for:
- Detecting unintentional changes to serialization formats
- Large generated output where specific assertions are impractical
- As a supplement to behavioral assertions, not a replacement

**Question to ask:** "If this snapshot changed, would a reviewer know whether to accept or reject the update?"

## Iron Laws

These are non-negotiable principles for test quality:

1. **Never test mock behavior.** If your assertion is `expect(mock).toHaveBeenCalled()`, you're testing the mock library, not your code. Test outcomes instead.

2. **Never add test-only methods to production code.** If you need `_resetForTesting()` or `_skipValidation`, the design needs to change. Use dependency injection.

3. **Never mock what you don't understand.** If you're mocking a dependency, you must understand its contract. A mock that doesn't match the real behavior produces tests that pass but code that fails in production.

## Summary

| Anti-Pattern | Detection Signal | Fix |
|-------------|-----------------|-----|
| Testing implementation | Test breaks on refactor | Assert on behavior/outcomes |
| Excessive mocking | More mock setup than assertions | Use fakes, reduce dependencies |
| Test-only production code | Methods named `_forTesting` | Dependency injection |
| Asserting on mocks | `expect(mock).toHaveBeenCalled()` | Verify the actual outcome |
| Snapshot addiction | `toMatchSnapshot()` everywhere | Targeted, meaningful assertions |
