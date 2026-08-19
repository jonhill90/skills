# Eval case

A fixture for checking that `mechanize` actually changes the answer, not
just restates whichever way the reader was already leaning. It is a test
case definition, not a scored run — no transcript, harness, or private
evaluation evidence is attached; that methodology lives outside this
repository.

## Scenario

A supervisor loop watches several worker lanes. Each tick, an agent reads
the last few lines of each pane's output and decides: "is this lane
stalled?"

Across the first ten ticks, the agent's reasoning is always the same
three-step check:
1. Has the pane's last line changed since the previous tick?
2. Is there a shell prompt with no running process?
3. Has more than N minutes passed since the last change?

Every tick reaches the same rule-based answer from the same three facts.
On tick eleven, a lane shows unchanged output, a shell prompt, and stale
timing — but the agent notices the prompt is inside a `git rebase -i`
editor waiting on human input, not a truly idle shell.

## Applying the test

**The test:** is "is this lane stalled" a function of the input? For ticks
1-10, yes — three checkable facts feed a fixed rule, and the smell already
names this: an answer a model re-derives identically every time it runs.
Mechanize the three-step check into a script that returns stalled /
not-stalled / unknown.

**The counter-test:** what new failure mode would the tool be blind to?
Tick eleven answers it directly — a shell prompt is not by itself evidence
of idleness; a rebase editor, a pager, or a confirmation prompt all produce
one. A tool built only from ticks 1-10 would misclassify tick eleven as
stalled and could trigger an unwanted action (e.g. a restart) against a
lane that is correctly waiting on a human.

## Expected verdict

- Mechanize the three-step detection (changed line, shell prompt, elapsed
  time) into a script — it is a pure function of visible pane state and
  was re-derived identically for ten straight ticks.
- Do **not** mechanize the final "is this lane actually stalled" call.
  Keep AI reading the tool's output specifically to catch the case the
  tool cannot enumerate: a shell prompt that means "waiting on a human,"
  not "idle." The tool narrows what AI has to look at each tick; it does
  not replace the judgement call.

A run of this skill against the scenario above should reach that same
split — mechanize the detection, keep AI on the interpretation — and
should name the rebase-editor case (or an equivalent one it invents) as
the reason the whole decision doesn't mechanize.
