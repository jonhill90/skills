---
name: verify-the-instrument
description: Check the measuring device before trusting what it reports — prove a check can actually fail before believing it passed, and prove a fix is load-bearing before believing it worked. Use right before acting on a test result, review, metric, or another agent's claimed finding. Not for writing the check or running it the first time — that is ordinary testing, not this.
---

# Verify the Instrument

A green result is a claim about the checker, not just the subject. Before
you act on a test that passed, a review that found nothing, a metric that
looks fine, or another agent's "done" — confirm the thing that produced that
verdict was actually capable of reporting the other outcome. An instrument
that cannot fail is not evidence; it is decoration that happens to look like
evidence.

This is a discipline for the moment a verdict is about to be trusted, not a
replacement for testing. Writing the test, running the check, debugging why
something failed — none of that is this skill. This is the pause right
before the verdict changes what you do next.

## Reach for this when

- You are about to act on a green test, a clean review, a passing gate, or
  a metric — and the check itself has never been observed to fail.
- Another agent, a subprocess, or a prior turn reports a result and you are
  about to build on it without having watched the mechanism work.
- A check that used to catch something has gone quiet, and quiet is being
  read as "fixed" rather than checked.

Do not reach for it when you are writing the check for the first time, or
when you are debugging a failure you can already see — that is normal
development, not an instrument in question. And do not reach for it as a
substitute for `sanity-check`: that skill is for reasoning with no test to
run; this one is for a verdict a command already produced.

## Five checks, in order

### 1. Prove the check can fail

A check that has only ever been observed to pass has not been observed at
all. Plant the violation it claims to catch, run it, and confirm it fails
with a message that names the actual problem — not a crash, not silence.
Remove the violation, run it again, confirm it passes. Only both
observations together establish the check is wired to reality.

```
1. Introduce the exact defect the check is supposed to catch.
2. Run the check. Expect: FAIL, with a message pointing at the defect.
3. Revert the defect.
4. Run the check again. Expect: PASS.
```

If step 2 doesn't fail, or fails with an unrelated error, stop — you do not
have a check yet, you have a script that runs.

**Three specific shapes this takes**, each one a check that still prints a
verdict while no longer able to report the failure:

- **A pipeline reports the last stage's exit code, not the command you meant
  to check.** `cmd | tail` exits with `tail`'s status — a failing `cmd` piped
  into a successful `tail` reads as success. Capture the exit code of the
  command you actually care about (`${PIPESTATUS[0]}` in bash, or split the
  pipe and check each stage) rather than trusting `$?` after a pipeline.
- **A file or directory's existence stands in for the work it names having
  happened.** A check that confirms a test directory exists, or that a
  report file was written, has confirmed a side effect — not that the tests
  ran, or that the report's content is right. Track the thing itself (tests
  executed, assertions run, a count) rather than a proxy for it.
- **A mutation's success is assumed instead of confirmed.** After a script
  claims to have edited, moved, or written something, re-read the target
  before trusting a later step that depends on it. A write that silently
  failed — wrong path, a permissions error, a caught exception — reports
  success identically to one that didn't, until something reads back what
  is actually on disk.

### 2. Prove the fix is load-bearing

"Red before green" is not only for writing your own code — it applies to
reviewing anyone else's fix, including a subagent's. Revert the fix and
confirm the specific test that's supposed to cover it now fails. Reapply
and confirm it passes again. A fix that passes with or without itself
applied was not tested by that check; something else made the run green.

```
1. Revert the change under review (git stash, checkout HEAD~1, or by hand).
2. Run the specific test the change claims to satisfy. Expect: FAIL.
3. Reapply the change.
4. Run the same test again. Expect: PASS.
```

Skipping step 2 is the single most common way a broken fix ships: the
after-state was checked, the before-state never was, so nothing establishes
the fix caused the pass.

### 3. Distinguish "nothing to check" from "the check could not run"

Zero findings and zero coverage look identical on the page and mean
opposite things. Before reading an empty result as clean, confirm the
check actually iterated something:

- Did it report *how many* items it examined, not just how many it flagged?
- If it targets a file, glob, or config, does that path currently resolve —
  or would a silently-empty match, a caught exception, or a moved file
  produce the same empty output?
- Would the check still report "0 findings" if its input file were deleted,
  renamed, or made empty? If yes, "0 findings" and "the check didn't run"
  are the same string, and you cannot currently tell them apart.

Where possible, make the check assert a nonzero baseline — "examined N
files" or "N assertions ran" — so an empty run is loud instead of quiet.

**Give the check a third exit code.** A check with only pass and fail has
no way to say *I could not see*, so blindness has to borrow one of the two
— and it always borrows "pass", because that is what an empty result
looks like. Reserve a distinct code for it:

```
0  clean          — the check ran and found nothing
1  violation      — the check ran and found something
3  could-not-measure — the check could not see; do not read this as clean
```

