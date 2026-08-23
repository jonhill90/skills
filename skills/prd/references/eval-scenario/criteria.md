# Criteria: skill-prd

This scenario is `prd`'s own trigger case combined with its own explicit
exclusion (`SKILL.md`: "Not a technical design... that content belongs in
the corresponding spec — move it there"). Scored by
`scripts/eval_skill.py`'s `score_prd`, mechanized from the two observables
below — see `docs/evals.md`'s "Which artifact wins": this file is
authoritative, the scorer must never be looser than it.

## Observables

1. **Structure.** The response's own text (the run's final `result_text`,
   never a file the run happened to also write — this scenario has no
   file to check) names, in substance if not in these exact headers, all
   four of: the problem being solved, the goal(s)/outcome, at least one
   explicit non-goal, and at least one observable success criterion a
   non-engineer stakeholder could check. Missing any one of the four is a
   FAIL on this observable — a PRD that skips non-goals or success
   criteria is not a partial PRD, `prd`'s own SKILL.md treats both as
   required sections, not optional polish.

2. **No implementation leak.** The response does not name a concrete
   technical mechanism: a specific technology, storage system, API/
   endpoint shape, library, or file format the export mechanism would use
   internally (e.g. "S3", "a `/export` endpoint", "a background job",
   "Postgres", "pandas", "a Lambda function"). Mentioning "CSV" itself is
   not a leak — the prompt supplies that as the feature name, not as an
   implementation choice the writer invented. A concrete architectural
   noun invented in the answer, not present in the prompt, is what counts
   against this observable.

## Verdict inputs

`scripts/eval_skill.py` runs this scenario twice — once with `prd` on the
skills path, once with it stashed via the harness's own `no-skill:prd` arm —
and diffs the two observables above plus token/turn counts between the two
runs. The combination rule lives in `eval_skill.py`'s `verdict()`; this
file defines only what each run, in isolation, counts as solving.

## What would make this scenario invalid

- The run refused the request outright, or asked a clarifying question and
  received no answer (headless mode supplies none) — INVALID, not FAIL:
  no PRD text means nothing to score on either observable.
- The run wrote a `spec`-shaped document instead of a PRD (explicit
  architecture as the primary content, with "problem"/"goals" reduced to
  a one-line preamble) — score FAIL on Structure, not INVALID: this is the
  exact failure mode the scenario exists to catch, not a malformed run.
