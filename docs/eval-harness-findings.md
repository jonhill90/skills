# Eval harness findings (2026-08-23, supersedes 2026-08-22)

**This file supersedes its own 2026-08-22 version, not appends to it.**
That version named two causes from the first six `could_not_measure`
results. The population has since grown to 20 skills (22 independent
evaluations -- `plan-parallel-execution` and `supervised-lane-loop` were
each evaluated twice, by two different lanes, before either knew about
the other; both sub-evaluations are counted separately below since they
can, and sometimes do, hit different obstacles). **The two-cause account
does not hold at this sample size.** It undercounted by naming the
destination (both arms behave identically) as if it were the cause,
when the destination is nearly universal and what actually varies is
what got in the way of confirming that cleanly. Read below for the
corrected account; do not trust the old two-bucket table.

## The number that motivated this pass

`docs/eval-status.json`, measured 2026-08-23: **keep 3 · improve 6 ·
could_not_measure 20 · unevaluated 11** (40 total). Of the 29 skills
actually run through the loop, 20 -- 69% -- produced no usable signal.
Running the remaining 11 through the same loop unchanged would most
likely add roughly seven or eight more rows of nothing, at this rate.
Volume was never the constraint; the loop's own ability to discriminate
is, and this file exists to say precisely why, with counts, before
spending more passes finding the same five things one at a time.

## Five distinct obstacles, not two

Every one of the 22 evaluations below terminates in the SAME place:
both arms (with the skill, with it removed) behaved identically on the
scenario actually run. What differs, and what the original two-cause
account conflated with the destination itself, is what stood between a
human and confirming that cleanly. There are five distinct such
obstacles in the current population, not two:

