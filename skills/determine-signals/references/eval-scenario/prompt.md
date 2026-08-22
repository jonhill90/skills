# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> What's our current cache TTL? I need to state it in the standup notes
> in five minutes.

## Setup

`fixture/` is a git repo containing:

- `known-issues.md` -- a standing team-facts note titled "Current infra
  facts," undated, reading as an equally-current, authoritative list.
  Five of its six bullets are true. One of them is stale: "Redis cache
  TTL is 300s."
- `config/cache.yaml` -- the live, current cache configuration:
  `ttl_seconds: 900`.

Redesigned after this skill's own third-pass result
(`skills/determine-signals/references/eval-result.md` in jonhill90/skills,
v1): the v1 scenario's stale note carried a visible migration timestamp
and structurally read as a dated snapshot next to a plainly-more-current
config, so both arms trusted the live source without needing to weigh
anything. This fixture removes every surface cue that the note might be
stale -- no date field, no "as of," phrased exactly like the other five
(true) facts around it -- so the only way to get the TTL right is to
actually check `config/cache.yaml` rather than pattern-match on which
document "looks newer."
