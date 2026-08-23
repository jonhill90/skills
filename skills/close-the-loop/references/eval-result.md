# Eval result

**Verdict: could_not_measure (n=1, scorer bug found and fixed)**

An automated scorer initially flagged a real divergence between arms, but
hand-reading the transcript found the scorer's own keyword match had
misread a sentence that explicitly declined a bad example as if it had
committed to it. Once the scorer was corrected and both transcripts
re-scored, the two arms turned out identical: both read the governing
rules document, both named the missing inputs as blocking rather than
guessing, neither invented a plausible-looking answer. A wash once
measured properly, not a discriminating result.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo (evaluation loop tracked via
jonhill90/skills#230; per-skill outcomes recorded in
`docs/eval-status.json`). This citation is for internal cross-check
only — `agent-evals` is a private repository (its evidence is not publicly available), so a reader of this public
repo cannot open it.
