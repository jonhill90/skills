---
name: durable-fact-before-label
description: When a single operation must write both a durable record and a lighter derived label, lock, or claim that points at it, write the durable fact first and update or release the label second — so a crash between the two steps leaves a stale but harmless label, never a record that must be reconciled by hand. Use when writing or reviewing a completion script, finalize step, lock/claim release, rename-on-success, or reconciler that touches two places that must stay consistent. Not for deciding whether to resume an identity after a gap (refuse-invented-identity, its sibling and not its duplicate) or whether a mechanism has a caller at all (wire-it-when-you-write-it).
---

# Durable Fact Before Label

A crash mid-operation is not avoidable by writing careful code; it is
avoidable by choosing which of the two things you're writing gets left
wrong. Every operation that touches a durable record and a cheap pointer
to it — a lock, a claim, a ledger status, a filename — has an order. One
order leaves a **label** wrong when interrupted: stale, but visibly so,
and cheap to recompute or discard. The other leaves a **record** wrong:
silently inconsistent, trusted by the next reader, and expensive to
detect because nothing about it looks broken.

The record is the thing whose correctness other code depends on. The
label is the thing that merely announces the record's state. Get the
order backwards and a crash corrupts the thing everyone trusts while
leaving the announcement of trustworthiness intact.

## The rule

> **Commit the durable fact first. Update or release the derived label
> second.**

Concretely, for any operation that writes both:

1. Write or finalize the durable record — the file, the merged PR, the
   renamed artifact, the row that downstream code reads as ground truth.
2. Only after step 1 is confirmed on disk (or otherwise durably
   observable), update the label that points at it — release the lock,
   clear the claim, flip the ledger status, delete the in-progress
   marker.

If the process dies between 1 and 2, the record is already correct and
the label is merely stale — still marked in-progress, still holding a
claim nobody needs anymore. That is loud: the next reader (a reaper, a
human, a retry) sees "this looks unfinished" and either re-verifies or
re-runs, and re-running against an already-correct record is idempotent
or at worst wasteful, never wrong.

If the order is reversed — release the label first, write the record
second — a crash between them leaves the label saying "available" or
"done" while the record is missing, half-written, or still the old
value. The next reader trusts the label, skips re-verification, and
either loses the work or acts on stale data with full confidence.

This is not "always write files in some fixed order" — it applies
specifically to the pair (durable record, derived pointer to it). If
there is no derived label — just one write — this rule has nothing to
order.

## Reach for this when

- Writing a completion, finalize, or "mark done" step that both produces
  or updates an artifact (a file, a merged PR, a renamed record) and
  releases something else that gates access to it (a lock, a claim, a
  ledger row, a status field).
- Writing a reconciler or sweep that stamps a verdict onto a record based
  on indirect evidence (a timeout, a missing heartbeat) — the stamp is a
  label; do not let it overwrite the durable fact it is trying to
  summarize.
- Reviewing someone else's completion/reconcile code: find the two
  writes, name which one is the record and which is the label, and check
  the record lands first.

## Portable incidents

**Lock released before the record it protects (2026-08-14).** A
completion script released a shared lock/ledger entry before renaming or
finalizing the record that lock was protecting. A crash between those two
steps left the record wrong while the lock already looked free — the
worse ordering, because a wrong-but-available record could be picked up
and trusted by the next reader before anyone noticed it was wrong.
Reordering so the finalize happens before the release turns that same
crash into a lock that looks held (loud, gets investigated) instead of a
record that looks fine (quiet, gets trusted). Filed as jonhill90/skills#178,
candidate 9 of jonhill90/skills#174's mining pass.

**Reconciler's verdict overwrites the record it's summarizing
(2026-08-20).** `reconcile-lane-completions` in agent-supervisor writes
its "did this lane finish?" verdict by *replacing* `results/<task>.md` —
the lane's own report of what it did — with wording like "failed, not
completed" whenever the lane didn't signal completion through the
expected channel. Measured against the live results directory: 133 of 817
result files carry that stamp, 101 of those still have a lane-log, and 31
of those lane-logs name a pull request — one of which was independently
confirmed `MERGED`. The reconciler's label (a status inference from
silence) overwrote the durable record (what the lane actually reported)
instead of being written beside it. The fix agent-supervisor#401 asks for
is exactly this rule: append the reconciliation verdict to a sibling
path, never overwrite the lane's own account, so a crash or a missed
signal leaves a wrong *label next to* a correct record instead of erasing
the record.

**The six-lane symptom this rule exists to prevent (2026-08-20, could not
measure).** Six ledger tasks are said to have sat at `status=accepted` for
6–10 hours with zero live processes and zero tmux windows behind them, four
of the six GitHub issues already `CLOSED`, and `reap-lane-claims` returning
`count:0`. No issue, PR, or commit in `jonhill90/agent-supervisor` matching
this specific incident could be found to check the counts against (unlike
the two incidents above, which cite #178 and agent-supervisor#401
respectively and check out against those records). Had the ledger's status
field been ordered as a label updated *after* a durable "this lane
finished" fact rather than as the thing a crash could leave permanently
wrong, the reaper would have had something loud to catch.

## What this is not

- **Not `refuse-invented-identity`.** That skill governs *reusing* an
  identity or label after a gap — whether to trust a name match when
  resuming. This skill governs *the order two writes happen in* during a
  single operation, before any gap exists. They compose: get the
  ordering here wrong and you can produce exactly the ambiguous,
  can't-confirm-the-match state that skill then has to refuse.
- **Not `verify-the-instrument`.** That skill asks whether a check's
  "clean" result can be trusted once it runs. This skill is about how to
  write the two mutations in the first place so that an interruption
  between them fails in the cheap direction — it applies before there is
  any verdict to distrust.
- **Not `wire-it-when-you-write-it`.** That skill asks whether a
  mechanism has a caller at all. This skill assumes the mechanism runs
  and asks only: of the two things it writes, which goes first.
- **Not general "commit before you signal" advice for distributed
  systems at large.** This is scoped to the specific shape of one
  process, two writes, a durable record and a derived pointer to it —
  not two-phase commit across services, not database transaction
  isolation levels.

## What would invoke this

This is model-invoked, not something a human runs by name. It should
surface — via the harness's own skill matcher on this file's
`description` — whenever a task is: writing a completion or finalize
script, writing or reviewing a lock/claim release, writing a reconciler
or sweep that stamps derived state onto a record, or reviewing a PR that
touches any of those. The concrete trigger phrases in the frontmatter
("completion script", "finalize step", "lock/claim release",
"rename-on-success", "reconciler") are chosen to match how this shape of
code is actually named in this estate, based on the two incidents above.

## Where this came from

Named as candidate 9 in jonhill90/skills#174's mining pass over
2026-08-11..14 estate incidents, filed as jonhill90/skills#178, and
grounded further by the 2026-08-20 evidence in agent-supervisor#401 (133
reconciler-overwritten results, 31 naming a merged PR) and the same day's
six stuck-`accepted` ledger tasks with zero live processes behind them.
