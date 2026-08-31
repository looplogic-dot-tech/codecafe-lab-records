#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Run this on the target Mac so pip downloads packages compatible with that Mac/Python architecture." >&2
  exit 69
fi
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "Python 3 is required." >&2; exit 69; }
mkdir -p packages/macos
"$PYTHON" -m pip download --disable-pip-version-check --dest packages/macos -r requirements.txt
"$PYTHON" -m pip download --disable-pip-version-check --dest packages/macos -r requirements-build.txt -r requirements-build.txt
printf '\nmacOS dependency/build cache updated: %s/packages/macos\n' "$PWD"
