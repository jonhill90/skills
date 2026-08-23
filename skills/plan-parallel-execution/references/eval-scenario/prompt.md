# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Group these five tasks into batches that can run concurrently
> without file collisions. List each batch and which task numbers are
> in it.
>
> 1. Add a "gold" tier to wherever customer discount tiers are defined.
> 2. Reject empty passwords at the login entrypoint.
> 3. Add a `currency` field next to the existing pricing-tier
>    definitions.
> 4. Add a simple rate limiter (max 5 attempts per minute) to the
>    login entrypoint.
> 5. Update the README to mention the new gold tier.

## Setup

`fixture/` is a git repo containing `billing/pricing.py` (a
`PRICING_TIERS` dict), `auth/login.py` (a `login()` function), and
`README.md` -- no task names a file path directly; each task
description names a BEHAVIOR ("wherever customer discount tiers are
defined," "the login entrypoint") that only resolves to a real path by
actually reading the fixture.

The collision this scenario plants: tasks 1 and 3 both land in
`billing/pricing.py` ("discount tiers" and "pricing-tier definitions"
are the same dict, described two different ways); tasks 2 and 4 both
land in `auth/login.py` ("login entrypoint," named identically both
times but never as a literal path in the prompt). Task 5 touches only
`README.md` and collides with nothing. A plan that only intersects
LITERAL file-path strings named in the prompt (there are none) finds
zero collisions and groups everything as fully parallel; a plan that
actually derives an ownership manifest from the fixture's real paths
(this skill's own "Mechanize first" section) finds both.
