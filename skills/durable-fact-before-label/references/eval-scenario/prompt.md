# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> We had a crash last night mid-reconcile. Now some claims look released
> while their result files are missing. Find the bug in `reconcile.py`
> and fix it.

## Setup

`fixture/` is a git repo containing:

- `reconcile.py` -- a ~100-line reconciler with several functions
  (argument handling, retry/backoff, logging, a claims store) around the
  one real bug: `process_one()` releases the claim on an item BEFORE
  writing that item's result file to durable storage. A crash between
  those two lines leaves the claim released (so the item looks free/done)
  while the result file never got written -- exactly the symptom
  described in the prompt.
- `crash-report.txt` -- the symptom as observed, phrased the way an
  operator would describe it (no line numbers, no pointer at the bug).

Redesigned after this skill's own third-pass result
(`skills/durable-fact-before-label/references/eval-result.md` in
jonhill90/skills, v1): the v1 fixture's bug was "two adjacent lines to
swap" in an otherwise-empty `finalize.py`, legible from the code alone
with no investigation required. This fixture buries the same ordering
mistake inside a realistic reconciler with retry logic, logging, and
unrelated helper functions around it -- finding it requires reading
`process_one()`'s actual call sequence, not noticing two isolated lines
next to each other.
