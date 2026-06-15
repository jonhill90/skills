#!/bin/bash
# Fetch documentation from Context7

if [ $# -lt 2 ]; then
    echo "Usage: fetch-docs.sh <library-id> <query>" >&2
    exit 1
fi

LIBRARY_ID="$1"
QUERY="$2"

# Load API key from the environment or common project-local files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
API_KEY="${CONTEXT7_API_KEY:-}"
for ENV_FILE in "$REPO_ROOT/.env" "$REPO_ROOT/.claude/.env"; do
    if [ -z "$API_KEY" ] && [ -n "$REPO_ROOT" ] && [ -f "$ENV_FILE" ]; then
        API_KEY=$(grep "^CONTEXT7_API_KEY=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'" || true)
    fi
done

# URL encode parameters
ENCODED_LIB=$(printf %s "$LIBRARY_ID" | jq -sRr @uri)
ENCODED_QUERY=$(printf %s "$QUERY" | jq -sRr @uri)
URL="https://context7.com/api/v2/context?libraryId=${ENCODED_LIB}&query=${ENCODED_QUERY}"

# Make request and display
if [ -n "$API_KEY" ]; then
    curl -s -H "Authorization: Bearer $API_KEY" "$URL"
else
    curl -s "$URL"
fi
