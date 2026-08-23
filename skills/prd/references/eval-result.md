# Eval result

**Verdict: two passes, `could_not_measure` (n=1) then `improve` (n=1, not replicated)**

Two independently-designed traps for the same boundary this skill draws
— keeping a named solution out of the problem statement. The first found
both arms correctly kept a proposed technology out of the substantive
requirements sections, differing only in a title-level framing choice
the scenario's own scoring didn't set out to measure — a clean wash. The
second, testing the adjacent case where the request itself names its
own output format, found both arms produced an equally complete,
non-leaking document, but at a real, unreplicated cost delta favoring
the no-skill arm. An earlier scorer misread in that second pass (a
too-literal phrase match, and a negation check too narrow to see an
excluded mechanism as excluded) was caught and fixed by hand-reading the
actual output before trusting either number. Read together: across two
independent traps, this model has not yet been caught crossing the
substantive line this skill draws — the open question is cost, not
correctness.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo, at `skills/prd/eval-scenario/`
(moved there by the landing PR jonhill90/agent-evals#22) — this covers
the second pass; the first pass's evidence lives in the same private repo
without a moved scenario directory (evaluation loop tracked via
jonhill90/skills#230; per-skill outcomes recorded in
`docs/eval-status.json`). This citation is for internal cross-check
only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of this public
repo cannot open it.
