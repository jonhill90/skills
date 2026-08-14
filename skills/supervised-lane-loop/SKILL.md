---
name: supervised-lane-loop
description: Run a long-lived supervisor loop over one or more worker agent lanes — recurring health gate, a named defect family as the work seam, and verification standards that let work merge without the human reading diffs. Use when supervising agents across many hours or days, when a recurring cron prompt drives an agent, or when deciding whether a lane's PR is safe to merge.
---

# Supervised lane loop

A supervisor agent runs on a recurring prompt. Each firing it checks
production, reviews what the worker lanes produced, merges what it verified,
and gives idle lanes new work. The lanes implement; the supervisor never
implements and never trusts.

This works for days without human input because the *prompt* carries the
contract, the *seam* generates the next task, and the *standards* make merging
safe. Remove any of the three and the loop degrades within an hour — usually
into documentation passes, which feel productive and are not.

**Status: practice, not measured.** This describes one estate, one supervisor,
two lanes, about two days of continuous operation. It has never been run
against a counterfactual, so which rules carry the weight and which are the
author's preference is unknown. The supervisor's own untested guess: the
self-sufficient prompt and the defect family do most of the work, the merge
standards make it safe, and the rest is refinement. Treat that as a hypothesis.

The standards below are per-decision rules you can judge one at a time. That
the loop *compounds* over days — the prompt surviving context loss, the seam
generating the next task unaided — is the part no single observation
establishes. Weigh the two differently.

## Preconditions

Without these the loop does not degrade gracefully — it becomes unsupervised
implementation wearing a supervisor's vocabulary.

- **A health gate that can actually go red.** If the check cannot fail, the
  first leg is decorative and nothing stops work landing on a broken estate.
- **CI that can fail, and an issue tracker.** The standards below assume a
  merge can be blocked and a parked finding has somewhere to live.
- **A codebase large enough to sustain one defect family for days.** A small
  repo exhausts a family in an hour, and then the loop needs new seams far
  more often than this implies.

## The recurring prompt must be self-sufficient

Restate the whole contract every firing: the health command, the lane
protocol, the current seam, the standing rules, and the do-not-relearn list.

Do not rely on conversation history. Context gets summarised, sessions get
resumed cold, and standards that live 200 messages back decay silently. A
prompt that re-establishes everything costs a few hundred tokens per firing
and makes every firing independent.

Keep a **do-not-relearn list** in the prompt: conclusions already settled,
traps already paid for, and instrument quirks specific to this estate. Its
job is to stop the loop re-deriving the same answers, which is the main way
these loops waste days.

### The loop's own pane is single-writer

A dynamic recurring loop stays alive by scheduling its own next wakeup at the
end of every turn. **A plain message sent into that same pane replaces the
loop's prompt outright** — the next turn is an ordinary turn, nothing
re-arms, and the loop ends silently. A watchdog cannot distinguish that from
a crash; both look like "idle pane, agent alive, no pending wakeup."

