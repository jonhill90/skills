#!/usr/bin/env bash
# check_clean.sh -- refuses (exit 1) if the working tree has uncommitted
# changes; exits 0 if clean. Complete, tested (see
# tests/test_check_clean.sh) -- and, as shipped, never called by anything.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ -n "$(cd "$HERE" && git status --porcelain)" ]; then
  echo "check_clean: uncommitted changes present -- refusing" >&2
  exit 1
fi
echo "check_clean: tree is clean"
exit 0
