# Environment Variable Management

## Architecture

Main shell profiles are tracked in git. They source local files that contain secrets. Local files are gitignored.

```
Main Profile (tracked) → sources Local Profile (gitignored) → exports secrets
```

Secrets never appear in tracked files. MCP configs reference environment variables by name, not value.

---

## Required Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `CONTEXT7_API_KEY` | Context7 MCP, context7 skills | Library documentation API |
| `AZURE_DEVOPS_PAT` | az-devops skill | Azure DevOps personal access token |

---

## Shell Setup

### zsh

**`~/.zshrc`** (tracked) — add at end:

```bash
[ -f ~/.zshrc.local ] && source ~/.zshrc.local
```

**`~/.zshrc.local`** (gitignored) — add secrets:

```bash
export CONTEXT7_API_KEY="your-key-here"
export AZURE_DEVOPS_PAT="your-pat-here"
```

### PowerShell Core (pwsh 7+)

**`$PROFILE`** (tracked) — add at end:

```powershell
$LocalProfile = Join-Path $PSScriptRoot "Microsoft.PowerShell_profile_local.ps1"
if (Test-Path $LocalProfile) { . $LocalProfile }
```

**`Microsoft.PowerShell_profile_local.ps1`** (gitignored) — add secrets:

```powershell
$env:CONTEXT7_API_KEY = "your-key-here"
$env:AZURE_DEVOPS_PAT = "your-pat-here"
```

### Windows PowerShell 5.1

Same pattern as pwsh 7+, but the profile directory is `Documents\WindowsPowerShell\` instead of `Documents\PowerShell\`.

---

## MCP Configuration

### Claude Code (`.mcp.json`)

Use `${VAR_NAME}` syntax in headers:

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "Authorization": "Bearer ${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

### Codex CLI (`.codex/config.toml`)

Use `bearer_token_env_var` — references the variable name (no `$`, no `{}`):

```toml
[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
bearer_token_env_var = "CONTEXT7_API_KEY"
```

---

## Gitignore Patterns

Add to `.gitignore` in any repo using this pattern:

```gitignore
.zshrc.local
*_profile_local.ps1
.env.local
```

---

## Verification

```bash
# zsh — confirm variable loads
source ~/.zshrc && echo $CONTEXT7_API_KEY | head -c 10

# PowerShell — confirm variable loads
. $PROFILE; $env:CONTEXT7_API_KEY.Substring(0,10)

# Test MCP auth — Claude Code
# Environment variables should be available when MCP servers start
```

---

## Security

**Do:**
- Keep `*_local.*` files out of version control
- Use environment variables for all secrets
- Use `bearer_token_env_var` in Codex config
- Use `${VAR_NAME}` syntax in Claude Code config

**Don't:**
- Commit API keys to git
- Hardcode secrets in tracked files
- Share `*_local.*` files
