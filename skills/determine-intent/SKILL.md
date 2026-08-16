---
name: determine-intent
description: Work out what the user actually wants — from the literal words of the request and from what they have already told you — before starting the work, and state that reading so it can be corrected. Use before acting on a non-trivial request, especially one that echoes something asked before, one that could be read more than one way, or one that may sit against a goal the user has already stated elsewhere. Not for checking reasoning you already produced (see sanity-check, which runs after) and not for confronting a claim the user just made (see keep-me-honest, which reacts to a conflict already visible) — this skill runs before work starts and is about the goal, not the method or a specific statement.
---

# Determine Intent

A request repeated more than once was not understood the first time. When
that happens, supplying the missing understanding by voice, again, is not
a fix — it is the user doing the work this skill should do. Before starting
on a non-trivial request, work out what is actually wanted: the literal
sentence in front of you, and the goal behind it, are not always the same
thing, and building the first when the second was meant is a failure that
looks like success until the output is checked against the real want.

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

1. **Separate the literal ask from the underlying goal.** State both, even
   when they match. "You asked for X; the goal driving that looks like Y"
   makes the read visible instead of silently substituting one for the
   other.
2. **Consult what the user has already told you before inferring intent
   from this one message.** Standing notes, memory facts, prior threads on
   this same topic, an earlier decision on the same question — read them
   before concluding this request is a fresh, isolated ask. A message that
   looks new is often the third instance of an old one.
3. **Surface conflicts instead of silently resolving them.** Users hold
   goals that genuinely conflict — move fast *and* wait for confirmation,
   minimize cost *and* maximize thoroughness. When the request sits on one
   side of a conflict like that, say so and ask which one governs here,
   rather than picking a side and proceeding as if there were no tension.
4. **State the intent you are acting on, and make it correctable.** A
   silent assumption cannot be caught before the work is done; a stated
   one can be corrected in one turn. Put the reading where the user will
   see it before the work starts, not buried in a summary after.
5. **Proceed once the reading stands unchallenged** — do not treat this as
   a license to interrogate every request into a questionnaire. One stated
   reading, one chance to correct it, then act.

## What this is not

- Not `sanity-check`. That skill dispatches a second reviewer to test
  reasoning that already exists — a plan, a diagnosis, a rationale. This
  skill runs earlier, before there is any reasoning to test, and its
  question is "what does the user want," not "does this hold up."
- Not `keep-me-honest`. That skill reacts to a conflict already visible
  between something the user just asserted and something you observed.
  This skill runs before the user has asserted anything about the work at
  hand — it is about recovering a goal that was never fully stated, not
  about correcting a claim that was.
- Not a substitute for asking a clarifying question when the request is
  genuinely underspecified. Determining intent from available context
  comes first; if the context does not settle it, ask — do not guess
  further and label the guess "determined."
- Not a mandate to second-guess every request. The failure this skill
  targets is specific: work that matches the words but misses the goal,
  usually visible because the same ask keeps recurring or because two
  known goals point different directions. Where neither sign is present,
  a plain reading is the right reading.
