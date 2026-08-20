---
name: plan-parallel-execution
description: Turn a task list into groups several agents can execute concurrently without colliding — derive file ownership mechanically, then supply the judgement a file-intersection cannot: shared resources that are not files, dependencies stated only in prose, and what each group's gate must prove. Use when work will be split across concurrent agents or worktrees, or when reviewing such a plan before it runs. Not for deciding how many agents or what each may see (dispatching-subagents), not for testing whether the plan's reasoning holds (sanity-check), and not for whether a step should be a tool at all (mechanize).
---

# Plan Parallel Execution

Concurrent agents fail by collision, not by confusion. Two workers editing
one file, or writing one database, produce a mess that neither can see from
inside its own turn — and the plan that scheduled them looked fine.

Most of the work here is mechanical and belongs in a script. This skill owns
the part that is not, and the seam between them is the whole point: a
file-intersection check is necessary, cheap, and **blind to the collisions
that actually happen**.

## Mechanize first, then reason

Derive, never hand-maintain:

- one **ownership manifest** — `task → path` for every file each task
  creates or modifies, generated from the task list itself
- **duplicate detection** — intersect the sets; any path claimed twice is a
  collision unless it is a deliberate serialization
- **file-based dependencies** — task B modifies what task A creates
- **topological grouping** — group 1 has no dependencies, group 2 depends
  only on group 1, and so on

A hand-kept manifest drifts from the tasks it describes, and a manifest that
disagrees with the plan is worse than none. Give the detector three exit
codes — clean, violation, **could-not-measure** — because a missing manifest
run through `cut | sort | uniq -d` produces silence, and silence is what
clean looks like.

Expect a known number of deliberate duplicates and assert it. **Zero
duplicates is a failure**, not a pass, when you know some exist: it means the
parser never saw those blocks.

## Then supply what the tool cannot see

### Shared resources that are not files

This is the failure a file-based rule is structurally unable to catch, and
it is the common one. Two tasks with disjoint file lists still collide on:

- a database — same file, different tables, concurrent writers
- a user-global config a whole machine reads
- a scheduler's domain, a session, a socket, a port
- an external API with rate limits or per-resource locking

Enumerate these per task by hand and declare which are **sequential-only**.
A plan that says "ledger writes never happen concurrently" and then schedules
two ledger writers in one group has not been read against itself.

### Dependencies that exist only in prose

Some ordering constraints are stated in a task's rationale and appear in no
file list. *"Task N's failing run is task M's before-picture"* — run M first
and the evidence is destroyed permanently, and nothing mechanical objects.

Read every task's validation section looking for ordering language, and
promote what you find into declared dependencies. Ascending task numbers
invite the wrong order; if the number order and the real order disagree, say
so loudly and in both places.

### Writes nobody owns

Ask what runs on a schedule while the plan executes. A migration applied on
object construction, a cron that rewrites state, a watcher that restarts a
service: these write during your groups and appear in no task's file list.
Either quiesce them or gate them, and name which you chose.

### What each group's gate must prove

A gate is an assertion or it is decoration. Per group, write the commands
that must pass before the next group starts, and:

- make each one `exit` on failure — a `grep -c` that prints `0` and exits 1
  is indistinguishable from success inside a non-`set -e` block
- give the gate a positive control, so a blind gate and a clean estate look
  different
- mutation-check it: break what the group fixed, confirm the gate goes red

One gate usually carries the whole plan's claim. Identify it, and state
plainly that the plan **stops** if it fails — otherwise the next group starts
on an unproven foundation and nobody decided to allow that.

## Rules that keep concurrency honest

- **Exclusive ownership, plan-wide.** Every path belongs to exactly one task.
  Where two findings touch one file, merge them into one task even if they
  are logically unrelated — consolidation is what makes the rest parallel.
- **An agent that needs a file it does not own stops and reports.** It does
  not edit and it does not negotiate.
- **One worktree and branch per task**, branched from the integration ref,
  never from a sibling. A task needing another's output waits for the group
  barrier.
- **Cap a group at 3–6.** Beyond that, name which member is held and why.
- **Barriers between groups are real.** Create the next group's worktrees
  only after the previous group's gate is green *and its work is merged* —
  a gate run against a checkout where the work does not exist yet passes or
  fails for the wrong reason.

## Have someone else read the finished plan

An author cannot audit their own bookkeeping. The manifest, the dependency
order and the validation blocks get re-read by their author the same way they
were written. A separate context, given the finished artifact and told to
intersect the file sets and re-read every validation line, finds in one pass
what the author cannot see at all. See `dispatching-subagents`.

## What this is not

- **`dispatching-subagents`** decides how many agents, what each may see,
  isolation boundaries, and what counts as external evidence. This decides
  what may run beside what.
- **`mechanize`** decides whether a step should become a tool. This applies
  that decision to one domain and names the seam.
- **`sanity-check`** tests whether reasoning holds. Run it on the plan after
  this produces one.
- **`loop-contract`** designs a repeating unattended loop. This designs one
  bounded fan-out.

## Where this came from

A 35-task plan for 3–6 concurrent agents, reviewed adversarially before it
ran. The file-ownership half held up exactly as designed: 142 paths, one
intersection, and that intersection was the deliberate serialization the plan
had declared.

Everything the review found was on the other side of the seam.

- The parallel-safety manifest **did not exist**, and its detector —
  `cut -f2 … | sort | uniq -d`, with the rule "silence is clean" — returned
  silence and exit 0 against the missing file.
- The lane-claim command the contract specified **was not a command**;
  the real subcommand had a different name and different arguments. All 35
  agents would have failed it.
- **Two tasks writing the same database were scheduled in one group** — the
  plan's own findings list identified the pair, and then placed them
  together. Their file sets were disjoint.
- One task mutated a **user-global config** while four sibling agents ran
  against it, and that file appeared in no task's file list.
- A migration was applied by a **scheduled job, not by any task**, at an
  unpredictable point mid-plan.
- **Five dependencies existed only in prose.** One of them destroyed a later
  task's evidence if run in numeric order.
- **All eight group gates printed rather than asserted** — including the one
  guarding the plan's central claim, which passed against a script that was
  `exit 0` and nothing else.
