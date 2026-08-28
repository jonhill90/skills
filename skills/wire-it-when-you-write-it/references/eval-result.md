# Eval result

**Verdict: improve (n=1 — rerun before trusting further)**

Re-run for `jonhill90/skills#290`: `jonhill90/skills#282` found this
skill missing from the harness's shared install path at audit time. The
prior recorded run here claimed an install-path defect "invalidated a
first attempt and was fixed before the recorded run," but that claim
predates `#282`'s own audit finding the skill uninstalled again — an
uninstalled "with" arm cannot produce a real difference regardless of
what an earlier note says was fixed. Visibility was confirmed directly
before trusting this run: `~/.claude/skills/wire-it-when-you-write-it`
resolves as a symlink to this skill's directory and `SKILL.md` reads back
through it.

New live pair (`claude -p`, project-local skill vs.
`--disable-slash-commands`), task: wire an existing, unused
`normalize_email()` helper into a `create_user()` call site. Both arms
wired the call correctly and verified the normalized output by running
it. **They diverged on this skill's own second half — "add the check
that fails when a caller disappears."** The WITH arm wrote a persistent
test file asserting the normalized output, then ran an explicit
mutation check (removed the call, confirmed the test failed; restored
it, confirmed it passed) before reporting done. The WITHOUT arm verified
with an ad-hoc one-off run only, explicitly named the absence of a test
file, and offered to add one only if asked, rather than doing it
unprompted. This is the first discriminating result recorded for this
skill (prior trials were all invalidated by the install-path defect) —
weak by construction at n=1, but a real, skill-attributable difference
in the mechanism this skill exists to enforce, not a wash. Re-run before
trusting further, per this collection's own convention for a first
positive single-trial result.
