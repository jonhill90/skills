# 0001 Documentation layout

- Status: Accepted; the `docs/eval-status.json` exception below was removed by [0002](0002-remove-eval-system.md)
- Date: 2026-09-30

## Context

`docs/` used a lifecycle taxonomy (`canonical/`, `historical/`,
`research/`). Nearly all of it recorded investigations into the behavioral
evaluation system, which is being replaced by a community-maintained one.
Six pointer files at the old top-level paths remained from an earlier move.
Long rationale sections had accumulated in `AGENTS.md` (303 lines), which
agents load on every session.

## Decision

Organize `docs/` by subject, following `skills/organize-repository`:
`reference/` for maintained explanations and `decisions/` for records like
this one. `docs/README.md` indexes both.

Removed, recoverable from git history at `ec20f6c`:

- every file under `docs/canonical/`, `docs/historical/`, and
  `docs/research/` (14 documents: eval-harness investigations, the
  loop-tick placement investigation for #160, and the open docs proposal
  for #161, which this decision answers);
- the six pointer files at old `docs/*.md` paths. Only prose cited them
  (reports in `agent-estate`, scenario notes in `agent-evals`, one
  `agent-dotfiles` triage note); no code reads them.

Kept: `docs/eval-status.json`, a symlink `agent-estate` code reads.

Moved from `AGENTS.md` into `docs/reference/`, unchanged: the merge-gate
details, spec-conformance details, and distribution notes. `AGENTS.md`
keeps a short rule for each with a link.

## Consequences

- `scripts/docs_lint.py` enforces the subject layout instead of the
  lifecycle one.
- Some eval-tooling comments and eval scenarios still name removed paths as
  provenance. They will go with the evaluation system they describe.
- A new document goes under `reference/` if it stays true and is maintained,
  or `decisions/` if it records a choice. Investigations belong in issues or
  pull requests, not in `docs/`.
