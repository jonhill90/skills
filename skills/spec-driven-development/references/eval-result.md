# Eval result

**Verdict: could_not_measure (n=1, re-run after skills#282)**

Re-run for `jonhill90/skills#290`: `jonhill90/skills#282` found this skill
missing from the harness's shared install path at audit time. The prior
recorded run here claimed the same defect was "caught and fixed before
the recorded run," but that claim predates `#282`'s own audit finding the
skill uninstalled again — an uninstalled "with" arm cannot produce a real
difference regardless of what an earlier note says was fixed. Visibility
was confirmed directly before trusting this run:
`~/.claude/skills/spec-driven-development` resolves as a symlink to this
skill's directory and `SKILL.md` reads back through it.

New live pair (`claude -p`, project-local skill vs.
`--disable-slash-commands`), task: plan (no code yet) how to add password
validation to a signup form. Both arms independently produced a
falsifiable acceptance criterion before any implementation, both named a
mutation check (remove the guard, confirm the test goes red) unprompted,
both insisted on running the check against the real form and pasting
actual output rather than describing a pass. No discrimination — the
skill was genuinely visible this time, and the base model already
front-loads a falsifiable criterion and a mutation check on a
well-specified scoping task of this size, before this skill's own
prompting.
