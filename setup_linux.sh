#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "Python 3 is required." >&2; exit 69; }
if [[ -d .venv ]] && { [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -c 'import sys; raise SystemExit(0 if sys.platform.startswith("linux") else 1)' >/dev/null 2>&1; }; then
  echo "Removing incompatible or incomplete .venv..."
  rm -rf .venv
fi
if [[ ! -d .venv ]]; then
  "$PYTHON" -m venv .venv
fi
shopt -s nullglob
cached=(packages/linux/*.whl packages/linux/*.tar.gz packages/linux/*.zip)
if ((${#cached[@]})); then
  echo "Using local dependency cache: packages/linux"
  .venv/bin/python -m pip install --disable-pip-version-check --no-index --find-links packages/linux -r requirements.txt
else
  echo "Local cache is empty; installing dependencies from PyPI."
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
fi
if command -v tesseract >/dev/null 2>&1; then
  echo "OCR engine detected: $(tesseract --version 2>/dev/null | head -n1)"
  if ! tesseract --list-langs 2>/dev/null | grep -qx 'spa'; then
    echo "WARNING: Spanish OCR language data was not detected. Run ./install_ocr_linux.sh"
  fi
else
  echo "WARNING: Tesseract OCR is not installed. Text PDFs will work, but scanned PDFs need OCR."
  echo "         On CentOS/DNF systems run: ./install_ocr_linux.sh"
fi
.venv/bin/python -c 'import flask, pypdf, fitz, webview; print("Desktop dependencies: OK")'
printf '\nSetup complete. Start the desktop window with:\n  ./run_linux.sh\n' 
