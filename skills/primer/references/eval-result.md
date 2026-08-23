# Eval result

**Verdict: drop (n=2, replicated), reinforced by an earlier could_not_measure pass**

Two independent evaluations, three independent with/without samples in
total across two different fixtures, all converging on the same
non-result. The first tested whether a run avoids fabricating a command
that doesn't exist in a manifest with no test/lint setup at all — both
arms handled it correctly and identically, recorded conservatively at n=1
as `could_not_measure`. The second, harder fixture set the project's own
documentation directly against its actual manifest (a mismatched
language/stack claim) and ran the comparison twice, independently, not as
one pair re-scored — both runs, both arms, correctly caught the
discrepancy by checking the manifest rather than trusting the
documentation, with cost inside tolerance both times. Two independent,
replicated samples showing no gap, on top of a first pass that already
found none, is read as the closest this evaluation loop's own methodology
gets to an honest `drop` for a scenario at this scale — not evidence
against a harder, more ambiguous repository still showing a real gap.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at
`skills/primer/eval-scenario/` (moved there by the landing PR
jonhill90/agent-evals#22) — this covers the second pass; the first pass's
evidence lives in the same private repo without a moved scenario
directory (evaluation loop tracked via jonhill90/skills#230; per-skill
outcomes recorded in `docs/eval-status.json`). This citation is for
internal cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a
reader of this public repo cannot open it.
