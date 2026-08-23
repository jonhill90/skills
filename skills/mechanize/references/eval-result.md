# Eval result

**Verdict: could not measure a reliable skill-attributable difference**

An initial attempt found the automated scorer had a real blind spot
(recognizing only one vocabulary for "recommend mechanizing this") that a
hand read caught — reported as an instrument problem, not a skill
verdict. A follow-up counting-measurement redesign (a real, mechanically
scored quantity rather than a scored write-up) ran several trials across
a baseline framing and a pressure framing that argued against building
reusable tooling. Most trials showed no discrimination; one trial
surfaced a real, evidenced qualitative divergence in HOW the two arms
solved the task that the scoring schema of the time wasn't built to
detect. The schema was subsequently extended to capture that exact
distinction, and a fresh live re-run under the corrected schema again
showed no clean divergence. Taken together: the instrument now can see
the divergence when one occurs, but this fixture does not reliably
produce one.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at
`skills/mechanize/eval-scenario-count/` (moved there by the
landing PR jonhill90/agent-evals#22). This citation is for internal
cross-check only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of
this public repo cannot open it.
