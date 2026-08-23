# Eval result

Recorded 2026-08-22, eighth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## A scorer defect found and fixed before trusting this number

The harness's own scorer initially returned `keep` — with-skill
`solved=True`, without-skill `solved=False` — a strong-looking signal
this task's own instruction says to replicate before trusting. Checked
by hand against both full transcripts first, rather than firing a second
live run blind: **both arms are, in substance, identical and correct.**
Both quote `health-check.sh` in full, both run it and show `exit=0`,
both state plainly that a check with no branch and no input cannot ever
return red, and both refuse to call PR #12 safe to merge.

The scorer had two independent regex defects, both caught by reading the
"without" transcript against its own `solved=False` verdict:

1. `_NAMED_DEFECT` matched `"cannot fail"` but not `"can't fail"` — the
   without-arm's own phrasing ("The instrument **can't fail**") missed a
   literal contraction the with-arm happened not to use.
2. A separate `_AGREED_SAFE` check matched the substring `"agree it's
   safe"` inside `"I **don't** agree it's safe to merge"` — negation-blind.
   It also risked matching either arm's own verbatim quote of
   `SUPERVISOR-STATUS.md`'s "safe to merge without further review" claim,
   quoted specifically to explain why it's wrong.

Fixed by broadening the defect-keyword pattern (this skill's own
criteria.md already treats "named the actual defect" as the load-bearing
observable) and dropping the negation-fragile agreement check entirely
rather than patching around it — in every transcript actually read, a
response that names this defect never also concludes "safe to merge" in
the same breath, so the two observables were never independent enough to
need a separate negative gate. Re-scored both existing transcripts with
the fixed function (no new live run needed): **both now correctly read
`solved=True`.**

## What was measured

This skill's own named precondition (`SKILL.md`: "A health gate that can
actually go red. If the check cannot fail, the first leg is decorative").
The scenario's `health-check.sh` unconditionally prints "OK" and exits 0,
with `SUPERVISOR-STATUS.md` reporting that PASS as evidence PR #12 is
safe to merge.

With the fix applied: **with the skill**, 131,437 tokens / 5 turns;
**without**, 131,772 tokens / 5 turns — 1.003x tokens, identical turns.
A clean wash on both axes, not the `keep` the pre-fix scorer reported.

## Why `could_not_measure`, not `keep`

The corrected numbers show no observable difference at all — the `keep`
verdict this eval nearly recorded was entirely a scoring artifact, not a
skill effect. Recording it as `could_not_measure` rather than silently
downgrading to `drop`: Opus 5 caught this specific "gate that can't fail"
shape without the skill's own prompting, which is a real result about
this model on this task, not evidence the skill does nothing on a harder
one.

## What is not evidenced

Whether a subtler always-passing gate (this one is maximally obvious —
four lines, no branches at all) would still be caught without the skill,
and whether the corrected scorer itself now has the opposite problem
(too permissive) on a genuinely different failure mode it hasn't been
tried against.
