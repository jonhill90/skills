# Eval result

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (seventh pass).
Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other
three results.

## Verdict: could_not_measure (n=1)

## What was measured

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

## A real scoring bug, caught by reading the actual transcripts

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

## What was found, reading both transcripts in full

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

## Why `could_not_measure`, not `improve` or `drop`

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

## What is not evidenced

Whether the base model would still find both collisions without the
skill on a scenario where the file-path obfuscation is less generous
(this prompt still uses closely-related vocabulary -- "discount tiers"
/ "pricing tiers" -- for the same object; a scenario using genuinely
unrelated phrasing for the same file would be a harder test).
