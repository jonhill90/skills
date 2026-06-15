# Migration Source Audit

This audit records how overlapping personal skills were selected during the
`vibes` to `skills` refactor. Hill90 was refreshed from `origin/main` before the
comparison; its latest commit was `169dd57` on 2026-04-26.

Gentiva was used only to identify patterns and gaps. No Gentiva content was
migrated.

| Skill | Selected basis | Migration decision |
|---|---|---|
| `closing-the-loop` | Hill90 latest | Preserve the nine-section plan contract and strong workaround disposition; remove Hill90 CI paths |
| `using-tmux` | Hill90 latest, including 2026-03-16 enhancements | Preserve pane safety, send verification, recovery, self-test, watcher, and recurring supervision; generalize lane names and paths |
| `primer` | Hill90 workflow plus portable rewrite | Preserve phased orientation and report structure without Claude preprocessing |
| `context7` | Hill90 unified identity plus prior cross-platform scripts | Keep one skill identity, include Bash/Python/PowerShell fallbacks, and use portable environment discovery |
| `create-skill` | Portable rewrite informed by current Agent Skills guidance | Prefer open format and deterministic validation over the older Claude-specific version |
| `validate-skill` | Portable rewrite | Replace the prompt-only validator with `scripts/validate_repository.py` |
| `linear` | Existing personal version | Exclude Hill90 team, project, and status policy |
| `lint-agents` | Existing behavior with canonical paths | Point at root `agents/`; require explicit approval for fixes |
| `obsidian` | Existing personal version | Content matches Hill90; remove Claude-only frontmatter |
| `youtube-transcript` | Existing personal version | Content matches Hill90; update canonical paths and remove Claude-only frontmatter |
| `gh-cli` | Identical across personal and Hill90 copies | Move unchanged |
| `ms-learn` | Identical across personal and Hill90 copies | Move unchanged |

The initially migrated `dispatching-parallel-agents`,
`test-driven-development`, and `using-git-worktrees` skills were removed after
confirming that Superpowers already owns and distributes skills with those
identities. Personal forks would create duplicate triggers and ongoing drift.

Future promotions from project repositories should update this table or a
successor provenance manifest rather than relying on memory or file copying.
