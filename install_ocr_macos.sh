#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This helper is intended for macOS." >&2
  exit 69
fi
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew was not found. Install Homebrew first, then re-run this helper." >&2
  exit 69
fi
brew install tesseract tesseract-lang
printf '\nInstalled Tesseract OCR and additional language data.\n'
tesseract --version | head -n1
echo "Languages detected:"
tesseract --list-langs 2>/dev/null | grep -E '^(eng|spa)$' || true
