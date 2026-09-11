# Merging is gated on CI-green plus a genuine cross-lane verdict (jonhill90/skills#255, #256)

**Status:** decided and enforced in CI-adjacent tooling. `scripts/merge_pr.py`
is the only sanctioned way to merge a PR in this repository.

## What departs from the norm, and why

Every agent lane working this repository pushes through the same shared
GitHub login, so `gh pr review --approve` is refused as self-review
regardless of who is actually asking — this repository has no way to record
a real cross-lane review as a native GitHub review object. That gap is why
`jonhill90/skills#255` (this gate's own PR) got self-merged, unreviewed,
2 minutes 22 seconds after opening: `gh pr merge` is a bare, unchecked
command. It does not know CI is red, and it does not know whether a
`Verdict:` comment exists, let alone whether it is a genuine cross-lane one
at the current head. Nothing stopped it, because nothing checked.

## The mechanism

A reviewing lane records a cross-lane review as a plain PR comment instead
of a GitHub review object:

```
Verdict: APPROVE            (or REQUEST CHANGES, with specifics)
Review-Lane: <reviewing lane's own name>
Reviewed-SHA: <the exact head commit SHA reviewed>
```

and the PR's own body states which lane opened it:

```
Author-Lane: <authoring lane's own name>
```

`scripts/merge_pr.py --repo <owner/name> --number <N>` is the wrapper that
cannot skip the gate. It checks, in order, and merges only if both pass:

1. CI is green (`gh pr checks`) — any failing or still-pending check, or no
   checks at all, refuses.
2. `scripts/pr_verdict.py --repo <owner/name> --number <N>` exits `0`
   (`approved`) **at the PR's current head** — exit `1` (rejected), `2` (no
   verdict on record), or `3` (unknown/unresolved: same lane, stale SHA, a
   missing trailer) each refuse, the same as CI being red.

Exit code `0` means it merged; `1`/`2`/`3` each name a specific refusal
reason in the printed JSON — see `scripts/merge_pr.py`'s own doc comment for
the full exit-code table. `scripts/pr_verdict.py` on its own is the thing to
run for the verdict without merging (a dry-run read, or a caller building on
top of it); it is a port of `jonhill90/agent-supervisor`'s
`verdict.py`/`verdict-independence.sh`, adapted because this repository has
no lane ledger to resolve authorship from independently —
`Author-Lane:`/`Review-Lane:` are both self-declared, the same trust model
either side already has.

## Not wired into CI, deliberately

This repository's own CI (`.github/workflows/validate.yml`) never merges a
PR — every job here validates content and exits; merging is always a
separate `scripts/merge_pr.py` invocation an operator or an agent lane runs
directly, outside any workflow. There is no merge-time CI job to attach this
gate to without inventing one that does not otherwise exist; `scripts/merge_pr.py`
is the script that invocation must run instead of `gh pr merge`, by
convention stated here — the same way `scripts/check_skill_install.py` is
wired into `eval_status.py --record` as a Python import rather than a
workflow step, because its caller is also not a CI job.

## References

- jonhill90/skills#255 — the incident: this gate's own PR, self-merged
  unreviewed 2m22s after opening
- jonhill90/skills#256 — the decision and its implementation
- `scripts/merge_pr.py`, `scripts/pr_verdict.py` — the enforcing code
