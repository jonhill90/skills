---
name: decide-by-variant
description: Build several genuinely different real artifacts in the real medium with fake data, and let the human pick by looking, instead of asking a taste decision in prose. Use whenever a decision has no objectively right answer — a glyph, a layout, a default, a name, a wording, a sort order — and describing the options in words would cost the human more thought than looking at them would. Run determine-intent first — if the answer is already a known parameter, build nothing. Not for getting different positions from agents on one question (ask-a-council); not for attacking an answer once chosen (devils-advocate runs after a variant is picked, not instead of building one).
---

# Decide by Variant

*"If you have questions just make an example section so I can cycle through
things."*

A taste decision asked in prose costs the human two minutes of imagining what
you mean, and returns an answer vague enough that you then over-interpret it.
The same decision shown as two or three real, different artifacts costs two
seconds per option and returns a pointed finger. Never ask in prose what a
variant could answer instead — that is the whole rule; everything below is
mechanism for doing it well.

## Reach for this when

- The decision has no objectively right answer — it is a matter of taste:
  a glyph, a layout, a default, a name, a colour, a wording, a sort order.
- You are about to write a question that starts "should it look like..." or
  "would you prefer...". That sentence is the signal to stop typing prose
  and start building.
- More than one reasonable answer exists and building each is cheap relative
  to guessing wrong and redoing it later.

Do not reach for this when the answer is already known. Run `determine-intent`
first — if the human already specified the answer, stated it as a standing
preference, or it is a known parameter recorded somewhere, building variants
to re-ask a settled question wastes the artifact and the human's attention on
both ends. Variants are for genuine, unresolved taste calls, not a ritual
performed before every decision.

## The four requirements

A variant set that fails any one of these has quietly turned back into the
prose question it was supposed to replace.

### 1. Genuinely different options, not variations of one

Three shades of the same layout is one option shown three times. Before
building, check: would all the options survive the same objection? If a
single complaint ("too dense," "too formal," "wrong scope") kills every
variant at once, they are not variants — they are one idea with cosmetic
knobs. Pick axes that actually diverge: not "spacing A/B/C" but "a table,"
"a stream," "a tree." If you cannot state what distinct bet each option is
making, you have not built variants yet.

### 2. Real artifacts, not descriptions

A paragraph describing a layout is the prose question this skill exists to
replace, just moved one level down. Build the thing — render it, run it,
generate the file — so the human looks at output, not at your description
of output. If producing a real artifact for every option is expensive, that
expense is information: either the decision does not warrant this many
options, or the seam that would make variation cheap does not exist yet
(see "Fake state, not medium" below).

### 3. Presented so the human can cycle

A page, a gallery, a numbered set, a `tab`-through picker — anything that
lets one glance land on one option and the next glance land on the next.
Sending four files across four separate messages is not cycling; the human
loses the option they saw three messages ago. Put the options where
attention can move linearly across all of them in one sitting.

### 4. Say what each option implies, not just what it looks like

Rejection happens on implication as often as on appearance — a name that
implies the wrong product scope, a layout that implies the wrong information
density, a default that implies a different failure mode is common. Label
each option with the one-line consequence it commits to, next to the
artifact itself: not "option 2: a tree view" but "option 2: a tree view —
implies nesting is the primary way people will navigate this, not search."
An artifact without its implication stated makes the human reconstruct the
implication themselves, which is exactly the inference cost this skill is
supposed to remove.

## One question per build

Vary one dimension per variant set. Cycling three dimensions at once — is
this about the glyph, the layout, or the density? — turns a picker into a
maze where no answer is clean, because a rejected option might have been
rejected for any of the three reasons. If a decision genuinely has two
independent axes, build two separate variant sets and let the human answer
them in sequence, not one set trying to carry both.

## Ship a working default

The human should be able to say nothing and still get something sane. A
variant set is for surfacing preference, not for forcing a decision nobody
has made yet — if the picker is ignored, the artifact still has to work.
Pick the default before showing the set, and make it whichever variant you
would ship if no one ever answered.

