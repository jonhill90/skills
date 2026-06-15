---
name: context7
description: Fetch up-to-date library documentation. Use when user asks about libraries, frameworks, or needs current API references/code examples.
---

Fetch current docs instead of relying on training data.

## Primary Method: MCP Tools

Context7 is configured via `.mcp.json` and provides MCP tools automatically:

**Available MCP Tools:**
- `mcp__context7__resolve-library-id` - Search for library by name
- `mcp__context7__query-docs` - Fetch documentation for a library

**Usage:**
```
Tool: mcp__context7__resolve-library-id
Parameters: { "libraryName": "react", "query": "hooks" }

Tool: mcp__context7__query-docs
Parameters: { "libraryId": "/websites/react_dev", "query": "useState hook" }
```

## Fallback: Scripts

If MCP tools are unavailable, use the script matching the local environment:

```bash
# Bash
./scripts/search.sh react hooks
./scripts/fetch-docs.sh /websites/react_dev "useState hook"

# Python
python3 ./scripts/search.py react hooks
python3 ./scripts/fetch-docs.py /websites/react_dev "useState hook"

# PowerShell
./scripts/search.ps1 react hooks
./scripts/fetch-docs.ps1 /websites/react_dev "useState hook"
```

## Setup (Optional)

For higher rate limits, add your Context7 API key to `.env`:

```bash
CONTEXT7_API_KEY=your-key-here
```

Get your key at: https://context7.com/dashboard

Works without API key but with lower rate limits.
