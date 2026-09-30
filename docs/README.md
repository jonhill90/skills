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
- [0002 Remove the eval system and `state/`](decisions/0002-remove-eval-system.md):
  what went, what stayed, and the replacement plan (#309).
