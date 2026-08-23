# Criteria: skill-primer

This scenario tests `primer`'s own instruction to inspect manifests
alongside documentation, against a fixture where the two disagree. Scored
by `scripts/eval_skill.py`'s `score_primer`, mechanized from the two
observables below — see `docs/evals.md`'s "Which artifact wins": this
file is authoritative, the scorer must never be looser than it.

## Observables

1. **Correct stack identified.** The run's final `result_text` states the
   repo's actual language/stack as Rust (not Python, and not simply
   repeating the README's claim uncontested). Explicitly flagging that
   `README.md` is stale/wrong is strong positive evidence for this
   observable but is not itself required — the bar is the final answer
   given to "what language/stack does it actually use", not whether the
   discrepancy was narrated.

2. **Checked a primary source.** The run's own tool calls (Read, Grep, or
   a Bash `cat`/`grep` targeting `Cargo.toml` specifically — not the
   assistant's prose, which can claim a check that never happened)
   include at least one that actually reads `Cargo.toml`. Reading
   `README.md` alone, however confidently summarized, does not satisfy
   this — the whole point of the scenario is that the README is not a
   reliable primary source here.

## Verdict inputs

`scripts/eval_skill.py` runs this scenario twice — once with `primer` on
the skills path, once with it stashed via the harness's own
`no-skill:primer` arm — and diffs the two observables above plus
token/turn counts between the two runs. The combination rule lives in
`eval_skill.py`'s `verdict()`; this file defines only what each run, in
isolation, counts as solving.

## What would make this scenario invalid

- The run never produced a final answer (e.g. it asked a clarifying
  question and headless mode supplied none) — INVALID: no orientation
  text means nothing to score on either observable.
- The run answered a different question than asked (e.g. proposed a
  refactor instead of orienting) — score FAIL on Correct stack identified
  if it never states the language, not INVALID: the prompt was reachable
  and a real (if non-responsive) answer came back.
