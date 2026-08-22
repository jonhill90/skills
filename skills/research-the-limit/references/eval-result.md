# Eval result

Recorded 2026-08-22 as a backfill: this skill was the very first one
evaluated by the keep/improve/rename/drop harness itself, in the pull
request that built the harness (agent-evals#21). That evidence is not published here — plain-text provenance only, per this repository's own
Scope section. This entry predates jonhill90/skills having its own
structured eval-status record (docs/eval-status.json) and is added now
so the record covers everything actually run, not just what ran after
the record existed.

## Verdict: improve

## What was measured

A fixture where `report.sh` emits `sqlite3`'s default (non-JSON) output
and the task asks for JSON with "no new script or dependency" — the trap
being that `sqlite3` has had a native `-json` flag since 2020, so
"sqlite3 can't do JSON" is a plausible-sounding, false capability claim.

Three independent live runs against Opus 5, same scenario, same fixture,
stash cleanly restored after each:

- Run 1 (scored under an earlier, pre-fix verdict-logic pass in the same
  PR — not the corrected decision table below): both arms solved it, with
  the skill using less than half the tokens/turns of the run without it.
- Run 2: both arms solved it; `checked_source` (a primary-source read,
  from tool calls) was true only with the skill; tokens 168,015 vs.
  273,365 without (1.6x), turns 7 vs. 8.
- Run 3: both arms solved it again; `checked_source` true only with the
  skill again; but this time WITH the skill cost more — tokens 431,260
  vs. 233,827 (1.8x), turns 16 vs. 8 — the opposite direction from run 1.

## Why "improve," not "keep"

The outcome axis was a wash across all three runs: Opus 5 already knew
`sqlite3 -json` and solved the fixture correctly with or without the
skill installed every time. The one signal that consistently tracked
skill presence was `checked_source` (true only when the skill was
installed, in both runs where it was measured, never a false positive)
— real evidence the skill changes *how* the answer is reached, not
whether it's reached. Token/turn cost swung in both directions across
runs with no consistent sign, which the harness's own ×2/×3-before-
trusting-a-verdict bar reads as noise, not a directional cost claim
either way.

## What is not evidenced

The recorded runs used only `claude` (Opus 5) — no second CLI or model
family, so a model-independent read of this skill's effect is still
open.
