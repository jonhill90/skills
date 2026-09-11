# AGENTS.md

## Project

`skills` is Jon Hill's public collection of portable [Agent
Skills](https://agentskills.io/specification) — model- and
provider-agnostic instructions an AI coding agent can load on demand.
Each skill is self-contained: a `SKILL.md` plus optional `scripts/`,
`references/`, and `assets/`. Nothing here depends on any particular
harness, personal dotfiles, or private evaluation tooling.

This file is the shared repository policy. `CLAUDE.md` and
`.github/copilot-instructions.md` are committed **symlinks** to it, so
each harness reads its own filename and there is one source. Edit this
file; the other two follow with no sync step.

## Scope

- This repository holds only portable skill content plus the minimal
  validation, tests, and CI needed to keep that content correct.
- Personal harness configuration (instructions, hooks, agents, settings,
  MCP declarations, install/sync tooling) lives in Jon's separate
  `agent-dotfiles` repository, which consumes this collection rather than
  vendoring it.
- Behavioral evaluation methodology, scenarios, transcripts, and results
  live in a private companion repository. None of that is published here.
- Employer-owned or project-specific material is never copied into this
  repository.

## What "shipped" means

Merging a skill here does not install it anywhere. This repository has no
install gate of its own — a merged, CI-green skill is published and
installable (`npx skills add`, or as an Agent Plugin), and that is the whole
of what this repository controls.

Whether a harness loads it automatically is a **separate, later decision**
made in a different repository: Jon's `agent-dotfiles`
(`settings/default-skills.txt`) rosters the subset it installs by default
for his own harnesses, per its own evidence bar (SPEC §10.1 rule 5) — a new
skill does not earn a roster slot by arriving here. `default-skills.txt`
also carries a `[benched]` section recording, per skill, that withholding it
was a deliberate decision rather than an oversight.

Concretely, for a skill authored here: merged and un-rostered is the normal
resting state for a brand-new skill, not a bug — but merged, un-rostered,
and **un-benched** is exactly the failure jonhill90/skills#162 measured
(eleven skills, 2026-08-11, installed on no harness, with no record either
repository could point to). `scripts/check_orphan_skills.py` (see "Orphan
skill check" below) is this repository's own advisory view into that
question; it cannot roster or bench anything itself.

### Orphan skill check

`scripts/check_orphan_skills.py` reports skills present here that
`agent-dotfiles`' roster neither rosters nor benches. It is **advisory, not
authoritative** — this repository is not where the roster lives, and it may
not be the only consumer — so it never fails CI (the `orphan-check` job runs
with `continue-on-error: true`) and its verdict is not a gate.

It degrades honestly: "the roster was not reachable" and "checked, no
orphans" are different exit codes (2 vs. 0) and different printed lines, on
purpose — reporting the former as the latter would be the same blind spot
`agent-dotfiles#145` fixed for the skill description budget, one layer over.
Run it locally with `python3 scripts/check_orphan_skills.py`; point it at a
local `agent-dotfiles` checkout with `--roster-path
/path/to/agent-dotfiles/settings/default-skills.txt` if you have one, rather
than relying on the network fetch CI uses.

## Canonical Layout

```text
plugin.json                # Agent Plugins 1.0.0 manifest (closed schema)
skills/
  <skill-name>/
    SKILL.md
    scripts/
    references/
    assets/
scripts/
  validate_repository.py   # structural + link + naming checks
  check_orphan_skills.py   # advisory: rostered/benched in agent-dotfiles?
docs/
  README.md                # taxonomy index -- read this first
  canonical/                # current, standing reference material
  historical/               # dated investigation/decision records
  research/                 # open proposals, not yet decided
tests/
  test_validate_repository.py
  test_plugin_manifest.py  # manifest fields + plugin-root path containment
  test_check_orphan_skills.py
  test_docs_lint.py         # enforces the docs/ classification below
.github/workflows/         # CI: validate + unit tests
```

`docs/` is classified into `canonical/` (actively true today), `historical/`
(dated investigation/decision records, each stating its own disposition:
landed, rejected, or still open), and `research/` (open proposals) —
[`docs/README.md`](docs/README.md) is the one-page signpost, and
`scripts/docs_lint.py` enforces the shape in CI: no unclassified file
directly under `docs/`, no generated state committed there, no duplicate
content. A document with no disposition note predates the classification
convention (2026-08-16) — treat its recommendation as unconfirmed until
checked against `gh issue view` / `gh pr list` for what actually happened,
never as settled practice on its own say-so.

## Skill Authoring

- Use `skills/<name>/SKILL.md`.
- Match the directory name and frontmatter `name`.
- Use lowercase letters, digits, and hyphens; maximum 64 characters.
- Include what the skill does and when it should trigger in `description`.
- Keep portable frontmatter to `name` and `description` by default;
  `license`, `compatibility`, `metadata`, and `allowed-tools` are also
  accepted.
- Use imperative instructions.
- Keep `SKILL.md` under 500 lines.
- Move detailed material to `references/` and link it directly from `SKILL.md`.
- Put deterministic, repeated operations in tested, executable scripts
  under `scripts/`.
- Do not add a README inside a skill directory.
- Avoid harness-specific preprocessing syntax.
- Classify each skill as *model-invoked* (a reusable discipline the agent
  should reach on its own) or *user-invoked* (a workflow reached
  deliberately). Express the classification in `description` trigger
  wording, not in frontmatter fields.
- Frontmatter fields are flat `key: value` lines — never nested mappings or
  flow collections. Write a colon in a `description` freely (e.g. "runs
  long: repetition, not duration"); the validator quotes such values before
  either parser sees them, so plain YAML's "unquoted `: ` is a mapping
  separator" rule never applies to skill descriptions
  (jonhill90/skills#142).

## Workflow

1. Orient in the repository and inspect current changes.
2. Define observable success criteria.
3. For behavioral code (scripts), use red-green-refactor.
4. Make the smallest coherent change.
5. Run repository validation and relevant script tests.
6. Review the diff for generated files, broken links, and source duplication.

## Work Tracking

GitHub Issues on this repository (`gh issue list`) is the tracking
surface for open work here. Close an issue with `Fixes #N` in the PR
body. Branch with a type prefix (`docs/`, `feat/`, `chore/`); CI gates on
`pull_request`.

## Merging PRs (jonhill90/skills#254, #256)

**`scripts/merge_pr.py --repo <owner/name> --number <N>` is the only way to
merge a PR in this repository.** Never `gh pr merge` — it does not check CI
or review state, which is exactly how skills#255 got self-merged unreviewed.
A reviewing lane records a cross-lane review as a `Verdict:`/`Review-Lane:`/
`Reviewed-SHA:` PR comment (GitHub review objects are unusable here — every
lane shares one login, so `gh pr review --approve` is refused as
self-review); `merge_pr.py` merges only when CI is green and
`scripts/pr_verdict.py` confirms an approved verdict at the current head.
Full mechanism, the incident that forced it, and why it is a script rather
than a CI job: [`docs/historical/merge-gate-required-256.md`](docs/historical/merge-gate-required-256.md).

## Required Verification

Run before considering repository changes complete:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

Run language-specific tests when changing bundled scripts.

## Spec Conformance

`scripts/validate_repository.py` and `plugin.json` are each checked against
their own external reference (`skills-ref`, `agent-plugins.org`'s schema) by
a dedicated CI job — reading the spec and comparing it to our own code is
not an independent check; those jobs are. This repository is deliberately
stricter than the reference in a few named ways (ASCII-only names,
uppercase `SKILL.md`, a few checks the spec doesn't cover at all); none of
the differences are spec violations. Full list and rationale:
[`docs/canonical/spec-conformance.md`](docs/canonical/spec-conformance.md).

## Recording Figures

A number written into this repository's docs is either **measured** — a
command was run and its output read — or **inferred** from a setting, a
prediction, or arithmetic. State which. Do not quote a count for a set
you have not enumerated.

## Distribution

- `npx skills add jonhill90/skills --list` browses the collection.
- `npx skills add jonhill90/skills --skill <name>` installs one skill
  into the current project.
- `plugin.json` declares the whole repository as an Agent Plugins 1.0.0
  plugin, so any conformant client can consume it without bespoke
  tooling (#159). **It replaces nothing today.** `npx skills` stays the
  per-skill install path and is a different granularity — one skill,
  content-hash pinned — which no whole-plugin install offers. A
  consumer's `apm.yml` pinning is that consumer's concern, not this
  repository's.
- **Claude Code does not read this manifest.** Its own manifest is
  `.claude-plugin/plugin.json`; `claude plugin validate .` on this tree
  reports "No manifest found ... Expected .claude-plugin/marketplace.json
  or .claude-plugin/plugin.json". Adding that second file is a separate
  decision, not implied by this one.
- Do not hand-maintain a growing matrix of harness-specific copies of
  this repository; harness projection is that consumer's job, not this
  repository's.
- Do not add `mcp.json`. It is optional, this repository ships no MCP
  servers, and a missing fixed component location is explicitly not an
  error for a client.

## Guardrails

Do:

- use current primary documentation for changing formats and tools;
- preserve progressive disclosure;
- document compatibility assumptions.

Do not:

- copy employer-owned or project-specific content into this repository;
- add duplicate skill identities;
- encode one harness as the portable source model;
- claim validation without running the commands above;
- publish private evaluation evidence or link to private repositories
  from this tree — plain provenance statements (what happened, when) are
  fine; clickable links to private material are not. This repository is
  public deliberately; a relative Markdown link or `https://` link into a
  private repository (the companion behavioral-evaluation repository
  mentioned in "Scope", `jonhill90/agent-evals`, or any repository named
  by convention with a `-private` suffix) is simply broken for every
  public reader. Name the private source in plain text instead — a repo
  name and issue number a reader cannot click through to is provenance,
  not a leak. `scripts/validate_repository.py`'s `validate_no_private_links`
  check (jonhill90/skills#201) enforces this in CI so the convention does
  not depend on anyone remembering it.
