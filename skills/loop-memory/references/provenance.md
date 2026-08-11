# Provenance

This skill's file set, re-injection rule, receipt discipline, and 60%
handoff threshold come from an internal research review of long-running
and scheduled agent loops. That review is not a published repository and
is not linked here; treat every claim below as practice recommended by
that review, not as a result this skill's own use has measured.

- **Persistent memory as an underdeveloped field.** The review's source
  corpus is public: a 50-loop survey of long-running agents,
  [arXiv 2607.00038](https://arxiv.org/pdf/2607.00038), which names
  persistent memory as one of the two most underdeveloped fields across
  the loops it examined. Most real loops are forgetful, and forgetfulness
  in a loop is not a lapse — it produces repeated work, repeated mistakes,
  and an audit trail that cannot answer "why did it do that on Tuesday?"
- **Re-injection and the 60% threshold.** Drawn from the long-running-
  agents and planning-with-files literature surveyed by the same review.
  Not independently measured here.
- **Receipts and "green ≠ success."** The rule that a green process exit
  means the process exited, not that the task succeeded, is corroborated
  publicly by Anthropic's own Routines documentation, which warns that a
  passing run status alone does not mean the task passed.
- **The stale-handoff failure mode.** A concrete instance of a running
  supervisor loop treating its own stale handoff doc as current, prompting
  the "edit in place, verify before trusting" rule in the main skill body.
  This is a single observed incident, not a scored comparison.
- **The circuit-breaker-before-retry pattern.** Also drawn from the same
  internal review; not independently measured here.

**What is not evidenced:** no run has compared a loop that keeps this file
set against an otherwise-identical loop that does not, and scored the
difference. The file set, thresholds, and rules above are the review's
recommendations, adopted as practice, not a finding this skill can point
to as its own result.
