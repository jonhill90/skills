# Eval result

Recorded 2026-08-23, jonhill90/skills#229's own build — this is the first
evaluation this skill has ever had, run as part of the same pass that
wrote it, per #229's explicit ask ("a way to measure whether it is
actually being done"). Run locally (no private-harness dependency): a
corpus-scale fixture (`fixture/vault/`, 100 generated notes + an index,
`~15KB` of note content) and real Agent-tool invocations, one per arm,
scored by mechanical check (`fixture/check_answer.py`) against a ground
truth fixed at fixture-generation time — not against either arm's own
report of what it did. Full design and why this axis was chosen over a
longitudinal or pure-scale escalation: `references/eval-scenario/
criteria.md`.

## Verdict: `improve` (n=2 trials, 4 arm-runs total)

## Two trials, not one — the first found nothing, and that was worth keeping

### Trial 1 (baseline framing): clean no-discrimination

Both arms given the identical task ("what is `ingest-worker`'s max retry
backoff, in seconds") against the 100-note fixture. Arm A read this
skill's `SKILL.md` first; arm B got no skill.

| | tokens | tool_uses | files opened | correct |
|---|---:|---:|---:|---|
| A (skill) | 38,639 | 4 | 2 (`index.md`, `fact-073.md`) | yes |
| B (no skill) | 36,572 | 3 | 2 (`index.md`, `fact-073.md`) | yes |

Indistinguishable — B was marginally *cheaper*. Both arms independently
found the index, matched the one relevant entry, and stopped. This is
the same shape `docs/eval-harness-findings.md` §2 and #248 documented
for habit skills, for a related but distinct reason: this task's own
structure (one specific fact, findable by keyword match) already
telegraphs "search the index," so a capable model's default agentic
reflex (grep/targeted read over cat-everything) already matches this
skill's advice with nothing to choose between. Not a scenario defect —
see `criteria.md`'s validity checks, all of which passed — a real
finding that at this scale, with this framing, there is no gap to close.

### Trial 2 (thoroughness-pressure framing): real, mechanically-verified divergence

Same fixture, same question. Added one line to both arms' prompt: "Time
is not a constraint... being thorough matters more than being quick" —
a real, plausible competing pull toward exhaustive reading, the single-
shot "adversarial pressure" axis `distill`'s own escalation used, not a
longitudinal design.

| | tokens | tool_uses | files opened | correct |
|---|---:|---:|---:|---|
| A (skill) | 38,742 | 4 | 2 (`index.md`, `fact-073.md`) | yes |
| B (no skill) | 39,195 | 13 | 10 (never opened `index.md`; grabbed 10 fact files directly, one of them the right one) | yes |

The skill-loaded arm's behavior did not move at all between trial 1 and
trial 2 — same two files, same tool-call count, holding to the
discipline regardless of the pressure sentence. The no-skill arm's
behavior changed substantially under the same pressure: 5x the files
opened, more than 3x the tool calls, and — notably — it never opened
`index.md` at all, going straight to guessing-and-checking individual
fact files instead. Both arms still landed on the correct answer, so
this is not "the skill prevents wrong answers" — it is specifically
"the skill holds cost down under a pull that pushes the unguided
baseline toward reading more," which is the conjunctive claim #229
itself named as the one worth testing ("progressive uses fewer tokens
AND still solves it — cheaper and wrong is not a win"). Per this
scenario's own `criteria.md` scoring rule (observable 3), that is
`improve`: cheaper (tool_uses and files_opened, unambiguously; tokens,
marginally) and correct, against a comparison arm that is correct but
not cheaper.

## Why this counts as discrimination where the habit-skill scenarios did not

`docs/eval-harness-findings.md` and #248 diagnosed the OLD single-shot
design as unable to separate arms for *habit/consistency* skills because
the base model already behaves carefully regardless of skill-loading —
no scenario pressure changes a disposition that was never in question.
Trial 2 here is a direct, live counter-case to that pattern for a
different reason: it isn't testing whether the model is disciplined in
the abstract, it is testing whether a real competing instruction
("be thorough") moves behavior differently across arms — and it does,
by a factor the mechanical instrument counted, not judged. Trial 1's own
null result is kept in this file rather than discarded, per this
estate's standing "either outcome is a real result" practice — it is
what makes trial 2's divergence a finding about the pressure axis
specifically, not an artifact of the fixture being unfair to one arm.

## The ceiling — "does B even fit" (#229's fourth metric, answered analytically)

Not forced to a literal failure in either trial (100 notes, ~15KB, fits
comfortably in a single context either way). Computed from the fixture's
own measured size instead: ~135 tokens/note average. A full dump stays
under a 50,000-token budget only up to roughly 370 notes; under 150,000
tokens up to roughly 1,110 notes. The estate's own real vault
(`$AGENT_MEMORY_VAULT`) is far smaller than that today — 63 facts, per
#229's own framing — so dumping IT would not currently hit this ceiling
either; `memory-conventions`' own index-first discipline is precautionary
at today's scale, not yet load-bearing. The corpus #229 actually named as
the motivating case (3,756 prompts) is a different, much larger body — a
rough extrapolation at comparable per-item size (not measured directly
here, and stated as an estimate, not a fact) would already sit in the
hundreds-of-thousands-of-tokens range, past where a full dump is a
reasonable strategy regardless of skill. The ceiling is real and
approaching for the corpus #229 was written about, even though this
specific 100-note trial fixture sits well under it.

## Evidence

Both pairs of manifests (`manifest.json` per arm, real ordered
`files_opened` lists, self-reported but cross-checked against
`tool_uses` — no inconsistency found in either trial) and
`fixture/check_answer.py`'s scored output are reproducible by re-running
`references/eval-scenario/prompt.md` against `fixture/vault/`; not
committed verbatim here to keep this file short. `subagent_tokens` and
`tool_uses` are the Agent-tool infrastructure's own real counters, not
either arm's self-report.

## What this trial does NOT do

- Does not run a literal-overflow trial at the ~370+ note scale the
  ceiling section computes — that scale was judged, not measured, to be
  worth the cost only if a first trial at this scale found nothing at
  all; trial 2 found a real signal at 100 notes, so the more expensive
  scale escalation is left as future work, not run here.
- Does not build a general-purpose scorer (no new `eval_status.py` flag,
  no schema change) — one hand-run, hand-scored pair of trials, the same
  weight class as this estate's other single-shot escalations.
- Does not claim the skill prevents wrong answers — both arms answered
  correctly in both trials; the demonstrated value is cost under
  pressure, stated precisely rather than rounded up.
