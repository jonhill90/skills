# Prompt (longitudinal, two sessions per arm)

This scenario is the longitudinal alternative `docs/eval-harness-findings.md`
§4 recommended and `docs/eval-longitudinal-design.md` specifies, run once,
against `loop-memory` specifically -- see that design doc for why this
skill was the first candidate. It replaces `loop-memory`'s original
single-turn pass-12 scenario (`could_not_measure`, #230 pass 12); this is
not a second independent run of the old design, it is the harder
instrument the old result's own write-up asked for.

## Setup

`fixture/` is the seed state, identical for both arms: a git repo with
`src/01.cfg`-`12.cfg` (twelve legacy config files) and `dest/01.json`-
`04.json` (four already migrated, correct). Copy it twice before running
anything -- `sandbox-with/` and `sandbox-without/` -- so the two arms
never share mutable state.

Two files in `src/` (`06.cfg`, `11.cfg`) contain a value with a literal
`#` character *inside* it, not at the start of a line. Nothing in
`TASK.md`, the fixture, or either prompt below calls this out -- it is
discovered by running the work, not announced up front, matching the
design doc's "pressure introduced partway through, not stated at the
start" requirement. `06.cfg` lands in session 1's batch, `11.cfg` in
session 2's, in both arms, so the same specific mistake is available to
repeat, not just a same-shaped one.

## Session 1 (both arms: fresh subagent, `TASK.md` + this message)

> `TASK.md` in this directory describes a config migration. Items 01-04
> are already done -- verify on disk before continuing, don't just trust
> the note. Migrate items 05-08 next. Use `migrate_check.py` to check
> your own work as you go.

**With-skill arm only:** also given `loop-memory`'s own `SKILL.md` as
context, told to follow it for this session.

**Without-skill arm:** no mention of `loop-memory`, no skill content
loaded. Otherwise identical fixture, identical task message.

**Partway through session 1** (after item 06 has been attempted, before
item 08 is reached -- send as a follow-up message in the same
conversation, not a second subagent), both arms receive:

> [SYSTEM] Context is at 91%. Compaction or a restart is imminent. The
> next instance that picks this work up will have no memory of this
> session -- finish or abandon whatever you're mid-item on, then leave
> whatever that next instance will need, and stop.

This is the one deliberate asymmetry from a plain harder-single-shot
scenario: the pressure is a mid-session interrupt, not a fact stated in
the opening prompt, and what "leave what's needed" means is left to each
arm's own judgment -- the with-skill arm has `loop-memory`'s file-set
guidance to draw on (progress, decisions, known failures, receipts,
handoff); the without-skill arm does not.

## Session 2 (both arms: a BRAND NEW subagent -- no conversation
## continuity with session 1, only whatever session 1 left on disk)

> Continue the migration in this directory. Check disk for anything a
> prior session may have left before starting -- don't assume there's
> nothing there, and don't assume anything you find is still accurate
> without checking it against the repo's actual state. Migrate items
> 09-12. Use `migrate_check.py` to check your own work as you go.

**With-skill arm:** also given `loop-memory`'s own `SKILL.md` again (a
fresh instance following the skill has no memory of having been told
this before -- the skill has to be re-supplied, matching how the skill
itself would actually be reloaded at the top of a new loop iteration in
real use, not carried in context from a session that no longer exists).

**Without-skill arm:** same as session 1 -- no skill content.

No mention of `06.cfg`'s mistake, if one happened, or of session 1's
transcript. Session 2 has access to nothing but the fixture directory as
session 1 left it.

## Why this counts as one longitudinal probe, not two single-shot runs

Session 2 is not scored on the migration task alone -- it is scored on
whether it re-derives, from a cold start, work session 1 already paid to
learn (see `criteria.md`). A two-arm design that only ran session 1 would
be exactly the design `docs/eval-harness-findings.md` already found
insufficient for this skill class.
