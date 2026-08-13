# Merge safety: closing keywords and revert claims

Two git/GitHub mechanics worth knowing exactly, because both fail silently —
the wrong answer looks identical to the right one until something is
already merged.

## What a merge will actually close

GitHub (and platforms with the same convention) auto-closes an issue when a
PR body or its commit messages contain a closing keyword
(`close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved`) directly
followed by `#<number>`. The parser matches that pattern wherever it
appears — inside a quote, inside a sentence explaining that the PR does
*not* close the issue, inside an example. It is not negation-aware:

> It does not explain or close #42

still links and closes #42, because "close #42" appears in the text
regardless of what comes before it.

Check the platform's own rendered "closing references" view (e.g. `gh pr
view <n> --json closingIssuesReferences`) before merging, not the prose. If
the list does not match intent, fix it before merging — this is the only
reliable way to see the linkage; it is invisible reading the body as
prose.

Two failure directions, not one:

- A keyword that should not be there closes an issue nothing has solved.
- A missing keyword hides live work — some duplicate-work tooling greps PR
  bodies for exactly this pattern to find in-flight work, so a PR that
  genuinely resolves an issue should carry the keyword, and stripping it on
  reflex breaks that signal for anyone else checking for it.

If a PR should close nothing, every keyword-then-number occurrence has to be
broken, including inside an explanation of the trap itself — describing the
pattern tends to reproduce it. And the **commit message** counts too, not
just the PR body: a squash merge folds commit messages into the merge
commit, so a keyword left in the last commit still fires even after the PR
body is clean.

## "Would this revert something" — two-dot vs. three-dot

`git diff main..branch` (two-dot) compares the two tips directly. Every
commit `main` has that the branch does not appears as a **deletion**,
because the branch's tree simply doesn't contain it — a property of
comparing tips, not a prediction about what merging does. Applied naively,
this reports a warning against *every* branch that is behind `main`, whether
or not merging removes anything.

A merge — including a squash merge — applies the **three-dot** diff instead:
the branch's own changes since its merge base. Everything else on `main` is
left untouched.

```
$ git diff --stat main..feature     # two-dot: looks like a revert
  feature.txt  | 1 +
  mainfile.txt | 1 -

$ git diff --stat main...feature    # three-dot: what a merge actually applies
  feature.txt | 1 +

$ git merge feature       -> mainfile.txt PRESENT (not reverted)
$ git merge --squash ...  -> mainfile.txt PRESENT
```

A squash merge does not move the branch's own merge base either — it writes
one new commit on `main` whose parent is `main`'s previous tip, so a later
branch forked before that squash still merges cleanly on top of it.

Being behind `main` is not sufficient to revert anything on its own. It
takes a genuine content conflict: the branch editing lines a newer commit on
`main` also changed, a rebase onto a stale base, or a delete-versus-modify.
Those show up in a three-dot diff or as a real merge conflict.

**When it matters, do the decisive thing instead of reading a diff: merge
into a scratch worktree and look.** A diff reading can miss a semantic
conflict that git itself reports as a clean merge; attempting the merge is
the only check that answers the actual question.

### A related but different question: does `main` already contain this branch's work?

Neither plain form answers this one correctly:

- Three-dot, after a squash merge, still lists the branch's content as
  outstanding — `main` holds it under a different commit now, so the diff
  against the merge base still shows it as new.
- Two-dot, once `main` has drifted, lists `main`'s own newer files as if
  they were the branch's deletions.

What works is a two-dot diff scoped to only the paths the branch touched,
with the pathspec passed through `xargs -0` so a filename cannot word-split:

```bash
mb=$(git merge-base main "$branch")
git diff --name-only -z "$mb" "$branch" | xargs -0 git diff --stat main.."$branch" --
# empty output => the branch's work is already on main
```

Do not write the pathspec as a bare `-- $paths` variable expansion — in a
shell that word-splits, a path containing a space breaks into two pathspecs
that match nothing, and in a shell that does not word-split, a multi-file
branch collapses into one newline-joined pathspec that also matches
nothing. Both failures report the same wrong answer: "already merged," the
direction that gets unmerged work silently discarded downstream.
