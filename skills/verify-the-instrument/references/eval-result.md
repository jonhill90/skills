# Eval result

Recorded 2026-08-22, closing one skill of jonhill90/skills#230's "26 of 35
never evaluated" gap, run against the keep/improve/rename/drop harness
that landed in the agent-evals repository (not published here; see
"Scope" above). This file states the verdict and what was measured, not
the scenario or transcript — those are private evaluation evidence per
this repository's own policy.

## Verdict: keep

## What was measured

One scenario: a CI gate script has been green for six months and nobody
has seen it fail; the task asks the run to confirm it can actually catch
a real problem before it starts blocking merges. The gate has a real,
planted bug matching this skill's own SKILL.md provenance section (a
count query that comes back empty reads as "nothing wrong," so a missing
or unreadable database prints PASS instead of failing loudly).

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm. Read
directly off the fixture's own files after each run (the strongest signal
here, independent of either run's own prose):

- **Without the skill:** the gate script was left byte-identical to the
  planted-bug version — unread as broken, or read and reported without a
  fix.
- **With the skill:** the gate script was rewritten with a third exit
  code separating "clean," "violation," and "could not measure" — this
  skill's own named pattern (SKILL.md check 3: "give the check a third
  exit code... reserve a distinct code for it"), applied to the actual
  planted bug, in the skill's own vocabulary.

## A scorer defect found and disclosed, not papered over

The harness's own automated scorer (a regex over the run's tool calls,
looking for a "delete/rename the database, then rerun the gate" sequence)
returned the opposite reading — `improve`, flagged as the skill-installed
run doing *worse*. Reading the fixture's own files by hand (above)
contradicts that: the skill-installed run produced a substantially more
complete fix than the run without it, which left the bug in place
entirely. The likely cause: the scorer only recognizes the literal
plant-then-rerun ritual, and the skill-installed run may have reasoned to
the fix from reading the script directly rather than performing that
exact sequence in an order the scorer's regex expects — a gap in the
measuring instrument, not evidence the skill made the outcome worse. The
verdict above follows the file-level evidence, not the scorer's own
number; the scorer's blind spot is recorded here so the next pass fixes
the check rather than re-discovering the same false reading.

## What is not evidenced

n=1 per arm. The exact tool-call sequence behind the skill-installed
run's fix was not preserved for replay (the harness parses each run's
transcript in memory and does not persist it), so the claim above rests
on the fixture's before/after file state, not a full accounting of every
step taken to get there.
