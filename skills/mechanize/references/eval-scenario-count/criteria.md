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
2. **`inference_judgements`, self-reported in `manifest.json` -- the
   primary cost signal (skills#267).** The count of the 26 required
   verdicts produced by the model's own per-record reasoning, as opposed
   to by one mechanical pass applied to all of them at once. This is
   what `mechanize`'s own claim is actually about
   (`docs/eval-cost-axis-principle.md`): raw tool-call/action counts
   conflate "how much judgement was done" with "how the answer was
   packaged into tool calls," because N per-record inferences can be
   emitted in fewer tool calls than a mechanical pass plus its
   supporting file operations. `inference_judgements` cannot be gamed by
   that packaging difference the way `tool_uses` can.
3. **`script_written` and `actions_log` length, cross-checked against
   `inference_judgements`, not used as the primary signal.** A
   `script_written=false` run with low `inference_judgements` (e.g. one
   inline command, not persisted) still counts as mechanizing --
   backing off a *file* under time pressure is a different, narrower
   call than backing off the mechanical pass itself. The plausibility
   flags in `check_answer.py` (`script_written` vs `actions_log` length)
   remain a secondary cross-check, not a substitute for the self-reported
   count.
4. **Raw `tool_uses`/`actions_log` length as tiebreak only**, when
   `inference_judgements` ties between arms (e.g. both 0, or both 26) --
   this is the one case raw counts still meaningfully distinguish cost,
   same as before this fix.

## Scoring rule

- Both arms correct AND `inference_judgements` ties (both ~0 or both
  ~26) → no discrimination on the judgement axis; fall back to raw
  `tool_uses` as tiebreak; if that also ties within noise, record
  `could_not_measure` (design did not fire, not evidence of no effect).
- Both arms correct AND one arm's `inference_judgements` is
  substantially lower than the other's (mechanized vs re-derived,
  regardless of `script_written` or raw tool-call count) → real
  discrimination on the cost axis mechanize's own claim is about. This
  is the `progressive-disclosure`-shaped result: record per whichever
  arm has the lower `inference_judgements` and whether that arm is the
  skill-loaded one.
- Either arm produces a malformed/missing `results.csv` or `manifest.json`
  (including a missing `inference_judgements` field) → INVALID for that
  arm specifically, not scored as wrong; re-run rather than record on a
  design failure.

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
