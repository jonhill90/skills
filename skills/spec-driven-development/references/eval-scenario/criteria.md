# Criteria: skill-spec-driven-development

Scored by `scripts/eval_skill.py`'s `score_spec_driven_development`,
mechanized from the two observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observables

1. **Actually looked at the existing codebase before writing anything
   new.** The run's own tool calls (Read, Grep, or Bash) touch
   `utils/slugify.py` or search for slug-related code -- not answered
   from the prompt's own wording alone.

2. **Reported that equivalent functionality already exists**, rather
   than adding a new, duplicate function. The run's final answer says
   this already exists (names `to_slug`, `utils/slugify.py`, or
   equivalent), and the fixture's own `utils/slugify.py` is unchanged
   (or only trivially touched -- a doc comment, not a new competing
   function) after the run.

Both matter: reading the file and then writing a duplicate anyway (or
never surfacing that it was found) is the exact failure this skill's own
"a criterion written before starting is also a search" line targets.

## What would make this scenario invalid

- The run never touched `utils/` or `routes.py` at all and gave no
  answer addressing the request -- INVALID, not FAIL: nothing to score.
