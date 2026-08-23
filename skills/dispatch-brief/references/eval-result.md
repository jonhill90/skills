# Eval result

**Verdict: keep (n=2, replicated)**

`dispatch-brief` was evaluated independently, twice, by two different
lanes against two different fixtures, before either pass knew about the
other. Both passes reached `keep` and, read together, converge on the
same specific observable: a brief written with this skill installed
explicitly permits an unresolved "could not measure" result as a
legitimate outcome; a brief written without it never does, across every
run in either pass. That is a real, replicated behavioral difference on
one of this skill's own named rules, not a cost-only or borderline
signal. A second observable tested by one of the two passes did not
survive its own replication and is not treated as settled.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at
`skills/dispatch-brief/eval-scenario-latency-guard/` and
`skills/dispatch-brief/eval-scenario/` (moved there by the
landing PR jonhill90/agent-evals#22). This citation is for internal
cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of
this public repo cannot open it.
