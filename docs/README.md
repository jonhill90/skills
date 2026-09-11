# docs/ — taxonomy index

Not a skill inventory (`SKILLS-INDEX.md` was deleted for exactly that
anti-pattern, #303 — never resurrected under any name, here or elsewhere).
This is a one-page signpost for the classified documentation tree
itself, enforced by `scripts/docs_lint.py`:

- **`canonical/`** — current, standing reference material. Actively
  true today, not a record of a past event.
- **`historical/`** — dated investigation/decision records. Correctly
  kept, not archived by accident; each states its own disposition.
- **`research/`** — open proposals, not yet decided one way or the
  other.

## Canonical

- [eval-cost-axis-principle](canonical/eval-cost-axis-principle.md)
- [spec-conformance](canonical/spec-conformance.md)

## Historical

- [audit-install-parity-270](historical/audit-install-parity-270.md)
- [could-not-measure-vocabulary-296](historical/could-not-measure-vocabulary-296.md)
- [eval-arm-wiring-retrofit-gap-287](historical/eval-arm-wiring-retrofit-gap-287.md)
- [eval-ask-a-council-266](historical/eval-ask-a-council-266.md)
- [eval-cost-delta-recount](historical/eval-cost-delta-recount.md)
- [eval-harness-adopt-or-build](historical/eval-harness-adopt-or-build.md)
- [eval-harness-findings](historical/eval-harness-findings.md)
- [eval-instrument-diagnosis-2026-08-23](historical/eval-instrument-diagnosis-2026-08-23.md)
- [eval-pass15-remaining-four](historical/eval-pass15-remaining-four.md)
- [loop-tick-placement-160](historical/loop-tick-placement-160.md)
- [merge-gate-required-256](historical/merge-gate-required-256.md)
- [stale-truth-pass-2026-08-23](historical/stale-truth-pass-2026-08-23.md)

## Research

- [eval-longitudinal-design](research/eval-longitudinal-design.md)
- [skills-docs-proposal-161](research/skills-docs-proposal-161.md)

Each list above is exhaustive as of this file's own last edit; `docs_lint.py`
enforces the classification, not this list's completeness — recount with
`ls docs/canonical docs/historical docs/research` before trusting it after
a later change adds or moves a file.

State (generated JSON/JSONL) lives under `state/` at the repo root, not
here — documentation and data are different trees. `docs/eval-status.json`
is the one exception you'll see in a directory listing: a symlink, not a
file, kept so `jonhill90/agent-estate`'s TUI (which hardcodes that exact
relative path as a Go constant) keeps resolving without this repo
hand-editing a sibling repo's source. The real, generated file lives at
`state/eval-status.json`.
