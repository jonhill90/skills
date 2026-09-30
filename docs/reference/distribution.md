# Distribution and what "shipped" means

Moved from `AGENTS.md` on 2026-09-30 so the agent instructions stay short; content unchanged.

Merging a skill here does not install it anywhere. This repository has no
install gate of its own — a merged, CI-green skill is published and
installable (`npx skills add`, or as an Agent Plugin), and that is the whole
of what this repository controls.

Whether a harness loads it automatically is a **separate, later decision**
made in a different repository: Jon's `agent-dotfiles`
(`settings/default-skills.txt`) rosters the subset it installs by default
for his own harnesses, per its own evidence bar (SPEC §10.1 rule 5) — a new
skill does not earn a roster slot by arriving here. `default-skills.txt`
also carries a `[benched]` section recording, per skill, that withholding it
was a deliberate decision rather than an oversight.

Concretely, for a skill authored here: merged and un-rostered is the normal
resting state for a brand-new skill, not a bug — but merged, un-rostered,
and **un-benched** is exactly the failure jonhill90/skills#162 measured
(eleven skills, 2026-08-11, installed on no harness, with no record either
repository could point to). `scripts/check_orphan_skills.py` (see "Orphan
skill check" below) is this repository's own advisory view into that
question; it cannot roster or bench anything itself.

## Orphan skill check

`scripts/check_orphan_skills.py` reports skills present here that
`agent-dotfiles`' roster neither rosters nor benches. It is **advisory, not
authoritative** — this repository is not where the roster lives, and it may
not be the only consumer — so it never fails CI (the `orphan-check` job runs
with `continue-on-error: true`) and its verdict is not a gate.

It degrades honestly: "the roster was not reachable" and "checked, no
orphans" are different exit codes (2 vs. 0) and different printed lines, on
purpose — reporting the former as the latter would be the same blind spot
`agent-dotfiles#145` fixed for the skill description budget, one layer over.
Run it locally with `python3 scripts/check_orphan_skills.py`; point it at a
local `agent-dotfiles` checkout with `--roster-path
/path/to/agent-dotfiles/settings/default-skills.txt` if you have one, rather
than relying on the network fetch CI uses.

## Distribution

- `npx skills add jonhill90/skills --list` browses the collection.
- `npx skills add jonhill90/skills --skill <name>` installs one skill
  into the current project.
- `plugin.json` declares the whole repository as an Agent Plugins 1.0.0
  plugin, so any conformant client can consume it without bespoke
  tooling (#159). **It replaces nothing today.** `npx skills` stays the
  per-skill install path and is a different granularity — one skill,
  content-hash pinned — which no whole-plugin install offers. A
  consumer's `apm.yml` pinning is that consumer's concern, not this
  repository's.
- **Claude Code reads its own manifests, not this one.** Since
  [decision 0003](../decisions/0003-claude-code-plugin.md),
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` make the
  repository a one-plugin Claude Code marketplace. Both plugin manifests use
  the name `jonhill90-skills`; `tests/test_plugin_manifest.py` keeps them in
  step, and the `claude-plugin-conformance` CI job runs
  `claude plugin validate .`.
- Do not hand-maintain a growing matrix of harness-specific copies of
  this repository; harness projection is that consumer's job, not this
  repository's.
- Do not add `mcp.json`. It is optional, this repository ships no MCP
  servers, and a missing fixed component location is explicitly not an
  error for a client.
