# Eval result

`plan-parallel-execution` was evaluated independently, by two different
lanes, with two different scenarios, before either pass knew about the
other (agent-supervisor's own estate dispatched overlapping skill sets
to two lanes concurrently -- a dispatch error upstream of both passes,
not a mistake by either). Both are preserved below rather than one
overwriting the other, since two independent evaluations of the same
skill is a stronger signal than either alone.

## Independent agreement

**Both passes reached `could_not_measure`, and agree in substance, not
just in the printed word.** In both passes' own scenarios (a
five-task/two-file-collision scenario in the seventh pass; a
six-task/one-collision, stale-manifest scenario in the eighth), BOTH
arms of BOTH passes correctly found and correctly resolved the planted
file-ownership collision(s) -- the skill made no observable difference
on outcome in either independent run. Cost stayed inside this harness's
own ×1.5 tolerance on both axes in both passes. Neither pass forced a
mechanical `drop` for the identical-outcome, inside-tolerance pair;
both independently invoked the same `docs/eval-harness-findings.md`
Cause-A reasoning ("the scenario didn't discriminate" is not the same
finding as "the skill measurably does nothing") to record
`could_not_measure` instead. Two independently-designed scenarios,
independently landing on the same verdict for the same reason, is
stronger evidence for `could_not_measure` here than either pass alone.

Both passes also independently found their own scenario's manifest/
input file did not actually exist in the fixture as their own prompt
claimed it did, and both models caught that gap unprompted in both arms
-- not scored as part of either verdict, but a striking parallel between
two unrelated fixtures built by two different lanes.

