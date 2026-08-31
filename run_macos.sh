#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then ./setup_macos.sh; fi
if ! .venv/bin/python -c 'import flask, pypdf, fitz, webview' >/dev/null 2>&1; then ./setup_macos.sh; fi
exec .venv/bin/python desktop_window.py "$@"
