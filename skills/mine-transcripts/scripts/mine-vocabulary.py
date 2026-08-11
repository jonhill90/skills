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


def mine(root: Path, pattern: str, ngram_max: int, radius: int, sample_cap: int):
    counts: dict[str, int] = defaultdict(int)
    files: dict[str, set] = defaultdict(set)
    contexts: dict[str, list] = defaultdict(list)
    snippets: dict[str, list] = defaultdict(list)

    for path in iter_files(root, pattern):
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
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

        passed = True
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'}: {name}")
            passed = passed and ok
        return passed


if __name__ == "__main__":
    sys.exit(main())
