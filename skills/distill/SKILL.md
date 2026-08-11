---
name: distill
description: Reduce a large body of source material to the smallest thing a reader can act on, at the cost of proportion — not a shorter version of everything, a decision about what matters. Use when asked to distill, or when the request is "what do I do about this" rather than "what does this say"; not for a summary that must preserve proportion.
---

# Distill

A summary shortens while keeping proportion — every section of the source
gets a smaller version of itself. A distillation does the opposite: it
discards most of the source and keeps only what the reader must act on. That
trade is deliberate, and it is why a distillation reads shorter and more
opinionated than a summary of the same material would.

## Reach for this when

- The request is "what do I do about this", "pull the working position out
  of this", or a corpus is standing between the reader and a decision.
- The source is large enough that quoting or restating all of it would bury
  the part that matters.
- The output will be read again later, as a live input to work — not filed
  once and forgotten.

Do not reach for it when the request is "what does this say" or "shorten
this" — that is a summary, and proportion is the point of a summary. Do not
reach for it to compress a single short document; distillation earns its
cost against a corpus, not a paragraph.

## The discipline

Five practices, each one a place a distillation quietly fails if skipped.

1. **State what was read and what was not.** Name every source file
   consulted, and name what was deliberately skipped and why — a
   distillation that hides its coverage cannot be audited, and a reader
   cannot tell "considered and excluded" from "never seen." If a skipped
   file's content was inherited through another source (a recommendations
   doc that already quotes it), say that explicitly rather than implying
   independent verification.
2. **Distill, do not quote.** State the position in your own words, sourced
   to where it came from. If checking the output against the source would
   mostly find matching sentences, it is a merged archive, not a
   distillation — go back and cut harder.
3. **Preserve the provenance of confidence.** A number or claim from the
   source is either what the source measured, or what it inferred, argued,
   or predicted — carry that distinction into the output instead of
   flattening everything to flat assertion. An inferred figure that reads as
   measured is the single most common failure here, and it is always
   self-flattering: it makes the corpus look more settled than it is.
4. **Record disagreement instead of smoothing it.** When the corpus and the
   consuming context's already-decided position diverge, say so and name
   which one governs. Dropping the conflict to make the output read cleanly
   destroys the most valuable thing a corpus can hand over — that two
   sources of judgment did not agree.
5. **Say what the output is for.** A distillation that will be read again
   and edited as work continues is shaped differently from one that
   archives a decision once — name which this is, because it changes what
   belongs in it.

## What this skill is not

It is not a compression technique — cutting word count without changing what
is kept is still a summary, just a terser one. It is not an excuse to drop
sourcing: every claim in the output still traces to a file, not to the
distillation's own authority. And it is not for a corpus you have not
actually read — practice 1 only works if there is real coverage to report.

## Worked example

`docs/loop-engineering.md` in Jon Hill's `agent-dotfiles` repository (merged
2026-08-11) distilled a 23-file external research corpus into one working
document for that repository. It names the seven files it read and the
sixteen it skipped and why, states positions in its own words rather than
quoting the corpus, marks each figure as the source's measurement or its
inference, records one place the corpus and the repository's decided
position diverged and says which one governs, and states up front that it is
a living document future work edits, not an archive. Read it as an example
of the shape this discipline produces, not as a template to copy — the
divergence it records and the files it names are specific to that corpus and
will not recur in a different one.
