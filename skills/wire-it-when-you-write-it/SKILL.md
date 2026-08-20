---
name: wire-it-when-you-write-it
description: Ship a mechanism and its caller in the same change, and add the check that fails when a caller disappears — never leave a tested module, script, or gate that nothing invokes. Use when creating any new script, module, hook, workflow, or check, and when reviewing a change that adds one. Not for deciding whether a tool should exist at all (mechanize), whether a tool's verdicts can be trusted (verify-the-instrument), or whether to adopt an existing tool instead of writing one (adopt-or-build) — this is only about the gap between writing a mechanism and something actually calling it.
---

# Wire It When You Write It

A capability nobody triggers is indistinguishable from a capability nobody
built — except that it is more expensive, because it looks finished.

The failure is not carelessness. It is that writing the mechanism is the
interesting part and wiring it is not, so the work stops at the moment it
feels done. Tests passing makes it worse: a green suite over an uncalled
module reads as *shipped*.

## The rule

> **A mechanism and its caller land in the same change, or neither lands.**

"Caller" means something that invokes it without a human choosing to: a
scheduled job, a hook, a CI step, another script's code path. A README line
is not a caller. A slash command a person might remember is not a caller.

If you cannot wire it today, you do not write it today. Write the issue
instead, and say what would have called it.

## Add the check that notices the caller leaving

Wiring it once is not enough — callers get refactored away. Ship the
assertion alongside:

- **Module with no non-test importer** → a test that fails.
- **Script with no invocation outside itself and its own tests** → a test
  that fails.
- **Workflow, hook, or scheduled job** → an assertion that it is registered
  where it claims to run, read from the *running* configuration rather than
  the file on disk. Those differ; a plist can be correct and not loaded.

Then **mutation-check the assertion**: delete the caller, confirm the test
goes red, restore. An anti-orphan check that has never been observed firing
has not been observed to be a check.

## Wired is not the same as able to fail

The subtler version of this defect: the caller exists, the job runs, and
nothing can go wrong.

- A CI job carrying `continue-on-error: true` runs and reports green
  whatever it finds.
- A guard written as `! some_pipeline` does **not** abort under
  `bash -eo pipefail` — bash's `set -e` exempts a negated command — so the
  step falls through to its final `echo` and exits 0.
- A check whose count reads empty and is then compared numerically errors to
  stderr, and an enclosing `if` swallows it.

A toothless caller is worse than no caller, because it produces a green tick
that stops anyone looking. When you find one, say plainly that it was wired
and could not fail — those are different defects with different fixes.

## Where the mechanism can actually observe the thing

Wiring is also placement. A check installed somewhere structurally unable to
see its subject will report clean forever:

- A CI runner cannot see what is installed on a laptop.
- A check that reads a config file cannot see what a scheduler loaded.
- A check that runs in one process environment cannot speak for another.

Before wiring, name what the check must observe and confirm the chosen
location can observe it. See `test-in-the-consumer-context`, which owns this
question in full.

## What this is not

- **`mechanize`** decides whether a tool should exist at all. This runs
  after that decision, and only about invocation.
- **`verify-the-instrument`** asks whether a check's verdict can be trusted
  once it runs. This asks whether it runs.
- **`adopt-or-build`** chooses between someone else's mechanism and your
  own. Either way, this applies to the result.
- **`close-the-loop`** confirms you have what you need before starting. This
  is a condition on what you may finish.

## Where this came from

Measured in one estate, one night, and the estate had already written the
pattern down without acting on it — `worktree.sh:79` says it "has shipped
that exact shape wrong five times already."

| Artifact | Shape |
|---|---|
| `acp_transport.py` | 302 lines, ~15 test classes, requested 23 times over 9 days — **0 lanes ever used it** |
| `poller-leak-cleanup.sh` | 183 lines, 9 tests, **0 callers**; run once by hand |
| `contest-stop.sh` | written to auto-contest a stop-conclusion — PR unmerged, **0-byte log** |
| `bootstrap-session.sh` | the **only** code able to create a session — callers: a README line and an unregistered MCP tool |
| `check_orphan_skills.py` | wired since day one, with `continue-on-error: true` — **runs and cannot fail** |
| 15 of 28 authored skills | never installed; **dark for weeks**, including the ones for expensive decisions |

The last row is the sharpest. Four of the uninstalled skills covered decisions
that were made by hand the same night — adopt-or-build, mechanize,
decide-by-variant, derive-independently-then-compare. The capability existed,
had been carefully written, and could not be reached. Nothing anywhere said so,
because the check that would have said so was the one carrying
`continue-on-error: true`.
