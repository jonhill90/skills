# Eval result

Recorded 2026-08-23, jonhill90/skills#230's evaluation loop, following
pass 15 (`docs/eval-pass15-remaining-four.md`, PR #250) which named
`tmux` as the last of the four remaining `unevaluated` skills, mechanically
blocked by an install-parity divergence rather than by scenario design.

## Verdict: could_not_measure (n=1) -- with a methodology confound, stated plainly

## Part 1: the install-parity fix (a real, verifiable resync)

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

## Part 2: the eval attempt, and why it's a weaker signal than it looks

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

## Why this is `could_not_measure`, not `keep`

The specific failure this skill exists to prevent did not occur in either
arm -- the outcome axis did not move.

## The confound this pass surfaces, not papered over

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

## What is not evidenced

Whether a run that actually has the skill's content in context (e.g. via
the private harness's own proper stash/restore mechanism against a real
installed-vs-stashed skills path, or the skill's `SKILL.md` pasted
directly into the arm's prompt) would out-perform the no-skill arm on
this or a harder-shaped scenario. A scenario for `tmux` already exists in
`jonhill90/agent-evals` (not publicly available) for exactly this, unrun
as of this pass -- the concrete next step, once its provenance is
confirmed clean rather than run blind over another lane's possible
in-flight state.

## What I did NOT do

- Did not run or commit anything in `jonhill90/agent-evals` -- its
  uncommitted local scenario state was of unclear origin and not safe to
  build on top of unverified.
- Did not claim the skill "does nothing" or propose `drop` -- one
  confounded pair on one scenario shape settles neither.
- Did not modify any other skill's verdict or log.
