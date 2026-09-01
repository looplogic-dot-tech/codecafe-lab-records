#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
cleanup_bytecode(){ find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true; find . -type f -name "*.pyc" -delete 2>/dev/null || true; }
trap cleanup_bytecode EXIT
cleanup_bytecode

python3 -m py_compile app.py app_v612.py desktop_window.py lab_pdf_parser.py lab_pdf_parser_v612.py clinical_dictionary.py glucose_filter.py multi_record_ocr.py tests/test_smoke.py tests/test_parser_unit.py tests/test_dictionary_unit.py tests/test_desktop_window.py tests/test_glucose_filter.py tests/test_multi_record_ocr.py tests/test_review_correction_source.py
if command -v node >/dev/null 2>&1; then
  node --check static/app.js
  node --check static/v612_review.js
else
  echo "Node not installed; skipping JavaScript syntax check (Node is NOT required to run the app)."
fi
bash -n build_linux.sh build_macos.sh setup_linux.sh setup_macos.sh run_linux.sh run_macos.sh run_browser_linux.sh run_browser_macos.sh

for required in app.py app_v612.py desktop_window.py lab_pdf_parser.py clinical_dictionary.py templates/index.html static/main.css static/app.js static/v612_review.js static/v612_review.css requirements.txt AUTHORSHIP.md; do
  [[ -s "$required" ]] || { echo "Missing required file: $required" >&2; exit 65; }
done

grep -q 'Jaime Sánchez Sáenz' app.py static/app.js README.md AUTHORSHIP.md || { echo "Permanent authorship attribution is missing." >&2; exit 65; }
grep -q 'contacto@codecafe.io' app.py static/app.js README.md AUTHORSHIP.md || { echo "Project contact attribution is missing." >&2; exit 65; }

if grep -RniE 'invoice|customer|client company|quote number' app.py lab_pdf_parser.py templates static --exclude='*.map'; then
  echo "Possible ERP business terminology found; review above." >&2
  exit 65
fi
if find . -type f -path './data/pdfs/*' ! -name '.gitkeep' -print -quit | grep -q .; then
  echo "A stored medical PDF is present in the source tree; remove it before packaging." >&2
  exit 65
fi
if find . -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -print -quit | grep -q .; then
  echo "A database file is present in the source tree; remove it before packaging." >&2
  exit 65
fi
echo "Source validation passed."
