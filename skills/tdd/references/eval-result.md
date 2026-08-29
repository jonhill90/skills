# Eval result

**Verdict: no_effect_observed (n=1)**

A with/without comparison against this skill's own greenfield-versus-bugfix
trigger case, scored on actual tool-call order rather than just presence,
found both arms independently writing the test before the implementation,
unprompted in the no-skill arm's case, at comparable cost. A real result
about this model's own default habit on a small, clearly-scoped
greenfield function, not evidence the skill changes nothing on a larger
or more ambiguous greenfield task, or one phrased to invite jumping
straight to an implementation — neither has been tried.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at `skills/tdd/eval-scenario/`
(moved there by the landing PR jonhill90/agent-evals#22). This citation
is for internal cross-check only — `agent-evals` is a private repository (its evidence is not publicly available),
so a reader of this public repo cannot open it.