Route out-of-band corrections through a side channel the loop explicitly
drains at the top of every firing — never as a raw message into its own
conversation. Measured on one estate: 27 raw messages sent into a running
loop produced zero re-armed wakeups; each one ended the loop, and every
restart cost real time before anyone noticed. A convention alone ("nobody
but the loop writes here") does not hold — enforce it by making corrections
arrive somewhere the loop reads on purpose, not somewhere it merely happens
to receive text.

## Health first, and it is a hard gate

Begin every firing with the same concrete check, by name, against the real
system. Not a count — a list. Counts agree with themselves; a name that is
absent is a name.

The gate is *a named list of things that must be true, checked against the
real system*. It is not any particular list — sixteen containers, seven
tenants and two endpoints is one estate's instance of it.

Degraded means stop everything and report. Do not start new work on a
degraded estate, and do not let a lane's PR merge into one.

Two rules that come from getting this wrong:

- **Suspect the instrument before believing the verdict.** A failed local
  command reads exactly like an outage. Retry once, and check from a second
  vantage point, before reporting anything as down.
- **A "clean" result from a query that could not see the thing is not clean.**
  An empty result proves nothing unless you can show the query was capable of
  returning a non-empty one.

### Suspect your own instrument first

The supervisor runs more one-off commands than any lane, so it makes more
instrument errors than any lane. Observed in a single day: a production
endpoint reported down when the supervisor's own `curl` had failed; a CI
failure line cut off by `tail` and the run called clean; a `grep` matched
against the wrong section of a file, twice; call sites miscounted by half.

Every one of those would have reached the human as a false report.

## The seam: name a defect family, not a task list

The single highest-leverage choice. A good seam is one sentence describing a
*class* of defect, and it generates its own next task.

The one that carried this repo for days: **"an operation that fails but
reports success."** From that one sentence, in order, without the human
supplying any of it:

read path in the UI → write path in the UI → non-atomic writes in the api →
success-reporting in shell scripts → unverified revokes in the secrets tooling

Each area exhausts, and the family points at the next one. Compare "find
bugs", which produces scattered, unrankable churn nobody can review.

Signs your seam has gone stale: findings get cosmetic, ranking gets
arbitrary, or the lanes start proposing documentation. Name a new family.

## The supervisor never implements

State it explicitly, because the loop only implies it and the pressure to
break it is constant. The reason is not workload. If the supervisor writes the
fix, the supervisor reviews its own work, and the independence of the second
seat — the entire value of the arrangement — is gone. Touching the tree also
contaminates a lane's workspace.

## Standards that make merging safe

The supervisor merges without the human reading diffs. That is only
defensible with all of these enforced.

**Positive-control everything, and show it failing first.** A test that has
never failed has not been shown to test anything. For a new check, prove both
directions: it goes red on a real violation and green without one. Prove it
against something real — a live container, a mutated production-shaped file —
not a fixture written to match the checker's own expectations, which only
proves the checker agrees with itself.

**Read the diff's file list, not just the claim.** Verify what the PR says it
does, then look at what else is in the commit. A 155-line file once rode into
a merged PR about wiring a CI check, because the wiring claim was verified and
nothing else was looked at. The file was this skill.

**A hit is not a finding.** Grep matches are candidates. For each, establish
what the caller/user/operator actually observes, and drop the ones where the
existing behaviour is correct. Report triaged-versus-real as a ratio. A sweep
that reports 66 findings from 66 matches did not triage.

**Closing something out as not-real is a result.** It is harder than fixing
it and more valuable. A defensive change to code that was already correct
looks like progress and leaves behind an error path that cannot occur.

**Verify against code or the host, never the PR body.** The body is the
author's belief. Read the diff, read the file, run the command. This catches
the specific class of error where the fix is right and the description is
wrong — and the reverse.

**Never re-run a test to make it green, and never quarantine one.** Read the
failure. If the suite is flaky enough that rerunning is reflex, that flake is
now the highest-leverage bug in the repo, because it is eroding this rule.

**Distinguish "the guard was off" from "something got through."** Every time
a missing check is found, these are two separate facts and the second must be
measured, not inferred from the first. Usually the answer is reassuring and
the report is stronger for having proven it.

**A suppression and the thing it suppresses are one change.** Wiring a check
and removing its allowlist entry ship together. Leave the entry behind and it
suppresses nothing today — but if that check is later removed or renamed, the
allowlist catches it on the way down and reports a regression as an
acknowledged gap.

**Check what a merge will actually close, not what its prose claims.** A
platform's closing-keyword parser is typically not negation-aware: a PR body
that says "does not close #N" still links and auto-closes #N, because the
keyword-then-number pattern matched regardless of the sentence around it.
Read the rendered list of issues a merge will close, not the words describing
it — and check the commit message too, since a squash merge folds it in.
Mechanics in [references/merge-safety.md](references/merge-safety.md).

**A "this would revert something" claim needs the merge attempted, not a
diff read.** Comparing two branch tips reports every commit one side lacks
as a deletion, whether or not merging removes anything — that is a property
of comparing tips, not a prediction about merging. When it matters, merge
into a scratch worktree and look, rather than trusting a diff reading;
mechanics and the exact pitfall in
[references/merge-safety.md](references/merge-safety.md).

**Serial work on shared files wants serial branches.** Cutting eight branches
up front that all edit the same file means every one after the first
conflicts. Cut the next branch after the previous merges.

**File an issue for anything parked**, and when an issue does not auto-close
on a squash merge, close it by hand *after* verifying the fix is on main. A
finding recorded only in a merged PR body is parked where nobody will look
for it again; an issue left open behind a shipped fix is the same defect
family in miniature.

### Instrument the rules rather than trusting them

Require every report to state the triaged-versus-real ratio and the file list
checked. A report that omits them is itself the degradation signal, and you
get that on every cycle for free instead of discovering it in an audit weeks
later.

This is the same principle as making an instrument capable of falsifying a
hypothesis before testing it, turned on the supervisor instead of the code.
It matters because these rules decay silently: the two worth watching are **a
hit is not a finding**, which fails first and is visible in the very next
report when a ratio disappears and volume starts standing in for judgement,
and **verify against code, never the PR body**, which is the last gate — when
it goes, nothing catches anything, and bad merges do not announce themselves.

## Anything probabilistic gets statistical honesty

State sample sizes before and after, and be willing to kill your own lead. A
flake investigation watched a file-level failure count fall from 4-in-30 to
1-in-30 and correctly refused to call it fixed: p=0.35, and 11-in-30 to
9-in-30 overall at p=0.78. A lead disproven with 30 runs behind it is real
progress, because it shortens the suspect list.

**Make the instrument capable of falsifying the hypothesis before testing
it.** In that same investigation the guard under test had no file output, so
"we never observed a violation" would have been indistinguishable from an
instrument that could not record one. Wiring durable evidence first is what
made the later negative result mean anything.

**Measurement batches run solo.** Two batches sharing a machine contaminate
exactly the timing-sensitive thing being measured.

## Reviewing a lane's work

Read the review *and* verify it. Confident, well-written, wrong is the normal
failure mode — for lanes, for external review bots, and for the supervisor.

Things worth checking every time:

- Arithmetic and counts. Re-count them yourself. A PR correcting a document
  *because* it carried a bad number is exactly where a fresh bad number ships.
- Whether the fix leaves the same defect one layer down.
- Whether a shared helper's new behaviour breaks a caller that did not change.
- Whether the change quietly narrows or widens a security boundary.

Send findings back rather than fixing them yourself, and tell the lane to
check your reasoning rather than take it. You will be wrong sometimes; a lane
that defers to you propagates it.

**A hypothesis you handed a lane that comes back refuted is a success.** A
suggestion from the reviewer is the easiest thing in the world to find
supporting evidence for, so a lane that declines — reporting that the code
path does not exist, with the reason — is worth more than one that delivers.

**Praise restraint explicitly.** That includes the refutation above, and a
lane declining to overturn an existing reasoned decision for lack of new
evidence. Say so out loud when it happens, or it stops happening.

## Lane mechanics

For pane targeting, send verification and clearing the input line, use the
[tmux skill](../tmux/SKILL.md) — it owns that ground and its rules are tested.
Three things here are not terminal mechanics and belong with the loop:

- **Idle detection is a correctness problem.** Getting it wrong costs cycles
  in both directions: stale scrollback made a finished lane read as working
  and it sat idle a full cycle, and a lane waiting on forked sub-agents read
  as idle and was nearly dispatched over. Check the live tail, never a
  keyword anywhere in the buffer. This generalises to any harness where a
  worker signals liveness through a rendered surface. The section below
  names the concrete states this looks like for a tmux-window-per-lane
  supervisor; treat it as one worked instance of this rule, not a separate
  one.
- **A lane that says it will wait and then ends its turn has stopped, not
  waited.** That is agent behaviour, not a terminal flag, and it cost four
  cycles across two lanes before it was diagnosed. Instruct lanes to block
  inside a single foreground command with a bounded polling loop, and never
  to end a turn whose only remaining step is waiting.
- **Give each lane a distinct surface** so two lanes never edit the same
  files. Parallelising a producer and its consumer ships a broken contract —
  the consumer merges before it knows about a new type.

Dispatch to an idle lane immediately; an idle lane is the only real waste.
For long tasks, state the goal, the ranking rule, the standard of evidence,
and the boundary you will not authorise crossing. Then let them work.

### The lane state machine (tmux-window-per-lane supervisors)

Where the lane protocol is `jonhill90/agent-supervisor`'s `lanes.sh`
(`scripts/supervisor/lanes.sh`), it is the probe, and this table is a
description of it, not the other way around — read the script when they
disagree. **Do not cite a fixed count for how many states it reports.**
The script's own header, its `AGENTS.md`, and a grep of its source have
disagreed with each other before (`agent-supervisor#131`, open) — a
number copied from any one of those goes stale the moment the script
changes. Verify coverage the same way: grep the script for the states it
assigns and diff that list against the table below.

| state | what it means | what an operator must NOT do |
|---|---|---|
| `free` | idle at the prompt, nothing delegated | do not treat it as an exclusive claim. A second, uncoordinated dispatcher may read the same table before you send (`agent-dotfiles#184`: the Director and the supervisor loop race on lane selection) — take the claim first, then dispatch. `lanes.sh`'s own comment on the supervisor window puts it plainly: "'Free' and 'yours to take' are different questions" |
| `busy` | mid-turn, recent tmux activity | do not dispatch — the brief queues behind the running turn |
| `hung` | looks busy, but tmux has seen no output for the hang window | do not dispatch — it would queue forever; needs a human |
| `menu-blocked` | waiting on a selection menu (folder-trust dialog, `/model`, a bash-permission prompt, `/theme`, or any unrecognised blocked shape — this is the default, not just one shape) | **never route free text here.** It lands as navigation keystrokes and the trailing Enter commits whatever option is highlighted — proven live, a routed reply changed a lane's theme instead of being read as an answer. This is the exact defect that, elsewhere, granted an agent filesystem read/edit/execute trust by typing a reply into a folder-trust dialog |
| `text-blocked` | waiting on a genuine free-text prompt | this is the one blocked state safe to answer with routed free text — but it has never been observed live in this estate; do not assume a blocked lane is this one without positive evidence, and the probe itself defaults to `menu-blocked` when unsure |
| `unsent` | a brief is typed into the input box and was never submitted | do not dispatch on top of it — a new brief lands behind stale unsubmitted text; a human needs to look |
| `broken` | the pane's working directory has been removed from disk, so it cannot start another turn | do not treat it as `dead` or `hung` — the harness process may still be alive, there may be no running turn to time out, and it will never read `free`. Re-home the pane into a directory that exists before doing anything else with it |
| `dead` | the pane's *current command* is a bare shell (`bash`/`zsh`/`sh`/`fish`/`login`) and its first process does not match the known-service whitelist, **and** its window name does not match the lane protocol's task-name pattern | restart the agent — but the whitelist (`LANES_SERVICE_RE`) is env-overridable and narrow (today, only `inbox-poll.sh`); a shell running some other long-lived script one whitelist entry away from `service` reads `dead` too. Confirm it is actually a lost agent, not an unlisted service, before restarting |
| `stale` | the pane's current command is that same bare shell, but its window name still matches the task-name pattern — it is a shell wearing the name of a task it finished or lost | do not trust the window name as a description of current work; it names a claim a human can leave behind long after the work it names ended. Restart it like `dead`, but do not let the name stand in for the ledger's own record of what the lane was doing |
| `service` | the pane's own first process matches the known-service whitelist (today, only `inbox-poll.sh`) | **never restart it as if it were dead.** `inbox-poll.sh` carries Jon's Telegram replies; restarting it looks exactly like nobody having written anything, because it silently stops the inbound channel instead of erroring |
| `scrolled` | the pane is in copy-mode (someone scrolled the scrollback up) | do not dispatch — keys are eaten by the copy-mode key table, not the agent, even when the visible text looks idle |
| `unknown` | no probe recognises the last line — a non-Claude-Code harness, or a footer shape not yet enumerated | do not guess free or dead; it needs a human to classify, not an assumption |
| `supervisor` | the supervisor's own window | never a dispatch target — a worker brief sent there `/clear`s the supervisor's own loop |

**The probe decides in a fixed order, and the first match wins** — it is not
independent per-state evaluation, so two orderings change what an operator
sees. `scrolled` is decided before any blocked check, so a `menu-blocked`
lane that someone scrolled up reads `scrolled` and is invisible to
`--blocked`, which the inbound reply router builds its table from. `broken`
is decided before the shell check, so a pane whose directory was removed
reads `broken` even if its current command is also a bare shell. And the
shell check (`dead`/`service`/`stale`) is decided before busy/blocked/free,
so none of those three can ever apply to a pane whose current command is a
shell.
`--free` offers only `free`. `--blocked` offers `menu-blocked` and
`text-blocked` together, tagged with which kind, because only
`text-blocked` is safe to answer with routed free text — but neither list is
an enumeration of every lane actually waiting on a human, because of the
ordering above.

**A window name is a projection of a record, never the record — and it is
never what makes a lane free.** Every read of it in this script stays
inside that boundary: `dead` vs. `stale` among shells is decided by whether
the name still matches the task-name pattern, and, separately, a bare-shell
pane whose own process is gone can still read `service` rather than `dead`
if the name matches the estate's one hardcoded poller window — a narrow
fallback for the gap where the pane's own process can't answer the question
at all. Neither read stands in for the ledger's record of what a lane was
doing, and neither one can produce `free`: that state comes only from tmux's
own pane facts or a positive text match. **Do not cite a count of how many
places read the name** — verify it yourself the same way, by finding every
reference to the name variable in the script, the same drift this table
already warns about for the state count. That is a fact about this probe,
not a claim about the rest of the estate: `agent-dotfiles#194` argues a
different call site (`lane-done.sh`'s own completion rename) is still
load-bearing rather than cosmetic.

## When everything left is blocked

**A gate on a human is often true of one verb, not the whole item.** Before
recording something as blocked, name the specific verb that is gated — the
rest is often ordinary, un-gated work. The split recurs in the same shape:
run vs. write, decide vs. prepare, deploy vs. build, measure vs. explain.
One worked case: an item read as fully blocked because every option it
proposed needed a billed baseline the owner had to authorise — true, and it
hid a free deliverable the same item's own text named. Recording the whole
item as blocked and moving on looks like discipline and is how work quietly
stops; state which part was gated and which part was done, every time.

**Blocked is a state to sleep through, not a reason to stop the loop.** When
every remaining item is genuinely gated, say so in one line and schedule the
longest available wakeup — never invoke the loop's own stop primitive over a
blocked backlog. This is loop-contract's `blocked-needs-human` terminal
state applied literally: a *state* the loop reports and continues past, not
an *exit*. Stopping requires a human to notice on their own and re-arm the
loop by hand, which defeats the reason it runs unattended. A blocked firing
should also be cheap — compare against what is already recorded and sleep if
nothing changed, not a fresh analysis of an already-settled question.

## Reporting to the human

One or two lines when nothing needs them. The value of a quiet report is that
a loud one means something.

Escalate only what genuinely needs a decision: an irreversible action, an
outward-facing change, a security finding with real blast radius, or a fork
where either branch is defensible.

**Escalate as a fork with a recommendation, never as an open question.** The
useful form is: here are the two branches, here is the cost of each, here is
what I would do.

Report outcomes faithfully. Failures with their output, skipped steps named
as skipped, and boundaries stated — "this proves the message reached the mail
server, not an inbox" is worth more than a clean claim.

## Where this came from

The single-writer loop-pane rule, the gated-verb split, the never-stop-on-
blocked rule, and the two merge-safety checks above are drawn from operating
a tmux-window-per-lane supervisor loop over multiple days on one estate,
recorded in `jonhill90/agent-supervisor` (private). That repository's own
tick document names its estate's scripts, paths, and issue history directly
because that coupling is real and load-bearing there; nothing here depends
on it — this skill states the principle and stops. Treat the specifics
(which verbs recur, how long a wakeup to schedule) as one estate's evidence,
not a universal constant.
