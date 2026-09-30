# 0003 Claude Code plugin

- Status: Accepted
- Date: 2026-09-30

## Context

The collection installed per skill with `npx skills` and declared an Agent
Plugins manifest (`plugin.json`), but Claude Code reads only
`.claude-plugin/`, so it could not install the collection as a plugin.
`mattpocock/skills` ships a Claude Code plugin from grouped folders
(`skills/<group>/<name>/`) and has to list every shipped skill in its
manifest. Its own decision record explains that the grouping blocks a native
Codex plugin, whose manifest accepts a single skills path.

## Decision

- Keep `skills/<name>/` flat. Skill status (default, benched) stays in
  `agent-dotfiles`' roster, not in paths, so a status change never moves a
  skill.
- Add `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: one
  marketplace, `jonhill90`, with one plugin, `jonhill90-skills`, sourced from
  the repository root. Claude Code scans `skills/` by default, so neither
  manifest lists skills.
- Leave `version` unset. Claude Code then versions the plugin by commit SHA,
  so installs follow `main` without a release process. `claude plugin
  validate` warns about the missing version; CI runs it without `--strict`.

## Verification (2026-09-30, Claude Code 2.1.285)

- `claude plugin validate .` passes with only the missing-version warning,
  and fails on a `source` containing `..`.
- In a throwaway config directory, `marketplace add` and `install` succeeded
  and `claude plugin details` listed all 42 skills, with ~5.6k tokens always
  on.

## Consequences

- Installing the plugin loads every skill. The per-skill route stays
  `npx skills add jonhill90/skills --skill <name>`.
- A native Codex plugin can point at `./skills/` directly if one is wanted,
  because nothing non-shipped lives there.
- A root `CLAUDE.md` is not loaded as plugin context; this repository's
  `CLAUDE.md` exists for working in the repository, not for plugin users.
