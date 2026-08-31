#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ -x .venv/bin/python ]] || ./setup_linux.sh
exec .venv/bin/python desktop_window.py --browser --port "${CODECAFE_PORT:-5000}" "$@"
