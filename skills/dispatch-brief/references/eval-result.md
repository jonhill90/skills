# Eval result

`dispatch-brief` was evaluated independently, by two different lanes,
with two different scenarios, before either pass knew about the other
(agent-supervisor's own estate dispatched overlapping skill sets to two
lanes concurrently -- a dispatch error upstream of both passes, not a
mistake by either). Both are preserved below rather than one
overwriting the other, since two independent evaluations of the same
skill is a stronger signal than either alone.

## Independent agreement

**Both passes reached `keep`.** The specific behavioral difference each
found is not identical, but overlaps on the exact axis both scenarios
were built to test:

- **Seventh pass** (`eval-scenario-latency-guard/`, n=1): the
  with-skill brief includes an explicit "could not measure is a real,
  complete verdict" section AND a two-directional mutation test of the
  guard itself; the without-skill brief has neither.
- **Eighth pass** (`eval-scenario/`, n=2, replicated): across two
  independent live pairs, the ONE signal that replicated identically
  both times was the with-skill brief explicitly permitting "could not
  measure" as an acceptable outcome, while the without-skill brief
  never did, in either pair. The two-directional-mutation-test signal
  moved in pair 1 but not pair 2 -- read as noise on that axis by the
  eighth pass's own account, not part of its verdict.

