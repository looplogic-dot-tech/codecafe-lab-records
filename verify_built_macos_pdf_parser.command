#!/bin/bash
set -Eeuo pipefail
cd "$(dirname "$0")"
APP="dist/Registros Clínicos.app"
BIN="$APP/Contents/MacOS/Registros Clínicos"
[[ -x "$BIN" ]] || {
  echo "The compiled app was not found at: $APP"
  echo "Run ./build_macos.sh first."
  read -r -p "Press Enter to close..."
  exit 70
}
PDF="$(/usr/bin/osascript <<'APPLESCRIPT'
try
  set f to choose file with prompt "Choose a PDF to test inside the compiled Registros Clínicos app" of type {"com.adobe.pdf"}
  return POSIX path of f
on error number -128
  return ""
end try
APPLESCRIPT
)"
[[ -n "$PDF" ]] || exit 0
OUT="/tmp/codecafe-lab-pdf-diagnostic.json"
rm -f "$OUT"
"$BIN" --diagnose-pdf "$PDF" --diagnostic-output "$OUT"
echo
echo "Compiled-app PDF diagnostic:"
echo "--------------------------------"
cat "$OUT"
echo
read -r -p "Press Enter to close..."
