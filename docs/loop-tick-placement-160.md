# Should `loop-tick.md` move from `agent-dotfiles` into this repo? (#160)

Investigation only, per #160's own instruction — no files move here. Same
discipline agent-dotfiles#143 and #161 used: measure, answer the three named
questions, recommend, and let Jon decide before anything moves.

Read directly: `agent-dotfiles/scripts/supervisor/loop-tick.md`, measured
2026-08-12 at **540 lines** (`wc -l`) — up from the 527 the issue cites when
it was filed, itself a small data point about how often this file changes.

## 1. Is it one skill, or a skill plus references?

This repository's own stated cap, from `create-skill/SKILL.md`: "Keep the
main file under 500 lines." `loop-tick.md` at 540 already exceeds that
before any reference material is even split out. The largest skills already
here split main file plus `references/` — `github-cli` (411 lines main),
`tmux` (381), `linear` (355), `close-the-loop` (223), `obsidian` (243),
`supervised-lane-loop` (270) — so size alone says split, not "leave as one
file."

But splitting by length is the wrong cut for this file. `references/` in
this repo's existing skills holds *background* material — provider tables,
advanced flag references, less-common procedures a reader skips on a normal
pass. `loop-tick.md` is not that shape: pull any section out — the
lane-health check, the claim/dispatch sequence, the revert-diff reasoning,
the completion-rename waiter — and every one of them is load-bearing
procedure, not background. There is no low-traffic 340 lines to defer behind
a "loaded on demand" reference; nearly the whole file is the thing an agent
needs on every tick. Progressive disclosure does not resolve this file's
size problem, because its size problem is not "too much detail," it is
"too much of it is specific to one estate's toolchain" — which is question 2.

One relevant precedent already in this repo: `tmux/references/
supervisor-lanes.md` covers agent-supervising-agent tmux patterns —
upward prompt flow, a generic watcher loop, `/loop` mechanics. Read in full:
it is deliberately generic (`workflow:agents.{bottom}`, a
`supervisor-watch.sh` that does not exist in `agent-dotfiles`), not this
estate's actual `lanes.sh`/`dispatch.sh`/`claim.sh` machinery or its exact
state names. No overlap, no duplication — it answers "how do I supervise a
pane at all," not "how does this estate's supervisor loop run." Worth
knowing before assuming a `loop-tick.md` move would consolidate with
something already here; it would not.

## 2. Name or contract — the crux, measured

Counted directly against the file, not estimated:

| what | count |
|---|---|
| references to this estate's own `*.sh` scripts by name (`dispatch.sh`, `lanes.sh`, `claim.sh`, `worktree.sh`, `lane-done.sh`, `director-inbox.sh`, `advance-live.sh`, `would-revert.sh`) | **36**, across all 8 |
| issue numbers cited | **35** mentions, **25** unique |
| code fences with literal commands, exact paths, exact flags | **26** |

