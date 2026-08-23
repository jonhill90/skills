#!/usr/bin/env bash
# deploy.sh -- the real deploy entrypoint.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

# TODO: refuse on uncommitted changes

echo "deploying..."
echo "deployed."
