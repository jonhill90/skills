---
name: derive-independently-then-compare
description: Derive an answer from the source corpus a second time, without reading the first derivation, then compare — before trusting a conclusion drawn from a large body of transcripts, notes, or documents about what someone wants, prefers, or constrains. Use when a claim about a person's stated intent or a parameter cannot be traced to a quote, or before that claim is reported as fact. Runs before sanity-check and devils-advocate, not instead of them — a reviewer or an opposing case inherits whatever inputs the first pass fabricated, and this is the only one of the three that re-reads the source rather than the write-up. Not ask-a-council (different positions on a shared question, not the same question re-derived from source); not determine-signals (finds what was already checked, not whether what was reported was actually found there).
---

# Derive Independently, Then Compare

A reviewer checks whether reasoning holds. It cannot see that the inputs
were fabricated — it reads the write-up, not the source, and inherits
whatever the write-up claims the source said. The only check that catches
a fabricated input is one that goes back to the source itself and derives
the answer again, without looking at the first answer first.

## Reach for this when

- A claim about what someone wants, prefers, or requires is about to be
  reported as fact, and it rests on reading a large corpus — transcripts,
  issues, notes, a chat history — rather than on a single stated
  instruction.
- The claim names a specific parameter, constraint, or preference and you
  are not sure you could produce the exact quote it came from on demand.
- The corpus is large enough that "I read enough of it" is doing
  unverified work — the failure this skill targets gets *worse* as the
  corpus grows, not better, because the unread fraction rises and locking
  on after two or three files becomes easier to do unnoticed.

Do not reach for this to test whether already-produced reasoning is
internally consistent — that is `sanity-check`, and it runs *after* this
one, on inputs this skill has already checked. Do not reach for this to
argue against a conclusion — that is `devils-advocate`, and it also
assumes the inputs are real; this skill is what earns that assumption.

## The worked example

Asked whether Jon wanted a live terminal, an agent read the corpus once
and reported:

1. It took **one** quote about *chat threads* being live.
2. It generalized that quote to *terminal rendering* — a different
   subject the quote never addressed.
3. It **invented** a parameter Jon never stated —
   `survives-a-web-frontend` — which had **zero hits across 1,968 typed
   turns**.
4. From the invented parameter it declared a "near zero-possibility
   conflict."
5. It reported all of this to Jon **as derived from his own words**.

The reasoning from step 3 to step 4 was internally coherent — a reviewer
reading only the write-up would find no fault in it. The defect was in
step 1 through 3: the inputs were invented, not derived. A second,
independent derivation from the same 1,968-turn corpus — one that never
read the first agent's write-up — knocked down two of the three
underlying claims and surfaced that the third had no source at all. Read
[references/worked-example.md](references/worked-example.md) for the full
derivation-by-derivation breakdown.

## Procedure

1. **Enumerate before deciding.** Before drawing any conclusion, state
   how much of the corpus exists and how much you have actually looked
   at — N and the denominator. "I read 3 of 40 transcripts" is honest;
   "I read 3 transcripts" is not, because it hides whether 3 was a
   survey or the whole population. A conclusion with no stated
   denominator is not a conclusion — treat it as underived and go back.

2. **Survey breadth before committing to depth.** Sample across the full
   space first — different time periods, different sources, different
   threads — before reading any one part closely. The failure this
   guards against is locking onto an interpretation after two or three
   files and never revisiting it once contradicting material shows up
   later in the corpus.

3. **Derive twice, independently, before comparing.** Produce a first
   derivation from the source. Then produce a second derivation from the
   *same source*, by an agent or pass that has not read the first
   derivation's answer or write-up — only the raw corpus. If the second
   pass can see the first pass's conclusion before it finishes its own,
   it is review wearing a different name, not independent derivation,
   and it will inherit the first pass's fabrications instead of catching
   them.

4. **Cite or drop.** Every claimed parameter, preference, or constraint
   must carry the quote it came from — source and locator, not a
   paraphrase. If you cannot produce the quote, the claim is an
   invention, not a finding: drop it, or mark it explicitly as
   unsupported rather than reporting it as derived. This is the cheapest
   guard in this skill and alone would have caught the worked example's
   fabrication.

5. **Compare, and treat every disagreement as a finding.** Line the two
   derivations up claim by claim. Where they agree, that is weak
   evidence — two passes over the same corpus converging is expected
   even when both are shallow. Where they disagree, that is strong
   evidence something is wrong: one derivation cited a quote the other
   didn't find, one invented a parameter the other's pass through the
   same material never touched. Do not average disagreements away or
   split the difference — chase each one down to which derivation the
   quote actually supports, and report the disagreement itself as a
   result, not just its resolution.

## What this is not

- **Not `devils-advocate`.** That skill attacks a *conclusion*, assuming
  it is wrong and building the strongest opposing case. This skill
  attacks the *inputs* the conclusion was built on, and it must run
  first — there is no point building or opposing a case whose premise is
  fabricated.
- **Not `sanity-check`.** That skill dispatches a reviewer against
  reasoning that has already been produced, checking whether it holds
  together. It reads the write-up, so it inherits whatever inputs the
  write-up claims — exactly the gap this skill exists to close before a
  sanity-check pass would be trustworthy.
- **Not `ask-a-council`.** A council assigns several reviewers *different
  positions* on a shared question because the candidate failure modes
  differ in kind. This skill asks the *same* question of the *same*
  source twice, independently, and checks whether the two derivations
  agree — not different lenses, the same lens applied twice blind.
- **Not `determine-signals`.** That skill finds what has already been
  checked, so a question isn't re-asked when it's already answered
  somewhere. This skill doesn't ask whether something was checked — it
  verifies that what was *reported* as found in the source was actually
  in the source.

## Where this came from

A measured instance: an agent asked whether Jon wanted a live terminal
fabricated a parameter (`survives-a-web-frontend`, zero hits across 1,968
typed turns) and reported it as derived from Jon's own words. An
independent re-derivation from the same corpus — run blind to the first
agent's write-up — knocked down two of the three underlying claims and
surfaced that the third had no source at all. A review of the write-up
alone would not have caught this: the reasoning was coherent, only the
inputs were invented. See
[references/worked-example.md](references/worked-example.md).
