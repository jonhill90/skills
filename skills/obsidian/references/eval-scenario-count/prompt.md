# Eval scenario: add a checklist item without losing the note (counting measurement)

Given to both arms verbatim, identical except for the skill-loading
instruction at the bottom. Modeled on `progressive-disclosure`'s
`eval-scenario/` (skills#265/#229) and `mechanize`'s `eval-scenario-count/`
(skills#266/#267/#268).

`obsidian` on your `PATH` is a fixture stub for this exercise, not the
real Obsidian CLI, and `fixture/vault/` is a plain directory standing in
for a vault — no Obsidian app needs to be running. Use the `obsidian`
command exactly as you would the real CLI (`obsidian <command>
key=value ...`).

---

You have access to a local directory: `fixture/vault/`. It contains one
note, `daily-log.md`, with existing content already in it.

**Task:** Add a new checklist item, `- [ ] Follow up with Peter`, to
`daily-log.md`, **without losing anything that is already in the note.**

As your last action, write `manifest.json` to the current directory:

```
{
  "actions_log": ["<one entry per obsidian/tool call you made after reading
    this prompt, in order, e.g. 'obsidian read file=daily-log.md',
    'obsidian append file=daily-log.md content=...'>"]
}
```

`actions_log` is a literal, ordered log of every tool call you actually
made while doing this task. Do not omit any.

---

**Arm A only** (obsidian loaded): before starting, read
`skills/obsidian/SKILL.md` in this repository and apply it to this task.

**Arm B only**: no additional instruction. Solve it however seems natural.
