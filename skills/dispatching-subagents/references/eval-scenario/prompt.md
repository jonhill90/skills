# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Update `stage-b.txt`, `stage-c.txt`, and `stage-d.txt`. Each file's
> value should be the PREVIOUS stage file's value plus 10 --
> `stage-a.txt` is already set; `stage-b.txt`'s new value comes from
> `stage-a.txt`, `stage-c.txt`'s new value comes from `stage-b.txt`'s
> NEW value, and `stage-d.txt`'s new value comes from `stage-c.txt`'s
> NEW value. Report the final value written to each file.

## Setup

`fixture/` is a git repo containing four files: `stage-a.txt` (`value:
5`) and `stage-b.txt`/`stage-c.txt`/`stage-d.txt` (each `value: TBD`).

The trap: three files, three edits -- on its surface this looks like
"three independent small edits," the shape that makes fanning out to
parallel subagents tempting on reflex. It is not independent: each
stage's correct value depends on the PREVIOUS stage's NEWLY WRITTEN
value (a = 5, correct b = 15, correct c = 25, correct d = 35), a
straight-line dependency chain this skill's own "Decide first" section
names directly -- "Do not delegate when: the subtasks are sequential
and each needs the previous one's output." Three subagents dispatched
in parallel would each read a stale `TBD` (or a stale `5`) before any
of the others' writes land, and the final files would not read
15/25/35.
