# Eval result

**Verdict: improve (n=1, second pass, jonhill90/skills#287, scenario
rewritten first — was could_not_measure)**

The first pass's own diagnosis (below) said the scenario, not just the
harness, needed rework before a re-run could mean anything: its prompt
scoped the search away from the one source that actually contained the
answer, so neither arm was ever positioned to demonstrate the behavior.
Fixed that specifically before re-running anything: built a small,
disposable transcript corpus where the target answer (a decision re-stated
three times, worded differently each time, across three separate sessions)
is genuinely inside the root the prompt names, and confirmed the extractor
sees it with a positive control (`--grep` against the fixture root returned
the seeded phrase across all three sessions) before trusting anything
downstream, the same instrument-first discipline this skill's own content
prescribes.

With the skill on the skills path: the run verified the extractor against
its default root first (nonzero, so the instrument itself was trusted),
then correctly narrowed to the given root, correctly excluded its own
earlier run's leaked log files from the corpus (noticed and explained
unprompted), and produced the single genuine candidate with accurate,
evidenced reasoning — rejecting a boilerplate header repeated verbatim and
several tool invocations for the reasons this skill's own judgement steps
name, not by coincidence. Twelve turns, task complete.

Without the skill (isolated-home stash, real `~/.claude` untouched): the
run ignored the root named in the prompt and instead queried the full
default corpus (thousands of real turns across thousands of sessions) with
ad hoc, self-written n-gram counting code — and did not complete. No
deliverable was produced; the process was still mid-analysis, well past
where the with-skill arm had already finished, when it stopped.

This is a real divergence, not a manufactured one — but it is `n=1`, and
the without-skill arm's non-completion has a genuine alternative
explanation this pass cannot rule out (a long-running, self-written
analysis over a much larger corpus being cut off by this environment,
rather than being incapable of finishing at all). Recorded as `improve`,
not `keep`: a real signal worth replicating, not a confident verdict past
what one pair supports.

Evidence for this pass is from a fresh, local run performed for
jonhill90/skills#287; it was not committed to the private
`jonhill90/agent-evals` repo, so there is nothing further to cite here
beyond this summary.

## Prior pass (superseded by the above, kept for the record)

**Previous verdict: could_not_measure (n=1) — the scenario, not just the harness, needs rework**

Hand-reading both transcripts found the real cause: the scenario's own
prompt inadvertently scoped the search away from the one source that
actually contained the answer, so neither arm was ever positioned to
demonstrate the behavior this skill's own incident is about. Both arms
did handle the resulting uncertainty honestly. Not scored as a
discrimination failure of the skill, since the scenario never gave it a
fair chance to fire. Full write-up (including the eval-instrument
finding behind this verdict) moved to `jonhill90/agent-evals` by
jonhill90/skills#272.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo (evaluation loop tracked via
jonhill90/skills#230; per-skill outcomes recorded in
`docs/eval-status.json`). This citation is for internal cross-check
only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of this public
repo cannot open it.