Two shapes make this concrete, both observed rather than imagined. A gate
compared a count that came back empty — `[ "$n" -gt 0 ]` with an unset `n`
prints `integer expected` to stderr, and an enclosing `if` swallows the
error, so the gate printed GREEN over a database it could not open. And a
staleness check computed a negative age, because a UTC timestamp was parsed
as local time; a negative age is not a small error, it is a branch that can
never be taken.

The caller then has somewhere honest to put the third case. A missing input
file, an unresolvable ref, an unreadable database, a zero-length manifest:
each is a 3. Refusing to answer is a real answer, and it is the one this
whole skill exists to make sayable.

### 4. Distinguish a changed source from a changed output

A diff of what's deployed, rendered, or generated is not a diff of what
changed the source. Before reporting drift, or the absence of it, confirm
which side you actually diffed:

- Comments, whitespace, and dead branches the projection strips can move in
  source without moving in output — and vice versa, a template or build
  step can leave stale output after source changed.
- If comparing "what shipped" to "what's in the repo," diff the same
  artifact class on both sides: rendered-to-rendered or source-to-source,
  never rendered-to-source.
- Regenerate or rebuild before diffing anything downstream of a build step.
  A stale build directory compared against fresh source will report drift
  that isn't there, or hide drift that is.

### 5. Two checks that agree are not corroboration unless they can fail independently

Running a second check and getting the same answer feels like confirmation.
It is only confirmation if the two could have disagreed. Two patterns with
overlapping blind spots return the same empty result for the same reason,
and the agreement is an artifact of the shared blindness rather than
evidence about the thing.

Before treating agreement as corroboration, ask what each check would have
to see to *disagree*. If you cannot name a case that one catches and the
other misses, you ran one check twice.

The same failure has a mirror image: an over-count from an unscoped input.
A pattern that sweeps more than the thing you meant to measure — a build
tree, a vendored copy, a directory of checkouts — inflates instead of
hiding, and looks just as authoritative.

Two shapes, both observed:

- Counting how many times something happened in a log, with two patterns
  that each missed for a different reason — one assumed a trailing colon
  the format did not have, the other assumed lowercase where the text was
  uppercase. Both returned `0`. The agreement made `0` look solid; the
  true count was 181. Neither pattern was checked against a line known to
  exist.
- Counting references to a name across a repository with a recursive
  search over the working tree, which also swept 113 sibling worktrees
  each carrying their own copy: 19,857 instead of 2,959. Scoping the same
  query to tracked files gave the real number.

The defence for both is the same and is cheap: **anchor every count to a
positive control.** Point the pattern at something you know is there and
confirm it matches, before you believe a number it produces about
something you cannot see. A count with no positive control is a claim, not
a measurement.

## What "verified" looks like when you report it

State which of the five checks applied and what each one showed — not just
"tests pass." A report that says "ran the suite, green" answers none of
these; a report that says "reverted the fix, confirmed the target test
failed, reapplied, confirmed it passed" is the thing itself.

If a check could not be exercised this way — no counterexample exists to
plant, the fix touches something you can't safely revert in place, the
output can't be regenerated cheaply — say that plainly instead of skipping
it silently. "Could not verify" and "verified" are different reports; do
not let the first one read as the second because both are absent from what
you said.

## What this skill is not

It does not decide *whether* to write a test, run a review, or dispatch a
second opinion — `failing-test-first` and `sanity-check` own those. It owns
one narrower thing: before a verdict from any of those is trusted, confirm
the thing that produced it was capable of saying no.

It is not a mechanism for automated CI gating — the five checks above are
manual discipline applied by whoever is about to act on a result, not a
script to install. Where a check *can* be made self-verifying (a test suite
that asserts its own fixture count, a validator that asserts nonzero files
scanned), prefer that over remembering to redo this by hand each time.

## Where this came from

The name and the first four checks come from a documented pattern across daily
agent operation: verdicts trusted from checks that turned out not to be
watching anything — a validator that reported zero findings because its
input had vanished, a test module silently skipped rather than run, and a
guard that stayed green after the code path it protected was deleted. Full
provenance for this pattern lives in issue jonhill90/skills#135 on this
repository; the incidents themselves are not reproduced here because the
underlying transcripts are private evaluation evidence, not published in
this collection.

The three blind spots under check 1 are a second, later incident: three
scans reported "clean" while blind, and four iterations of a supervising
loop reported a push as failed when it had actually succeeded, both traced
to a check that could not report the failure it was supposed to catch
(exit code lost through a pipeline, a check reading `$?` after `cmd |
tail`). Recorded portably in issue jonhill90/skills#174; the underlying
transcripts are private, not published here.

A third incident, and the source of check 5: in a single day of supervising
agent work, five separate claims were reported as measured and later
retracted — a count of 0 that was really 181, a cause ruled out that turned
out to be the cause, a cleanup reported as done whose kill command had
silently never run, and a timeout blamed for a leak it did not cause. Every
one was a claim made faster than it was checked, and in each case an
instrument that would have caught it was either not run or was run and not
believed.
