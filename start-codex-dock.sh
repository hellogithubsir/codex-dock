#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Starting codex-dock. Use --cli to open the terminal menu instead of the Web panel."

if command -v python3 >/dev/null 2>&1; then
  python3 -m scripts "$@"
elif command -v python >/dev/null 2>&1; then
  python -m scripts "$@"
else
  echo "Python 3.10+ not found."
  exit 1
fi
