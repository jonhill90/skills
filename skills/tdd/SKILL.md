---
name: tdd
description: Write a failing test for new behavior before implementing it, then implement only enough to pass, then refactor — red, green, refactor for code that has never worked yet. Use when building a new feature, function, endpoint, or component from scratch and no prior bug is being reproduced. Not for fixing a bug, defect, regression, or wrong output in existing code — that is failing-test-first, which owns the bugfix case specifically; defer to it whenever a prior working state exists to reproduce a break against.
---

# TDD

Test-driven development for **greenfield** code: behavior that has never
existed and has no prior failing state to reproduce. The discipline is red,
green, refactor — write a test that fails because the behavior does not
exist yet, write the smallest implementation that makes it pass, then
clean up with the test still green. This is the broader discipline that
`failing-test-first` is one instance of; that skill owns the narrower,
already-rostered case of reproducing an existing bug with a test before
fixing it. Where the two could both apply — extending existing code with a
new capability that isn't a bugfix — this skill governs; where a defect in
already-working code is being reproduced, `failing-test-first` governs, not
this one.

## Reach for this when

- Building a new function, endpoint, component, or feature that does not
  exist in the codebase yet.
- Extending existing code with new behavior that has never run before (a
  new branch of logic, a new parameter's effect, a new command).
- The user asks to "test-drive" or "TDD" a piece of new work.

Do not reach for it when:

- A bug, defect, regression, or wrong output is being fixed in code that
  used to work — that is `failing-test-first`; write the reproduction
  first, but follow that skill's contract, not this one.
- The change is a pure refactor with no behavior change — there is nothing
  new to write a failing test against; the existing suite is the check.

## Red

Write the test for the behavior you are about to build, against the
interface you intend it to have, before writing that implementation. Run
it and confirm it fails for the reason you expect — a missing function, an
unimplemented branch, an assertion on behavior that does not exist — not
for an unrelated reason (a typo, an import error, a fixture that doesn't
build). A red test that fails for the wrong reason proves nothing about
the behavior you're adding.

## Green

Write the smallest implementation that makes the test pass. Resist adding
behavior the test doesn't ask for — extra parameters, extra branches,
speculative generality — even if you can predict a future need for them.
Run the test and confirm it now passes, and run the surrounding suite to
confirm nothing else broke.

## Refactor

With the test green, clean up: remove duplication, rename for clarity,
extract what deserves extracting. Run the suite after each change. If a
refactor requires a behavior change to work, that is new red-green work,
not refactoring — stop and go back to red.

## Keep the test

The test stays in the suite after the feature ships. It is now a
regression check for behavior that, before this skill ran, did not exist
to regress.