## Fake state, not medium — the general lesson

Jon asked, on a real decision, whether to mock a terminal UI in HTML first —
iterate on look and feel there, then build the real thing. The instinct
(build something to look at before committing) is right; the medium is
wrong.

**HTML lies about the medium.** A terminal is a fixed grid of monospace
cells: no subpixel positioning, no arbitrary fonts, no shadows, no rounded
corners, no smooth animation. An HTML mock locks in a look the terminal
cannot render, and the cuts a real build has to make land exactly on the
polish the mock was used to specify. The human picks an HTML variant, then
watches the thing they picked get worse with every constraint the terminal
imposes that HTML never had.

**The fix is not "less mocking," it's "mock the state, not the surface."**
Build the real thing — same renderer, same font, same colour depth, same
wrapping — and hand it throwaway, hardcoded fake state instead of a live
connection. This is proven, not theoretical: `--gallery` renders every lane
state against every glyph set with no supervisor connection at all. Point
the same pattern at a rail, a board, an API response shape, a log line — the
renderer is real, the data feeding it is invented.

This is also the cheaper path. The expensive parts of an app are usually the
plumbing — live data, network wiring, embedding in another process — not
rendering. A rail with six invented lane states is hours of work; an HTML
mock plus the real build afterward is both those hours *and* the mock's, and
still ends with the same cuts landing on the same polish.

**Invented state must still be honest state.** Fake data that only covers
the three rows that look good measures nothing but the happy path — a
variant that cannot render the rare or ugly case (empty, overflowing,
erroring, all-selected) is not a candidate, it is a demo. Enumerate the real
states before inventing fake instances of them, so the picker is choosing
between artifacts that will hold up, not artifacts staged to flatter one
option.

**The general rule:** prefer a real artifact in the real medium with fake
data over a faithful mock built in the wrong medium. The medium is what
determines what the human is actually approving; the data is the cheap part
to substitute.

## Design for cheap variation

This only pays off if adding a variant costs a line, not a rewrite. If a
variant turns out to be expensive to add or remove, that expense *is* the
finding — the seam sits in the wrong place, a variant should be data behind
an interface, not a forked code path. Report that instead of working around
it; a picker that is expensive to extend is quietly measuring how modular
the underlying code is every time it gets used.

## Presentation tooling

For terminal work specifically, two of Charm's own tools make a variant
lookable-at without attaching to anything live:

- **`freeze`** — renders a terminal's output to a static SVG or PNG. Good
  for a numbered gallery of options a human scans in one image viewer or
  one doc.
- **`vhs`** — runs a scripted terminal session and records it to a GIF.
  Good when the variant is a behavior over time (an animation, a
  transition, a multi-step flow) rather than a single frame.

Neither requires the live system the real artifact will eventually connect
to — which is what makes cycling through several possible.

## Record the choice and the reason

Once the human picks, write down which option and why in the same place the
decision lives (a commit message, a PR description, a doc) — not just the
selection, but the implication it confirmed or rejected. An unrecorded
choice gets re-litigated the next time someone hits a similar decision and
doesn't know it was already settled.

## What this is not

- **Not `ask-a-council`.** A council gets different positions from *agents*
  reviewing the same artifact, each through a different lens, to decide
  whether something holds up. This skill gets a decision from *the human*,
  by showing them artifacts to look at. Different subject (agents vs. the
  human), different question (does this hold up vs. which do you prefer).
- **Not `determine-intent`.** That skill runs first, and answers whether
  variants are even needed — it works out what the human already specified.
  If the answer to a decision is already a known parameter, `determine-intent`
  should catch that and this skill should not run at all. Only build
  variants for what is genuinely still open.
- **Not `devils-advocate`.** That skill attacks a conclusion already
  reached, before it is committed to. Variants precede a conclusion — they
  are how one gets reached in the first place. Once the human has picked
  from a variant set, `devils-advocate` can stress-test the pick; it does
  not replace building the set.
