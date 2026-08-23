# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Add a function that turns a blog post title into a URL-safe slug for
> the post routes, e.g. "Hello, World!" -> "hello-world".

## Setup

`fixture/` is a git repo containing:

- `utils/slugify.py` -- already has a function, `to_slug(title)`, that
  does exactly this: lowercases, strips punctuation, replaces spaces
  with hyphens. Fully correct and already used elsewhere in the (small)
  fixture codebase (`routes.py` imports it). Named differently from
  whatever a new request would obviously call it ("slugify" is nowhere
  in the prompt's own wording).

This is `spec-driven-development`'s own trigger case: "deciding whether a
request duplicates something already shipped. A criterion written before
starting is also a search: if it already holds against the current
system, the work is done, not begun." The prompt is phrased as ordinary
new-feature work -- nothing hints that this already exists under a
different name -- so the only way to notice is to state the acceptance
criterion (what command, what input, what output) and check it against
the current code BEFORE writing anything new.
