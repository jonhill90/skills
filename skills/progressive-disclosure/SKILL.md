---
name: progressive-disclosure
description: Load a large corpus, document set, or codebase the way an index is meant to be used — read the index first, pull individual files or facts in on demand as the task actually needs them, and stop once there is enough to act, instead of reading everything up front. Use before reading many files, an entire directory, or a large document set for a task that plausibly needs only a fraction of it.
---

# Progressive Disclosure

Reading everything before starting is the easiest way to answer "did I miss
something," and the most expensive. An index exists precisely so that most of
a corpus never has to be read for most tasks — reading it anyway is a choice
to spend tokens and turns buying certainty the task didn't ask for.

## Reach for this when

- About to read every file in a directory, every reference in a skill or
  doc set, or an entire corpus, before knowing which parts the task needs.
- An index, table of contents, header list, or one-line-per-entry summary
  exists (or could cheaply be produced) that would let the right subset be
  identified without opening everything.
- The corpus is large enough, or growing, that "read it all" will not keep
  working — not just slow, but eventually impossible within budget.

Do not reach for this when the task already names the specific file, or the
corpus is small enough that reading all of it costs less than the overhead of
deciding what to skip — the discipline exists to save cost, not to add a
detour when there was nothing to save. Do not reach for this to decide WHICH
source to trust when several disagree — that is `determine-signals`. Do not
reach for it to turn a large corpus into one artifact for someone else to
read later — that is `distill`, and it runs on material already loaded,
not on the decision of how much to load. `memory-conventions` is one
concrete instance of this pattern, scoped to the durable-fact vault
specifically (`index.md`, capped, facts loaded on demand) — read this skill
for the general discipline, that one for the vault's own layout.

## The discipline

1. **Read the index, not the corpus.** If no index exists, its cheapest
   substitute — a directory listing, a table of contents, a grep for
   headers — still costs less than opening every file, and is worth
   building first for that reason alone.
2. **Name what the task needs before opening anything.** State, even in one
   line, what specific fact or file would resolve the task. An index entry
   that plausibly matches is a candidate to open; entries that don't match
   are not insurance against having missed something — leave them closed.
3. **Open on demand, not in a batch.** Pull in the one file the task points
   to, check whether it was enough, and only then decide whether a second
   file is needed. Queuing "just read all of these while I'm at it" defeats
   the discipline even when each individual read looked justified in
   isolation.
4. **Stop when there is enough to act.** More reading past that point is not
   free caution — it is the exact cost this skill exists to avoid. If the
   task can be answered from what has been opened so far, answering is the
   next step, not one more file "to be sure."
5. **Say what was skipped, when it matters.** A task that visibly opened
   3 of 50 available files should be able to name, briefly, why the other
   47 were not needed — not enumerate them, just confirm the omission was a
   decision, not an oversight. This is `distill`'s first practice, reused
   here for the same reason: coverage that can't be audited invites the
   same "did I miss something" anxiety this skill is meant to remove.

## This repository practices what it teaches

The evidence is not hypothetical — every skill in this collection is built
this way. `SKILL.md` stays under 500 lines and points into `references/`
for anything that "changes what belongs in it" only for some requests
(`create-skill`'s own instruction); a skill's `references/` directory is
read on demand, never loaded by default. `memory-conventions`' own
`agent/index.md` is capped at 200 lines / 25KB specifically so a session
start reads the index, not the vault. The Explore search agent reads
excerpts rather than whole files for the same reason this skill exists: it
locates code without paying to read everything it locates. None of this is
a coincidence — it is the same discipline, applied consistently, and it is
why a search for "how should this skill demonstrate its own advice" turns
up working examples already in the tree rather than a hypothetical.

## What this skill is not

It is not a rule to always read less — a task that genuinely needs broad
context (an audit, a full-repo migration, "read everything and tell me
what's inconsistent") should read broadly; the discipline is deciding that
on purpose, not skipping it by default. It is not a caching or
summarization technique — the index is not a compressed copy of the corpus,
it is a map of where to look, and using it still means reading the real
file when the task needs the real file's content, not the index entry's
one-line gloss.
