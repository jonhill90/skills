#!/usr/bin/env python3
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

def find_repo_root() -> Path | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(Path(__file__).parent), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return Path(output.strip())
    except (OSError, subprocess.CalledProcessError):
        return None


def load_api_key() -> str:
    api_key = os.getenv("CONTEXT7_API_KEY", "")
    repo_root = find_repo_root()
    if api_key or repo_root is None:
        return api_key
    for env_file in (repo_root / ".env", repo_root / ".claude" / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("CONTEXT7_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


if len(sys.argv) < 3:
    print("Usage: fetch-docs.py <library-id> <query>", file=sys.stderr)
    sys.exit(1)

api_key = load_api_key()
params = {'libraryId': sys.argv[1], 'query': sys.argv[2]}
url = f"https://context7.com/api/v2/context?{urllib.parse.urlencode(params)}"
req = urllib.request.Request(url)
if api_key: req.add_header('Authorization', f'Bearer {api_key}')

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
