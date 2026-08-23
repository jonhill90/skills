# Eval result

Recorded 2026-08-22, ninth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=2, scorer bug found and fixed, effect did not replicate)

## No documented incident for this candidate

As with this pass's other two picks, no remaining unevaluated skill had
a genuine documented incident in its own SKILL.md text. `decide-by-variant`
was picked for its own precise caveat instead (`SKILL.md`: "Run
`determine-intent` first — if the answer is already a known parameter,
build nothing... Do not reach for this when the answer is already
known.").

## What was measured

A request phrased exactly like this skill's own trigger ("propose a few
accent color options... so I can pick one") against a fixture where
`DECISIONS.md` already settles the question ("Accent color: blue
(`#2563eb`). Confirmed 2026-07-01. Do not re-propose options for this —
it is settled, not open."). Scored on: did the run read `DECISIONS.md`,
did it name the settled decision, and did it build/propose new color
options as an open choice anyway.

## A real scorer bug, caught by hand-reading the "without" transcript

The first live pair scored a clean `keep` after correction (see below):
with-skill refused to build variants and asked whether the user wanted
to reopen the settled decision; without-skill built a five-row comparison
table (Indigo `#4f46e5`, Violet `#7c3aed`, Teal `#0d9488`, Orange
`#ea580c`, plus the incumbent blue) with WCAG contrast ratios computed
for each — a textbook variant-picker despite having read and quoted
`DECISIONS.md` immediately beforehand.

`_BUILT_VARIANTS`'s original regex only matched literal "option A/B/1"
or "variant A/B/1" phrasing. This response used neither — it presented
the options as a markdown table with color names as row labels — so the
regex missed a real, unambiguous violation of the scenario's own
criteria.md ("no 'option A: ..., option B: ...' shape... no new candidate
hex values offered as a picker"). Fixed by adding a second check: two or
more new hex color codes (excluding the settled `#2563eb`) anywhere in
the response counts as building variants, regardless of phrasing.
Re-scored the same saved transcripts with the fix — flipped from
`solved=True` (scorer bug) to the correct `solved=False` for the
without-skill arm.

## Second pair run to check the signal — it did not replicate

Per this pass's own instruction to re-run any signal that looks strong
on first pass: a second independent live pair (same fixture, same
prompt) showed the without-skill arm ALSO correctly refusing to build
variants this time — reading `DECISIONS.md` and asking the user to
confirm whether the decision should be reopened, no hex table. Hand-read
that transcript to confirm the scorer's `solved=True` was not itself a
false negative on the newly-added hex-count check; it was correct — the
response contains no new hex codes at all.

| Pair | With: solved | Without: solved |
|---|---|---|
| 1 | yes (asked, no variants) | no (built a 5-color table anyway) |
| 2 | yes (asked, no variants) | yes (asked, no variants) |

## Why `could_not_measure`, not `keep` or `drop`

Two samples, one showing a real difference and one showing none, is
exactly the noisy-signal case this loop's ×2/×3-repetitions bar exists to
catch (originally stated in `docs/evals.md`, which was removed from this
repo 2026-08-09, before this pass ran -- could not be re-checked against
the current tree) — n=1 (pair 1 alone) would have shipped a false
confident `keep`. Recorded `could_not_measure`. Worth naming as
suggestive rather than settled: the skill-installed arm was correct in
both runs (2/2), the skill-absent arm in only one (1/2) — consistent
with, but not proof of, the skill making baseline behavior more reliable
on this exact trap rather than changing what a already-good run looks
like. A third pair, or a harder-to-spot variant-request phrasing, would
be needed to settle it either way.

## What is not evidenced

Whether the without-arm's inconsistency (1/2) is a real base-rate for
this model on this exact trap, or noise from only two samples. Also not
tested: whether the skill's benefit (if real) holds on a decision that
is settled less explicitly than an in-repo `DECISIONS.md` with an
explicit "do not re-propose" line — the fixture here may be an
unusually easy signal to catch either way.
