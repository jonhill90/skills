---
name: determine-intent
description: Work out what the user actually wants — from the literal words of the request and from what they have already told you — before starting the work, and state that reading so it can be corrected. Use before acting on a non-trivial request, especially one that echoes something asked before, one that could be read more than one way, or one that may sit against a goal the user has already stated elsewhere. Not for finding out what has already been said (see determine-signals, which runs on the same "before acting" moment but asks the record, not the goal); not for checking reasoning you already produced (see sanity-check, which runs after); not for confronting a claim the user just made (see keep-me-honest, which reacts to a conflict already visible); not for building the case against a plan (see devils-advocate, which opposes a conclusion, not a request) — this skill runs before work starts and is about the goal, not the record, the method, or a specific statement.
---

# Determine Intent

A request repeated more than once was not understood the first time. When
that happens, supplying the missing understanding by voice, again, is not
a fix — it is the user doing the work this skill should do. Before starting
on a non-trivial request, work out what is actually wanted: the literal
sentence in front of you, and the goal behind it, are not always the same
thing, and building the first when the second was meant is a failure that
looks like success until the output is checked against the real want.

## The model: intent is a constraint solve, not interpretation

Treat yourself as a generate-anything machine. Capability was never the
constraint — you could produce any of a huge number of valid answers to
most requests. What is scarce is generating more than a handful of them
and choosing among the pile, and doing that costs tokens and time you do
not have unlimited amounts of. A request is not a description to interpret;
it is a set of parameters — filters and statements — that prune the space
of everything you could generate down to the range you should. **A
prompt's worth is measured by the generations it prevents, not by how
evocatively it describes the one you land on.**

This reframes the whole skill: "determine intent" means *count how many
things satisfy the stated constraints*, not *guess which one thing was
meant*. The count is the diagnosis.

## Reach for this when

- The request is non-trivial — the kind where getting the goal wrong costs
  real work, not a quick redo.
- The request echoes something asked before, in this conversation or in
  prior history available to you. A second or third ask of the same thing
  usually means the underlying goal was missed, not that the user enjoys
  repeating themselves.
- The literal wording admits more than one reasonable reading, and the
  readings lead to different work.
- Acting on the literal request would sit against something the user has
  said elsewhere — a standing preference, a prior decision, a rule they
  set for exactly this kind of situation.

Do not reach for it for genuinely simple, unambiguous asks — interrogating
intent behind "fix this typo" manufactures friction the request never
needed. Save it for the requests where a wrong read is expensive.

## What to do

1. **List the constraints, each one carrying a quote.** Pull every filter
   and statement the request actually asserts — from this message, from
   standing notes, from memory facts, from an earlier decision on the same
   question — and attach the exact words each one comes from. **A
   constraint with no quote does not go on the list.** This is a hard
   requirement, not a style preference: an uncited constraint is not a
   real filter, it is one you hallucinated and then let narrow the search
   as if the user had said it. See "Every parameter carries a quote"
   below.
2. **Solve for how many possibilities the cited constraints leave, and act
   on the count** — this is the core of the skill; see "The target is a
   range" below. Do not stop at "is there a conflict?" — a request with no
   conflict can still be zero, many, or a few, and each of those needs a
   different response.
3. **State the intent you are acting on, and make it correctable.** Once
   the count says "exactly one," say what that one is and why — "You asked
   for X; given [quoted constraints], the goal driving that looks like Y"
   — so a silent assumption isn't the thing that ships. A stated reading
   can be corrected in one turn; a silent one can only be corrected after
   the work is done.
4. **Proceed once the reading stands unchallenged** — do not treat this as
   a license to interrogate every request into a questionnaire. One stated
   reading, one chance to correct it, then act.

## The target is a range, not a floor

The old failure mode was treating "no conflict found" as done. It is not.
Every request resolves to a count of surviving possibilities, and the
count has four zones, each with its own response — "best guess" is not one
of them:

- **Zero → over-constrained.** The cited constraints leave nothing.
  **Ask the user to relax one** — name which constraints collided and let
  them choose, rather than silently dropping one yourself. See "Three ways
  to reach zero" below for how zero actually happens; most of the time it
  is not a direct contradiction.
- **Too many → under-constrained.** A "best guess" here is not a
  judgment call, it is a random pick dressed up as one — nothing in the
  stated constraints favored the guess over the alternatives it beat.
  **Do not silently choose.** Narrow using the corpus (standing notes,
  memory, prior decisions on this same question) first; if that still
  doesn't collapse the range, ask. Silently picking one and presenting it
  as "the" answer is the failure mode this skill previously had no name
  for — name it when it happens.
- **A few → healthy, route to variants.** A handful of live candidates is
  not a problem to resolve into one — it is the right amount of ambiguity
  to build. Construct them as variants and hand off to `decide-by-variant`
  so the user cycles through real output rather than answering a
  clarifying question about a hypothetical. Collapsing "a few" into a
  single guess throws away options that were cheap to build and expensive
  to reconstruct if the guess was wrong; collapsing it into a question
  makes the user do in words what variants would do in seconds.
- **Exactly one → act, do not ask.** The constraints fully determine the
  answer. Stating the reading (step 3 above) is still required — silence
  is still silence — but do not turn a determined answer into a question.
  Asking here is the mirror-image failure of guessing when there are many.

