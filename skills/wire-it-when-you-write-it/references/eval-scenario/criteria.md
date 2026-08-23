# Criteria: skill-wire-it-when-you-write-it

Scored by `scripts/eval_skill.py`'s `score_wire_it_when_you_write_it`,
mechanized from the one observable below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observable

**`deploy.sh` actually refuses on a dirty tree, demonstrated by running
it, not by reading its source.** After the run, the scorer:

1. Makes an uncommitted change in the fixture repo (`echo x >> file.txt`,
   no commit).
2. Runs the run's own final `deploy.sh`.
3. Passes only if `deploy.sh` exits non-zero and the check actually ran
   (not merely "some check exists in the file" -- the DEMONSTRATED
   behaviour, matching this skill's own bar: "the behaviour has to be
   demonstrated, not merely the code to exist").

This is deliberately NOT a text/grep check for "does deploy.sh mention
check_clean" -- a call that's present but never reached (dead code,
wrong function, wrong conditional) would pass a text search and still
leave the failure this skill exists to prevent. Running it is the only
check that cannot be fooled by code that merely LOOKS wired.

## What would make this scenario invalid

- The run never touched `deploy.sh` at all -- INVALID, not FAIL: nothing
  to score.
- The run deleted or renamed `deploy.sh` -- INVALID for this mechanized
  check (nothing to execute); a human would need to read the rewrite by
  hand.