Full write-ups below, unedited except a heading correcting the pass
number in the seventh-pass section (see that section's own note).

---

## Seventh pass

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (seventh pass).
Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other
three results.

### Verdict: could_not_measure (n=1)

### What was measured

Five tasks, described only by BEHAVIOR ("wherever customer discount
tiers are defined," "the login entrypoint"), to be grouped into
concurrent batches -- no task names a file path directly. The fixture
plants two real collisions that only resolve by actually reading the
repo: tasks 1 and 3 both edit `billing/pricing.py`'s `PRICING_TIERS`
dict (described two different ways: "discount tiers" and "pricing-tier
definitions"), and tasks 2 and 4 both edit `auth/login.py`'s `login()`
(both called "the login entrypoint," never a literal path). Task 5
(README) collides with nothing. A plan that only intersects literal
file-path strings named in the prompt -- there are none -- would find
zero collisions; a plan that derives an ownership manifest from the
real fixture (this skill's own "Mechanize first" section) finds both.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm (scoped
real-path swap, restored immediately after each run -- see
`skills/dispatch-brief/references/eval-result.md`'s own harness-defect
section).

### A real scoring bug, caught by reading the actual transcripts

The mechanical scorer for this scenario was deliberately written as a
starting heuristic only (its own criteria.md says so: "a criterion this
specific... is a statement about the plan's own structure, not a fixed
string a keyword match can safely resolve"). Read by hand, as required:
the heuristic parser flagged the WITH arm as having failed to avoid the
1∩3 collision, because it grouped tasks 1 and 3 together under one
batch label ("Batch A — 2 agents, concurrent... A1 = tasks 1 + 3"). That
is a real misread: the WITH arm's own text explains it MERGED tasks 1
and 3 into one combined task, executed by ONE agent in a single pass --
not two agents concurrently fighting over the same file. Merging
colliding tasks into a single unit is a valid resolution of a collision
by construction (this scenario's own criteria.md explicitly allows "a
deliberate serialization" as an acceptable alternative to separate
batches), not a miss.

### What was found, reading both transcripts in full

**Both arms correctly identified and correctly resolved both
collisions**, via two different valid strategies:

- **With the skill**: merged 1+3 into one task owning
  `billing/pricing.py` and 2+4 into one task owning `auth/login.py`,
  each run by a single agent -- explicitly named the merge-conflict
  risk ("They edit overlapping lines, so this is a merge conflict, not
  just a same-file adjacency"), added a non-file-resource audit (found
  none in this fixture, but named what WOULD become one -- a shared
  rate-limiter store), wrote a two-part mechanical gate with an explicit
  positive control (`login('demo','demo') is True`) and its own
  mutation-check instruction ("delete the `gold` key and confirm red"),
  and correctly held Task 5 back to a later batch on a PROSE-only
  dependency (it documents "the new gold tier," which Task 1 creates) --
  a dependency no file-intersection check alone would catch.
- **Without the skill**: also correctly found both collisions by name
  ("there is only one tier definition... both edit that same dict") and
  serialized them into two separate batches (Batch 1: tasks 1, 2, 5;
  Batch 2: tasks 3, 4) -- also correctly identified Task 5's prose-only
  dependency on Task 1 independently, and additionally named that tasks
  2 and 4 "conflict semantically, not just textually," since whichever
  runs second must compose with the first's guard rather than replace
  it.

Both transcripts confirm real file reads (not guessed from the prompt's
repeated phrasing) -- both cite real line numbers from
`billing/pricing.py` and `auth/login.py`.

### Why `could_not_measure`, not `improve` or `drop`

Cost: 104,216 tokens / 7 turns with the skill, 96,643 tokens / 5 turns
without (1.08x tokens, 1.4x turns -- both inside this harness's own
1.5x efficiency-flag tolerance). Both arms reached the correct outcome
by valid, if differently-shaped, means, and the cost delta does not
clear the tolerance bar on either axis. Same Cause-A pattern
`docs/eval-harness-findings.md` already names for four other skills in
this loop, and the same reason `dispatching-subagents`' own result in
this same pass reaches the same verdict: the mechanical harness would
print `drop`, but "both arms solved it" is not the same finding as "the
skill makes no difference" -- this scenario did not discriminate
between arms on this model, which is a real result about the scenario
and the model, not the skill.

The WITH arm's answer is, on a qualitative read, noticeably richer
(mutation-checking its own gate, auditing non-file shared resources,
naming the positive-control failure mode explicitly) -- flagged here
for a reader's own judgment rather than mechanized into the verdict,
since "richer" is not one of this scenario's own two named observables
and inflating a real qualitative impression into a verdict the
criteria.md didn't ask for would repeat the exact mistake this section
exists to avoid.

### What is not evidenced

Whether the base model would still find both collisions without the
skill on a scenario where the file-path obfuscation is less generous
(this prompt still uses closely-related vocabulary -- "discount tiers"
/ "pricing tiers" -- for the same object; a scenario using genuinely
unrelated phrasing for the same file would be a harder test).

---

## Eighth pass

Recorded 2026-08-22, eighth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

**Note added resolving PR #240's conflict: this section's own original
heading called itself "seventh pass" -- renumbered here to eighth,
since #240's own seventh-pass section above was the earlier of the two
by wall-clock dispatch, per docs/eval-status.json's merge order. Content
otherwise unedited.**

### Verdict: could_not_measure (n=1)

### What was measured

This skill's own trigger case (`SKILL.md`: derive the ownership manifest
mechanically from the CURRENT task list; "a manifest that disagrees with
the plan is worse than none"). The scenario gives a 6-task plan split
across 3 concurrent groups, and a manifest whose own header admits it was
"generated before T5 was added" and lists only 5 of 6 tasks — T3 and T5,
in different concurrent groups, both write `config/settings.json`, a real
collision the stale manifest's "0 duplicates" claim never covered.

Run twice, live, same task, same fixture, once with `plan-parallel-execution`
installed and once with it removed via the harness's `no-skill:<name>`
arm:

- **With the skill:** found the T3/T5 collision, named the exact files
  each modifies, explained why `uniq -d` produced no output (T5 was
  excluded from its input), and additionally noticed `manifest.tsv` (the
  command's own stated input) does not exist in the fixture at all --
  the pasted "clean" result cannot even be reproduced. 98,209 tokens, 5
  turns.
- **Without the skill:** the same result, same collision, same
  observation about the missing `manifest.tsv`, plus a further note that
  none of the six target paths exist in the fixture either (a planning
  document, not a live tree). 131,016 tokens, 5 turns.

Both transcripts read in full by hand (kept locally alongside each run,
not published per this repository's own scope) -- both are correct,
specific, and go beyond the fixture's own planted trap to find additional
real problems with the evidence (the unreproducible manifest command).

### Why `could_not_measure`, not `drop`

Identical, correct outcome in both arms; cost is a wash (1.33x tokens,
1.0x turns -- inside the ×1.5 ratio this harness's own `verdict()` treats
as noise). Not passed through as the harness's own mechanical `drop` for
an identical-outcome pair, per this loop's own fifth-pass finding
(`docs/eval-harness-findings.md`): that branch has no separate outcome
for "the scenario didn't discriminate" versus "the skill measurably does
nothing." Opus 5 caught this specific file-ownership collision and the
stale-manifest reasoning without needing the skill's own prompting -- a
real result about this model on this task, not evidence the skill is
dead.

### What is not evidenced

Whether a plan large enough that the collision is not visible by eye in
one screen (this skill's own real-world case was 35 tasks, 142 paths;
this scenario used 6 tasks specifically so a strong model could plausibly
spot it by inspection alone) would still be caught without the skill's
own "mechanize the manifest, then reason" discipline.

---

## Counting-measurement re-run (jonhill90/skills#266, real execution)

Recorded 2026-08-23. Both prior passes (above) scored a *written plan* —
a document describing a grouping, never actually run. This re-run,
modeled on `progressive-disclosure`'s `eval-scenario/` (skills#265/#229),
instead makes the arm **execute** the work for real via
`references/eval-scenario-count/fixture/worker.sh`, a script whose
read-then-append pattern produces a genuine, mechanically detectable lost
-update race (duplicate `seq=` numbers) if two tasks targeting the same
output file actually run concurrently — verified by hand before use (two
manual dry runs: concurrent same-file writers produced real duplicates;
serialized writers did not). Full design: `references/eval-scenario-count/
criteria.md`.

### A real scenario defect, caught before recording anything

The first version of this scenario's `prompt.md`/`tasks.md` told BOTH
arms directly to group same-file tasks apart from each other, and named
the file collision as "planted" in the task list's own header — handing
the no-skill arm the exact rule the skill exists to derive. Two live
trials against that version (not counted below) showed identical,
correct grouping and comparable cost in both arms, which is worthless as
a result given the leak. Caught by re-reading the actual prompt text
given to both arms (the same discipline `docs/eval-harness-findings.md`
names for `create-skill`'s own leaked fixture, §2) before trusting the
clean result. Fixed by removing the stated safety rule and the "planted
collision" framing entirely — both arms are now told only to "get all
five tasks done as quickly as you reasonably can," with no hint that a
collision exists or that grouping matters at all. All numbers below are
from the corrected version.

### Result: clean no-discrimination, genuinely this time

| | tokens | tool_uses | groups | turns_used | real collision? |
|---|---:|---:|---|---:|---|
| A (skill) | 41,140 | 6 | `[[T1,T2,T4],[T3,T5]]` | 2 | none (checked: 0 dupes in all 3 files) |
| B (no skill) | 37,149 | 6 | `[[T1,T2,T4],[T3,T5]]` | 2 | none (checked: 0 dupes in all 3 files) |

Both arms independently read the five task descriptions, correctly
identified that task 3's "the counter file the payments ingest path also
writes to" is the same target as task 1's `out/ingest.log`, and that task
5's "the same audit trail task 2 writes" is the same target as task 2's
`out/billing.log` — the exact two-collision structure this scenario
plants — and both produced the identical grouping (three disjoint-file
tasks concurrent, then the two collision-partners concurrent with each
other but after their same-file sibling finished), executed via real
backgrounded `worker.sh` runs, confirmed collision-free by an actual
duplicate-`seq=` check against the real output files. Cost is
essentially identical (6 tool_uses each; tokens within 10%). No
discrimination on correctness or cost.

### Why this generalizes the same way `mechanize`'s re-run did

A competent, coding-capable baseline model already treats "does task 3's
prose describe the same target as task 1's" as an ordinary reading-
comprehension step, and "don't run two writers on the same file at once"
as a default safety habit, with nothing in this task pushing it away from
either. `progressive-disclosure`'s trial 2 (skills#265) discriminated
because its added pressure argued directly FOR the specific behavior the
skill argues against; no equivalent pressure was found for this scenario
that specifically tempts a capable baseline toward ignoring a file
collision it has already noticed, without simply telling it not to check
for collisions at all (which would test instruction-following, not
judgement). This is the same "no engineered competing pull on the
skill's own axis" gap `mechanize`'s trial 2 surfaced, not a new failure
mode.

### What is (still) not evidenced

Whether a genuinely large task list (the skill's own real-world case:
35 tasks, 142 paths) or a real deadline/urgency framing that specifically
argues for "just run everything at once, we're behind schedule" — a
pressure that targets the skill's own axis (concurrency safety) the way
`progressive-disclosure`'s "be thorough" pressure targeted its axis
(reading everything) — would still produce identical grouping without
the skill. Not run here; the honest answer for this scenario at this
scale, this task-count, and this framing is **could not measure** a
skill-attributable difference.
