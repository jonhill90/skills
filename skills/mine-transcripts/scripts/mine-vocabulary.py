#!/usr/bin/env python3
"""Deterministic counting pass for the mine-transcripts skill.

Read-only: opens transcript files for reading and never writes, moves, or
deletes anything under the directory it is pointed at. Counts candidate
terms, measures how consistently each term's surrounding words repeat
(a proxy for "explained the same way every time"), flags common CLI tool
names as a likely false-positive class, redacts secret-shaped substrings,
and prints one inspectable JSON object to stdout.

This script does not decide whether a term names a procedure worth a
skill. That is judgement, done in the review step described in SKILL.md,
against this script's output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".log", ".jsonl", ".json"}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z-]{2,}")

# Deliberately small and generic — not tuned to any one person's transcripts.
STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "have", "from", "your",
    "you", "are", "was", "were", "will", "would", "should", "could",
    "then", "than", "them", "they", "their", "there", "here", "what",
    "when", "where", "which", "while", "about", "into", "onto", "over",
    "under", "again", "also", "just", "like", "make", "made", "need",
    "needs", "needed", "want", "wants", "wanted", "run", "runs", "running",
    "file", "files", "code", "line", "lines", "does", "done", "each",
    "some", "such", "only", "very", "much", "more", "most", "same", "one",
    "two", "now", "not", "all", "any", "can", "did", "get", "gets",
    "got", "has", "had", "its", "out", "see", "set", "use", "used",
    "uses", "using", "yes", "way", "still", "these", "those", "been",
    "being", "look", "looks", "looking", "check", "checks", "checking",
}

# Frequent because a *tool* is invoked, not because a decision is
# re-made. A prior, not a verdict — the review step can override it.
TOOL_TOKENS = {
    "git", "gh", "npm", "npx", "pip", "pytest", "python", "docker",
    "curl", "grep", "sed", "awk", "bash", "make", "node", "yarn",
    "brew", "ssh", "scp", "rsync", "tmux", "vim", "jq", "kubectl",
    "terraform", "cargo", "rustc", "java", "mvn", "gradle", "go",
    "unittest", "pyyaml", "argparse",
}

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gh[oesu]_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def iter_files(root: Path, pattern: str):
    for path in sorted(root.rglob(pattern)):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


def snippet_around(raw: str, start: int, end: int, pad: int = 50) -> str:
    lo = max(0, start - pad)
    hi = min(len(raw), end + pad)
    text = " ".join(raw[lo:hi].split())
    home = str(Path.home())
    if home and home in text:
        text = text.replace(home, "~")
    return redact(text)[:160]


def _turn_text_from_content(content) -> str:
    """Pull human-readable text out of a transcript message's `content`.

    `content` is either a plain string (typical for a user turn) or a list
    of content blocks (typical for an assistant turn). Only `text` and
    `thinking` blocks are prose; `tool_use` (a JSON call) and `tool_result`
    (often huge or binary) are structure, not vocabulary, and are skipped.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                parts.append(block.get("text", ""))
            elif block_type == "thinking":
                parts.append(block.get("thinking", ""))
        return "\n".join(p for p in parts if p)
    return ""


def _read_transcript_text(path: Path) -> str:
    """Read a file as mining input, extracting real turns from `.jsonl`.

    Session transcripts like Claude Code's are JSON-per-line, and most of
    that JSON is API request/response envelope (token counts, cache
    metadata, UUIDs) rather than anything anyone said. Tokenizing that
    envelope as prose drowns every real candidate in structural noise
    (jonhill90/skills#199) — every line that parses as JSON and has the
    shape of a transcript turn (`type` in user/assistant with a matching
    `message.role`) contributes only its extracted text/thinking content.
    A `.jsonl` file that is not transcript-shaped (plain text or logs that
    merely use the `.jsonl` suffix) falls back to being read as-is, one
    line at a time, so that existing non-transcript uses of this script
    are unaffected.
    """
    if path.suffix != ".jsonl":
        return path.read_text(encoding="utf-8", errors="ignore")

    lines = []
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                # Not JSON at all — a plain-text line in a `.jsonl`-named
                # file. Keep it verbatim rather than silently dropping it.
                lines.append(line)
                continue
            if not isinstance(record, dict):
                continue
            record_type = record.get("type")
            if record_type not in ("user", "assistant"):
                # Envelope/meta lines (file-history snapshots, session
                # markers, ...) — structure, not vocabulary. Skip.
                continue
            message = record.get("message")
            if not isinstance(message, dict) or message.get("role") not in (
                "user",
                "assistant",
            ):
                continue
            turn_text = _turn_text_from_content(message.get("content"))
            if turn_text.strip():
                lines.append(turn_text)
    return "\n".join(lines)


