#!/usr/bin/env bash
# Proves check_clean.sh's own logic is correct, in isolation -- exactly
# the shape this skill's own incident names (acp_transport.py: "302
# lines, ~15 test classes, requested 23 times over 9 days -- 0 lanes
# ever used it"). Passing this test proves nothing about whether
# anything in this repo actually CALLS the script it tests -- and
# nothing does, as shipped.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"

echo dirty >> "$HERE/README.md"
if bash "$HERE/check_clean.sh" >/dev/null 2>&1; then
  echo "FAIL: check_clean.sh should have refused on a dirty tree" >&2
  git -C "$HERE" checkout -q -- README.md
  exit 1
fi
git -C "$HERE" checkout -q -- README.md

if ! bash "$HERE/check_clean.sh" >/dev/null 2>&1; then
  echo "FAIL: check_clean.sh should pass on a clean tree" >&2
  exit 1
fi

echo "ok: check_clean.sh's own logic is correct in isolation"
