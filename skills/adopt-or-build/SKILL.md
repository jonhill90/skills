---
name: adopt-or-build
description: Decide, per component, whether to adopt an existing name, dependency, library, or tool or build it in-house, weighing blast radius over convenience. Use at the point a name or dependency is about to be chosen or recommended — before it is proposed, not after. Not for finding a technology's capability ceiling (research-the-limit), not the mechanism for genuinely different reviewer lenses (ask-a-council, which this skill may call), and not a substitute for attacking the chosen answer (devils-advocate, which this skill invokes as its final step).
---

# Adopt or Build

"Adopt X" is the wrong unit of decision. A codebase is not one choice, it
is a set of components with different blast radii, and the same dependency
that is safe to adopt at the edge can be the wrong call at the trust
boundary. Treat every adopt-or-build question as several smaller
questions, one per component, and answer each on its own evidence.

## Reach for this when

- A name, dependency, library, or tool is about to be proposed or chosen —
  for a component, a product name, a subsystem.
- The choice is not yet load-bearing: it can still change cheaply. Once it
  ships and other work depends on it, the cost of reversing goes up, so run
  this before that point, not after.
- More than one option exists (adopt a specific thing, adopt the pattern
  without the code, or build it) and nobody has yet checked what already
  exists under that name or in that space.

Do not reach for this to explore what a technology can do at its ceiling —
that is `research-the-limit`. Do not reach for it as the mechanism for
convening several genuinely different reviewer perspectives — that is
`ask-a-council`, and this skill may call it for a genuinely plural
question, but does not replace it. Do not reach for it to attack a
decision that has already been reasoned through — that is `devils-advocate`,
invoked at the end of this workflow, not duplicated inside it.

## Order of operations

Run these in order. Do not skip to the council or the recommendation before
the check and the classification are both done — that is the mistake this
skill exists to prevent.

### 1. Check availability and prior art, before recommending anything

A name or dependency proposed without evidence next to it is not a
proposal — it is a guess with a label. Before recommending anything, check:

- **Repo search** — `gh search repositories <name>` (and the same on
  npm/PyPI/crates as applicable). A name check that stops at "I don't
  recall one" is not a check.
- **Org and namespace** — does the name collide with an existing org,
  package, or product, even one that isn't famous?
- **Domain** — is the name already taken where it would need to live
  publicly?
- **The evidence itself, shown beside the candidate** — not "I checked and
  it's fine," but what the check returned: the search command run and what
  it found (or didn't).

This step is cheap and comes first for a reason: see step 4 below.

### 2. Classify each component by blast radius, not the system as a whole

For every component in scope, ask: **what breaks if this choice is
wrong?** Sort into one of three buckets — do not answer "adopt or build"
for the whole system at once.

| Blast radius | What it covers | Default |
|---|---|---|
| **Trust boundary** | Auth, the ledger, anything that can corrupt the record or grant access it shouldn't | Build, or adopt only with overwhelming evidence — a strong license, an active maintainer, a track record under load matching yours |
| **Replaceable leaf** | A component with a narrow contract and a clean swap path | Adopt freely — being wrong costs a rewrite of one leaf, not a system |
| **Design, not code** | The common case — a shape or contract worth reusing, but the implementation isn't trustworthy enough to depend on wholesale | Take the pattern, write your own implementation of it |

A single system usually has components in all three buckets. Naming a
whole product "we're adopting X" skips this classification and is the
error this step exists to catch.

### 3. Prefer a contract over vendoring code

When a candidate is thin — few stars, few maintainers, unclear support —
the choice is not "adopt or skip," it is "read or depend." Reading a
repository has zero supply-chain risk; importing it, even as a
dependency, has all of it. Study the shape it exposes (its public
methods, its lifecycle, the contract it implies) and reimplement that
shape rather than pulling in code you have not verified you can trust
long-term. This is the same move as bucket three above, applied to the
dependency question specifically.

### 4. Treat "no license" as disqualifying, not as a factor to weigh

An unlicensed repository grants no rights, regardless of star count,
activity, or how well it fits. This is not a judgment call to balance
against popularity — no license means study-only, full stop. Check the
license before weighing anything else about a candidate; a well-starred,
well-maintained, unlicensed repo is still study-only.

### 5. Run cheap deterministic checks before convening anyone

Before reaching for `ask-a-council` or any multi-agent review, run the
checks that a `grep`, a search, or a single command can already answer.
An expensive council built on a premise a two-line check would have
falsified wastes the council's cost and still gets the wrong answer if
every member shares that unexamined premise. Convene only once the cheap
checks are exhausted and what remains is a genuine judgment call —
usually the blast-radius classification in step 2, or a question where
the failure modes are plural in kind (see `ask-a-council`).

### 6. Attack the recommendation before it ships

Once a recommendation is reached — for a name, a component, or a
build-vs-adopt split — invoke `devils-advocate` on it as the final step,
before it is committed to. A recommendation that has not been attacked is
a first draft, not a decision. Do not build a second opposition pass here;
`devils-advocate` owns that mechanism.

## What this is not

- **Not `research-the-limit`.** That skill checks a primary source before
  asserting a technology's capability boundary — "can X do Y." This
  skill assumes the capability question is settled and chooses between
  existing options (or building) for a component that already has a job
  to do.
- **Not `ask-a-council`.** That skill is the mechanism for convening
  several reviewers with genuinely non-overlapping lenses. This skill may
  call it — the blast-radius classification or a genuinely contested
  component can be exactly the kind of plural question a council is for —
  but running a council is not this skill's job, and this skill does not
  restate how to assign lenses.
- **Not `devils-advocate`.** That skill attacks a chosen answer. This
  skill invokes it as the mandatory final step once a recommendation
  exists; it does not duplicate the attack itself, and a recommendation
  from this skill that skips that step is incomplete.

## Where this came from

Four adopt-or-build decisions run ad hoc in one session, each missing part
of this method:

- **`herdr`**, **`ScottRBK`'s `agent-shell` / eval-harness / forgetful**,
  **`CodexBar`**, and three separate orchestrators independently named
  **`loom`** — `loom` was proposed without noticing three existing agent
  orchestrators already carried the name, because no repo search ran
  before the proposal.
- **`keelson`** was applied to the product before anyone ran
  `gh search repositories` — which would have found `akapril/keelson`, a
  local-first AI workbench for Claude/Codex sessions, i.e. almost exactly
  the same product, before the name shipped anywhere.
- **`agent-shell`**, at 12 stars, taught the shape worth keeping: its
  `execute` / `stream` / `cancel` / `health_check` contract was worth
  studying. Depending on the repository itself was not — the contract
  survived, the dependency didn't.
- **`context-hub-plugin`** had no license and was seven months stale; it
  was correctly treated as study-only regardless of how well it fit.
- Both the **CodexBar** and **tmux-control-mode** recommendations survived
  only until someone actually attacked them — neither had been through a
  `devils-advocate` pass before being proposed.
- A four-agent council was overturned by a two-line `grep`, because every
  member of the council shared the same unexamined premise that the cheap
  check would have falsified before the council was convened.

Recorded in jonhill90/skills#202. The receipts above are a record of one
session's mistakes, not a validated general taxonomy — apply the method,
not the specific examples, to a new decision.
