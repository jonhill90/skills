#!/bin/bash
# PostToolUse (Edit|Write) hook: validates YAML frontmatter in skill and agent files.
# Only checks files matching skills/*/SKILL.md or agents/*.md.
# Non-blocking: exits 0 with systemMessage warnings on issues found.
# Soft-requires jq — degrades silently if missing.

set -euo pipefail

# Guard: jq required
command -v jq >/dev/null 2>&1 || exit 0

# Read stdin JSON (hook input)
INPUT=$(cat)

# Guard: empty input
[ -z "$INPUT" ] && exit 0

# Extract file path from tool_input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Guard: missing file path
[ -z "$FILE_PATH" ] && exit 0

# Determine what kind of file this is
IS_SKILL=false
IS_AGENT=false

if echo "$FILE_PATH" | grep -qE '(^|/)skills/[^/]+/SKILL\.md$'; then
    IS_SKILL=true
elif echo "$FILE_PATH" | grep -qE '(^|/)agents/[^/]+\.md$'; then
    IS_AGENT=true
fi

# Exit silently for non-skill, non-agent files
if [ "$IS_SKILL" = false ] && [ "$IS_AGENT" = false ]; then
    exit 0
fi

# Guard: file must exist
[ -f "$FILE_PATH" ] || exit 0

# Count --- markers to verify frontmatter is properly delimited
MARKER_COUNT=$(grep -c '^---$' "$FILE_PATH" || true)

# Extract frontmatter (content between first pair of --- markers)
FRONTMATTER=$(awk '/^---$/{if(n++)exit;next}n' "$FILE_PATH")

# Collect warnings
WARNINGS=""

if [ "$MARKER_COUNT" -lt 2 ]; then
    WARNINGS="Missing or unclosed YAML frontmatter (need opening and closing --- markers)\n"
elif [ -z "$FRONTMATTER" ]; then
    WARNINGS="Empty YAML frontmatter (no fields between --- markers)\n"
else
    if [ "$IS_SKILL" = true ]; then
        # Skills require: name, description
        if ! echo "$FRONTMATTER" | grep -qE '^name:'; then
            WARNINGS="${WARNINGS}Missing required field: name\n"
        fi
        if ! echo "$FRONTMATTER" | grep -qE '^description:'; then
            WARNINGS="${WARNINGS}Missing required field: description\n"
        fi
    fi

    if [ "$IS_AGENT" = true ]; then
        # Agents require: name, description
        if ! echo "$FRONTMATTER" | grep -qE '^name:'; then
            WARNINGS="${WARNINGS}Missing required field: name\n"
        fi
        if ! echo "$FRONTMATTER" | grep -qE '^description:'; then
            WARNINGS="${WARNINGS}Missing required field: description\n"
        fi

        # Check for comma-separated strings in array fields (common mistake)
        for FIELD in tools disallowedTools skills; do
            VALUE=$(echo "$FRONTMATTER" | grep -E "^${FIELD}:" | sed "s/^${FIELD}:[[:space:]]*//" || true)
            if [ -n "$VALUE" ] && echo "$VALUE" | grep -qE ','; then
                WARNINGS="${WARNINGS}Field '${FIELD}' appears to be a comma-separated string — must be a YAML array\n"
            fi
        done
    fi
fi

# Output warning if any issues found
if [ -n "$WARNINGS" ]; then
    FILE_TYPE="skill"
    [ "$IS_AGENT" = true ] && FILE_TYPE="agent"
    # Use printf to expand \n, then pass to jq
    MESSAGE=$(printf "Frontmatter issue in %s file %s:\n%b" "$FILE_TYPE" "$FILE_PATH" "$WARNINGS")
    echo "$MESSAGE" | jq -Rs '{ systemMessage: . }'
fi

exit 0
