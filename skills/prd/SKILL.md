---
name: prd
description: Author or review a Product Requirements Document — the problem being solved, who it's for, the goals and explicit non-goals, and the success criteria a stakeholder would use to judge whether the problem is actually solved. Use when asked to write, update, or review a PRD, or to define what a product or feature should do and why before any technical approach is chosen. Not for how it will be built — that is spec, which a PRD hands off to once the problem and goals are settled. Not a general project plan or pre-flight checklist — see close-the-loop for that.
---

# PRD

A Product Requirements Document answers one question: what problem is
being solved, for whom, and how will anyone know it's solved? It is
audience-facing to stakeholders who may never read the implementation —
product owners, other teams, future maintainers deciding whether a
feature still matches its original intent. It deliberately excludes
architecture, interfaces, and implementation approach; those belong in a
`spec` written against this document, not inside it.

## Reach for this when

- Asked to write, update, or review a PRD specifically.
- Asked to define what a product or feature should do, for whom, and why
  — before any technical approach has been chosen.
- A `spec` is being requested but no PRD exists yet to hand off from; flag
  the gap and offer to write the PRD first rather than letting the spec
  invent requirements it should be receiving.

Do not reach for it when the request is about *how* something will be
built (`spec`), a checklist for whether a specific change is ready to
start (`close-the-loop`), or a reduction of existing material to what a
reader needs to act on (`distill`).

## Structure

Keep every section traceable to a decision someone will actually make from
it. A section nobody will use to decide anything is padding.

1. **Problem.** What is broken, missing, or costly today, for whom,
   evidenced where possible — not asserted. If there's no problem, there's
   no PRD; say so instead of inventing one to justify a solution already
   chosen.
2. **Goals.** The outcomes this delivers, stated as what changes for the
   user or business, not as a list of features.
3. **Non-goals.** What this explicitly does not attempt, named as
   specifically as the goals. A PRD without non-goals invites scope creep
   because nothing in it says no.
4. **Success criteria.** Observable conditions a stakeholder — not an
   engineer — could check to tell whether the problem from section 1 is
   actually solved. If a criterion requires reading the implementation to
   evaluate, it belongs in the spec instead.
5. **Audience / users.** Who this is for, and who it is explicitly not
   for, when that distinction changes what gets built.

## What this hands off

A PRD that's ready to hand to `spec` states the problem and success
criteria concretely enough that two different engineers reading it would
propose comparably-scoped solutions, even if their technical approaches
differ. If the problem statement is vague enough that a spec would have to
guess at what "done" means, the PRD isn't finished yet — finish it before
handing off, rather than letting the spec quietly redefine the problem to
fit a chosen implementation.

## What this is not

- Not a technical design. If you find yourself naming a database, an API
  shape, or a library while writing this, that content belongs in the
  corresponding `spec` — move it there.
- Not a general plan. `close-the-loop` checks whether a already-scoped
  change has everything it needs to start; a PRD exists upstream of that,
  before the change is scoped at all.
- Not a summary of existing material. `distill` reduces a large source to
  what a reader can act on; a PRD originates requirements, it doesn't
  compress something that already exists.
