---
name: spec-driven-development
description: Write a falsifiable acceptance criterion and its mutation check before writing any code, and require the behaviour to be demonstrated — not merely the code to exist — before closing the work. Use when scoping non-trivial work before it starts, when deciding whether a request duplicates something already shipped, or when deciding whether an issue can be closed. Not for planning the steps of already-scoped work (close-the-loop), not for writing the test that implements a chosen criterion (tdd, failing-test-first), and not for confirming an existing check can fail (verify-the-instrument) — this is what happens before any of those three has something to work from.
---

# Spec-Driven Development

Every expensive failure traces to the same root: work started before its
acceptance criterion existed. Not "before the code was tested" — before the
criterion that would judge the code was ever written down. Once work is
underway, the criterion that gets written matches whatever was built, which
proves nothing. Write it first, in a form that can say no, and hold the
finished work to it rather than the other way around.

## Reach for this when

- Scoping non-trivial work before any code is written — a new feature, a
  restore or recovery path, anything whose failure mode matters.
- Deciding whether a request duplicates something already shipped. A
  criterion written before starting is also a search: if it already holds
  against the current system, the work is done, not begun.
- Deciding whether an issue, ticket, or PR can be closed. Closing is a claim
  that a specific criterion now holds, not a claim that a diff merged.
- Reviewing a claim that something works, phrased in prose — a PR body, a
  changelog line, a status update — rather than in a command and its output.

