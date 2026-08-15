---
name: research-the-limit
description: Before asserting that a tool, library, or system cannot do something, check a primary source — its own docs, --help, source, or what is actually installed — rather than asserting from memory. Use whenever about to write or say "X cannot do Y", "there is no way to Y", or plan around a limit nobody has actually checked. Not for judging whether a check's verdict can be trusted (verify-the-instrument) or for reasoning with no command or document available to settle it (sanity-check) — this is specifically for a claimed capability boundary that a primary source can confirm or refute.
---

# Research the Limit

A claim that something is impossible is a claim about the world, and most
of the time a primary source can settle it in minutes: the tool's own
`docs/`, its `--help`, its source, or a five-minute check of what is
already installed. Training data is a fuzzy, dated picture of that world —
some of what it would need is too recent to be in there at all — and the
failure mode this skill exists to stop is specific: an agent hits a wall,
concludes the wall is a property of the world, and designs around a limit
that a primary source would have shown does not exist.

## Reach for this when

- You are about to write or say "X cannot do Y", "there is no way to
  Z", or "that's not supported" — before it lands in a plan, a message, or
  code that routes around the supposed limit.
- A plan is being shaped by a constraint nobody has actually looked up —
  a flag, a capability, a version behavior, an API limit.
- A prior turn, another agent, or your own memory asserted a limit and the
  decision built on it has real cost if the limit turns out to be wrong.

Do not reach for it when the limit is already confirmed by something you
read this session — re-checking a source you already opened is waste, not
diligence. And do not reach for it as a substitute for `sanity-check`: if
there is no primary source to consult at all (the question is a judgment
call, not a fact), dispatching a second reviewer is the right tool, not
this one.

## The practice

1. **Read the tool's own docs first.** Local, free, and current in a way
   no model's training data can be — `<package>/docs/`, `--help`, the
   README, the source itself if nothing else exists.
2. **Check what is already installed or available** before concluding a
   capability is missing. The capability you need is often already on the
   machine, under a name or flag you have not looked for yet.
3. **Search the web for anything that could postdate your knowledge.**
   Tooling changes fast; a limit that was true a year ago may not be true
   now, and a limit you're inferring from an old default may never have
   applied to the current version.
4. **Before writing "X cannot do Y", state how you know.** If the honest
   answer is "I believe it" or "I don't recall it supporting that," that
   is a hypothesis, not a finding — go look before it ships as either.
5. **Prefer the primary source over recollection.** Read the actual
   script, schema, `--help` output, or doc page rather than what you
   remember of a similar tool or an earlier version.

**Cite what you read.** A claim with a source can be checked by someone
else; a claim from memory cannot be distinguished from a guess after the
fact, and reporting it as settled when it was only recalled is what lets a
wrong limit reshape a plan unchallenged.

## What counts as having checked

Not "I'm fairly sure" — a specific artifact read, with what it said:

- "`--help` lists no such flag, and the docs directory has no mention of
  it" is a check.
- "I don't remember it supporting that" is not a check; it is the belief
  this skill exists to interrupt before it is reported as a fact.

If the primary source genuinely cannot be reached — no docs ship with the
tool, it is not installed anywhere available, a web search turns up
nothing current — say that plainly ("could not find a primary source for
this") rather than letting the gap read as a checked "no."

## What this skill is not

It does not decide whether a *check's verdict* can be trusted — that is
`verify-the-instrument`, for a test, review, or metric that already ran.
It does not supply a second reviewer for a reasoning question with no
document or command to settle it — that is `sanity-check`. This skill
owns the narrower moment before a capability boundary gets asserted:
confirm it against a primary source before it becomes the premise of a
plan.

## Where this came from

Three confident claims from the same short stretch of real operation, each
wrong, each reshaping a plan until corrected:

- A CLI tool was declared unusable, inferred from a stale flag list in
  seconds, without opening the docs directory already shipped alongside
  it on disk. Reading it directly turned up several capabilities,
  including exactly the transport mode the plan needed — which reshaped
  the whole approach that had just been designed around its absence.
- A terminal multiplexer was declared incapable of a specific layout,
  asserted without looking. It took one real check to find several
  actively maintained tools that already do it, over a dedicated element,
  not the fallback the assertion had assumed was the ceiling.
- An agent's inability to see the rendered output of a terminal UI was
  accepted as an open problem and filed as one. It was solved within the
  hour with tools already installed on the machine — capturing the
  terminal's own frame buffer (which already carries color and layout,
  the same way a browser's DOM carries a rendered page) and converting it
  to an image. The analogy that had been used to justify the limit
  ("there's no way to screenshot a terminal") was exact in the wrong
  direction and nobody had checked it.

Recorded portably in issue jonhill90/skills#174; the underlying
transcripts are private daily-operation records, not published in this
collection.
