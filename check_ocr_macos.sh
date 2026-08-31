#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ "$(uname -s)" == "Darwin" ]] || { echo "This helper is intended for macOS." >&2; exit 69; }
PYTHON=".venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="${PYTHON3:-python3}"
PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON" - <<'PY'
from lab_pdf_parser import ocr_status
s=ocr_status()
print(f"tessdata: {s.get('tessdata') or 'NOT FOUND'}")
print(f"  eng: {'OK' if s.get('eng') else 'missing'}")
print(f"  spa: {'OK' if s.get('spa') else 'missing'}")
print(f"  self-contained OCR data: {'ready' if s.get('available') else 'NOT READY'}")
raise SystemExit(0 if s.get('available') and s.get('eng') and s.get('spa') else 1)
PY
