# Stale-docs truth pass, 2026-08-23

Measured, before starting: 12 of 116 tracked `.md` files had no commit
touching them in the last 14 days —

```
$ now=$(date +%s); git ls-files '*.md' | while read -r f; do
    ts=$(git log -1 --format=%ct -- "$f")
    [ $(( (now - ts) / 86400 )) -ge 14 ] && echo "$f"
  done
```

A lower proportion than `agent-dotfiles` (16/43, 37%) at the same pass,
but this repo's 116-file, 657 KB doc corpus is the largest in the
estate, so the absolute risk was worth checking rather than accepting
the lower ratio as evidence of health.

## Method

For every claim in the 12 files that asserts something about the state
of code, a tool, or a command's actual behavior: checked against the
current tree, a real command run, or an installed binary's actual
`--help` output — never against another document, since a doc citing a
doc is how an error propagates rather than gets caught. Real commands
run, not recalled: `gh --version`, `linear --help` and per-subcommand
`--help`, `tmux -V` and an isolated-server `show-options` (to separate
tmux's own factory default from this machine's `~/.tmux.conf`
override), `wc`, `ls`, and direct reads of `scripts/merge_pr.py` /
`scripts/pr_verdict.py` / `scripts/validate_repository.py` for the exit
codes and constants this repo's own `AGENTS.md` describes. The live
`$AGENT_MEMORY_VAULT` was read directly for `memory-conventions`'
claims about `index.md`'s frontmatter and size.

Not rewritten for style, structure, or completeness — a diff full of
rewording would bury a real correction if one existed. None of the 12
needed one.

## Eval-record claims, checked specifically per this pass's brief

None of the 12 stale files assert anything about eval verdicts, the
`could_not_measure` count, the capability-vs-habit taxonomy, or specific
skill counts — grepped all 12 for `eval`, `could_not_measure`,
`taxonomy`, `capability.*habit`, a skill-count pattern, and both recent
issue numbers (`#275`, `#276`); zero hits. The eval record moved a lot
today (`could_not_measure` now 29/41, 0 unevaluated; the taxonomy
hypothesis filed and refuted same-day in `#276`; `#275`'s vally spike
landed with the scoring rule ported) but none of that content lives in
any of the 12 files this pass covers — nothing here needed correcting
for it.

## Result: 12 checked, 0 corrected, 0 could-not-measure, 12 entirely accurate

Every specific, checkable claim in all 12 files held against the
current tree or a real command run:

| File | Disposition |
|---|---|
| `CLAUDE.md` (+ `.github/copilot-instructions.md`, its committed symlink twin — one file, one check) | accurate — merge-gate exit codes (0/1/2/3) match `scripts/merge_pr.py`'s `_EXIT_FOR_DECISION`/`scripts/pr_verdict.py`'s `EXIT_*` constants exactly; every referenced script, test file, and workflow job name exists; `NAME_RE`/`SKILL_LINE_CAP` match `validate_repository.py`; symlink structure confirmed on disk |
| `skills/primer/SKILL.md` | accurate — procedural only, no external-state claims to falsify |
| `skills/linear/references/teams-projects.md` | accurate — every subcommand, flag, and the `LINEAR_ISSUE_SORT` env var confirmed against the real installed `linear` CLI (v1.9.1) |
| `skills/memory-conventions/SKILL.md` | accurate — `okf_version: "0.1"`, the 200-line/25KB cap (live: 82 lines / 12,670 B), and the `type: user\|feedback\|project\|reference` set confirmed directly against the live vault |
| `skills/failing-test-first/SKILL.md` | accurate — procedural only |
| `skills/linear/SKILL.md` | accurate — CLI structure, `--sort` required-with-error confirmed live, `--from-ref`/`--branch`/`--base`/`--draft`/`--title` all confirmed against the real CLI; both referenced `references/` files exist |
| `skills/tmux/references/fundamentals.md` | accurate — "Validated against tmux 3.5" matches the installed binary exactly; `history-limit` default checked against a truly isolated server (`-f /dev/null`), not this machine's overridden `~/.tmux.conf` (50000) — factory default is 2000, matching the doc |
| `skills/close-the-loop/SKILL.md` | accurate — internally consistent (9 sections stated, 9 listed, 9 in the checklist), no external-state claims |
| `skills/github-cli/SKILL.md` | accurate — version floor (2.65.0+) satisfied by the installed 2.85.0; every spot-checked flag (`--reason`, `--failed`, `--clone`, `--add-assignee`/`--remove-assignee`, `--auto`) confirmed live; all 4 referenced files exist |
| `skills/github-cli/references/issues-labels.md` | accurate — lock reasons, `--checkout`, `--force` on both `label create` and `label clone` confirmed live |
| `skills/github-cli/references/actions.md` | accurate — cache `--sort`/`--order`/`--all`, secret `--visibility`, rerun `--debug` all confirmed live |

No file was rewritten, deleted, or marked historical — nothing here was
found obsolete. This record exists so the next stale-docs pass does not
re-measure the same 12 files from zero.