That is not a file that describes a contract in the abstract and cites tools
as an example. `dispatch.sh 81 dispatch-worktree ~/.local/state/agent-
dotfiles-supervisor/ad81-brief.md jonhill90/agent-dotfiles ~/source/repos/
Personal/agent-dotfiles` is not a pattern, it is this machine's actual path
and this repo's actual name, typed as the thing to run. The state names
(`free`, `busy`, `hung`, `dead`, `service`, `unknown`, `blocked`,
`menu-blocked`) are `lanes.sh`'s own literal vocabulary, not a described
interface a differently-named tool could also satisfy. The incident
citations (#73, #81, #89, #99, #102, #108, and 19 more) are `agent-
dotfiles`' own history, load-bearing as the *reason* for each rule, and
meaningless without that repository's issue tracker.

Compare this repo's own `loop-contract/SKILL.md`, which already faces the
identical tension — its evidence also comes entirely from `agent-dotfiles`
(the twelve-field contract, the cron-as-stall-detector rule, the measured
defect behind it) — and resolves it differently: the skill body stays
abstract ("cron is a stall detector, never the driver, wherever a
supervisor/worker pattern already holds the loop's state"), and a single
"Where this came from" section at the end *cites* `agent-dotfiles
docs/SPEC.md §14` and `agent-dotfiles#22` as the evidentiary source, once,
without the skill's operational content depending on that repo's file
layout, script names, or issue numbers to be usable. `loop-tick.md` does
the opposite of that on every page: the citation and the instruction are the
same sentence, 36 and 25 times over.

**This is the crux, and it resolves against the move weakening the coupling
objection.** The tick describes almost everything by name, not by contract.
A future rename of `dispatch.sh`, a renamed lane state, or a retired issue
number would each independently break passages of a moved copy with nothing
short of the current single-repo, single-commit discipline catching it —
which is exactly the failure #158 already measured happening to the skills
that already try to describe this material from a different repo (see the
table below).

Independently corroborates #158's own claim, extended: of the three lane
states `#158` says are new since `supervised-lane-loop` was last touched
(`blocked`, `menu-blocked`, `service`), a fresh search across every `SKILL.md`
and reference in this repo finds `busy`, `service`, and `menu-blocked` in
**zero** skills — `blocked` and `hung`/`dead`/`unknown` appear, but not in
`lanes.sh`'s specific sense, in a handful of unrelated skills
(`notify`, `loop-memory`, `verify-the-instrument`). The drift #158 named is
real and current, not historical.

## 3. What breaks on day one

`SUPERVISOR_TICK` is real and does exactly what the issue suspects.
`agent-dotfiles/scripts/supervisor/watchdog.sh:51`:

```bash
TICK="${SUPERVISOR_TICK:-$HERE/loop-tick.md}"
```

and its only use, `watchdog.sh:568`, embeds it as a plain string in the
`/loop` prompt text: `"Follow $TICK exactly."`. `watchdog.sh` never reads,
parses, or executes the file — it only tells the supervisor pane where to
`Read` it. So redirecting where the tick lives is genuinely a one-line
environment-variable change with **zero** code change to `watchdog.sh`,
confirmed by reading the only two lines that touch it. The issue's intuition
is correct on this narrow point.

What is not free is what `SUPERVISOR_TICK` would need to point *at*, and
this repository's own policy makes that a real decision, not a formality.
Checked directly against `agent-dotfiles/settings/default-skills.txt`:
every skill in `[benched]` — eleven of them, including recent ones like
`loop-contract` and `keep-me-honest` — is withheld from the installed
roster by explicit policy, quoting the file itself: *"nothing joins the
roster on evidence credit until it clears failed x2 baseline, passed x3
with the model pinned, and a counter-scenario at x2."* A newly-authored
`loop-tick` skill would start there. That means a plain `git mv` into this
repo, even after `agent-dotfiles`' pinned `apm.yml` ref is bumped to the new
commit and `apm install -g` / `scripts/sync.py apply` actually run, would
**not** put the file anywhere `SUPERVISOR_TICK` could point to via the
normal installed-skill path (`~/.claude/skills/<name>/SKILL.md`,
`~/.agents/skills/<name>/SKILL.md` — both confirmed to exist on this
machine today, for the currently-rostered skills only) unless the estate's
own operating loop is treated as an explicit exception to its own evidence
bar, or someone hand-installs it outside the roster.

The alternative — point `SUPERVISOR_TICK` at a raw checkout path in a
sibling `Skills` clone, the same way `watchdog.sh` already resolves its own
`$HERE` — sidesteps all of that and is genuinely trivial. But it also
skips the entire mechanism "being a skill" is for: it is not `npx skills`-
installable, it pins nothing, and no other consumer benefits, because a
hardcoded local clone path is not a portable install. Either path is
workable; which one is intended is a decision this issue's answer needs to
name, not something a move can leave implicit — the roster path has a real
governance cost this repo already imposes on itself, and the checkout path
opts out of the reason this repo exists.

## A fourth question neither side of #160 named: does this content belong here at all?

This repository's own `AGENTS.md` and `README.md`, verbatim: *"Nothing here
depends on any particular harness, personal dotfiles, or private evaluation
tooling"* and *"Personal harness configuration ... lives in Jon's separate
`agent-dotfiles` repository, which consumes this collection rather than
vendoring it."*

`loop-tick.md`, as written today, is exactly that — personal harness
configuration for one specific estate. It names Jon by name, the Director by
name, four specific repositories by name, eight of this estate's own scripts
by name, and 25 of that estate's own issue numbers. It is not "instructions
an agent loads on demand" in the portable sense the rest of this repository
means by that phrase; it is agent-dotfiles' own operations manual, written
in markdown instead of bash only because prose was the right tool for that
content, not because it is meant to travel.

This repo has already drawn this exact line once and gotten it right:
`loop-contract` extracts the portable *shape* of a supervisor loop
(twelve-field contract, autonomy staging, treat-payloads-as-untrusted) and
leaves the estate-specific evidence as a citation. `loop-tick.md` is the
other half of that same tension — the concrete instance the contract is
distilled *from* — and the concrete instance is exactly what this
repository's own scope section says stays where the code is.

## Recommendation

**Do not move `loop-tick.md` as written.** Question 2's measurement resolves
the crux against the move — the coupling objection is not weakened, it is
confirmed, at 36 script-name references and 25 unique issue citations. Moving
it unmodified would also cross this repository's own stated scope boundary,
independent of the coupling question.

The productive path is the one `loop-contract` already demonstrates working:
extract the portable *principles* `loop-tick.md`'s incidents taught — a
tri-state (or richer) lane-health check before dispatching to anything, never
trust an unresolved empty target, claims expire with the process rather than
a clock, verify a "would this revert" claim by attempting the merge rather
than reading a diff, a completion signal tied to the one event that cannot
fire early — written generically, the way `loop-contract` and `tmux/
references/supervisor-lanes.md` already are, citing `agent-dotfiles` once as
where the evidence came from. The concrete, executable tick — script names,
exact paths, the 25-incident history that justifies each rule — stays
versioned with the code in `agent-dotfiles`, where that coupling is real and
currently load-bearing.

If that extraction happens, question 3 still needs an explicit answer before
anything is wired: whether `SUPERVISOR_TICK` should point at an installed,
rostered skill (real portability, real governance cost — the new skill starts
benched under this repo's own evidence-bar policy) or a raw sibling-checkout
path (trivial, but not portable to any other consumer). This document does
not pick one.

None of this is written here. A follow-up issue, scoped to whichever
principles are worth extracting, does the actual authoring — in this
repository, following `create-skill`'s own contract, not as a copy of
`loop-tick.md`.
