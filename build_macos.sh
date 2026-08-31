#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
step(){ printf '\n[%s/8] %s\n' "$1" "$2"; }

step 1 "Checking macOS"
[[ "$(uname -s)" == "Darwin" ]] || { echo "The macOS app must be built on macOS." >&2; exit 69; }

step 2 "Checking Apple build tools"
if ! xcode-select -p >/dev/null 2>&1 || ! xcrun --find lipo >/dev/null 2>&1; then
  cat >&2 <<'MSG'
Apple Command Line Tools are not ready.
Finish their installation first, then verify:
  xcode-select -p
  xcrun --find lipo
Then rerun ./build_macos.sh.
MSG
  exit 69
fi

step 3 "Preparing Python environment"
./setup_macos.sh
./validate_source.sh
shopt -s nullglob
cached=(packages/macos/*.whl packages/macos/*.tar.gz packages/macos/*.zip)
if ((${#cached[@]})); then
  .venv/bin/python -m pip install --disable-pip-version-check --no-index --find-links packages/macos -r requirements-build.txt
else
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements-build.txt
fi

step 4 "Building Registros Clínicos.app"
rm -rf build dist "Registros Clínicos.spec"
DATA_ARGS=()
while IFS= read -r -d '' file; do
  rel="${file#./}"; dest="$(dirname "$rel")"; DATA_ARGS+=(--add-data "$rel:$dest")
done < <(find ./templates ./static -type f -print0)
# v0.6.5 ships OCR language data in the source package.  Do not depend on
# Homebrew or Finder's PATH: the exact same eng/spa traineddata is always
# embedded into the final .app.
SOURCE_TESSDATA="$PWD/ocr/tessdata"
[[ -f "$SOURCE_TESSDATA/eng.traineddata" ]] || { echo "Bundled eng.traineddata is missing from the source package." >&2; exit 72; }
[[ -f "$SOURCE_TESSDATA/spa.traineddata" ]] || { echo "Bundled spa.traineddata is missing from the source package." >&2; exit 72; }
echo "Bundling self-contained OCR data: $SOURCE_TESSDATA"
DATA_ARGS+=(--add-data "$SOURCE_TESSDATA/eng.traineddata:tessdata")
DATA_ARGS+=(--add-data "$SOURCE_TESSDATA/spa.traineddata:tessdata")

.venv/bin/python -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name "Registros Clínicos" \
  --osx-bundle-identifier "io.codecafe.labrecords" \
  --collect-all webview \
  --collect-all pypdf \
  --collect-all pymupdf \
  "${DATA_ARGS[@]}" desktop_window.py
APP_PATH="dist/Registros Clínicos.app"
[[ -d "$APP_PATH" ]] || { echo "Expected .app was not created." >&2; exit 70; }
[[ -f "$APP_PATH/Contents/Info.plist" ]] || { echo "Invalid .app bundle." >&2; exit 71; }

step 5 "Self-testing PDF extraction inside the compiled .app"
SELFTEST_DIR="$(mktemp -d /tmp/codecafe-mac-selftest.XXXXXX)"
trap 'rm -rf "$SELFTEST_DIR"' EXIT
.venv/bin/python tests/create_build_pdf_fixtures.py "$SELFTEST_DIR" >/dev/null
BIN="$APP_PATH/Contents/MacOS/Registros Clínicos"
for kind in embedded_text scanned uroculture; do
  PDF="$SELFTEST_DIR/${kind}_test.pdf"
  OUT="$SELFTEST_DIR/${kind}.json"
  "$BIN" --diagnose-pdf "$PDF" --diagnostic-output "$OUT"
  .venv/bin/python - "$kind" "$OUT" <<'PYVERIFY'
import json, sys
kind, path = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding='utf-8'))
count = int(data.get('results') or 0)
ocr = data.get('ocr') or {}
expected = 1 if kind == 'uroculture' else 2
print(f"  {kind}: engine={data.get('engine')} results={count} ocr={ocr}")
if count < expected:
    print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
    raise SystemExit(f"Compiled-app {kind} PDF self-test failed: expected at least {expected} structured result(s).")
if kind == 'scanned' and not ocr.get('available'):
    raise SystemExit('Compiled app cannot locate its bundled OCR language data.')
PYVERIFY
done

step 6 "Creating macOS installer package"
INSTALLROOT="dist/CodeCafe_Lab_Records_macOS_Installer"
rm -rf "$INSTALLROOT"
mkdir -p "$INSTALLROOT"
ditto "$APP_PATH" "$INSTALLROOT/Registros Clínicos.app"
cp AUTHORSHIP.md "$INSTALLROOT/AUTHORSHIP.txt"
cat > "$INSTALLROOT/Install Registros Clínicos.command" <<'INSTALL'
#!/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$ROOT/Registros Clínicos.app"
DEST="/Applications/Registros Clínicos.app"
[[ -d "$SOURCE" ]] || { echo "Registros Clínicos.app is missing from this installer." >&2; read -r -p "Press Enter to close..."; exit 70; }

echo "Installing Registros Clínicos in /Applications..."
/usr/bin/osascript - "$SOURCE" "$DEST" <<'APPLESCRIPT'
on run argv
    set sourcePath to item 1 of argv
    set destPath to item 2 of argv
    set cmd to "/bin/rm -rf " & quoted form of destPath & " && /usr/bin/ditto " & quoted form of sourcePath & " " & quoted form of destPath
    do shell script cmd with administrator privileges
end run
APPLESCRIPT

[[ -d "$DEST" && -f "$DEST/Contents/Info.plist" ]] || { echo "Installation validation failed." >&2; read -r -p "Press Enter to close..."; exit 71; }
/usr/bin/touch "$DEST" || true

echo
echo "✓ Installed in /Applications."
echo "The downloaded/build folder can now be deleted."
echo "Opening Registros Clínicos..."
/usr/bin/open "$DEST"
sleep 2
INSTALL
chmod +x "$INSTALLROOT/Install Registros Clínicos.command"

cat > "$INSTALLROOT/README-INSTALL.txt" <<'README'
Registros Clínicos by CodeCafe — macOS installation

1. Double-click "Install Registros Clínicos.command".
2. Authorize the copy to /Applications when macOS asks.
3. After Registros Clínicos opens successfully from /Applications, this installer folder may be deleted.

Patient data and PDFs are NOT stored inside the installer folder or app bundle.
They remain under:
  ~/Library/Application Support/CodeCafe Lab Records/
README

step 7 "Packaging macOS installer"
ZIP_PATH="dist/CodeCafe_Lab_Records_macOS_Installer.zip"
rm -f "$ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$INSTALLROOT" "$ZIP_PATH"

step 8 "Done"
printf 'Application bundle: %s/%s\n' "$PWD" "$APP_PATH"
printf 'End-user installer: %s/%s\n' "$PWD" "$ZIP_PATH"
printf 'Install from the installer ZIP; after installation the build/source folder may be deleted.\n'
