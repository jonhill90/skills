# Merging pull requests (jonhill90/skills#254, #256)

Moved from `AGENTS.md` on 2026-09-30 so the agent instructions stay short; content unchanged.

When more than one agent lane works this repository at once, every lane
pushes through the same shared GitHub login — `gh pr review --approve`
is refused as self-review regardless of who is actually asking, so a
real cross-lane review has to be recorded another way: a reviewing lane
posts a plain PR comment, not a GitHub review object, carrying

```
Verdict: APPROVE            (or REQUEST CHANGES, with specifics)
Review-Lane: <reviewing lane's own name>
Reviewed-SHA: <the exact head commit SHA reviewed>
```

and the PR's own body states which lane opened it:

```
Author-Lane: <authoring lane's own name>
```

**`scripts/merge_pr.py` is the only way to merge a PR in this repository
(jonhill90/skills#256).** Do not run `gh pr merge` directly — not by
hand, not from a lane. `gh pr merge` is a bare, unchecked command; it
does not know CI is red, and it does not know whether a `Verdict:`
comment exists, let alone whether it is a genuine cross-lane one at the
current head. That gap is exactly how `jonhill90/skills#255` (this
gate's own PR) got self-merged unreviewed 2m22s after opening — nothing
stopped it, because `gh pr merge` never checked. `scripts/merge_pr.py`
is the wrapper that cannot skip the gate:

```bash
python3 scripts/merge_pr.py --repo <owner/name> --number <N>
```

It checks, in order, and merges only if BOTH pass:

1. CI is green (`gh pr checks`) — any failing or still-pending check,
   or no checks at all, refuses.
2. `scripts/pr_verdict.py --repo <owner/name> --number <N>` exits `0`
   (`approved`) at the PR's CURRENT head — every other exit code (`1`
   rejected, `2` no verdict on record, `3` unknown/unresolved: same
   lane, stale SHA, a missing trailer) refuses, same as CI being red.

Exit code `0` means it merged; `1`/`2`/`3` each name a specific refusal
reason in the printed JSON — see `scripts/merge_pr.py`'s own doc comment
for the full exit-code table. `scripts/pr_verdict.py` on its own is
still the thing to run when you want the verdict WITHOUT merging (a
dry-run read, or building another caller on top); `scripts/pr_verdict.py`'s
own doc comment covers exactly what that check does and why — it is a
port of `jonhill90/agent-supervisor`'s `verdict.py`/`verdict-independence.sh`,
adapted because this repository has no lane ledger to resolve
authorship from independently — `Author-Lane:`/`Review-Lane:` are both
self-declared, the same trust model either side already has.

**Not wired into CI, deliberately.** This repository's own CI
(`.github/workflows/validate.yml`) never merges a PR — every job here
validates content and exits; merging is always a separate
`scripts/merge_pr.py` invocation an operator or an agent lane runs
directly, outside any workflow. There is no merge-time CI job to attach
this gate to without inventing one that does not otherwise exist;
`scripts/merge_pr.py` is the script that invocation must run instead of
`gh pr merge`, by convention stated here, the same way
`scripts/check_skill_install.py` is wired into `eval_status.py --record`
as a Python import rather than a workflow step because ITS caller is
also not a CI job.
