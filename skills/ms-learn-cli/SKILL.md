---
name: ms-learn-cli
description: Query Microsoft Learn through the repository's standalone Go CLI. Use when official Microsoft documentation or code samples are needed and Microsoft Learn MCP tools are unavailable or a scriptable local client is preferred.
---

Fetch current Microsoft docs instead of relying on training data.

## Primary Method: MCP Tools

Microsoft Learn is configured via `.mcp.json` and provides MCP tools automatically:

**Available MCP Tools:**
- `mcp__microsoft-learn__microsoft_docs_search` - Find docs (concepts, tutorials, config, limits)
- `mcp__microsoft-learn__microsoft_docs_fetch` - Get full page content
- `mcp__microsoft-learn__microsoft_code_sample_search` - Find official code samples

**Usage:**
```
Tool: mcp__microsoft-learn__microsoft_docs_search
Parameters: { "query": "Azure Functions Python v2 programming model" }

Tool: mcp__microsoft-learn__microsoft_docs_fetch
Parameters: { "url": "https://learn.microsoft.com/..." }

Tool: mcp__microsoft-learn__microsoft_code_sample_search
Parameters: { "query": "Cosmos DB", "language": "csharp" }
```

## Fallback: Go CLI

If MCP tools are unavailable, use the `mslearn` binary in `tools/mslearn/`:

```bash
# Build (one-time)
cd tools/mslearn && make build

# Search docs
./tools/mslearn/mslearn search --query "Azure Functions Python v2"

# Fetch full page
./tools/mslearn/mslearn fetch --url "https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview"

# Search code samples
./tools/mslearn/mslearn samples --query "Cosmos DB" --language python

# Batch queries from JSONL
./tools/mslearn/mslearn batch --file tools/mslearn/queries.jsonl

# Session reuse for multiple queries
./tools/mslearn/mslearn session start
./tools/mslearn/mslearn search --query "test"
./tools/mslearn/mslearn session end
```

**Output formats:** `--format compact` (default), `json`, `jsonl`, `md`

## Query Tips

Be specific:
- Include **version**: `.NET 8`, `EF Core 8`
- Include **intent**: `quickstart`, `tutorial`, `limits`
- Include **platform**: `Linux`, `Windows`

## Languages (for code search)

`csharp` `typescript` `python` `powershell` `azurecli` `java` `go` `rust`

## Note

Zero runtime dependencies. Build requires Go 1.22+. Free to use, no API key needed.
