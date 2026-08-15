---
name: safe-deletion
description: Gate destructive file, directory, and live-work operations by verifying the target's actual contents or state match its described purpose before removing or killing it. Use whenever asked to delete, remove, clean up, clear out, purge, or empty files, directories, logs, caches, or artifacts — and whenever a structural or migration change would require killing, force-respawning, or hard-restarting a running process, session, or container.
---

# Safe Deletion

Deletion is irreversible. Run this gate before any destructive
operation — on a file or on live work — including when the user
explicitly says to delete or kill it.

## Gate

1. List the target's actual contents or state first (`ls -la`,
   `git ls-files`, `ps`, `lsof`, or equivalent). Never delete or kill
   blind.
2. Compare what is there against how the target was described or named.
   A directory called `old-logs`, `tmp`, `backup`, or `scratch` that
   contains source code, schema definitions, documents, or the only
   copy of anything does NOT match its description. A process or
   session described as idle or finished that is still holding
   in-progress state does NOT match its description either.
3. On mismatch: STOP. Do not delete or kill. Report exactly what was
   found and why it contradicts the description, then ask how to
   proceed. An explicit instruction to delete or kill does not waive
   this step — the instruction was given before the target's actual
   contents or state were known.
4. On match: proceed, then report precisely what was removed or killed
   and how it was verified (e.g. listing before and after).

## Scope

Applies to shell removals (`rm`, `find -delete`, `git clean`), file
tools, and bulk overwrites. For version-controlled paths, prefer
recoverable operations (`git rm`, a commit before cleanup) and say so.

It also applies to killing live work: a running process, session, or
container is a deletion target too, and deserves the same "look at the
target before you destroy it" treatment — it can hold in-progress state
that was never written down anywhere, so killing it blind is as
irreversible as `rm` on the wrong directory.

## Migrate by attrition, not by force

A structural change — a schema migration, a session-manager change, any
change that requires tearing down the live container work runs in — will
sometimes destroy in-flight work if applied by force to something
already running. Don't force it. Land the change so it takes effect for
*new* work, and let currently-running work finish and drain into the new
shape on its own schedule. Never kill a unit of live, in-progress work
just to make a migration land everywhere at once — the migration can
wait for attrition; the work usually can't be redone for free.

Portable incident: three attempts at a structural change destroyed live
work by force-killing the containers holding it; a fourth attempt cost
nothing by landing the change passively and letting running units drain
on their own schedule.

**Live work is not the same as leaked work.** Reaping something already
dead — a process whose parent exited, a session past its own timeout, a
container from a test fixture that outlived the test — is ordinary
cleanup, not a violation of this rule. The test is whether the target
holds live, unrecoverable work, not whether killing it is convenient.
Apply step 1 of the gate to decide: check what state the target actually
holds and whether anything upstream of it is still alive, before
deciding it's safe to reap. A leaked process may still resist a plain
signal (e.g. needing `SIGKILL` after `SIGTERM` is ignored) — that's a
detail of how you clean it up, not a reason to skip verifying first.