def mine(root: Path, pattern: str, ngram_max: int, radius: int, sample_cap: int):
    counts: dict[str, int] = defaultdict(int)
    files: dict[str, set] = defaultdict(set)
    contexts: dict[str, list] = defaultdict(list)
    snippets: dict[str, list] = defaultdict(list)

    for path in iter_files(root, pattern):
        try:
            raw = _read_transcript_text(path)
        except OSError:
            continue
        tokens = list(WORD_RE.finditer(raw))
        lowered = [m.group(0).lower() for m in tokens]

        for n in range(1, ngram_max + 1):
            for i in range(len(tokens) - n + 1):
                words = lowered[i:i + n]
                if any(w in STOPWORDS for w in words):
                    continue
                term = " ".join(words)
                counts[term] += 1
                files[term].add(str(path))

                ctx_lo = max(0, i - radius)
                ctx_hi = min(len(lowered), i + n + radius)
                ctx = set(lowered[ctx_lo:i]) | set(lowered[i + n:ctx_hi])
                ctx -= STOPWORDS
                if len(contexts[term]) < sample_cap:
                    contexts[term].append(ctx)

                if len(snippets[term]) < 3:
                    start = tokens[i].start()
                    end = tokens[i + n - 1].end()
                    snippets[term].append(snippet_around(raw, start, end))

    results = []
    for term, count in counts.items():
        sampled = contexts[term]
        pairs = 0
        total = 0.0
        for a in range(len(sampled)):
            for b in range(a + 1, len(sampled)):
                union = sampled[a] | sampled[b]
                if not union:
                    continue
                total += len(sampled[a] & sampled[b]) / len(union)
                pairs += 1
        consistency = round(total / pairs, 3) if pairs else 0.0
        results.append({
            "term": term,
            "count": count,
            "distinct_files": len(files[term]),
            "consistency": consistency,
            "likely_tool": any(w in TOOL_TOKENS for w in term.split()),
            "sample_snippets": snippets[term],
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path,
                         help="transcript directory to scan (read-only)")
    parser.add_argument("--glob", default="*",
                         help="glob applied under root (default: *, recursive)")
    parser.add_argument("--ngram-max", type=int, default=2,
                         help="largest term size in words (default: 2)")
    parser.add_argument("--radius", type=int, default=6,
                         help="context window size in words each side (default: 6)")
    parser.add_argument("--min-count", type=int, default=3)
    parser.add_argument("--min-files", type=int, default=2)
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--include-tools", action="store_true",
                         help="keep terms flagged likely_tool in the ranked output")
    parser.add_argument("--self-test", action="store_true",
                         help="run the built-in fixture check and exit; ignores root")
    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    if args.root is None:
        parser.error("root is required unless --self-test is given")

    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    results = mine(root, args.glob, args.ngram_max, args.radius, sample_cap=25)
    results = [r for r in results if r["count"] >= args.min_count
               and r["distinct_files"] >= args.min_files]
    if not args.include_tools:
        results = [r for r in results if not r["likely_tool"]]
    results.sort(key=lambda r: (r["count"] * (1 + r["consistency"])), reverse=True)
    results = results[:args.top]

    print(json.dumps({
        "root": str(root),
        "read_only": True,
        "candidate_count": len(results),
        "candidates": results,
    }, indent=2))
    return 0


def self_test() -> bool:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "a.md").write_text(
            "We should sanity-check the plan before merging.\n"
            "Always sanity-check the diagnosis with a second reviewer.\n"
            "Before acting, sanity-check the rationale one more time.\n",
            encoding="utf-8",
        )
        (root / "b.md").write_text(
            "Run pytest to check the suite. Run pytest again after the fix.\n"
            "pytest is fast so run pytest often.\n",
            encoding="utf-8",
        )
        (root / "c.md").write_text(
            "the the file file run run about about into into\n"
            "token: ghp_ABCDEFGHIJ1234567890abcdEFGH was pasted here by mistake\n",
            encoding="utf-8",
        )

        # A Claude-Code-shaped transcript: mostly API envelope (tokens,
        # cache, uuids), with a small amount of real turn text repeating a
        # decision — the exact shape that swamped every candidate with
        # noise before jonhill90/skills#199.
        transcript_lines = []
        for i in range(4):
            transcript_lines.append(json.dumps({
                "type": "user",
                "message": {"role": "user", "content": "sanity-check the plan before merging"},
                "uuid": f"turn-{i}",
                "usage": {"input_tokens": 111, "cache_read_input_tokens": 222},
            }))
            transcript_lines.append(json.dumps({
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "sanity-check the diagnosis first"},
                        {"type": "tool_use", "name": "Bash", "input": {"command": "pytest"}},
                    ],
                },
                "usage": {"cache_creation_input_tokens": 333, "ephemeral_5m_input_tokens": 0},
            }))
            transcript_lines.append(json.dumps({
                "type": "system",
                "subtype": "file-history-snapshot",
                "isSnapshotUpdate": False,
            }))
        (root / "d.jsonl").write_text("\n".join(transcript_lines) + "\n", encoding="utf-8")

        results = mine(root, "*", ngram_max=2, radius=6, sample_cap=25)
        by_term = {r["term"]: r for r in results}

        checks = []

        checks.append(("sanity-check counted", "sanity-check" in by_term))
        if "sanity-check" in by_term:
            checks.append((
                "sanity-check has high consistency",
                by_term["sanity-check"]["consistency"] >= 0.2,
            ))
            checks.append((
                "sanity-check spans multiple files or repeats",
                by_term["sanity-check"]["count"] >= 3,
            ))

        checks.append(("pytest flagged as a likely tool", by_term.get("pytest", {}).get("likely_tool") is True))
        checks.append(("stopwords excluded", "the" not in by_term and "run" not in by_term))

        dumped = json.dumps(results)
        checks.append(("secret redacted", "ghp_ABCDEFGHIJ" not in dumped))
        checks.append(("redaction marker present", "[REDACTED]" in dumped))

        # jsonl transcript extraction (jonhill90/skills#199): envelope
        # fields must not appear as candidates, and the real repeated turn
        # text must be counted and ranked above noise-level consistency.
        checks.append(("jsonl envelope keys excluded", "usage" not in by_term and "uuid" not in by_term))
        checks.append(("jsonl cache/token noise excluded", "tokens" not in by_term and "cache" not in by_term))
        checks.append(("jsonl real turn text counted", "sanity-check" in by_term))
        if "sanity-check" in by_term:
            checks.append((
                "jsonl turn text has real consistency, not noise",
                by_term["sanity-check"]["consistency"] > 0,
            ))

        passed = True
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'}: {name}")
            passed = passed and ok
        return passed


if __name__ == "__main__":
    sys.exit(main())