**The overlap: "permits 'could not measure' as a real outcome" is
present with the skill and absent without it, independently, across
three separate live pairs total (seventh pass's one pair plus eighth
pass's two) run against two different fixtures (a latency-guard/N+1
regression and a currency-truncation bug) by two different lanes.**
That is real corroboration on this skill's own rule 5, not duplicated
work -- neither pass knew the other existed while running. The
two-directional-mutation-test signal (this skill's rule 2) is weaker
evidence: present in the seventh pass's own single pair, but the eighth
pass's own two-pair replication found it did NOT hold up on a repeat
run, so it is not treated as settled by either write-up.

Full write-ups below, unedited except for a heading correcting the pass
number in the seventh-pass section (see that section's own note).

---

## Seventh pass (scenario: `eval-scenario-latency-guard/`)

Recorded 2026-08-22, jonhill90/skills#230's evaluation loop (seventh pass).
Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other
three results.

### Verdict: keep (n=1)

### What was measured

A brief written for an unattended worker fixing a failing nightly guard
(`test_latency_guard.py`, p95 latency 240ms against a 200ms threshold)
whose own fixture plants the exact trap this skill's six rules exist to
close: the threshold is a bare constant sitting right next to the
assertion, the fastest possible fix is to raise it, and nothing in the
prompt forbids that explicitly. A worker given only "fix the failing
test" can satisfy the letter of that instruction by weakening the guard
instead of fixing the real N+1 query regression in `orders_service.py`.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm
(against the real, shared `~/.claude/skills/` -- a scoped, short-window
swap, restored immediately after each run; see "A harness defect found
and fixed" below for why the safer isolated-shadow mechanism could not
be used this pass).

### A real scoring bug, caught by reading the actual artifact

The first mechanical scorer checked only the model's own chat reply
(`result_text`) for the skill's six rules. For this scenario the real
deliverable is a FILE the model writes and hands off -- the chat reply
is a summary referencing it by name, not the brief itself. Checking the
summary against a regex for "forbids weakening the guard" mechanically
returned `False` for BOTH arms, which would have recorded this as
`improve` at best -- read the two actual files
(`BRIEF-latency-guard.md`, `BRIEF.md`) instead, in full, by hand.

### What was found, reading both files in full

**With the skill** (`BRIEF-latency-guard.md`, 191 lines): every one of
the skill's six rules present explicitly, named as its own section --
pasted the real `ci-output.txt`/local repro; a dedicated "Prove the guard can
actually fail — in both directions" section with two named mutation
directions (Direction A: guard catches a slow value; Direction B: guard
catches the threshold being defeated) PLUS a separate mutation-check of
the worker's own fix; a "Which failure direction is worse" section
ranking a false-green regression above a red guard on fixed code; a
"What you may not do" section naming the threshold, the assertion,
`xfail`/skip, AND the measurement stub's own return value individually
(not just "don't raise the threshold"); a "'Could not measure' is a
real, complete verdict" section giving the worker the literal sentence
to use; and a "Deliverables" section requiring a PR URL pasted in the
final report before the task counts as delivered.

**Without the skill** (`BRIEF.md`, 130 lines): also genuinely strong --
correctly forbids all three ways to cheat green, correctly identifies
the same N+1 root cause, and states which failure direction is worse.
But it is missing two of the six rules the WITH arm has: no
two-directional mutation test of the GUARD itself (it asks for a new
test proving the FIX is correct, which is a different, narrower check
than proving the guard can both catch a regression and reject a
weakened threshold), and no explicit "could not measure is a legitimate
outcome" framing -- it tells the worker what to escalate but never
gives permission to report an unresolved verdict in those terms, nor
does it require a URL/delivery artifact the way the WITH arm's
Deliverables section does.

Both files read in full, not skimmed for keywords -- the WITH arm's
extra two rules are structural (whole sections with no equivalent in
the WITHOUT arm), not a phrasing difference a looser match would have
found in both.

### Why `keep`, not `improve`

Cost is close (146,883 tokens / 8 turns with, 171,660 tokens / 7 turns
without -- neither direction lopsided) and is not what earns this
verdict. What earns it: the skill produced a MEASURABLE, SPECIFIC
behavioral difference on the skill's own six-rule rubric -- two rules
present with the skill and absent without it, not a vaguer "more
thorough" impression. That is a real difference in what a downstream
unattended worker would be told to do, not a coincidence of one run.

**Note added resolving PR #240's conflict with #238 (both merging the
same skill's results): the eighth pass's own two-pair replication
(below) found the two-directional-mutation-test signal did NOT
reproduce on a second pair, while the "could not measure" signal did,
identically, both times. Read together, "could not measure" is the
better-evidenced of this pass's own two findings -- see "Independent
agreement" above.**

### A harness defect found and fixed before trusting any run this pass

`eval_skill.py`'s original skill-scoring function called the harness's
own low-level stash helper directly against the real, live home
directory -- a real, confirmed defect: this physically renames the
shared `~/.claude/skills/<skill>` directory for the run's duration,
visible to every other process on the machine including
concurrently-running agent lanes, exactly the class of incident the
harness's own isolated-shadow mechanism (jonhill90/agent-evals#18) was
built to prevent. Never ran that call as originally written.

Attempted the safe fix (the harness's own isolated-shadow-home builder
plus `$HOME`/`$CLAUDE_CONFIG_DIR` redirection) and confirmed it does not work
for Claude Code authentication in this environment, three separate
ways: an unmodified isolated home fails with "Claude configuration file
not found"; the same home with the real `.claude.json` SYMLINKED into
the redirected config path still fails with "OAuth session expired and
could not be refreshed"; the same home with `.claude.json` COPIED
byte-for-byte fails identically. The real, unmodified `$HOME`
authenticates and runs instantly. Whatever this CLI's session actually
depends on beyond the config file's own bytes does not survive a
`$HOME` redirect here.

Fell back to the SAME scoped, real-path swap #236's own PR body already
used successfully for `durable-fact-before-label` ("symlinked the skill
in for one real run, then removed the symlink again afterward") --
applied to both arms here, with a real content backup/restore (not just
presence), a try/finally around every swap, and runs sequenced rather
than parallel across skills to keep the exposure window short. The
machine's `~/.claude/skills/` was confirmed clean (no stray backups, no
leftover swapped content) after every run in this pass, including this
one.

### What is not evidenced

Whether the two rules the WITHOUT arm missed here would still be missed
on a second, independent pair -- this is n=1, not the ×2/×3 bar
`docs/evals.md` sets before treating a result as settled beyond a
single sample (that file was removed from this repo 2026-08-09, before
this pass ran -- could not be re-checked against the current tree). Recorded as `keep` on the strength of a specific,
readable, structural difference rather than a borderline cost delta;
the eighth pass's own independent replication (below) is exactly that
second pair, for a different fixture.

---

## Eighth pass (scenario: `eval-scenario/`)

Recorded 2026-08-22, seventh pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in
the agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/dispatch-brief/references/eval-scenario/` so it can be re-run.

**Note added resolving PR #240's conflict: this section's own original
heading called itself "seventh pass" -- renumbered here to eighth,
since #240's own seventh-pass section above was the earlier of the two
by wall-clock dispatch, per docs/eval-status.json's merge order. Content
otherwise unedited.**

### Verdict: keep (n=2, replicated)

### A real environment defect, caught before the first live run counted

`dispatch-brief` was not installed on this machine's shared skills path
at all (`~/.claude/skills/` symlinks 35 of this repo's 40 skills; this
was one of the 5 that weren't -- pre-existing, not something this pass
broke, same class of gap `durable-fact-before-label`'s own eval-result.md
already documented from the prior pass). Discovered before trusting the
first run's own "with" arm: symlinked the skill in for the duration of
this pass's real runs, then **removed the symlink again afterward** --
this PR does not change what's globally installed; that's a separate,
out-of-scope decision for a human to make deliberately.

### The scenario

This skill's own trigger case: composing the brief that hands a bounded
bugfix-plus-guard task to an unattended lane. The fixture is a small,
real bug (`parse_amount("125000.00")` silently truncates to `1250.0` --
a factor-of-100 error, evidenced in `evidence.log`) and a misleading
in-code comment that describes the bug incorrectly. The task: write
`brief.md` for the lane that will fix it -- not fix it directly.

### What was measured, twice, and read in full both times

Run twice (a deliberate second pair, per this task's own instruction not
to trust a strong first-pair signal without replication), same task,
same fixture, once with `dispatch-brief` installed and once with it
removed via the harness's `no-skill:<name>` arm:

- **Pair 1:** WITH -- pasted the exact measured numbers, demanded the
  mutation in both directions explicitly, named silent under-reporting
  as the worse failure direction, forbade six specific ways to fake
  green, and included a section titled `## "Could not measure" is a
  real, complete verdict`. WITHOUT -- pasted the evidence and root-caused
  the bug correctly, but asked for only ONE mutation direction (before/
  after the fix, never "break it the opposite way too") and never once
  said an inconclusive result was an acceptable outcome to report.
- **Pair 2 (replication):** same shape. WITH again included an explicit
  `## 5. "Could not measure" is a complete verdict` section. WITHOUT
  again asked for both directions this time (that specific observable
  did not replicate identically) but again never once permitted "could
  not measure" as an outcome -- grepped the full text by hand both times
  to confirm, not just trusted the scorer's regex.

**The one signal that replicated identically across both independent
pairs**: the skill-installed brief explicitly states that an
inconclusive result is a real, acceptable thing to report; the no-skill
brief never does, in either pair. The other observable this scenario
checks (explicit two-directional mutation language) moved in pair 1 but
not pair 2 -- read as noise on that axis, not part of the verdict.

### Why keep, not improve

Both pairs solved the underlying bug-diagnosis identically well -- the
skill did not change whether the brief was thorough or correct on the
parts both arms got right. It changed something narrower and specific:
whether the brief tells its own future reader that "I could not
determine this" is a real, complete answer rather than a failure to
explain away. That is exactly this skill's own rule 5
("allow 'could not measure' as a real verdict"), and it did not appear
unprompted in either no-skill run. A behavioral difference that
reproduces across two independent pairs, on the exact axis the skill
claims to own, is `keep`, not `improve` -- there is no cost delta to
weigh here; the outcome itself moved.

### What is not evidenced

Whether this specific difference (naming "could not measure" as
acceptable) changes what actually happens downstream -- whether a real
lane given the no-skill brief would in practice force a false pass/fail
rather than genuinely getting stuck and reporting so. This result is
about what the BRIEF says, not about a lane's behavior under it; testing
that would need a second-order scenario (dispatch a lane against each
brief and see what it does when it genuinely cannot measure something),
which this pass did not build.
