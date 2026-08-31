#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ -x .venv/bin/python ]] || { echo "Run the platform setup script first (setup_linux.sh or setup_macos.sh)." >&2; exit 69; }
.venv/bin/python -m unittest discover -s tests -v
