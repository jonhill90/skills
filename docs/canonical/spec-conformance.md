# Where this repository's validator is stricter than the Agent Skills spec (jonhill90/skills#157, #159)

`scripts/validate_repository.py` is checked against the specification's own
reference implementation — `skills-ref` from
[agentskills/agentskills](https://github.com/agentskills/agentskills) — by
the `spec-conformance` CI job, which runs `skills-ref validate` over every
skill. Reading the spec and comparing it to our own code is not an
independent check; that job is the independent instrument.

`plugin.json` follows the same split (#159). `tests/test_plugin_manifest.py`
encodes the Agent Plugins constraints offline — required fields, the exact
`$schema` value, the `name` pattern, and the closed top-level key set — and
the `plugin-conformance` CI job validates the same file against the schema
fetched from `agent-plugins.org`. The manifest schema is closed, so one
misspelled key fails every conformant client; both instruments were
confirmed to go red on a `keywords` → `keyword` edit before this was merged.

## Where the two deliberately differ

None of these are spec violations — a skill accepted here is accepted by the
reference. This repository is simply the stricter one:

- **ASCII names only.** `NAME_RE` allows `a-z0-9-`; the reference also
  accepts Unicode letters (`café-skill` passes it, fails us). The spec's own
  wording is "lowercase alphanumeric characters (`a-z`, `0-9`)", and ASCII
  directory names travel better across filesystems and URLs.
- **`SKILL.md` must be uppercase.** The reference also accepts `skill.md`.
- **A skill must have a body.** The reference accepts frontmatter with no
  markdown after it.
- **Names are not whitespace-stripped** before the directory-match check.
- Plus checks the spec does not cover at all: the 500-line cap, resolvable
  relative links, no `README.md` inside a skill, executable bits on bundled
  scripts, collection-wide duplicate names, and the privacy denylist.
