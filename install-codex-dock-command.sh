#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Installing the codex-dock shell command into your profile."

if command -v python3 >/dev/null 2>&1; then
  python3 -c 'from scripts.main import install; install()'
elif command -v python >/dev/null 2>&1; then
  python -c 'from scripts.main import install; install()'
else
  echo "Python 3.10+ not found."
  exit 1
fi
