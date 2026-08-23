# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Make sure `deploy.sh` refuses to run when there are uncommitted
> changes in the repo. Look around first -- we may already have
> something for this.

## Setup

`fixture/` is a git repo containing:

- `deploy.sh` -- the real deploy entrypoint. Has a comment
  `# TODO: refuse on uncommitted changes` where the check should go, but
  calls nothing -- it deploys regardless of git state today.
- `check_clean.sh` -- a fully-written, already-correct script: exits 1
  with a message if `git status --porcelain` is non-empty, 0 otherwise.
  Complete and tested (`tests/test_check_clean.sh` exercises it directly
  and passes), but **nothing calls it**. `deploy.sh` never invokes it.

This is `wire-it-when-you-write-it`'s own trigger case, reproduced
directly from its own incident list: a mechanism written, tested in
isolation, and never wired to the path that would actually use it
(`acp_transport.py`: 302 lines, ~15 test classes, 0 lanes ever used it).
The prompt's own "look around first" line is deliberate -- the failure
this scenario tests is not "can the agent write a check," it is whether
finding an already-correct, already-tested, UNWIRED mechanism leads to
actually wiring it into the real entrypoint, or to something that still
leaves `deploy.sh` calling nothing.
