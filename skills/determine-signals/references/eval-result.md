# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop (estate-loop/agent-b2.md), superseding this file's own third-pass
result. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario itself is committed at
`skills/determine-signals/references/eval-scenario/` so it can be
re-run.

## Verdict: could_not_measure (still)

## The new scenario

`docs/eval-harness-findings.md`'s Cause A named this skill's own
third-pass scenario as too easy: the stale note carried a visible
migration timestamp next to a plainly-more-current config, so both arms
trusted the live source without weighing anything. This pass's fixture
removes every surface cue: `known-issues.md` is an undated "Current
infra facts" list, five of six bullets true, phrased identically to the
one stale bullet ("Redis cache TTL is 300s") -- nothing marks it as
older or less authoritative than the other five. The live value
(`config/cache.yaml`: `ttl_seconds: 900`) can only be found by actually
reading that file, not by pattern-matching which document "looks newer."

## What was measured, and a real inconsistency caught by reading both
## full transcripts before trusting either number

Run **twice** (the second run specifically to read the full transcript
before trusting the first pair's printed cost delta -- see below), same
task, same fixture, once with `determine-signals` installed and once
with it removed via the harness's `no-skill:<name>` arm:

- **Pair 1:** both arms read `config/cache.yaml` and answered 900s, not
  300s. With: 9 turns, 181,767 tokens. Without: 4 turns, 94,967 tokens
  -- a 1.9x/2.2x delta, which the harness's mechanical rule reads as
  `improve`.
- **Pair 2 (rerun to inspect the full answer text, not the 300-character
  preview):** both arms again read the config and answered 900s. With:
  6 turns, 138,141 tokens. Without: 6 turns, 139,120 tokens -- a 1.007x
  delta, inside the harness's own ×1.5 tolerance, no signal at all.

The full transcripts (not the truncated preview) show both arms, both
pairs, giving essentially the same answer: state 900s decisively, note
the disagreement with `known-issues.md`, hedge honestly that git history
(one commit, both files) cannot establish which is stale. Nothing about
the SKILL's presence changed what was found or how it was reasoned about
in either pair.

## Why this is could_not_measure, not improve

The outcome axis never moved across two independent pairs: four arms,
four correct answers, all citing the live config. The cost axis moved
sharply in pair 1 and not at all in pair 2 -- the same scenario, same
skill, same absence of it, producing a large delta once and none the
next time. A cost signal that does not reproduce across independent runs
is exactly the ×2/×3-repetitions bar `docs/evals.md` sets before trusting
an efficiency delta at all (that file was removed from this repo
2026-08-09, before this pass ran -- could not be re-checked against the
current tree); recording `improve` off pair 1 alone, when
pair 2 directly contradicts it, would be trusting noise. Recorded as
`could_not_measure` -- genuinely unmeasured, not a wash dressed up as a
pass, and not an unreproduced delta dressed up as a finding.

## What is not evidenced

Whether the cost-delta inconsistency itself is meaningful (e.g. the
skill sometimes prompts a more thorough hedge-and-caveat pass, sometimes
not) or pure run-to-run variance unrelated to the skill -- distinguishing
those would need several more pairs, which is the ×2/×3 bar this result
explicitly declines to claim it cleared.
