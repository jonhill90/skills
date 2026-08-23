# Eval scenario: tick classifier (counting measurement)

Given to both arms verbatim, identical except for the skill-loading
instruction at the bottom. Modeled on `progressive-disclosure`'s
`eval-scenario/` (skills#265/#229): a real quantity the harness counts
mechanically, not a scored write-up.

---

You have access to a local directory: `fixture/ticks/`. It contains 30
files, `tick-01.json` through `tick-30.json`, one JSON object per file:
`{"tick_id": N, "error_rate": <float>, "latency_ms": <int>}`.

A supervisor has already told you, by example, how the first four ticks
were classified `healthy` or `unhealthy`:

- `tick-01.json` (`error_rate=0.01, latency_ms=120`) → **healthy**
- `tick-02.json` (`error_rate=0.02, latency_ms=180`) → **healthy**
- `tick-03.json` (`error_rate=0.08, latency_ms=150`) → **unhealthy**
- `tick-04.json` (`error_rate=0.01, latency_ms=250`) → **unhealthy**

**Task:** Classify every remaining tick, `tick-05.json` through
`tick-30.json` (26 more), the same way, using whatever rule the four
worked examples imply. Write your verdicts to `results.csv` in the
current directory, one line per tick: `tick_id,verdict` (verdict is
exactly `healthy` or `unhealthy`), for all 30 ticks (the 4 worked
examples plus the 26 you classify).

As your last action, write `manifest.json` to the current directory:

```
{
  "script_written": <true|false>,
  "script_path": "<path, or null>",
  "actions_log": ["<one entry per tool call you made after reading this
    prompt, in order, e.g. 'read tick-05.json', 'wrote classify.py',
    'ran classify.py', 'wrote results.csv'>"],
  "ticks_processed": <int, should be 30>
}
```

`actions_log` is not a summary of your approach — it is a literal,
ordered log of every tool call (file read, file write, command run) you
actually made while doing this task. Do not omit any.

---

**Arm A only** (mechanize loaded): before starting, read
`skills/mechanize/SKILL.md` in this repository and apply its test to
this task before deciding how to do the classification.

**Arm B only**: no additional instruction. Solve it however seems
natural.
