# Criteria: mechanize (counting measurement, skills#266)

Not run through `scripts/eval_status.py`'s scoring path (no scorer exists
for this skill there; that script only checks the *record*, never assigns
a verdict). Scored by hand against the observables below, then recorded
via `--record` if and only if a real divergence is found.

This is a second, from-scratch scenario for `mechanize`, not a re-run of
`eval-case.md`'s tick-eleven scenario (already tried, `references/
eval-result.md`, found a scorer defect and a habit-skill-shaped
no-discrimination result). This one is built the way
`progressive-disclosure`'s `eval-scenario/` (skills#265) was: a real
countable quantity, not a scored transcript read.

## The countable quantity

`mechanize`'s own "smell" section names the target directly: *"any answer
a model re-derives identically every time it runs."* The fixture gives 26
identical judgments to make (is this tick healthy, by a fixed two-field
rule implied by 4 worked examples) -- a repeated-execution task, not a
one-shot planning document. The claim under test: does loading the skill
change whether the model recognizes the repetition and mechanizes it (one
script, run once) versus re-deriving the same judgement 26 times by hand
(one tool call's worth of reasoning per tick)?

1. **Correctness, checked mechanically.** `fixture/check_answer.py`
   scores `results.csv` against a ground truth fixed at fixture-generation
   time (`ground_truth.json`, not exposed to either arm -- kept one level
   above `fixture/`, the directory both arms are told about).
2. **`script_written`, self-reported in `manifest.json`, cross-checked**
   against `actions_log`'s length per the plausibility flags in
   `check_answer.py` -- a script-based solve should need roughly a
   constant number of actions regardless of the 26-tick count (read the
   ticks, write one script, run it, write results); a manual solve should
   scale with the tick count.
3. **`actions_log` length itself** -- the primary countable cost signal,
   analogous to `progressive-disclosure`'s `tool_uses`/`files_opened`.
   Not a judged impression of "did it feel more disciplined" -- a literal
   count.

## Scoring rule

- Both arms correct AND both mechanize (script_written=true, short
  actions_log) → no discrimination on this axis; record
  `could_not_measure` (design did not fire, not evidence of no effect).
- Both arms correct AND neither mechanizes (both process ticks
  individually, actions_log scales with 26) → same, `could_not_measure`.
- One arm mechanizes (short, roughly-constant actions_log) and the other
  does not (actions_log visibly scales with the 26 remaining ticks), both
  still correct → real discrimination on the cost axis mechanize's own
  claim is about. This is the `progressive-disclosure`-shaped result:
  record per whichever arm is cheaper and whether that arm is the
  skill-loaded one.
- Either arm produces a malformed/missing `results.csv` or `manifest.json`
  → INVALID for that arm specifically, not scored as wrong; re-run rather
  than record on a design failure.

## What would make this scenario invalid

- The four worked examples are insufficient to derive the true rule
  (`error_rate < 0.05 AND latency_ms < 200`) uniquely -- checked at
  fixture-generation time: the four examples span both classes and both
  boundary directions (one field over threshold, the other under, in each
  of the two false cases) so the rule is not underdetermined by them.
- The ground truth leaks into `fixture/ticks/` itself -- checked:
  `grep -rl healthy fixture/ticks/` and `grep -rl unhealthy fixture/ticks/`
  before trusting a run; the tick files contain only `tick_id`,
  `error_rate`, `latency_ms`.
- Arm A was not actually given `mechanize`'s `SKILL.md` to read (a wiring
  mistake) -- invalidates the trial; re-run rather than record.
