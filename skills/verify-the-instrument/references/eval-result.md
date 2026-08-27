# Eval result

**Verdict: keep**

A with/without comparison against a fixture with a real, planted defect
found the skill-installed run producing a substantially more complete
fix — applying this skill's own named pattern to the actual bug, in the
skill's own vocabulary — while the no-skill run left the defect in place
entirely, confirmed by reading the fixture's own before/after file state
directly. n=1 per arm; the exact tool-call path behind the fix was not
preserved for replay. Full write-up (including the eval-instrument
finding behind this verdict) moved to `jonhill90/agent-evals` by
jonhill90/skills#272.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo (evaluation loop tracked via
jonhill90/skills#230; per-skill outcomes recorded in
`docs/eval-status.json`). This citation is for internal cross-check
only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of this public
repo cannot open it.
