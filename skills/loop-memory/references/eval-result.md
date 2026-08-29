# Eval result

**Verdict: no_effect_observed (n=1, including a longitudinal escalation)**

A local sandbox trial found both arms correctly persisting resumable
state to disk before stopping on a single-session, context-exhaustion
scenario — the specific failure this skill exists to prevent didn't occur
in either arm, though the two arms structured what they wrote
differently. A follow-up escalation tested a genuinely harder,
longitudinal shape: a real cross-session memory-loss boundary with an
unannounced repeated trap. It still didn't discriminate — the base model
wrote a specific, adequate handoff note both times, with or without the
skill's own file-taxonomy and regression-log guidance. Not evidence
against the skill's value at the scale its own content actually targets
(many more files, a real crash/restart, several repeated sessions); that
scale has not been tried.

The single-session trial ran locally, with no cross-repo citation. The
longitudinal escalation's evidence lives outside this repository, in the
private `jonhill90/agent-evals` repo, at
`skills/loop-memory/eval-scenario/` (moved there by the
landing PR jonhill90/agent-evals#22). This citation is for internal
cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of
this public repo cannot open it.
