# docs/

Maintained documentation for this repository, organized by subject. Start
with the root [`AGENTS.md`](../AGENTS.md) for the rules; come here for the
detail behind them. The skill inventory is the generated table in the root
`README.md`; do not add another one here (#303).

## Reference

- [Distribution](reference/distribution.md): what merging a skill does and
  does not do, the plugin manifest, and the orphan-skill check.
- [Merge gate](reference/merge-gate.md): the cross-lane verdict comment and
  `scripts/merge_pr.py`.
- [Validation](reference/validation.md): spec conformance, and where this
  repository is deliberately stricter than the reference validator.

## Decisions

- [0001 Documentation layout](decisions/0001-documentation-layout.md): why
  `docs/` is organized by subject, and what was removed.

## Not documentation

`eval-status.json` is a symlink to the generated `state/eval-status.json`.
It stays because `jonhill90/agent-estate`'s TUI hardcodes this path as a Go
constant. Remove it when that constant changes.
