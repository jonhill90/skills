---
name: ask-a-council
description: Convene several harnesses or models against one question, each doing a distinct job it can fail at — different evidence, a different objective, or a withheld conclusion — before an artifact becomes load-bearing and being wrong is expensive. Diversity comes from what each reviewer is given, never from a character it plays. Use when the failure modes genuinely differ in kind — a single reviewer's prompt would only catch what its own lens looks for. Not for a question a cheap deterministic check settles (run the check first); not for one reviewer's prompt (sanity-check owns that); not for dispatch mechanics or isolation boundaries (dispatching-subagents owns those); not for trusting a verdict already returned (verify-the-instrument owns that).
---

# Ask a Council

A council is several harnesses or models given *different jobs* against the
same artifact, not one question asked several times and not one question
asked to several characters. Four reviewers given the same prompt buy
agreement — four votes on one read. Four reviewers each assigned a
character but shown the same material buy tone — four styles of writing
the same read. Four reviewers each given different evidence, a different
objective, or no visibility into each other's conclusion buy coverage —
four reads that fail in different places. The value is in what differs
between them, not in the count and not in the costume.

## The proof, in one line

A measured run against `watchdog.sh` on 2026-08-11 (jonhill90/skills#147)
gave four reviewers — three models, four harnesses — one lens each:
mechanism, legitimacy, portability, legibility. Every lens found something
none of the others found. The single highest-value finding — a failed `gh`
call counted as zero work, so the watchdog logged "nothing actionable"
while eleven items sat open — came from the **legibility** lens, not from
either reviewer hunting bugs. Four bug-hunters would have missed it. Keep
that sentence in mind when a council starts to feel like four copies of the
same review: it means the lenses collapsed, not that the council worked
extra hard.

## Check the frame before convening (RULE B2)

A council prices options within a frame; it does not audit the frame. Run
whatever cheap, deterministic check would settle a shared premise — a
`grep`, a status command, a file read — before spending four reviewers'
worth of budget on it. A four-agent council was once overturned by a
two-line `grep` because every member shared an unexamined premise none of
them was assigned to question. If a command can settle it, run the
command; convene the council for what is left after that.

## Reach for this when

- Being wrong is expensive — the artifact is about to be promoted, merged,
  shipped, or relied on by something else.
- The artifact is about to become **load-bearing**: other work will build
  on it, or it becomes harder to unwind the longer it stands.
- The candidate failure modes are **genuinely different in kind** — a
  correctness bug, a legitimacy question, a portability constraint, and a
  legibility gap are not variations on one theme, and no single reviewer
  prompt covers all of them at once.

Do not reach for this when a command settles the question — run the
command (see RULE B2 above). Do not reach for it because one reviewer's
answer felt uncomfortable; that is a second opinion, and `sanity-check`
already owns building that single prompt well. A council is for when the
*kind* of question is plural, not when one answer needs a tiebreaker.

## Diversity does not come from personas

Assigning a reviewer a character — a skeptic, an optimist, a devil's
advocate persona — changes how the output reads, not what it was checked
against. Two reviewers given the same material and told to play different
roles will produce differently-toned agreement, not independent findings,
because both are reasoning from the same premises. That is worse than
running one reviewer: it produces the *appearance* of a second opinion,
and an appearance of verification that was never earned is more dangerous
than an honest absence of one, because it reassures.

**The incident that forced this:** an agent was asked whether Jon wanted a
live terminal. It took one quote about *chat threads* being live,
generalised it to *terminal rendering* — a different subject — invented a
parameter he never stated (`survives-a-web-frontend`), and reported the
result to him as derived from his own words. The reasoning that produced
it was internally consistent; nothing about it looked wrong from the
inside. A reviewer re-reading that reasoning would not have caught it,
because the reviewer inherits the same invented premise the first agent
did. What caught it was a second agent deriving independently from Jon's
own corpus instead of from the first agent's summary — `mine_prompts.py
--typed-only --grep 'web frontend'` returned zero hits across 1,968 typed
turns, and `--grep 'survives'` matched only a worktree path. **It caught
the fabrication because it read different evidence, not because it had a
different personality.** See the eval case below to run this incident
against a proposed council design directly.

Ranked cheapest to strongest, this is what diversity of *reasoning* — as
opposed to diversity of *tone* — actually costs:

| Mechanism | What it does | Cost |
|---|---|---|
| (a) Withhold the conclusion | Each reviewer derives independently, before seeing any other reviewer's answer; compare only after. | Free — no extra dispatch, just discipline about ordering. |
| (b) Different source material | One reviewer reads code, one reads transcripts, one reads external prior art. They cannot echo each other because they have not seen the same thing. | One dispatch per material source. |
| (c) Opposing objectives | Not "be skeptical" — a job: "find the case against." This is precisely why `devils-advocate` works as a lens. | One dispatch with a stated adversarial objective. |
| (d) A different model | Genuinely uncorrelated failure modes — a different model fails differently even given the identical lens. | Highest — needs a second harness or provider with quota. **Currently blocked**: codex is at 100% weekly usage with zero credits, copilot at 97.1%. Record this as available in principle and unavailable in practice, so it is not silently forgotten when quota returns. |

Personas do not appear in that table. Dropping persona assignment in favor
of evidence-partitioning ((a)/(b)) and job-assignment ((c), and (d) when
available) is the change this skill makes.

## The positive case: evidence-partitioning already worked here

Earlier councils in this estate did produce genuine disagreement — a
council on 2026-08-16 assigned two agents opposite sides of a
build-vs-adopt question and they disagreed on nearly every fact, forcing
verification that corrected the record (jonhill90/skills#192, and see
`devils-advocate`'s "Where this came from"). The ScottRBK review similarly
had three agents reach opposed conclusions. In both cases the agents were
given **different questions and different material**, not different
characters. That is mechanisms (b) and (c) above, even in runs that were
described at the time as giving reviewers personas — the part of the setup
that actually produced disagreement was never the character, it was what
each agent was pointed at.

## Assign lenses — the core mechanic

A lens is a job a reviewer is given — an evidence source, an objective, or
both — not a role name. Two rules make a lens valid:

1. **Non-overlapping.** No two reviewers' lenses can produce the same
   finding by different wording. If two lenses would flag the same defect,
   merge them — a council with overlapping lenses is bug-hunting with
   extra steps, dressed as coverage.
2. **A real "no" is reachable.** Each lens must be able to return a
   negative verdict that the others cannot. If a lens can only ever come
   back "looks fine," it is not a lens, it is a formality.

Starting set, drawn from the measured run above — adapt the wording to the
artifact, but keep the questions this shaped:

| Lens | The question it answers | A real "no" looks like |
|---|---|---|
| Mechanism | Does this actually do what it claims, mechanically, in the environment it will run in? | It fails silently under cron, redirection, or a missing dependency the happy path never hits. |
| Legitimacy | Should this exist at all, in this form, right now? | Hold off — there's no escalation path, or the premise is wrong. |
| Portability | Does this violate a constraint of where it's about to live — one harness, one OS, one repo's boundaries? | It only works on the author's machine, or belongs in a different repository. |
| Legibility | Would a human watching the healthy path actually see it fail? | It logs success while doing nothing, or the failure is real but invisible until someone reads the wrong log line closely. |
| Cost | Is what this costs to run, maintain, or trust worth what it buys? | The maintenance burden or blast radius outweighs the value, even if it works. |

Five is a starting point, not a quota — convene only the lenses the
artifact actually has failure surface for. A council of two well-chosen
lenses beats five where three are padding.

## Harness and model diversity is a deliberate variable

Two reviewers on the same model are one reviewer with two prompts, not two
reviewers. Diversity of harness and model is mechanism (d) above — different
models fail differently even given the same lens, and a shared model family
quietly halves the council's actual coverage while still reading as four
independent opinions.

Before convening, record for each reviewer: the harness and the underlying
model. After the council reports, state plainly whether any two reviewers
shared a model family. The measured run this skill is built on failed this
itself — Copilot and the Claude worker ran on the same model family — and
that fact belongs in the report next to the findings, not smoothed over
because the run still produced value. Say it happened; do not claim
diversity you did not get.

## Reconciliation — disagreement is the finding

When two lenses disagree, do not average their verdicts and do not add a
fifth reviewer to break the tie. Two lenses reaching different conclusions
from different angles is itself information about the artifact — usually
that it is fine along one axis and not along another. Record:

- What each reviewer concluded, in its own terms.
- Which lens each verdict came from — a portability "no" and a mechanism
  "yes" are not a contradiction, they are two true things about different
  parts of the artifact.
- Whether the disagreement is resolvable by evidence (one reviewer was
  simply wrong about a fact — check it) or is a genuine tradeoff no single
  answer closes (report it as open, do not force a verdict).

A council that reconciles every disagreement into a single answer has
thrown away the reason it cost four times as much as one reviewer.

## Reading the result

Once the council reports, the rules for trusting any one finding are
`sanity-check`'s, not restated here: a finding without evidence is a lead,
not a fact; check the instrument before believing an empty review means
nothing was wrong rather than that the reviewer never ran; and see
`sanity-check`'s "Read the result honestly" section before treating
agreement across lenses as verification — it means the artifact survived
those particular questions, nothing broader. Before acting on the
council's collective verdict, `verify-the-instrument` governs the same way
it would for a single check: confirm each reviewer that reported "nothing
found" actually had something to look at.

## The unattended cost

A council is not a background task you start and walk away from. In the
measured run, two of four reviewers stalled on interactive approval
prompts — one for 23 minutes — and a human had to clear them before the
run could finish. A harness that blocks on a permission dialog turns "ask
four reviewers" into "ask four reviewers and then babysit two of them."

Before convening a council:

- Confirm each harness can run its review non-interactively, or budget a
  human to clear prompts during the run — that time is part of the cost of
  the council, not a rounding error.
- Do not schedule a council unattended (overnight, on a cron, while
  stepping away) unless every reviewer in it has been confirmed to run
  without a human present.
- Report the actual wall-clock cost, including any stall time, alongside
  the findings — a council that took four hours because of approval
  prompts is a more expensive tool than one that took twenty minutes, even
  if the findings are identical.

## Eval case: the fabrication incident

This is the acceptance test for this skill's mechanism. Run it against any
proposed council design before trusting that design:

**Setup.** An agent is asked whether Jon wanted a live terminal. It reads
one quote about chat threads being live, generalises it to terminal
rendering, invents a parameter (`survives-a-web-frontend`), and writes up
a confident, internally-consistent conclusion attributing the parameter to
Jon's own words.

**A persona-based council fails this case.** Give four reviewers — a
skeptic, an optimist, a pragmatist, a completeness-checker — the first
agent's write-up and ask each to review it in character. All four inherit
the invented premise, because none of them was asked to check it against
anything outside the write-up; they can only disagree about tone and
emphasis. This council reports "looks fine," or at most a mild style
objection. **That is a pass on a fabricated conclusion.**

**An evidence-partitioned council catches this case.** Assign one reviewer
mechanism (a): derive an answer to the same underlying question
independently from Jon's own corpus, without reading the first agent's
write-up first. That reviewer runs `mine_prompts.py --typed-only --grep
'web frontend'` and gets zero hits across 1,968 typed turns; `--grep
'survives'` matches only a worktree path. The independent derivation
disagrees with the first agent's write-up outright — not on tone, on the
premise. **That is a catch, and it is mechanism (a) plus (b) together:
withhold the conclusion, and use source material (the corpus) the first
agent's write-up is not.**

A council design that would pass the persona version of this case and
would not assemble the evidence-partitioned version of it is not ready to
convene on anything load-bearing — fix the design, not the incident.

## What this is not

- **Not persona or character assignment.** A council's reviewers differ in
  evidence, objective, harness, or model — never in the personality they
  are asked to perform. See "Diversity does not come from personas" above.
- **Not dispatch mechanics.** How to actually launch and isolate each
  reviewer, what model tier each worker runs on, and when delegation is
  warranted at all belong to `dispatching-subagents`. This skill decides
  *that* several different jobs should be assigned and *what* those jobs
  are; it does not decide *how* each is sent.
- **Not a single reviewer's prompt.** Building one reviewer's prompt — the
  lens, the evidence requirements, permission to return empty-handed — is
  `sanity-check`'s eight properties, applied once per lens here. This
  skill assigns the lens; `sanity-check` builds the prompt that carries it.
- **Not trusting the verdict.** Once the council has reported, deciding
  whether to believe a clean result or a fix it endorsed is
  `verify-the-instrument`'s job, applied to the council as the instrument.
- **Not a harness-specific command.** No dispatch syntax appears here on
  purpose — it differs per harness and changes often. Use whatever
  mechanism `dispatching-subagents` resolves to for the current harness.

## Where this came from

The lens set, the diversity failure, and the unattended-cost figures above
are a single measured run, not a general claim: `watchdog.sh`, four
reviewers, three models, 2026-08-11, recorded in jonhill90/skills#147. This
skill has been exercised once on that artifact. The persona-versus-evidence
rewrite above comes from a separate, later incident — the fabricated
`survives-a-web-frontend` parameter, independently re-verified with
`mine_prompts.py` before being filed as jonhill90/skills#206 — and from
re-reading the ScottRBK and build-vs-adopt (jonhill90/skills#192) councils
against that incident, which showed their genuine disagreements had always
come from differing evidence and objectives, not from differing personas.
Treat the lens table as a strong starting point proven on one artifact and
the eval case above as the acceptance bar for any future change to this
skill's diversity mechanism, not as a validated general taxonomy.