| Obstacle | Count (of 20 skills) | Skills |
|---|---:|---|
| **Scorer/regex misread** (a keyword, regex, or heuristic check produced a WRONG verdict -- usually a false `keep` -- caught only by reading the actual transcript by hand) | **6** | `close-the-loop`, `determine-intent`, `failing-test-first`, `mechanize`, `plan-parallel-execution` (seventh pass), `supervised-lane-loop` (both passes) |
| **Fixture/installation defect** (the skill under test was not actually installed on the machine's shared skills path, or an environment variable the fixture claimed was set never actually was) — NEW, not named in the 2026-08-22 account | **4** | `durable-fact-before-label`, `spec-driven-development`, `test-in-the-consumer-context`, `wire-it-when-you-write-it` |
| **Cost-signal noise across replicated pairs** (outcome never differed; a token/turn delta looked like `improve` on one pair and inverted, vanished, or reversed on a second, independent pair) — NEW, not named in the 2026-08-22 account | **4** | `decide-by-variant`, `determine-signals`, `devils-advocate`, `keep-me-honest` |
| **Clean no-discrimination** (the scenario simply didn't separate the arms; no scorer bug, no fixture defect, no cost noise -- the original 2026-08-22 "Cause A" in its unconfounded form) | **4** | `ask-a-council`, `dispatching-subagents`, `distill`, `sanity-check` |
| **Scenario design defect** (the prompt's own wording pre-empted the very test it meant to run, or the skill was never actually invoked/consulted by either arm) — NEW, not named in the 2026-08-22 account | **2** | `mine-transcripts`, `notify` |

20 skills, 20 rows (each skill assigned to its dominant obstacle; three
skills hit more than one and are noted under their own heading below).

### 1. Scorer/regex misread — 6 of 20, the largest single bucket, and the one already-known cause that stayed dominant

This is the 2026-08-22 account's own "Cause B," and at the larger
sample it is confirmed as the single most frequent near-miss, not
merely a real one. Every instance is a check written against ONE
expected phrasing -- a literal string, an un-negated substring match, a
path suffix, a fixed keyword list -- that a real, correct model response
did not happen to use:

- `close-the-loop`: a regex matched the literal substring of a command
  the model named specifically to DECLINE inventing, not to run.
- `determine-intent`: a bare keyword match on rendering vocabulary
  couldn't tell "discussed and declined" from "built."
- `failing-test-first`: a path-suffix regex (`shipping\.py$`) also
  matched `test_shipping.py`, so ordering logic compared the test file
  against itself.
- `mechanize`: a fixed keyword list ("script"/"mechanize"/"automate")
  missed an equivalent proposal phrased as "classifier"/"detector" --
  this one COMPOUNDS with clean no-discrimination underneath it (see
  its own note below).
- `plan-parallel-execution` (seventh pass): a heuristic batch-label
  parser flagged a valid collision-resolution strategy (merging two
  tasks into one, run by a single agent) as a missed collision because
  it grouped two task numbers under one label.
- `supervised-lane-loop` (both passes, independently): the seventh
  pass's own scorer matched a QUOTED restatement of a claim being
  refuted as the model's own affirmation; the eighth pass's own scorer
  (built independently, by a different lane) missed a literal
  contraction ("can't fail" vs. "cannot fail") and separately matched
  "agree it's safe" inside "I **don't** agree it's safe" --
  negation-blind, the identical shape of bug in a scorer that had never
  seen the seventh pass's own fix.

**Every one of these six was caught, not missed** -- by the same
practice the 2026-08-22 account already recommended: read the actual
transcript before trusting the printed verdict. That practice is
working. The volume here says the practice needs to keep being followed
precisely because scorers keep having this shape of bug, not that it
has failed.

### 2. Fixture/installation defect — 4 of 20, NEW, and the more expensive obstacle of the two most common ones

Four skills -- `durable-fact-before-label`, `spec-driven-development`,
`test-in-the-consumer-context`, `wire-it-when-you-write-it` -- each lost
a real, paid-for first pair to the SAME root problem, discovered
independently four separate times: the skill under test was not
actually present on `~/.claude/skills/` at all (three cases), or a
fixture-promised environment variable was never actually exported into
the run (`test-in-the-consumer-context`'s own `INTERACTIVE_SESSION`
gap). In every case the "with" arm was silently ALSO a without-the-skill
run, or the planted trap was silently absent -- producing a broken pair
that had to be diagnosed, discarded, and re-run before any real
evidence existed.

This is strictly more expensive than a scorer bug: a scorer bug is
caught by reading a transcript that already exists. An installation gap
is caught only by noticing a suspiciously short run (1 turn, 0 tokens)
and then investigating WHY -- and until this pass, that investigation
was reinvented fresh each time rather than being a standing first step.
`~/.claude/skills/` symlinking 35 of this repo's 40 skills (5
consistently missing, unrelated to any single pass) means roughly one
in eight skills drawn for evaluation will hit this by default.

**Mechanical fix (jonhill90/skills#230, this repo's `scripts/
check_skill_install.py`):** a local, network-free comparison of
`~/.claude/skills/<name>` against this repo's own `skills/<name>`,
reporting MISSING (never installed) and DIVERGENT (installed but
drifted) as distinct verdicts rather than one collapsed "bad install."
It is wired into `scripts/eval_status.py --record` -- recording a verdict
refuses by default unless the skill under test passes this check, so the
investigation this section describes as "reinvented fresh each time" no
longer has to be. A hand override exists (`--skip-install-check
"<reason>"`) for the case where the install-state assumption genuinely
doesn't apply, and it prints the reason rather than skipping silently.
This is scoped to the public loop's own record-writing step; the private
`agent-evals` harness's own pre-run dispatch is out of scope for this
repository and untouched here.

### 3. Cost-signal noise across replicated pairs — 4 of 20, NEW

`decide-by-variant`, `determine-signals`, `devils-advocate`, and
`keep-me-honest` all share the same shape: the OUTCOME never differed
across any run in either pair (4/4, in every case) -- what looked
promising was a token/turn cost delta on a first pair, which then
either vanished, inverted direction, or failed to reproduce on an
independent second pair. `docs/evals.md`'s own ×2/×3-repetitions bar
exists precisely to catch this, and in all four cases it did -- a human
read both pairs and declined to trust a single-pair cost signal, per
that bar, rather than recording a premature `improve`. This was not
previously named as its own obstacle because the six-result sample that
produced the 2026-08-22 account had not yet run a second pair on
anything -- it is a property of doing the replication the loop's own
protocol already calls for, not a new defect in anything.

### 4. Clean no-discrimination — 4 of 20, the 2026-08-22 account's own "Cause A" with nothing else going on

`ask-a-council`, `dispatching-subagents`, `distill`, and `sanity-check`
hit no scorer bug, no fixture defect, and no cost noise -- the scenario
simply did not separate the two arms on a clean first read. This is the
smallest bucket at the larger sample, not the largest one the original
account implied (it was 4 of 6, 67%, in the original six; it is 4 of
20, 20%, now that the other four categories are named separately rather
than folded into it).

`ask-a-council` deserves its own footnote here: this is not a case
where the base model happened to reach the right answer without the
skill's help. The transcript shows the skill's OWN rules correctly
concluding a council was not warranted for this artifact ("check the
frame before convening") -- the skill fired correctly by declining to
fire. That is a different mechanism from the other three in this
bucket (where the skill, if invoked, would presumably have said
something, and the base model just got there anyway) even though the
measured outcome -- no observable difference -- looks identical from the
verdict alone.

### 5. Scenario design defect — 2 of 20, NEW

`mine-transcripts` and `notify` share a distinct failure: in both, the
prompt's own literal wording prevented the test from ever exercising
what it was built to test. `mine-transcripts`'s own prompt scoped the
search to `transcripts/` by name, so neither arm ever had a reason to
check the `vault/` note that actually held the answer -- both arms
correctly respected the stated scope, which is exactly what a careful
model should do, and is not evidence about the skill either way.
`notify`'s scenario framed the task as "modify this skill's own
script," which never read as `notify`'s actual trigger condition to
either arm -- the WITH arm never once called the `Skill` tool to load
`notify`'s own guidance, so the with/without conditions never actually
differed on the axis the scenario meant to test. Neither is a harness
bug (the scorers in both cases correctly read what the transcripts
actually contained) and neither is a fixture bug (nothing was broken or
missing) -- the SCENARIO itself, as authored, could not have discriminated
regardless of what the skill does.

## Answering agent-b5.md's four questions directly

**1. How many distinct causes are there really?** Five, not two -- the
table above. The eleven-plus new results since the six-result account
did not all fall into the original two buckets; two entirely new
categories (fixture/installation defects, cost-signal noise across
replicated pairs) turned out to be as common as the original "Cause A,"
and a third new category (scenario design defects) is smaller but
distinct in kind from both scorer bugs and fixture bugs.

**2. Which cause dominates, by count?** Scorer/regex misread, 6 of 20
(30%). Fixture/installation defects and cost-signal noise are tied for
second at 4 of 20 (20%) each. Clean no-discrimination, previously
assumed to be the majority case, is 4 of 20 (20%). Scenario design
defects are smallest at 2 of 20 (10%).

**3. Is any of the 20 a property of the skill rather than the harness?**
**No.** Reading all 22 evaluations for this question specifically:
every `could_not_measure` traces to the MEASUREMENT -- scenario
authoring, scorer code, fixture setup, or an under-replicated cost
signal -- never to a skill's own description being too vague to
discriminate against. Where a scenario picked a case the skill's own
text explicitly says is out of scope (`sanity-check`'s ~2%-arithmetic
case; the skill's own text says not to reach for it on a
single-command-verifiable number) or a scenario was simply too small to
engage the skill's actual cost-justification claim (`distill`'s
23-line corpus), that is a scenario-DIFFICULTY miss, not a vagueness
finding about the skill -- the skill's own rules are legible enough in
every one of these write-ups to say plainly what a HARDER scenario
would need to look like (see each result's own "what is not evidenced"
section). Nothing in this population is a candidate for `improve` on
the grounds of the skill itself being unclear.

**4. Is `could_not_measure` being used correctly in all 20?** **Yes, in
all 20 (22 sub-evaluations).** None reads as an under-called `keep` or
`improve` (a real difference found but softened) or an over-called
`drop` (a genuine "this skill changes nothing" hardened past what a
single scenario, at n=1 or n=2, can support). Every write-up that found
a scorer or fixture defect fixed it and re-scored BEFORE recording
anything, rather than reporting the pre-fix number. Every write-up that
found a cost delta on one pair and not on a second explicitly declined
to promote it to `improve` on the strength of the unreplicated pair
alone. This population is, if anything, evidence the loop's human
judgment layer is working exactly as intended -- the volume problem is
entirely upstream of verdict-recording, in what obstacles get in the
way of a clean measurement in the first place.

## The single highest-value change, and why it ranks first

**Add a mandatory pre-flight step to the loop's own protocol: before
trusting ANY run, confirm the skill under test is actually present on
the machine's shared skills path and matches this repository's own
current copy of it.** A one-line `diff -rq ~/.claude/skills/<name>
skills/<name>` (or equivalent) before the first live call.

This is not a harness patch -- it is a documentation/process change to
this repository's own evaluation method (`docs/evals.md`), squarely in
scope per this task's own constraint that scenario design and process
are in scope, harness internals are not.

**Why this ranks above fixing scorer bugs (the actual largest bucket):**
scorer misreads are already being caught, every single time, by a
practice this repository's own prior finding already named and every
subsequent pass has kept following ("read the actual transcript before
trusting the number"). That practice does not need a new recommendation
-- it needs to keep happening, which it is. Fixture/installation defects
have NO equivalent standing practice: four independent passes each
discovered the same failure mode fresh, diagnosed it by hand, and paid
for a discarded first pair before anyone thought to check installation
state up front. A pre-flight check would have caught all four before a
single token was spent on a broken first attempt, is trivially cheap to
run, requires no private-harness access at all (it is a local
filesystem comparison), and directly prevents the more expensive of the
two most common failure modes -- not merely the most frequent one.

Cost-signal noise (the other new category) does not need a new
recommendation either: the ×2/×3-repetitions bar that already caught
all four instances is `docs/evals.md`'s own existing protocol, working
as designed. Scenario design defects (`mine-transcripts`, `notify`) are
real but too varied in shape, at n=2, to generalize into one process
fix yet -- each needs its own rewritten scenario, which is scenario
design work for a future pass, not a standing checklist item.

### Cause C (found in the eleventh pass, one instance so far): a
### committed scenario's own fixture file can silently vanish

`notify`'s scenario fixture named its planted evidence file
`deploy-attempts.log`. This repository's own `.gitignore` excludes
`*.log` globally, so `git add -A` never staged it — the file existed on
disk for the live run that produced this pass's own result, but a fresh
checkout of the committed scenario (anyone re-running it later, per this
loop's own "committed so it can be re-run" convention since #236) would
find the fixture missing the one file its own prompt.md names by name.
Caught before committing, not after, by checking `git status --porcelain`
against what was expected rather than assuming `git add -A` staged
everything it should have.

This is the same class of defect as Cause B above, one layer earlier:
Cause B is a scorer reading the RIGHT file and misinterpreting its
content; this is a scenario whose own fixture reads as complete on the
authoring machine (the file is right there) while silently shipping
incomplete to anyone else, because nothing checks a scenario's own
file list against what actually got committed. Renamed the file to
`.txt` and confirmed it tracked before opening the PR — the mechanical
fix for this one instance — but the general lesson is Cause B's own
sentence with one word changed: **a scenario's own fixture list should
be checked against `git status`, not assumed complete because `git add
-A` ran without complaint.**

## What I did NOT do

- Did not patch, reproduce, or open a PR against the private
  `agent-evals` harness. This file names patterns in the harness's own
  observed behavior; it changes nothing in that repository.
- Did not relabel or delete any of the 20 `could_not_measure` entries,
  and did not record `drop` for any skill. All 20 verdicts were checked
  for correctness (see question 4 above) and found sound as recorded.
- Did not build a new scenario for any skill, including the two named
  under "scenario design defect" above -- naming what is wrong with
  `mine-transcripts`'s and `notify`'s own scenarios is this file's job;
  rewriting them is separate scenario-design work for a future pass.
- Did not implement the pre-flight installation check recommended
  above -- recommending it, with the evidence for why it ranks first,
  is this task's own scope; implementing it belongs to whoever picks
  up `docs/evals.md`'s own protocol next.
