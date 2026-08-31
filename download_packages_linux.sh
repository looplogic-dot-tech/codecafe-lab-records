#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "Python 3 is required." >&2; exit 69; }
mkdir -p packages/linux
"$PYTHON" -m pip download --disable-pip-version-check --dest packages/linux -r requirements.txt
"$PYTHON" -m pip download --disable-pip-version-check --dest packages/linux -r requirements-build.txt
printf '\nLinux dependency cache updated: %s/packages/linux\n' "$PWD"
