# Eval result

Two independent evaluations, three independent with/without samples
total across two different fixtures, all three landing on the same
outcome. This file preserves both write-ups, each attributed to its own
pass, per `docs/eval-status.json`'s "one entry per skill" record and the
convention this loop uses when a second pass lands on a skill a prior
pass already covered: neither overwrites the other.

## Agreement

**The two passes agree, and reinforce each other.** Pass 13's
TypeScript/Express fixture (no test/lint script anywhere) and pass 14's
Python-vs-Rust manifest-discrepancy fixture test genuinely different
edges of `primer`'s own instruction set — "don't fabricate what isn't
there" versus "check the manifest even when the docs aren't silent, just
wrong" — and every one of the three independent with/without samples
across both (pass 13's one pair, pass 14's two replicated pairs) came
back identical-outcome, no cost anomaly. Recorded as `could_not_measure`
at pass 13 (n=1, correctly conservative at that sample size) and `drop`
at pass 14 (n=2, meeting the replication bar `could_not_measure` was
itself withholding judgment for). Taken together this is three
convergent samples, not one — the strongest evidence in this skill's own
record for the reading pass 14 settled on.

---

## Pass 13 (2026-08-23)

Recorded 2026-08-23, thirteenth pass of jonhill90/skills#230's
evaluation loop, run against the keep/improve/rename/drop harness that
lives in the agent-evals repository (private evaluation evidence, not
published here). Recorded via `scripts/eval_status.py --record` — the
one supported write path since #245's per-skill append-only logs.

### Verdict: could_not_measure (n=1)

### Selection

`primer` was picked from the same six-skill remaining pool as `prd`
(see that skill's own eval-result.md for the full remaining-pool
context) for its own explicit instruction: "Keep the report concise and
evidence-based. Do not infer unsupported commands or architecture."

### What was measured

A small TypeScript/Express service fixture: `package.json` declares a
`build` script and a `start` script, no `test` script, no `lint`
script, no test-framework devDependency, no `tests/` directory, no CI
config anywhere. Scored on: did the run read `package.json`, did it
avoid stating a fabricated `npm test`/`npm run lint` command that
doesn't actually exist in the manifest, and did it explicitly name the
absence of a test/lint command rather than staying silent about it.

### Outcome: both arms handled it correctly, in detail

Both arms read `package.json`, reported only the two commands that
actually exist (`npm run build`, `npm start`), and explicitly named the
absence — the WITH arm: "No test script, linter, or CI config exists.
There's nothing to run for verification..."; the WITHOUT arm: "No
tests, no test script, no CI config, no linter." Neither fabricated an
`npm test` or `npm run lint` invocation anywhere in either response.
Both went further than the minimum bar: both independently noticed the
missing `tsconfig.json` would make the declared `build` script fail
outright, both noticed `typescript`/`@types/express` are absent from
devDependencies despite being required for the code to typecheck, and
both declined to run `npm install` unprompted (a mutating action
against a repo they were only asked to survey). Hand-read both full
result texts; no scorer bug found — the `named_absence`/`fabricated`
regexes matched real, correctly-attributed text in both arms.

Cost: 129,872 tokens / 7 turns (with) vs. 95,557 / 5 turns (without) —
1.36x token ratio, 1.4x turn ratio, both under this harness's own 1.5x
efficiency-flag threshold. No second pair run — no signal near the
threshold, consistent with this loop's practice of reserving
replication for results close to or across that line.

### Why `could_not_measure`, not `drop`

Nothing failed. Both arms produced an accurate, evidence-based primer
report with no fabricated command and an explicit absence-flag exactly
where the skill's own output template calls for one. Per
`docs/eval-harness-findings.md`, an identical-outcome pair reads as
`could_not_measure`, not the mechanical `drop`.

### What is not evidenced

Whether the same discipline holds on a repository with a MORE
plausible-looking, but still absent, test setup — e.g. a `devDependencies`
entry for `jest` or `vitest` with no matching `scripts.test` entry (a
half-configured state closer to a real abandoned setup than this
fixture's clean absence), which would test whether the model
distinguishes "framework installed but not wired to a script" from
"nothing here at all" rather than just noticing a script key is
missing.

---

## Pass 14 (2026-08-23)

Recorded 2026-08-23, fourteenth pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/primer/references/eval-scenario/` so it can be re-run.

### Verdict: drop (n=2, replicated)

### Why this skill, with no documented incident

Per pass 9's own finding (still true at this pass — checked again by
grepping `docs/eval-harness-findings.md` for every remaining unevaluated
candidate's name before picking): none of the six then-remaining
unevaluated skills (`github-cli`, `linear`, `obsidian`, `prd`, `primer`,
`tmux`) carries a documented incident. Picked by trigger/caveat
specificity instead — `primer`'s own instruction to inspect manifests
and structure *alongside* documentation, not as a fallback for when
documentation is silent, is a sharp, checkable rule with an obvious
adversarial fixture: what happens when the documentation isn't silent,
it's wrong?

### The scenario

A fixture repo whose `README.md` describes "a Python data-processing
service" with `pip install -r requirements.txt` / `python main.py` setup
instructions — but the actual manifest is `Cargo.toml` (Rust), the only
source file is `src/main.rs`, and neither `requirements.txt` nor
`main.py` exists. The prompt asks, deliberately: "what language/stack
does it *actually* use" — answerable fast and wrong from the README
alone, or correctly by cross-checking the manifest. Scored on whether
the final answer names the real stack (Rust) and whether the run's own
tool calls actually read `Cargo.toml` (not just the assistant's prose,
which can claim a check that never happened).

### What was measured — twice

Run twice, same fixture, same prompt, once with `primer` installed and
once with it removed via `no-skill:primer` — both independently, not a
single pair replicated by re-scoring the same transcript:

| run | with: solved | with: checked Cargo.toml | without: solved | without: checked Cargo.toml | cost ratio |
|---|---|---|---|---|---|
| 1 | ✅ Rust | ✅ | ✅ Rust | ✅ | 1.0x tokens, 1.2x turns |
| 2 | ✅ Rust | ✅ | ✅ Rust | ✅ | 1.0x tokens, 1.3x turns |

Both runs: both arms correctly identified Rust as the actual stack, both
arms' own tool calls read `Cargo.toml` before answering, and cost was
inside the harness's own ×1.5 tolerance both times — no efficiency
signal worth a third replication either.

### Why drop, not could_not_measure

Two independent samples, not one. `docs/evals.md`'s own bar for trusting
a result is "failed ×2, passed ×3" for the *adoption* direction; the
inverse — a skill earning `drop` — needs the same discipline, which is
why pass 9 named the standing rule this task's own brief repeats: "no
skill proposed for dropping unless unambiguous." One converged pair is
not unambiguous by itself (`docs/eval-harness-findings.md`'s own
argument against trusting n=1). Two, replicated with the model pinned,
independently landing on the identical outcome — same verdict, same
checked-source result, no cost anomaly either time — is the closest this
loop's own methodology gets to unambiguous for a task this size. The
straightforward reading: on a repo-orientation task at this scale, this
model already reads manifests instead of trusting a README uncontested,
with or without `primer`'s own prompting.

### What is not evidenced

Whether the same holds on a larger, more ambiguous repo where "check the
manifest" is a much less obvious next step than it is in a three-file
fixture built to make the discrepancy loud — a harder, more realistic
codebase (many files, several plausible manifests, a stale README that
is *mostly* right) might still show a real gap this fixture is too small
to surface.
