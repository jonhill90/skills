# Eval result

**Verdict: could_not_measure (n=1, re-run after skills#282)**

Re-run for `jonhill90/skills#290`: `jonhill90/skills#282` found this skill
missing from the harness's shared install path at audit time, which
invalidates any prior with/without pair regardless of what an earlier
recorded run claimed about the defect being fixed first — an uninstalled
"with" arm cannot produce a real difference. Visibility was confirmed
directly before trusting this run: `~/.claude/skills/durable-fact-before-label`
resolves as a symlink to this skill's directory, `SKILL.md` reads back
through it, and the target shares an inode with this checkout (same
mechanism `#282` used to close its own audit).

New live pair (`claude -p`, project-local skill vs. `--disable-slash-commands`),
task: write a `complete_job()` function that finishes a job by writing a
durable `status.json` record and removing a lock file. Both arms wrote the
durable record first, released the lock second, and independently added
atomic-write and directory-fsync handling with near-identical reasoning
for the ordering (a stale lock after a crash is recoverable and idempotent;
the reverse order risks silent duplicate work). No discrimination — the
skill was genuinely visible this time (unlike the prior pass this issue
re-runs), and the base model already applies this ordering by default on
a task this size and this legible. A version where the durable-record
step is less obviously "first" in the prompt's own framing has not been
tried.
