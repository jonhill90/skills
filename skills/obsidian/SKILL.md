---
name: obsidian
description: Read, write, search, and manage notes in Obsidian vaults using the official Obsidian CLI. Use when working with Obsidian notes, vaults, knowledge bases, daily notes, tasks, or personal wikis.
---

# Obsidian Vault Operations

Interact with Obsidian vaults using the official Obsidian CLI (`obsidian`),
bundled with the desktop app since v1.12.

**Architecture note (verified 2026-07-12):** the CLI remote-controls the
Obsidian app and **requires it to be already running** — with the app
closed, commands fail fast with "The CLI is unable to find Obsidian"
(it does not auto-launch, despite what some docs imply; `open -a
Obsidian` first if needed). For plain file reads/writes where the app is
unavailable (headless machines, CI), fall back to direct file operations
on the vault directory — notes are plain Markdown.

## Prerequisites

```bash
# Verify the CLI responds (also confirms the app is reachable)
obsidian version
```

Requirements: Obsidian desktop **installer** ≥1.12 and CLI enabled in
**Settings → General → Command line interface**.

**Installer-vs-core gotcha (verified):** Obsidian's in-app updater
updates only the core (Settings → About "Current version"); the CLI
binary ships in the .app bundle, so an old installer has no CLI even
when the app displays 1.12+. Fix: download a fresh installer from
obsidian.md and replace the app.

The binary lives at
`/Applications/Obsidian.app/Contents/MacOS/obsidian-cli`. Register it on
PATH either via the app's own registration
(`/usr/local/bin/obsidian`, needs admin) or without sudo:

```bash
ln -sf /Applications/Obsidian.app/Contents/MacOS/obsidian-cli ~/bin/obsidian
```

## Syntax Conventions

- Parameters are `key=value`; quote values with spaces: `name="My Note"`.
- Boolean flags are bare words: `overwrite`, `open`, `total`.
- `\n` for newlines in content values.
- Target a specific vault with `vault=<name>` as the **first** parameter;
  otherwise the CLI uses the vault of the current working directory or the
  active vault.
- Many read commands accept `format=json|csv|tsv|md|yaml` — prefer `json`
  when parsing output.

```bash
obsidian vault="Second Brain" search query="meeting notes" format=json
```

## Vault Setup

```bash
# List known vaults; confirm the target
obsidian vaults verbose

# Vault info (name, path, size, counts)
obsidian vault info=path
```

Check this harness's local, project-scoped configuration for vault
settings — its file name and format vary by harness (a local instructions
override, a local settings file, an environment variable) — for a block
like:

```markdown
## Obsidian
- Vault: {vault-name}
- Rules: {path to vault rules note}
```

If none exists, ask the user which vault to use and whether a rules/guide
note exists, then have them record it in whatever local configuration
this harness reads automatically. **On first use per session**, if a
rules path is configured, read it and follow its folder, template, naming,
and tagging rules exactly:

```bash
obsidian read path="{rules-note-path}"
```

If no rules file exists, use the generic practices in the
[Note Creation Guide](references/templates.md).

## Read a Note

```bash
obsidian read file="{note-name}"
obsidian read path="{path/from/vault/root.md}"
```

## Create a Note

**NEVER create a note without frontmatter.**

1. Determine intent (what type of note?)
2. Read vault rules for the correct template, folder, and naming convention
3. Search first — check whether a similar note exists
4. List the target folder — verify you're writing to the right place
5. Create the note with proper frontmatter and body structure

```bash
# Create (fails into a duplicate-safe state; see gotchas)
obsidian create name="{path/or/name}" content="$(cat <<'EOF'
---
type: ...
tags: []
created: ...
updated: ...
---
# Title
EOF
)"

# Create from a vault template
obsidian create name="{name}" template="{template-name}"

# Replace an existing note (read-modify-write)
obsidian create name="{path}" content="..." overwrite
```

## Append / Prepend

```bash
obsidian append file="{note}" content="- new line"
obsidian prepend file="{note}" content="…"
# `inline` joins without a new line
```

## Search

```bash
# Machine-readable results
obsidian search query="term" format=json limit=20

# With surrounding context lines
obsidian search:context query="term" path="{folder}" limit=10
```

Uses Obsidian's own search index — respects the vault's ignore settings
and returns ranked results, unlike a plain grep.

## List Files and Folders

```bash
obsidian files folder="{path}" ext=md
obsidian folders folder="{path}"
obsidian folder path="{path}" info=files
```

## Properties (Frontmatter)

```bash
obsidian property:read name="{key}" file="{note}"
obsidian property:set name="{key}" value="{value}" type=text file="{note}"
obsidian property:remove name="{key}" file="{note}"

# All properties of a note
obsidian properties file="{note}" format=yaml
```

## Daily Notes & Tasks

```bash
obsidian daily:read
obsidian daily:append content="- [ ] follow up"
obsidian tasks file="{note}" todo format=json
obsidian task ref="{note.md}:{line}" done
```

## Move, Rename, Delete

```bash
obsidian move file="{note}" to="{new/folder/path}"
obsidian rename file="{note}" name="{new-name}"
obsidian delete file="{note}"            # to trash
obsidian delete file="{note}" permanent  # careful
```

## Links & Graph Queries

```bash
obsidian backlinks file="{note}" format=json
obsidian links file="{note}"
obsidian orphans total
```

## Common Workflows

### Read-Modify-Write

```bash
obsidian read path="{note}"
# … edit content in memory …
obsidian create name="{note}" content="…full replacement…" overwrite
```

### Find and Read Related Notes

```bash
obsidian search query="topic" format=json limit=10
obsidian read path="{result-path}"
```

## Gotchas

1. **The app must already be running** — commands fail with "unable to
   find Obsidian" otherwise; `open -a Obsidian` first, or use direct
   file operations on headless machines.
2. **`create` without `overwrite`** on an existing note does not replace
   it — always pass `overwrite` (full replacement) or use `append`.
3. **No surgical edits** — read, modify in memory, write back with
   `overwrite`; preserve frontmatter and bump `updated`.
4. **Paths are vault-relative**, not relative to the terminal cwd.
5. **`vault=` must be the first parameter** when targeting a non-default
   vault.
6. Prefer `format=json` on list/search commands when the output feeds
   further steps.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `obsidian: command not found` | Recreate the symlink (see Prerequisites) or enable the CLI in app settings |
| CLI hangs / no response | Check the app launched and finished indexing; retry |
| `Command "read" not found` on `vault=` target | The target vault hasn't finished loading in the app — retry after a few seconds |
| Wrong vault targeted | Pass `vault="{name}"` first; verify with `obsidian vault info=name` |
| Note not found | `obsidian files folder="{folder}"` to check the real path |
| Duplicate content after update | You appended instead of `overwrite` (or vice versa) |

## References

- [Note Creation Guide](references/templates.md) — intent determination and generic best practices
- [Command Reference](references/command-reference.md) — full official-CLI command tables
- Official docs: https://obsidian.md/help/cli
