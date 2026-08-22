# Eval result

Recorded 2026-08-22, closing one skill of jonhill90/skills#230's "26 of 35
never evaluated" gap, run against the keep/improve/rename/drop harness
that landed in the agent-evals repository (not published here; see
"Scope" above). This file states the verdict and what was measured, not
the scenario or transcript — those are private evaluation evidence per
this repository's own policy.

## Verdict: keep

## What was measured

One scenario: given a small set of extracted raw prompts (four), decide a
judgement for each and write it out, one row per prompt. One of the four
prompts carries no decision, question, or preference at all — a bare
acknowledgement. The task's own wording ("one row per meaningful decision,
question, or preference you find") reads naturally as license to skip a
prompt like that; this skill's own SKILL.md names the opposite rule
("every prompt gets an entry ... the single most common mistake") as the
trap this scenario tests.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm:

- **Without the skill:** the run wrote three entries, silently omitting
  the acknowledgement-only prompt. The other three entries also used
  vocabulary the skill's own schema does not use (`weight: "high"/
  "medium"` rather than `hard`/`preference`; `kind: "constraint"` rather
  than `directive`).
- **With the skill:** the run wrote four entries — one per prompt,
  including the acknowledgement-only one, recorded with `kind: "thought"`,
  `weight: "retracted"`, `status: "dropped"`, and a `status_reason`
  explaining why it was kept rather than skipped. The other three entries
  used the skill's own vocabulary (`weight: "hard"`/`"preference"`,
  `kind: "directive"`).

This is a clean, countable difference (3 rows vs. 4, against a 4-prompt
fixture) — not a cost or token delta requiring a rerun to trust, unlike
the other two skills evaluated in this same pass. n=1 per arm; the
difference itself is unambiguous, but a repeat run against a different
prompt set would still strengthen this before treating it as fully
settled.

## What is not evidenced

This scenario tests exactly one of `prompt-corpus`'s several named traps
(the omission rule). It says nothing about the skill's other rules —
`weight=hard` vs. `preference` discipline, the topic-keyword-filter trap,
the `order by length(text_raw) desc` sampling trap, or the loader's
non-atomic-write behavior — none of which this pass measured.
