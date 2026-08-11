---
name: spec
description: Author or review a technical specification — architecture, interfaces, data flow, and the implementation approach engineers will build against, plus the trade-offs behind the choices made. Use when asked to write, update, or review a technical spec or design doc, or to decide how something will be built once what it should do is already settled. Not for defining what a product should do and why, or who it's for — that is prd, which a spec is written against. Not an in-session pre-flight checklist for a single change — see close-the-loop for that.
---

# Spec

A technical specification answers a different question than a PRD: given
an agreed problem and success criteria, how will this actually be built?
It is audience-facing to engineers who will implement or maintain the
system — interfaces, data flow, architecture, and the trade-offs behind
choices that a PRD would never mention (a PRD says a feature must be fast;
a spec says why it's a cache versus an index versus a precomputed table,
and what each costs).

## Reach for this when

- Asked to write, update, or review a technical spec or design document.
- Asked to decide *how* something will be built, once *what* it should do
  and *why* are already settled — by a `prd`, by an existing decision, or
  because the scope is small enough that a separate PRD would be
  overhead.
- Reviewing an existing spec for whether its architecture actually
  satisfies the requirements it claims to implement.

Do not reach for it when the request is about what a product should do
and for whom before any technical approach is chosen (`prd`), a checklist
for whether one already-scoped change is ready to start (`close-the-loop`),
or in-session planning for a single PR with no durable document intended
(the operating loop's plan step already covers that; not every plan needs
a spec).

## Structure

Every section should let a reader implement or review without having to
ask the author what was meant.

1. **Context and requirements.** What this is being built to satisfy —
   link the PRD if one exists; state the requirement inline if the scope
   is small enough not to have one. A spec that doesn't say what it's
   satisfying can't be checked against anything.
2. **Approach.** The architecture or design chosen: components, interfaces,
   data flow, how they fit the existing system. Concrete enough that a
   different engineer implementing from this document would build
   something comparable, not just directionally similar.
3. **Alternatives considered and rejected.** At least the options that
   were genuinely live, with the reason each was passed over. An
   alternatives section with no real alternatives in it is decoration.
4. **Trade-offs and risks.** What this approach costs — performance,
   complexity, a dependency taken on, a case it doesn't handle — stated
   plainly rather than buried in the approach section where a reader
   skimming for "does this work" will miss it.
5. **Verification.** How the spec's claims will be checked once built —
   the tests, the metrics, the manual check — not what the PRD's success
   criteria are (those live there), but how *this specific implementation*
   will be confirmed to meet them.

## What this is not

- Not a PRD. If you find yourself stating why a problem matters to a user
  or business rather than how a chosen solution works, that content
  belongs in the corresponding `prd` — move it there, or flag that one is
  needed first.
- Not a pre-flight checklist. `close-the-loop` confirms a single
  already-scoped change has everything it needs before starting; a spec
  is a durable document read by people who were not in the room when it
  was written, not a readiness gate for one PR.
- Not required for every change. Small, well-understood changes go
  straight to implementation; write a spec when the design has real
  alternatives worth recording or will outlive the person who wrote it.
