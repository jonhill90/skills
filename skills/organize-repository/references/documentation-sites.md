# Documentation sites

Read this when a repository adds, replaces, or removes a rendered docs site.

## The rule

Maintainer docs (architecture, decisions, runbooks, development) stay where
they are. The site is one root with the renderer's native layout inside
it. Changing the renderer means replacing that root, not moving the rest.

## Placing the site root

| Arrangement | Use when | Watch for |
|---|---|---|
| `docs/site/` beside the maintainer docs | Default. Keeps audiences visibly separate and works with any renderer that accepts a configured root | One extra level for published pages |
| The renderer owns `docs/`, with maintainer docs inside it | The repository already does this, or the tool has no configurable root | Maintainer files are published unless excluded; see Mintlify below |
| `services/docs/` or `apps/docs/` | The site is a buildable application in a workspace | Treat it as a service with its own manifest |
| The repository root | Documentation-only repository | Code-profile rules do not apply |

Never move maintainer docs into a new subdirectory (`docs/engineering/`,
`docs/maintainer/`) to make room for a site. That forces a migration on
every repository that adds a site later.

## Mintlify

- `docs.json` sits at the documentation root, which may be a subdirectory
  in a monorepo.
- Every `.md` and `.mdx` file under the root is published. A page missing
  from `docs.json` navigation is still reachable by URL (verified with
  `mint dev`, 2026-09-29). Hidden pages are for unlisted public pages, not
  for private material.
- `.mintignore` (gitignore syntax, at the docs root) removes files
  entirely. `README.md`, `LICENSE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
  dot-directories, and `node_modules` are ignored by default.
- When Mintlify shares a directory with maintainer docs, use an allowlist
  so new internal files are private by default:

  ```gitignore
  /*
  !/docs.json
  !/index.mdx
  !/guides/
  ```

  A denylist (`decisions/`) leaks every internal file added later.
- Moving a page changes its URL. Add a redirect in `docs.json` and update
  navigation in the same change.

`scripts/check_layout.py` reports Mintlify pages that are published but not
in navigation.

## Any other renderer

Before placing files, record in `docs/README.md` or `AGENTS.md`:

1. the tool and version, and its configuration file;
2. the source root, and which files it publishes;
3. how navigation is defined;
4. generated output location, and whether it is committed;
5. the build or preview command.

Keep the tool's reserved names (for example Antora's `antora.yml`,
`modules/`, `ROOT`). Do not create a framework-neutral copy of the docs to
satisfy a shared tree.
