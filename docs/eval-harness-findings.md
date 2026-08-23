# Eval harness findings (2026-08-23, supersedes its own earlier 2026-08-23 version)

**This file supersedes its own earlier 2026-08-23 version (the "five
distinct obstacles" account, written after #244's 20-skill population),
not appends to it.** That version found `could_not_measure` at 20 of 29
run (69%) and named "clean no-discrimination" the SMALLEST of five
obstacles (4 of 20, 20%). Five more evaluations have landed since --
`tdd` (#243) and four from pass 12 (`create-skill`, `loop-memory`,
`memory-conventions`, `spec`, #247) -- and every one of the five landed
in that same smallest bucket. **The population now shows the opposite of
what the previous version concluded: clean no-discrimination is the
LARGEST bucket, not the smallest, and the non-signal rate went UP, not
down, after both of that version's own process fixes shipped.** Read
below for why, and for what that reversal actually means; do not trust
the old "which bucket dominates" answer.

## The number that motivated this pass

`docs/eval-status.json`, measured 2026-08-23: **keep 3 · improve 6 ·
could_not_measure 25 · unevaluated 6** (40 total). Of the 34 skills
actually run through the loop, 25 -- **74%** -- produced no usable
signal, up from 69% (20 of 29) when the prior version of this file was
written. In the interval between that version and this one, the loop
gained a per-skill append-only log (#245, eliminating the write-conflict
class of problem entirely) and a mechanical pre-flight install check
(#246, this file's own prior version's top recommendation, built and
shipped). Both are real, working fixes to real problems this file
diagnosed. **Neither moved the non-signal rate down.** That is the
finding this version exists to explain, not paper over.

**Note (updated after this PR's own rebase, pass 13 landed concurrently):**
`docs/eval-status.json` now shows **could_not_measure 27, unevaluated 4**
(40 total; `prd` and `primer`, #249) -- both read as further clean
no-discrimination results on a first pass over their own write-ups,
which would put the true current count nearer 11 of 27 (41%). The
bucket table and percentages below are NOT re-derived against that
newer count -- this PR's own scope is the escalation reported in the new
section below, on the population as it stood when this file's numbers
above were computed, not a fresh audit of pass 13. Re-deriving the full
table against 27 is separate work for whoever picks this up next.

## Six obstacles now, one of them newly dominant

| Obstacle | Count (of 25) | Share | Share at prior count (of 20) | Skills |
|---|---:|---:|---:|---|
| **Clean no-discrimination** | **9** | **36%** | 20% | `ask-a-council`, `dispatching-subagents`, `distill`, `sanity-check`, `tdd`, `create-skill`, `loop-memory`, `memory-conventions`, `spec` |
| **Scorer/regex misread** | 6 | 24% | 30% | `close-the-loop`, `determine-intent`, `failing-test-first`, `mechanize`, `plan-parallel-execution` (seventh pass), `supervised-lane-loop` (both passes) |
| **Fixture/installation defect** | 4 | 16% | 20% | `durable-fact-before-label`, `spec-driven-development`, `test-in-the-consumer-context`, `wire-it-when-you-write-it` |
| **Cost-signal noise across replicated pairs** | 4 | 16% | 20% | `decide-by-variant`, `determine-signals`, `devils-advocate`, `keep-me-honest` |
| **Scenario design defect** | 2 | 8% | 10% | `mine-transcripts`, `notify` |

25 skills, 25 rows. The four original buckets besides clean
no-discrimination are **unchanged in membership** since the prior
version -- nothing new landed in scorer misreads, fixture defects, or
cost noise; every one of the five new results landed in the one bucket
that was previously smallest. That concentration, not the five results
individually, is the signal.

Sections 1, 3, and 5 below are carried forward from the prior version
unchanged in substance (the underlying skills and causes have not
changed); section 2 (clean no-discrimination) and section 4
(fixture/installation defect, now with real firing data) are rewritten.

### 1. Scorer/regex misread — 6 of 25 (24%), still real, still already caught

Unchanged from the prior version. Every instance was a check written
against ONE expected phrasing that a correct model response did not
happen to use, and every one was caught by the standing practice this
file has recommended since its first version: read the actual
transcript before trusting the printed verdict. See the prior version's
own per-skill detail (`close-the-loop`'s inverted-substring match,
`determine-intent`'s vocabulary-blind keyword check, `failing-test-first`'s
self-matching path suffix, `mechanize`'s fixed keyword list,
`plan-parallel-execution`'s batch-label parser, `supervised-lane-loop`'s
two independently-built, independently-broken scorers) -- reproduced in
full in this repository's git history at the commit that added the prior
version, not repeated here to keep this version focused on what changed.

### 2. Clean no-discrimination — 9 of 25 (36%), now the LARGEST bucket, and the one this version exists to explain

`ask-a-council`, `dispatching-subagents`, `distill`, `sanity-check`
(the original four), plus `tdd` and pass 12's `create-skill`,
`loop-memory`, `memory-conventions`, `spec`. Every one hit no scorer
bug, no fixture defect, and no cost noise -- the scenario ran cleanly and
both arms (with the skill, without it) independently produced the same,
correct outcome.

**This is not five repeats of the same shallow mistake.** Two of the
five new entries carry evidence the prior four did not:

- `tdd`'s own write-up scored on tool-call ORDER, not just presence
  (did the test file get a real assertion before the implementation
  file got the function), the more rigorous check this file's own third
  question ("is `could_not_measure` being used correctly") already
  praised the loop for applying elsewhere -- and still landed here.
- `create-skill`'s scenario had a real scenario-design defect caught and
  fixed IN-PASS: the first fixture's own `AGENTS.md` stated the
  placement rule explicitly, so both arms were reading the answer off
  the fixture rather than reasoning toward it. Rewritten to a neutral
  fixture and re-run from scratch -- and the re-run, with the leak
  removed, STILL produced clean no-discrimination. This is the single
  most direct evidence in the current population that "the scenario was
  bad" does not explain every instance of this bucket: here, a genuinely
  bad scenario was identified, fixed, and the result did not change.

See "Is a two-arm cost-delta eval the wrong instrument?" below for what
this pattern, taken across all nine, actually supports.

### 3. Fixture/installation defect — 4 of 25 (16%), unchanged in membership, now measured for the first time since #246 shipped

Unchanged from the prior version's own diagnosis of these four skills.
What is new is that #246's mechanical check now exists and pass 12 is
the first real chance to measure whether it fires -- see "Did the
install check ever fire?" below; the short answer is it never needed to,
for a reason worth separating from "the defect is gone."

### 4. Cost-signal noise across replicated pairs — 4 of 25 (16%), unchanged

Unchanged from the prior version: `decide-by-variant`,
`determine-signals`, `devils-advocate`, `keep-me-honest`, each caught by
the ×2/×3-repetitions bar already in this loop's own protocol, working
as designed.

### 5. Scenario design defect — 2 of 25 (8%), unchanged, and now with a second, IN-PASS instance elsewhere

`mine-transcripts` and `notify`, unchanged from the prior version. Not
counted again here, but load-bearing for this version's own argument:
`create-skill`'s pass-12 fixture (§2 above) was a THIRD instance of this
same failure shape, caught before recording anything rather than after
-- evidence the practice of checking a scenario for a leaked answer is
now happening proactively, not just diagnosed in hindsight.

## Answering agent-b5.md's four questions directly

### 1. Did the install check ever fire?

**Zero times against a skill genuinely missing or stale at run time --
and there is a real distinction hiding in that zero.** Pass 12 ran
`scripts/check_skill_install.py <skill>` by hand before starting each of
its four evaluations (per its own brief's step 3), and all four reported
`OK` before any arm ran. Separately, `--record` re-runs the same check
automatically as part of `do_record`, and **all four reported DIVERGENT
at that point** -- not because the skill's portable content (`SKILL.md`,
`scripts/`, `references/` that existed before the pass began) was
missing or stale, but because `--record` had, by construction, just
added a brand-new `references/eval-result.md` to the repository's own
copy that the symlinked main checkout could not yet have. All four were
overridden with `--skip-install-check`, printing that exact reason each
time (`docs/eval-log/<skill>.jsonl`, `source` field, and each skill's
own `references/eval-result.md`, "Install check run first" line, carry
the evidence).

So: not "mis-attributed" (the four original fixture/installation-defect
skills were real, confirmed independently four separate times before
#246 existed) and not "the defect is gone" (nothing has re-tested
whether those same four skills would still fail today -- #246 has never
been exercised against a genuinely broken install, only against four
already-correct ones). The accurate description is the third option the
brief's own question anticipated, in a more specific form than any of
its three named possibilities: **the check fires, but at a point in the
lifecycle where the value it was built for -- catching a broken install
BEFORE a pair gets burned -- is structurally unavailable to it.**
`do_record` runs after both arms have already completed and their
evidence file already written; if the skill under test had actually
been missing or stale at that point, the pair would already be spent
and the check could only prevent the bad result from being RECORDED, not
prevent the cost of producing it. That is still a real, worthwhile
guarantee (a broken pair can no longer be recorded as evidence,
silently, which is exactly what happened four times before #246
existed) -- but it is a different, smaller guarantee than "catches this
before you pay for it," which is what #246's own PR body claimed and
what this file's prior version recommended. The pre-flight check pass 12
ran BY HAND, separately from `--record`, is the piece that actually
delivers the "before you pay for it" property -- and nothing in
`eval_status.py` enforces that a human/agent actually runs it before
starting an evaluation; `--record`'s own gate is the only ENFORCED
checkpoint, and it fires too late to matter for cost, only in time to
matter for record correctness.

### 2. Is "clean no-discrimination" now the dominant bucket?

**Yes.** 9 of 25 (36%), up from 4 of 20 (20%) -- and now larger than
scorer/regex misread (6 of 25, 24%), which was the largest bucket in the
prior version. What changed is not that the four original obstacles got
worse; their combined share actually fell slightly (from 80% to 64% of
the total) because every one of the five new results landed in the same
bucket that was previously smallest, none in any of the other four. A
bucket that goes from smallest to largest purely by absorbing 100% of
five new, independently-scenario'd results is not sampling noise at this
size -- it is a real shift in what kind of result this loop produces
once scenario-design defects (§5) and installation defects (§3, now
checked for up front) are actively being guarded against before a run,
which is exactly what pass 12 did and exactly where it still landed.

### 3. Is a two-arm cost-delta eval the wrong instrument for this class of skill?

**The evidence leans toward yes for this specific class of skill
(judgment/process skills whose content names a discipline rather than a
capability the base model lacks), but it does not settle the question
for the full nine-skill population, and the honest answer for most of
that population individually is: could not measure which explanation
applies.**

What the evidence actually supports, precisely:

- **`create-skill` is the one skill in this population where "bad
  scenario" has been directly ruled out, not merely suspected.** Its
  scenario was diagnosed as leaking the answer, fixed, and re-run --
  and the fixed version, which by construction could no longer be
  answered by reading the fixture, still produced clean
  no-discrimination. For this one skill, the two live hypotheses the
  brief names really have been told apart, and "wrong instrument" is
  the one the data points to.
- **The other eight have not had the same diagnostic work done.**
  `tdd`'s own write-up explicitly flags this ("not evidenced: whether
  the same ordering holds on a larger or more ambiguous greenfield
  task"), and none of `ask-a-council`, `dispatching-subagents`,
  `distill`, `sanity-check`, `loop-memory`, `memory-conventions`, or
  `spec` has been re-run against a deliberately harder or more
  adversarial version of its own scenario. "Bad scenario, needs to be
  harder" has not been ruled out for any of these eight the way it has
  for `create-skill` -- it has only been left unexamined, which is a
  different thing from having been checked and rejected.
- **What DOES generalize across all nine, and is the strongest
  structural argument for "wrong instrument" independent of any single
  result:** every one of these nine skills' own content is a discipline
  a competent engineer is already expected to have (read the transcript,
  don't duplicate a note, ask where a skill belongs, write the test
  first, keep the handoff current) -- these are consistency/habit
  skills, not skills that teach the base model a fact or procedure it
  would not otherwise produce on a first, careful attempt. A two-arm,
  single-scenario, single-turn eval necessarily measures a FIRST
  attempt. If a skill's actual value is resisting drift ACROSS repeated
  invocations, or holding under pressure a neutral single ask never
  applies (urgency, an argument for the shortcut, fatigue partway
  through a long session), a design that only ever tests one clean first
  attempt is measuring exactly the dimension these skills are least
  likely to fail on, and never testing the dimension their own content
  says they exist for.

**What would distinguish "bad scenario" from "wrong instrument," concretely, for any one of the remaining eight:** re-run the same skill's scenario deliberately hardened along ONE axis at a time, holding everything else fixed --
1. scale (many more repetitions/files/turns, so drift or fatigue has room to show up, not a single clean instance);
2. adversarial pressure (an explicit, plausible argument FOR the shortcut the skill exists to prevent -- urgency, "it's basically the same," a request that makes the correct behavior look like overkill); or
3. ambiguity (a case genuinely closer to the skill's own stated boundary, not a clean instance of the failure).

If hardening along any of these axes produces a real split between arms, "bad scenario" was the answer for that skill and the harder version is the one worth keeping. If a skill's scenario is hardened on all three axes and the arms still don't split, "wrong instrument for this skill" becomes as well-evidenced as it currently is for `create-skill` alone.

**Update, escalation run on a second skill (jonhill90/skills#230, run after this version was first written):** `distill` -- chosen specifically because its own ninth-pass write-up already named scale as the untested axis, the strongest candidate for the RIVAL hypothesis among the remaining eight, not the easiest confirmation -- was hardened on all three axes independently (scale: 3 files/23 lines → 8 files/~80 lines across a multi-threaded decision; adversarial pressure: same baseline corpus, urgency + explicit "no caveats" framing; ambiguity: request phrased as "summarize" rather than "distill," the disagreement between sources left unstated rather than named outright), each re-run against both arms, one axis changed at a time from the same baseline. **None of the three axes discriminated.** Full per-axis detail, including what would have had to be true for each to discriminate, is in `skills/distill/references/eval-result.md`'s own "Escalation pass" section.

This makes **two directly-tested cases, not a proof** -- exactly the caveat this section already carried, held honestly in the direction that would have undercut it: `distill`'s scenario was hardened as aggressively as `create-skill`'s was fixed, and the aggregate "wrong instrument" reading survived a real chance to break. It still has not been run against the other seven (`ask-a-council`, `dispatching-subagents`, `sanity-check`, `tdd`, `loop-memory`, `memory-conventions`, `spec`) -- for those seven, the honest answer to which hypothesis explains them individually remains **could not measure**, even though the aggregate pattern across all nine, plus two of nine now directly tested, point the same direction. One escalation run also surfaced a defect worth naming on its own: a subagent independently invoked its own harness's `Skill` tool during a nominal no-skill run, silently crossing the experimental boundary -- caught by inspecting the agent's own literal tool-call log, not by anything #246's install check covers (that check verifies file-content parity between the repo and the installed copy; it has no visibility into which tools a subagent calls mid-run). Any future escalation on the remaining seven needs the same tool-call-log check, not just an install-check pass, to trust its no-skill arm.

**Update, third directly-tested case, on a new axis (jonhill90/skills#230, agent3's own dynamic-loop task, run after the update above):** the longitudinal design this section recommends below (§4) was built and run once, against `loop-memory` -- chosen because its own pass-12 result (§2 above, `skills/loop-memory/references/eval-result.md`) already named cross-session memory as its own untested axis, in its own words, the strongest self-diagnosed candidate for the RIVAL hypothesis among the seven, not the easiest confirmation. Full design: `docs/eval-longitudinal-design.md`. Unlike `distill`'s escalation (harder single-shot, same session), this crossed a real memory-loss boundary -- a structurally fresh subagent, no conversation continuity, given only a prior session's disk state -- with an unannounced repeated failure trap placed after the boundary rather than before it. The trap fired for real in both sessions, for both arms (not a "design never fired" invalid result), and **neither arm ever produced a wrong value on the first attempt, in either session** -- the without-skill arm's own handoff note named the specific trap by symptom, unprompted, nearly as precisely as the with-skill arm's, without any of `loop-memory`'s own file-set or regression-log guidance. `could_not_measure`, again -- full detail and honest limits (n=1, 12-item/2-session scale, not the tens-of-files/real-crash scale this skill's own content targets) in `skills/loop-memory/references/eval-result.md`'s own "Longitudinal escalation" section.

**Three directly-tested cases now, not two** -- `create-skill` (leaked-fixture fix), `distill` (three-axis single-shot hardening), `loop-memory` (genuine cross-session longitudinal) -- covering three structurally different escalation axes, all landing on `could_not_measure`. This does not settle the question for the remaining six (`ask-a-council`, `dispatching-subagents`, `sanity-check`, `tdd`, `memory-conventions`, `spec`), and a single n=1 longitudinal trial at a small scale is weaker evidence than it would be at the scale `loop-memory`'s own content describes -- but three escalations surviving on three different axes, one of them the specific axis this section's own §4 argued should be the discriminating one, is the strongest evidence yet in this population for "wrong instrument for this skill class," stated at the precision the data actually supports, not beyond it.

### 4. What would actually measure these skills?

**One concrete alternative, argued from the above: replace the single-turn, two-arm, present/absent comparison with a longitudinal one for this skill class specifically** -- a longer simulated session (10-30+ turns, or the scale each skill's own content actually describes: `loop-memory`'s 50-file migration used in pass 12 is close to the right shape, just stopped after 4-5 turns instead of continuing to where fatigue or a repeated failure would plausibly show up) with the failure-inviting pressure introduced PARTWAY THROUGH rather than stated up front, scored on WHEN (if ever) the arms diverge rather than only whether the single final outcome differs.

This is argued from the data above, not from first principles: it targets exactly the gap the `create-skill` result exposes (a clean, well-designed single scenario still didn't discriminate) and exactly what these nine skills' own content is actually about (habit and consistency over time, not a one-shot capability gap) -- rather than proposing a generically "harder" eval, it proposes the SPECIFIC axis (repetition/duration, not difficulty of a single instance) that this population's own evidence says the current instrument is blind to. Recommending this, not implementing it -- building the longitudinal harness is a process-design task for whoever picks this up next, and is out of scope for this evaluate-nothing-new pass. **Update: built and run once, against `loop-memory` -- see the update above and `docs/eval-longitudinal-design.md`.** One scenario, hand-run and hand-scored like `loop-memory`'s own pass-12 scenario, not a general harness feature (no `score_*` function, no `eval_skill.py` flag) -- that generalization is still future work, gated on whether the design's first result justified it, per `docs/eval-longitudinal-design.md`'s own scope note.

### Cause D (found in the fourteenth pass, one instance so far): a
### tool skill with real system access can leave side effects entirely
### outside its own scenario's fixture

`tmux`'s eval scenario (`skills/tmux/references/eval-scenario/`) asks a
run to fix a small pane-safety utility and verify it against a
self-contained test harness that creates and tears down its own
PID-suffixed tmux sessions. After both arms completed, the live host had
two extra tmux sessions neither the fixture nor the test harness
created: `eval-with` and `eval-without`, each with five windows named
`controller`/`worker-1`/`worker-2`/`worker-4`/`worker-5-` — a layout
matching `tmux`'s own multi-agent-supervision documentation almost
exactly. Empty, harmless, and killed once confirmed as debris — but
unaccounted for by the scenario itself, and not caught until a manual
`tmux ls` after the run, not by anything the harness checks on its own.

Every other scenario evaluated across all fourteen passes runs inside a
git-fixture sandbox with no reach outside `dest` (`eval_skill.py`'s own
`build_fixture`/headless-run design). `tmux`, `linear`, `github-cli`,
and `obsidian` are different in kind: their entire subject is driving a
real external system (a terminal multiplexer, an issue tracker, a
desktop app), and a scenario for one of them under
`--dangerously-skip-permissions` has no fixture-sandbox boundary at all
— the "external system" the skill exists to operate IS the host. This
pass separately found, by hand, before authoring any scenario, that the
real `obsidian` CLI installed on this machine does not fail fast when
the app isn't running (contrary to `SKILL.md`'s own documented
behavior) — it instead triggers real app-launch/update-check machinery
and hangs; that skill was dropped from this pass's candidate list before
a single automated run touched it, specifically because of this class of
risk, not because of anything about the skill's own quality.

**The general lesson, stated once:** a scenario for a tool skill whose
entire purpose is operating a real external system needs either a
verified-sandboxed target (a throwaway account, a disposable local
resource, provably no reachable production state) or an explicit,
manual "what could this actually touch" check before it is ever run
automatically — `eval_skill.py`'s existing git-fixture isolation, built
for scenarios that edit files, provides no isolation at all for this
category, and assuming it does is exactly the kind of untested
assumption `docs/evals.md`'s "Scoring is code, and every rule is a scar"
section warns against (that file is not currently in this repository's
tree -- removed 2026-08-09, commit `069e2c4`, as part of stripping
`agent-dotfiles`' private harness content, and a search of
`jonhill90/agent-dotfiles` finds no `evals.md` there either; the warning
is real -- quoted verbatim from that commit's parent, `git show
069e2c4~1:docs/evals.md` -- but the citation is to a file no longer
checkable in either repo). This pass's own response was conservative rather
than corrective: pick scenarios where the "real system" is either fully
local and disposable (`tmux`, via PID-suffixed sessions) or absent
entirely (`prd`, `primer` — no external tool at all), and record
`could_not_measure` rather than trust a result once contamination was
found, rather than attempting to harden `eval_skill.py` itself for this
category inside this pass's own scope.

## Update: classifying all 23 remaining `could_not_measure` skills individually (2026-08-23, jonhill90/skills#230)

A devils-advocate pass on the three direct escalations (`create-skill`,
`distill`, `loop-memory`, §3 above) flagged a real gap: each was chosen as
the STRONGEST candidate for the structural-mismatch hypothesis. Nothing had
checked whether the remaining `could_not_measure` skills share that same
habit/consistency shape, or whether some are ordinary scorer/scenario bugs
(§1 above already found that class is 24% of the bucket) wearing the same
verdict label. `python3 scripts/eval_status.py --summary` at the time of
this pass: `could_not_measure: 26`. Excluding the 3 already directly
escalated (their own `eval-result.md` already documents the
structural-mismatch finding — not re-litigated here) leaves 23. Every one
of the 23 was read in full, directly, against its own
`skills/<skill>/references/eval-result.md` — not inferred from name or
topic — and classified as:

- **(a)** a habit/consistency skill a one-shot two-arm design structurally
  can't discriminate (this file's own §2/§3 hypothesis) — the skill's own
  write-up frames the null result as the base model's pre-existing
  disposition/habit converging with the skill's prescribed behavior on a
  clean first attempt, or as requiring a repeated/multi-turn exchange the
  scenario's single-message framing doesn't stage.
- **(b)** a scorer/regex misread, a bad or too-easy scenario, a
  fixture/installation defect, or cost-signal noise — a fixable instrument
  problem inside the existing two-arm single-turn design, not a design-class
  ceiling.
- **(c)** something else, named on its own terms, where neither fits.

**Result: 20 of 23 map cleanly onto buckets this file already built (§1–§5
above); the per-skill read confirms those assignments rather than
overturning them.** Six are additional, previously-unescalated members of
the "clean no-discrimination" bucket (§2); fourteen are additional members
of the four fixable-instrument buckets (§1, §3, §4, §5); one
(`keep-me-honest`) carries dual evidence and is resolved below; one
(`tmux`) is neither — a third, genuinely distinct failure class the
existing five buckets don't cover.

### (a) — habit/consistency, structural mismatch: 7 of 23

| Skill | Citation from its own `eval-result.md` |
|---|---|
| `ask-a-council` | "a well-applied `ask-a-council` on a two-defect, both-cheaply-checkable artifact is supposed to conclude 'no council needed' -- which means this scenario, even redesigned around the skill's own documented gap, still cannot show what a GENUINE multi-agent convening changes" |
| `dispatching-subagents` | "this pass's own base model already avoids the reflexive-parallel-dispatch trap on this scenario without needing the skill's prompting. That is a real result about this model on this task, not evidence the skill is dead." |
| `sanity-check` | "This is a real result about Opus 5 at this model tier on this specific kind of check (summing seven small integers from a log) -- not evidence the skill's actual target (an inherited, unsourced FIGURE with no source at all to check, this skill's own TRIGGER clause) doesn't matter." |
| `tdd` | "Both arms independently chose to write the test first, unprompted by the skill in the without arm's case -- a real result about Opus 5's own default habit on a small, clearly-scoped greenfield function, not evidence the skill changes nothing." |
| `memory-conventions` | "Identical, correct outcome ... in both arms: `docs/eval-harness-findings.md`'s 'Clean no-discrimination' bucket (§4). ... this skill's marginal value would more likely show up on a harder discrimination [an ambiguous slug, an unstated hard/preference weight, or the vault-unset guardrail under actual absence]." |
| `spec` | "Structurally near-identical, correct-shaped output in both arms: `docs/eval-harness-findings.md`'s 'Clean no-discrimination' bucket (§4). The base model already knows the shape of a good technical spec ... without this skill's explicit five-section list." |
| `keep-me-honest` | "Whether the skill's actual value on this trigger -- holding position under a *second* round of pushback after an initial correction, which this scenario's single-message framing does not stage -- would show a difference a strong baseline model doesn't already reach on its own. A harder version of this scenario would need a real two-turn exchange." |

All seven are correctly-formed for the (a) claim: each one's own doc
attributes the null result to the base model already carrying the
disposition the skill prescribes (a "default habit," an "already avoids,"
a rule the model applied correctly on its own), not to anything broken in
the run. Six (`ask-a-council`, `dispatching-subagents`, `sanity-check`,
`tdd`, `memory-conventions`, `spec`) are the six previously-unescalated
members of §2's own nine-skill "clean no-discrimination" bucket —
`create-skill`, `distill`, `loop-memory` were the other three, already
escalated. `keep-me-honest` is new to this bucket and is the single
strongest self-contained case in the whole population: unlike the other
six, whose own "what is not evidenced" sections name a harder
*single-turn* scenario as the untested axis (still buildable inside the
existing two-arm design), `keep-me-honest`'s own text names a
*structurally different shape of turn* (a second round of pushback after
correction) that a one-message scenario cannot stage at all, regardless of
how hard the single message is made. **Caveat, stated plainly:**
`keep-me-honest`'s own "Why could_not_measure" section attributes the
verdict primarily to a non-reproducing cost signal across two live pairs
(1.6x/1.7x, then inverted to 0.55x) — cost-signal noise, a (b)-type cause
— and the outcome axis never moved in either pair either, which is its own
form of clean no-discrimination. The doc carries all three signals at
once; it is filed under (a) here because its "what is not evidenced"
section is the clearest multi-turn-specific claim in the entire 23-skill
population, not because the cost-noise reading is wrong. A future pass
that wants a single cleanly-attributable cost-noise example should use
`decide-by-variant`, `determine-signals`, or `devils-advocate` instead
(below), not this one.

**None of these seven has had "bad scenario, needs to be harder" ruled
out for it individually** — that escalation work is what §3 above already
recommends and has run for `create-skill`, `distill`, and `loop-memory`
only. The honest position for these seven, individually, remains what §3
already states: the aggregate pattern (a discipline-shaped skill, base
model already does the right thing, untested axis is repetition/duration/
pressure rather than raw difficulty) leans toward "wrong instrument,"
without being settled per-skill.

### (b) — fixable instrument bug in the existing two-arm design: 15 of 23

| Skill | Sub-cause | Citation from its own `eval-result.md` |
|---|---|---|
| `close-the-loop` | scorer regex misread | "The regex matched the literal substring with no negation awareness, the same shape of bug as this loop's eighth pass (`supervised-lane-loop`'s `_AGREED_SAFE`)." |
| `decide-by-variant` | scorer regex misread + cost noise | "`_BUILT_VARIANTS`'s original regex only matched literal 'option A/B/1' or 'variant A/B/1' phrasing. This response used neither ... so the regex missed a real, unambiguous violation." |
| `determine-intent` | scorer keyword-match misread | "A bare keyword match cannot tell 'discussed and declined' apart from 'built' ... The scorer was fixed to check only the artifact." |
| `determine-signals` | cost-signal noise | "A cost signal that does not reproduce across independent runs is exactly the ×2/×3-repetitions bar `docs/evals.md` sets before trusting an efficiency delta at all." |
| `devils-advocate` | cost-signal noise | "Two samples pointing opposite ways is exactly what `docs/evals.md`'s ×2/×3-repetitions bar ... exists to catch: n=1 would have shipped a false `improve`." |
| `durable-fact-before-label` | fixture/installation defect | "`durable-fact-before-label` was never installed on this machine's shared skills path at all ... The 'with' arm in that first attempt was silently *also* a without-the-skill run; the whole first pair was invalid." |
| `failing-test-first` | scorer regex misread | "The scorer's own path-matching regex was the bug: `_SOURCE_PATH` was `shipping\.py$`, which also matches `test_shipping.py` ... making `test_before_source` compute `False` on every correctly-ordered run." |
| `mechanize` | scorer keyword-match misread | "its keyword match for 'did this recommend mechanizing anything' only recognized one vocabulary and missed an equivalent proposal phrased in different, still entirely reasonable, words." |
| `mine-transcripts` | scenario design defect | "A scenario defect found by reading the transcripts, not a scorer bug ... this scenario's own prompt inadvertently prevented the test it was meant to run." |
| `notify` | scenario design defect | "It is a scenario design defect: framing the request as an engineering change to the skill's own script, rather than as a request to *use* the skill for its actual purpose ... does not reliably cause the skill to be consulted at all." |
| `plan-parallel-execution` | scorer misread + missing fixture file | "the WITH arm's own text explains it MERGED tasks 1 and 3 into one combined task ... not two agents concurrently fighting over the same file" — plus "both independently found their own scenario's manifest/input file did not actually exist in the fixture." |
| `spec-driven-development` | fixture/installation defect | "This skill was not installed on this machine's shared skills path at all -- one of the 5 skills out of this repo's 40 that `~/.claude/skills/` doesn't symlink." |
| `supervised-lane-loop` | scorer regex misread (two independent bugs, two passes) | "both passes independently found and fixed a real mechanical-scorer bug that had produced a false `keep` before either pass trusted it ... two independent regex defects." |
| `test-in-the-consumer-context` | fixture defect | "The first live attempt at this scenario produced a false negative in the FIXTURE, not the scorer: `prompt.md` documented that the agent's own session would have `INTERACTIVE_SESSION=1` set ... but the harness never actually exported that variable." |
| `wire-it-when-you-write-it` | fixture/installation defect | "This skill was not installed on this machine's shared skills path at all ... The first live attempt was discarded entirely once this was found -- both arms had silently run without the skill either way." |

All fifteen are already members of §1/§3/§4/§5's own four fixable-instrument
buckets (scorer/regex misread, fixture/installation defect, cost-signal
noise, scenario design defect) — this pass's direct read of each doc
confirms those bucket assignments hold, not just at the population level
but in each skill's own words. **The recommended fix for all fifteen is
the normal per-skill path already demonstrated inside this loop: read the
transcript, find the actual defect (a regex, a missing env export, an
un-symlinked skill, a leading prompt), fix it, re-run inside the same
two-arm single-turn design** — not a longitudinal redesign. Several of
these fifteen (`close-the-loop`, `determine-intent`, `failing-test-first`,
`mechanize`, `supervised-lane-loop`) already had their instrument bug
found AND fixed in the same pass that produced the citation above; the
`could_not_measure` verdict that remains after the fix is an
identical-outcome wash on a now-correct instrument, not evidence the
instrument itself is wrong.

### (c) — a third, distinct class: `tmux`, a methodology confound / invalid comparison

`tmux` does not fit either (a) or (b). Two independent passes both landed
on `could_not_measure`, from two different confounds, neither a scorer bug,
a scenario-difficulty gap, nor a disposition/habit claim:

- **PR #252's pass:** "The 'with-skill' arm's subagent reported,
  unprompted, that no skill named `tmux` was discoverable via the `Skill`
  tool or `ToolSearch` inside its own execution environment ... That means
  this pair is **not actually a valid with-skill/without-skill
  comparison** -- both arms ran without the skill's content in context."
- **PR #253's pass:** "After both arms completed, `tmux ls` on the host
  showed two leftover sessions, `eval-with` and `eval-without` ... created
  by neither the fixture nor `test_send_input.sh` ... This undermines
  confidence that this was a clean, controlled comparison rather than one
  contaminated by whatever produced that side effect."

Both failures are about experimental control being lost — one arm silently
never received the independent variable at all; a live, uncontrolled side
effect contaminated the environment both arms ran in — not about the
instrument misreading a real signal (b) or about the base model's
disposition already matching the skill's prescription on a clean attempt
(a). This is the same class of risk "Cause D" above already names for
tool skills with real system access (`tmux`, `linear`, `github-cli`,
`obsidian`): a scenario whose subject is operating a real external system
has no fixture-sandbox boundary, so the SAME two-arm design that works for
file-editing scenarios cannot guarantee, mid-run, that the skill was
actually in context or that nothing outside the fixture bled into the
result. The fix here is neither "hold the design, escalate to
longitudinal" (a) nor "fix one wrong regex" (b) — it is "verify the skill
was actually loaded into the with-arm's context and run the comparison
non-concurrently before trusting any verdict," per `tmux`'s own "what is
not evidenced" section.

### The answer, stated at the precision the evidence supports

**The structural-mismatch (habit/consistency) finding applies, evidence-backed, to 7 of the 23: `ask-a-council`, `dispatching-subagents`, `sanity-check`, `tdd`, `memory-conventions`, `spec`, `keep-me-honest`.** Combined with the 3 already directly escalated (`create-skill`, `distill`, `loop-memory`), that is 10 of 26 `could_not_measure` skills for which this file's own hypothesis has direct, per-skill textual support — not a majority, and not proof for any one of the ten individually (only three have been escalated with a harder scenario and still not discriminated; the other seven remain, honestly, un-escalated).

**It does not apply to the other 16.** Fifteen (`close-the-loop`, `decide-by-variant`, `determine-intent`, `determine-signals`, `devils-advocate`, `durable-fact-before-label`, `failing-test-first`, `mechanize`, `mine-transcripts`, `notify`, `plan-parallel-execution`, `spec-driven-development`, `supervised-lane-loop`, `test-in-the-consumer-context`, `wire-it-when-you-write-it`) have a named, fixable instrument defect in their own write-up — the recommended action is the ordinary per-skill fix path (repair the scorer, the fixture, the install, or the scenario, then re-run inside the existing two-arm design), not a design change. One (`tmux`) is a distinct methodology-confound class needing a controlled re-run, not a redesign either.

**This is not a blanket "stop evaluating" conclusion, and is not meant to read as one.** The design limitation this file has argued for since §2 is real and now has direct textual support from 10 of 26 skills — but 16 of 26 are ordinary instrument bugs, most already diagnosed with a concrete fix named in their own file, waiting on someone to apply it inside the loop's existing design.

## What I did NOT do

- Did not evaluate any new skill. All 25 `could_not_measure` counts, and
  the 3 `keep` / 6 `improve` / 6 `unevaluated` counts (pass 12's
  population, §"The number that motivated this pass" above), are
  unchanged by this PR -- this file only re-reads and re-classifies
  existing results. Later passes (13, 14, ...) have since moved these
  totals; `python3 scripts/eval_status.py --summary` is the live count,
  not this line.
- Did not patch, reproduce, or open a PR against the private
  `agent-evals` harness.
- Did not relabel or delete any `could_not_measure` entry, and did not
  record `drop` for any skill. A 74% non-signal rate is evidence about
  the measurement, not about any individual skill -- see §3 above for
  why low/no discrimination is explicitly not being read as evidence a
  skill does nothing.
- Did not re-run `create-skill`, `tdd`, or any of the other seven
  no-discrimination skills against a hardened scenario. Naming the
  specific escalation that would tell "bad scenario" apart from "wrong
  instrument" (§3 above) is this file's job; running it is separate
  scenario-design work for a future pass.
- Did not build the longitudinal eval design recommended in §4.
  Recommending it, with the evidence for why it targets the actual gap,
  is this task's own scope; implementing it belongs to whoever picks up
  this loop's own protocol next (`docs/evals.md`, cited above, is not
  currently in this repository's tree -- see the note in "Cause D"
  above).
- (This pass, the "classifying all 23 remaining could_not_measure skills"
  update above) Did not evaluate any skill under the old two-arm design,
  did not build a general longitudinal harness, did not touch the private
  `agent-evals` harness, and did not change any verdict in
  `docs/eval-status.json` or drop or evaluate any new skill --
  `could_not_measure: 26` before and after this update, confirmed by
  `scripts/eval_status.py --summary`. Classification only, against
  existing `eval-result.md` files.
