# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Write a PRD for a new feature: letting a user export their account data
> to a CSV file. Explain what problem it solves, for whom, and how we'd
> know it's actually done. Keep it to what a product stakeholder needs,
> not an engineer.

## Setup

`fixture/` is an empty git repo — this scenario is a pure writing task with
no code to inspect or edit, so there is nothing else to seed.

## The trap

"Export to CSV" is a request with an unusually short, obvious-looking
distance to an implementation: it names its own output format. That makes
it easy to drift into describing *how* the export would be built — an
endpoint, a background job, a storage location, a library — while writing
what is nominally a requirements document. `prd`'s own SKILL.md draws this
exact line explicitly ("Not a technical design. If you find yourself
naming a database, an API shape, or a library while writing this, that
content belongs in the corresponding `spec`") and the scenario is built to
test whether that line holds when the request practically hands the
writer a shortcut across it.
