# Criteria: skill-loop-memory (longitudinal)

Not run through `scripts/eval_skill.py` (no `score_loop_memory` exists;
this scenario predates any mechanized scorer for the longitudinal design
-- see `docs/eval-longitudinal-design.md`'s "What this trial does NOT
build" for why that is a deliberate scope cut, not an oversight). Scored
by hand against the observables below, the same way `loop-memory`'s
original pass-12 result was.

## The observable: does session 2 repeat session 1's mistake

1. **Did session 1 mishandle the `#`-in-value case in `06.cfg`?**
   (`migrate_check.py`'s `06: FAIL` before any self-correction, or a
   transcript inspection showing a truncated `archive_path` value at any
   point.) If NEITHER arm ever produces a wrong `06.json` at any point in
   session 1, this scenario did not get a chance to test the mechanism it
   was built for -- record `could_not_measure (design did not fire)`,
   distinct from `could_not_measure (clean no-discrimination)`; see
   "What would make this scenario invalid" below.

2. **If session 1 mishandled it, did session 1 leave a record of the
   specific failure** -- not just "migration complete" or a generic
   progress note, but something identifying the `#`-mid-value symptom
   specifically (a decisions/known-failures entry, a comment in the
   migration script, a line in a handoff note)? This is the
   divergence-point candidate: `loop-memory`'s own "Known failures become
   a regression set" section is exactly this practice; its absence in the
   without-skill arm is the predicted (not assumed) gap.

3. **Does session 2's FIRST write of `dest/11.json` match the reference
   transform** (`migrate_check.py`'s `11: PASS` on the first check run
   that covers item 11, not after a fix-and-recheck cycle)? This is the
   actual divergence measurement:
   - **First-attempt correct** = the mistake did not recur for this arm.
     If this happens for the with-skill arm and NOT the without-skill
     arm, that is the discriminating result the longitudinal design
     exists to produce -- score `improve` for `loop-memory` (its
     recorded discipline is what closed the gap between the two arms;
     name the specific mechanism -- e.g., a known-failures entry read
     before item 11 -- not just the outcome).
   - **Both arms first-attempt correct** = clean no-discrimination,
     same bucket as the original single-shot result, but now with a
     harder instrument's confirmation rather than a lighter one's
     assumption -- record accordingly rather than treating "the design
     worked" and "the skill helped" as the same finding.
   - **Both arms repeat the mistake** = the skill's file set didn't
     transfer the specific fix into session 2 either, or session 2 never
     consulted whatever was written -- read the with-skill arm's session
     1 output and session 2 transcript before concluding either "wrong
     instrument" or "skill's own practice wasn't followed"; those are
     different findings and the transcript, not the outcome alone, tells
     them apart.

4. **Divergence point, if any exists:** the specific tool call in session
   2 where the with-skill and without-skill arms' behavior first differs
   -- e.g., with-skill session 2 reads a `known-failures.md` before
   writing `11.json` and gets it right immediately; without-skill session
   2 writes `11.json` wrong, runs `migrate_check.py`, sees `11: FAIL`,
   and only then fixes it (or doesn't). Record the tool-call index and
   quote the relevant line, the same evidentiary standard
   `tdd`'s own `criteria.md` uses for its order check.

## What would make this scenario invalid

- Session 1 never attempts item 06 in one or both arms (ran out of the
  interrupt budget too early, or reordered the batch) -- INVALID for
  that arm, not FAIL: nothing to compare against session 2.
- Session 2 never attempts item 11 -- same, INVALID not FAIL.
- The interrupt message is delivered before item 06 is reached in an arm
  -- that arm never had the chance to make the mistake the scenario is
  built around; record `could_not_measure (design did not fire)` for that
  arm specifically, re-run with the interrupt timed later rather than
  silently counted as a clean pass.
- Session 2 is accidentally given conversation continuity with session 1
  (same subagent, same context) -- invalidates the entire trial; the
  premise being tested is specifically "no memory across the boundary."
