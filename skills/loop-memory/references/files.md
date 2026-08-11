# File Templates and Prune Rules

Pick file names and a home directory that fit the repo; nothing here
prescribes a fixed layout. Where a durable ledger already exists for the
loop (see the main skill body's "Compose with a durable ledger" section),
put this content there instead of a new flat file.

## Progress / plan

Re-injected every iteration — the loop's driving prompt reads this file
and acts on it, rather than carrying the plan in context.

```markdown
# Progress — <loop name>

## Goal
<one sentence>

## Queue
- [ ] item A
- [x] item B — done, see receipt <run-id>

## Watermark
Last processed: <timestamp or item id>

## Current status
<one paragraph, updated every iteration>
```

**Prune rule:** collapse completed items to a one-line reference to their
receipt once the run that did them is more than a few iterations old.
Keep the queue short enough that an iteration can read it whole.

## Decisions

Written on any non-obvious choice — one that later work will need the
reason for, not every choice made.

```markdown
## <date> — <short title>
Decided: <what>
Why: <the reasoning, and what was ruled out>
```

**Prune rule:** never prune a decision entry; prune only by moving entries
older than the active work into an archive file, so the active file stays
short.

## Known failures

One entry per distinct failure mode, not per occurrence.

```markdown
## <short id> — <symptom>
Input: <what triggered it>
Wrong behavior: <what happened>
Check: <the test or guard that now catches it>
Seen: <count or last-seen date>
```

**Prune rule:** merge duplicate entries by incrementing "seen" rather than
appending a new entry; remove an entry only once its check has been
promoted into the repo's actual test suite, where it belongs permanently.

## Run receipts

One per run, written by the wrapper or harness driving the loop — not by
the agent's own final turn, so a receipt exists even for a crashed or
budget-capped run.

```markdown
## <run id> — <timestamp>
Terminal state: <succeeded | failed | crashed | budget-capped>
Did: <a few lines>
Chose: <notable choices and why, if any>
Evidence: <test output, diff, PR URL>
Cost: <tokens, dollars, iterations>
Artifacts: <files, PRs, issues produced>
```

**Prune rule:** keep receipts append-only; roll receipts older than the
loop's audit window into a compressed summary rather than deleting them —
the audit trail is one of the three jobs a receipt does.

## Handoff note

Written before compaction, a model switch, or a long pause — and edited in
place as state changes, not re-typed from scratch each time.

```markdown
# Handoff — <loop name>, <date>

## Goal
<one sentence>

## Done
<with evidence: commits, passing tests>

## In progress
<precisely where it stopped>

## Known issues and dead ends already ruled out
<the highest-value section — what stops the next reader re-walking them>

## Next action
<one concrete next step>
```

**Prune rule:** a handoff note has exactly one live copy. When a successor
resumes from it and moves state forward, edit the same file rather than
appending a new dated section — an edited-in-place file is what keeps a
stale read impossible to mistake for current.
