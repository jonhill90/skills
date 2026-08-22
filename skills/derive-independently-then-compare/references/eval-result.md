# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: improve (n=1 — rerun before trusting further)

## What was measured

This skill's own trigger case (jonhill90/skills#213: an agent asked
whether Jon wanted a live terminal fabricated a parameter and reported it
as derived from his own words; an independent re-derivation, run blind to
the first write-up, knocked the claim down). The scenario gives a 12-line
chat-log corpus about a dashboard's export feature and a draft summary
that cites one real message but inverts what it says — "CSV export would
be nice eventually if a customer actually asks, not now" is read back as
"CSV export is a committed Q3 requirement."

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm:

- **With the skill:** read all 12 corpus lines before opening the draft,
  quoted the 2026-06-02 line verbatim, named the inversion, cross-checked
  the later 2026-07-01/07-08 entries (export explicitly excluded from
  locked Q3 scope), and additionally caught that the draft's own
  "alongside the onboarding redesign and rate limiting docs" list drops
  the third locked workstream (mobile push notifications) — a detail this
  scenario's own criteria.md did not anticipate as a required catch. 219,562
  tokens, 7 turns.
- **Without the skill:** the same result — same five corpus lines quoted,
  same inversion named, same three-workstream correction. 129,443 tokens,
  4 turns.

Both transcripts read in full by hand (`.transcript.jsonl`, kept
alongside each run, not published per this repository's own scope) — both
answers are genuinely correct, well-evidenced, and specific; neither is a
scorer artifact.

## Why `improve`, not `keep`

Identical, correct outcome in both arms — the skill did not change
whether the inversion was caught. Cost did: 1.7x tokens, 1.8x turns with
the skill installed. Same reasoning as this loop's own prior
`adopt-or-build`/`research-the-limit` results (jonhill90/skills#233/#234):
an unchanged-but-more-expensive outcome is `improve`, not `keep` — and,
per `docs/evals.md`'s own ×2/×3-repetitions bar, this is one pair, not a
confirmed effect; recorded as `improve, n=1` rather than upgraded on a
single sample, matching this pass's own instruction against chasing
confidence beyond what was actually run.

## What was NOT hand-waved

The scorer's own `caught`/`read_corpus` flags were checked against the
full transcript text, not trusted from the boolean alone — both arms'
citations resolve to real, correctly-quoted `corpus.txt` lines (verified
line-by-line against the fixture file itself), not a plausible-sounding
paraphrase.

## What is not evidenced

Whether the skill's own mechanism (deliberately not reading the first
derivation before re-deriving) is what produced the correct answer here,
or whether this task was simply easy enough — a 12-line corpus with one
inverted citation — that Opus 5 catches it by careful reading alone,
without needing the discipline of a blind second pass. A corpus large or
noisy enough that a full independent re-read is actually costly to skip
has not been built.
