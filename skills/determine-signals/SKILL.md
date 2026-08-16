---
name: determine-signals
description: Find out what has already been said — in transcripts, issues and PRs, the ledger, the notebook, and vault facts — before asking a question or stating a fact as current, and prefer live system state over any stored record when they disagree. Use before acting on a non-trivial request, right where you would otherwise ask something you could answer by looking, or restate a fact without rechecking it. Not for what the user wants (see determine-intent, which runs on the same "before acting" moment but asks the goal, not the record); not a deliberate periodic transcript sweep for new skill candidates (see mine-transcripts, which is scheduled, not per-task); not for judging whether a check or metric can be trusted once you have its verdict (see verify-the-instrument) — this skill decides which signal source to consult and which one wins when two disagree, not whether a given source's zero result is real.
---

# Determine Signals

A question about to be asked, or a fact about to be stated, has often
already been answered somewhere: a transcript, an issue, a ledger entry,
a notebook page, a vault fact, or the live system itself. The failure
this skill targets is not lacking information — it is acting as though
the information does not exist because nobody checked. A stored signal
and a live signal can also disagree, and picking the stored one by
default because it's already in context is exactly how a settled
decision gets silently reopened.

## Reach for this when

- About to ask the user something answerable by looking at a transcript,
  issue, ledger, or vault entry instead.
- About to state something as current — a decision, a count, a system's
  state — that has not been rechecked since it was last recorded.
- A memory fact, a prior message, or a document disagrees with what the
  live system currently shows, and the pull is to resolve it silently in
  either direction.
- About to report "nothing found" from a source not yet confirmed capable
  of returning something.

Do not reach for this to decide what the user wants right now — both this
skill and `determine-intent` fire at the same "before acting" moment, but
`determine-intent` asks what the goal is; this skill asks what is already
known. Run this one first when a request might already be answered by a
record, then `determine-intent` for what to do with what you found. Do
not reach for this as a scheduled sweep of your own transcripts to find
new skill material — that is `mine-transcripts`, and it is deliberate and
periodic, not per-task. Do not reach for this to decide whether a check
or metric you already have a verdict from can be trusted — that is
`verify-the-instrument`; this skill is what sends you looking for a
signal source in the first place, and it hands off to
`verify-the-instrument`'s method the moment a specific source returns
zero.

## Enumerate sources before concluding anything

Do not stop at the first source that returns an answer. Check what is
available and relevant, in roughly this order of currency:

1. **Live system state** — the running process, the actual file, the
   current git status, the ledger's live tables. This is what "current"
   means; everything else is a record of what someone believed at some
   earlier point.
2. **This conversation's own transcript** — what was already said or
   decided in the current task, before re-deriving it.
3. **Issues and PRs** on the relevant repository — a decision or
   rationale is often already written down as a closed issue or a merged
   PR description.
4. **The ledger or notebook**, if the environment has one — completion
   events, verdicts, prior runs. Check whether it is actually being read
   anywhere downstream, not only written to.
5. **Vault or memory facts** — durable notes from prior sessions. These
   are the most likely to be stale, because nothing forces them to be
   rechecked when the world moves.

Not every source applies to every question. The discipline is checking
which ones do, not running all five every time.

## Prefer live signal over stored signal, and say when they disagree

When a stored fact (memory, a vault note, an old issue) and a live check
(current file contents, current process list, current git state)
disagree, the live one wins — but the disagreement itself is information
the user needs, not something to resolve quietly and move on from. State
both: what was recorded, what was found live, and which one is being
acted on and why.

A stale memory fact reopening a settled build-vs-adopt decision while
sixteen lanes were visibly building the app in plain view is the shape of
this failure: the stored signal was cheaper to read, so it won by
default, not by evidence.

## Hand off to verify-the-instrument at the first zero result

A source returning nothing is not the same as a source with nothing in
it. The moment a specific query, search, or read comes back empty, stop
and apply `verify-the-instrument`'s check before trusting that emptiness:
confirm the query is capable of a nonzero result before believing its
zero. That skill owns the mechanics; this skill owns noticing that a
zero-result source is standing in for "no signal" without having earned
that reading. Two measured shapes this has taken:

- A ledger with 444 completion events and 0 acknowledgements is not
  evidence the events were unimportant — it is evidence nothing
  downstream reads it. "Written but never read" and "never written" are
  different findings; which one is present is a `determine-signals`
  question, and confirming the read path is dead rather than merely quiet
  is `verify-the-instrument`'s.
- `find -newermt` matching 0 of 1159 files, `pgrep -c` returning empty
  against 5 live matching processes, and `log show` returning 0 lines for
  every window checked were each read as "nothing happened," when the
  actual finding was that each query could not report a hit.

## State which signal supports each conclusion

For every conclusion reported, name the source: "per issue #145," "per
the live ledger query," "per this conversation's earlier message," "no
recorded source — inferred." A conclusion with no named source is a
guess wearing a conclusion's clothes, and the reader cannot tell the
difference unless it is said.

## What this skill is not

- **Not `determine-intent`.** That skill works out what the user wants —
  the goal behind the request — before acting. This skill works out what
  is already known or already true before assuming or asking. They share
  a trigger moment and often run back to back: determine what is already
  known, then determine what is wanted given it. `determine-intent`'s own
  description states this ordering; this skill is the earlier half of it
  where a record, not a goal, is in question.
- **Not `mine-transcripts`.** That skill is a deliberate, periodic sweep
  of transcripts to find vocabulary worth turning into a new skill. This
  skill runs per-task, mid-work, and produces an answer to the question
  in front of you, not a candidate list.
- **Not `verify-the-instrument`.** That skill checks whether a test,
  review, or metric already in hand was capable of reporting failure.
  This skill is what sends you looking for a signal source at all, and
  decides which source to trust when several disagree; the instant a
  specific source returns an empty result, apply `verify-the-instrument`'s
  method to that result rather than this skill's.
- **Not `sanity-check` or `keep-me-honest`.** Those operate on reasoning
  and on what gets told to the user, respectively, after the answer is
  already in hand. This skill runs earlier, while what is known is still
  being gathered.
- **Not `devils-advocate`.** That skill builds the strongest case against
  a decision that is about to be made. This skill does not argue a side —
  it establishes what the record and the live system already say, which
  an opposing case then argues from or against.

## Where this came from

Rationale and measured evidence are recorded in issue jonhill90/skills#191
on this repository: a stale memory fact reopening a settled
build-vs-adopt decision (#24, closed decided-build) while sixteen lanes
were visibly building the app in plain view; a ledger with 444 completion
events written and never read (0 notified, 0 acked, `pr_verdicts` empty);
and three instrument-blind zero-result queries (`find -newermt` matching
0 of 1159 files, `pgrep -c` returning empty against 5 live processes,
`log show` returning 0 lines for every window). The underlying
transcripts are private evaluation evidence, not published here.

This skill was named, alongside `determine-intent`, `devils-advocate`,
`keep-me-honest`, and `sanity-check`, in a single design pass on
2026-08-16 that set out explicit "not-this" boundaries for all five
before the three missing ones were built (jonhill90/skills#190,
jonhill90/skills#191, jonhill90/skills#192) — the boundary wording above
was checked against that design and against `determine-intent` and
`devils-advocate` as proposed in their own PRs (#193, #194), including
the `devil-advocate` → `devils-advocate` naming correction #194 made to
its own branch before merge, rather than invented independently.
