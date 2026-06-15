# Search for Context7 library IDs
param(
    [Parameter(Mandatory=$true)]
    [string]$LibraryName,

    [Parameter(Mandatory=$false)]
    [string]$Query
)

if (-not $Query) {
    $Query = $LibraryName
}

# Load API key from the environment or common project-local files
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (& git -C $ScriptDir rev-parse --show-toplevel 2>$null)
$ApiKey = $env:CONTEXT7_API_KEY
if (-not $ApiKey -and $RepoRoot) {
    foreach ($EnvFile in @((Join-Path $RepoRoot ".env"), (Join-Path $RepoRoot ".claude/.env"))) {
        if (Test-Path $EnvFile) {
            foreach ($line in Get-Content $EnvFile) {
                if ($line -match '^CONTEXT7_API_KEY=(.+)$') {
                    $ApiKey = $matches[1].Trim('"').Trim("'")
                    break
                }
            }
        }
        if ($ApiKey) { break }
    }
}

# Build URL with encoded parameters
$EncodedLib = [System.Web.HttpUtility]::UrlEncode($LibraryName)
$EncodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
$Url = "https://context7.com/api/v2/libs/search?libraryName=$EncodedLib&query=$EncodedQuery"

# Make request
$Headers = @{}
if ($ApiKey) {
    $Headers["Authorization"] = "Bearer $ApiKey"
}

try {
    $Response = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get

    Write-Host "Available Libraries:`n"
    foreach ($lib in $Response.results) {
        Write-Host "- **$($lib.title)**"
        Write-Host "  ID: ``$($lib.id)``"
        Write-Host "  Description: $($lib.description)"
        Write-Host "  Snippets: $($lib.totalSnippets)"
        Write-Host ""
    }
} catch {
    Write-Error "Error: $_"
    exit 1
}
