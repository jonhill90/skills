---
name: refuse-invented-identity
description: Refuse and report unrecoverable when a recovery, resume, restore, or failover path cannot positively confirm which prior identity, session, or state it is restoring — never start a fresh instance under the old label and let it pass as continuous. Use when resuming a session, reconnecting to a worker or lane, restoring from a checkpoint, or reclaiming any id, name, or label after a gap, and the record needed to confirm it maps to a specific prior state is missing, ambiguous, or unverifiable.
---

# Refuse Invented Identity

A recovery path's job is to reconnect to a *specific* prior state, not to
produce *something* that answers to the old name. When the record needed
to make that match is missing, a fresh instance started under the old
label looks fully healthy and carries none of the original context — the
worst available outcome, because nothing downstream can tell the
difference until the missing context actually matters. Guessing is worse
than refusing: a wrong identity is not a failed recovery, it is a silent
one, and everything computed from that identity afterward — authorship,
independence, ownership, a merge gate — inherits the error without
knowing it has one.

## Reach for this when

- Resuming a session, conversation, or task by id, name, or label after a
  gap (a restart, a crash, a reconnect, a new process).
- Reclaiming a lane, worker, pane, or job identity where the claim rests
  on a record — a nonce, a session id, a checkpoint hash — that may or
  may not still point at the thing being resumed.
- A restore, failover, or retry path is about to reuse an identity after
  time has passed, and the only evidence it is the *same* identity is
  that the name matches.
- The record that would confirm the match is absent, stale, ambiguous
  (matches more than one candidate), or was never written in the first
  place.

Do not reach for this when the match is positively confirmed by a record
made at the time the identity was created — a session id returned by the
resumed process itself, a nonce stored before the gap and read back
unchanged, a checkpoint whose hash you verified against the source. A
confirmed match is a normal resume, not a guess.

## The rule

1. **Attempt positive confirmation first.** Look for the record made
   *before* the gap that ties the label to a specific prior state — a
   session id, a claim token, a pane nonce, a checkpoint reference. A
   name or label alone is not this record; names get reused, and a
   plausible-sounding match is exactly what makes the guess look safe.
2. **If confirmation succeeds: resume, and say what confirmed it.** State
   the record checked and what it matched, the same way any conclusion
   should name its source. This is the case that needs no further
   caution — proceed normally.
3. **If confirmation fails or the record is missing: refuse.** Do not
   start a fresh instance and let it answer to the old name. Report the
   specific state as unrecoverable (a distinct exit code or status if the
   path is automated, an explicit "cannot confirm identity" if it is
   not) and stop there rather than substituting a guess.
4. **State exactly what could not be confirmed and why**, not a generic
   "resume failed." Name the record that was expected, where it should
   have been, and what was found (or not found) instead — the same
   specificity `keep-me-honest` asks for when naming a conflict.

## What to do instead of guessing — the positive case

Refusing to invent an identity is not the same as refusing to make
progress. Once the prior state is reported unrecoverable, the available
paths forward are:

- **Start genuinely new work, under a genuinely new identity**, and say
  so plainly — a new session id, a new lane name, a new job label. This
  is fine and often the right call; what is not fine is doing this while
  keeping the *old* label, because that is what erases the distinction
  between "this continues prior work" and "this replaces it."
- **Surface the gap for a human or an upstream system to resolve.** Some
  recoveries need a person to say "yes, that is the same thing, here is
  how I know" — reconciliation with independent authority (a ticket
  number, a human's direct confirmation) rather than an automated guess.
  This is deliberate escalation, not a stall.
- **Fix the recording gap going forward**, if the reason confirmation
  failed is that nothing captured the record needed to confirm it later.
  A recovery path that positively fails today because the record was
  never written is more useful than one that silently guesses today and
  keeps guessing until the failure becomes expensive to trace back.

## Portable incident

A restore path was changed to record, at dispatch time, enough to
positively map a recovery target to its real prior state. Before that
change, a missing record would have let restore start a new instance
under the recovered name with no way to tell it apart from a genuine
resume. After the change, a missing record makes restore report
`UNRECOVERABLE` and exit non-zero instead. The failure this guards
against is general: any resume, retry, or failover path that reuses an
identity — a worker id, a session name, a job label — after a gap has the
same failure available to it if it treats a name match as sufficient
confirmation.

## What this is not

- Not `safe-deletion`. That skill gates a destructive action on verifying
  a target's actual contents or state before removing or killing it —
  same "look before you act" posture, but the object is something being
  destroyed, not an identity being resumed. A recovery path that
  confirms identity correctly may still need `safe-deletion`'s gate
  separately if the recovery also involves killing or replacing existing
  state.
- Not `determine-signals`. That skill decides which signal source to
  trust and prefers live state over a stored record when they disagree.
  This skill is narrower: it applies specifically to the moment an
  identity is about to be reused after a gap, and its default on
  insufficient evidence is refuse, not "prefer whichever source is
  live" — a live-looking process is not by itself confirmation it is the
  *same* process the label refers to.
- Not `verify-the-instrument`. That skill checks whether a check or
  metric was capable of reporting a nonzero result before trusting its
  "none." This skill is about trusting an identity match, not a
  measurement.

## Where this came from

Named as candidate 6 in jonhill90/skills#174's mining pass over
2026-08-11..14 estate incidents, and built out as jonhill90/skills#179
after the mining issue judged it distinct enough from `safe-deletion` to
stand on its own — different verb (resuming an identity, not destroying a
target), different object (a process or session identity, not a file or
directory).
