#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This setup script is intended for macOS." >&2
  exit 69
fi

PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || {
  echo "Python 3 is required. Install Python 3, then run this script again." >&2
  exit 69
}

if [[ -d .venv ]]; then
  if [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.platform == "darwin" else 1)' >/dev/null 2>&1; then
    echo "Removing incompatible or incomplete .venv..."
    rm -rf .venv
  fi
fi

if [[ ! -d .venv ]]; then
  echo "Creating a fresh macOS virtual environment..."
  "$PYTHON" -m venv .venv
fi

shopt -s nullglob
cached=(packages/macos/*.whl packages/macos/*.tar.gz packages/macos/*.zip)
if ((${#cached[@]})); then
  echo "Using local dependency cache: packages/macos"
  .venv/bin/python -m pip install --disable-pip-version-check --no-index --find-links packages/macos -r requirements.txt
else
  echo "Local macOS cache is empty; installing dependencies from PyPI."
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
fi

.venv/bin/python -c 'import flask, pypdf, pymupdf, fitz, webview; print("Desktop dependencies: OK")'

if ./check_ocr_macos.sh; then
  echo "macOS self-contained OCR data: ready"
else
  echo "ERROR: bundled OCR language data is missing from this source package." >&2
  exit 72
fi

printf '\nmacOS setup complete. Start the desktop window with:\n  ./run_macos.sh\n'
