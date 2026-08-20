---
name: test-in-the-consumer-context
description: Run a check where the thing that depends on it runs — same user, shell, environment, working directory, and privileges — before believing its verdict, and place a check only where it can actually observe its subject. Use before reporting that a command, credential, path, or tool works or fails for something other than your own session, and before siting a check in CI, a hook, or a scheduled job. Not for proving a check can fail at all (verify-the-instrument) and not for checking a claimed capability limit against primary sources (research-the-limit) — this is specifically about the check running somewhere its consumer is not.
---

# Test in the Consumer's Context

The same command can be correct in one place and wrong in another, and both
answers look equally authoritative. A verdict about someone else's
environment, taken from yours, is a guess wearing the clothes of a
measurement.

This is not a subtle failure. It reverses the sign of the answer, and it
does so most confidently exactly where the environments differ most: an
interactive shell versus a daemon, a laptop versus a CI runner, your user
versus a service account.

## Before you report a verdict

> **Ask: who consumes this answer, and did I measure where they live?**

If the consumer is a scheduled job, run it from a scheduled job. If it is a
tmux pane, run it in a tmux pane. If it is CI, run it in CI. Reproduce the
consumer's context, do not approximate it — the differences that matter are
the ones you would not have thought to replicate.

The dimensions that have actually flipped answers:

- **Interactive versus non-interactive.** Login shells source profiles;
  daemons do not. A `PATH`, a shell function, an alias, an env var can all
  exist in one and not the other.
- **Keychain and credential access.** An interactive session may unlock a
  keyring that a spawned process cannot reach, so a credential store reads
  as present or as *invalid* depending only on who asked.
- **Working directory and repository.** A command run from the wrong tree
  answers about the wrong tree, and will do so silently.
- **User, privileges, and platform.** A check needing elevation returns
  empty rather than refusing, which is indistinguishable from a clean result.

## Before you site a check

Placement is the same question asked earlier. A check installed where it
cannot observe its subject reports clean forever, and nothing about the
green tick reveals why.

> **Name the thing the check must observe, then confirm the chosen location
> can observe it.**

- A CI runner cannot see what is installed on a developer's machine.
- A check reading a config file on disk cannot see what a scheduler actually
  loaded — read the running configuration, not the file.
- A check inside one process cannot speak for a differently-privileged one.

When the location cannot see the subject, the fix is to move the check, not
to weaken the claim.

## When a report contradicts your own measurement

Someone else's environment is evidence about their environment, and yours is
not. If a worker, agent, or colleague reports a failure you cannot
reproduce:

1. **Reproduce in their context before doubting them.** Not in yours again,
   and not in an approximation of theirs.
2. **Treat the contradiction itself as the finding.** Two opposite results
   from the same command is a real, reportable fact — usually the fastest
   route to the cause.
3. **Do not override a reporter on the strength of a measurement taken
   elsewhere.** That is the specific move this skill exists to prevent, and
   it costs the reporter their next hour.

## What this is not

- **`verify-the-instrument`** asks whether a check can fail at all, and
  whether an empty result means "nothing found" or "nothing ran." This
  assumes the check works and asks whether you ran it where it counts.
- **`research-the-limit`** checks a claimed capability against a primary
  source. This checks a claimed *observation* against the consumer's
  environment.
- **`wire-it-when-you-write-it`** owns whether a mechanism is invoked at
  all. This owns whether it is invoked somewhere meaningful.

## Where this came from

Two instances, one night, one estate.

**A credential that was both valid and invalid.** Lane agents reported that
`gh` could not authenticate. Their supervisor ran `gh auth status` in its own
interactive shell, got a clean pass, and told the first lane its blocker was
false. Both verdicts were correct:

```
interactive shell:   ✓ Logged in to github.com account … (keyring)
tmux-spawned:        X The token in default is invalid.    rc=1
```

The token lived only in the macOS keyring. An interactive session reached it;
a tmux-spawned process could not, and fell back to a tokenless entry in
`hosts.yml`. Two lanes had diagnosed it correctly and one was overruled by a
measurement taken from the wrong seat. Every review lane in the estate had
been blocking on it — and within two minutes of the real fix, two pull
requests merged themselves.

**A check sited where it could not see.** The same estate had 15 of 28
authored skills uninstalled for weeks. The proposed fix was a CI job to catch
it. CI runs on a hosted runner; the install directory is on a laptop. **No CI
job could ever have observed the defect.** The check had to run where the
answer lives.
