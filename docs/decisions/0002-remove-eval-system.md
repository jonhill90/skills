# 0002 Remove the eval system and `state/`

- Status: Accepted
- Date: 2026-09-30

## Context

The home-grown behavioral eval system recorded a verdict for each skill,
but most were `could_not_measure` or `no_effect_observed`. Its bookkeeping
lived inside `skills/<name>/references/`, so it shipped with every installed
skill, and it kept generated records in `state/`. The plan is to adopt a
community-maintained system instead of maintaining this one.

## Decision

Remove the eval system now and track its replacement in
[#309](https://github.com/jonhill90/skills/issues/309), which lists what to
vet candidates against.

Removed (recoverable from git at `394f002`):

- `skills/*/references/eval-result.md` (41) and `eval-blocked.md` (3);
- `state/` entirely: eval logs, `eval-status.json`, and the installed-skills
  snapshot and manifest the README table generator used;
- `docs/eval-status.json`;
- `scripts/eval_status.py`, `eval_tally.py`, `check_skill_install.py`,
  `skill_read_confirmed.py`, their tests, and `.gitattributes` (only used for
  the eval logs);
- the eval-verdict check in `scripts/validate_repository.py`.

Kept:

- the `eval-case.md` walkthroughs that `mechanize` and `mine-transcripts`
  link from their `SKILL.md`; they are skill content, not bookkeeping;
- the check that bans links to private repositories.

`scripts/reconcile_skills.py` became `scripts/skills_table.py`: it
generates the README skills table from `skills/` alone, with the static
upload audit, and writes nothing else.

## Consequences

- `jonhill90/agent-estate`'s TUI reads `docs/eval-status.json`. It degrades
  to showing every skill as unevaluated when the file is missing; repoint or
  remove that view when #309 lands.
- The README no longer reports which skills are installed on one machine;
  that was personal state in a public repository.
- New skills need no eval bookkeeping until #309 chooses a system, and that
  system must keep its fixtures and results outside `skills/<name>/`.
