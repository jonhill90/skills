# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> I'm about to make a change in this repo and don't know it at all. Give
> me a concise orientation: what is this, what language/stack does it
> actually use, and anything I should know before touching it.

## Setup

`fixture/` is a git repo whose `README.md` and actual manifest disagree:

- `README.md` describes "a Python data-processing service" with a
  `pip install -r requirements.txt` / `python main.py` setup.
- The repo's actual manifest is `Cargo.toml` (Rust), and the only source
  file is `src/main.rs`. `requirements.txt` and `main.py` — the two files
  the README's own setup instructions name — do not exist.

## The trap

The word "actually" in the prompt is doing real work: it is answerable by
reading `README.md` alone (fast, plausible, wrong) or by cross-checking it
against the manifest that is actually present (slower, correct).
`primer`'s own instructions name manifests and structure as required
inspection alongside documentation, not as a fallback for when
documentation is silent — this scenario tests whether that ordering
survives contact with a document that is not silent, just wrong.
