# Eval result

**Verdict: improve**

Recorded as a backfill: this was the first skill ever evaluated by this
evaluation loop's own harness, in the pull request that built the
harness itself. Three independent live runs against a fixture built
around a plausible-sounding but false capability claim found the outcome
axis a wash across all three — a strong model already knew the real
capability and solved it correctly with or without the skill every time.
One signal consistently tracked the skill's presence across every run
where it was measured: whether the run actually checked a primary source
before answering, true only with the skill installed, never a false
positive. Token/turn cost swung in both directions across runs with no
consistent sign, read as noise rather than a directional cost claim.

Evidence for this verdict lives outside this repository, in the private
`jonhill90/agent-evals` repo — this was the very first skill evaluated
there, in the pull request that built the harness (jonhill90/agent-evals#21).
This citation is for internal cross-check only — `agent-evals` is a private repository (not publicly available), so a reader of this public repo cannot open it.
