#!/usr/bin/env bash
# Read a Claude Code hook payload from stdin and print tool_input.file_path.
#
# Usage: f=$(/path/to/hook-file-path.sh)
#
# - Tries jq first (preferred — universally available in most environments).
# - Falls back to python3 if jq is missing.
# - Prints empty string if neither is available, or if the field is missing.
# - Always exits 0 so PostToolUse hooks never fail when jq isn't installed.

set -u

if command -v jq >/dev/null 2>&1; then
  jq -r '.tool_input.file_path // empty' 2>/dev/null || true
elif command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json,sys
try:
  d=json.load(sys.stdin)
  print(d.get("tool_input",{}).get("file_path",""))
except Exception:
  pass' 2>/dev/null || true
fi

exit 0
