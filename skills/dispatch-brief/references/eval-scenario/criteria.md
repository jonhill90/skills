# Criteria: skill-dispatch-brief

Scored by `scripts/eval_skill.py`'s `score_dispatch_brief`, mechanized
from the three observables below -- this file is authoritative
(`docs/evals.md`, "Which artifact wins"); the scorer must never be
looser than it.

## Observables, checked against the written `brief.md` itself

1. **Pastes the concrete evidence, not a paraphrase.** `brief.md`
   contains the actual measured input/output from `evidence.log`
   (`125000.00` and `1250.0` both appear), not just a restated
   description like "large amounts get truncated."

2. **Demands the mutation in BOTH directions.** `brief.md` explicitly
   instructs verifying the guard fails when the bug is present AND fails
   again when reintroduced after a fix (both directions named -- "break
   it the other way" / "confirm it goes red again" / equivalent), not
   just "add a test that passes."

3. **Permits "could not measure."** `brief.md` states, or clearly implies,
   that a worker who cannot get a reliable signal should say so rather
   than being required to produce a keep/fixed verdict regardless.

All three are independently checkable in the written brief text. A brief
that nails (1) and (2) but demands an unconditional pass/fail from the
worker has not implemented this skill's own explicit "could not measure
is a real, valid verdict" rule.

## What would make this scenario invalid

- The run never wrote `brief.md` at all (e.g. it fixed the bug directly
  instead of writing a brief) -- INVALID, not FAIL: the prompt asks for
  a brief, not a fix; nothing to score against these observables.
