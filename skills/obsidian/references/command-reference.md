# Official Obsidian CLI — Command Reference

Condensed from https://obsidian.md/help/cli (app ≥1.12; core commands
verified hands-on 2026-07-12 on 1.12.7). Parameters are `key=value`;
boolean flags are bare words; `vault=<name>` goes first when targeting a
non-default vault. Many list/read commands accept
`format=json|csv|tsv|md|yaml` and `--copy`. The app must be running.

## File operations (verified: create, read, append, delete)

| Command | Syntax |
|---|---|
| create | `obsidian create name=<name> content=<text> template=<name> open overwrite newtab` |
| read | `obsidian read file=<name> path=<path>` |
| append | `obsidian append file=<name> content=<text> inline` |
| prepend | `obsidian prepend file=<name> content=<text> inline` |
| move | `obsidian move file=<name> to=<path>` |
| rename | `obsidian rename file=<name> name=<newname>` |
| delete | `obsidian delete file=<name> permanent` |
| file info | `obsidian file file=<name> path=<path>` |
| wordcount | `obsidian wordcount file=<name> words characters` |

## Listing

| Command | Syntax |
|---|---|
| files | `obsidian files folder=<path> ext=<ext> total` |
| folders | `obsidian folders folder=<path> total` |
| folder info | `obsidian folder path=<path> info=files\|folders\|size` |

## Search (verified)

| Command | Syntax |
|---|---|
| search | `obsidian search query=<text> path=<folder> limit=<n> case total format=text\|json` |
| search:context | `obsidian search:context query=<text> path=<folder> limit=<n> case` |
| search:open | `obsidian search:open query=<text>` |

## Properties / frontmatter (verified: property:read)

| Command | Syntax |
|---|---|
| property:set | `obsidian property:set name=<name> value=<value> type=text\|list\|number\|checkbox\|date\|datetime file=<name>` |
| property:read | `obsidian property:read name=<name> file=<name>` |
| property:remove | `obsidian property:remove name=<name> file=<name>` |
| properties | `obsidian properties active file=<name> counts sort=count format=yaml\|json\|tsv` |
| aliases | `obsidian aliases active file=<name> total verbose` |

## Daily notes

| Command | Syntax |
|---|---|
| daily | `obsidian daily paneType=tab\|split\|window` |
| daily:path / daily:read | `obsidian daily:path`, `obsidian daily:read` |
| daily:append / daily:prepend | `obsidian daily:append content=<text> open inline` |

## Tasks

| Command | Syntax |
|---|---|
| tasks | `obsidian tasks file=<name> path=<path> status="<char>" done todo verbose daily total format=json\|tsv\|csv` |
| task | `obsidian task ref=<path:line> file=<name> line=<n> status="<char>" toggle done todo daily` |

## Links & graph

| Command | Syntax |
|---|---|
| backlinks | `obsidian backlinks file=<name> counts total format=json\|tsv\|csv` |
| links | `obsidian links file=<name> total` |
| unresolved | `obsidian unresolved total counts verbose` |
| orphans / deadends | `obsidian orphans total`, `obsidian deadends total` |

## Tags, templates, outline

| Command | Syntax |
|---|---|
| tags | `obsidian tags file=<name> active sort=count total counts` |
| tag | `obsidian tag name=<tag> total verbose` |
| templates | `obsidian templates total` |
| template:read | `obsidian template:read name=<name> title=<title> resolve` |
| template:insert | `obsidian template:insert name=<name>` |
| outline | `obsidian outline file=<name> format=tree\|md\|json total` |

## Vaults (verified: vaults, vault info)

| Command | Syntax |
|---|---|
| vault | `obsidian vault info=name\|path\|files\|folders\|size` |
| vaults | `obsidian vaults total verbose` |

## History & Obsidian Sync

| Command | Syntax |
|---|---|
| history family | `obsidian history file=<name>`, `history:read file=<name> version=<n>`, `history:restore …` |
| diff | `obsidian diff file=<name> from=<n> to=<n> filter=local\|sync` |
| sync family | `obsidian sync:status`, `sync:history file=<name>`, `sync:deleted total`, … |

## App control & misc

| Command | Syntax |
|---|---|
| open | `obsidian open file=<name> path=<path> newtab` |
| commands / command | `obsidian commands filter=<prefix>`, `obsidian command id=<command-id>` |
| plugins family | `obsidian plugins`, `plugin:enable id=<id>`, `plugin:install id=<id> enable`, … |
| eval | `obsidian eval code=<javascript>` (advanced; runs in app context) |
| reload / restart / version | `obsidian reload`, `obsidian restart`, `obsidian version` |
| random | `obsidian random:read folder=<path>` |

Running bare `obsidian` opens the interactive TUI — avoid in scripts;
use single commands with `format=json` for automation.
