---
name: organize-repository
description: Decide where code, tests, docs, scripts, config, and generated files belong in a repository, so placement stays predictable across projects instead of being re-decided each time. Use when starting a repository, adding something whose home is not obvious, adding a documentation site such as Mintlify, moving or retiring files, auditing a layout for drift, or writing a repository's layout rules into AGENTS.md. Not for choosing application architecture or dependency boundaries.
---

# Organize a Repository

Every "where does this go?" answered from scratch is friction, and every
answer that differs from the last one is drift. Give each kind of file one
predictable home, follow the tools' own rules where they have them, and
write down the exceptions so they are not mistaken for drift later.

## Reach for this when

- Starting a repository, or adding its first test, doc, script, or config.
- Adding a file and more than one location looks plausible.
- Adding, replacing, or removing a documentation site.
- Moving, renaming, or retiring files other things might point at.
- Asked to audit, tidy, or standardize a repository's layout.

Do not reach for this to design module boundaries, layering, or dependency
rules inside the code — that is architecture, not placement. Do not reach
for it when the repository's own `AGENTS.md` already names the home for the
thing at hand; follow that.

## Routine

1. **Read before placing.** Read the root `AGENTS.md`, the docs index, and
   any decision records about layout. A documented decision outranks every
   default below, including one that looks inconsistent with other repos.
2. **Identify the profile and the tools.** Match the repository to a profile
   in [references/profiles.md](references/profiles.md). Note every tool with
   path rules of its own: language build/test tools, docs renderers,
   deployment tools. Tool-native layout outranks these defaults.
3. **Classify the thing.** Code, test, doc (which audience), script,
   config, generated output, or research. Most placement confusion is two
   of these being treated as one.
4. **Place it by the rules below.** If two homes still fit, pick the one a
   stranger would look in first, then record why.
5. **Record exceptions.** A deliberate deviation goes in a decision record
   with its reason. An unrecorded deviation is drift, and will be "fixed"
   by the next agent.
6. **Verify.** Run `scripts/check_layout.py`. Confirm tests are still
   discovered by the runner, links resolve, and anything moved still has
   its consumers updated (see [references/moving-files.md](references/moving-files.md)).

## Rules

Common to every repository:

- **Entry points.** `README.md` at the root for humans. `AGENTS.md` at the
  root for agents, as the real file; `CLAUDE.md` is absent, a symlink to
  it, or starts with `@AGENTS.md`. State in `AGENTS.md` only the rules an
  agent would get wrong from the tree alone — a tour of the directories
  does not help agents.
- **One home per fact.** A rule or explanation lives in one maintained
  place; everything else links to it. A README that restates the docs is
  how the docs go stale.
- **Tests mirror source.** `tests/<same path as src>/test_<name>.py`, with
  `--import-mode=importlib` set for pytest. Go, Rust, and JS/TS frameworks
  with a native convention for tests keep that convention.
- **Maintainer docs never move for a renderer.** Docs about building,
  running, and deciding live directly under `docs/`, indexed by
  `docs/README.md`. A published site gets its own root beside them (see
  [references/documentation-sites.md](references/documentation-sites.md)),
  so adding, swapping, or removing a renderer touches only that root.
- **Decisions are superseded, not deleted.** Mark the old record with what
  replaced it. Other retired documents are deleted; git history is the
  archive. Leave a pointer only when something outside the repository still
  reads the old path.
- **Scripts are for repeated operations.** Repository-wide scripts in
  `scripts/`; scripts owned by one component live with that component.
- **Generated output is labelled.** Either gitignored, or committed under a
  directory whose README (or the docs index) names the generator and says
  not to hand-edit.
- **Directories are created when needed.** No placeholders. A topic starts
  as one file (`docs/development.md`) and becomes a directory when a second
  document arrives.
- **Lowercase, hyphenated names** for directories you create. Tool-required
  names (`SKILL.md`, `Dockerfile`, `ROOT`) keep their required form.

Varies by profile or tool — decide from
[references/profiles.md](references/profiles.md) and the tool's docs, not
from another repository's tree:

- whether code lives in `src/`, `services/`, or tool-defined directories;
- the docs taxonomy the repository declares in `docs/README.md`;
- manifest names and locations;
- test location in ecosystems with a native convention.

## Checking

`scripts/check_layout.py [root] [--json]` reports what a script can decide:
missing entry points, an inverted or drifting `CLAUDE.md`/`AGENTS.md`
pair, placeholder directories, test file names pytest cannot collect, and
Mintlify pages that are published by URL without being in navigation.
Exit `0` means no errors, `1` errors, `2` could not check. It does not judge
whether something is in the right home; that stays with the routine above.

## When the answer is still unclear

Do not invent a new top-level directory to avoid choosing. Put the file in
the nearest existing home, note the ambiguity in the pull request, and
propose a rule for the repository's `AGENTS.md` so the question is answered
once.
