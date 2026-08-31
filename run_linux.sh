#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  echo "Python environment is missing. Running setup first..."
  ./setup_linux.sh
fi
if ! .venv/bin/python -c 'import flask, pypdf, fitz, webview' >/dev/null 2>&1; then
  echo "Dependencies are incomplete. Repairing setup..."
  ./setup_linux.sh
fi
exec .venv/bin/python desktop_window.py "$@"