Do not reach for it when a criterion already exists and the only question is
how to build to it (`spec`), how to sequence and verify an already-scoped
change (`close-the-loop`), how to turn a chosen criterion into a running
test (`tdd`, `failing-test-first`), or whether an existing check can be
trusted (`verify-the-instrument`). Those four own real, adjacent ground; see
[What this is not](#what-this-is-not) for where each boundary sits.

## Write the acceptance criterion first, and make it falsifiable

Before touching code, state: what command, what output, and — this is the
part that gets skipped — **what result would prove this wrong**. A criterion
with no reachable "no" is not a criterion; it is a description of what you
already intend to see.

"The restore path works" is not falsifiable — nothing you could observe
would make you say it doesn't. "Killing the running process and restarting
from the restore path reaches the same state within N seconds, verified by
comparing a checksum of the recovered data against the pre-kill checksum"
is: it names the command, the output, and the exact observation that would
falsify it. A restore path is routinely judged only against its happy path —
started, stopped cleanly, restarted — because that is the path anyone
naturally exercises first, and the failure it exists for is the one nobody
induced.

The same shape applies past infrastructure. A component's behaviour gets
reported from the document that introduced it — a PR body's description of
what it does — rather than from actually running it once. A description
written at commit time is a claim, not a criterion, and it outlives the one
moment anyone might have checked it against the real thing. The falsifiable
version names what running it would show, not what it was designed to do.

**A criterion written first is also how a duplicate gets caught.** State
what would prove the request already satisfied — the command, the expected
output — and check that against the current system before writing any new
code. A request can ask for something that shipped hours earlier under a
different name; nothing catches that unless the criterion is checked against
reality before work starts, not after.

## The mutation check belongs in the spec, not the review

Write the check that proves the guard can fail *while writing the spec*,
before the implementation exists to check. Not as a step added during
review once code is up for judgement — by then the check tends to get
written to agree with whatever was built, and a check written to match the
code cannot catch that code being wrong.

State it as part of the criterion: "break X, run the check, confirm it goes
red; restore X, confirm it goes green." A test suite has repeatedly been
shipped that still passes with the guard it claims to enforce removed —
that is precisely what deciding the mutation in advance, as part of the
acceptance criterion rather than an afterthought, is meant to stop. Designing
the break *before* the code exists means there's no implementation yet to
unconsciously write the check around.

`verify-the-instrument` owns actually running this proof once a check
exists — plant the violation, confirm red, revert, confirm green. This
section is upstream of that: decide what the break is and write it into the
spec while the criterion is being written, so there is nothing to retrofit
later.

## Separate "the code exists" from "the behaviour holds"

These are two different claims and only the second one closes anything.
"The restore path is implemented" and "the restore path recovers from a
real failure" are not the same sentence, and treating them as the same has
closed issues while what they promised did not actually work. A PR merging
is evidence for the first claim. It is not evidence for the second.

Write both claims down separately when reporting status, and close only on
the second:

- **Code exists**: the diff is merged, the function is callable, the path is
  reachable.
- **Behaviour holds**: the falsifiable criterion from the section above was
  run against the real thing, and it passed.

A status update that only states the first is not lying, but it reads as
the second unless it says otherwise. Say which one you have.

## Three outcomes, never two

When the criterion is checked, there are three possible answers, not two:

1. **Holds** — the criterion was run and passed.
2. **Does not hold** — the criterion was run and failed.
3. **Could not measure** — the criterion could not be run at all: the
   instrument to observe it doesn't exist yet, the environment couldn't be
   reached, the failure couldn't be safely induced.

Blindness must never be recorded as success. An instrument that cannot see
the thing looks exactly like the thing being absent, and both report
silence — the difference only shows up if "could not measure" is a distinct
answer you were watching for, not a case "holds" quietly absorbs. Decide,
while writing the criterion, what "could not measure" would look like for
*this specific* check — a missing fixture, an environment you can't safely
break, a dependency not yet built — so it's recognisable in the moment
rather than reasoned about after the fact under pressure to report
something.

## What good looks like

The failure mode above is not hypothetical, but neither is the fix. A
multi-phase piece of work once had its acceptance criteria — three of
them, each a command and an expected output — written before any of the
phase's code existed. Running them against the finished work caught a real
defect: an identifier that was supposed to resolve never did. A code review
of the same diff, reading the logic rather than running the criterion,
would have passed it — the code looked correct; it just didn't produce the
id it claimed to. The criteria did not describe what the code was supposed
to do in the abstract; they ran the actual command and checked the actual
output, and that is what caught what reading the diff could not.

That is the whole method working: written first, falsifiable, run against
the real thing rather than reasoned about.

## What this is not

- **`spec`** owns the technical *how* of an already-agreed problem —
  architecture, interfaces, trade-offs, the document engineers build
  against. This skill does not replace a technical spec and is not one; it
  is the narrower discipline that any spec-shaped artifact, from a full
  design document down to a two-line acceptance criterion in an issue
  comment, has to satisfy before code starts and before the work can close.
  A `spec` document's "Verification" section is exactly where this skill's
  criterion and mutation check belong — this fills that section in, rather
  than adding a second document next to it.
- **`close-the-loop`** is the general pre-flight checklist for an
  already-scoped change — nine sections covering scope, sequencing, CI
  gates, risk, done criteria. This skill is narrower and comes earlier: it
  owns the shape the acceptance criterion itself must have (falsifiable,
  with its mutation check decided) and the rule that closing requires the
  behaviour demonstrated, not the code merged. `close-the-loop`'s "TDD
  Matrix" and "Verification Matrix" sections are where this skill's output
  lands; use both, in that order, not one instead of the other.
- **`tdd`** and **`failing-test-first`** own writing and running the actual
  test, red before green, once a criterion already exists — the code-level
  mechanics of proving one specific criterion. This skill owns whether that
  criterion exists yet, what it must contain, and applies even where no
  unit test will ever be written — a duplicate-work check, a status update,
  a claim about what a shipped feature does.
- **`verify-the-instrument`** owns confirming, right before a verdict is
  trusted, that the check which produced it was actually capable of
  failing — a check on work already done. This skill owns designing that
  same falsification into the spec at the start, before the check or the
  code exists, so there's nothing to retrofit; and it extends the same
  three-outcome idea from a check's exit code to how a whole issue gets
  closed.

## Where this came from

Motivated by recurring failures on one estate — described portably, without
estate-specific paths or issue numbers, at the request of the issue that
asked for this skill: `jonhill90/skills#172`.
