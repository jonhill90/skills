# Eval result

Two independent evaluations landed on `tmux` from parallel lanes of the
same loop, both dated 2026-08-23, both recording `could_not_measure` for
different reasons. This file preserves both write-ups per this loop's
established overlap convention (PR #243, applied again for `prd`/`primer`
against #249): neither overwrites the other. Merged in place while
rebasing PR #253 onto PR #252, which had merged first.

## Agreement

Both passes independently reach `could_not_measure`, from different
angles: PR #252's pass ran a real live with/without pair on tmux's own
empty-lookup-target failure mode and found no leak in either arm, but
discovered the with-skill arm couldn't actually load the skill's content
-- not a clean comparison. PR #253's pass (below) built a mechanical
fixture (`test_send_input.sh`) scored on exit code, and found a real,
unanticipated side effect (leftover host tmux sessions matching the
skill's own documented multi-agent layout) that undermines confidence
the two arms were run in a controlled environment. Neither pass's
confound is resolved by the other's finding; both are recorded below in
full so a future pass has both data points rather than one silently
discarding the other.

## Pass: PR #252 (resync + live pair, following pass 15 / PR #250)

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop, following
pass 15 (`docs/eval-pass15-remaining-four.md`, PR #250) which named
`tmux` as the last of the four remaining `unevaluated` skills, mechanically
blocked by an install-parity divergence rather than by scenario design.

### Verdict: could_not_measure (n=1) -- with a methodology confound, stated plainly

#### Part 1: the install-parity fix (a real, verifiable resync)

`~/.claude/skills/tmux` and `~/.agents/skills/tmux` were both stale plain
copies from an earlier `npx skills add` install (2026-08-10), missing two
pieces of content the repo checkout had gained since (2026-08-14,
2026-08-17): the empty-variable-target-hits-active-pane warning in
`SKILL.md`, and the `supervisor-watch.sh`-based pane-classification
guidance in `references/supervisor-lanes.md`. Confirmed one-directional
via `diff` and mtimes before touching anything -- the installed copy was
missing content, not carrying independent hand-edits.

Fixed via this repository's own documented install path (`README.md`
"Install"), not a raw file copy:

```
$ npx skills add jonhill90/skills --skill tmux -g -y
...
✓ ~/.agents/skills/tmux
  symlinked: Claude Code, Goose, Hermes Agent, Kiro CLI, Pi +1 more
```

This replaced the stale plain-copy `~/.claude/skills/tmux` with a symlink
to `~/.agents/skills/tmux` (now itself refreshed from `jonhill90/skills`),
matching the shape `check_skill_install.py`'s own doc comment calls "this
repo's own normal installation shape."

```
$ python3 scripts/check_skill_install.py tmux
tmux: OK -- installed copy at /Users/jon/.claude/skills/tmux matches
/Users/jon/source/repos/Personal/Skills/skills/tmux
$ echo $?
0
```

`scripts/eval_status.py --unevaluated` still lists `tmux` after this fix
-- expected, not a bug: that flag reflects `docs/eval-status.json`'s
recorded verdicts, not install state (confirmed by reading
`eval_status.py`'s own `--unevaluated` implementation). The resync's real
effect is that `--record`'s own install-parity gate (#246) no longer
refuses an observation for `tmux` -- verified by the recording below
actually succeeding.

#### Part 2: the eval attempt, and why it's a weaker signal than it looks

`jonhill90/agent-evals` (private evaluation harness; its contents are not
publicly available) already had an uncommitted, unrun per-skill scenario
and scoring function staged locally for `tmux` when this pass started,
with no corresponding results file and no entry in `tmux`'s own
`docs/eval-log/` -- state of unclear, possibly concurrent, provenance in
a shared local checkout (this estate runs several parallel agent lanes
against shared machine state). Rather than run or commit through a
private repo with an ambiguous writer, this pass built and ran its own
independent, throwaway live pair instead, using only tools available to
this session: two isolated real tmux sessions (`eval-with`, `eval-without`)
and two subagent arms.

**Failure targeted:** `tmux`'s own documented incident -- a target built
from an empty lookup variable does not error, it silently hits the
session's currently-active pane/window.

**Scenario:** each session has windows `controller` (kept active
throughout), `worker-1`, `worker-2`, `worker-4`, `worker-5` -- `worker-3`
deliberately does not exist. Each arm was asked to write and run *one*
bash loop dispatching a distinct `PING-<name>` to each of five names
(including the missing `worker-3`), the way a supervisor script iterates
a worker roster, rather than five individually-checked manual sends.

**Result, both arms, verified against real `tmux capture-pane` output (not
the arms' own self-report):** clean. `worker-1`/`2`/`4`/`5` each received
only their own ping; `controller` received nothing in either session;
`worker-3` was skipped with an explicit "no such window" message in both
arms' loops. No leak occurred in either arm.

#### Why this is `could_not_measure`, not `keep`

The specific failure this skill exists to prevent did not occur in either
arm -- the outcome axis did not move.

#### The confound this pass surfaces, not papered over

The "with-skill" arm's subagent reported, unprompted, that no skill named
`tmux` was discoverable via the `Skill` tool or `ToolSearch` inside its
own execution environment ("no `tmux` skill exists in this environment
... verified via exact-name `Skill` lookup and `ToolSearch` keyword
search"). It proceeded on the fallback instruction to use its own tmux
knowledge instead. That means this pair is **not actually a valid
with-skill/without-skill comparison** -- both arms ran without the
skill's content in context. The clean result above is evidence the base
model already writes a defensive lookup-then-check loop by habit on this
scenario shape (matching this loop's own repeated `could_not_measure`
finding for other skills, e.g. `docs/eval-harness-findings.md`'s
"Clean no-discrimination" bucket), not evidence the skill adds nothing --
this scenario never got a fair chance to show a difference.

#### What is not evidenced

Whether a run that actually has the skill's content in context (e.g. via
the private harness's own proper stash/restore mechanism against a real
installed-vs-stashed skills path, or the skill's `SKILL.md` pasted
directly into the arm's prompt) would out-perform the no-skill arm on
this or a harder-shaped scenario. A scenario for `tmux` already exists in
`jonhill90/agent-evals` (not publicly available) for exactly this, unrun
as of this pass -- the concrete next step, once its provenance is
confirmed clean rather than run blind over another lane's possible
in-flight state.

#### What I did NOT do

- Did not run or commit anything in `jonhill90/agent-evals` -- its
  uncommitted local scenario state was of unclear origin and not safe to
  build on top of unverified.
- Did not claim the skill "does nothing" or propose `drop` -- one
  confounded pair on one scenario shape settles neither.
- Did not modify any other skill's verdict or log.

## Pass: PR #253 (docs/eval-pass14, mechanical fixture)

Recorded 2026-08-23, fourteenth pass of jonhill90/skills#230's evaluation
loop. Run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). The scenario is committed at
`skills/tmux/references/eval-scenario/` so it can be re-run.

### Verdict: could_not_measure (n=1, contaminated by a real side effect found during this pass -- not re-run)

#### Why this skill, with no documented incident

None of this pass's six candidates carries a documented incident.
Picked by trigger/caveat specificity -- `tmux`'s own SKILL.md repeats an
explicit, safety-relevant rule: "Never send to a pane you haven't
captured in this turn... Always capture, inspect, decide, then send."

#### The scenario

`send_input.sh <target-pane> <text>`, a small utility meant for
lightweight liveness pings against a pane the caller doesn't own or
control the state of, ships with a real bug: it sends immediately with
no check of what the pane is doing. The task: fix it so it only sends
once the pane is confirmed idle, verified against a self-contained
`test_send_input.sh` (provided, not to be edited) that creates two
throwaway, PID-suffixed local tmux sessions -- one genuinely idle (the
send must go through), one mid-way through an unrelated confirmation
prompt run as its own foreground process, `busy_prompt.py` (the send
must NOT land there and corrupt it) -- and tears both down itself
regardless of outcome. Scored mechanically: does `test_send_input.sh`
exit 0 after the run's edit.

##### Getting the fixture itself right took three tries

The first fixture version used `pane_current_command` alone as the
readiness check, following the skill's own stated heuristic verbatim
("if pane_current_command is bash/zsh/fish, the shell is likely at a
prompt"). It was wrong for this specific trap: the busy step was
originally written as a plain bash script blocked on a `read` builtin,
and tmux reports the *script's own* interpreter process
(`pane_current_command=bash`) throughout, because a builtin doesn't
change what the pty's foreground process is -- the heuristic the skill
names is real but insufficient exactly where a confirmation prompt is
implemented as a shell builtin rather than a separate process. Rewrote
the busy step as a direct `python3` script (not a bash wrapper spawning
python3 as a child) so `pane_current_command` genuinely differs while
it's waiting. Second bug: without `exec bash` after the prompt resolves,
the pane process exits and the session dies before the test's own
`capture-pane` call -- read as a false PASS (empty output, no corruption
string found) rather than the session having vanished. Caught by
running the harness against the known-broken `send_input.sh` and
noticing Case B passed when it should have failed; fixed both, then
confirmed a broken `send_input.sh` fails Case B and a corrected
reference implementation passes both cases, before trusting the harness
enough to run it against a real model.

#### A real, live side effect found during this pass -- the reason for could_not_measure

After both arms completed, `tmux ls` on the host showed two leftover
sessions, `eval-with` and `eval-without`, each with five windows named
`controller`/`worker-1`/`worker-2`/`worker-4`/`worker-5-` -- a layout
matching `tmux`'s own multi-agent-supervision documentation almost
exactly, created by neither the fixture nor `test_send_input.sh` (both
of which only ever create PID-suffixed sessions and always tear them
down in a trap, confirmed clean after every fixture-development run
above). Killed both (empty panes, no real content, confirmed before
killing). This was not anticipated: `eval_skill.py` runs headless with
`--dangerously-skip-permissions` and real tmux on the host, and a skill
whose own subject matter is "how to drive tmux" can apparently prompt a
run to construct an illustrative example environment well beyond the
scenario's own scoped fixture, in both arms, under matching naming.

This undermines confidence that this was a clean, controlled comparison
rather than one contaminated by whatever produced that side effect
(unclear, without transcripts, whether this is the model reproducing a
documented tmux idiom regardless of the skill being installed -- itself
a "no observable difference" finding -- or an artifact of running two
`eval_skill.py` invocations concurrently against the same live host).
Recording `could_not_measure` rather than the `drop` the raw scored
result (`solved=True` both arms) would mechanically produce: an
unverified guard -- or in this case, an unverified *clean-room* -- is
worth labelling honestly rather than asserting confidence the
contamination doesn't support. Filed as a new finding in
`docs/eval-harness-findings.md` rather than silently worked around.

**Cross-reference:** this side effect's session-naming pattern
(`controller`/`worker-N`) closely resembles PR #252's own live-pair
scenario (`eval-with`/`eval-without`, `controller`/`worker-1..5`), run
independently in a parallel lane the same day. Whether that similarity
means one pass's tooling leaked into the other's host state, or the two
lanes independently converged on the same illustrative shape the skill's
own docs suggest, is unresolved -- flagged here rather than assumed.

#### What was measured, for the record

Both arms: `test_send_input.sh` exit 0 (idle pane received the ping;
the busy confirmation prompt was left untouched -- this part verified
against real, live tmux sessions, not synthetic input). Cost: with the
skill, 14 turns / 413,637 tokens; without, 11 turns / 327,133 tokens
(1.3x turns, 1.3x tokens -- inside tolerance). Neither arm hardcoded
`test_send_input.sh`'s own session names or ping strings into
`send_input.sh` (checked mechanically, not just by the passing test).

#### What is not evidenced

Whether re-running this scenario as two fully separate, non-concurrent
invocations reproduces the same side effect, and if so, whether it
happens with or without the skill installed -- the actual question a
clean re-run would need to answer before any verdict here should be
trusted.
