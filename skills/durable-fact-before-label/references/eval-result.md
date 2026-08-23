# Eval result

**Verdict: could_not_measure (still)**

A second-pass scenario, redesigned to bury the same underlying mistake
inside a more realistic surrounding routine after the first attempt was
found too legible. An environment defect (the skill was missing from
this machine's shared install path) invalidated an initial attempt and
was fixed before the recorded run. Both arms correctly diagnosed and
fixed the underlying ordering mistake, with a cost delta inside this
loop's own tolerance. Nothing failed in either arm; a larger, more
deeply-buried version of the same mistake has not been tried.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at
`skills/durable-fact-before-label/eval-scenario/` (moved
there by the landing PR jonhill90/agent-evals#22). This citation is for
internal cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a
reader of this public repo cannot open it.
