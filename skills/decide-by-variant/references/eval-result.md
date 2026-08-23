# Eval result

**Verdict: could_not_measure (n=2, scorer bug found and fixed, effect did not replicate)**

A first live pair, after a scorer fix (a keyword-only detector missed an
unlabeled but real violation), scored as a clean discriminating result. A
second independent pair, run specifically to check that signal before
trusting it, did not reproduce it — the arm that had failed the first
time succeeded the second. Two samples pointing in different directions
is exactly the noise this loop's own repetition bar exists to catch; an
n=1 read would have shipped a false confident verdict.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo (evaluation loop tracked via
jonhill90/skills#230; per-skill outcomes recorded in
`docs/eval-status.json`). This citation is for internal cross-check
only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of this public
repo cannot open it.
