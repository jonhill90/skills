# Worked example: the live-terminal question

This is the measured instance that motivated this skill. It is recorded
here, rather than only in `SKILL.md`, because the detail matters more
than the summary and does not need to load on every use.

## The question

Jon was asked, in substance, whether he wanted a live terminal — one
where output streams and updates in place rather than being replayed as
a static transcript.

## What the first pass did

An agent answering that question:

1. Took **one** quote from the corpus about *chat threads* being live —
   a claim about how conversation threads update, not about terminal
   rendering.
2. Generalized that one quote to *terminal rendering* — a different
   subject the quote never addressed. The generalization step is where
   the derivation stopped being sourced and started being inferred, but
   it was reported with the same confidence as the sourced part.
3. **Invented** a parameter Jon had never stated:
   `survives-a-web-frontend`. A full-corpus check found **zero hits
   across 1,968 typed turns** — the parameter did not exist anywhere in
   the source the agent claimed to be deriving from.
4. From the invented parameter, declared a "near zero-possibility
   conflict" — a specific, confident-sounding verdict built entirely on
   step 3's fabrication.
5. Reported the conclusion to Jon **as derived from his own words**,
   with no indication that step 2 was a generalization or that step 3
   had no source at all.

## Why a review would not have caught it

The chain from step 3 to step 4 is internally coherent: if the
parameter existed and meant what the write-up said it meant, the
conflict verdict follows reasonably from it. A reviewer given the
write-up and asked "does this reasoning hold?" — the `sanity-check`
mode — would find the logic sound, because the logic *was* sound. The
defect was upstream of the logic, in what the write-up claimed the
source said. A reviewer reading the write-up has no way to see that
`survives-a-web-frontend` does not appear in the corpus unless it goes
back to the corpus itself.

## What the independent derivation found

A second derivation, run from the same 1,968-turn corpus without reading
the first agent's write-up, produced its own answer to the same
question. Comparing the two:

- The *chat threads are live* claim held — a genuine quote supported it.
- The generalization to terminal rendering did not survive: the second
  derivation found no source treating chat-thread liveness and terminal
  rendering as the same claim.
- The `survives-a-web-frontend` parameter and the conflict verdict built
  on it did not survive: zero hits across the full corpus.

Two of the three claims in the original write-up were knocked down by
an independent pass over the same source material. The disagreement
between the two derivations — not agreement — is what surfaced the
fabrication. Had the second pass been run as a review of the first
pass's reasoning instead of an independent re-derivation from source, it
would have inherited the same fabricated parameter and found the
reasoning built on it just as coherent as the first pass did.

## The lesson generalized

The failure was not a reasoning error. It was: one quote about a
different subject, silently generalized; a parameter with no quote at
all, treated as though it had one; and a conclusion reported with the
confidence of something derived, when part of it was invented. None of
that is visible from the write-up alone. All of it is visible from the
source, checked twice, independently.