## Every parameter carries a quote

A filter that cannot be traced to something the user actually said or
wrote is not a constraint — it is a phantom, and phantoms are how a
request gets miscounted as zero when the true count was one or a few.
Before a constraint is allowed to prune anything:

- It must have a quote — the user's words, a memory fact's text, a prior
  decision's actual wording. "It seems like he'd want X" is not a quote.
- The quote must be load-bearing for the *specific* reading, not just
  thematically related. A stray aside ("we don't always have to build
  from scratch") is not the same as a stated requirement ("must build
  from scratch") — see "different weights" below for the general version
  of this mistake.

Treat an uncited constraint the way you would treat an unverified claim in
a review: it does not get to participate in the solve. Drop it and recount
before concluding zero, before concluding conflict, before concluding
anything the phantom constraint was propping up.

## Three ways to reach zero — only the first is obvious

"Zero possibilities" is usually read as "a direct contradiction," but that
is the rare case. Check for all three before telling the user the request
is impossible:

1. **Direct contradiction.** Two cited, simultaneously-live, hard
   constraints assert opposite things (red vs. blue). Rare, and usually
   visible on inspection.
2. **Accidental over-constraint.** Every constraint is satisfiable alone;
   no combination of them is. *Live rendering* + *no new dependencies* +
   *ship this week* can each look completely reasonable in isolation while
   leaving nothing standing together. This is the common case, and it is
   invisible if you only check constraints pairwise — check the full
   combination, not just each pair of constraints against each other.
3. **Phantom constraint.** A filter nobody actually set gets treated as
   binding, and the real constraints get sacrificed to satisfy it. This is
   the most dangerous of the three, because the zero-possibility verdict
   looks well-reasoned right up until someone checks whether the deciding
   constraint was ever said. "Every parameter carries a quote" above
   exists specifically to catch this before it reaches a verdict.

## Two things that look like conflicts and are not

Both of these produce a *sequence* of statements that read as contradictory
on their face. Neither is a conflict once the actual relationship between
the statements is checked.

- **Different weights.** "Probably red" and "must be blue" are not two
  colliding hard constraints — only two *hard* constraints can actually
  collide. A soft preference loses to a hard requirement; it does not tie
  with it. Before calling something a conflict, check whether both sides
  are actually binding, or whether one is a stated certainty and the
  other is a hedge, an aside, or a "we don't always have to" — those carry
  weight, not force, and do not get to veto a hard constraint.
- **Different times.** Red stated Monday and blue stated Friday is not a
  conflict, it is an update — blue supersedes. Only constraints that are
  simultaneously live can conflict; a later statement on the same question
  retires the earlier one rather than competing with it. Check whether
  both constraints are still current before treating their difference as
  a collision.

## What this is not

- Not `determine-signals`. That skill runs at the same "before acting"
  moment and is the nearest real collision, but it asks a different
  question: what has already been said, and which source to believe when
  two disagree. This skill asks what is wanted. Run `determine-signals`
  first when the two would otherwise compete — the record informs the
  goal, not the other way around.
- Not `decide-by-variant`. That skill builds and presents the actual
  variants once "a few" possibilities have been identified here. This
  skill decides *that* the count calls for variants and what the surviving
  candidates are; it does not build or present them.
- Not `sanity-check`. That skill dispatches a second reviewer to test
  reasoning that already exists — a plan, a diagnosis, a rationale. This
  skill runs earlier, before there is any reasoning to test, and its
  question is "what does the user want," not "does this hold up."
- Not `keep-me-honest`. That skill reacts to a conflict already visible
  between something the user just asserted and something you observed.
  This skill runs before the user has asserted anything about the work at
  hand — it is about recovering a goal that was never fully stated, not
  about correcting a claim that was.
- Not `devils-advocate`. That skill builds the strongest case against a
  conclusion already reached, before it is committed to. This skill runs
  earlier still, before there is a conclusion to oppose — it establishes
  the goal a plan will later be built and argued against.
- Not a substitute for asking a clarifying question when the request is
  genuinely underspecified. Determining intent from available context
  comes first; if the context does not settle it, ask — do not guess
  further and label the guess "determined."
- Not a mandate to second-guess every request. The failure this skill
  targets is specific: work that matches the words but misses the goal,
  usually visible because the same ask keeps recurring or because two
  known goals point different directions. Where neither sign is present,
  a plain reading is the right reading.

## Where this came from, and the case it must resolve correctly

This skill shipped as jonhill90/skills#193. The same afternoon, a watchdog
run using it asked the user a question his own corpus already answered,
and separately built a "near zero-possibility conflict" out of a parameter
he had never stated — `survives-a-web-frontend`, invented, uncited, and
then treated as binding enough to override a real constraint. That
incident (jonhill90/skills#213) is the eval this version must pass:

- Given a corpus that already contains the answer to a live-rendering
  question, this skill must resolve it **without asking** — the answer was
  one cited constraint away, and asking anyway is the "too many" failure
  turned on its head: treating a determined answer (count of one) as if it
  were unresolved.
- Given `survives-a-web-frontend` with no quote behind it, this skill must
  **reject the parameter** — recount without it — rather than building a
  zero-possibility verdict on top of it.

A version of this skill that resolves the first case correctly but still
lets an uncited parameter drive a verdict in the second has not implemented
the change; both have to hold at once.
